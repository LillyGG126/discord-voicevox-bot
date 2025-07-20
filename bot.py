import discord
from discord import app_commands
import requests
import json
import asyncio
import io
import os
import functools
import traceback # エラー詳細表示のために追加

# --- 設定項目（Renderの環境変数から読み込む） ---
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_CHANNEL_ID_STR = os.getenv('TARGET_CHANNEL_ID')
TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID_STR) if TARGET_CHANNEL_ID_STR else 0
VOICEVOX_URL = os.getenv('VOICEVOX_URL', 'http://127.0.0.1:50021')

# --- グローバル変数 ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
voice_client = None
message_queue = asyncio.Queue()
user_speakers = {}
DEFAULT_SPEAKER_ID = 14

# --- 関数定義 ---

def blocking_synthesize(text, speaker):
    """
    【重要】requestsライブラリのブロッキング処理をこの関数にまとめる
    """
    try:
        # 1. 音声合成用のクエリを作成
        print("      [Thread] -> audio_query request")
        query_params = {"text": text, "speaker": speaker}
        query_response = requests.post(f"{VOICEVOX_URL}/audio_query", params=query_params, timeout=15)
        query_response.raise_for_status()
        audio_query = query_response.json()
        print("      [Thread] <- audio_query success")

        # 2. 音声合成を実行
        print("      [Thread] -> synthesis request")
        synth_params = {"speaker": speaker}
        synth_response = requests.post(
            f"{VOICEVOX_URL}/synthesis",
            headers={"Content-Type": "application/json"},
            params=synth_params,
            data=json.dumps(audio_query),
            timeout=15 # タイムアウトを15秒に延長
        )
        synth_response.raise_for_status()
        print("      [Thread] <- synthesis success")
        return synth_response.content
    except requests.exceptions.RequestException as e:
        print(f"!!! ERROR in thread: VOICEVOX APIへの接続に失敗しました: {e}")
        return None

async def synthesize_voice(text, speaker):
    """
    ブロッキング処理を別スレッドで実行し、Botのメイン処理を止めないようにする
    """
    loop = asyncio.get_event_loop()
    func = functools.partial(blocking_synthesize, text, speaker)
    wav_data = await loop.run_in_executor(None, func)
    return wav_data

def after_playing(error, filename):
    """再生終了後に呼ばれるコールバック関数"""
    if error:
        print(f'!!! ERROR after playing: {error}')
    else:
        print(f'--> Finished playing audio.')
    
    # ファイルが存在すれば削除
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f'--> Deleted temp file: {filename}')
        except Exception as e:
            print(f'!!! ERROR deleting temp file {filename}: {e}')


async def audio_player_task():
    while True:
        author_id, line_to_speak = await message_queue.get()
        
        if not (voice_client and voice_client.is_connected()):
            print("--> Player waiting: Voice client not connected.")
            await asyncio.sleep(1)
            # 処理できなかったのでキューに戻す（場合によるが、今回はシンプルに破棄）
            message_queue.task_done()
            continue

        while voice_client.is_playing():
            await asyncio.sleep(0.2)

        speaker_id = user_speakers.get(author_id, DEFAULT_SPEAKER_ID)
        print(f"--> Synthesizing (User: {author_id}, Speaker: {speaker_id}): '{line_to_speak}'")
        
        wav_data = await synthesize_voice(line_to_speak, speaker_id)
        
        if wav_data:
            print(f"--> Synthesis complete. Received {len(wav_data)} bytes of audio data.")
            if voice_client and voice_client.is_connected():
                temp_filename = f"_temp_{author_id}.wav"
                try:
                    with open(temp_filename, "wb") as f:
                        f.write(wav_data)
                    
                    source = discord.FFmpegPCMAudio(temp_filename)
                    
                    # afterコールバックを正しく設定
                    callback = functools.partial(after_playing, filename=temp_filename)
                    print(f"--> Playing audio from {temp_filename}...")
                    voice_client.play(source, after=callback)

                except Exception as e:
                    print(f"!!! ERROR: Failed to play audio: {e}")
                    traceback.print_exc() # エラーの詳細を表示
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
            else:
                print("--> Skipped playing: Voice client disconnected during synthesis.")
        else:
            print("--> Skipped playing: Synthesis failed (wav_data is None).")
        
        message_queue.task_done()

@client.event
async def on_ready():
    print("--- Bot is ready! ---")
    await tree.sync()
    print("--- Slash commands synced! ---")
    client.loop.create_task(audio_player_task())
    print("--- Audio player task started ---")
    print("-----------------------\n")

@client.event
async def on_message(message):
    global voice_client
    if message.author.bot: return
    if voice_client and voice_client.is_connected() and message.channel.id == TARGET_CHANNEL_ID:
        lines = message.content.split('\n')
        for line in lines:
            if line.strip():
                await message_queue.put((message.author.id, line))

@tree.command(name="join", description="Botがボイスチャンネルに参加し、読み上げを開始します。")
async def join_command(interaction: discord.Interaction):
    global voice_client
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)
            await interaction.response.send_message(f"`{channel.name}` に移動しました。", ephemeral=True)
        else:
            voice_client = await channel.connect()
            await interaction.response.send_message(f"`{channel.name}` に参加しました。読み上げを開始します。", ephemeral=True)
    else:
        await interaction.response.send_message("先にボイスチャンネルに入ってください。", ephemeral=True)

@tree.command(name="leave", description="Botがボイスチャンネルから退出します。")
async def leave_command(interaction: discord.Interaction):
    global voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        voice_client = None
        while not message_queue.empty():
            try:
                message_queue.get_nowait()
                message_queue.task_done()
            except asyncio.QueueEmpty:
                break
        await interaction.response.send_message("ボイスチャンネルから退出しました。", ephemeral=True)
    else:
        await interaction.response.send_message("Botはボイスチャンネルに参加していません。", ephemeral=True)

@tree.command(name="speaker", description="読み上げキャラクターのIDを設定します。")
@app_commands.describe(id="VOICEVOXのキャラクターID（数字）")
async def set_speaker(interaction: discord.Interaction, id: int):
    user_id = interaction.user.id
    user_speakers[user_id] = id
    await interaction.response.send_message(f"あなたの読み上げキャラクターをID: {id} に設定しました。", ephemeral=True)
    print(f"--- Speaker for {interaction.user.name} set to {id} ---")

# --- Botの起動 ---
if __name__ == '__main__':
    if not DISCORD_BOT_TOKEN:
        print("!!! FATAL ERROR: 環境変数 'DISCORD_BOT_TOKEN' が設定されていません！")
    else:
        client.run(DISCORD_BOT_TOKEN)

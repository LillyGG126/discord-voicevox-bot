import discord
from discord import app_commands
import requests
import json
import asyncio
import io
import os

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
async def synthesize_voice(text, speaker):
    try:
        query_params = {"text": text, "speaker": speaker}
        query_response = requests.post(f"{VOICEVOX_URL}/audio_query", params=query_params, timeout=10)
        query_response.raise_for_status()
        audio_query = query_response.json()
        synth_params = {"speaker": speaker}
        synth_response = requests.post(
            f"{VOICEVOX_URL}/synthesis",
            headers={"Content-Type": "application/json"},
            params=synth_params,
            data=json.dumps(audio_query),
            timeout=10
        )
        synth_response.raise_for_status()
        return synth_response.content
    except requests.exceptions.RequestException as e:
        print(f"!!! ERROR: VOICEVOX APIへの接続に失敗しました: {e}")
        return None

async def audio_player_task():
    while True:
        author_id, line_to_speak = await message_queue.get()
        if voice_client and voice_client.is_connected() and not voice_client.is_playing():
            speaker_id = user_speakers.get(author_id, DEFAULT_SPEAKER_ID)
            print(f"--> Reading (User: {author_id}, Speaker: {speaker_id}): {line_to_speak}")
            wav_data = await synthesize_voice(line_to_speak, speaker_id)
            if wav_data:
                temp_filename = f"_temp_{author_id}.wav"
                try:
                    with open(temp_filename, "wb") as f:
                        f.write(wav_data)
                    source = discord.FFmpegPCMAudio(temp_filename)
                    voice_client.play(source, after=lambda e: os.remove(temp_filename) if os.path.exists(temp_filename) else None)
                except Exception as e:
                    print(f"!!! ERROR: Failed to play audio: {e}")
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
        message_queue.task_done()
        await asyncio.sleep(0.1)

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
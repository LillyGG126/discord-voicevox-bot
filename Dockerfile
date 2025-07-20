# 1. ベースとなる公式Pythonイメージを指定
FROM python:3.13-slim

# 2. 管理者(root)権限でシステムパッケージをインストール
# .7zファイルを解凍するために p7zip-full を追加
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ffmpeg \
    p7zip-full \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. アプリケーション用のディレクトリを作成
WORKDIR /app

# 4. 最新版(0.24.1)のVOICEVOX Engineをダウンロードして展開
# 正しいファイル名(.7z.001)を指定
RUN wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.24.1/voicevox_engine-linux-cpu-x64-0.24.1.7z.001 && \
    # 7zコマンドで解凍し、不要になった圧縮ファイルを削除
    7z x voicevox_engine-linux-cpu-x64-0.24.1.7z.001 && \
    rm voicevox_engine-linux-cpu-x64-0.24.1.7z.001

# 5. 必要なプロジェクトファイルをコピー
COPY requirements.txt .
COPY start.sh .
COPY bot.py .
COPY keep_alive.py .

# 6. Pythonライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 7. 起動スクリプトに実行権限を付与
RUN chmod +x ./start.sh

# 8. コンテナ起動時に実行するコマンドを指定
CMD ["./start.sh"]
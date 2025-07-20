# 1. ベースとなる公式Pythonイメージを指定
FROM python:3.11-slim

# 2. 管理者(root)権限でシステムパッケージをインストール
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. アプリケーション用のディレクトリを作成
WORKDIR /app

# 4. 最新版(0.24.1)のVOICEVOX Engineをダウンロードして展開
RUN wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.24.1/voicevox_engine-linux-cpu-0.24.1.zip && \
    unzip voicevox_engine-linux-cpu-0.24.1.zip && \
    rm voicevox_engine-linux-cpu-0.24.1.zip

# 5. 必要なプロジェクトファイルをコピー
COPY requirements.txt .
COPY start.sh .
COPY bot.py .

# 6. Pythonライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 7. 起動スクリプトに実行権限を付与
RUN chmod +x ./start.sh

# 8. コンテナ起動時に実行するコマンドを指定
CMD ["./start.sh"]

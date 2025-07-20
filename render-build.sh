#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. 必要なシステムパッケージをインストール (updateなしで直接インストール)
apt-get install -y wget unzip ffmpeg

# 2. 最新版(0.19.4)のVOICEVOX Engineをダウンロードして展開
wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.19.4/voicevox_engine-linux-cpu-0.19.4.zip
unzip voicevox_engine-linux-cpu-0.19.4.zip

# 3. Pythonライブラリをインストール
pip install -r requirements.txt

# 4. 起動スクリプトに実行権限を付与
chmod +x start.sh
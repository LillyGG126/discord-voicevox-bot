#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. 必要なシステムパッケージをインストール
apt-get update && apt-get install -y ffmpeg wget unzip

# 2. VOICEVOX Engineをダウンロードして展開
# 注意: バージョンが更新された場合、このURLと下のディレクトリ名も変更が必要
wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.16.1/voicevox_engine-linux-cpu-0.16.1.zip
unzip voicevox_engine-linux-cpu-0.16.1.zip

# 3. Pythonライブラリをインストール
pip install -r requirements.txt

# 4. 起動スクリプトに実行権限を付与
chmod +x start.sh
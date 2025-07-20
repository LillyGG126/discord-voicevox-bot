#!/usr/bin/env bash
# exit on error
set -o errexit

# apt-get updateを削除し、installのみ実行
apt-get install -y ffmpeg

pip install -r requirements.txt
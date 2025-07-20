#!/usr/bin/env bash

# VOICEVOX Engineをバックグラウンドで起動（正しいパスを指定）
./voicevox_engine-linux-x64-cpu-0.24.1/voicevox_engine/run --host 0.0.0.0 &

# Webサーバーをバックグラウンドで起動
python keep_alive.py &

# Discord Botをフォアグラウンドで起動
python bot.py
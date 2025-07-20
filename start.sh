#!/usr/bin/env bash

# VOICEVOX Engineをバックグラウンドで起動
./run --host 0.0.0.0 &

# Discord Botをフォアグラウンドで起動
python bot.py
#!/usr/bin/env bash

# 解凍後に作成される正しいディレクトリパスを指定してVOICEVOX Engineをバックグラウンドで起動
./voicevox_engine-linux-x64-cpu-0.24.1/voicevox_engine/run --host 0.0.0.0 &

# Discord Botをフォアグラウンドで起動
python bot.py

#!/usr/bin/env bash

# 展開された最新版の正しいディレクトリの中にあるVOICEVOX Engineをバックグラウンドで起動
./voicevox_engine-linux-x64-cpu-0.24.1/run --host 0.0.0.0 &

# Discord Botをフォアグラウンドで起動
python bot.py
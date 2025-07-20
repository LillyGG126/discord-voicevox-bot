#!/usr/bin/env bash

# 展開された最新版のディレクトリ(0.24.1)の中にあるVOICEVOX Engineをバックグラウンドで起動
./voicevox_engine-linux-cpu-0.24.1/run --host 0.0.0.0 &

# Discord Botをフォアグラウンドで起動
python bot.py
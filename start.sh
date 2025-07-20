#!/usr/bin/env bash

# 展開されたディレクトリの中にあるVOICEVOX Engineをバックグラウンドで起動
./voicevox_engine-linux-cpu-0.16.1/run --host 0.0.0.0 &

# Discord Botをフォアグラウンドで起動
python bot.py
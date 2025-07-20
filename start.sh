#!/usr/bin/env bash

# 展開された新しいディレクトリ(0.19.4)の中にあるVOICEVOX Engineをバックグラウンドで起動
./voicevox_engine-linux-cpu-0.19.4/run --host 0.0.0.0 &

# Discord Botをフォアグラウンドで起動
python bot.py
#!/usr/bin/env bash

# あなたが特定してくれた正しいパスを指定してVOICEVOX Engineをバックグラウンドで起動
./voicevox_engine-linux-cpu-x64-0.24.1/linux-cpu-x64/run --host 0.0.0.0 &

# Webサーバーをバックグラウンドで起動
python keep_alive.py &

# Discord Botをフォアグラウンドで起動
python bot.py
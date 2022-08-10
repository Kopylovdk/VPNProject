#!/bin/sh

echo $(kill $(pgrep -f bot_main.py))
exec python apps/service/bot/bot_main.py

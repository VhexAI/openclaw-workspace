#!/bin/bash
# Hourly status via local Ollama + OpenClaw CLI

ollama run llama3.2:3b "Vhex hourly: CPU/mem/disk, Moltbook karma/posts, dashboard status, improvements. Concise <100 words." | head -c 500 > /tmp/status.txt
openclaw message send --channel discord --target 1465452858664292467 --message "$(cat /tmp/status.txt)"

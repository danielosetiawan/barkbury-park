#!/usr/bin/env bash
# Render episodes back to back: ./render_all.sh ep01 ep02
cd "$(dirname "$0")"
for ep in "$@"; do ./overnight.sh "$ep" > "logs/${ep}_overnight.log" 2>&1; done

#!/usr/bin/env bash
# After the episode renders: one fix-up pass (re-renders any still/clip pulled in review), then music, then assemble.
#   ./after_renders.sh <pid-to-wait-for> ep01 ep02
cd "$(dirname "$0")"
PY="${WAN2GP_PYTHON:-$HOME/miniforge3/envs/wan2gp/bin/python}"
WAIT_PID="$1"; shift
stamp() { date "+[%H:%M]"; }
echo "$(stamp) waiting for render job $WAIT_PID"
while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 60; done
while pgrep -f "wgp.py --process" >/dev/null; do sleep 30; done

for ep in "$@"; do
  if [ -n "$("$PY" build.py missing "$ep" stills)$("$PY" build.py missing "$ep" clips)" ]; then
    echo "$(stamp) fix-up pass for $ep"
    ./overnight.sh "$ep" > "logs/${ep}_fixup.log" 2>&1
  fi
done

for ep in "$@"; do "$PY" build.py music "$ep"; done
"$PY" - "$@" <<'PYEOF'
import json, sys
tasks = [t for ep in sys.argv[1:] for t in json.load(open(f"queues/{ep}_music.json"))]
json.dump(tasks, open("queues/music_batch.json", "w"), indent=2)
PYEOF
echo "$(stamp) music"
./run.sh queues/music_batch.json music
echo "$(stamp) music batch exited with $?"
for ep in "$@"; do
  echo "$(stamp) assemble $ep"
  "$PY" build.py assemble "$ep"
done
echo "$(stamp) done"

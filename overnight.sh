#!/usr/bin/env bash
# Chain an episode end to end: wait for any running WanGP batch -> stills -> review gate -> animatic -> clips -> assemble.
#   nohup caffeinate -is ./overnight.sh ep01 > logs/ep01_overnight.log 2>&1 &
# Shots that already have a still / clip are skipped, so it's safe to re-run after an interruption.
# Review gate: after new stills, waits up to REVIEW_WAIT minutes for review/<ep>_stills.ok. A reviewer
# moves rejected stills out of keyframes/<ep>/raw and touches the .ok file; rejected shots re-render first.
set -uo pipefail
EP="${1:?usage: overnight.sh <episode id>}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${WAN2GP_PYTHON:-$HOME/miniforge3/envs/wan2gp/bin/python}"
REVIEW_WAIT="${REVIEW_WAIT:-40}"
cd "$ROOT"
stamp() { date "+[%H:%M]"; }

echo "$(stamp) waiting for running WanGP batch to finish"
while pgrep -f "wgp.py --process" >/dev/null; do sleep 30; done

for round in 1 2 3; do
  read -ra need <<< "$("$PY" build.py missing "$EP" stills)"
  [ ${#need[@]} -eq 0 ] && break
  echo "$(stamp) stills for: ${need[*]}"
  "$PY" build.py keyframes "$EP" --variants 1 --only "${need[@]}"
  ./run.sh "queues/${EP}_keyframes.json" "keyframes/$EP/raw"
  echo "$(stamp) stills batch exited with $?"
  mkdir -p review; rm -f "review/${EP}_stills.ok"; echo "${need[*]}" > "review/${EP}_stills.pending"
  echo "$(stamp) waiting up to ${REVIEW_WAIT} min for stills review"
  for _ in $(seq $((REVIEW_WAIT * 2))); do [ -f "review/${EP}_stills.ok" ] && break; sleep 30; done
  [ -f "review/${EP}_stills.ok" ] && echo "$(stamp) stills reviewed" || echo "$(stamp) no review, continuing"
  rm -f "review/${EP}_stills.pending" "review/${EP}_stills.ok"
done

echo "$(stamp) animatic"
"$PY" build.py animatic "$EP" || echo "$(stamp) animatic failed (continuing)"

read -ra todo <<< "$("$PY" build.py missing "$EP" clips)"
if [ ${#todo[@]} -gt 0 ]; then
  echo "$(stamp) clips for: ${todo[*]}"
  "$PY" build.py clips "$EP" --only "${todo[@]}"
  ./run.sh "queues/${EP}_clips.json" "clips/$EP"
  echo "$(stamp) clips batch exited with $?"
fi

echo "$(stamp) assemble"
"$PY" build.py assemble "$EP"
echo "$(stamp) done"

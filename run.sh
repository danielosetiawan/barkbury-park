#!/usr/bin/env bash
# Run a WanGP queue headless.   ./run.sh queues/ep01_keyframes.json keyframes/ep01/raw [--dry-run]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WAN2GP="${WAN2GP_DIR:-$HOME/repos/wan2gp}"
PY="${WAN2GP_PYTHON:-$HOME/miniforge3/envs/wan2gp/bin/python}"

QUEUE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="$ROOT/$2"
shift 2
mkdir -p "$OUT"

# Let MPS fall back to CPU for any op it doesn't implement.
export PYTORCH_ENABLE_MPS_FALLBACK=1
# M1/M2: use BF16 instead of FP16 (FP16 gives black frames). Needs the patch in shared/mps/device_patch.py.
export WANGP_MPS_BF16="${WANGP_MPS_BF16:-1}"
cd "$WAN2GP"
# --vae-config 1 = decode whole frames (no tiling): ~2x faster than 256px tiles on a 16 GB Mac
exec "$PY" wgp.py --process "$QUEUE" --output-dir "$OUT" --vae-config 1 "$@"

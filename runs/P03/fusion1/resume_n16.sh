#!/bin/sh
set -eu

cd "$(dirname "$0")"

if ps -eo args | grep -E '[.]?/engine 3 tau3' | grep -v grep >/dev/null 2>&1; then
    echo "n16 engine shards are already running" >&2
    exit 1
fi

if [ ! -x ./engine ]; then
    gcc -O3 -std=c11 -o engine engine.c
fi

python3 - <<'PY'
import pathlib
import re

full = pathlib.Path("n16_full_engine.txt").read_text().splitlines()
for shard in range(8):
    log = pathlib.Path(f"n16full_{shard}.log")
    completed = sum(1 for line in log.read_text().splitlines()
                    if line.startswith("GRAPH "))
    assigned = full[shard::8]
    remaining = assigned[completed:]
    pathlib.Path(f"n16_resume_{shard}.txt").write_text(
        "".join(line + "\n" for line in remaining)
    )
    print(f"shard={shard} completed={completed} remaining={len(remaining)}")
PY

for shard in $(seq 0 7); do
    stdbuf -oL -eL ./engine 3 tau3 0 1 \
        < "n16_resume_${shard}.txt" \
        >> "n16full_${shard}.log" 2>&1 &
done
echo "launched 8 n16 shards"

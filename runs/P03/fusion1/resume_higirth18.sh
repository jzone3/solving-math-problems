#!/bin/sh
set -eu

ENGINE=/tmp/p03_engine_higirth18
if pgrep -f "$ENGINE 3 tau3" >/dev/null; then
    echo "higirth18 shards already running" >&2
    exit 1
fi
gcc -O3 -std=c11 -Wall -Wextra -o "$ENGINE" engine.c

python3 - <<'PY'
import json
from pathlib import Path

shards = [Path(f"higirth18_shard_{i}.txt") for i in range(8)]
if not all(path.exists() for path in shards):
    handles = [path.open("w") for path in shards]
    try:
        with open("higirth18.kept.jsonl") as source:
            for index, raw in enumerate(source):
                record = json.loads(raw)
                edges = record["edges"]
                text = " ".join(f"{u} {v}" for u, v in edges)
                handles[index % 8].write(
                    f"18 {len(edges)} {text}\n"
                )
    finally:
        for handle in handles:
            handle.close()

for shard, path in enumerate(shards):
    log = Path(f"higirth18_{shard}.log")
    completed = sum(
        1 for line in log.read_text().splitlines()
        if line.startswith("GRAPH ")
    ) if log.exists() else 0
    assigned = path.read_text().splitlines()
    Path(f"higirth18_resume_{shard}.txt").write_text(
        "".join(line + "\n" for line in assigned[completed:])
    )
    print(f"shard={shard} completed={completed} remaining={len(assigned)-completed}")
PY

for shard in $(seq 0 7); do
    ./launch_higirth18_shard.sh "$shard" >/dev/null
done
echo "launched 8 higirth18 shards"

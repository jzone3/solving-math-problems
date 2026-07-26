#!/bin/sh
set -eu

if ps -eo args | grep -F './engine 4 tau4a' | grep -v grep >/dev/null; then
    echo "n14 tau4a shards already running" >&2
    exit 1
fi

gcc -O3 -std=c11 -Wall -Wextra -o engine engine.c

python3 - <<'PY'
import gzip
from pathlib import Path
import networkx as nx

engine_input = Path("tau4_n14a_engine.txt")
if not engine_input.exists():
    with gzip.open("tau4_n14a.kept.g6.gz", "rt") as source, engine_input.open("w") as target:
        for raw in source:
            graph = nx.from_graph6_bytes(raw.strip().encode())
            edges = " ".join(
                f"{min(u, v)} {max(u, v)}" for u, v in sorted(graph.edges())
            )
            target.write(f"14 {graph.number_of_edges()} {edges}\n")

full = engine_input.read_text().splitlines()
for shard in range(8):
    log = Path(f"tau4n14a_{shard}.log")
    lines = log.read_text().splitlines() if log.exists() else []
    completed = sum(1 for line in lines
                    if line.startswith("GRAPH "))
    assigned = full[shard::8]
    remaining = assigned[completed:]
    Path(f"tau4n14a_resume_{shard}.txt").write_text(
        "".join(line + "\n" for line in remaining)
    )
    print(f"shard={shard} completed={completed} remaining={len(remaining)}")
PY

for shard in $(seq 0 7); do
    stdbuf -oL -eL ./engine 4 tau4a 0 1 \
        < "tau4n14a_resume_${shard}.txt" \
        >> "tau4n14a_${shard}.log" 2>&1 &
done
echo "launched 8 n14 tau4a shards"

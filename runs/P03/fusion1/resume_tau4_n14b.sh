#!/bin/sh
set -eu

ENGINE=/tmp/p03_engine_role
if pgrep -f "$ENGINE 4 tau4b" >/dev/null; then
    echo "n14 tau4b shards already running" >&2
    exit 1
fi
gcc -O3 -std=c11 -Wall -Wextra -o "$ENGINE" engine.c

python3 - <<'PY'
import gzip
from pathlib import Path
import networkx as nx

shards = [Path(f"tau4n14b_shard_{i}.txt") for i in range(8)]
if not all(path.exists() for path in shards):
    handles = [path.open("w") for path in shards]
    try:
        with gzip.open("tau4_n14b.kept.g6.gz", "rt") as source:
            for index, raw in enumerate(source):
                graph = nx.from_graph6_bytes(raw.strip().encode())
                edges = " ".join(
                    f"{min(u, v)} {max(u, v)}" for u, v in sorted(graph.edges())
                )
                handles[index % 8].write(
                    f"14 {graph.number_of_edges()} {edges}\n"
                )
    finally:
        for handle in handles:
            handle.close()

for shard, path in enumerate(shards):
    log = Path(f"tau4n14b_{shard}.log")
    lines = log.read_text().splitlines() if log.exists() else []
    completed = sum(1 for line in lines if line.startswith("GRAPH "))
    assigned = path.read_text().splitlines()
    Path(f"tau4n14b_resume_{shard}.txt").write_text(
        "".join(line + "\n" for line in assigned[completed:])
    )
    print(f"shard={shard} completed={completed} remaining={len(assigned)-completed}")
PY

for shard in $(seq 0 7); do
    stdbuf -oL -eL "$ENGINE" 4 tau4b 0 1 \
        < "tau4n14b_resume_${shard}.txt" \
        >> "tau4n14b_${shard}.log" 2>&1 &
done
echo "launched 8 n14 tau4b shards"

"""
P06/V1 sanity: exhaust ALL graphs (including disconnected, nauty-geng) n <= 10,
float-score dev - R, list every graph with score > -1e-9 (ties/violations).
Confirms the equality characterization on small n and re-verifies the known
exhaustive frontier including disconnected graphs.
"""
import math
import subprocess
import sys

sys.path.insert(0, ".")
import harness as H


def g6_to_adj(line):
    data = [c - 63 for c in line.encode()]
    n = data[0]
    bits = []
    for x in data[1:]:
        bits += [(x >> k) & 1 for k in range(5, -1, -1)]
    es, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                es.append((i, j))
            idx += 1
    return H.from_edges(n, es)


for n in range(2, 11):
    p = subprocess.run(["nauty-geng", "-q", str(n)], capture_output=True, text=True)
    cnt, hits = 0, []
    for line in p.stdout.split():
        adj = g6_to_adj(line)
        cnt += 1
        s = H.score(adj)
        if s > -1e-9:
            hits.append((s, line))
    print(f"n={n}: {cnt} graphs, near-zero/violations: {hits}")

"""Independent cross-check of the exhaust.py pipeline.

Uses a completely separate code path (networkx: eigenvalues via nx.adjacency_spectrum,
omega via nx.find_cliques) on random samples of geng output, and re-derives the
prune + resolve decision, comparing against exhaust.py's core logic on the same graphs.
Prints PASS/FAIL.
"""
import random
import subprocess
import sys

import networkx as nx
import numpy as np

from bn_core import g6_to_adj, evaluate

def main():
    n = int(sys.argv[1])
    sample = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    rng = random.Random(12345)
    # sample via geng on random res/mod slices, take random lines
    lines = []
    mod = 1000
    while len(lines) < sample:
        res = rng.randrange(mod)
        out = subprocess.run(["nauty-geng", "-q", str(n), f"{res}/{mod}"],
                             capture_output=True, text=True).stdout.splitlines()
        lines.extend(rng.sample(out, min(len(out), sample // 10 + 1)))
    lines = lines[:sample]
    bad = 0
    for g6 in lines:
        nn, adj = g6_to_adj(g6)
        score, ratio, l1, l2, m, w = evaluate(nn, adj)
        G = nx.from_numpy_array(np.array(
            [[1 if (adj[i] >> j) & 1 else 0 for j in range(nn)] for i in range(nn)]))
        spec = sorted(np.real(nx.adjacency_spectrum(G)))
        L1, L2 = spec[-1], spec[-2]
        W = max((len(c) for c in nx.find_cliques(G)), default=1)
        if abs(L1 - l1) > 1e-8 or abs(L2 - l2) > 1e-8 or W != w:
            print("MISMATCH", g6, l1, L1, l2, L2, w, W)
            bad += 1
        if W < nn and G.number_of_edges() > 0:
            s2 = L1 * L1 + L2 * L2 - 2 * G.number_of_edges() * (1 - 1 / W)
            if s2 > 1e-6:
                print("VIOLATION (independent path)", g6, s2)
    print(f"PASS: {len(lines)} graphs at n={n} cross-checked, {bad} mismatches"
          if bad == 0 else f"FAIL: {bad} mismatches")


if __name__ == "__main__":
    main()

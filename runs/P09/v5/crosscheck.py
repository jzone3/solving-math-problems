"""Independent cross-check of the exhaustive pipeline.

1. graph6 parsing: compare g6_to_adj_batch against networkx.from_graph6_bytes
   on random samples from geng for n = 8..11.
2. score logic: for a random sample of graphs, recompute score with networkx
   (find_cliques for omega) + numpy eigvalsh and confirm score <= 1e-9, and that
   the exhaustive candidate filter (omega < 2m/(2m-L)) agrees with score > 0.
Prints PASS/FAIL.
"""
import subprocess, random
import numpy as np
import networkx as nx
from exhaustive import g6_to_adj_batch

ok = True
rng = random.Random(42)
for n in [8, 9, 10, 11]:
    out = subprocess.run(["nauty-geng", "-cq", str(n), "0/1000"],
                         capture_output=True).stdout.splitlines()
    sample = rng.sample(out, min(300, len(out)))
    A = g6_to_adj_batch(sample, n)
    for i, ln in enumerate(sample):
        G = nx.from_graph6_bytes(ln)
        B = nx.to_numpy_array(G, nodelist=sorted(G.nodes()))
        if not np.array_equal(A[i], B):
            print("PARSE MISMATCH", n, ln); ok = False
        w = max(len(c) for c in nx.find_cliques(G))
        lam = np.sort(np.linalg.eigvalsh(B))
        L = lam[-1] ** 2 + lam[-2] ** 2
        m2 = B.sum()
        if w < n:
            score = L - m2 * (1 - 1 / w)
            viol_direct = score > 1e-9
            viol_filter = (m2 - L > 1e-9 and w < m2 / (m2 - L)) or (m2 - L <= 1e-9)
            if viol_direct and not viol_filter:
                print("FILTER WOULD MISS", n, ln, score); ok = False
            if viol_direct:
                print("VIOLATION IN SAMPLE?!", n, ln, score); ok = False
    print(f"n={n}: {len(sample)} graphs cross-checked")
print("PASS" if ok else "FAIL")

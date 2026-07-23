"""A: minimal K such that h = P^K d satisfies Mh >= 0, over all connected
delta>=2 graphs at given n.  Reports histogram of minimal K (cap 30).
Usage: powK_n9.py n [res mod]
"""
import sys
import numpy as np
from collections import Counter
from common import g6_to_adj, build, geng

n = int(sys.argv[1])
res = int(sys.argv[2]) if len(sys.argv) > 2 else 0
mod = int(sys.argv[3]) if len(sys.argv) > 3 else 1
hist = Counter()
tot = 0
worst = []
for g6 in geng(n, res=res, mod=mod):
    tot += 1
    G = build(g6_to_adj(g6))
    M, P = G["M"], G["B"] / G["T"][:, None]
    h = G["d"].copy()
    K = 0
    while K <= 30 and (M @ h).min() < -1e-9:
        h = P @ h
        h = h / h.max()
        K += 1
    if K > 30:
        hist["FAIL"] += 1
        worst.append(g6)
    else:
        hist[K] += 1
print(f"n={n} res={res}/{mod}: {tot} graphs, minK hist {dict(sorted(hist.items(), key=str))}")
for g in worst[:10]:
    print("  FAIL", g)

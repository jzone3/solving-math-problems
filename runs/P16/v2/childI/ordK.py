"""Order-K CW test: P^K d <= d entrywise (P = diag(1/T)B) implies
rho(P)^K = rho(P^K) <= max_i (P^K d)_i / d_i <= 1, hence F2.
(Collatz-Wielandt upper bound holds for any nonnegative matrix and any h>0.)

Report, for each connected delta>=2 graph, the minimal K <= 30 with
P^K d <= d; histogram.  Usage: ordK.py n [res mod]
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
    P = G["B"] / G["T"][:, None]
    d = G["d"]
    h = d.copy()
    K = 1
    ok = False
    while K <= 30:
        h = P @ h
        if (h <= d + 1e-9).all():
            ok = True
            break
        K += 1
    if ok:
        hist[K] += 1
    else:
        hist["FAIL"] += 1
        worst.append(g6)
print(f"ordK n={n} res={res}/{mod}: {tot} graphs, minK hist {dict(sorted(hist.items(), key=str))}")
for g in worst[:10]:
    print("  FAIL", g)

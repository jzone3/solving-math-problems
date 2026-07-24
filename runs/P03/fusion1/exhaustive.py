"""
Exhaustive check of Woodall's conjecture (k = tau = 3) over ALL simple DAGs on
n <= N labeled vertices. Every simple DAG admits a topological order, so
enumerating arc subsets of {(i,j) : i < j} on a fixed order covers every
isomorphism class. (Parallel arcs are excluded; note rho >= 4 forces >= 8
vertices in a counterexample by ACZ 2023, so this is a consistency check /
independent confirmation for small n.)

Usage: python3 exhaustive.py N
"""

import sys
import time
from itertools import combinations

from harness import tau, has_k_disjoint_dijoins

K = 3


def run(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    P = len(pairs)
    total = 1 << P
    checked = tau3 = nonpack = 0
    t0 = time.time()
    for mask in range(total):
        arcs = [pairs[i] for i in range(P) if (mask >> i) & 1]
        if len(arcs) < 3 * 2:      # tau=3 needs >= 6 arcs (source+sink deg >= 3)
            continue
        # quick prune: every vertex must have degree >= 3 or degree 0?  No —
        # isolated vertices give an empty dicut (tau=0); any vertex with
        # 1 <= indeg+outdeg and (indeg == 0 -> outdeg >= 3), (outdeg == 0 -> indeg >= 3)
        indeg = [0] * n
        outdeg = [0] * n
        for (u, v) in arcs:
            outdeg[u] += 1
            indeg[v] += 1
        ok = True
        for v in range(n):
            d = indeg[v] + outdeg[v]
            if d == 0:
                ok = False   # isolated vertex -> disconnected -> tau=0
                break
            if indeg[v] == 0 and outdeg[v] < K:
                ok = False   # source dicut smaller than 3
                break
            if outdeg[v] == 0 and indeg[v] < K:
                ok = False
                break
        if not ok:
            continue
        t = tau(n, arcs)
        checked += 1
        if t != K:
            continue
        tau3 += 1
        if not has_k_disjoint_dijoins(n, arcs, K):
            nonpack += 1
            print("NONPACKING:", n, arcs, flush=True)
        if tau3 % 20000 == 0:
            print(f"progress mask={mask}/{total} checked={checked} tau3={tau3} "
                  f"nonpack={nonpack} t={time.time()-t0:.0f}s", flush=True)
    print(f"DONE n={n}: masks={total} passed_prune={checked} tau3={tau3} "
          f"nonpacking={nonpack} wall={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    run(int(sys.argv[1]))

"""B: exploit the freedom in D (Theorem F3 holds for ANY diagonal D = diag(s)).

For each graph, ask: does there exist s (entrywise, s_i >= 0) such that the
h = d certificate works for M(s) := 2 diag(s) + 4I - Q - diag(s) H diag(s)?
Condition (M(s) d)_i >= 0:

  2 s_i d_i + 4 d_i - d_i (d_i + m_i) - s_i sum_{j~i} w_ij (s_i d_i + s_j d_j) >= 0

Coordinate-wise: quadratic in s_i given the others.  We run projected
coordinate ascent maximizing the min slack, starting from s = sigma = d+m-4.
If feasible on all n<=8 graphs, regress s* vs local invariants.

NOTE: w depends only on degrees, not on s -- H is fixed.
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng


def slack(G, s):
    d, w, edges, Q = G["d"], G["w"], G["edges"], G["Q"]
    n = G["n"]
    r = 2 * s * d + 4 * d - Q @ d
    for k, (i, j) in enumerate(edges):
        r[i] -= s[i] * w[k] * (s[i] * d[i] + s[j] * d[j])
        r[j] -= s[j] * w[k] * (s[j] * d[j] + s[i] * d[i])
    return r


def optimize(G, iters=200):
    d = G["d"]
    s = G["sig"].copy()
    n = G["n"]
    w, edges = G["w"], G["edges"]
    # precompute neighbor weight structure
    nbrw = [[] for _ in range(n)]
    for k, (i, j) in enumerate(edges):
        nbrw[i].append((j, w[k]))
        nbrw[j].append((i, w[k]))
    for it in range(iters):
        r = slack(G, s)
        i = int(np.argmin(r))
        if r[i] >= -1e-10:
            return s, r.min()
        # solve the per-coordinate quadratic for s_i to maximize r_i,
        # but moving s_i also changes r_j for j~i; do a small line search
        # maximize min(r) along coordinate i
        Wi = sum(wk for _, wk in nbrw[i])
        best = (r.min(), s[i])
        for cand in np.linspace(0, max(2 * s[i], 4), 41):
            s2 = s.copy(); s2[i] = cand
            rm = slack(G, s2).min()
            if rm > best[0]:
                best = (rm, cand)
        if best[1] == s[i]:
            return s, r.min()  # stuck
        s[i] = best[1]
    return s, slack(G, s).min()


nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 7
tot = infeas = 0
data = []
for n in range(3, nmax + 1):
    for g6 in geng(n):
        tot += 1
        G = build(g6_to_adj(g6))
        if slack(G, G["sig"]).min() >= -1e-10:
            continue
        s, rmin = optimize(G)
        if rmin < -1e-10:
            infeas += 1
            data.append((g6, rmin))
print(f"n<={nmax}: {tot} graphs, h=d-with-optimized-s infeasible (heuristic) on {infeas}")
for g, r in data[:15]:
    print("  stuck", g, r)

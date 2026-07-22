"""Escalated V2 search: large double brooms / caterpillars / spiders (n up to ~20000).

For TREES, n+(T) = n-(T) = matching number mu(T) (classical: rank(A(T)) = 2 mu(T),
spectrum of a tree is symmetric since trees are bipartite). We exploit this to push
far past eigensolve sizes, cross-checking against a dense eigensolve for n <= 1200.

Score of interest: gap = min(n+,n-) - dev(D)  (counterexample iff gap < 0)
and ratio = dev / min(n+,n-).
"""

import sys
import numpy as np
from collections import deque
from families import double_broom, caterpillar, spider, evaluate, bfs_dists

EPS = 1e-8


def tree_matching(adj_list, n):
    """Exact maximum matching of a tree via leaf-stripping DP (iterative)."""
    deg = [len(a) for a in adj_list]
    matched = [False] * n
    removed = [False] * n
    mu = 0
    q = deque(i for i in range(n) if deg[i] == 1)
    while q:
        leaf = q.popleft()
        if removed[leaf]:
            continue
        removed[leaf] = True
        # find its remaining neighbor
        parent = -1
        for v in adj_list[leaf]:
            if not removed[v]:
                parent = v
                break
        if parent < 0:
            continue
        if not matched[leaf] and not matched[parent]:
            matched[leaf] = matched[parent] = True
            mu += 1
        # remove parent edge implicitly
        deg[parent] -= 1
        if matched[parent]:
            # parent effectively dead for matching; strip it when it becomes a leaf
            pass
        if deg[parent] == 1:
            q.append(parent)
    return mu


def dev_and_diam(edges, n):
    adj_list = [[] for _ in range(n)]
    for u, v in edges:
        adj_list[u].append(v)
        adj_list[v].append(u)
    s1 = s2 = 0
    diam = 0
    for src in range(n):
        dist = bfs_dists(adj_list, src, n)
        for d in dist:
            s1 += d
            s2 += d * d
            if d > diam:
                diam = d
    s0 = n * n
    var = s2 / s0 - (s1 / s0) ** 2
    return float(np.sqrt(max(var, 0.0))), diam, adj_list


def check(desc, edges, n, do_eig):
    dev, diam, adj_list = dev_and_diam(edges, n)
    mu = tree_matching(adj_list, n)
    if do_eig:
        A = np.zeros((n, n))
        for u, v in edges:
            A[u, v] = A[v, u] = 1.0
        ev = np.linalg.eigvalsh(A)
        npos = int(np.sum(ev > EPS))
        nneg = int(np.sum(ev < -EPS))
        assert npos == mu and nneg == mu, (desc, npos, nneg, mu)
    gap = mu - dev
    ratio = dev / mu if mu else float("inf")
    print(f"{desc:45s} n={n:6d} diam={diam:5d} dev={dev:10.4f} mu=n+=n-={mu:5d} "
          f"gap={gap:+9.4f} ratio={ratio:.5f}", flush=True)
    return gap, ratio


def main():
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    worst = (float("inf"), None)
    bestr = (0.0, None)
    cases = []
    # balanced double brooms: handle h, huge bristle count b at both ends
    for h in (10, 20, 50, 100, 200, 400, 800):
        for b in (h, 2 * h, 5 * h, 10 * h, 50 * h):
            if h + 2 * b <= max_n:
                cases.append((f"dbroom(h={h},b={b})", double_broom(h, b, b)))
    # caterpillars with 1 leg every vertex, large spine
    for s in (200, 500, 1000, 2000, 5000):
        if 2 * s <= max_n:
            cases.append((f"cat(s={s},1leg,p1)", caterpillar(s, 1, 1)))
    # spiders, many long legs
    for k in (3, 10, 50, 200):
        for L in (100, 500, 2000):
            if 1 + k * L <= max_n:
                cases.append((f"spider(k={k},L={L})", spider(k, L)))
    for desc, (edges, n) in cases:
        gap, ratio = check(desc, edges, n, do_eig=(n <= 1200))
        if gap < worst[0]:
            worst = (gap, desc)
        if ratio > bestr[0]:
            bestr = (ratio, desc)
    print(f"\nminimum gap  min(n+,n-)-dev : {worst[0]:+.4f}  at {worst[1]}")
    print(f"maximum ratio dev/min(n+,n-): {bestr[0]:.5f}  at {bestr[1]}")
    if worst[0] <= 0:
        print("COUNTEREXAMPLE CANDIDATE FOUND (verify exactly!)")
    else:
        print("no counterexample; consistent with proof dev < ceil(diam/2) <= mu")


if __name__ == "__main__":
    main()

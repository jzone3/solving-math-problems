#!/usr/bin/env python3
"""Probe: can any graph with n < 118 violate conjecture 154?
Simulated annealing over connected graphs at fixed n, score = 2*m*S^2 /
(n^3 * C(n,2)^2) (pairs convention; >1 means violation). Seeded from the best
lollipop of that size. Exact integer S via all-pairs BFS each eval."""
import random
import sys
from collections import deque
from math import comb


def bfs_S(adj, n):
    tot = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        seen = 1
        while q:
            x = q.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    seen += 1
                    q.append(y)
        if seen < n:
            return None
        tot += sum(dist)
    return tot // 2


def score(adj, n):
    S = bfs_S(adj, n)
    if S is None:
        return None
    m = sum(len(a) for a in adj) // 2
    return 2 * m * S * S / (n ** 3 * comb(n, 2) ** 2), m, S


def lollipop_adj(a, l):
    n = a + l
    adj = [set() for _ in range(n)]
    for i in range(a):
        for j in range(i + 1, a):
            adj[i].add(j)
            adj[j].add(i)
    chain = [0] + list(range(a, n))
    for x, y in zip(chain, chain[1:]):
        adj[x].add(y)
        adj[y].add(x)
    return adj


def anneal(n, iters=4000, seed=0):
    rng = random.Random(seed)
    # seed from best lollipop split for this n
    best = None
    for a in range(2, n):
        adj = lollipop_adj(a, n - a)
        sc = score(adj, n)
        if best is None or sc[0] > best[0]:
            best = (sc[0], a)
    a = best[1]
    adj = lollipop_adj(a, n - a)
    cur = score(adj, n)[0]
    best_sc = cur
    T0, T1 = 0.002, 0.00005
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue
        if v in adj[u]:
            adj[u].discard(v)
            adj[v].discard(u)
            added = False
        else:
            adj[u].add(v)
            adj[v].add(u)
            added = True
        sc = score(adj, n)
        if sc is None:
            new = None
        else:
            new = sc[0]
        if new is not None and (new >= cur or rng.random() < pow(2.718, (new - cur) / T)):
            cur = new
            if cur > best_sc:
                best_sc = cur
                if cur > 1:
                    print(f"n={n}: VIOLATION found, score={cur}")
                    return best_sc
        else:  # revert
            if added:
                adj[u].discard(v)
                adj[v].discard(u)
            else:
                adj[u].add(v)
                adj[v].add(u)
    return best_sc


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [100, 110, 115, 117]
    for n in ns:
        for seed in range(2):
            b = anneal(n, iters=3000, seed=seed)
            print(f"n={n} seed={seed}: best score {b:.5f}")

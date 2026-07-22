"""V2 structured-construction search for Graffiti 39/40 (P08).

Conjectures (WoW 39/40, RC-2025 encoding): for every connected G,
  dev(D) <= n+(G)   and   dev(D) <= n-(G),
where dev(D) = population std-dev of all n^2 entries of the distance matrix
and n+/n- = number of positive/negative adjacency eigenvalues.

This module builds parameterized long-diameter, spectrally degenerate families
(brooms, double brooms, caterpillars with periodic legs, subdivided stars/spiders,
complete multipartite + pendant paths, kite/lollipop) and scores them:
  score = dev(D) - min(n+, n-).
It also checks the proof chain  dev <= diam/2 <= ceil(diam/2) <= min(n+, n-)
on every instance evaluated.
"""

import numpy as np
from collections import deque

EPS = 1e-8


def bfs_dists(adj_list, src, n):
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj_list[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def evaluate(edges, n):
    """Return dict with dev, n+, n-, diam, score39, score40 for graph on n nodes."""
    adj_list = [[] for _ in range(n)]
    for u, v in edges:
        adj_list[u].append(v)
        adj_list[v].append(u)
    # distances (exact integers)
    s0 = s1 = s2 = 0  # count, sum, sum of squares over all n^2 entries
    diam = 0
    for src in range(n):
        dist = bfs_dists(adj_list, src, n)
        for d in dist:
            if d < 0:
                return None  # disconnected
            s1 += d
            s2 += d * d
            if d > diam:
                diam = d
    s0 = n * n
    var = s2 / s0 - (s1 / s0) ** 2
    dev = np.sqrt(max(var, 0.0))
    A = np.zeros((n, n))
    for u, v in edges:
        A[u, v] = A[v, u] = 1.0
    ev = np.linalg.eigvalsh(A)
    npos = int(np.sum(ev > EPS))
    nneg = int(np.sum(ev < -EPS))
    return dict(n=n, dev=dev, npos=npos, nneg=nneg, diam=diam,
                score39=dev - npos, score40=dev - nneg,
                var_num=(s0 * s2 - s1 * s1), var_den=s0 * s0)  # exact variance = var_num/var_den


# ---------- families ----------

def path_edges(n, offset=0):
    return [(offset + i, offset + i + 1) for i in range(n - 1)]


def broom(handle, bristles):
    """Path of `handle` vertices with `bristles` pendant leaves at one end."""
    n = handle + bristles
    e = path_edges(handle)
    e += [(handle - 1, handle + i) for i in range(bristles)]
    return e, n


def double_broom(handle, b1, b2):
    n = handle + b1 + b2
    e = path_edges(handle)
    e += [(0, handle + i) for i in range(b1)]
    e += [(handle - 1, handle + b1 + i) for i in range(b2)]
    return e, n


def caterpillar(spine, legs_per, period=1):
    """Spine path; every `period`-th spine vertex gets `legs_per` pendant leaves."""
    e = path_edges(spine)
    n = spine
    for i in range(0, spine, period):
        for _ in range(legs_per):
            e.append((i, n))
            n += 1
    return e, n


def caterpillar_legpattern(spine, pattern):
    """pattern: list of leg-counts repeated periodically along the spine."""
    e = path_edges(spine)
    n = spine
    for i in range(spine):
        for _ in range(pattern[i % len(pattern)]):
            e.append((i, n))
            n += 1
    return e, n


def spider(nlegs, leglen):
    """Subdivided star: center + nlegs paths of length leglen."""
    e = []
    n = 1
    for _ in range(nlegs):
        prev = 0
        for _ in range(leglen):
            e.append((prev, n))
            prev = n
            n += 1
    return e, n


def multipartite_plus_path(parts, tail):
    """Complete multipartite K(parts) with a pendant path of `tail` vertices."""
    sizes = list(parts)
    idx = []
    n = 0
    for s in sizes:
        idx.append(list(range(n, n + s)))
        n += s
    e = []
    for a in range(len(sizes)):
        for b in range(a + 1, len(sizes)):
            for u in idx[a]:
                for v in idx[b]:
                    e.append((u, v))
    prev = 0
    for _ in range(tail):
        e.append((prev, n))
        prev = n
        n += 1
    return e, n


def kite(clique, tail):
    """K_clique with pendant path of `tail` vertices (lollipop)."""
    e = [(i, j) for i in range(clique) for j in range(i + 1, clique)]
    n = clique
    prev = 0
    for _ in range(tail):
        e.append((prev, n))
        prev = n
        n += 1
    return e, n

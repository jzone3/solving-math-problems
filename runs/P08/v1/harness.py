"""P08 V1 harness: invariants for Graffiti 39/40.

dev(D): population std over all n^2 entries of the distance matrix
        (matches Roucairol-Cazenave refutationGBR encoding).
n+ / n-: number of adjacency eigenvalues > tol / < -tol (tol=1e-4, matching RC).
Also computes diameter and the proof-chain quantities.
"""
import numpy as np
from collections import deque


def bfs_dist_row(adj_list, src, n):
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


def invariants(adj_list, n, tol=1e-4):
    """Return dict with dev, npos, nneg, diam. adj_list: list of neighbor lists."""
    total = 0.0
    total_sq = 0.0
    diam = 0
    for s in range(n):
        row = bfs_dist_row(adj_list, s, n)
        for d in row:
            if d < 0:
                return None  # disconnected
            total += d
            total_sq += d * d
            if d > diam:
                diam = d
    m = n * n
    mean = total / m
    var = total_sq / m - mean * mean
    dev = np.sqrt(max(var, 0.0))
    A = np.zeros((n, n))
    for u in range(n):
        for v in adj_list[u]:
            A[u, v] = 1.0
    eig = np.linalg.eigvalsh(A)
    npos = int((eig > tol).sum())
    nneg = int((eig < -tol).sum())
    return dict(dev=dev, npos=npos, nneg=nneg, diam=diam)


def edges_to_adjlist(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def check(adj_list, n):
    """Return (inv, score39, score40, lemma_ok). lemma: dev <= d/2 <= floor((d+1)/2) <= min(n+,n-)."""
    inv = invariants(adj_list, n)
    if inv is None:
        return None
    s39 = inv["dev"] - inv["npos"]
    s40 = inv["dev"] - inv["nneg"]
    d = inv["diam"]
    lemma_ok = (inv["dev"] <= d / 2 + 1e-9) and ((d + 1) // 2 <= min(inv["npos"], inv["nneg"]))
    return inv, s39, s40, lemma_ok

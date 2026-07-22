"""Core utilities for P09 (Bollobas-Nikiforov) V5 run.

Score(G) = lam1^2 + lam2^2 - 2m(1 - 1/omega).  Conjecture: score <= 0 for all G != K_n.
A positive score on any non-complete graph is a counterexample.
"""
import numpy as np
import random

def adj_from_edges(n, edges):
    A = np.zeros((n, n))
    for u, v in edges:
        A[u, v] = A[v, u] = 1.0
    return A

def top2(A):
    w = np.linalg.eigvalsh(A)
    return w[-1], w[-2]

def max_clique(A):
    """Exact max clique via Tomita-style branch and bound with greedy coloring."""
    n = A.shape[0]
    adj = [frozenset(np.nonzero(A[i])[0].tolist()) for i in range(n)]
    best = [0]

    def color_sort(P):
        # greedy coloring; returns vertices ordered with color bounds
        order, bounds = [], []
        Pset = list(P)
        color_classes = []
        for v in sorted(Pset, key=lambda x: -len(adj[x] & set(Pset))):
            placed = False
            for ci, cl in enumerate(color_classes):
                if not (adj[v] & cl):
                    cl.add(v)
                    placed = True
                    break
            if not placed:
                color_classes.append({v})
        for ci, cl in enumerate(color_classes):
            for v in cl:
                order.append(v)
                bounds.append(ci + 1)
        return order, bounds

    def expand(R, P):
        if not P:
            best[0] = max(best[0], len(R))
            return
        order, bounds = color_sort(P)
        for i in range(len(order) - 1, -1, -1):
            if len(R) + bounds[i] <= best[0]:
                return
            v = order[i]
            expand(R + [v], P & adj[v])
            P = P - {v}

    expand([], frozenset(range(n)))
    return best[0]

def score(A, omega=None):
    n = A.shape[0]
    m = A.sum() / 2
    if omega is None:
        omega = max_clique(A)
    if omega >= n:  # complete graph excluded
        return None, omega
    l1, l2 = top2(A)
    return l1 * l1 + l2 * l2 - 2 * m * (1 - 1 / omega), omega

def turan_graph(n, r):
    parts = [n // r + (1 if i < n % r else 0) for i in range(r)]
    edges, offs, s = [], [], 0
    for p in parts:
        offs.append((s, s + p)); s += p
    for i in range(r):
        for j in range(i + 1, r):
            for u in range(*offs[i]):
                for v in range(*offs[j]):
                    edges.append((u, v))
    return adj_from_edges(n, edges)

def union(A, B):
    n, k = A.shape[0], B.shape[0]
    C = np.zeros((n + k, n + k))
    C[:n, :n] = A
    C[n:, n:] = B
    return C

def join(A, B):
    C = union(A, B)
    n = A.shape[0]
    C[:n, n:] = 1.0
    C[n:, :n] = 1.0
    return C

"""Parametric structured families living in the open region
(connected, irregular, many triangles, omega>=3), scanned exactly.

Families:
  A. Two balanced Turan blobs overlapping in a q-set (q < r so omega stays r).
  B. Balanced Turan graph with a pendant clique K_s attached at a vertex.
  C. K_a join (T(n1,r-a) union T(n2,r-a))  -- join lifts omega by a.
  D. Two balanced Turan blobs joined by a sparse bipartite bridge of b edges.
  E. Turan blowup of a 5-cycle / Petersen-like frames (quasi-random, many triangles).
Reports max score per family (must stay <= 0).
"""
import itertools
import numpy as np
from core import adj_from_edges, turan_graph, union, join, score

def report(name, A, best):
    s, w = score(A)
    if s is not None and s > best[0]:
        best[0] = s; best[1] = name
    if s is not None and s > -0.05:
        print(f"  near-tight: {name} score={s:+.6f} w={w}")
    return s

def famA():
    best = [-1e9, None]
    for r in [3, 4, 5]:
        for k1 in [1, 2, 3]:
            for k2 in [1, 2, 3]:
                for q in range(1, r):
                    n1, n2 = k1 * r, k2 * r
                    n = n1 + n2 - q
                    A = np.zeros((n, n))
                    A[:n1, :n1] = turan_graph(n1, r)
                    B = turan_graph(n2, r)
                    idx = list(range(n1 - q, n1)) + list(range(n1, n))
                    for a in range(n2):
                        for b in range(n2):
                            if B[a, b]:
                                A[idx[a], idx[b]] = 1
                    report(f"A r={r} k1={k1} k2={k2} q={q}", A, best)
    print("Family A best:", best)

def famB():
    best = [-1e9, None]
    for r in [3, 4, 5]:
        for k in [1, 2, 3, 4]:
            for s in range(2, r + 1):
                n1 = k * r
                n = n1 + s - 1
                A = np.zeros((n, n))
                A[:n1, :n1] = turan_graph(n1, r)
                verts = [0] + list(range(n1, n))
                for a, b in itertools.combinations(verts, 2):
                    A[a, b] = A[b, a] = 1
                report(f"B r={r} k={k} s={s}", A, best)
    print("Family B best:", best)

def famC():
    best = [-1e9, None]
    for a in [1, 2, 3]:
        for r0 in [2, 3, 4]:
            for k1 in [1, 2, 3]:
                for k2 in [1, 2, 3]:
                    Ka = np.ones((a, a)) - np.eye(a)
                    U = union(turan_graph(k1 * r0, r0), turan_graph(k2 * r0, r0))
                    A = join(Ka, U)
                    report(f"C a={a} r0={r0} k1={k1} k2={k2}", A, best)
    print("Family C best:", best)

def famD():
    rng = np.random.default_rng(7)
    best = [-1e9, None]
    for r in [3, 4, 5]:
        for k in [2, 3]:
            n1 = k * r
            base = union(turan_graph(n1, r), turan_graph(n1, r))
            n = 2 * n1
            for b in [1, 2, 3, 5, 8]:
                for trial in range(30):
                    A = base.copy()
                    cnt = 0
                    while cnt < b:
                        i = rng.integers(0, n1); j = rng.integers(n1, n)
                        if not A[i, j]:
                            A[i, j] = A[j, i] = 1; cnt += 1
                    report(f"D r={r} k={k} b={b} t={trial}", A, best)
    print("Family D best:", best)

def famE():
    best = [-1e9, None]
    # blowups of C5 and Petersen by cliques/independent sets
    C5 = [(i, (i + 1) % 5) for i in range(5)]
    for t in [2, 3, 4]:
        for mode in ["clique", "indep"]:
            n = 5 * t
            A = np.zeros((n, n))
            for u, v in C5:
                for a in range(t):
                    for b in range(t):
                        A[u * t + a, v * t + b] = A[v * t + b, u * t + a] = 1
            if mode == "clique":
                for u in range(5):
                    for a in range(t):
                        for b in range(a + 1, t):
                            A[u * t + a, u * t + b] = A[u * t + b, u * t + a] = 1
            report(f"E C5 t={t} {mode}", A, best)
    print("Family E best:", best)

if __name__ == "__main__":
    famA(); famB(); famC(); famD(); famE()

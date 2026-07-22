#!/usr/bin/env python3
"""Independent verifier for P08 (Graffiti 39 & 40) proof-chain lemmas and conjectures.

Checks, on exhaustive small graphs and random graphs/trees:
  (a) dev(D) <= diam/2                      [Popoviciu step]
  (b) floor((diam+1)/2) <= min(n+, n-)      [interlacing + path inertia step]
  (c) dev(D) <= min(n+, n-)                 [conjectures 39 & 40]

dev(D) = population std over all n^2 entries of the distance matrix
(Roucairol-Cazenave refutationGBR convention). Inertia computed two ways:
float eigensolve AND exact rational symmetric Gaussian elimination
(Sylvester's law of inertia), which must agree.

Dependencies: numpy only. Prints PASS on success.
"""
import itertools
import math
import random
from fractions import Fraction

import numpy as np


def floyd_warshall(A, n):
    INF = float("inf")
    D = [[0 if i == j else (1 if A[i][j] else INF) for j in range(n)] for i in range(n)]
    for k in range(n):
        Dk = D[k]
        for i in range(n):
            dik = D[i][k]
            if dik == INF:
                continue
            Di = D[i]
            for j in range(n):
                v = dik + Dk[j]
                if v < Di[j]:
                    Di[j] = v
    return D


def dev_and_diam(D, n):
    vals = [D[i][j] for i in range(n) for j in range(n)]
    if any(v == float("inf") for v in vals):
        return None, None
    m = n * n
    mean = sum(vals) / m
    var = sum((v - mean) ** 2 for v in vals) / m
    return math.sqrt(var), max(vals)


def inertia_exact(A, n):
    """Exact inertia of a symmetric integer matrix via rational symmetric elimination.

    Sylvester's law: congruence preserves inertia. Handle zero pivots with the
    standard 2x2 hyperbolic-pair trick (a zero diagonal with nonzero off-diagonal
    contributes one positive and one negative eigenvalue).
    """
    M = [[Fraction(A[i][j]) for j in range(n)] for i in range(n)]
    idx = list(range(n))
    pos = neg = zero = 0
    k = 0
    size = n
    while size > 0:
        # find nonzero diagonal pivot
        p = next((i for i in range(size) if M[i][i] != 0), None)
        if p is not None:
            piv = M[p][p]
            if piv > 0:
                pos += 1
            else:
                neg += 1
            # eliminate row/col p
            rest = [i for i in range(size) if i != p]
            newM = [[M[i][j] - M[i][p] * M[p][j] / piv for j in rest] for i in rest]
            M = newM
            size -= 1
            continue
        # all diagonal zero: find off-diagonal nonzero
        q = None
        for i in range(size):
            for j in range(i + 1, size):
                if M[i][j] != 0:
                    q = (i, j)
                    break
            if q:
                break
        if q is None:
            zero += size
            break
        i, j = q
        b = M[i][j]
        pos += 1
        neg += 1
        rest = [r for r in range(size) if r not in (i, j)]
        # eliminate the 2x2 block [[0,b],[b,0]]: for remaining rows r,s:
        # M'[r][s] = M[r][s] - (M[r][i]*M[j][s] + M[r][j]*M[i][s]) / b
        newM = [[M[r][s] - (M[r][i] * M[j][s] + M[r][j] * M[i][s]) / b for s in rest]
                for r in rest]
        M = newM
        size -= 2
    return pos, neg


def inertia_float(A, n, tol=1e-8):
    eig = np.linalg.eigvalsh(np.array(A, dtype=float))
    return int((eig > tol).sum()), int((eig < -tol).sum())


checked = 0


def check_graph(A, n, exact=True):
    global checked
    D = floyd_warshall(A, n)
    dev, diam = dev_and_diam(D, n)
    if dev is None:
        return  # disconnected
    npos_f, nneg_f = inertia_float(A, n)
    if exact:
        npos_e, nneg_e = inertia_exact(A, n)
        assert (npos_f, nneg_f) == (npos_e, nneg_e), \
            f"inertia mismatch n={n}: float {(npos_f, nneg_f)} exact {(npos_e, nneg_e)}"
    npos, nneg = npos_f, nneg_f
    assert dev <= diam / 2 + 1e-9, f"(a) FAIL n={n} dev={dev} diam={diam}"
    assert (diam + 1) // 2 <= min(npos, nneg) or diam == 0, \
        f"(b) FAIL n={n} diam={diam} npos={npos} nneg={nneg}"
    assert dev <= min(npos, nneg) + 1e-9, \
        f"(c) FAIL (CONJECTURE VIOLATED) n={n} dev={dev} npos={npos} nneg={nneg}"
    checked += 1


def all_graphs_up_to(nmax):
    for n in range(2, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            A = [[0] * n for _ in range(n)]
            for b, (i, j) in enumerate(pairs):
                if mask >> b & 1:
                    A[i][j] = A[j][i] = 1
            check_graph(A, n, exact=(n <= 5))


def random_tree(n, rng):
    A = [[0] * n for _ in range(n)]
    for v in range(1, n):
        u = rng.randrange(v)
        A[u][v] = A[v][u] = 1
    return A


def random_connected_graph(n, p, rng):
    A = random_tree(n, rng)  # spanning tree ensures connectivity
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                A[i][j] = A[j][i] = 1
    return A


def main():
    rng = random.Random(12345)
    print("exhaustive: all graphs on <= 6 vertices (exact inertia for n<=5)...")
    all_graphs_up_to(6)
    print(f"  ok ({checked} connected graphs so far)")
    print("random trees n in [10,400] ...")
    for _ in range(300):
        n = rng.randrange(10, 401)
        check_graph(random_tree(n, rng), n, exact=False)
    print("random connected graphs ...")
    for _ in range(300):
        n = rng.randrange(10, 121)
        p = rng.choice([0.02, 0.05, 0.1, 0.3, 0.7])
        check_graph(random_connected_graph(n, p, rng), n, exact=False)
    print("exact-inertia cross-check on random graphs n<=12 ...")
    for _ in range(100):
        n = rng.randrange(4, 13)
        check_graph(random_connected_graph(n, 0.3, rng), n, exact=True)
    print(f"total graphs checked: {checked}")
    print("PASS")


if __name__ == "__main__":
    main()

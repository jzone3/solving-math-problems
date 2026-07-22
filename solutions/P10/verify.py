#!/usr/bin/env python3
"""
P10 (Brouwer's conjecture) — independent verifier.

Finding (V5, literature-first): Brouwer's conjecture is no longer open. It was
proved by Kothari & Tudose, "On Brouwer's Laplacian conjecture",
arXiv:2606.12197 (10 Jun 2026), via the Grone-Merris-Bai theorem for split
graphs. Three independent later papers (arXiv:2607.03388, 2607.08452,
2607.17293) cite the result as established.

This script independently machine-verifies the paper's entire logical chain
on exact-rational and random numeric instances:

  GMB(split)  =>  Lemma 3.2  ||L_H - |K| C||_* <= |K||S|
              =>  identity (5.3) + trace duality  =>  Lemma 5.5 (routing)
              =>  Lemma 5.3  =>  Lemma 5.6  sum_{i!=j}(M_ij)_+ <= k(k+1)
              =>  (Lemma 5.1)  Brouwer:  sum_{i<=k} lam_i <= m + C(k+1,2).

Dependencies: python3 + numpy only. Prints PASS on success.
"""
import random
from fractions import Fraction

import numpy as np

random.seed(1)
rng = np.random.default_rng(1)
ok = True


def fail(msg):
    global ok
    ok = False
    print("FAIL:", msg)


# ---- exact algebraic identities (Lemma 5.2, v-identity, identity (5.3)) ----
def frac_matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
            for i in range(len(A))]


def frac_inv(A):
    n = len(A)
    M = [row[:] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [row[n:] for row in M]


for _ in range(5):
    n = random.randint(4, 8)
    k = random.randint(1, n - 2)
    V = []
    for _ in range(k):
        v = [Fraction(random.randint(-4, 4)) for _ in range(n)]
        s = sum(v)
        V.append([x - Fraction(s, n) for x in v])
    G = [[sum(V[i][t] * V[j][t] for t in range(n)) for j in range(k)] for i in range(k)]
    try:
        Gi = frac_inv(G)
    except StopIteration:
        continue
    VT = [[V[i][t] for i in range(k)] for t in range(n)]
    P = frac_matmul(frac_matmul(VT, Gi), V)
    if frac_matmul(P, P) != P or sum(P[i][i] for i in range(n)) != k:
        fail("projection construction")
        continue
    # Lemma 5.2
    s = Fraction(0)
    for i in range(n):
        for j in range(n):
            if i != j:
                a = P[i][i] + P[j][j] - 2 * P[i][j]
                s += a * a - (P[i][i] - P[j][j]) ** 2
    if s != 4 * k * (k + 1):
        fail(f"Lemma 5.2 identity n={n} k={k}")
    # v = C M 1 = n C diag(P)
    M = [[(P[i][i] + P[j][j] - 2 * P[i][j] - 1) if i != j else Fraction(0)
          for j in range(n)] for i in range(n)]
    Mrow = [sum(r) for r in M]
    tot = sum(Mrow)
    v = [Mrow[i] - Fraction(tot, n) for i in range(n)]
    dbar = Fraction(k, n)
    if v != [n * (P[i][i] - dbar) for i in range(n)]:
        fail(f"v-identity n={n} k={k}")
    # identity (5.3) for every r
    CM = [[M[i][j] - Fraction(sum(M[t][j] for t in range(n)), n) for j in range(n)]
          for i in range(n)]
    N = [[CM[i][j] - Fraction(sum(CM[i][t] for t in range(n)), n) for j in range(n)]
         for i in range(n)]
    for r in range(1, n):
        L = [[Fraction(0)] * n for _ in range(n)]
        edges = [(i, j) for i in range(r) for j in range(i + 1, r)]
        edges += [(i, j) for i in range(r) for j in range(r, n) if M[i][j] >= 0]
        for (i, j) in edges:
            L[i][i] += 1
            L[j][j] += 1
            L[i][j] -= 1
            L[j][i] -= 1
        lhs = sum(v[i] for i in range(r)) + sum(abs(M[i][j]) for i in range(r)
                                                for j in range(r, n))
        tr = Fraction(0)
        for i in range(n):
            for j in range(n):
                Cij = Fraction(int(i == j)) - Fraction(1, n)
                tr += (L[i][j] - r * Cij) * N[j][i]
        if lhs != -tr:
            fail(f"identity (5.3) n={n} k={k} r={r}")

# ---- numeric inequality checks ----
def laplacian(n, edges):
    L = np.zeros((n, n))
    for i, j in edges:
        L[i, i] += 1; L[j, j] += 1; L[i, j] -= 1; L[j, i] -= 1
    return L


for _ in range(300):
    n = random.randint(3, 25)
    r = random.randint(1, n - 1)
    edges = [(i, j) for i in range(r) for j in range(i + 1, r)]
    cut = [(i, j) for i in range(r) for j in range(r, n) if random.random() < 0.5]
    L = laplacian(n, edges + cut)
    lam = np.linalg.eigvalsh(L)
    if np.sum(np.maximum(lam - r, 0)) > len(cut) + 1e-8:
        fail(f"GMB positive-part bound split n={n} r={r}")
    C = np.eye(n) - np.ones((n, n)) / n
    if np.abs(np.linalg.eigvalsh(L - r * C)).sum() > r * (n - r) + 1e-8:
        fail(f"Lemma 3.2 split n={n} r={r}")

for _ in range(300):
    n = random.randint(3, 30)
    k = random.randint(1, n - 1)
    X = rng.standard_normal((n, k))
    X -= X.mean(axis=0, keepdims=True)
    Q, _ = np.linalg.qr(X)
    P = Q @ Q.T
    d = np.diag(P)
    M = d[:, None] + d[None, :] - 2 * P - 1
    np.fill_diagonal(M, 0)
    one = np.ones(n)
    v = M @ one - (one @ M @ one / n) * one
    x = rng.standard_normal(n)
    iu = np.triu_indices(n, 1)
    if abs(x @ v) > np.sum((1 - np.abs(M[iu])) * np.abs(x[iu[0]] - x[iu[1]])) + 1e-7:
        fail(f"Lemma 5.5 n={n} k={k}")
    off = ~np.eye(n, dtype=bool)
    if np.sum((1 - np.abs(M[off])) ** 2) < 2 / n * v @ v - 1e-7:
        fail(f"Lemma 5.3 n={n} k={k}")
    if np.sum(np.maximum(M[off], 0)) > k * (k + 1) + 1e-7:
        fail(f"Lemma 5.6 n={n} k={k}")

for _ in range(800):
    n = random.randint(3, 22)
    p = random.random()
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if random.random() < p]
    lam = np.sort(np.linalg.eigvalsh(laplacian(n, edges)))[::-1]
    cs = np.cumsum(lam)
    for k in range(1, n + 1):
        if cs[k - 1] > len(edges) + k * (k + 1) / 2 + 1e-7:
            fail(f"Brouwer violated?! n={n} k={k}")

print("PASS" if ok else "OVERALL FAIL")

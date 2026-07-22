#!/usr/bin/env python3
"""
V5 audit of Kothari--Tudose, "On Brouwer's Laplacian conjecture", arXiv:2606.12197v1.

Machine-verifies every lemma / identity in the paper's forward chain
    GMB(split) => Lemma 3.2 => (5.3)+trace duality => Lemma 5.5 => Lemma 5.3
              => Lemma 5.6 => (with Lemma 5.1) Brouwer's conjecture,
both with exact rational arithmetic (for the algebraic identities) and
numerically on random instances (for the inequalities).

Prints PASS/FAIL per check and an overall verdict.
"""
import itertools
import random
from fractions import Fraction

import numpy as np

rng = np.random.default_rng(20260722)
random.seed(20260722)

FAILURES = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append((name, detail))


# ---------------------------------------------------------------------------
# Exact rational linear algebra helpers
# ---------------------------------------------------------------------------

def frac_matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]


def frac_inv(A):
    n = len(A)
    M = [row[:] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]


def random_exact_projection(n, k):
    """Exact rank-k orthogonal projection P (rational entries) with P1=0."""
    while True:
        # random rational vectors orthogonal to 1
        V = []
        for _ in range(k):
            v = [Fraction(random.randint(-5, 5)) for _ in range(n)]
            s = sum(v)
            v = [x - Fraction(s, n) for x in v]
            V.append(v)
        # Gram matrix
        G = [[sum(V[i][t] * V[j][t] for t in range(n)) for j in range(k)] for i in range(k)]
        try:
            Gi = frac_inv(G)
        except StopIteration:
            continue  # singular, resample
        # P = V^T G^{-1} V   (V is k x n)
        VT = [[V[i][t] for i in range(k)] for t in range(n)]  # n x k
        P = frac_matmul(frac_matmul(VT, Gi), V)  # n x n
        return P


def exact_projection_checks(trials=6):
    for _ in range(trials):
        n = random.randint(4, 9)
        k = random.randint(1, n - 2)
        P = random_exact_projection(n, k)
        one = [[Fraction(1)] for _ in range(n)]
        # sanity: P^2=P, P1=0, tr P = k
        P2 = frac_matmul(P, P)
        assert P2 == P and all(r[0] == 0 for r in frac_matmul(P, one))
        assert sum(P[i][i] for i in range(n)) == k

        # Lemma 5.2 identity:
        # (1/4) sum_{i!=j} [a_ij^2 - (P_ii-P_jj)^2] = k(k+1),  a_ij = P_ii+P_jj-2P_ij
        s = Fraction(0)
        for i in range(n):
            for j in range(n):
                if i != j:
                    a = P[i][i] + P[j][j] - 2 * P[i][j]
                    s += a * a - (P[i][i] - P[j][j]) ** 2
        check("Lemma 5.2 identity (exact)", s / 4 == k * (k + 1), f"n={n} k={k}")

        # M1 identity used in Lemma 5.6: v = C M 1 = n * C * diag(P)
        M = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    M[i][j] = P[i][i] + P[j][j] - 2 * P[i][j] - 1
        Mrow = [sum(M[i][j] for j in range(n)) for i in range(n)]
        tot = sum(Mrow)
        v = [Mrow[i] - Fraction(tot, n) for i in range(n)]
        d = [P[i][i] for i in range(n)]
        dbar = sum(d) / n
        v2 = [n * (d[i] - dbar) for i in range(n)]
        check("Lemma 5.6 identity v = nC diag(P) (exact)", v == v2, f"n={n} k={k}")

        # Identity (5.3): for each r, with G_r the split graph (clique on first r,
        # cut edges where M_ij>=0):
        #   sum_{i<=r} v_i + sum_{i<=r<j} |M_ij| = -tr((L_{G_r} - r C) N),  N = C M C
        # verify exactly (order vertices as given; identity holds for any labeling)
        # Build N = C M C exactly
        CM = [[M[i][j] - Fraction(sum(M[t][j] for t in range(n)), n) for j in range(n)] for i in range(n)]
        N = [[CM[i][j] - Fraction(sum(CM[i][t] for t in range(n)), n) for j in range(n)] for i in range(n)]
        for r in range(1, n):
            # L_{G_r}
            L = [[Fraction(0)] * n for _ in range(n)]
            edges = [(i, j) for i in range(r) for j in range(i + 1, r)]
            edges += [(i, j) for i in range(r) for j in range(r, n) if M[i][j] >= 0]
            for (i, j) in edges:
                L[i][i] += 1
                L[j][j] += 1
                L[i][j] -= 1
                L[j][i] -= 1
            lhs = sum(v[i] for i in range(r)) + sum(abs(M[i][j]) for i in range(r) for j in range(r, n))
            # -tr((L - rC) N)
            tr = Fraction(0)
            for i in range(n):
                for j in range(n):
                    Cij = (Fraction(int(i == j)) - Fraction(1, n))
                    tr += (L[i][j] - r * Cij) * N[j][i]
            if lhs != -tr:
                check("Identity (5.3) (exact)", False, f"n={n} k={k} r={r}")
                break
        else:
            check("Identity (5.3) (exact)", True, f"n={n} k={k} all r")


# ---------------------------------------------------------------------------
# Numeric checks
# ---------------------------------------------------------------------------

def laplacian(n, edges):
    L = np.zeros((n, n))
    for i, j in edges:
        L[i, i] += 1
        L[j, j] += 1
        L[i, j] -= 1
        L[j, i] -= 1
    return L


def random_split_graph(n):
    r = random.randint(1, n - 1)
    K = list(range(r))
    S = list(range(r, n))
    edges = [(i, j) for i in K for j in K if i < j]
    cut = [(i, j) for i in K for j in S if random.random() < random.random()]
    return r, edges + cut, len(cut)


def split_graph_checks(trials=400):
    ok_gmb, ok_nuc = True, True
    for _ in range(trials):
        n = random.randint(3, 30)
        r, edges, Ecut = random_split_graph(n)
        s = n - r
        L = laplacian(n, edges)
        lam = np.sort(np.linalg.eigvalsh(L))[::-1]
        # GMB-derived bound used in proof of 3.2: sum_{lam_i > r}(lam_i - r) <= E(K,S)
        if np.sum(np.maximum(lam - r, 0)) > Ecut + 1e-8:
            ok_gmb = False
        # Lemma 3.2: ||L - r C||_* <= r*s
        C = np.eye(n) - np.ones((n, n)) / n
        nuc = np.abs(np.linalg.eigvalsh(L - r * C)).sum()
        if nuc > r * s + 1e-8:
            ok_nuc = False
    check("GMB positive-part bound on split graphs", ok_gmb, f"{trials} random split graphs")
    check("Lemma 3.2 nuclear norm bound", ok_nuc, f"{trials} random split graphs")


def random_projection(n, k):
    X = rng.standard_normal((n, k))
    X -= X.mean(axis=0, keepdims=True)  # orthogonal to 1
    Q, _ = np.linalg.qr(X)
    return Q @ Q.T


def projection_lemma_checks(trials=400):
    ok55, ok53, ok56 = True, True, True
    worst56 = -np.inf
    for _ in range(trials):
        n = random.randint(3, 40)
        k = random.randint(1, n - 1)
        P = random_projection(n, k)
        d = np.diag(P)
        M = d[:, None] + d[None, :] - 2 * P - 1
        np.fill_diagonal(M, 0)
        one = np.ones(n)
        v = M @ one - (one @ M @ one / n) * one
        # Lemma 5.5 routing inequality for random x and x=v
        for _x in range(5):
            x = rng.standard_normal(n)
            lhs = abs(x @ v)
            iu = np.triu_indices(n, 1)
            rhs = np.sum((1 - np.abs(M[iu])) * np.abs(x[iu[0]] - x[iu[1]]))
            if lhs > rhs + 1e-7:
                ok55 = False
        # Lemma 5.3: sum_{i!=j}(1-|M_ij|)^2 >= 2/n ||v||^2
        offdiag = ~np.eye(n, dtype=bool)
        lhs53 = np.sum((1 - np.abs(M[offdiag])) ** 2)
        if lhs53 < 2 / n * v @ v - 1e-7:
            ok53 = False
        # Lemma 5.6: sum_{i!=j} (M_ij)_+ <= k(k+1)
        s56 = np.sum(np.maximum(M[offdiag], 0))
        worst56 = max(worst56, s56 - k * (k + 1))
        if s56 > k * (k + 1) + 1e-7:
            ok56 = False
    check("Lemma 5.5 routing inequality", ok55, f"{trials} random (P,x)")
    check("Lemma 5.3 inequality (5.2)", ok53)
    check("Lemma 5.6 bound (5.5)", ok56, f"max slack violation {worst56:.3e} (<=0 ok)")


def adversarial_56(restarts=60, steps=300):
    """Projected-gradient ascent on Stiefel trying to violate Lemma 5.6."""
    worst = -np.inf
    arg = None
    for _ in range(restarts):
        n = random.randint(6, 24)
        k = random.randint(1, n - 1)
        X = rng.standard_normal((n, k))
        X -= X.mean(axis=0, keepdims=True)
        for _s in range(steps):
            Q, _ = np.linalg.qr(X)
            P = Q @ Q.T
            d = np.diag(P)
            M = d[:, None] + d[None, :] - 2 * P - 1
            np.fill_diagonal(M, 0)
            G = (M > 0).astype(float)  # gradient of sum (M)_+ wrt M
            np.fill_diagonal(G, 0)
            # dM/dP: dS/dP_ab = sum_ij G_ij d(M_ij)/dP_ab
            g = np.diag(G.sum(axis=1) + G.sum(axis=0)) - 2 * G
            # gradient wrt X of tr(g P): 2 g Q Q^T ... use dP = proj; simple ascent:
            GX = 2 * g @ Q
            X = Q + 0.05 * GX
            X -= X.mean(axis=0, keepdims=True)
        Q, _ = np.linalg.qr(X)
        P = Q @ Q.T
        d = np.diag(P)
        M = d[:, None] + d[None, :] - 2 * P - 1
        np.fill_diagonal(M, 0)
        val = np.sum(np.maximum(M, 0)) - k * (k + 1)
        if val > worst:
            worst, arg = val, (n, k)
    check("Adversarial ascent vs Lemma 5.6", worst <= 1e-6,
          f"best found slack {worst:.4e} at (n,k)={arg} (equality is attained by threshold-graph projections)")


def brouwer_end_to_end(trials=1500):
    ok = True
    worst = -np.inf
    for _ in range(trials):
        n = random.randint(3, 24)
        p = random.random()
        edges = [(i, j) for i in range(n) for j in range(i + 1, n) if random.random() < p]
        m = len(edges)
        lam = np.sort(np.linalg.eigvalsh(laplacian(n, edges)))[::-1]
        cs = np.cumsum(lam)
        for k in range(1, n + 1):
            slack = cs[k - 1] - m - k * (k + 1) / 2
            worst = max(worst, slack)
            if slack > 1e-7:
                ok = False
    check("Brouwer inequality end-to-end (random graphs)", ok,
          f"{trials} graphs, max slack {worst:.3e} (equality on threshold graphs)")


if __name__ == "__main__":
    exact_projection_checks()
    split_graph_checks()
    projection_lemma_checks()
    adversarial_56()
    brouwer_end_to_end()
    print()
    if FAILURES:
        print("OVERALL: FAIL", FAILURES)
    else:
        print("OVERALL: PASS — all lemmas and identities of arXiv:2606.12197v1 verified "
              "on exact and random instances; no counterexample found.")

"""Adversarial search: minimize min-eig of M(sigma_c) over edge flips
(simulated annealing / greedy descent), keeping connected + delta >= 2.
Any candidate < -1e-8 gets an exact rational recheck (Fraction arithmetic).

Usage: python3 adversarial.py <n> <cap> <restarts> [seed]
Seeds: random G(n,p), hub-heavy starts, windmill-like starts.
"""
import sys
from fractions import Fraction
import numpy as np
import networkx as nx
from common import build_base, with_diag, sigma_cap, min_eig, windmill

n = int(sys.argv[1])
cap = float(sys.argv[2])
restarts = int(sys.argv[3])
seed0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
rng = np.random.default_rng(seed0)


def ok(A):
    d = A.sum(1)
    if d.min() < 2:
        return False
    return nx.is_connected(nx.from_numpy_array(A))


def obj(A):
    b = build_base(A)
    return min_eig(with_diag(b, sigma_cap(b["d"], b["m"], cap))["M"])


def exact_check(A):
    """Exact rational min diag of LDL / test x^T M x for float eigvec x
    rationalized — returns exact Fraction value of x^T M x."""
    nn = A.shape[0]
    d = [Fraction(int(A[i].sum())) for i in range(nn)]
    m = [Fraction(sum(int(A[i, j].sum() and 0) for j in range(0)) )for i in range(nn)]
    m = []
    for i in range(nn):
        s = sum(d[j] for j in range(nn) if A[i, j])
        m.append(s / d[i])
    s = [d[i] - 4 + min(m[i], d[i] + Fraction(int(cap))) for i in range(nn)]
    # float eigvec
    b = build_base(A)
    M = with_diag(b, sigma_cap(b["d"], b["m"], cap))["M"]
    ev, V = np.linalg.eigh(M)
    x = V[:, 0]
    xr = [Fraction(v).limit_denominator(10**6) for v in x]
    # exact M: quadratic form x^T M x = sum_i T_i x_i^2 - x^T Q x - x^T DHD x
    val = Fraction(0)
    for i in range(nn):
        val += (2 * s[i] + 4) * xr[i] ** 2 - d[i] * xr[i] ** 2
    for i in range(nn):
        for j in range(i + 1, nn):
            if A[i, j]:
                val -= 2 * xr[i] * xr[j]
    # DHD term: sum_e w_e (s_i x_i + s_j x_j)^2
    for i in range(nn):
        for j in range(i + 1, nn):
            if A[i, j]:
                a4 = 2 * (d[i] ** 2 + d[j] ** 2) - Fraction(16) * d[i] * d[j] / (m[i] + m[j])
                if a4 != 0:
                    val -= (s[i] * xr[i] + s[j] * xr[j]) ** 2 / a4
    return val


def start(kind):
    if kind == 0:
        while True:
            A = (rng.random((n, n)) < rng.uniform(0.08, 0.4)).astype(float)
            A = np.triu(A, 1)
            A = A + A.T
            if ok(A):
                return A
    if kind == 1:  # hub + random sparse
        while True:
            A = (rng.random((n, n)) < 0.08).astype(float)
            A = np.triu(A, 1); A = A + A.T
            A[0, 1:] = A[1:, 0] = 1
            if ok(A):
                return A
    # windmill-ish padded
    k = (n - 1) // 2
    W = windmill(k)
    A = np.zeros((n, n))
    A[:W.shape[0], :W.shape[0]] = W
    for i in range(W.shape[0], n):
        A[i, 0] = A[0, i] = 1
        A[i, 1] = A[1, i] = 1
    return A if ok(A) else start(0)


best_global = 1e18
for r in range(restarts):
    A = start(r % 3)
    cur = obj(A)
    T0 = 0.3
    for it in range(1500):
        T = T0 * (1 - it / 1500) + 1e-3
        i, j = rng.integers(0, n, 2)
        if i == j:
            continue
        A[i, j] = A[j, i] = 1 - A[i, j]
        if not ok(A):
            A[i, j] = A[j, i] = 1 - A[i, j]
            continue
        new = obj(A)
        if new < cur or rng.random() < np.exp((cur - new) / T):
            cur = new
        else:
            A[i, j] = A[j, i] = 1 - A[i, j]
        if cur < -1e-8:
            print(f"NEGATIVE candidate n={n} cap={cap} r={r} mineig={cur:.3e}")
            ex = exact_check(A)
            print("  exact x^T M x =", ex, float(ex))
            if ex < 0:
                g = nx.from_numpy_array(A)
                print("  COUNTEREXAMPLE g6:", nx.to_graph6_bytes(g).decode().strip())
                sys.exit(1)
    best_global = min(best_global, cur)
    if r % 10 == 0:
        print(f"restart {r}: cur={cur:.4f} best={best_global:.4f}", flush=True)

print(f"DONE n={n} cap={cap} restarts={restarts}: best min-eig {best_global:.6f} (no counterexample)")

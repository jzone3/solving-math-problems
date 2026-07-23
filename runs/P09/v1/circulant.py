"""Exhaustive Bollobas-Nikiforov check over circulant graphs C_n(S).

For each n in [nmin, nmax], enumerate all connection sets S subseteq {1..floor(n/2)}
(2^(n//2) graphs, one per subset; includes disconnected ones). Eigenvalues are closed-form:
lambda_j = sum_{s in S, s<n/2} 2 cos(2 pi j s / n) + [n/2 in S] cos(pi j)  (j = 0..n-1).
Violation iff omega * r < 2m with r = 2m - l1^2 - l2^2; prune with omega >= 2, resolve
survivors with greedy clique lower bound then exact max_clique.

Usage: python3 circulant.py nmin nmax
"""
import sys

import numpy as np

from bn_core import max_clique, evaluate
from exhaust import greedy_clique

TOL = 1e-7


def run_n(n):
    h = n // 2
    js = np.arange(n)
    C = np.zeros((h, n))
    for s in range(1, h + 1):
        if 2 * s == n:
            C[s - 1] = np.cos(np.pi * js)
        else:
            C[s - 1] = 2.0 * np.cos(2.0 * np.pi * js * s / n)
    weights = np.array([1 if 2 * (s + 1) == n else 2 for s in range(h)], dtype=np.float64)
    total = 0
    checked = 0
    best = (-1e18, None)
    nsub = 1 << h
    batch = 1 << 14
    for start in range(0, nsub, batch):
        idx = np.arange(start, min(start + batch, nsub), dtype=np.uint64)
        B = ((idx[:, None] >> np.arange(h, dtype=np.uint64)[None, :]) & 1).astype(np.float64)
        spec = B @ C                      # (k, n) eigenvalues
        deg = (B * weights).sum(axis=1)   # degree of each vertex
        m2 = n * deg                      # 2m
        spec.sort(axis=1)
        l1 = spec[:, -1]
        l2 = spec[:, -2]
        r = m2 - l1 * l1 - l2 * l2
        surv = np.nonzero((2.0 * r < m2 + TOL) & (m2 > 0))[0]
        total += len(idx)
        for si in surv:
            mask = int(idx[si])
            S = [s + 1 for s in range(h) if (mask >> s) & 1]
            adj = [0] * n
            for i in range(n):
                for s in S:
                    adj[i] |= 1 << ((i + s) % n)
                    adj[i] |= 1 << ((i - s) % n)
            g = greedy_clique(n, adj)
            if g * r[si] >= m2[si] - TOL:
                if g < n:
                    continue
            om = max_clique(n, adj)
            if om >= n:
                continue
            if om * r[si] >= m2[si] - TOL:
                continue
            checked += 1
            score, ratio, *_ = evaluate(n, adj)
            if score > best[0]:
                best = (score, S)
            if score > 1e-6:
                print(f"VIOLATION circulant n={n} S={S} score={score}", flush=True)
    print(f"circulant n={n}: subsets={total} violations_checked={checked} "
          f"best={best[0]:.3e} S={best[1]}", flush=True)


if __name__ == "__main__":
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    for n in range(nmin, nmax + 1):
        run_n(n)

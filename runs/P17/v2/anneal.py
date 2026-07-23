"""Simulated annealing / hill climb maximizing s20 = n+ - sumpos and s21 = n- - sumpos.
Float scoring only; any score > -1e-6 must go through verify.py (exact).
Usage: python3 anneal.py {20|21} n seed iters
"""
import numpy as np, sys, random

which, n, seed, iters = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rng = random.Random(seed)
np.random.seed(seed)

def score(A):
    w = np.linalg.eigvalsh(A)
    sp = float(w[w > 1e-9].sum())
    if which == 20:
        return int((w > 1e-9).sum()) - sp
    return int((w < -1e-9).sum()) - sp

A = (np.random.rand(n, n) < 0.5).astype(float)
A = np.triu(A, 1); A = A + A.T
s = score(A)
best, bestA = s, A.copy()
T0, T1 = 0.5, 0.005
for it in range(iters):
    T = T0 * (T1 / T0) ** (it / iters)
    i = rng.randrange(n); j = rng.randrange(n)
    if i == j: continue
    A[i, j] = A[j, i] = 1 - A[i, j]
    s2 = score(A)
    if s2 >= s or rng.random() < np.exp((s2 - s) / T):
        s = s2
        if s > best:
            best, bestA = s, A.copy()
    else:
        A[i, j] = A[j, i] = 1 - A[i, j]
print(f"which={which} n={n} seed={seed} best={best:+.6f}")
if best > -0.05:
    idx = np.triu_indices(n, 1)
    edges = [(int(a), int(b)) for a, b in zip(*idx) if bestA[a, b]]
    print("edges:", edges)

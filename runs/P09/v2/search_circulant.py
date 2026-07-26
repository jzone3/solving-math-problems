"""Wave 4: circulant graph sweep C_n(S), n up to NMAX.

Eigenvalues closed-form: lambda_j = sum_{s in S} 2 cos(2 pi j s / n)
(for s = n/2, contribution cos(pi j) once). omega exact via igraph C solver.
Exhaustive over all connection sets for small n; random + hill-climb on S for
larger n. Prints any score > -1e-6.
"""
import sys
import time
import itertools
import random
import numpy as np
import igraph as ig

TIME_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 3600


def spec_top2_and_m(n, S):
    j = np.arange(n)
    lam = np.zeros(n)
    m = 0
    for s in S:
        if 2 * s == n:
            lam += np.cos(np.pi * j)
            m += n // 2
        else:
            lam += 2 * np.cos(2 * np.pi * j * s / n)
            m += n
    lam.sort()
    return lam[-1], lam[-2], m


def omega(n, S):
    edges = []
    for s in S:
        for i in range(n):
            edges.append((i, (i + s) % n))
    g = ig.Graph(n=n, edges=edges)
    g.simplify()
    return g.clique_number()


def score(n, S):
    full = set(range(1, n // 2 + 1))
    if set(S) == full or not S:
        return None  # complete or empty
    l1, l2, m = spec_top2_and_m(n, S)
    w = omega(n, S)
    return l1 * l1 + l2 * l2 - 2.0 * m * (1 - 1.0 / w), l1, l2, m, w


best = (-1e18, None, None)
count = 0
t0 = time.time()


def consider(n, S):
    global best, count
    r = score(n, S)
    if r is None:
        return
    count += 1
    s = r[0]
    if s > best[0]:
        best = (s, n, tuple(sorted(S)))
    if s > -1e-6:
        tag = "VIOLATION" if s > 1e-6 else "BOUNDARY"
        print(f"{tag} n={n} S={sorted(S)} score={s:.6g} w={r[4]} m={r[3]}", flush=True)


# exhaustive for n <= 22
for n in range(4, 23):
    half = list(range(1, n // 2 + 1))
    for r in range(1, len(half)):
        for S in itertools.combinations(half, r):
            consider(n, S)
print(f"exhaustive n<=22 done: {count} circulants, best={best}", flush=True)

# random + hill-climb for 23 <= n <= 80
rng = random.Random(7)
while time.time() - t0 < TIME_BUDGET:
    n = rng.randint(23, 80)
    half = list(range(1, n // 2 + 1))
    S = set(rng.sample(half, rng.randint(2, max(2, len(half) - 2))))
    cur = score(n, S)
    if cur is None:
        continue
    for _ in range(150):
        s0 = rng.choice(half)
        T = set(S)
        if s0 in T:
            if len(T) <= 2:
                continue
            T.remove(s0)
        else:
            T.add(s0)
        r = score(n, T)
        if r is not None and r[0] > cur[0]:
            S, cur = T, r
    consider(n, S)

print(f"TOTAL {count} circulants scored, best score={best[0]:.6g} at n={best[1]} S={best[2]}", flush=True)

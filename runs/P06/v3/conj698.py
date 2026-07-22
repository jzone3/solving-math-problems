"""Conjecture 698 under its plausible intended reading (the refutationGBR code
computes sqrt(sum of squares of NEGATIVE eigenvalues of the LAPLACIAN) -- which
is identically 0 since L is PSD, making 698-as-coded vacuous).

Intended reading tested here:  sqrt(Σ_{λ_i<0} λ_i²) over ADJACENCY eigenvalues
<= R(G).  Stars give exact equality (negative eigenvalue -sqrt(k), norm sqrt(k)
= R), and equality survives adding isolated vertices.

(a) exhaust geng n<=9;  (b) anneal edge flips n in 10..36 from star seeds.
"""
import math, random, sys
import numpy as np

def score(adjmat, n):
    d = adjmat.sum(1)
    if d.sum() == 0: return None
    ev = np.linalg.eigvalsh(adjmat)
    neg = math.sqrt(float((ev[ev < 0] ** 2).sum()))
    iu, ju = np.nonzero(np.triu(adjmat, 1))
    R = float((1.0 / np.sqrt(d[iu] * d[ju])).sum())
    return neg - R

def parse_g6(line):
    data = [c - 63 for c in line.encode()]
    n = data[0]
    bits = []
    for b in data[1:]:
        for i in range(5, -1, -1):
            bits.append((b >> i) & 1)
    A = np.zeros((n, n))
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: A[i, j] = A[j, i] = 1
            k += 1
    return n, A

if sys.argv[1] == "geng":
    best = (-1e18, None)
    cnt = 0
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        n, A = parse_g6(line)
        s = score(A, n)
        if s is None: continue
        cnt += 1
        if s > best[0]: best = (s, line)
        if s > 1e-9: print("VIOLATION", s, line)
    print(f"scanned {cnt}: max negnorm-R = {best[0]:.12f} at {best[1]}")
else:
    rnd = random.Random(3)
    overall = (-1e18, None)
    for n in [10, 14, 18, 24, 30, 36]:
        for restart in range(6):
            A = np.zeros((n, n))
            hub = 0
            for v in range(1, n): A[0, v] = A[v, 0] = 1  # star seed
            cur = score(A, n)
            best = cur
            iters = 20000
            for it in range(iters):
                T = 0.05 * (1 - it / iters)
                i, j = rnd.sample(range(n), 2)
                A[i, j] = A[j, i] = 1 - A[i, j]
                s = score(A, n)
                if s is not None and (s >= cur or rnd.random() < math.exp((s - cur) / max(T, 1e-9))):
                    cur = s
                    best = max(best, cur)
                else:
                    A[i, j] = A[j, i] = 1 - A[i, j]
            print(f"n={n} restart={restart}: best negnorm-R = {best:.9f}", flush=True)
            if best > overall[0]: overall = (best, n)
    print("OVERALL:", overall)

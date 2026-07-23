#!/usr/bin/env python3
"""Numerical check of Kumar-Pragada arXiv:2607.19817 (Energy and independence number)
over all connected graphs n <= 9 (requires nauty-geng, numpy):
  (1) Lemma 2.2 (neighbourhood deletion): 4m + sum_v E(G-N[v]) <= n*E(G)
  (2) Theorem 1.2: E(G) >= 2*(n - alpha(G))
  (3) Cvetkovic inertia bound: max(n+, n-) <= n - alpha(G)
(2)+(3) imply WoW 20 & 21. Output archived in logs/kumar-pragada-check.txt.
"""
import numpy as np, subprocess


def energy(A):
    if A.shape[0] == 0:
        return 0.0
    return float(np.abs(np.linalg.eigvalsh(A)).sum())


def alpha(A, n):
    adj = [0] * n
    for i in range(n):
        for j in range(n):
            if A[i, j]:
                adj[i] |= 1 << j
    best = 0

    def bb(cand, cur):
        nonlocal best
        if cur + bin(cand).count('1') <= best:
            return
        if cand == 0:
            best = max(best, cur)
            return
        v = (cand & -cand).bit_length() - 1
        bb(cand & ~(1 << v) & ~adj[v], cur + 1)
        bb(cand & ~(1 << v), cur)

    bb((1 << n) - 1, 0)
    return best


def parse(line):
    d = [ord(c) - 63 for c in line]
    n = d[0]
    bits = []
    for x in d[1:]:
        bits += [(x >> k) & 1 for k in range(5, -1, -1)]
    A = np.zeros((n, n))
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i, j] = A[j, i] = 1
            idx += 1
    return A


def main():
    worst22 = worst12 = worstcor = 1e9
    tot = 0
    for n in range(2, 10):
        p = subprocess.run(['nauty-geng', '-q', '-c', str(n)], capture_output=True, text=True)
        for line in p.stdout.split():
            A = parse(line)
            tot += 1
            E = energy(A)
            m = int(A.sum() // 2)
            s = 0.0
            for v in range(n):
                keep = [u for u in range(n) if u != v and A[v, u] == 0]
                s += energy(A[np.ix_(keep, keep)])
            worst22 = min(worst22, n * E - (4 * m + s))
            a = alpha(A, n)
            worst12 = min(worst12, E - 2 * (n - a))
            w = np.linalg.eigvalsh(A)
            npos = int((w > 1e-9).sum())
            nneg = int((w < -1e-9).sum())
            worstcor = min(worstcor, (n - a) - max(npos, nneg))
        print(f"n={n}: lemma2.2 min slack={worst22:.6f}  thm1.2 min slack={worst12:.6f}"
              f"  inertia-bound min slack={worstcor}")
    print("graphs checked:", tot)


if __name__ == '__main__':
    main()

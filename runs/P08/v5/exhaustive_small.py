#!/usr/bin/env python3
"""Exhaustive check of Graffiti 39/40 and the proof chain on all connected
graphs with n <= NMAX vertices (nauty-geng). Prints the maximum of
dev - min(n_pos, n_neg) seen and PASS/FAIL."""
import subprocess
import sys
import numpy as np

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
EPS = 1e-4


def g6_to_adj(line):
    data = [c - 63 for c in line]
    n = data[0]
    bits = []
    for b in data[1:]:
        bits.extend((b >> i) & 1 for i in range(5, -1, -1))
    A = np.zeros((n, n))
    k = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[k]
            k += 1
    return A


def dist_matrix(A):
    n = len(A)
    INF = 10 ** 6
    D = np.where(A > 0, 1, INF).astype(float)
    np.fill_diagonal(D, 0)
    for k in range(n):
        D = np.minimum(D, D[:, k][:, None] + D[k, :][None, :])
    return D


def main():
    worst = -1e9
    worst_g = None
    total = 0
    for n in range(2, NMAX + 1):
        p = subprocess.Popen(["nauty-geng", "-cq", str(n)], stdout=subprocess.PIPE)
        for raw in p.stdout:
            line = raw.strip()
            A = g6_to_adj(line)
            D = dist_matrix(A)
            diam = D.max()
            dev_full = D.ravel().std()
            dev_off = D[~np.eye(len(A), dtype=bool)].std()
            ev = np.linalg.eigvalsh(A)
            npos = int((ev > EPS).sum())
            nneg = int((ev < -EPS).sum())
            # proof chain
            assert dev_full <= diam / 2 + 1e-9
            assert dev_off <= diam / 2 + 1e-9
            assert min(npos, nneg) >= (diam + 1) // 2
            s = max(dev_full, dev_off) - min(npos, nneg)
            if s > worst:
                worst, worst_g = s, line.decode()
            if s > 1e-6:
                print("REFUTED:", line.decode())
                sys.exit(123)
            total += 1
        print(f"n={n} done, cumulative {total} graphs, max score {worst:.6f} ({worst_g})", flush=True)
    print(f"PASS exhaustive n<={NMAX}: {total} connected graphs, max dev-min(n+,n-) = {worst:.6f}")


if __name__ == "__main__":
    main()

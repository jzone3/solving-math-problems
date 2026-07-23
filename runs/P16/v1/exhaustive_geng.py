#!/usr/bin/env python3
"""P16 v1: exhaustive float screening of ALL connected graphs on n vertices
(nauty-geng -c) against BHS bounds 44 and 46. Reports max margin per n.
Float screening only; any positive hit goes to the exact verifier."""
import math
import subprocess
import sys

import numpy as np


def g6_to_adj(line):
    data = [c - 63 for c in line.encode()]
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        bits.extend((x >> s) & 1 for s in range(5, -1, -1))
    A = np.zeros((n, n), dtype=np.int64)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]
            idx += 1
    return A


def margins(A):
    n = A.shape[0]
    d = A.sum(axis=1)
    m = (A @ d) / d
    L = np.diag(d) - A
    mu = np.max(np.linalg.eigvalsh(L.astype(float)))
    r44 = -np.inf
    r46 = -np.inf
    ok44 = ok46 = True
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                di, dj, mi, mj = float(d[i]), float(d[j]), m[i], m[j]
                in44 = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
                in46 = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
                if in44 < 0:
                    ok44 = False
                else:
                    r44 = max(r44, 2 + math.sqrt(in44))
                if in46 < 0:
                    ok46 = False
                else:
                    r46 = max(r46, 2 + math.sqrt(in46))
    m44 = mu - r44 if ok44 else None
    m46 = mu - r46 if ok46 else None
    return m44, m46


def main(n):
    proc = subprocess.Popen(["nauty-geng", "-c", "-q", str(n)],
                            stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    best44 = (-np.inf, None)
    best46 = (-np.inf, None)
    neg44 = neg46 = 0
    cnt = 0
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        cnt += 1
        A = g6_to_adj(line)
        m44, m46 = margins(A)
        if m44 is None:
            neg44 += 1
        elif m44 > best44[0]:
            best44 = (m44, line)
        if m46 is None:
            neg46 += 1
        elif m46 > best46[0]:
            best46 = (m46, line)
        if m44 is not None and m44 > 1e-9:
            print(f"VIOLATION44 n={n} g6={line} margin={m44}", flush=True)
        if m46 is not None and m46 > 1e-9:
            print(f"VIOLATION46 n={n} g6={line} margin={m46}", flush=True)
    print(f"n={n} graphs={cnt} best44={best44[0]:.6f} ({best44[1]}) "
          f"best46={best46[0]:.6f} ({best46[1]}) inner<0: b44 on {neg44}, b46 on {neg46}",
          flush=True)


if __name__ == "__main__":
    for n in range(2, int(sys.argv[1]) + 1):
        main(n)

"""P16 childC — fast float screener for graph6 input on stdin (n <= 62).

Screens BOTH bounds 44 and 46. Prints any graph with gap < THRESH (candidate)
and reports the minimum gap seen. Cheap skip: mu(G) <= max_{ij in E}(d_i+d_j)
(Anderson-Morley), so if RHS >= that for both bounds, no eigensolve needed.

Usage:  nauty-geng -c ... n | python3 geng_screen.py [label]
"""
import sys

import numpy as np

THRESH = 1e-6


def g6_to_adj(line):
    data = [c - 63 for c in line]
    n = data[0]
    bits = []
    for c in data[1:]:
        for k in range(5, -1, -1):
            bits.append((c >> k) & 1)
    A = np.zeros((n, n), dtype=np.float64)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i, j] = A[j, i] = 1.0
            idx += 1
    return A


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else ""
    min44 = min46 = np.inf
    arg44_min = arg46_min = None
    cnt = 0
    eig = 0
    for raw in sys.stdin.buffer:
        line = raw.strip()
        if not line:
            continue
        cnt += 1
        A = g6_to_adj(line)
        d = A.sum(axis=1)
        m = (A @ d) / d
        iu, ju = np.nonzero(np.triu(A))
        di, dj = d[iu], d[ju]
        mi, mj = m[iu], m[ju]
        a44 = 2.0 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
        a46 = 2.0 * (di ** 2 + dj ** 2) - 16.0 * di * dj / (mi + mj) + 4.0
        r44 = np.max(np.where(a44 >= 0, 2.0 + np.sqrt(np.maximum(a44, 0)), -np.inf))
        r46 = np.max(np.where(a46 >= 0, 2.0 + np.sqrt(np.maximum(a46, 0)), -np.inf))
        am = np.max(di + dj)  # Anderson-Morley upper bound on mu
        if r44 >= am and r46 >= am:
            continue
        eig += 1
        L = np.diag(d) - A
        mu = np.linalg.eigvalsh(L)[-1]
        g44 = r44 - mu
        g46 = r46 - mu
        if g44 < min44:
            min44, arg44_min = g44, line.decode()
        if g46 < min46:
            min46, arg46_min = g46, line.decode()
        if g44 < THRESH or g46 < THRESH:
            print(f"CANDIDATE {line.decode()} gap44={g44:.3e} gap46={g46:.3e}",
                  flush=True)
    print(f"[{label}] done: {cnt} graphs, {eig} eigensolves, "
          f"min gap44={min44:.6g} ({arg44_min}), min gap46={min46:.6g} ({arg46_min})",
          flush=True)


if __name__ == "__main__":
    main()

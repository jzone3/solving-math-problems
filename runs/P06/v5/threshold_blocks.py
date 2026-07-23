"""Large-scale scan of conjecture 129 (dev_L <= R) over BLOCK THRESHOLD graphs.

A threshold graph is given by a creation sequence; we parameterize it by
blocks: sizes (a_1, b_1, a_2, b_2, ..., a_k, b_k) meaning a_1 isolated-joins,
then b_1 dominating-joins, etc. (trailing isolated block allowed via a_{k+1}
conceptually -- covered by including a final independent block with b=0 not
needed since padding never helped past n*).

Structure: label independent blocks I_1..I_k (sizes a_i) and dominating
blocks D_1..D_k (sizes b_i). Vertex in D_j is adjacent to: all previous
vertices (I_1..I_j, D_1..D_j minus itself) and all later dominating vertices.
So with B_j = b_j + b_{j+1} + ... + b_k (suffix sums), degrees:
  deg(I_i) = B_i
  deg(D_j) = (a_1+..+a_j) + (b_1+..+b_k) - 1
Edges between I_i and D_j exist iff j >= i (count a_i*b_j); D-D complete.

dev_L^2 = (sum d(d+1))/n - (2m/n)^2;  R = sum_edges 1/sqrt(du dv).

Scans all 2k-block tuples with sizes from a log grid, n up to ~1e5.
Usage: python3 threshold_blocks.py <k> <gridmax>
"""

import sys
import itertools
import numpy as np


def score(As, Bs):
    k = len(As)
    a = np.array(As, dtype=float)
    b = np.array(Bs, dtype=float)
    sb = float(b.sum())
    ca = np.cumsum(a)                     # a_1+..+a_j
    Bsuf = np.cumsum(b[::-1])[::-1]       # b_j+..+b_k
    dI = Bsuf.copy()                      # degree of I_i vertices
    dD = ca + sb - 1                      # degree of D_j vertices
    n = float(a.sum() + sb)
    m = float(np.sum(a * dI)) / 1.0       # I-D edges counted from I side
    mdd = sb * (sb - 1) / 2
    m_total = m + mdd
    M1p = float(np.sum(a * dI * (dI + 1)) + np.sum(b * dD * (dD + 1)))
    dev2 = M1p / n - (2 * m_total / n) ** 2
    if dev2 <= 0:
        return -1e18
    # R: I_i -- D_j edges for j >= i: a_i*b_j / sqrt(dI_i * dD_j)
    R = 0.0
    for i in range(k):
        R += a[i] * float(np.sum(b[i:] / np.sqrt(dI[i] * dD[i:])))
    # D-D edges: between D_i and D_j (i<j): b_i*b_j; within D_j: C(b_j,2)
    for i in range(k):
        R += b[i] * (b[i] - 1) / 2 / dD[i]
        R += b[i] * float(np.sum(b[i + 1:] / np.sqrt(dD[i] * dD[i + 1:])))
    return float(np.sqrt(dev2)) - R


def main():
    k, gridmax = int(sys.argv[1]), int(sys.argv[2])
    grid = sorted(set(
        list(range(1, 12)) + [15, 20, 30, 50, 80, 120, 200, 400, 800,
                              1500, 3000, 6000, 12000]))
    grid = [g for g in grid if g <= gridmax]
    best = []
    tried = 0
    for As in itertools.product(grid, repeat=k):
        for Bs in itertools.product(grid, repeat=k):
            s = score(As, Bs)
            tried += 1
            best.append((s, As, Bs))
            if len(best) > 50000:
                best.sort(reverse=True)
                del best[8:]
    best.sort(reverse=True)
    print(f"k={k} gridmax={gridmax} tuples={tried}; top 129 scores "
          f"(violation if >0):")
    for s, As, Bs in best[:8]:
        n = sum(As) + sum(Bs)
        print(f"  {s:+.8f}  a={As} b={Bs} n={n}")


if __name__ == "__main__":
    main()

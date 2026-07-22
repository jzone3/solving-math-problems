"""Exhaustive scan of ALL threshold graphs on n vertices (creation sequences)
for the eigenvalue-free reduction M*: S * dev_L <= m^2.

Rationale: sqrt(xy) is supermodular, so among realizations of a fixed degree
sequence S is maximized at switch-stable (shifted/threshold-like) graphs, and
dev_L depends on degrees only; hence threshold graphs are the natural extremal
candidates for M* (and 129). Creation sequence b_2..b_n in {0,1}: vertex j
joins isolated (0) or dominating (1). Isolated-vertex padding is included
(leading zeros).

Usage: python3 threshold_scan.py <n>
"""

import sys
import numpy as np


def main():
    n = int(sys.argv[1])
    nbits = n - 1
    total = 1 << nbits
    batch = 1 << 12
    worst = []
    tri = np.tril(np.ones((n, n)), -1)  # tri[j,i]=1 for i<j
    for start in range(0, total, batch):
        cnt = min(batch, total - start)
        idx = np.arange(start, start + cnt, dtype=np.int64)
        B = ((idx[:, None] >> np.arange(nbits)[None, :]) & 1).astype(np.float64)
        b = np.concatenate([np.zeros((cnt, 1)), B], axis=1)  # vertex 0 joins isolated
        # degrees: d_i = b_i * i + sum_{j>i} b_j
        suff = np.cumsum(b[:, ::-1], axis=1)[:, ::-1] - b
        d = b * np.arange(n)[None, :] + suff
        m = d.sum(axis=1) / 2
        ok = m > 0
        sq = np.sqrt(d)
        # S = sum over j with b_j=1, i<j of sqrt(d_i d_j)
        S = np.einsum('bj,ji,bi->b', b * sq, tri, sq)
        M1 = np.sum(d * d, axis=1)
        dev2 = (M1 + 2 * m) / n - 4 * m * m / (n * n)
        score = np.where(ok, S * np.sqrt(np.maximum(dev2, 0)) - m * m, -1e18)
        top = np.argsort(score)[-3:]
        for t in top:
            worst.append((float(score[t]), start + int(t)))
        worst.sort(reverse=True)
        del worst[6:]
    print(f"n={n} top M* over all {total} threshold creation sequences "
          f"(violation if >0):")
    for s, code in worst[:6]:
        bits = [(code >> k) & 1 for k in range(nbits)]
        print(f"  {s:+.10f}  creation=0{''.join(map(str, bits))}")


if __name__ == "__main__":
    main()

"""Anneal the eigenvalue-free reduction M* for 129:
    M*:  S * dev_L <= m^2,   S = sum_E sqrt(du dv).
(129 follows via Cauchy-Schwarz R*S >= m^2.)
Usage: python3 mstar_anneal.py <n> <restarts> <iters> [seed]
"""

import sys
import numpy as np
from local_search import anneal, adj_to_g6


def mstar(A):
    n = len(A)
    d = A.sum(axis=1).astype(float)
    m = d.sum() / 2
    if m == 0:
        return -1e9
    dev = np.sqrt(np.sum(d * (d + 1)) / n - (2 * m / n) ** 2)
    i, j = np.nonzero(np.triu(A, 1))
    S = float(np.sum(np.sqrt(d[i] * d[j])))
    return (S * dev - m * m) / max(m, 1.0)


if __name__ == "__main__":
    n, restarts, iters = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    best, bestA = -1e9, None
    for r in range(restarts):
        b, A = anneal(mstar, n, iters, r % 5)
        if b > best:
            best, bestA = b, A
    print(f"M* n={n} best(normalized)={best:+.8f} g6={adj_to_g6(bestA)}"
          + ("  VIOLATION-CANDIDATE" if best > 1e-9 else ""))

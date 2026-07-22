"""Conj 154: std-dev of adjacency eigenvalues (= sqrt(2m/n)) <= n/mu.
Equivalently 2*m*mu^2 <= n^3. Scan dumbbells for min-n violation, both mu defs."""
from fractions import Fraction
from score143 import bfs_all_dist_sum
import numpy as np
from score143 import dumbbell, lollipop


def ratio154(A):
    n = A.shape[0]
    adj = [np.nonzero(A[i])[0].tolist() for i in range(n)]
    m = int(A.sum()) // 2
    dsum, conn = bfs_all_dist_sum(adj, n)
    if not conn:
        return None
    mu_rc = Fraction(dsum, n * n)
    mu_pair = Fraction(dsum, n * (n - 1))
    return (Fraction(2 * m) * mu_rc ** 2 / n ** 3,
            Fraction(2 * m) * mu_pair ** 2 / n ** 3, m, dsum)


for n in range(20, 301, 5 if True else 1):
    best = None
    for a in range(3, n - 4):
        for b in range(a, n - a - 2):
            ell = n - a - b
            if ell < 1:
                continue
            r = ratio154(dumbbell(a, ell, b))
            if r and (best is None or r[0] > best[0][0]):
                best = (r, a, ell, b)
    r, a, ell, b = best
    flag = " *** VIOLATION(rc) ***" if r[0] > 1 else (" *** VIOLATION(pair) ***" if r[1] > 1 else "")
    print(f"n={n}: D({a},{ell},{b}) 2m*mu_rc^2/n^3={float(r[0]):.5f} "
          f"pair={float(r[1]):.5f} m={r[2]}{flag}", flush=True)

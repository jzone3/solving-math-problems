"""Fine scan for minimal-n conjecture-154 violations (2*m*mu^2 > n^3), exact integers.
Family: dumbbells D(a,ell,b) with a>=1,b>=1 (a=1 or b=1 degenerate to lollipop/path)."""
from fractions import Fraction
import numpy as np
from score143 import dumbbell, lollipop, bfs_all_dist_sum


def check(A):
    n = A.shape[0]
    adj = [np.nonzero(A[i])[0].tolist() for i in range(n)]
    m = int(A.sum()) // 2
    dsum, conn = bfs_all_dist_sum(adj, n)
    if not conn:
        return None
    # exact: violation iff 2*m*dsum^2 > n^3 * D^2
    return (Fraction(2 * m * dsum * dsum, n ** 3 * (n * n) ** 2),
            Fraction(2 * m * dsum * dsum, n ** 3 * (n * (n - 1)) ** 2), m, dsum)


for n in range(100, 136):
    best = None
    for a in range(2, n - 2):
        for b in range(a, n - a):
            ell = n - a - b
            if ell < 0:
                continue
            if ell == 0:
                continue
            r = check(dumbbell(a, ell, b)) if a >= 2 and b >= 2 else None
            if r and (best is None or r[0] > best[0][0]):
                best = (r, a, ell, b)
    # lollipops too
    for a in range(3, n - 1):
        r = check(lollipop(a, n - a))
        if r and r[0] > best[0][0]:
            best = (r, a, n - a, 0)
    r, a, ell, b = best
    flag = ""
    if r[0] > 1:
        flag = " *** VIOLATION rc+pair ***" if r[1] > 1 else " *** VIOLATION rc ***"
    elif r[1] > 1:
        flag = " *** VIOLATION pair ***"
    print(f"n={n}: D({a},{ell},{b}) rc={float(r[0]):.5f} pair={float(r[1]):.5f} m={r[2]} dsum={r[3]}{flag}",
          flush=True)

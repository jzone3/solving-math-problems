"""Tightened degree-sequence relaxation for conjecture 129.

For a GRAPHICAL degree sequence d (Erdos-Gallai checked), every realization G
has an edge-type histogram x_ab (a<=b, over distinct degree values) satisfying
  (stub balance)  sum_b x_ab + 2 x_aa [b=a] = a * n_a
  (capacities)    x_ab <= n_a n_b (a<b),  x_aa <= C(n_a,2)
so  R(G) >= LP := min sum x_ab / sqrt(ab)  over that polytope.
If dev(d) <= LP for all graphical d, conjecture 129 holds.

This scans all graphical degree sequences with n <= NMAX (isolated vertices
allowed via a zero-degree count, which affects dev only), reporting violations
dev > LP + eps of the tightened relaxation.
"""
import math
import sys
from itertools import combinations_with_replacement
from collections import Counter

import numpy as np
from scipy.optimize import linprog

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def erdos_gallai(degs):
    d = sorted(degs, reverse=True)
    n = len(d)
    if sum(d) % 2:
        return False
    pref = 0
    for k in range(1, n + 1):
        pref += d[k - 1]
        tail = sum(min(x, k) for x in d[k:])
        if pref > k * (k - 1) + tail:
            return False
    return True


def lp_min_randic(degs):
    cnt = Counter(degs)
    vals = sorted(cnt)
    pairs = [(a, b) for i, a in enumerate(vals) for b in vals[i:]]
    c = np.array([1.0 / math.sqrt(a * b) for a, b in pairs])
    A_eq = np.zeros((len(vals), len(pairs)))
    b_eq = np.array([a * cnt[a] for a in vals], dtype=float)
    for j, (a, b) in enumerate(pairs):
        ia, ib = vals.index(a), vals.index(b)
        A_eq[ia, j] += 1
        A_eq[ib, j] += 1  # a==b contributes 2 correctly
    ub = np.array([cnt[a] * cnt[b] if a != b else cnt[a] * (cnt[a] - 1) / 2
                   for a, b in pairs], dtype=float)
    res = linprog(c, A_eq=A_eq, b_eq=b_eq / 1.0, bounds=list(zip([0.0] * len(pairs), ub)),
                  method="highs")
    return res.fun if res.status == 0 else None


def dev_of(degs, n):
    m = sum(degs) // 2
    S = sum(d * d for d in degs)
    var = (S + 2 * m) / n - (2 * m / n) ** 2
    return math.sqrt(max(var, 0.0))


for n in range(2, NMAX + 1):
    worst, warg = -1e18, None
    cnt = viol = 0
    for k in range(1, n + 1):  # k positive-degree vertices, n-k isolated
        for degs in combinations_with_replacement(range(1, k), k):
            if not erdos_gallai(degs):
                continue
            cnt += 1
            lp = lp_min_randic(degs)
            if lp is None:
                continue
            f = dev_of(degs, n) - lp
            if f > worst:
                worst, warg = f, degs
            if f > 1e-7:
                viol += 1
                if viol <= 5:
                    print(f"  VIOLATION n={n} degs={degs} dev-LP={f:.9f}")
    print(f"n={n:3d}: {cnt} graphical seqs, worst dev-LP = {worst:+.9f} at {warg}, "
          f"violations = {viol}", flush=True)

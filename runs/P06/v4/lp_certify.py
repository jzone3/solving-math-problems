#!/usr/bin/env python3
"""LP certification of Graffiti 129 for ALL graphs on n vertices.

dev(L) depends only on the degree sequence D (see NOTES.md). Hence 129 holds
for every graph with degree sequence D iff dev(D) <= Rmin(D), the minimum
Randic index over realizations of D. We lower-bound Rmin(D) by an LP
relaxation over degree-class edge counts:

  classes = distinct positive degrees a with multiplicity n_a
  vars    x_ab = #edges between class a and class b (a<=b)
  min     sum x_ab / sqrt(ab)
  s.t.    sum_{b != a} x_ab + 2 x_aa = a * n_a          (degree balance)
          0 <= x_ab <= n_a*n_b (a<b),  x_aa <= C(n_a,2)

Every graph realizing D yields a feasible x, so LP optimum <= Rmin(D).
If dev(D) <= LP_opt - margin for all graphical D on n vertices, conjecture
129 is certified for all graphs on n vertices (modulo LP solver numerics;
near-tight sequences are re-reported for exact scrutiny).

Enumerates all graphical degree sequences (Erdos-Gallai), including zeros.
Usage: lp_certify.py n [start_idx end_idx]
"""
import math, sys, itertools
import numpy as np
from scipy.optimize import linprog

def graphical(D):
    """D sorted descending, even sum, Erdos-Gallai."""
    if sum(D) % 2: return False
    n = len(D)
    pref = 0
    for k in range(1, n+1):
        pref += D[k-1]
        rhs = k*(k-1) + sum(min(d, k) for d in D[k:])
        if pref > rhs: return False
    return True

def dev(D):
    n = len(D); m2 = sum(D)
    var = (sum(d*d for d in D) + m2)/n - (m2/n)**2
    return math.sqrt(max(var, 0.0))

def lp_lower_bound(D):
    """LP lower bound on Randic index over realizations of positive part."""
    from collections import Counter
    cnt = Counter(d for d in D if d > 0)
    degs = sorted(cnt)
    k = len(degs)
    idx = {}
    costs, ub = [], []
    for i in range(k):
        for j in range(i, k):
            a, b = degs[i], degs[j]
            idx[(i, j)] = len(costs)
            costs.append(1.0/math.sqrt(a*b))
            ub.append(cnt[a]*(cnt[a]-1)/2 if i == j else cnt[a]*cnt[b])
    nv = len(costs)
    A = np.zeros((k, nv)); rhs = np.zeros(k)
    for i in range(k):
        rhs[i] = degs[i]*cnt[degs[i]]
        for j in range(k):
            v = idx[(min(i, j), max(i, j))]
            A[i, v] += 2.0 if i == j else 1.0
    res = linprog(costs, A_eq=A, b_eq=rhs,
                  bounds=[(0, u) for u in ub], method="highs")
    if not res.success:
        return None  # infeasible LP => no realization? (shouldn't happen for graphical D)
    return res.fun

def gen_partitions(n, maxpart):
    """nonincreasing sequences of length n with entries in [0, maxpart]."""
    def rec(rem, mx, cur):
        if rem == 0:
            yield cur; return
        for v in range(min(mx, cur[-1] if cur else mx), -1, -1):
            if v == 0:
                yield cur + [0]*rem
                return
            yield from rec(rem-1, mx, cur + [v])
    yield from rec(n, maxpart, [])

def main():
    n = int(sys.argv[1])
    worst = 1e18; worstD = None
    checked = 0; hard = []
    for D in gen_partitions(n, n-1):
        if sum(D) == 0 or sum(D) % 2: continue
        if not graphical(D): continue
        dv = dev(D)
        # cheap pre-bound: R >= sum(sqrt(d))/(2 sqrt(Delta))
        Delta = D[0]
        cheap = sum(math.sqrt(d) for d in D)/(2*math.sqrt(Delta))
        if dv <= cheap - 1e-9:
            checked += 1
            margin = cheap - dv
            if margin < worst: worst, worstD = margin, (list(D), 'cheap')
            continue
        lb = lp_lower_bound(D)
        checked += 1
        if lb is None:
            hard.append((list(D), 'LP-infeasible')); continue
        margin = lb - dv
        if margin < worst: worst, worstD = margin, (list(D), 'lp')
        if margin < 1e-6:
            hard.append((list(D), f"margin={margin:.3e} dev={dv:.9f} lp={lb:.9f}"))
            print("TIGHT/VIOL", D, f"dev={dv:.9f} lp={lb:.9f} margin={margin:.3e}",
                  flush=True)
    print(f"n={n}: {checked} graphical degree sequences checked")
    print(f"worst margin (bound - dev) = {worst:.9e} at {worstD}")
    print(f"hard/tight cases: {len(hard)}")
    for h in hard[:50]: print("  ", h)
    if all(True for _ in hard) and len(hard) == 0 and worst > 0:
        print(f"CERTIFIED: conjecture 129 holds for ALL graphs on {n} vertices")

if __name__ == "__main__":
    main()

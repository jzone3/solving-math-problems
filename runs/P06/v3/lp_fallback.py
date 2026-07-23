"""Exact-R LP fallback certificate for degree sequences flagged NEAR/VIOLATION
by enum_seq3 ((*) close to or above 0).

For a degree sequence with n_a vertices of degree a, ANY simple-graph
realization satisfies the transportation constraints on edge counts x_{ab}
(a <= b):
    sum_b x_{ab} + x_{aa}  ... precisely: for each degree a,
        2*x_{aa} + sum_{b != a} x_{ab} = a * n_a
    0 <= x_{aa} <= C(n_a,2),  0 <= x_{ab} <= n_a*n_b  (simple-graph caps)
Minimizing  sum x_{ab}/sqrt(ab)  over this LP gives a valid LOWER bound R_LP
<= R(G) for every realization G. If dev^2 <= R_LP^2, conjecture 129 is
certified for ALL graphs with that degree sequence.

usage: python3 lp_fallback.py < file_with_NEAR_lines   (reads 'seq: d1 d2 ...')
"""
import sys, math
from collections import Counter
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

def rlp_lower_bound(degs):
    cnt = Counter(d for d in degs if d > 0)
    vals = sorted(cnt)
    pairs = [(a, b) for i, a in enumerate(vals) for b in vals[i:]]
    idx = {p: k for k, p in enumerate(pairs)}
    c = [1.0 / math.sqrt(a * b) for a, b in pairs]
    A_eq = np.zeros((len(vals), len(pairs)))
    b_eq = np.zeros(len(vals))
    for r, a in enumerate(vals):
        b_eq[r] = a * cnt[a]
        for (x, y), k in idx.items():
            if x == a: A_eq[r, k] += 1
            if y == a: A_eq[r, k] += 1   # x==y==a contributes 2
    bounds = []
    for a, b in pairs:
        cap = cnt[a] * (cnt[a] - 1) / 2 if a == b else cnt[a] * cnt[b]
        bounds.append((0, cap))
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        return None
    return res.fun

def main():
    any_seq = False
    all_ok = True
    seen = set()
    for line in sys.stdin:
        if "seq:" not in line: continue
        degs = tuple(int(x) for x in line.split("seq:")[1].split())
        if degs in seen: continue
        seen.add(degs)
        any_seq = True
        n = len(degs)
        m2 = sum(degs)
        A = sum(d * (d + 1) for d in degs)
        dev2 = Fraction(A, n) - Fraction(m2 * m2, n * n)
        rlp = rlp_lower_bound(degs)
        ok = rlp is not None and float(dev2) <= rlp * rlp + 1e-12
        all_ok &= ok
        print(f"{'CERTIFIED' if ok else 'UNRESOLVED'} dev={float(dev2)**0.5:.9f} "
              f"R_LP>={rlp:.9f} n={n} seq={degs}")
    if any_seq:
        print("ALL CERTIFIED" if all_ok else "SOME UNRESOLVED — needs deeper check")
    else:
        print("no sequences on input")

if __name__ == "__main__":
    main()

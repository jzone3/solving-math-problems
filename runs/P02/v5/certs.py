#!/usr/bin/env python3
"""Compute exact integer Farkas certificates for all infeasible boundary
graphs found by search.py.  Certificate: integer vector y with
sum(y) = 0,  yT A >= 0 componentwise,  yT A != 0.
Then any x with Ax = d*1 gives 0 = d*sum(y) = (yT A) x >= min positive entry
* 1 > 0 (since x >= 1), contradiction.

Method: float LP (scipy HiGHS) to find y, then rationalize and verify
exactly with Fractions; scale to integers.
Writes counterexamples.json: [{g6, n, degrees, y}].
"""
import json, sys
from fractions import Fraction
from math import lcm
import numpy as np
from scipy.optimize import linprog
from search import g6_to_adj, is_maximal_tf

def exact_check(adj, y):
    n = len(adj)
    if sum(y) != 0:
        return False
    z = [sum(y[u] * adj[u][v] for u in range(n)) for v in range(n)]
    return all(zi >= 0 for zi in z) and any(zi > 0 for zi in z)

def find_cert(adj):
    n = len(adj)
    A = np.array(adj, float)
    # variables y (free). constraints: A^T y >= 0 ; sum y = 0 ; sum(A^T y) = 1
    res = linprog(np.zeros(n),
                  A_ub=-A.T, b_ub=np.zeros(n),
                  A_eq=np.vstack([np.ones(n), A.sum(axis=1)]),  # sum(y)=0, deg.y = sum(A^T y) = 1
                  b_eq=np.array([0.0, 1.0]),
                  bounds=[(None, None)] * n, method='highs')
    if not res.success:
        return None
    yf = res.x
    for den in (1, 2, 3, 4, 6, 8, 12, 24, 48, 120, 360, 2520):
        y = [Fraction(round(v * den), den) for v in yf]
        if exact_check(adj, y):
            L = lcm(*[f.denominator for f in y]) if y else 1
            return [int(f * L) for f in y]
    return None

def main():
    out = []
    for g6 in sys.argv[1:]:
        n, adj = g6_to_adj(g6)
        assert is_maximal_tf(n, adj)
        y = find_cert(adj)
        assert y is not None and exact_check(adj, [Fraction(v) for v in y]), g6
        deg = [sum(r) for r in adj]
        assert min(deg) * 3 >= n
        out.append({"g6": g6, "n": n, "mindeg": min(deg), "y": y})
        print("cert OK:", g6, y)
    json.dump(out, open("counterexamples.json", "w"), indent=1)

if __name__ == "__main__":
    main()

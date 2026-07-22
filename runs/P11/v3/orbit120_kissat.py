#!/usr/bin/env python3
"""Decide CW(120,49) via kissat on the multiplier-orbit CNF.

Same mathematical content as orbit120_sat.py (complete decision procedure via
AGZ Thm 2.4: multiplier 7 fixes a translate; row constant on <7>-orbits):
UNSAT => no CW(120,49) exists.
"""
import sys
import numpy as np

sys.path.insert(0, ".")
sys.path.insert(0, "../../../solutions/P11")
from icw_enum import orbits_of
from verify import check, is_proper
from cnf_cw import Builder, ternary, product_lits

n, k = 120, 49
orbs = orbits_of(7, n)
sizes = [len(o) for o in orbs]
no = len(orbs)

C = np.zeros((no, no, n), dtype=np.int64)
for i, oi in enumerate(orbs):
    for j, oj in enumerate(orbs):
        for x in oi:
            for y in oj:
                C[i, j, (y - x) % n] += 1

b = Builder()
tv = [ternary(b, i) for i in range(no)]

# products (i<=j); for i==j: v^2=1 iff pos|neg
pp = {}
pn = {}
for i in range(no):
    for j in range(i, no):
        if i == j:
            nz = b.or2(tv[i][0], tv[i][1])
            pp[(i, i)] = nz
            pn[(i, i)] = None
        else:
            pp[(i, j)], pn[(i, j)] = product_lits(b, *tv[i], *tv[j])

# weight: sum sizes[i] * (v_i^2) = 49
b.eq_sums([(sizes[i], pp[(i, i)]) for i in range(no)],
          [(k, b.var("TRUE"))])
b.add(b.var("TRUE"))

# PACF(t) = 0 for t=1..n//2
for t in range(1, n // 2 + 1):
    pos_terms, neg_terms = [], []
    for i in range(no):
        for j in range(i, no):
            c = int(C[i, j, t] + C[j, i, t]) if j > i else int(C[i, i, t])
            if not c:
                continue
            pos_terms.append((c, pp[(i, j)]))
            if pn[(i, j)] is not None:
                neg_terms.append((c, pn[(i, j)]))
    b.eq_sums(pos_terms, neg_terms)

print(f"CNF: {b.cnf.nv} vars, {len(b.cnf.clauses)} clauses", flush=True)
tmo = int(sys.argv[1]) if len(sys.argv) > 1 else None
res, model = b.solve(timeout=tmo)
print("result:", res, flush=True)
if res == "SAT":
    a = [0] * n
    for i, o in enumerate(orbs):
        v = 1 if b.var(("pos", i)) in model else (-1 if b.var(("neg", i)) in model else 0)
        for x in o:
            a[x] = v
    P = [i for i, x in enumerate(a) if x == 1]
    N = [i for i, x in enumerate(a) if x == -1]
    check(n, k, P, N, proper=False)
    print("VERIFIED CW(120,49)! proper =", is_proper(n, P, N))
    print("P =", P)
    print("N =", N)
elif res == "UNSAT":
    print("THEOREM: no CW(120,49) exists (complete multiplier-orbit exhaust).")

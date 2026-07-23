#!/usr/bin/env python3
"""Sanity-check the CNF machinery on a known-SAT case: CW(13,9) with
multiplier 3 (exists: q=3 classical family). Expect SAT and a verified witness."""
import sys
import numpy as np

sys.path.insert(0, ".")
sys.path.insert(0, "../../../solutions/P11")
from icw_enum import orbits_of
from verify import check
from cnf_cw import Builder, ternary, product_lits

n, k, mult = 13, 9, 3
orbs = orbits_of(mult, n)
sizes = [len(o) for o in orbs]
no = len(orbs)
C = np.zeros((no, no, n), dtype=np.int64)
for i, oi in enumerate(orbs):
    for j, oj in enumerate(orbs):
        for x in oi:
            for y in oj:
                C[i, j, (y - x) % n] += 1

b = Builder()
T = b.var("TRUE")
b.add(T)
tv = [ternary(b, i) for i in range(no)]
pp, pn = {}, {}
for i in range(no):
    for j in range(i, no):
        if i == j:
            pp[(i, i)] = b.or2(tv[i][0], tv[i][1])
            pn[(i, i)] = None
        else:
            pp[(i, j)], pn[(i, j)] = product_lits(b, *tv[i], *tv[j])
b.eq_sums([(sizes[i], pp[(i, i)]) for i in range(no)], [(k, T)])
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

res, model = b.solve(timeout=60)
assert res == "SAT", f"expected SAT, got {res}"
a = [0] * n
for i, o in enumerate(orbs):
    v = 1 if b.var(("pos", i)) in model else (-1 if b.var(("neg", i)) in model else 0)
    for x in o:
        a[x] = v
P = [i for i, x in enumerate(a) if x == 1]
N = [i for i, x in enumerate(a) if x == -1]
check(n, k, P, N, proper=False)
print("PASS: encoder sane, CW(13,9) witness P =", P, "N =", N)

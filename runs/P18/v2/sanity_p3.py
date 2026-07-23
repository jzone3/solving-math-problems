#!/usr/bin/env python3
"""Sanity check of the SAT encoding: the p >= 3 variant (moduli m = p-1, p prime >= 3,
i.e. modulus 2 allowed) must be SAT over L = 360 (Selfridge). Same encoding as
sat_cover.py but with the p >= 3 pool and no symmetry breaking."""
import time
from sympy import isprime, divisors
from pysat.solvers import Cadical153

L = 360
P = sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 3)
print("pool:", P)
var, nv, clauses = {}, 0, []
for m in P:
    for a in range(m):
        nv += 1
        var[(m, a)] = nv
for m in P:
    for i in range(m):
        for j in range(i + 1, m):
            clauses.append([-var[(m, i)], -var[(m, j)]])
for x in range(L):
    clauses.append([var[(m, x % m)] for m in P])
t0 = time.time()
with Cadical153(bootstrap_with=clauses) as s:
    res = s.solve()
    print("SAT" if res else "UNSAT", f"{time.time()-t0:.1f}s")
    assert res, "encoding sanity check FAILED: p>=3 variant must be SAT over 360"
    model = set(l for l in s.get_model() if l > 0)
    W = sorted(((a, m) for (m, a), v in var.items() if v in model), key=lambda t: t[1])
    covered = bytearray(L)
    ms = [m for _, m in W]
    assert len(set(ms)) == len(ms)
    for a, m in W:
        for x in range(a, L, m):
            covered[x] = 1
    assert all(covered)
    print("witness verified:", W)

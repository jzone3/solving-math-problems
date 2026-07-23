#!/usr/bin/env python3
"""Enumerate sigma-invariant HoSi copies edge-disjoint from H0, per fv class.
Writes disjoint_cls<c>.txt (25 orbit indices per line).
Usage: enum_disjoint.py <cls> [cap]
"""
import sys, time
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195
from search_sat import perm_order7, close_group, edge_orbits, cycle_orbit_reps, N

cls = int(sys.argv[1])
cap = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9

group = close_group(perm_order7())
orbits, seen = edge_orbits(group)
no = len(orbits)
tri = cycle_orbit_reps(group, seen, 3)
c4 = cycle_orbit_reps(group, seen, 4)
fv_orbits = sorted({seen[(min(49, u), max(49, u))] for u in range(N) if u != 49})
vreps = [0, 7, 14, 21, 28, 35, 42, 49]

pool = IDPool()
Y = [pool.id(('y', o)) for o in range(no)]
cnf = CNF()
for v in vreps:
    w = {}
    for u in range(N):
        if u == v:
            continue
        o = seen[(min(u, v), max(u, v))]
        w[o] = w.get(o, 0) + 1
    lits = []
    for o, wt in w.items():
        lits.append(Y[o])
        for d in range(wt - 1):
            y = pool.id(('dup', o, v, d))
            cnf.append([-y, Y[o]]); cnf.append([y, -Y[o]])
            lits.append(y)
    cnf.extend(CardEnc.equals(lits=lits, bound=7, vpool=pool,
                              encoding=EncType.totalizer).clauses)
cnf.extend(CardEnc.equals(lits=Y, bound=25, vpool=pool,
                          encoding=EncType.totalizer).clauses)
for t in tri:
    cnf.append([-Y[o] for o in t])
for q in c4:
    cnf.append([-Y[o] for o in q])

H0 = set(int(x) for x in open('copy0_orbits.txt').read().split())
cnf.append([Y[fv_orbits[cls]]])
for o in H0:
    cnf.append([-Y[o]])

t0 = time.time()
cnt = 0
with Cadical195(bootstrap_with=cnf) as s, open(f"disjoint_cls{cls}.txt", 'w') as f:
    while cnt < cap and s.solve():
        m = set(l for l in s.get_model() if l > 0)
        cp = [o for o in range(no) if Y[o] in m]
        f.write(" ".join(map(str, cp)) + "\n")
        cnt += 1
        s.add_clause([-Y[o] for o in cp])
        if cnt % 1000 == 0:
            print(f"cls {cls}: {cnt} ({time.time()-t0:.0f}s)", flush=True)
print(f"cls {cls}: TOTAL {cnt} ({time.time()-t0:.0f}s)", flush=True)

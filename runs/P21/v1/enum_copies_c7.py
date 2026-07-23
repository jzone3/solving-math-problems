#!/usr/bin/env python3
"""
Phase 1 (C7): enumerate ALL C7-invariant Hoffman-Singleton subgraphs of K50
(sigma = seven 7-cycles on 0..48, fixed point 49), as sets of 25 edge orbits.
Each copy is 7-regular girth>=5 on 50 vertices => HoSi.
Enumeration: single-color SAT instance + blocking clauses.
Output: copies_c7.txt, one copy per line = sorted orbit indices.
Also writes orbits_c7.txt mapping orbit index -> its 7 edges.
"""
import time
from search_sat import perm_order7, close_group, edge_orbits, cycle_orbit_reps
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

N = 50
group = close_group(perm_order7())
orbits, seen = edge_orbits(group)
no = len(orbits)
tri = cycle_orbit_reps(group, seen, 3)
c4 = cycle_orbit_reps(group, seen, 4)
print(f"{no} orbits, {len(tri)} tri reps, {len(c4)} c4 reps", flush=True)

pool = IDPool()
X = lambda o: pool.id(('x', o))
cnf = CNF()

# degree 7 at each vertex-orbit representative
vreps = [0, 7, 14, 21, 28, 35, 42, 49]
for v in vreps:
    w = {}
    for u in range(N):
        if u == v: continue
        o = seen[(min(u, v), max(u, v))]
        w[o] = w.get(o, 0) + 1
    lits = []
    for o, wt in w.items():
        lits.append(X(o))
        for d in range(wt - 1):
            y = pool.id(('dup', o, v, d))
            cnf.append([-y, X(o)]); cnf.append([y, -X(o)])
            lits.append(y)
    cnf.extend(CardEnc.equals(lits=lits, bound=7, vpool=pool,
                              encoding=EncType.totalizer).clauses)
for t in tri:
    cnf.append([-X(o) for o in t])
for q in c4:
    cnf.append([-X(o) for o in q])
cnf.extend(CardEnc.equals(lits=[X(o) for o in range(no)], bound=25, vpool=pool,
                          encoding=EncType.totalizer).clauses)

with open('orbits_c7.txt', 'w') as f:
    for i, orb in enumerate(orbits):
        f.write(f"{i} " + " ".join(f"{u},{v}" for (u, v) in orb) + "\n")

t0 = time.time()
count = 0
with Cadical195(bootstrap_with=cnf) as s, open('copies_c7.txt', 'w') as out:
    while s.solve():
        model = set(l for l in s.get_model() if l > 0)
        copy = sorted(o for o in range(no) if X(o) in model)
        assert len(copy) == 25
        out.write(" ".join(map(str, copy)) + "\n")
        out.flush()
        count += 1
        if count % 100 == 0:
            print(f"{count} copies, {time.time()-t0:.0f}s", flush=True)
        s.add_clause([-X(o) for o in copy])
print(f"DONE: {count} C7-invariant HoSi copies, {time.time()-t0:.0f}s", flush=True)

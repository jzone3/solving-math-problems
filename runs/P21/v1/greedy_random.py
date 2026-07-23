#!/usr/bin/env python3
"""P21 v1: randomized copy-by-copy construction of a C7-invariant 6-packing.

Level d (d=0..k-1) picks a sigma-invariant HoSi copy in fixed-vertex class
class_order[d], edge-disjoint from all previously chosen copies.  Copy 0 is the
fixed H0 (sound: N(<sigma>) is transitive on sigma-invariant copies).  Each
level is a small SAT instance over the 175 sigma-orbits; diversity comes from
random assumption seeding; on failure we retry with fresh randomness, and after
`tries` failures at a level we restart from level 1.

Usage: greedy_random.py <k> <seed> [out]
"""
import os, sys, random, time
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195
from search_sat import perm_order7, close_group, edge_orbits, cycle_orbit_reps, N

k = int(sys.argv[1])
seed = int(sys.argv[2])
outpath = sys.argv[3] if len(sys.argv) > 3 else f"w_greedy_k{k}_s{seed}.txt"
rng = random.Random(seed)

group = close_group(perm_order7())
orbits, seen = edge_orbits(group)
no = len(orbits)
tri = cycle_orbit_reps(group, seen, 3)
c4 = cycle_orbit_reps(group, seen, 4)
fv_orbits = sorted({seen[(min(49, u), max(49, u))] for u in range(N) if u != 49})
vreps = [0, 7, 14, 21, 28, 35, 42, 49]

# base CNF for "one sigma-invariant HoSi copy" over orbit vars 1..no
pool = IDPool()
Y = [pool.id(('y', o)) for o in range(no)]
base = CNF()
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
            base.append([-y, Y[o]]); base.append([y, -Y[o]])
            lits.append(y)
    base.extend(CardEnc.equals(lits=lits, bound=7, vpool=pool,
                               encoding=EncType.totalizer).clauses)
base.extend(CardEnc.equals(lits=Y, bound=25, vpool=pool,
                           encoding=EncType.totalizer).clauses)
for t in tri:
    base.append([-Y[o] for o in t])
for q in c4:
    base.append([-Y[o] for o in q])

H0 = [int(x) for x in open('copy0_orbits.txt').read().split()]
assert len(H0) == 25

def solve_copy(cls, banned, rand_orbits):
    """find copy containing fv_orbits[cls], avoiding banned orbits;
    rand_orbits: list of orbit indices to force in (assumptions)."""
    with Cadical195(bootstrap_with=base) as s:
        assum = [Y[fv_orbits[cls]]] + [-Y[o] for o in banned] + \
                [Y[o] for o in rand_orbits]
        if s.solve(assumptions=assum):
            m = set(l for l in s.get_model() if l > 0)
            return [o for o in range(no) if Y[o] in m]
    return None

cls_of_H0 = [i for i, f in enumerate(fv_orbits) if f in H0]
assert cls_of_H0 == [0]
all_classes = list(range(7))

t0 = time.time()
attempt = 0
while True:
    attempt += 1
    classes = [c for c in all_classes if c != 0]
    rng.shuffle(classes)
    classes = classes[:k-1]
    chosen = [H0]
    used = set(H0)
    ok = True
    for lvl, cls in enumerate(classes):
        got = solve_copy(cls, used, [])
        if got:
            # try to diversify with random forced orbits
            cand = [o for o in range(no) if o not in used and o not in fv_orbits]
            for t in range(8):
                rng.shuffle(cand)
                alt = solve_copy(cls, used, cand[:rng.randint(1, 3)])
                if alt:
                    got = alt
                    break
        if not got:
            ok = False
            break
        chosen.append(got)
        used |= set(got)
    if ok:
        print(f"SUCCESS attempt {attempt} ({time.time()-t0:.0f}s)", flush=True)
        with open(outpath, 'w') as f:
            for c, cp in enumerate(chosen):
                for o in cp:
                    for (u, v) in orbits[o]:
                        f.write(f"{c} {u} {v}\n")
        sys.exit(0)
    if attempt % 10 == 0:
        print(f"attempt {attempt}, reached depth {len(chosen)}/{k} ({time.time()-t0:.0f}s)",
              flush=True)

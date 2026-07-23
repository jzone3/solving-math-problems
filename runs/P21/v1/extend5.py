#!/usr/bin/env python3
"""P21 v1: enumerate C5xC5-invariant 5-packings, and for each try to find an
arbitrary (no prescribed symmetry) 6th edge-disjoint HoSi copy in the leftover
14-regular graph, via raw-edge SAT: 350 edge vars, degree 7 at each vertex,
no triangle, no C4 (=> 7-regular girth>=5 on 50 vertices = HoSi).

If SAT: a 6-packing whose first five copies are order-25-invariant -- checked
by verify.py; would be outside Macaj's order-7 family.

Usage: extend5.py <seed_offset> [max_packings]
"""
import sys, time, itertools
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195
from search_sat import group_c5xc5, close_group, edge_orbits, cycle_orbit_reps, N

offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9

group = close_group(group_c5xc5())
orbits, seen = edge_orbits(group)
no = len(orbits)
tri = cycle_orbit_reps(group, seen, 3)
c4 = cycle_orbit_reps(group, seen, 4)
K = 5

# --- outer: 5-packing enumerator over C5xC5 orbits ---
pool = IDPool()
def X(o, c): return pool.id(('x', o, c))
cnf = CNF()
for o in range(no):
    for i in range(K):
        for j in range(i+1, K):
            cnf.append([-X(o, i), -X(o, j)])
vseen = set(); vreps = []
for v in range(N):
    if v in vseen: continue
    vreps.append(v)
    for g in group: vseen.add(g[v])
for v in vreps:
    w = {}
    for u in range(N):
        if u == v: continue
        o = seen[(min(u, v), max(u, v))]
        w[o] = w.get(o, 0) + 1
    for c in range(K):
        lits = []
        for o, wt in w.items():
            lits.append(X(o, c))
            for d in range(wt - 1):
                y = pool.id(('dup', o, c, v, d))
                cnf.append([-y, X(o, c)]); cnf.append([y, -X(o, c)])
                lits.append(y)
        cnf.extend(CardEnc.equals(lits=lits, bound=7, vpool=pool,
                                  encoding=EncType.totalizer).clauses)
for c in range(K):
    for t in tri:
        cnf.append([-X(o, c) for o in t])
    for q in c4:
        cnf.append([-X(o, c) for o in q])

# --- inner: raw-edge 6th copy in leftover graph ---
def sixth_copy(used_edges):
    left = [e for e in itertools.combinations(range(N), 2) if e not in used_edges]
    assert len(left) == 350
    adj = {}
    p2 = IDPool()
    E = {}
    for (u, v) in left:
        E[(u, v)] = p2.id(('e', u, v))
        adj.setdefault(u, []).append((u, v)); adj.setdefault(v, []).append((u, v))
    c2 = CNF()
    for v in range(N):
        c2.extend(CardEnc.equals(lits=[E[e] for e in adj[v]], bound=7, vpool=p2,
                                 encoding=EncType.totalizer).clauses)
    leftset = set(left)
    def has(a, b):
        return (min(a, b), max(a, b)) in leftset
    def var(a, b):
        return E[(min(a, b), max(a, b))]
    for a, b, c in itertools.combinations(range(N), 3):
        if has(a, b) and has(b, c) and has(a, c):
            c2.append([-var(a, b), -var(b, c), -var(a, c)])
    for a, b in itertools.combinations(range(N), 2):
        common = [w for w in range(N) if w != a and w != b and has(a, w) and has(b, w)]
        for w1, w2 in itertools.combinations(common, 2):
            c2.append([-var(a, w1), -var(w1, b), -var(b, w2), -var(w2, a)])
    with Cadical195(bootstrap_with=c2) as s:
        if s.solve():
            m = set(l for l in s.get_model() if l > 0)
            return [e for e in left if E[e] in m]
    return None

t0 = time.time()
cnt = 0
with Cadical195(bootstrap_with=cnf) as s:
    while cnt < maxp and s.solve():
        m = set(l for l in s.get_model() if l > 0)
        packing = {}
        sel = []
        for o in range(no):
            for c in range(K):
                if X(o, c) in m:
                    sel.append((o, c))
                    packing.setdefault(c, []).extend(orbits[o])
        cnt += 1
        # block all 120 color-permutations of this packing (extension test is
        # invariant under color relabeling)
        classes = {}
        for (o, c) in sel:
            classes.setdefault(c, []).append(o)
        for perm in itertools.permutations(range(K)):
            s.add_clause([-X(o, perm[c]) for c in classes for o in classes[c]])
        if cnt <= offset:
            continue
        used = set()
        for c in packing:
            for (u, v) in packing[c]:
                used.add((min(u, v), max(u, v)))
        assert len(used) == 875
        ext = sixth_copy(used)
        print(f"packing {cnt}: 6th copy {'FOUND' if ext else 'none'} "
              f"({time.time()-t0:.0f}s)", flush=True)
        if ext:
            out = f"w_ext6_p{cnt}.txt"
            with open(out, 'w') as f:
                for c in range(K):
                    for (u, v) in packing[c]:
                        f.write(f"{c} {min(u,v)} {max(u,v)}\n")
                for (u, v) in ext:
                    f.write(f"5 {u} {v}\n")
            print(f"WROTE {out}", flush=True)
            sys.exit(0)
print(f"exhausted after {cnt} packings ({time.time()-t0:.0f}s)", flush=True)

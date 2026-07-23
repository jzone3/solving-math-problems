#!/usr/bin/env python3
"""V3: Kramer-Mesner (prescribed automorphisms) orbit-matrix ILP for the 4 open BTD instances.

A BTD(V,B; r1,r2,R; K,Lam): B blocks = multisets of size K over V elements, multiplicities <=2;
each element appears with multiplicity 1 in exactly r1 blocks, multiplicity 2 in exactly r2;
for every unordered pair i<j: sum over blocks of m(i)*m(j) == Lam.

We prescribe a permutation group G on the V points, assume the block multiset is G-invariant,
enumerate G-orbits of candidate blocks (functions V->{0,1,2}, sum K), and solve the orbit ILP
with OR-Tools CP-SAT.

Usage: km_solve.py INSTANCE GROUP TIMELIMIT_S
  INSTANCE in {1,2,3,4}; GROUP name from GROUPS[V].
"""
import sys, json, time
from itertools import combinations
from ortools.sat.python import cp_model

INSTANCES = {
    1: dict(V=14, B=18, r1=7, r2=1, K=7, Lam=4),
    2: dict(V=12, B=15, r1=6, r2=2, K=8, Lam=6),
    3: dict(V=12, B=20, r1=4, r2=3, K=6, Lam=4),
    4: dict(V=14, B=28, r1=8, r2=3, K=7, Lam=6),
}

def cyc(V, shift):
    return tuple((i + shift) % V for i in range(V))

def two_orbit_cyc(V):  # V=2n: rotate each half by 1
    n = V // 2
    return tuple([(i + 1) % n for i in range(n)] + [n + ((i + 1) % n) for i in range(n)])

def mult_two_orbits(V, m):  # x -> m*x mod n on each half
    n = V // 2
    return tuple([(m * i) % n for i in range(n)] + [n + ((m * i) % n) for i in range(n)])

def reflect(V):
    return tuple((-i) % V for i in range(V))

def cyc_type(V, lens):
    """Permutation with disjoint cycles of the given lengths on 0..V-1 (rest fixed)."""
    perm = list(range(V))
    pos = 0
    for L in lens:
        pts = list(range(pos, pos + L))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            perm[a] = b
        pos += L
    assert pos <= V
    return tuple(perm)

GROUPS = {
    14: {
        'C14': [cyc(14, 1)],
        'C7': [two_orbit_cyc(14)],
        'C2': [cyc(14, 7)],
        'D7': [two_orbit_cyc(14), tuple([(-i) % 7 for i in range(7)] + [7 + ((-i) % 7) for i in range(7)])],
        'F21': [two_orbit_cyc(14), mult_two_orbits(14, 2)],
        'D14': [cyc(14, 1), reflect(14)],
        'C7xC2': [two_orbit_cyc(14), tuple(list(range(7, 14)) + list(range(7)))],
        'C7f': [cyc_type(14, [7])],           # one 7-cycle, 7 fixed points
        'C2a': [cyc_type(14, [2] * 6)],        # 6 transpositions, 2 fixed
        'C2b': [cyc_type(14, [2] * 5)],
        'C2c': [cyc_type(14, [2] * 4)],
        'C3a': [cyc_type(14, [3] * 4)],        # 4 3-cycles, 2 fixed
        'C3b': [cyc_type(14, [3] * 3)],
        'C4a': [cyc_type(14, [4] * 3)],        # order 4, 2 fixed
        'C6a': [cyc_type(14, [6, 6])],
        'C13': [cyc_type(14, [13])],
        'C11a': [cyc_type(14, [11])],
        'C5a': [cyc_type(14, [5, 5])],
        'C5b': [cyc_type(14, [5])],
        'C3c': [cyc_type(14, [3] * 2)],
        'C3d': [cyc_type(14, [3])],
        'C2d': [cyc_type(14, [2] * 3)],
        'C2e': [cyc_type(14, [2] * 2)],
        'C2f': [cyc_type(14, [2])],
    },
    12: {
        'C12': [cyc(12, 1)],
        'C6': [tuple([(i + 1) % 6 for i in range(6)] + [6 + ((i + 1) % 6) for i in range(6)])],
        'C4': [tuple([(i + 1) % 4 for i in range(4)] + [4 + ((i + 1) % 4) for i in range(4)] + [8 + ((i + 1) % 4) for i in range(4)])],
        'C3': [tuple([(i + 1) % 3 for i in range(3)] + [3 + ((i + 1) % 3) for i in range(3)] + [6 + ((i + 1) % 3) for i in range(3)] + [9 + ((i + 1) % 3) for i in range(3)])],
        'C2': [cyc(12, 6)],
        'D6': [cyc(12, 1) if False else tuple([(i + 1) % 6 for i in range(6)] + [6 + ((i + 1) % 6) for i in range(6)]),
               tuple([(-i) % 6 for i in range(6)] + [6 + ((-i) % 6) for i in range(6)])],
        'D12': [cyc(12, 1), reflect(12)],
        'C6+1': [cyc(12, 2)],  # i->i+2 mod 12: two orbits of 6 interleaved
        'G12': [ (1,2,0, 4,5,3, 7,8,6, 10,11,9), (3,4,5, 0,1,2, 9,10,11, 6,7,8) ],  # some perm group, valid for KM
        'C3a': [cyc_type(12, [3] * 3)],        # 3 3-cycles, 3 fixed
        'C3b': [cyc_type(12, [3] * 2)],
        'C2a': [cyc_type(12, [2] * 5)],
        'C2b': [cyc_type(12, [2] * 4)],
        'C2c': [cyc_type(12, [2] * 3)],
        'C5': [cyc_type(12, [5, 5])],
        'C11': [cyc_type(12, [11])],
        'C4b': [cyc_type(12, [4, 4])],
        'C6b': [cyc_type(12, [6])],
        'C7a': [cyc_type(12, [7])],
        'C5b': [cyc_type(12, [5])],
        'C3c': [cyc_type(12, [3])],
        'C2d': [cyc_type(12, [2] * 2)],
        'C2e': [cyc_type(12, [2])],
    },
}

def close_group(V, gens):
    ident = tuple(range(V))
    group = {ident}
    frontier = [ident]
    while frontier:
        nxt = []
        for g in frontier:
            for h in gens:
                gh = tuple(h[g[i]] for i in range(V))
                if gh not in group:
                    group.add(gh)
                    nxt.append(gh)
        frontier = nxt
    return sorted(group)

def enum_blocks(V, K):
    blocks = []
    for d in range(0, K // 2 + 1):  # number of 2s
        ones = K - 2 * d
        if ones < 0 or d + ones > V:
            continue
        for twos in combinations(range(V), d):
            rest = [x for x in range(V) if x not in twos]
            for onset in combinations(rest, ones):
                m = [0] * V
                for x in twos: m[x] = 2
                for x in onset: m[x] = 1
                blocks.append(tuple(m))
    return blocks

def orbits_of(items, group, act):
    idx = {it: None for it in items}
    orbs = []
    for it in items:
        if idx[it] is not None: continue
        oid = len(orbs)
        orb = set()
        stack = [it]
        idx[it] = oid
        orb.add(it)
        while stack:
            cur = stack.pop()
            for g in group:
                im = act(g, cur)
                if idx[im] is None:
                    idx[im] = oid
                    orb.add(im)
                    stack.append(im)
        orbs.append(sorted(orb))
    return orbs, idx

def act_block(g, b):
    V = len(b)
    out = [0] * V
    for i in range(V):
        out[g[i]] = b[i]
    return tuple(out)

def act_elem(g, e):
    return g[e]

def act_pair(g, p):
    a, b = g[p[0]], g[p[1]]
    return (a, b) if a < b else (b, a)

def solve(inst_id, group_name, tl):
    p = INSTANCES[inst_id]
    V, B, r1, r2, K, Lam = p['V'], p['B'], p['r1'], p['r2'], p['K'], p['Lam']
    gens = GROUPS[V][group_name]
    G = close_group(V, gens)
    t0 = time.time()
    blocks = enum_blocks(V, K)
    borbs, _ = orbits_of(blocks, G, act_block)
    eorbs, _ = orbits_of(list(range(V)), G, act_elem)
    porbs, _ = orbits_of(list(combinations(range(V), 2)), G, act_pair)
    print(f"inst{inst_id} group={group_name} |G|={len(G)} blocks={len(blocks)} borbs={len(borbs)} eorbs={len(eorbs)} porbs={len(porbs)} enum={time.time()-t0:.1f}s", flush=True)

    model = cp_model.CpModel()
    ub = min(B, r2 * 3 + r1)  # loose
    xs = [model.NewIntVar(0, ub, f"x{i}") for i in range(len(borbs))]
    # block count
    model.Add(sum(len(o) * x for o, x in zip(borbs, xs)) == B)
    # element constraints
    for eo in eorbs:
        e = eo[0]
        c1 = [sum(1 for b in o if b[e] == 1) for o in borbs]
        c2 = [sum(1 for b in o if b[e] == 2) for o in borbs]
        model.Add(sum(c * x for c, x in zip(c1, xs) if c) == r1)
        model.Add(sum(c * x for c, x in zip(c2, xs) if c) == r2)
    # pair constraints
    for po in porbs:
        i, j = po[0]
        cc = [sum(b[i] * b[j] for b in o) for o in borbs]
        model.Add(sum(c * x for c, x in zip(cc, xs) if c) == Lam)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    import os
    solver.parameters.num_workers = int(os.environ.get('WORKERS', '8'))
    solver.parameters.log_search_progress = False
    st = solver.Solve(model)
    name = solver.StatusName(st)
    print(f"inst{inst_id} group={group_name} status={name} time={solver.WallTime():.1f}s", flush=True)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        cols = []
        for o, x in zip(borbs, xs):
            v = solver.Value(x)
            for _ in range(v):
                cols.extend(o)
        assert len(cols) == B
        mat = [[cols[j][i] for j in range(B)] for i in range(V)]
        fn = f"witness_inst{inst_id}_{group_name}.json"
        json.dump(dict(params=p, matrix=mat, group=group_name), open(fn, 'w'))
        print(f"WITNESS -> {fn}", flush=True)
        return 'SAT'
    return name

if __name__ == '__main__':
    inst = int(sys.argv[1]); grp = sys.argv[2]; tl = float(sys.argv[3])
    solve(inst, grp, tl)

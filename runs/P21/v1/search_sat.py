#!/usr/bin/env python3
"""
P21 v1: prescribed-automorphism SAT search for k edge-disjoint Hoffman-Singleton
copies in K50 (k=6 packing, k=7 decomposition).

Encoding (exact, integer-only):
  - Fix a permutation sigma on V={0..49} of order p (7 with one fixed point,
    5 fixed-point-free, or a semiregular group of order 25).
  - Edge orbits of <sigma> partition E(K50).  Each of the k color classes must be
    a union of orbits (the packing is <sigma>-invariant).
  - Variables x[o][c] : orbit o gets color c (colors 0..k-1; if k==6 an orbit may
    also be uncolored = leftover).
  - Constraints:
      * each orbit gets at most one color (exactly one if k==7),
      * every vertex has degree exactly 7 in every color (weighted card on orbit
        representatives; weights 1 or 2),
      * no monochromatic triangle and no monochromatic 4-cycle
        (one representative per sigma-orbit of triangles / 4-cycles).
  - Any color class then is a 7-regular girth>=5 graph on 50 vertices, i.e. the
    Hoffman-Singleton graph (unique (7,5)-Moore graph); no isomorphism test needed.

Symmetry breaking: colors are interchangeable; where the group has a fixed vertex
(order 7), the 7 orbits through the fixed vertex are bijectively matched to colors.
"""
import sys, itertools, time
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

N = 50

def perm_order7():
    # one fixed point (49), seven 7-cycles on 0..48
    sigma = list(range(N))
    for b in range(7):
        for i in range(7):
            sigma[b*7 + i] = b*7 + (i+1) % 7
    sigma[49] = 49
    return [sigma]

def perm_order5_fpf():
    # ten 5-cycles
    sigma = list(range(N))
    for b in range(10):
        for i in range(5):
            sigma[b*5 + i] = b*5 + (i+1) % 5
    return [sigma]

def group_c5xc5():
    # elementary abelian 5^2 acting semiregularly with two orbits of size 25
    # vertices: orbit0 = 0..24 as (i,j) -> 5*i+j ; orbit1 = 25..49 similarly
    a = list(range(N)); b = list(range(N))
    for o in (0, 25):
        for i in range(5):
            for j in range(5):
                v = o + 5*i + j
                a[v] = o + 5*((i+1) % 5) + j
                b[v] = o + 5*i + (j+1) % 5
    return [a, b]

def group_c25():
    sigma = list(range(N))
    for o in (0, 25):
        for i in range(25):
            sigma[o + i] = o + (i+1) % 25
    return [sigma]

def group_f21():
    # F21 = <sigma, tau | sigma^7, tau^3, tau sigma tau^-1 = sigma^2>
    # vertex orbits: fixed pt 49; four 7-orbits (blocks 0..3, tau: i->2i);
    # one 21-orbit (blocks 4,5,6 cycled by tau).
    # tau fixes 5 vertices (49 and (b,0) for b=0..3), matching the K_{1,4}
    # fixed subgraph of order-3 automorphisms of HoSi.
    sigma = list(range(N))
    for b in range(7):
        for i in range(7):
            sigma[b*7 + i] = b*7 + (i+1) % 7
    sigma[49] = 49
    tau = list(range(N))
    for b in range(4):
        for i in range(7):
            tau[b*7 + i] = b*7 + (2*i) % 7
    for j in range(3):
        for i in range(7):
            tau[(4+j)*7 + i] = (4 + (j+1) % 3)*7 + (2*i) % 7
    tau[49] = 49
    # sanity
    t3 = [tau[tau[tau[v]]] for v in range(N)]
    assert t3 == list(range(N))
    lhs = [tau[sigma[v]] for v in range(N)]
    rhs = [sigma[sigma[tau[v]]] for v in range(N)]
    assert lhs == rhs, "tau sigma != sigma^2 tau"
    assert sum(1 for v in range(N) if tau[v] == v) == 5
    return [sigma, tau]

def close_group(gens):
    # returns list of permutations (tuples) forming the generated group
    ident = tuple(range(N))
    group = {ident}
    frontier = [ident]
    gens = [tuple(g) for g in gens]
    while frontier:
        new = []
        for h in frontier:
            for g in gens:
                comp = tuple(g[h[v]] for v in range(N))
                if comp not in group:
                    group.add(comp); new.append(comp)
        frontier = new
    return sorted(group)

def edge_orbits(group):
    seen = {}
    orbits = []
    for u in range(N):
        for v in range(u+1, N):
            e = (u, v)
            if e in seen:
                continue
            orb = set()
            for g in group:
                a, b = g[u], g[v]
                orb.add((min(a, b), max(a, b)))
            idx = len(orbits)
            orbits.append(sorted(orb))
            for f in orb:
                seen[f] = idx
    return orbits, seen

def cycle_orbit_reps(group, seen, size):
    """One representative per group-orbit of triangles (size=3) / 4-cycles (size=4).
    Returns list of tuples of edge-orbit indices (as multiset tuple)."""
    reps = set()
    done = set()
    if size == 3:
        it = itertools.combinations(range(N), 3)
        for (a, b, c) in it:
            key = (a, b, c)
            if key in done:
                continue
            # mark whole group orbit of this triangle as done
            for g in group:
                done.add(tuple(sorted((g[a], g[b], g[c]))))
            reps.add(tuple(sorted((seen[(a, b)], seen[(a, c)], seen[(b, c)]))))
    else:
        # 4-cycles: choose 4 vertices, 3 cyclic orderings
        for quad in itertools.combinations(range(N), 4):
            a, b, c, d = quad
            for (p, q, r, s) in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                cyc = canon_c4(p, q, r, s)
                if cyc in done:
                    continue
                for g in group:
                    done.add(canon_c4(g[p], g[q], g[r], g[s]))
                es = [ (min(p,q),max(p,q)), (min(q,r),max(q,r)),
                       (min(r,s),max(r,s)), (min(s,p),max(s,p)) ]
                reps.add(tuple(sorted(seen[e] for e in es)))
    return sorted(reps)

def canon_c4(p, q, r, s):
    cyc = (p, q, r, s)
    best = None
    for rot in range(4):
        t = cyc[rot:] + cyc[:rot]
        for cand in (t, tuple(reversed(t))):
            # normalize reversed rotationally too
            if best is None or cand < best:
                best = cand
    return best

def build_and_solve(name, gens, k, fixed_vertex=None, timeout=None, fix_copy=None,
                    miss=None):
    t0 = time.time()
    group = close_group(gens)
    orbits, seen = edge_orbits(group)
    no = len(orbits)
    print(f"[{name}] group order {len(group)}, {no} edge orbits, k={k}", flush=True)
    tri = cycle_orbit_reps(group, seen, 3)
    c4 = cycle_orbit_reps(group, seen, 4)
    print(f"[{name}] {len(tri)} triangle reps, {len(c4)} C4 reps ({time.time()-t0:.1f}s)", flush=True)

    pool = IDPool()
    def X(o, c): return pool.id(('x', o, c))
    cnf = CNF()

    # at-most-one color per orbit (exactly-one if k==7)
    for o in range(no):
        lits = [X(o, c) for c in range(k)]
        for i in range(k):
            for j in range(i+1, k):
                cnf.append([-lits[i], -lits[j]])
        if k == 7:
            cnf.append(lits)

    # optionally freeze a full copy (sound for C7: N(sigma) acts transitively on
    # sigma-invariant HoSi copies, see NOTES.md), colored by its fv-orbit class
    if fix_copy is not None:
        fv_orbits_all = sorted({seen[(min(fixed_vertex, u), max(fixed_vertex, u))]
                                for u in range(N) if u != fixed_vertex})
        fvo_of_copy = [o for o in fix_copy if o in fv_orbits_all]
        assert len(fvo_of_copy) == 1
        use0 = [o for i, o in enumerate(fv_orbits_all) if i != miss] if miss is not None \
               else fv_orbits_all
        assert fvo_of_copy[0] in use0, "miss class equals frozen copy's class"
        c0 = use0.index(fvo_of_copy[0])
        assert c0 < k
        print(f"[{name}] freezing copy of {len(fix_copy)} orbits as color {c0}", flush=True)
        fixset = set(fix_copy)
        for o in range(no):
            cnf.append([X(o, c0)] if o in fixset else [-X(o, c0)])

    # symmetry breaking: orbits through fixed vertex <-> colors
    if fixed_vertex is not None:
        fv_orbits = sorted({seen[(min(fixed_vertex, u), max(fixed_vertex, u))]
                            for u in range(N) if u != fixed_vertex})
        assert len(fv_orbits) == 7
        use = [o for i, o in enumerate(fv_orbits) if i != miss] if miss is not None \
              else fv_orbits
        assert len(use) >= k
        for c in range(k):
            cnf.append([X(use[c], c)])

    # degree constraints on orbit representatives of vertices
    vseen = set(); vreps = []
    for v in range(N):
        if v in vseen: continue
        vreps.append(v)
        for g in group: vseen.add(g[v])
    for v in vreps:
        # weight of each edge-orbit at v
        w = {}
        for u in range(N):
            if u == v: continue
            o = seen[(min(u, v), max(u, v))]
            w[o] = w.get(o, 0) + 1
        for c in range(k):
            lits = []
            for o, wt in w.items():
                lits.append(X(o, c))
                for d in range(wt - 1):
                    y = pool.id(('dup', o, c, v, d))
                    cnf.append([-y, X(o, c)]); cnf.append([y, -X(o, c)])
                    lits.append(y)
            enc = CardEnc.equals(lits=lits, bound=7, vpool=pool, encoding=EncType.totalizer)
            cnf.extend(enc.clauses)

    # global count: each color uses exactly 175/|orbit| orbits (all orbits same size here)
    osz = len(orbits[0])
    if all(len(o) == osz for o in orbits) and 175 % osz == 0:
        per = 175 // osz
        for c in range(k):
            enc = CardEnc.equals(lits=[X(o, c) for o in range(no)], bound=per,
                                 vpool=pool, encoding=EncType.totalizer)
            cnf.extend(enc.clauses)

    # no monochromatic triangle / C4
    for c in range(k):
        for t in tri:
            cnf.append([-X(o, c) for o in t])
        for q in c4:
            cnf.append([-X(o, c) for o in q])

    print(f"[{name}] CNF: {pool.top} vars, {len(cnf.clauses)} clauses ({time.time()-t0:.1f}s)", flush=True)
    with Cadical195(bootstrap_with=cnf) as s:
        sat = s.solve()
        print(f"[{name}] k={k}: {'SAT' if sat else 'UNSAT'} ({time.time()-t0:.1f}s)", flush=True)
        if sat:
            model = set(l for l in s.get_model() if l > 0)
            colors = {}
            for o in range(no):
                for c in range(k):
                    if X(o, c) in model:
                        colors.setdefault(c, []).extend(orbits[o])
            return colors
    return None

def build_and_solve_twisted(name, k):
    """F21-twisted search: sigma (order 7, fixed pt 49) stabilizes every color;
    tau (order 3, tau sigma tau^-1 = sigma^2) permutes colors by
    pi = (0 1 2), fixing colors 3..k-1.
    Variables over sigma-orbits as in the C7 case, plus linking clauses
    X[o][c] <-> X[tau(o)][pi(c)].  The four tau-invariant fixed-vertex orbits
    (blocks 0..3) must take pi-fixed colors; blocks 4,5,6 take colors 0,1,2."""
    t0 = time.time()
    sigma, tau = group_f21()
    group = close_group([sigma])          # C7 only: orbits/constraints as before
    orbits, seen = edge_orbits(group)
    no = len(orbits)
    # tau action on sigma-orbits
    tmap = []
    for o in range(no):
        u, v = orbits[o][0]
        a, b = tau[u], tau[v]
        tmap.append(seen[(min(a, b), max(a, b))])
    pi = lambda c: (c + 1) % 3 if c < 3 else c
    tri = cycle_orbit_reps(group, seen, 3)
    c4 = cycle_orbit_reps(group, seen, 4)
    print(f"[{name}] {no} orbits, {len(tri)} tri, {len(c4)} c4 ({time.time()-t0:.1f}s)", flush=True)

    pool = IDPool()
    def X(o, c): return pool.id(('x', o, c))
    cnf = CNF()
    for o in range(no):
        lits = [X(o, c) for c in range(k)]
        for i in range(k):
            for j in range(i+1, k):
                cnf.append([-lits[i], -lits[j]])
        if k == 7:
            cnf.append(lits)
    # twist links
    for o in range(no):
        for c in range(k):
            cnf.append([-X(o, c), X(tmap[o], pi(c))])
            cnf.append([X(o, c), -X(tmap[o], pi(c))])
    # fixed-vertex orbit assignment: block b fv orbit
    fvo = [seen[(min(49, b*7), max(49, b*7))] for b in range(7)]
    cnf.append([X(fvo[4], 0)])   # tau: block4->5->6
    if k == 7:
        # blocks 0..3 get the four pi-fixed colors 3,4,5,6
        for b in range(4):
            cnf.append([X(fvo[b], 3 + b)])
    else:
        # k=6: pi-fixed colors 3,4,5 go to three of blocks 0..3 (one uncolored),
        # keep order to break symmetry: color 3+i to the i-th colored block
        for b in range(4):
            # block b colored => with a pi-fixed color; ordering constraint:
            cnf.append([-X(fvo[b], 0)]); cnf.append([-X(fvo[b], 1)]); cnf.append([-X(fvo[b], 2)])
        # symmetry: color 3 on block 0 or (block0 uncolored and color3 on block1)...
        # simple ordering: if block a and block b (a<b) colored with pi-fixed colors,
        # colors increase: encode: block0 in {3,uncolored}, then next colored gets next color.
        # (light version: forbid color 4 or 5 on block 0, color 5 on block 1 unless...)
        cnf.append([-X(fvo[0], 4)]); cnf.append([-X(fvo[0], 5)])
        cnf.append([-X(fvo[1], 5)])
    # degree constraints (identical to untwisted C7 case)
    vreps = [0, 7, 14, 21, 28, 35, 42, 49]
    for v in vreps:
        w = {}
        for u in range(N):
            if u == v: continue
            o = seen[(min(u, v), max(u, v))]
            w[o] = w.get(o, 0) + 1
        for c in range(k):
            lits = []
            for o, wt in w.items():
                lits.append(X(o, c))
                for d in range(wt - 1):
                    y = pool.id(('dup', o, c, v, d))
                    cnf.append([-y, X(o, c)]); cnf.append([y, -X(o, c)])
                    lits.append(y)
            cnf.extend(CardEnc.equals(lits=lits, bound=7, vpool=pool,
                                      encoding=EncType.totalizer).clauses)
    for c in range(k):
        for t in tri:
            cnf.append([-X(o, c) for o in t])
        for q in c4:
            cnf.append([-X(o, c) for o in q])
        cnf.extend(CardEnc.equals(lits=[X(o, c) for o in range(no)], bound=25,
                                  vpool=pool, encoding=EncType.totalizer).clauses)
    print(f"[{name}] CNF: {pool.top} vars, {len(cnf.clauses)} clauses ({time.time()-t0:.1f}s)", flush=True)
    with Cadical195(bootstrap_with=cnf) as s:
        sat = s.solve()
        print(f"[{name}] k={k}: {'SAT' if sat else 'UNSAT'} ({time.time()-t0:.1f}s)", flush=True)
        if sat:
            model = set(l for l in s.get_model() if l > 0)
            colors = {}
            for o in range(no):
                for c in range(k):
                    if X(o, c) in model:
                        colors.setdefault(c, []).extend(orbits[o])
            return colors
    return None

def dump(colors, path):
    with open(path, 'w') as f:
        for c in sorted(colors):
            for (u, v) in sorted(colors[c]):
                f.write(f"{c} {u} {v}\n")
    print("witness written to", path)

if __name__ == '__main__':
    which = sys.argv[1]
    k = int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else None
    if which == 'c7':
        res = build_and_solve('C7', perm_order7(), k, fixed_vertex=49)
    elif which == 'c5':
        res = build_and_solve('C5fpf', perm_order5_fpf(), k)
    elif which == 'c5xc5':
        res = build_and_solve('C5xC5', group_c5xc5(), k)
    elif which == 'c25':
        res = build_and_solve('C25', group_c25(), k)
    elif which == 'f21':
        res = build_and_solve_twisted('F21', k)
    elif which == 'c7fix':
        # optional 4th arg: index of fv class to leave out (k=6), else None
        miss = int(sys.argv[4]) if len(sys.argv) > 4 else None
        copy0 = [int(x) for x in open('copies_c7.txt').readline().split()]
        res = build_and_solve('C7fix', perm_order7(), k, fixed_vertex=49,
                              fix_copy=copy0, miss=miss)
    else:
        raise SystemExit('unknown group')
    if res and out:
        dump(res, out)

"""Exact large-neighbourhood *descent* on a non-4-colorable vertex set.

Greedy deletion is the standard minimiser and it is badly off: on W4, which
provably contains Parts' 509, every deletion-style reducer in this run stalls
around 1850 vertices (E13).  The reason is that removing one vertex at a time
can never trade a region for a cheaper region.  This script does exactly that
trade, and does it *completely*:

    pick a centre, drop the H vertices of S nearest it,
    ask a hitting-set solver for <= H-1 replacements from the pool around the
    hole such that the result is still non-4-colorable.

Each neighbourhood ends in a strictly smaller certified witness, or in UNSAT
(no cheaper refill of that region exists at all) -- never in a heuristic floor.

Env: POOL, START (pickle of the vertex list), H, HOPS, TIME, SEED, OUT.
"""
import os
import pickle
import random
import subprocess
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

import coremin
import lattice
from sat import color_cnf, write_cnf, KISSAT

START = os.environ.get('START', 'rec_w4x.pkl')
H = int(os.environ.get('H', '30'))
HOPS = int(os.environ.get('HOPS', '1'))
TLIM = float(os.environ.get('TIME', '600'))      # per neighbourhood
TABU = int(os.environ.get('TABU', '150000'))
NOISE = float(os.environ.get('NOISE', '0.02'))
SEED = int(os.environ.get('SEED', '1'))
RANDHOLE = int(os.environ.get('RANDHOLE', '0'))
DROPK = int(os.environ.get('DROPK', '1'))   # refill must be this much smaller
OUT = os.environ.get('OUT', f'descend_{SEED}.pkl')

E, adj, PTS = coremin.E, coremin.adj, coremin.allpts
om = lattice.omega_t_complex(int(os.environ.get('OMT', '4')))
Z = [lattice.to_complex(q) * (om if t == 'B' else 1) for t, q in PTS]
rng = random.Random(SEED)


def kissat_color(S, tag):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    nvars, cls = color_cnf(len(S), E2, 4)
    cnf = f'/tmp/ld_{tag}_{os.getpid()}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return None
        pos = {int(x) for line in r.stdout.splitlines() if line.startswith('v ')
               for x in line[2:].split() if int(x) > 0}
        return {v: c for i, v in enumerate(S) for c in range(4)
                if 4 * i + c + 1 in pos}
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def hyperedge(fixed_col, movable, nbr):
    """Colour `movable` by min-conflicts on top of `fixed_col`; return a vertex
    cover of the surviving conflicts (= a set whose removal leaves the rest
    4-colorable, i.e. a clause every witness must hit)."""
    col = dict(fixed_col)
    mv = set(movable)
    for v in movable:
        col[v] = rng.randrange(4)
    cnt = {v: [0, 0, 0, 0] for v in movable}
    for v in movable:
        for u in nbr[v]:
            if u in col:
                cnt[v][col[u]] += 1
    bad = {v for v in movable if cnt[v][col[v]]}
    for _ in range(TABU):
        if not bad:
            break
        v = rng.choice(tuple(bad))
        old = col[v]
        c = (rng.randrange(4) if rng.random() < NOISE
             else min(range(4), key=lambda k: (cnt[v][k], rng.random())))
        if c == old:
            continue
        col[v] = c
        for u in nbr[v]:
            if u in mv:
                cnt[u][old] -= 1
                cnt[u][c] += 1
                (bad.add if cnt[u][col[u]] else bad.discard)(u)
        (bad.add if cnt[v][c] else bad.discard)(v)
    conf = [(u, v) for u, v in E
            if u in col and v in col and col[u] == col[v]]
    if any(u not in mv and v not in mv for u, v in conf):
        return None
    deg = {}
    for u, v in conf:
        for x in (u, v):
            if x in mv:
                deg[x] = deg.get(x, 0) + 1
    D = set()
    while conf:
        x = max(deg, key=lambda k: deg[k])
        D.add(x)
        conf = [(u, v) for u, v in conf if u != x and v != x]
        deg = {}
        for u, v in conf:
            for y in (u, v):
                if y in mv and y not in D:
                    deg[y] = deg.get(y, 0) + 1
    return D


def neighbourhood(S, tag):
    """One exact trade: returns a strictly smaller witness, or None."""
    Sset = set(S)
    if RANDHOLE:
        drop = set(rng.sample(S, H))
    else:
        c = Z[S[rng.randrange(len(S))]]
        drop = set(sorted(S, key=lambda v: abs(Z[v] - c))[:H])
    fix = sorted(Sset - drop)
    fixs = set(fix)
    near = set(drop)
    for _ in range(HOPS):
        near |= {u for v in near for u in adj[v]}
    cand = sorted(near - fixs)
    if not cand:
        return None
    nbr = {v: sorted(adj[v] & (set(cand) | fixs)) for v in cand}
    budget = H - DROPK

    pool = IDPool(start_from=1)
    svar = {v: pool.id(('s', v)) for v in cand}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=[svar[v] for v in cand], bound=budget,
                             vpool=pool, encoding=EncType.seqcounter).clauses:
        outer.add_clause(cl)

    phases = [svar[v] if v in drop else -svar[v] for v in cand]

    t0, it = time.time(), 0
    while time.time() - t0 < TLIM:
        it += 1
        # Re-steer every iteration towards the region just removed: learnt
        # clauses overwrite saved phases, and without the nudge the solver
        # returns arbitrary budget-sized subsets of a few hundred candidates
        # and never stumbles on "that region minus a vertex".
        # The outer solver alone is a poor proposer here: it returns arbitrary
        # budget-sized subsets of a few hundred candidates and phase steering
        # does not survive clause learning, so it misses the cheapest trade
        # ("the same region minus the redundant vertices").  Propose that
        # directly every other iteration; the solver keeps the search complete.
        if it % 2 == 0:
            sub = sorted(rng.sample(sorted(drop), budget))
            if kissat_color(fix + sub, tag) is None:
                return sorted(fixs | set(sub))
        outer.set_phases(phases)
        if not outer.solve():
            print(f'  hole of {H}: UNSAT, no <= {budget} refill ({it} its)',
                  flush=True)
            return None
        model = set(outer.get_model())
        sel = [v for v in cand if svar[v] in model]
        if kissat_color(fix + sel, tag) is None:
            return sorted(fixs | set(sel))
        col = kissat_color(fix, tag)      # colouring of the frozen part
        if col is None:                   # frozen part alone already works
            return fix
        rest = [v for v in cand if v not in set(sel)]
        for _ in range(3):
            D = hyperedge(col, rest, nbr)
            if D:
                outer.add_clause([svar[v] for v in D])
    print(f'  hole of {H}: timeout after {it} its', flush=True)
    return None


def main():
    S = sorted(pickle.load(open(START, 'rb')))
    assert kissat_color(S, f'ld{SEED}') is None, 'start is 4-colorable'
    print(f'start {len(S)} vertices, hole {H}, budget {H-DROPK}', flush=True)
    while True:
        new = neighbourhood(S, f'ld{SEED}')
        if new and len(new) < len(S):
            assert kissat_color(new, f'ld{SEED}') is None
            S = new
            pickle.dump(S, open(OUT, 'wb'))
            print(f'*** DESCENT to {len(S)} vertices', flush=True)


if __name__ == '__main__':
    main()

"""Exact large-neighbourhood *descent* in the translated-placement universe.

Port of runs/P23-fusion1's `lnsdescend.py` / `hlns.py` to the universe of
`tuniv.py` (field coordinates rather than lattice 4-tuples), with the two
soundness fixes described below.

One neighbourhood:

    drop the H vertices of the current witness S nearest a centre (BALL=1) or
    H random ones (BALL=0);  FIX = S \\ hole;
    CAND = (HOPS-hop pool neighbourhood of the hole) \\ FIX;
    search *completely* for R subset CAND, |R| <= H - DROPK, with FIX u R
    non-4-colorable.

So each neighbourhood ends in a strictly smaller certified witness (kissat says
UNSAT on FIX u R) or in a proof that this hole admits no refill that cheap --
never in a heuristic floor.

Soundness of the outer refinement (this differs from `lnsdescend.py`, which
generated its hyperedges over CAND \\ sel only and therefore could in principle
report a spurious outer UNSAT):

* every tabu hyperedge D is a vertex cover of the conflicts of a colouring of
  FIX u CAND, i.e. FIX u (CAND \\ D) is properly 4-coloured, so *any* refill
  avoiding D is 4-colorable -- the clause "pick something in D" is valid;
* additionally, whenever FIX u sel is found 4-colorable, FIX u (any subset of
  sel) is too, so "pick something outside sel" is valid as well.

Both are implied constraints on real refills, so an outer UNSAT is a genuine
non-existence proof for the neighbourhood.

Env: POOL, START, H, HOPS, TIME, SEED, BALL, DROPK, TABU, NOISE, OUT, LOG.
"""
import os
import pickle
import random
import subprocess
import time

import numpy as np
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

import coremin
import mfield
from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'tuniv_1.6_1.3.pkl')
START = os.environ.get('START', '')
H = int(os.environ.get('H', '40'))
HOPS = int(os.environ.get('HOPS', '1'))
TLIM = float(os.environ.get('TIME', '900'))
SEED = int(os.environ.get('SEED', '1'))
BALL = int(os.environ.get('BALL', '1'))
DROPK = int(os.environ.get('DROPK', '1'))
TABU = int(os.environ.get('TABU', '200000'))
NOISE = float(os.environ.get('NOISE', '0.02'))
PERIT = int(os.environ.get('PERIT', '2'))
OUT = os.environ.get('OUT', f'tlns_{SEED}.pkl')

F = mfield.MField([3, 5, 11])
pts, E = pickle.load(open(POOL, 'rb'))
N = len(pts)
Z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
ADJ = [set() for _ in range(N)]
for u, v in E:
    ADJ[u].add(v)
    ADJ[v].add(u)
rng = random.Random(SEED)


def colorable(vs, tag):
    """None on timeout, else True/False.  Temp files are pid-specific."""
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/tl_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, '--time=1200', cnf],
                           capture_output=True, text=True)
        if 's SATISFIABLE' in r.stdout:
            return True
        if 's UNSATISFIABLE' in r.stdout:
            return False
        return None
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def coloring(vs, tag):
    """A proper 4-colouring of `vs` as {vertex: colour}, or None if UNSAT."""
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/tc_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return None
        pos = {int(x) for line in r.stdout.splitlines() if line.startswith('v ')
               for x in line[2:].split() if int(x) > 0}
        return {v: c for i, v in enumerate(vs) for c in range(4)
                if 4 * i + c + 1 in pos}
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def tabu_cover(fixed_col, movable):
    """Colour `movable` on top of the fixed colouring by min-conflicts, then
    return a vertex cover D (inside `movable`) of the surviving conflicts.
    Removing D leaves the whole set properly 4-coloured."""
    col = dict(fixed_col)
    mv = set(movable)
    for v in movable:
        col[v] = rng.randrange(4)
    cnt = {v: [0, 0, 0, 0] for v in movable}
    for v in movable:
        for u in ADJ[v]:
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
        for u in ADJ[v]:
            if u in mv:
                cnt[u][old] -= 1
                cnt[u][c] += 1
                (bad.add if cnt[u][col[u]] else bad.discard)(u)
        (bad.add if cnt[v][c] else bad.discard)(v)
    conf = [(u, v) for u, v in E if u in col and v in col and col[u] == col[v]]
    if any(u not in mv and v not in mv for u, v in conf):
        return None                      # a conflict inside the frozen part
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
    """One complete region trade.  Returns a strictly smaller witness or None."""
    Sset = set(S)
    if BALL:
        c = Z[S[rng.randrange(len(S))]]
        hole = set(sorted(S, key=lambda v: abs(Z[v] - c))[:H])
    else:
        hole = set(rng.sample(S, H))
    fix = sorted(Sset - hole)
    fixs = set(fix)
    # One solve, two answers: UNSAT means the hole was pure surplus (descend by
    # H at once), SAT gives the frozen colouring the hyperedge generator needs.
    col = coloring(fix, f'{tag}c')
    if col is None:
        return fix
    near = set(hole)
    for _ in range(HOPS):
        near |= {u for v in near for u in ADJ[v]}
    cand = sorted(near - fixs)
    budget = H - DROPK
    if not cand or budget <= 0:
        return None

    pool = IDPool(start_from=1)
    svar = {v: pool.id(('s', v)) for v in cand}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=[svar[v] for v in cand], bound=budget,
                             vpool=pool, encoding=EncType.seqcounter).clauses:
        outer.add_clause(cl)
    phases = [svar[v] if v in hole else -svar[v] for v in cand]

    t0, it, nh = time.time(), 0, 0
    while time.time() - t0 < TLIM:
        it += 1
        # The outer solver is a poor *proposer* (E25): over a few hundred
        # candidates it returns arbitrary budget-sized subsets and essentially
        # never hits "the removed region minus its redundant vertices", which is
        # the cheapest trade.  Propose that directly every other iteration; the
        # solver is kept for completeness, its UNSAT is still a real proof.
        if it % 2 == 0 and len(hole) >= budget:
            sel = sorted(rng.sample(sorted(hole), budget))
        else:
            outer.set_phases(phases)
            if not outer.solve():
                print(f'  hole {H} ({"ball" if BALL else "scattered"}): OUTER '
                      f'UNSAT after {it} its / {nh} hyperedges -- no refill of '
                      f'<= {budget} exists in this neighbourhood '
                      f'({round(time.time()-t0)}s)', flush=True)
                return None
            model = set(outer.get_model())
            sel = [v for v in cand if svar[v] in model]
        if colorable(fix + sel, f'{tag}s') is False:
            return sorted(fixs | set(sel))
        ss = set(sel)
        rest = [v for v in cand if v not in ss]
        if rest:
            outer.add_clause([svar[v] for v in rest])   # sound: see docstring
        for _ in range(PERIT):
            D = tabu_cover(col, cand)
            if D:
                outer.add_clause([svar[v] for v in D])
                nh += 1
    print(f'  hole {H}: timeout after {it} its / {nh} hyperedges', flush=True)
    return None


def main():
    S = sorted(pickle.load(open(START, 'rb'))) if START else list(range(N))
    tag = f'{SEED}'
    print(f'start {len(S)} vertices, pool {N}, hole {H}, budget {H-DROPK}, '
          f'hops {HOPS}, ball {BALL}', flush=True)
    while True:
        new = neighbourhood(S, tag)
        if new and len(new) < len(S):
            # Independent re-check of every accepted trade, done through the
            # DRAT-core path: kissat must say UNSAT *and* drat-trim must verify
            # the proof, and the core it extracts is itself a (possibly
            # strictly smaller) certified witness, so the recheck is not wasted.
            st, core = coremin.solve_core(new, seed=SEED, tag=f'tl{SEED}')
            assert st == 'UNSAT', f'descent broke the witness ({st})'
            S = sorted(core if len(core) < len(new) else new)
            pickle.dump(S, open(OUT, 'wb'))
            print(f'*** DESCENT to {len(S)} vertices'
                  f'{" (core jump)" if len(core) < len(new) else ""}',
                  flush=True)


if __name__ == '__main__':
    main()

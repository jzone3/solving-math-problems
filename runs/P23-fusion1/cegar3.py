"""Hitting-set search for a smaller half, with tabu-generated hyperedges.

Framework (Parts' minimal-graph search in modern terms): D is a hyperedge iff
pool \\ D is 4-colorable, every witness must hit every hyperedge, so the minimum
witness is a minimum hitting set.  The whole game is hyperedge quality:

    greedy colour extension    |D| ~ 850 of 2839   (useless)
    tabu / min-conflicts       |D| ~ 78            (usable)

Each iteration: the outer solver proposes a selection of <= MAXSEL free
vertices; if the induced graph (with the frozen half) is non-4-colorable we are
done -- that is a 508.  Otherwise we fix the proper colouring on frozen+selected
vertices, run min-conflicts tabu on the remaining candidates, and turn the
surviving conflicts into a hyperedge disjoint from the selection, which cuts it
off.

Env: POOL, FROZEN, FREEHALF, MAXSEL, SEED, TABU (iterations), NOISE.
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
from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'w4x.pkl')
FROZEN = os.environ.get('FROZEN', 'rec_w4x.pkl')
FREEHALF = int(os.environ.get('FREEHALF', '1'))
MAXSEL = int(os.environ.get('MAXSEL', '135'))
SEED = int(os.environ.get('SEED', '1'))
TABU = int(os.environ.get('TABU', '3000000'))
NOISE = float(os.environ.get('NOISE', '0.02'))

E, adj, PTS = coremin.E, coremin.adj, coremin.allpts
NP = len(PTS)
HALF = [0 if t == 'A' else 1 for t, _ in PTS]
rng = random.Random(SEED)

fro = set(pickle.load(open(FROZEN, 'rb')))
FIX = sorted(v for v in fro if HALF[v] != FREEHALF)
CAND = sorted(v for v in range(NP) if HALF[v] == FREEHALF)
CANDS = set(CAND)
NBR = {v: sorted(adj[v] & (CANDS | set(FIX))) for v in CAND}


def kissat_color(S):
    """Proper 4-colouring of S, or None."""
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    nvars, cls = color_cnf(len(S), E2, 4)
    cnf = f'/tmp/c3_{SEED}.cnf'
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


def hyperedge(fixed_col, movable):
    """min-conflicts colouring of `movable`; return conflicting movable ends."""
    col = dict(fixed_col)
    for v in movable:
        col[v] = rng.randrange(4)
    cnt = {v: [0, 0, 0, 0] for v in movable}
    mv = set(movable)
    for v in movable:
        for u in NBR[v]:
            if u in col:
                cnt[v][col[u]] += 1
    bad = {v for v in movable if cnt[v][col[v]]}
    best = None
    for it in range(TABU):
        if not bad:
            break
        v = rng.choice(tuple(bad))
        old = col[v]
        c = (rng.randrange(4) if rng.random() < NOISE
             else min(range(4), key=lambda k: (cnt[v][k], rng.random())))
        if c == old:
            continue
        col[v] = c
        for u in NBR[v]:
            if u in mv:
                cnt[u][old] -= 1
                cnt[u][c] += 1
                (bad.add if cnt[u][col[u]] else bad.discard)(u)
        (bad.add if cnt[v][c] else bad.discard)(v)
        if it % 200000 == 0:
            cur = sum(cnt[u][col[u]] for u in movable)
            if best is None or cur < best[0]:
                best = (cur, dict(col))
    cur = sum(cnt[u][col[u]] for u in movable)
    if best is None or cur < best[0]:
        best = (cur, dict(col))
    col = best[1]
    D = set()
    for u, v in E:
        if u in col and v in col and col[u] == col[v]:
            if u in D or v in D:
                continue
            if u in mv:
                D.add(u)
            elif v in mv:
                D.add(v)
            else:
                return None      # conflict inside the fixed part: retry
    return D


def main():
    pool = IDPool(start_from=1)
    svar = {v: pool.id(('s', v)) for v in CAND}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=[svar[v] for v in CAND], bound=MAXSEL,
                             vpool=pool, encoding=EncType.totalizer).clauses:
        outer.add_clause(cl)
    print(f'frozen {len(FIX)}, candidates {len(CAND)}, bound {MAXSEL}',
          flush=True)
    it = 0
    t0 = time.time()
    tot = 0
    while True:
        it += 1
        if not outer.solve():
            print(f'OUTER UNSAT after {it-1} hyperedges: no witness with '
                  f'<= {MAXSEL} free vertices ({round(time.time()-t0)}s)',
                  flush=True)
            return
        model = set(outer.get_model())
        sel = [v for v in CAND if svar[v] in model]
        col = kissat_color(FIX + sel)
        if col is None:
            S = sorted(set(sel) | set(FIX))
            pickle.dump(S, open(f'cegar3_hit_{SEED}.pkl', 'wb'))
            print(f'*** WITNESS {len(S)} vertices ({len(FIX)} frozen + '
                  f'{len(sel)} free)', flush=True)
            return
        movable = [v for v in CAND if v not in set(sel)]
        D = hyperedge(col, movable)
        if D is None:
            continue
        if not D:
            print('pool minus selection is 4-colorable and empty hyperedge?!',
                  flush=True)
            return
        outer.add_clause([svar[v] for v in D])
        tot += len(D)
        print(f'  it{it}: |sel|={len(sel)} hyperedge={len(D)} '
              f'(avg {tot//it}) {round(time.time()-t0)}s', flush=True)


if __name__ == '__main__':
    main()

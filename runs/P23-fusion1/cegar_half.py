"""Complete (non-heuristic) search for a SMALLER half of the record.

Everything tried so far is heuristic: greedy, LNS, swaps, column generation.
This asks a *complete* question, which is the only kind that can rule the move
out or produce a 508:

    freeze one half of the record (say L374) and ask whether ANY subset S' of
    the whole candidate pool of the other copy, with |S'| <= 135, makes
    L374 u omega S' non-4-colorable.

Method: CEGAR over selection variables s_v (v in the free half's pool) with a
cardinality bound, refined by "blocked-vertex" clauses:

    given a selection whose induced graph has a proper 4-colouring c, extend c
    greedily to the whole universe; let D be the vertices that could not be
    coloured.  Any selection avoiding D is 4-colourable, so the clause
    (OR_{v in D} s_v) is sound.  Outer UNSAT  =>  no such half exists.

Env: POOL, FROZEN (pkl of frozen indices), FREEHALF (0/1), MAXSEL, TIMEOUT.
"""
import os
import pickle
import random
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

import coremin

POOL = os.environ.get('POOL', 'w4x.pkl')
FROZEN = os.environ.get('FROZEN', 'rec_w4x.pkl')
FREEHALF = int(os.environ.get('FREEHALF', '1'))
MAXSEL = int(os.environ.get('MAXSEL', '135'))
SEED = int(os.environ.get('SEED', '1'))

E, adj, PTS = coremin.E, coremin.adj, coremin.allpts
NP = len(PTS)
HALF = [0 if t == 'A' else 1 for t, _ in PTS]
rng = random.Random(SEED)

rec = set(pickle.load(open(FROZEN, 'rb')))
FIX = sorted(v for v in rec if HALF[v] != FREEHALF)          # frozen half
CAND = sorted(v for v in range(NP) if HALF[v] == FREEHALF)   # free pool
print(f'frozen {len(FIX)} vertices, free pool {len(CAND)}, |S\'| <= {MAXSEL}',
      flush=True)


def greedy_extend(col, universe):
    """Extend partial colouring; return set of vertices that cannot be coloured."""
    D = []
    for v in universe:
        if v in col:
            continue
        used = {col[u] for u in adj[v] if u in col}
        free = [c for c in range(4) if c not in used]
        if free:
            col[v] = free[0]
        else:
            D.append(v)
    return D


def four_color(S):
    """DSATUR-ish exact-ish check via kissat; returns colouring or None."""
    from sat import color_cnf, write_cnf, KISSAT
    import subprocess
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    nvars, cls = color_cnf(len(S), E2, 4)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/ch_{SEED}_{os.getpid()}.cnf'
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


def main():
    pool = IDPool(start_from=1)
    svar = {v: pool.id(('s', v)) for v in CAND}
    solver = Cadical153()
    card = CardEnc.atmost(lits=[svar[v] for v in CAND], bound=MAXSEL,
                          vpool=pool, encoding=EncType.totalizer)
    for cl in card.clauses:
        solver.add_clause(cl)

    # WLOG min-degree 4: in a non-4-colorable graph any vertex of degree <= 3
    # can be coloured last, so it is removable.  Hence a *minimal* witness has
    # min degree >= 4, and we may demand it of every selected vertex.
    fixset = set(FIX)
    dropped = 0
    for v in CAND:
        nf = len(adj[v] & fixset)
        nb = sorted(adj[v] & set(CAND))
        if nf + len(nb) < 4:
            solver.add_clause([-svar[v]])
            dropped += 1
            continue
        need = 4 - nf
        if need <= 0:
            continue
        enc = CardEnc.atleast(lits=[svar[u] for u in nb], bound=need,
                              vpool=pool, encoding=EncType.totalizer)
        for cl in enc.clauses:
            solver.add_clause(cl + [-svar[v]])
    print(f'min-degree-4 constraints added ({dropped} candidates excluded '
          f'outright)', flush=True)
    universe = FIX + CAND
    it = 0
    t0 = time.time()
    while True:
        it += 1
        if not solver.solve():
            print(f'OUTER UNSAT after {it-1} refinements '
                  f'({round(time.time()-t0)}s): no half of size <= {MAXSEL} '
                  f'exists over this pool', flush=True)
            return
        model = set(solver.get_model())
        sel = [v for v in CAND if svar[v] in model]
        S = FIX + sel
        col = four_color(S)
        if col is None:
            pickle.dump(sorted(S), open(f'cegar_hit_{SEED}.pkl', 'wb'))
            print(f'*** NON-4-COLORABLE with {len(S)} vertices '
                  f'({len(FIX)} frozen + {len(sel)} free)', flush=True)
            return
        # try several extension orders, keep the shortest refinement clause
        Dbest = None
        for _ in range(5):
            order = list(universe)
            rng.shuffle(order)
            D = [v for v in greedy_extend(dict(col), order)
                 if HALF[v] == FREEHALF]
            if Dbest is None or len(D) < len(Dbest):
                Dbest = D
        Dfree = Dbest
        if not Dfree:
            print('refinement empty -- colouring extends to the whole pool; '
                  'no selection can work', flush=True)
            return
        solver.add_clause([svar[v] for v in Dfree])
        if it % 25 == 0:
            print(f'  it{it}: |sel|={len(sel)} |D|={len(Dfree)} '
                  f'({round(time.time()-t0)}s)', flush=True)


if __name__ == '__main__':
    main()

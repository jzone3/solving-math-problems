"""Exact region trades inside Heule's basin.

Freeze all but H vertices of the current witness, then search completely for a
replacement of at most H - 1 pool vertices drawn from the neighbourhood of the
hole: every neighbourhood ends either in a strictly smaller certified witness or
in an UNSAT proof that this hole admits no cheaper refill.  Same scheme as the
W_4 machinery (E25/E27), but in the second basin, where the current witness has
510 vertices, so two accepted trades reach 508.

Env: POOL, START, H, HOPS, TIME, SEED, BALL, OUT.
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

import mfield
from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'hpool.pkl')
START = os.environ.get('START', '')
H = int(os.environ.get('H', '30'))
HOPS = int(os.environ.get('HOPS', '1'))
TLIM = float(os.environ.get('TIME', '600'))
SEED = int(os.environ.get('SEED', '1'))
BALL = int(os.environ.get('BALL', '1'))
OUT = os.environ.get('OUT', f'hlns_{SEED}.pkl')

F = mfield.MField([3, 5, 11])
pts, E = pickle.load(open(POOL, 'rb'))
N = len(pts)
Z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
NBR = {v: set() for v in range(N)}
for u, v in E:
    NBR[u].add(v)
    NBR[v].add(u)
rng = random.Random(SEED)
S = sorted(pickle.load(open(START, 'rb'))) if START else list(range(510))


def colorable(vs, tag):
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/hl_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, '--time=600', cnf],
                           capture_output=True, text=True)
        if 's SATISFIABLE' in r.stdout:
            return True
        if 's UNSATISFIABLE' in r.stdout:
            return False
        return None
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def neighbourhood(hole):
    cand = set(hole)
    for _ in range(HOPS):
        grow = set()
        for v in cand:
            grow |= NBR[v]
        cand |= grow
    return sorted(cand)


def trade(S, tag):
    Sset = set(S)
    if BALL:
        c = Z[S[rng.randrange(len(S))]]
        hole = set(sorted(S, key=lambda v: abs(Z[v] - c))[:H])
    else:
        hole = set(rng.sample(S, H))
    fix = sorted(Sset - hole)
    if colorable(fix, f'{tag}_f') is False:
        return sorted(fix)                      # hole was pure surplus
    cand = [v for v in neighbourhood(hole) if v not in Sset - hole]
    budget = H - 1
    pool = IDPool()
    svar = {v: pool.id(('s', v)) for v in cand}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=list(svar.values()), bound=budget,
                             vpool=pool, encoding=EncType.seqcounter).clauses:
        outer.add_clause(cl)
    t0 = time.time()
    it = 0
    while time.time() - t0 < TLIM:
        it += 1
        if it % 2 == 0 and len(hole & set(cand)) >= budget:
            sub = rng.sample(sorted(hole & set(cand)), budget)
        else:
            if not outer.solve():
                print(f'  hole {H}: OUTER UNSAT after {it} its '
                      f'({round(time.time()-t0)}s)', flush=True)
                return None
            model = set(outer.get_model())
            sub = [v for v in cand if svar[v] in model]
        if colorable(fix + sub, f'{tag}_{it}') is False:
            return sorted(set(fix) | set(sub))
        # fix + sub is 4-colorable, hence so is fix + any subset of sub: force
        # at least one candidate from outside sub (an empty clause here would
        # be a spurious UNSAT, which is what an earlier version produced).
        ss = set(sub)
        outer.add_clause([svar[v] for v in cand if v not in ss])
    print(f'  hole {H}: timeout after {it} its', flush=True)
    return None


def main():
    cur = list(S)
    print(f'start {len(cur)} vertices, pool {N}, hole {H}', flush=True)
    if colorable(cur, 'start') is not False:
        print('START IS 4-COLORABLE -- aborting', flush=True)
        return
    while True:
        new = trade(cur, f'{SEED}')
        if new and len(new) < len(cur):
            cur = sorted(new)
            pickle.dump(cur, open(OUT, 'wb'))
            print(f'*** DESCENT to {len(cur)}', flush=True)
            if colorable(cur, 'chk') is not False:
                print('!!! descent produced a 4-colorable set', flush=True)
                return


if __name__ == '__main__':
    main()

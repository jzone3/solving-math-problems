"""Cheaper completions of the shared core of the two record graphs.

Parts' 509 and Heule's 510 share **466** vertices; Parts completes that core with
43 further points, Heule with 44.  So the record is one particular completion of
a common core, and the natural question nobody has asked is whether the core
admits a *cheaper* completion: is there X with |X| <= 42 in the surrounding
lattice such that core u X is non-4-colorable?  Any such X is a <= 508-vertex
5-chromatic unit-distance graph.

CEGAR over the completion only: propose X with |X| <= BUD, ask kissat for a
4-colouring of core u X, and on success extend the colouring greedily to a
maximal 4-colorable set T and add the clause "pick a candidate outside T"
(sound: 4-colorability is monotone under subsets).  Terminates either with a
witness or with a proof that no completion of this size exists in the pool.

Env: BUD, POOL, SEED, DROP (allow removing DROP core vertices), OUT.
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

BUD = int(os.environ.get('BUD', '42'))
POOL = os.environ.get('POOL', 'upool.pkl')
SEED = int(os.environ.get('SEED', '1'))
RESTRICT = os.environ.get('RESTRICT', '')
OUT = os.environ.get('OUT', f'core_{BUD}_{SEED}.pkl')

F = mfield.MField([3, 5, 11])
pts, E = pickle.load(open(POOL, 'rb'))
core = pickle.load(open('ucore.pkl', 'rb'))
N = len(pts)
coreset = set(core)
cand = [v for v in range(N) if v not in coreset]
if RESTRICT == 'union':
    # only the two record graphs' own completion vertices (43 + 44): small
    # enough that the CEGAR search can actually be run to completion
    keep = set(pickle.load(open('uparts.pkl', 'rb')))
    keep |= set(pickle.load(open('uheule.pkl', 'rb')))
    cand = [v for v in cand if v in keep]
NBR = {v: set() for v in range(N)}
for u, v in E:
    NBR[u].add(v)
    NBR[v].add(u)
print(f'pool {N}, core {len(core)}, candidates {len(cand)}, budget {BUD}',
      flush=True)
rng = random.Random(SEED)


def colour(vs, tag):
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/cc_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return None
        model = set()
        for line in r.stdout.splitlines():
            if line.startswith('v '):
                model |= {int(t) for t in line[2:].split() if int(t) > 0}
        col = {}
        for x, i in rm.items():
            for c in range(4):
                if 4 * i + c + 1 in model:
                    col[x] = c
                    break
        return col
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def extend(col):
    col = dict(col)
    order = sorted(set(range(N)) - set(col), key=lambda v: -len(NBR[v]))
    changed = True
    while changed:
        changed = False
        for v in order:
            if v in col:
                continue
            free = [c for c in range(4)
                    if c not in {col[u] for u in NBR[v] if u in col}]
            if free:
                col[v] = free[rng.randrange(len(free))]
                changed = True
    return set(col)


def main():
    pool = IDPool()
    x = {v: pool.id(('x', v)) for v in cand}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=list(x.values()), bound=BUD, vpool=pool,
                             encoding=EncType.seqcounter).clauses:
        outer.add_clause(cl)
    t0 = time.time()
    it = 0
    best = None
    while True:
        it += 1
        if not outer.solve():
            print(f'OUTER UNSAT after {it} its ({round(time.time()-t0)}s): '
                  f'the shared core has no completion of <= {BUD} pool '
                  f'vertices', flush=True)
            return
        model = set(outer.get_model())
        X = [v for v in cand if x[v] in model]
        S = core + X
        col = colour(S, f'{SEED}_{it}')
        if col is None:
            pickle.dump(sorted(S), open(OUT, 'wb'))
            print(f'*** WITNESS core+{len(X)} = {len(S)} vertices -> {OUT}',
                  flush=True)
            return
        T = extend(col)
        outside = [x[v] for v in cand if v not in T]
        if not outside:
            print('whole pool 4-colorable under this extension', flush=True)
            return
        outer.add_clause(outside)
        if best is None or len(outside) < best:
            best = len(outside)
        if it % 25 == 0:
            print(f'  it{it}: |X|={len(X)} clause {len(outside)} '
                  f'(best {best}, {round(time.time()-t0)}s)', flush=True)


if __name__ == '__main__':
    main()

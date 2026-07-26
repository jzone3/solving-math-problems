"""Implicit hitting set for the completion problem (optimal outer solver).

Same problem as corecomplete.py -- find X in the candidate set with core u X
non-4-colorable -- but the outer problem is solved to *optimality* with RC2
MaxSAT instead of asking a CDCL solver for an arbitrary model under a
cardinality bound.  Every iteration therefore reports the true minimum hitting
set of the clauses collected so far, which is a lower bound on the size of any
completion; as soon as that lower bound exceeds BUD the answer is UNSAT, with no
need to enumerate.  (The CDCL version spent over an hour inside a single outer
solve; the bound here is what makes the run terminate.)

Env: BUD, POOL, RESTRICT, SEED, BANK, OUT.
"""
import json
import os
import pickle
import random
import subprocess
import time

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

import mfield
from sat import color_cnf, write_cnf, KISSAT

BUD = int(os.environ.get('BUD', '42'))
POOL = os.environ.get('POOL', 'upool.pkl')
RESTRICT = os.environ.get('RESTRICT', 'union')
SEED = int(os.environ.get('SEED', '1'))
BANK = os.environ.get('BANK', f'hsbank_{RESTRICT}.jsonl')
OUT = os.environ.get('OUT', f'hs_{BUD}_{SEED}.pkl')

F = mfield.MField([3, 5, 11])
pts, E = pickle.load(open(POOL, 'rb'))
core = pickle.load(open('ucore.pkl', 'rb'))
N = len(pts)
coreset = set(core)
NBR = {v: set() for v in range(N)}
for a, b in E:
    NBR[a].add(b)
    NBR[b].add(a)
keep = set(pickle.load(open('uparts.pkl', 'rb')))
keep |= set(pickle.load(open('uheule.pkl', 'rb')))
keep -= coreset
if RESTRICT == 'near':
    grow = set(keep)
    for v in keep:
        grow |= NBR[v]
    keep = grow - coreset
cand = sorted(keep)
idx = {v: i for i, v in enumerate(cand)}
print(f'pool {N}, core {len(core)}, candidates {len(cand)}, budget {BUD}',
      flush=True)
rng = random.Random(SEED)


def colour(vs, tag):
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/hs_{tag}_{os.getpid()}.cnf'
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
    clauses = []
    if os.path.exists(BANK):
        for line in open(BANK):
            cl = json.loads(line)
            if cl:
                clauses.append(cl)
        print(f'{len(clauses)} clauses preloaded from {BANK}', flush=True)
    bank = open(BANK, 'a')
    t0 = time.time()
    it = 0
    while True:
        it += 1
        wc = WCNF()
        for cl in clauses:
            wc.append([idx[v] + 1 for v in cl])
        for i in range(len(cand)):
            wc.append([-(i + 1)], weight=1)
        with RC2(wc) as rc2:
            model = rc2.compute()
            lb = sum(1 for lit in model if lit > 0)
        X = [cand[i] for i in range(len(cand)) if model[i] > 0]
        if lb > BUD:
            print(f'OUTER UNSAT: minimum completion needs >= {lb} candidates '
                  f'> {BUD} ({it} its, {round(time.time()-t0)}s)', flush=True)
            return
        col = colour(core + X, f'{SEED}_{it}')
        if col is None:
            pickle.dump(sorted(core + X), open(OUT, 'wb'))
            print(f'*** WITNESS core+{len(X)} = {len(core)+len(X)} -> {OUT}',
                  flush=True)
            return
        T = extend(col)
        cl = [v for v in cand if v not in T]
        if not cl:
            print('pool 4-colorable under this extension', flush=True)
            return
        clauses.append(cl)
        bank.write(json.dumps(cl) + '\n')
        bank.flush()
        if it % 25 == 0:
            print(f'  it{it}: lower bound {lb}, clause {len(cl)} '
                  f'({round(time.time()-t0)}s)', flush=True)


if __name__ == '__main__':
    main()

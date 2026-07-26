"""Implicit hitting set over a whole universe: search and lower bound at once.

For a pool P, a set D is a *hyperedge* if P \\ D is 4-colorable; every
non-4-colorable subset must hit every hyperedge.  Each iteration solves the
minimum hitting set of the clauses collected so far (set-cover ILP, HiGHS), so

* the proposal is always a **minimum-size** candidate -- if the universe holds a
  witness smaller than 509, this is the formulation that walks into it, unlike
  deletion-style minimisation which is ~3.5x off optimum (E13);
* the optimum value is a monotone lower bound on the size of *any* witness in
  the universe.

Env: POOL, BUD, SEED, BANK, OUT.
"""
import json
import os
import pickle
import random
import subprocess
import time

import numpy as np
from scipy.optimize import LinearConstraint, milp

from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'tasym_1.6_1.3.pkl')
BUD = int(os.environ.get('BUD', '508'))
SEED = int(os.environ.get('SEED', '1'))
BANK = os.environ.get('BANK', 'hsfull_' + os.path.basename(POOL) + '.jsonl')
OUT = os.environ.get('OUT', f'hsfull_{SEED}.pkl')

pts, E = pickle.load(open(POOL, 'rb'))
N = len(pts)
NBR = {v: set() for v in range(N)}
for a, b in E:
    NBR[a].add(b)
    NBR[b].add(a)
print(f'pool {N} vertices, {len(E)} edges, budget {BUD}', flush=True)
rng = random.Random(SEED)


def colour(vs, tag):
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/hf_{tag}_{os.getpid()}.cnf'
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
        print(f'{len(clauses)} clauses preloaded', flush=True)
    seen = {frozenset(c) for c in clauses}
    bank = open(BANK, 'a')
    reader = open(BANK, 'r')
    reader.seek(0, 2)
    t0 = time.time()
    it = 0
    while True:
        it += 1
        for line in reader:
            o = json.loads(line)
            k = frozenset(o)
            if o and k not in seen:
                seen.add(k)
                clauses.append(o)
        if clauses:
            A = np.zeros((len(clauses), N))
            for r, cl in enumerate(clauses):
                A[r, cl] = 1.0
            cons = [LinearConstraint(A, lb=1, ub=np.inf)]
        else:
            cons = []
        obj = 1.0 + np.array([rng.random() for _ in range(N)]) / (10.0 * N)
        res = milp(c=obj, constraints=cons, integrality=np.ones(N),
                   bounds=(0, 1))
        sol = np.round(res.x).astype(int)
        S = [v for v in range(N) if sol[v]]
        lb = len(S)
        if lb > BUD:
            print(f'OUTER UNSAT: every witness in this universe needs >= {lb} '
                  f'vertices > {BUD}', flush=True)
            return
        col = colour(S, f'{SEED}_{it}') if S else {}
        if S and col is None:
            pickle.dump(sorted(S), open(OUT, 'wb'))
            print(f'*** WITNESS {len(S)} vertices -> {OUT}', flush=True)
            return
        T = max((extend(col) for _ in range(8)), key=len) if col else set()
        cl = [v for v in range(N) if v not in T]
        if not cl:
            print('universe 4-colorable?!', flush=True)
            return
        clauses.append(cl)
        seen.add(frozenset(cl))
        bank.write(json.dumps(cl) + '\n')
        bank.flush()
        if it % 10 == 0:
            print(f'  it{it}: lower bound {lb}, clause {len(cl)} '
                  f'({round(time.time()-t0)}s)', flush=True)


if __name__ == '__main__':
    main()

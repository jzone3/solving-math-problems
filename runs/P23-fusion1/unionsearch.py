"""Complete search for a <= B-vertex witness inside the union of the two record
graphs.

Parts' 509 and Heule's 510 share 466 vertices -- their union is only 553 points.
That is small enough for a *complete* CEGAR search: pick <= B vertices, ask
kissat for a 4-colouring, and when one exists extend it greedily to a maximal
4-colorable superset T and block with "select something outside T" (sound
because 4-colorability is monotone under taking subsets).

Outcome is decisive either way: a witness of <= B vertices, or a proof that the
union of the two best known graphs contains none.

Env: B (bound), SEED, OUT.
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

B = int(os.environ.get('B', '508'))
SEED = int(os.environ.get('SEED', '1'))
OUT = os.environ.get('OUT', f'union_{B}_{SEED}.pkl')

F = mfield.MField([3, 5, 11])
h = mfield.load_vtx(F, '/home/ubuntu/p23heule/vtx/510.vtx')
p = mfield.load_vtx(F, '/home/ubuntu/solving-math-problems/solutions/P23/'
                       'v509e2442.vtx')
pts = sorted(set(h) | set(p), key=lambda q: (F.to_float(q[0]),
                                             F.to_float(q[1])))
N = len(pts)
z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
E = []
for i in range(N):
    d = np.abs(z[i + 1:] - z[i])
    for k in np.nonzero(np.abs(d - 1.0) < 1e-7)[0]:
        j = i + 1 + int(k)
        dx = F.sub(pts[i][0], pts[j][0])
        dy = F.sub(pts[i][1], pts[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E.append((i, j))
print(f'union: {N} vertices, {len(E)} exact edges, bound {B}', flush=True)
NBR = {v: set() for v in range(N)}
for u, v in E:
    NBR[u].add(v)
    NBR[v].add(u)
rng = random.Random(SEED)


def colour(vs, tag):
    """Return a proper 4-colouring of vs, or None if there is none."""
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/us_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return None
        model = set()
        for line in r.stdout.splitlines():
            if line.startswith('v '):
                model |= {int(x) for x in line[2:].split() if int(x) > 0}
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
    """Greedily grow a 4-colouring to a maximal 4-colorable vertex set."""
    col = dict(col)
    order = sorted(set(range(N)) - set(col), key=lambda v: len(NBR[v]))
    changed = True
    while changed:
        changed = False
        for v in order:
            if v in col:
                continue
            used = {col[u] for u in NBR[v] if u in col}
            free = [c for c in range(4) if c not in used]
            if free:
                col[v] = free[0]
                changed = True
    return set(col)


def main():
    pool = IDPool()
    x = {v: pool.id(('x', v)) for v in range(N)}
    outer = Cadical153()
    for cl in CardEnc.atmost(lits=list(x.values()), bound=B, vpool=pool,
                             encoding=EncType.seqcounter).clauses:
        outer.add_clause(cl)
    t0 = time.time()
    it = 0
    while True:
        it += 1
        if not outer.solve():
            print(f'OUTER UNSAT after {it} iterations '
                  f'({round(time.time()-t0)}s): the union of Parts 509 and '
                  f'Heule 510 has no non-4-colorable subset of <= {B} '
                  f'vertices', flush=True)
            return
        model = set(outer.get_model())
        S = [v for v in range(N) if x[v] in model]
        col = colour(S, f'{SEED}_{it}')
        if col is None:
            pickle.dump(sorted(S), open(OUT, 'wb'))
            print(f'*** WITNESS {len(S)} vertices (saved {OUT})', flush=True)
            return
        T = extend(col)
        outside = [x[v] for v in range(N) if v not in T]
        outer.add_clause(outside)
        if it % 20 == 0:
            print(f'  it{it}: |S|={len(S)} maximal colorable {len(T)}, '
                  f'clause {len(outside)} ({round(time.time()-t0)}s)',
                  flush=True)


if __name__ == '__main__':
    main()

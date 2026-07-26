"""Minimise a partner half for Parts' fixed lattice half, in each placement.

Parts' record is L374 u rho*S136: a 374-point lattice half plus a 135-point
rotated partner (509 = 374 + 135).  His partner lives in the origin-centred copy.
This asks the same question in the *translated* copies found by E43: keep his
lattice half, and greedily minimise a partner drawn from one translated copy.
A partner of fewer than 135 points would be a sub-509 graph.

Control: the origin-centred copy must reproduce a partner of about 135.

Env: POOL, COPY (wA / T63 / T65), SEED, OUT.
"""
import os
import pickle
import random
import subprocess
from collections import Counter

import findrot as R
import mfield
from sat import color_cnf, write_cnf, KISSAT

F = R.F
POOL = os.environ.get('POOL', 'tradepool.pkl')
COPY = os.environ.get('COPY', 'wA')
SEED = int(os.environ.get('SEED', '1'))
OUT = os.environ.get('OUT', f'partner_{COPY}_{SEED}.pkl')

pts, E = pickle.load(open(POOL, 'rb'))
idx = {p: i for i, p in enumerate(pts)}
rec = mfield.load_vtx(
    F, '/home/ubuntu/solving-math-problems/solutions/P23/v509e2442.vtx')
FIX = sorted(idx[p] for p in rec if R.in_lattice(p))

ZERO = (R.elt({}), R.elt({}))
T = {'wA': ZERO,
     'T63': pickle.load(open('tscan.pkl', 'rb'))[0][1],
     'T65': pickle.load(open('tscan2.pkl', 'rb'))[0][1]}[COPY]
W = R.ROTS['w[15]']


def in_copy(p):
    q = (F.sub(p[0], T[0]), F.sub(p[1], T[1]))
    return R.in_lattice(R.cmul(q, R.conj(W)))


CAND = sorted(i for i, p in enumerate(pts)
              if not R.in_lattice(p) and in_copy(p))
print(f'fix {len(FIX)} lattice points, copy {COPY}: {len(CAND)} candidates',
      flush=True)
rng = random.Random(SEED)


def colorable(vs, tag):
    vs = sorted(vs)
    rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nv, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/pt_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nv, cls)
    try:
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        return 's UNSATISFIABLE' not in r.stdout
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def main():
    S = list(CAND)
    if colorable(set(FIX) | set(S), 'init'):
        print(f'{COPY}: fix + whole copy is 4-colorable -- no partner here',
              flush=True)
        return
    print(f'{COPY}: fix + copy is NON-4-colorable, minimising partner',
          flush=True)
    changed = True
    while changed:
        changed = False
        order = list(S)
        rng.shuffle(order)
        stack = [order[k:k + 8] for k in range(0, len(order), 8)]
        while stack:
            g = [v for v in stack.pop() if v in S]
            if not g:
                continue
            trial = [v for v in S if v not in set(g)]
            if not colorable(set(FIX) | set(trial), f'{SEED}'):
                S = trial
                changed = True
                print(f'  partner {len(S)} (total {len(FIX)+len(S)})',
                      flush=True)
                pickle.dump(sorted(set(FIX) | set(S)), open(OUT, 'wb'))
            elif len(g) > 1:
                h = len(g) // 2
                stack.append(g[:h])
                stack.append(g[h:])
    print(f'{COPY}: FINAL partner {len(S)}, total {len(FIX)+len(S)}',
          flush=True)


if __name__ == '__main__':
    main()

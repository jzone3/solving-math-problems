"""How small can the translated universes be and still fail to 4-colour?

In Parts' placement the obstruction switches on sharply between radius 1.95 and
2.0 (E34). If a translated placement obstructs at a *smaller* radius its whole
universe is smaller, which is where a smaller witness would have to live.

Env: IN (tscan pickle), IDX, RADII, TIME.
"""
import os
import pickle
import subprocess
from fractions import Fraction as Fr

import numpy as np

import findrot as R
from sat import color_cnf, write_cnf, KISSAT

F = R.F
W = R.ROTS['w[15]']
TLIM = os.environ.get('TIME', '600')
RADII = [float(x) for x in os.environ.get('RADII', '1.5,1.6,1.7,1.8,1.9').split(',')]

w4pts, _ = pickle.load(open('/home/ubuntu/p23w4/w4d.pkl', 'rb'))
ALL = [v for tag, v in w4pts if tag == 'A']


def to_field(p):
    a, b, c, d = p
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


def build(T, rad):
    lim = rad + 1e-9
    base = []
    for v in ALL:
        x = (v[0] + v[1] * 33 ** 0.5) / 12
        y = (v[2] * 3 ** 0.5 + v[3] * 11 ** 0.5) / 12
        if x * x + y * y <= lim * lim:
            base.append(to_field(v))
    pts = list(base)
    for q in base:
        r = R.cmul(q, W)
        pts.append((F.add(r[0], T[0]), F.add(r[1], T[1])))
    pts = sorted(set(pts), key=lambda q: F.to_float(q[0]))
    z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
    E = []
    for i in range(len(pts)):
        for k in np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]:
            j = i + 1 + int(k)
            dx = F.sub(pts[i][0], pts[j][0])
            dy = F.sub(pts[i][1], pts[j][1])
            if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
                E.append((i, j))
    return pts, E


def decide(pts, E):
    nv, cls = color_cnf(len(pts), E, 4)
    cnf = f'/tmp/tr_{os.getpid()}.cnf'
    write_cnf(cnf, nv, cls)
    r = subprocess.run([KISSAT, f'--time={TLIM}', cnf],
                       capture_output=True, text=True)
    os.unlink(cnf)
    return ('UNSAT' if 's UNSATISFIABLE' in r.stdout else
            'SAT' if 's SATISFIABLE' in r.stdout else 'timeout')


if __name__ == '__main__':
    ZERO = (R.elt({}), R.elt({}))
    cands = [('T=0', ZERO)]
    for f in ('tscan.pkl', 'tscan2.pkl'):
        if os.path.exists(f):
            n, T = pickle.load(open(f, 'rb'))[0]
            cands.append((f'score{n}', T))
    for lbl, T in cands:
        for rad in RADII:
            pts, E = build(T, rad)
            st = decide(pts, E)
            print(f'{lbl} r={rad}: {len(pts)} vtx, {len(E)} edges -> {st}',
                  flush=True)
            if st == 'UNSAT':
                pickle.dump((pts, E), open(f'tuniv_{lbl}_{rad}.pkl', 'wb'))
                break

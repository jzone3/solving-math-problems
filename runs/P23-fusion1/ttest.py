"""Test the best translations from `tscan.py`: is A u (T + omega A) 5-chromatic?

For each candidate translation the universe is rebuilt exactly at the requested
radius, all unit edges are recomputed exactly, and kissat decides 4-colorability.
Parts' own universe (T = 0) is included as the control.

Env: RAD, TOP, TIME, IN.
"""
import os
import pickle
import subprocess
from fractions import Fraction as Fr

import numpy as np

import findrot as R
from sat import color_cnf, write_cnf, KISSAT

F = R.F
RAD = float(os.environ.get('RAD', '2.0'))
TOP = int(os.environ.get('TOP', '5'))
TLIM = os.environ.get('TIME', '900')
IN = os.environ.get('IN', 'tscan.pkl')
W = R.ROTS['w[15]']

w4pts, _ = pickle.load(open('/home/ubuntu/p23w4/w4d.pkl', 'rb'))
lim = RAD + 1e-9
base = []
for tag, v in w4pts:
    if tag != 'A':
        continue
    x = (v[0] + v[1] * 33 ** 0.5) / 12
    y = (v[2] * 3 ** 0.5 + v[3] * 11 ** 0.5) / 12
    if x * x + y * y <= lim * lim:
        base.append(v)


def to_field(p):
    a, b, c, d = p
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


A = [to_field(p) for p in base]
B0 = [R.cmul(p, W) for p in A]
print(f'{len(A)} base points at radius {RAD}', flush=True)


def build(T):
    pts = list(A)
    for q in B0:
        pts.append((F.add(q[0], T[0]), F.add(q[1], T[1])))
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


ZERO = (R.elt({}), R.elt({}))
cands = [(0, ZERO)] + pickle.load(open(IN, 'rb'))[:TOP]
for n, T in cands:
    pts, E = build(T)
    nv, cls = color_cnf(len(pts), E, 4)
    cnf = f'/tmp/tt_{os.getpid()}.cnf'
    write_cnf(cnf, nv, cls)
    r = subprocess.run([KISSAT, f'--time={TLIM}', cnf],
                       capture_output=True, text=True)
    st = ('UNSAT' if 's UNSATISFIABLE' in r.stdout else
          'SAT' if 's SATISFIABLE' in r.stdout else 'timeout')
    print(f'T sample-score {n}: {len(pts)} vtx, {len(E)} exact edges -> {st}',
          flush=True)
    if st == 'UNSAT':
        pickle.dump((pts, E), open(f'tuniv_{n}.pkl', 'wb'))
    os.unlink(cnf)

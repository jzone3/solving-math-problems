"""Asymmetric radii: the two halves need not be equally large.

Every universe in this run (and in Parts') uses one radius for both halves.
With the score-65 translation the obstruction already appears at radius 1.6;
this checks how far each half can be shrunk independently, which is the cheapest
way to cut the universe further before minimising.

Env: TIME, PAIRS.
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
PAIRS = os.environ.get('PAIRS', '1.6:1.4,1.4:1.6,1.6:1.2,1.2:1.6,1.5:1.5,'
                                '1.6:1.0,1.0:1.6,1.5:1.3,1.3:1.5')

w4pts, _ = pickle.load(open('/home/ubuntu/p23w4/w4d.pkl', 'rb'))
ALL = [v for tag, v in w4pts if tag == 'A']
n65, T65 = pickle.load(open('tscan2.pkl', 'rb'))[0]


def disk(rad):
    lim = rad + 1e-9
    out = []
    for v in ALL:
        x = (v[0] + v[1] * 33 ** 0.5) / 12
        y = (v[2] * 3 ** 0.5 + v[3] * 11 ** 0.5) / 12
        if x * x + y * y <= lim * lim:
            out.append((R.elt({0: Fr(v[0], 12), 5: Fr(v[1], 12)}),
                        R.elt({1: Fr(v[2], 12), 4: Fr(v[3], 12)})))
    return out


def build(ra, rb, T):
    pts = list(disk(ra))
    for q in disk(rb):
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


if __name__ == '__main__':
    for spec in PAIRS.split(','):
        ra, rb = (float(x) for x in spec.split(':'))
        pts, E = build(ra, rb, T65)
        nv, cls = color_cnf(len(pts), E, 4)
        cnf = f'/tmp/ta_{os.getpid()}.cnf'
        write_cnf(cnf, nv, cls)
        r = subprocess.run([KISSAT, f'--time={TLIM}', cnf],
                           capture_output=True, text=True)
        os.unlink(cnf)
        st = ('UNSAT' if 's UNSATISFIABLE' in r.stdout else
              'SAT' if 's SATISFIABLE' in r.stdout else 'timeout')
        print(f'rA={ra} rB={rb}: {len(pts)} vtx, {len(E)} edges -> {st}',
              flush=True)
        if st == 'UNSAT':
            pickle.dump((pts, E), open(f'tasym_{ra}_{rb}.pkl', 'wb'))

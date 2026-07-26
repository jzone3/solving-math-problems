"""Multi-copy universes: several placements of the rotated copy at once.

Two translated copies of the same rotation can be strongly coupled to each other
(the tpool census showed 1022 unit pairs between T + omega A and -T + omega A
where A itself has only 96 to omega A), so a universe using several placements
may obstruct at a much smaller radius than any two-copy universe.

Env: SPEC (comma-separated copy labels), RADII, TIME.
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
RADII = [float(x) for x in os.environ.get('RADII', '1.0,1.1,1.2,1.3,1.4').split(',')]
SPEC = os.environ.get('SPEC', 'id,w,wT63,wT65').split(',')

w4pts, _ = pickle.load(open('/home/ubuntu/p23w4/w4d.pkl', 'rb'))
ALL = [v for tag, v in w4pts if tag == 'A']
ZERO = (R.elt({}), R.elt({}))
T63 = pickle.load(open('tscan.pkl', 'rb'))[0][1]
T65 = pickle.load(open('tscan2.pkl', 'rb'))[0][1]
ZM = R.elt({})
NEG63 = (F.sub(ZM, T63[0]), F.sub(ZM, T63[1]))
NEG65 = (F.sub(ZM, T65[0]), F.sub(ZM, T65[1]))
COPY = {'id': (None, ZERO), 'w': (W, ZERO), 'wT63': (W, T63),
        'wT65': (W, T65), 'wN63': (W, NEG63), 'wN65': (W, NEG65)}


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


def build(rad, spec):
    base = disk(rad)
    pts = set()
    for lbl in spec:
        rot, T = COPY[lbl]
        for q in base:
            r = R.cmul(q, rot) if rot else q
            pts.add((F.add(r[0], T[0]), F.add(r[1], T[1])))
    pts = sorted(pts, key=lambda q: F.to_float(q[0]))
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
    for rad in RADII:
        pts, E = build(rad, SPEC)
        nv, cls = color_cnf(len(pts), E, 4)
        cnf = f'/tmp/mc_{os.getpid()}.cnf'
        write_cnf(cnf, nv, cls)
        r = subprocess.run([KISSAT, f'--time={TLIM}', cnf],
                           capture_output=True, text=True)
        os.unlink(cnf)
        st = ('UNSAT' if 's UNSATISFIABLE' in r.stdout else
              'SAT' if 's SATISFIABLE' in r.stdout else 'timeout')
        print(f'{"+".join(SPEC)} r={rad}: {len(pts)} vtx, {len(E)} edges '
              f'-> {st}', flush=True)
        if st == 'UNSAT':
            pickle.dump((pts, E),
                        open(f'mc_{"_".join(SPEC)}_{rad}.pkl', 'wb'))
            break

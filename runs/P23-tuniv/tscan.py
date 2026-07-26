"""Translation scan: how strongly can a rotated copy be coupled to the base?

Parts pins the rotation centre at the origin, so his universe is A u omega*A and
the coupling between the halves is whatever that choice happens to give (96 unit
pairs at radius 2).  de Grey's earlier graphs (803/826/874, see `tshift.py`) use
a *translated* rotated copy T + omega*A, so the translation is a real degree of
freedom -- and coupling strength is what forces 5-chromaticity, so a T with many
more cross pairs is a plausible place for a smaller witness.

Candidate translations are exactly those that produce at least one cross edge:
T = p - q - u for p in A, q in omega*A and u a unit vector of the field.  This
scans a random sample of them and counts cross pairs numerically (floats are a
prefilter only; the winners are re-checked exactly by the pool builder).

Env: RAD, NSHIFT, OUT.
"""
import os
import pickle
import random
from collections import Counter
from fractions import Fraction as Fr

import numpy as np
from scipy.spatial import cKDTree

import findrot as R
from poolio import load_all

F = R.F
RAD = float(os.environ.get('RAD', '1.6'))
NSHIFT = int(os.environ.get('NSHIFT', '4000'))
OUT = os.environ.get('OUT', 'tscan.pkl')
W = R.ROTS['w[15]']

lim = RAD + 1e-9
base = []
for v in load_all():
    x = (v[0] + v[1] * 33 ** 0.5) / 12
    y = (v[2] * 3 ** 0.5 + v[3] * 11 ** 0.5) / 12
    if x * x + y * y <= lim * lim:
        base.append(v)


def to_field(p):
    a, b, c, d = p
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


A = [to_field(p) for p in base]
B = [R.cmul(p, W) for p in A]
za = np.array([[F.to_float(x), F.to_float(y)] for x, y in A])
zb = np.array([[F.to_float(x), F.to_float(y)] for x, y in B])
print(f'{len(A)} base points at radius {RAD}', flush=True)

# unit vectors of the base lattice: the neighbours of the origin
ta = cKDTree(za)
origin = int(np.argmin(np.linalg.norm(za, axis=1)))
units = [A[j] for j in ta.query_ball_point(za[origin], 1.0 + 1e-9)
         if abs(np.linalg.norm(za[j] - za[origin]) - 1.0) < 1e-9]
print(f'{len(units)} unit vectors', flush=True)

rng = random.Random(1)
tb = cKDTree(zb)


def cross_count(t):
    shifted = zb + np.array(t)
    return sum(len(x) for x in cKDTree(shifted).query_ball_tree(ta, 1.0 + 1e-9,
                                                                p=2)) - \
        sum(len(x) for x in cKDTree(shifted).query_ball_tree(ta, 1.0 - 1e-9,
                                                             p=2))


def cross_pairs(t):
    """Exact-count-free numeric count of unit pairs between A and t + omega A."""
    shifted = zb + np.array(t)
    ts = cKDTree(shifted)
    inner = ts.count_neighbors(ta, 1.0 - 1e-9)
    outer = ts.count_neighbors(ta, 1.0 + 1e-9)
    return int(outer - inner)


def main():
    seen = {}
    best = []
    for _ in range(NSHIFT):
        p = A[rng.randrange(len(A))]
        q = B[rng.randrange(len(B))]
        u = units[rng.randrange(len(units))]
        T = (F.sub(F.sub(p[0], q[0]), u[0]), F.sub(F.sub(p[1], q[1]), u[1]))
        key = (F.to_float(T[0]), F.to_float(T[1]))
        rk = (round(key[0], 9), round(key[1], 9))
        if rk in seen:
            continue
        n = cross_pairs(key)
        seen[rk] = n
        best.append((n, T))
    best.sort(key=lambda x: -x[0])
    zero = cross_pairs((0.0, 0.0))
    print(f'T = 0 (Parts): {zero} cross pairs', flush=True)
    print('best translations:', [n for n, _ in best[:10]], flush=True)
    print('distribution:', Counter(n for n, _ in best).most_common(8),
          flush=True)
    pickle.dump([(n, T) for n, T in best[:50]], open(OUT, 'wb'))


if __name__ == '__main__':
    main()

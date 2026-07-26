"""Rebuild the translated-placement universe A u (T + omega*A), exactly.

The universe this run works in is the one E43-E45 of runs/P23-fusion1 found:
Parts' Minkowski base A in the lattice (a + b sqrt33 + i(c sqrt3 + d sqrt11))/12,
omega = w[15] = (7 + i sqrt15)/8 as the rotation, but the rotated copy is
*translated* by T before being unioned with A.  The score-65 translation
decomposes exactly over the lattice (NOTES E43):

    T = a + omega * b,  12a = (0, 0, 4, 0),  12b = (6, 0, -6, 0)

so nothing here needs the float scan pickle: T is reconstructed in the field.

The two halves are clipped at *different* radii (E45): the A half must reach
1.6, the rotated half may stop at 1.3, which is the smallest exactly verified
non-4-colorable universe known in this family (2581 vertices, 14796 edges).

Floats are a prefilter only; every emitted edge satisfies dx^2 + dy^2 = 1 in
the field.

Env: RA, RB, LAYERS, OUT.
"""
import os
import pickle
from fractions import Fraction as Fr

import numpy as np

import findrot as R
import lattice

F = R.F
W = R.ROTS['w[15]']
RA = float(os.environ.get('RA', '1.6'))
RB = float(os.environ.get('RB', '1.3'))
LAYERS = int(os.environ.get('LAYERS', '3'))
OUT = os.environ.get('OUT', 'tuniv_1.6_1.3.pkl')


def to_field(v):
    a, b, c, d = v
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


def T65():
    """The score-65 translation, exactly: a + omega * b."""
    a = to_field((0, 0, 4, 0))
    b = to_field((6, 0, -6, 0))
    rb = R.cmul(b, W)
    return (F.add(a[0], rb[0]), F.add(a[1], rb[1]))


def base(radius, layers=LAYERS):
    return [to_field(p) for p in lattice.build_base(layers, radius)]


def exact_edges(pts):
    z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
    E = []
    for i in range(len(pts)):
        for k in np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]:
            j = i + 1 + int(k)
            dx = F.sub(pts[i][0], pts[j][0])
            dy = F.sub(pts[i][1], pts[j][1])
            if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
                E.append((i, j))
    return E


def build(ra=RA, rb=RB, T=None, layers=LAYERS):
    T = T65() if T is None else T
    pts = list(base(ra, layers))
    nA = len(pts)
    for q in base(rb, layers):
        r = R.cmul(q, W)
        pts.append((F.add(r[0], T[0]), F.add(r[1], T[1])))
    tag = {}
    for i, p in enumerate(pts):
        tag.setdefault(p, 'A' if i < nA else 'B')
    pts = sorted(set(pts), key=lambda q: (F.to_float(q[0]), F.to_float(q[1])))
    return pts, exact_edges(pts), [tag[p] for p in pts]


if __name__ == '__main__':
    pts, E, tags = build()
    print(f'rA={RA} rB={RB}: {len(pts)} vertices, {len(E)} exact edges, '
          f'{tags.count("A")} A / {tags.count("B")} B', flush=True)
    pickle.dump((pts, E), open(OUT, 'wb'))
    pickle.dump(tags, open(OUT.replace('.pkl', '') + '_tags.pkl', 'wb'))

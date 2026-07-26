"""Build the self-contained Parts pool and exact unit-edge universe."""
import os
import pickle
from fractions import Fraction as Fr

import numpy as np

import lattice
import findrot as R
from rotations import in_field_rotations

ROOT = os.path.dirname(__file__)
POOL = os.environ.get("POOL", os.path.join(ROOT, "pool.pkl"))
LAYERS = int(os.environ.get("LAYERS", "3"))
RADIUS = float(os.environ.get("RADIUS", "2.0"))


def to_field(v):
    a, b, c, d = v
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


def to_generic_field(v, field):
    a, b, c, d = v
    masks = {p: 1 << i for i, p in enumerate(field.primes)}
    return (tuple(Fr(a, 12) if i == 0 else
                  Fr(b, 12) if i == masks.get(3, -1) ^ masks.get(11, -1)
                  else Fr(0) for i in range(field.N)),
            tuple(Fr(c, 12) if i == masks.get(3, -1) else
                  Fr(d, 12) if i == masks.get(11, -1) else Fr(0)
                  for i in range(field.N)))


def build_universe_generic(rotation, translation=None, radius_a=2.0,
                            radius_b=2.0, layers=LAYERS):
    field, omega = rotation
    zero = (field.ZERO, field.ZERO)
    translation = translation or zero
    aa = lattice.build_base(layers, radius_a)
    bb = lattice.build_base(layers, radius_b)
    pts = [to_generic_field(p, field) for p in aa]
    for p in bb:
        x, y = to_generic_field(p, field)
        q = (field.sub(field.mul(x, omega[0]), field.mul(y, omega[1])),
             field.add(field.mul(x, omega[1]), field.mul(y, omega[0])))
        pts.append((field.add(q[0], translation[0]),
                    field.add(q[1], translation[1])))
    pts = sorted(set(pts), key=lambda q: (field.to_float(q[0]),
                                           field.to_float(q[1])))
    z = np.array([complex(field.to_float(x), field.to_float(y))
                  for x, y in pts])
    edges = []
    for i in range(len(pts)):
        near = np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]
        for k in near:
            j = i + 1 + int(k)
            dx = field.sub(pts[i][0], pts[j][0])
            dy = field.sub(pts[i][1], pts[j][1])
            if field.add(field.mul(dx, dx), field.mul(dy, dy)) == field.ONE:
                edges.append((i, j))
    return pts, edges


def load_pool(path=POOL):
    with open(path, "rb") as f:
        rec = pickle.load(f)
    return rec[0] if isinstance(rec, tuple) else rec


def build_base(layers=LAYERS, radius=RADIUS):
    return lattice.build_base(layers, radius)


def exact_edges(points):
    z = np.array([lattice.to_complex(p) for p in points])
    edges = []
    for i in range(len(points)):
        near = np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]
        for k in near:
            j = i + 1 + int(k)
            d = tuple(points[i][n] - points[j][n] for n in range(4))
            if lattice.is_unit(d):
                edges.append((i, j))
    return edges


def build_universe(omega=None, translation=None, radius_a=2.0, radius_b=2.0,
                   layers=LAYERS):
    omega = omega or R.ROTS["w[15]"]
    zero = (R.elt({}), R.elt({}))
    translation = translation or zero
    all_a = lattice.build_base(layers, radius_a)
    all_b = lattice.build_base(layers, radius_b)
    pts = [to_field(p) for p in all_a]
    pts += [(R.F.add(q[0], translation[0]), R.F.add(q[1], translation[1]))
            for p in all_b for q in [R.cmul(to_field(p), omega)]]
    pts = sorted(set(pts), key=lambda q: (R.F.to_float(q[0]), R.F.to_float(q[1])))
    z = np.array([complex(R.F.to_float(x), R.F.to_float(y)) for x, y in pts])
    edges = []
    for i in range(len(pts)):
        near = np.nonzero(np.abs(np.abs(z[i + 1:] - z[i]) - 1.0) < 1e-7)[0]
        for k in near:
            j = i + 1 + int(k)
            dx = R.F.sub(pts[i][0], pts[j][0])
            dy = R.F.sub(pts[i][1], pts[j][1])
            if R.F.add(R.F.mul(dx, dx), R.F.mul(dy, dy)) == R.F.ONE:
                edges.append((i, j))
    return pts, edges


if __name__ == "__main__":
    base = build_base()
    edges = exact_edges(base)
    pickle.dump(([("A", p) for p in base], edges), open(POOL, "wb"))
    print(f"{len(lattice.UNIT)} unit vectors; base {len(base)}; "
          f"{len(edges)} internal edges; wrote {POOL}", flush=True)

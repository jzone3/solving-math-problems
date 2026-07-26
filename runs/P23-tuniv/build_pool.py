"""Build the self-contained Parts pool and exact unit-edge universe."""
import os
import pickle
from fractions import Fraction as Fr

import numpy as np

import lattice
import findrot as R

ROOT = os.path.dirname(__file__)
POOL = os.environ.get("POOL", os.path.join(ROOT, "pool.pkl"))
LAYERS = int(os.environ.get("LAYERS", "4"))
RADIUS = float(os.environ.get("RADIUS", "2.0"))


def to_field(v):
    a, b, c, d = v
    return (R.elt({0: Fr(a, 12), 5: Fr(b, 12)}),
            R.elt({1: Fr(c, 12), 4: Fr(d, 12)}))


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
    all_a = [p for p in lattice.build_base(layers, radius_a)
             if abs(lattice.to_complex(p)) <= radius_a + 1e-9]
    all_b = [p for p in lattice.build_base(layers, radius_b)
             if abs(lattice.to_complex(p)) <= radius_b + 1e-9]
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

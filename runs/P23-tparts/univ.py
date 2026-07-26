# Provenance: reconstructed from origin/runs/P23-fusion1 build_w4x.py, ttest.py, and origin/runs/P23-parts-rho build_pool.py.
"""Rebuild translated two-half Parts universes with exact arithmetic.

The default ``pool_layers=3`` reproduces the legacy fusion1 pool used by E43-E45:
the pool is orbit-closed, then each half is clipped in the physical (positive)
embedding and augmented with the recovered L374 record half.  ``--pool-layers 4``
builds the corrected Parts pool (9259 points at radius 2) instead.

The pickle cache stores ``(points, edges, labels, metadata)``.  ``points`` are
complex coordinates as pairs of MField tuples; ``edges`` are sorted index pairs;
``labels`` maps ``'AA'``, ``'BB'`` and ``'cross'`` to edge lists.
"""
from __future__ import annotations

import argparse
import math
import os
import pickle
import time
from fractions import Fraction as F
from pathlib import Path

import numpy as np

import lattice as L
from mfield import MField


HERE = Path(__file__).resolve().parent
DECOMP = HERE / "decomp509.pkl"
FIELD = MField((3, 5, 11))
ZERO = (FIELD.ZERO, FIELD.ZERO)
OMEGA = (
    (F(7, 8), F(0), F(0), F(0), F(0), F(0), F(0), F(0)),
    (F(0), F(0), F(0), F(1, 8), F(0), F(0), F(0), F(0)),
)

TRANSLATIONS = {
    "0": ((0, 0, 0, 0), (0, 0, 0, 0)),
    "63": ((-5, 1, 7, -1), (2, 0, 0, -2)),
    "65": ((0, 0, 4, 0), (6, 0, -6, 0)),
}


def complex_mul(z, w):
    return (
        FIELD.sub(FIELD.mul(z[0], w[0]), FIELD.mul(z[1], w[1])),
        FIELD.add(FIELD.mul(z[0], w[1]), FIELD.mul(z[1], w[0])),
    )


def complex_add(z, w):
    return (FIELD.add(z[0], w[0]), FIELD.add(z[1], w[1]))


def lattice_field(p):
    a, b, c, d = p
    x = [F(0)] * FIELD.N
    y = [F(0)] * FIELD.N
    x[0], x[5] = F(a, 12), F(b, 12)
    y[1], y[4] = F(c, 12), F(d, 12)
    return tuple(x), tuple(y)


def translation_field(name):
    a, b = TRANSLATIONS[name]
    return complex_add(lattice_field(a), complex_mul(OMEGA, lattice_field(b)))


def pool_int(layers=3, radius=2.0):
    """Generate the orbit-closed integer pool used by fusion1.

    The intermediate slack is essential: a partial sum may leave the final
    disk while later unit-vector summands bring it back into the disk.
    """
    h2 = [L.frac_to_int(p) for p in L.Hm(2)]

    def radius2(p, conjugate=False):
        a, b, c, d = p
        n = a * a + 33 * b * b + 3 * c * c + 11 * d * d
        m = 2 * (a * b + c * d)
        sign = -1 if conjugate else 1
        return (n + sign * m * math.sqrt(33)) / 144.0

    cur = {(0, 0, 0, 0)}
    for step in range(layers):
        slack = layers - step - 1
        lim = (radius + slack + 1e-9) ** 2
        nxt = set()
        for p in cur:
            for q in h2:
                s = L.add(p, q)
                if min(radius2(s), radius2(s, conjugate=True)) <= lim:
                    nxt.add(s)
        cur = nxt

    lim = (radius + 1e-9) ** 2
    pool = set()
    for p in cur:
        a, b, c, d = p
        n = a * a + 33 * b * b + 3 * c * c + 11 * d * d
        m = 2 * (a * b + c * d)
        if min(n + m * math.sqrt(33), n - m * math.sqrt(33)) / 144.0 <= lim:
            pool.update(L.orbit(p))
    return sorted(pool)


def positive_radius(p):
    a, b, c, d = p
    n = a * a + 33 * b * b + 3 * c * c + 11 * d * d
    m = 2 * (a * b + c * d)
    return (n + m * math.sqrt(33)) / 144.0


def half_points(radius, pool, record_lattice):
    pts = {p for p in pool if positive_radius(p) <= (radius + 1e-9) ** 2}
    pts.update(record_lattice)
    return sorted(pts)


def edge_labels(points, memberships):
    """Enumerate exact unit edges and label every edge by all applicable kinds."""
    floats = np.array(
        [[FIELD.to_float(p[0]), FIELD.to_float(p[1])] for p in points],
        dtype=float,
    )
    cell = {}
    for i, (x, y) in enumerate(floats):
        cell.setdefault((math.floor(x), math.floor(y)), []).append(i)
    labels = {"AA": [], "BB": [], "cross": []}
    edges = []
    for (cx, cy), left in cell.items():
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                right = cell.get((cx + dx, cy + dy), ())
                for i in left:
                    for j in right:
                        if j <= i:
                            continue
                        d2 = float(np.sum((floats[i] - floats[j]) ** 2))
                        if abs(d2 - 1.0) > 1e-7:
                            continue
                        if FIELD.norm2(points[i], points[j]) != FIELD.ONE:
                            continue
                        e = (i, j)
                        edges.append(e)
                        # Shared points (notably the origin at T=0) can make
                        # an edge incident to both half-memberships.  Assign
                        # such an edge to a single deterministic bucket.
                        if memberships[i][0] and memberships[j][0]:
                            labels["AA"].append(e)
                        elif memberships[i][1] and memberships[j][1]:
                            labels["BB"].append(e)
                        else:
                            labels["cross"].append(e)
    return sorted(set(edges)), {k: sorted(set(v)) for k, v in labels.items()}


def build(translation="0", r_a=2.0, r_b=2.0, pool_layers=3):
    started = time.time()
    # Fusion1's radius ladder clips a single radius-2 pool at each requested
    # radius; rebuilding a smaller pool would silently change the universe.
    pool = pool_int(pool_layers, 2.0)
    data = pickle.load(DECOMP.open("rb"))
    record_lattice = {tuple(p) for p in data["L"]}
    a_int = half_points(r_a, pool, record_lattice)
    b_int = half_points(r_b, pool, record_lattice)
    a = [lattice_field(p) for p in a_int]
    t = translation_field(translation)
    b = [complex_add(t, complex_mul(OMEGA, lattice_field(p))) for p in b_int]

    points = []
    memberships = []
    index = {}
    for side, half in ((0, a), (1, b)):
        for p in half:
            if p not in index:
                index[p] = len(points)
                points.append(p)
                memberships.append([False, False])
            memberships[index[p]][side] = True
    edges, labels = edge_labels(points, memberships)
    metadata = {
        "translation": translation,
        "rA": r_a,
        "rB": r_b,
        "pool_layers": pool_layers,
        "pool_vertices": len(pool),
        "A_candidates": len(a_int),
        "B_candidates": len(b_int),
        "vertices": len(points),
        "edges": len(edges),
        "label_counts": {k: len(v) for k, v in labels.items()},
        "seconds": time.time() - started,
    }
    return points, edges, labels, metadata


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translation", choices=sorted(TRANSLATIONS), default="0")
    ap.add_argument("--rA", type=float, default=2.0)
    ap.add_argument("--rB", type=float, default=2.0)
    ap.add_argument("--pool-layers", type=int, default=3)
    ap.add_argument("--cache", default=None)
    args = ap.parse_args()
    result = build(args.translation, args.rA, args.rB, args.pool_layers)
    if args.cache:
        with open(args.cache, "wb") as f:
            pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
    _, edges, labels, meta = result
    print(
        f"{meta['translation']} rA={meta['rA']} rB={meta['rB']} "
        f"layers={meta['pool_layers']}: {meta['vertices']} vertices, "
        f"{len(edges)} edges, labels "
        f"AA={len(labels['AA'])} BB={len(labels['BB'])} cross={len(labels['cross'])}; "
        f"{meta['seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()

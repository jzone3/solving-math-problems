#!/usr/bin/env python3
"""Independent exact reproduction of the Polymath16 type-M rotations.

The base pools are rebuilt from this branch's mring.py.  Floating point is
used only to find candidate pairs; every accepted edge is confirmed in the
requested multiquadratic field.
"""

from __future__ import annotations

import argparse
import math
import os
import pickle
import subprocess
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "P23-fusion1"))
from mfield import MField
from mring import rotated_h

KISSAT = os.environ.get("KISSAT", "/home/ubuntu/tools/kissat/build/kissat")
DRATTRIM = os.environ.get("DRATTRIM", "/home/ubuntu/tools/drat-trim/drat-trim")
ZERO4 = (0, 0, 0, 0)


def norm144(p):
    a, b, c, d = p
    return a * a + 33 * b * b + 3 * c * c + 11 * d * d, 2 * (a * b + c * d)


def min_norm144(p):
    n, m = norm144(p)
    return n - abs(m) * math.sqrt(33.0)


def _half(a):
    if a % 2:
        raise ValueError(f"nonintegral symmetry image: {a}")
    return a // 2


def orbit24(p):
    """The same order-24 orbit, with integer-only direct transformations."""
    out = set()
    for x in (p, tau1(p), tau2(p)):
        for r in (x, (-x[0], -x[1], x[2], x[3])):
            for w in (r, (r[0], r[1], -r[2], -r[3])):
                out.add(w)
                out.add((w[0], -w[1], w[2], -w[3]))
    return out


def tau1(p):
    a, b, c, d = p
    return (_half(-a - 3 * c), _half(-b - d),
            _half(a - c), _half(3 * b - d))


def tau2(p):
    a, b, c, d = p
    return (_half(-a + 3 * c), _half(-b + d),
            _half(-a - c), _half(-3 * b - d))


def build_pool(t):
    """Build the orbit-closed radius-sqrt(t) pool using this branch's mring."""
    # The source construction deliberately adds a tiny epsilon before ceil:
    # at integral radii this admits the next Minkowski layer, while the final
    # radius test still retains only points on the requested disk.
    r = math.sqrt(t) + 1e-9
    n = max(2, math.ceil(r))
    h2 = rotated_h(2)
    cur = {ZERO4}
    for k in range(n):
        slack = n - k - 1
        limit = 144.0 * (r + slack) ** 2 + 1e-6
        nxt = set()
        for p in cur:
            for q in h2:
                s = tuple(x + y for x, y in zip(p, q))
                if min_norm144(s) <= limit:
                    nxt.add(s)
        cur = nxt
        print(f"pool t={t} summands={k + 1} candidates={len(cur)}",
              flush=True)
    limit = 144.0 * t + 1e-6
    pool = set()
    for p in cur:
        if min_norm144(p) <= limit:
            pool.update(orbit24(p))
    return sorted(pool)


def field_for(t):
    if t == 4:
        return MField((3, 5, 11))
    if t == 16:
        return MField((3, 7, 11))
    if t == 28:
        return MField((3, 11, 37))
    raise ValueError(t)


def mask_for(field, factors):
    mask = 0
    for p in factors:
        mask |= 1 << field.primes.index(p)
    return mask


def basis(field, mask):
    out = list(field.ZERO)
    out[mask] = Fraction(1)
    return tuple(out)


def rational(field, value):
    return field.scal(value, field.ONE)


def tuple_point(p, field):
    a, b, c, d = p
    rmask = mask_for(field, (3, 11))
    cmask = mask_for(field, (3,))
    dmask = mask_for(field, (11,))
    real = field.add(rational(field, Fraction(a, 12)),
                     field.scal(Fraction(b, 12), basis(field, rmask)))
    imag = field.add(field.scal(Fraction(c, 12), basis(field, cmask)),
                     field.scal(Fraction(d, 12), basis(field, dmask)))
    return real, imag


def omega(t, field):
    e = 4 * t - 1
    s = 1
    q = e
    f = 2
    while f * f <= q:
        while q % (f * f) == 0:
            q //= f * f
            s *= f
        f += 1
    factors = []
    left = q
    f = 2
    while f * f <= left:
        if left % f == 0:
            factors.append(f)
            while left % f == 0:
                left //= f
        f += 1
    if left > 1:
        factors.append(left)
    imag = basis(field, mask_for(field, tuple(factors)))
    return rational(field, Fraction(2 * t - 1, 2 * t)), field.scal(
        Fraction(s, 2 * t), imag)


def cmul(field, z, w):
    return (field.sub(field.mul(z[0], w[0]), field.mul(z[1], w[1])),
            field.add(field.mul(z[0], w[1]), field.mul(z[1], w[0])))


def norm2(field, z, w):
    dx = field.sub(z[0], w[0])
    dy = field.sub(z[1], w[1])
    return field.add(field.mul(dx, dx), field.mul(dy, dy))


def rotate_pool(t, pool, field):
    om = omega(t, field)
    return [cmul(field, om, tuple_point(p, field)) for p in pool]


def exact_edges(t, pool, field, rotated_pool=None):
    """Return tagged points and exact base/rotated/cross edge categories."""
    base = [tuple_point(p, field) for p in pool]
    rotated_lattice = pool if rotated_pool is None else rotated_pool
    rotated = rotate_pool(t, rotated_lattice, field)
    origin = rotated_lattice.index(ZERO4)
    points = [("A", p) for p in base]
    points += [("B", p) for i, p in enumerate(rotated) if i != origin]
    # The float array is only a candidate prefilter.
    floats = np.array([[field.to_float(z[0]), field.to_float(z[1])]
                       for _, z in points])
    edges = set()
    categories = {"base": 0, "rotated": 0, "cross": 0}
    n = len(points)
    block = 256
    for i0 in range(0, n, block):
        d = floats[i0:i0 + block, None, :] - floats[None, :, :]
        ii, jj = np.nonzero(np.sum(d * d, axis=2) <= 1.0 + 1e-7)
        for local_i, local_j in zip(ii, jj):
            if abs(float(np.sum(d[int(local_i), int(local_j)] ** 2)) - 1.0) > 1e-7:
                continue
            i, j = i0 + int(local_i), int(local_j)
            if i >= j:
                continue
            if norm2(field, points[i][1], points[j][1]) != field.ONE:
                continue
            edges.add((i, j))
            if points[i][0] == points[j][0]:
                categories["base" if points[i][0] == "A" else "rotated"] += 1
            else:
                categories["cross"] += 1
    return points, edges, categories


def write_cnf(path, nvars, clauses):
    with open(path, "w") as stream:
        stream.write(f"p cnf {nvars} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")


def color_cnf(n, edges):
    clauses = []
    for v in range(n):
        clauses.append([4 * v + c + 1 for c in range(4)])
        for c in range(4):
            for d in range(c + 1, 4):
                clauses.append([-(4 * v + c + 1), -(4 * v + d + 1)])
    for u, v in edges:
        for c in range(4):
            clauses.append([-(4 * u + c + 1), -(4 * v + c + 1)])
    # A triangle gives a useful, valid symmetry break without relying on
    # coordinates or side labels.
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    tri = None
    for u, v in edges:
        common = adj[u] & adj[v]
        if common:
            tri = (u, v, min(common))
            break
    if tri:
        for c, v in enumerate(tri):
            clauses.append([4 * v + c + 1])
    return 4 * n, clauses


def solve_color(n, edges, proof=False, timeout=7200):
    nvars, clauses = color_cnf(n, edges)
    with tempfile.TemporaryDirectory(prefix="rotation_repro_") as td:
        cnf = os.path.join(td, "graph.cnf")
        drat = os.path.join(td, "graph.drat")
        write_cnf(cnf, nvars, clauses)
        cmd = [KISSAT, "-q", cnf]
        if proof:
            cmd.append(drat)
        started = time.perf_counter()
        run = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout)
        elapsed = time.perf_counter() - started
        if "s UNSATISFIABLE" in run.stdout:
            if not proof:
                return "UNSAT", None, elapsed, run.stdout
            trim = subprocess.run([DRATTRIM, cnf, drat],
                                  capture_output=True, text=True,
                                  timeout=timeout)
            return ("UNSAT" if "s VERIFIED" in trim.stdout else "NOVERIFY",
                    None, elapsed, run.stdout + trim.stdout)
        if "s SATISFIABLE" not in run.stdout:
            return "UNKNOWN", None, elapsed, run.stdout
        model = set()
        for line in run.stdout.splitlines():
            if line.startswith("v "):
                model.update(int(x) for x in line.split()[1:] if int(x) > 0)
        return "SAT", model, elapsed, run.stdout


def check_model(model, n, edges):
    if model is None:
        return False
    colors = []
    for v in range(n):
        chosen = [c for c in range(4) if 4 * v + c + 1 in model]
        if len(chosen) != 1:
            return False
        colors.append(chosen[0])
    return all(colors[u] != colors[v] for u, v in edges)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("t", type=int, choices=(16, 28))
    ap.add_argument("--pool", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=7200)
    args = ap.parse_args()
    started = time.perf_counter()
    field = field_for(args.t)
    pool = pickle.load(args.pool.open("rb")) if args.pool else build_pool(args.t)
    print(f"t={args.t} pool={len(pool)}", flush=True)
    points, edges, categories = exact_edges(args.t, pool, field)
    print(f"t={args.t} union={len(points)} edges={len(edges)} "
          f"categories={categories}", flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("wb") as stream:
        pickle.dump((points, sorted(edges), pool, categories), stream)
    # Single copies use the exact subgraph induced by each side.
    for label, active in (("base", [i for i, p in enumerate(points)
                                    if p[0] == "A"]),
                          ("rotated", [i for i, p in enumerate(points)
                                       if p[0] == "B"])):
        remap = {x: i for i, x in enumerate(active)}
        subedges = [(remap[u], remap[v]) for u, v in edges
                    if u in remap and v in remap]
        status, model, elapsed, _ = solve_color(
            len(active), subedges, timeout=args.timeout)
        print(f"{label}: {status} model_exact={check_model(model, len(active), subedges)} "
              f"seconds={elapsed:.2f}", flush=True)
    status, _, elapsed, proof = solve_color(
        len(points), edges, proof=True, timeout=args.timeout)
    print(f"union: {status} seconds={elapsed:.2f} "
          f"drat_verified={'s VERIFIED' in proof}", flush=True)
    print(f"total_seconds={time.perf_counter() - started:.2f}", flush=True)


if __name__ == "__main__":
    main()

"""Type-M experiment for rotation omega_t: build W_t = P union omega_t*P
(P = base pool of radius sqrt(t), sharing the origin), compute all edges
exactly, and SAT-test 4-colorability.

Usage: typem.py <t> [<pool.pkl>]     (pool built on the fly if not given)
Writes wt_<t>.pkl = (points, edges) with points = list of ('A'|'B', tuple);
prints SAT (4-colorable => t does not support type M at this radius) or
UNSAT (5-chromatic witness!).
"""
import math
import pickle
import sys

import numpy as np

import build_pool_r
import lattice
from sat import color_cnf, solve


def build_wt(t, pool):
    e_s = lattice.squarefree_split(4 * t - 1)
    O = (0, 0, 0, 0)
    A = [p for p in pool]
    Bc = [p for p in pool if p != O]  # origin shared
    pts = [("A", p) for p in A] + [("B", p) for p in Bc]
    om = complex((2 * t - 1) / (2 * t), math.sqrt(4 * t - 1) / (2 * t))
    Z = np.array([lattice.to_complex(p) for _, p in pts])
    for k, (side, p) in enumerate(pts):
        if side == "B":
            Z[k] *= om
    n = len(pts)
    edges = []
    Bl = 256
    for i0 in range(0, n, Bl):
        D = np.abs(Z[i0:i0 + Bl, None] - Z[None, :])
        ii, jj = np.nonzero(np.abs(D - 1.0) < 1e-6)
        for i, j in zip(ii, jj):
            i, j = i0 + int(i), int(j)
            if i >= j:
                continue
            (s1, p1), (s2, p2) = pts[i], pts[j]
            if s1 == s2:
                ok = lattice.is_unit(p1, p2)
            else:
                u, v = (p1, p2) if s1 == "A" else (p2, p1)
                ok = lattice.cross_is_unit(u, v, t, e_s)
            if ok:
                edges.append((i, j))
    return pts, edges


def main():
    t = int(sys.argv[1])
    if len(sys.argv) > 2:
        pool = pickle.load(open(sys.argv[2], "rb"))
    else:
        pool = build_pool_r.build(math.sqrt(t) + 1e-9)
    pts, edges = build_wt(t, pool)
    print(f"t={t}: W has {len(pts)} vertices, {len(edges)} edges", flush=True)
    with open(f"wt_{t}.pkl", "wb") as f:
        pickle.dump((pts, edges), f)
    # symmetry-breaking triangle
    adj = {}
    for i, j in edges:
        adj.setdefault(i, set()).add(j)
        adj.setdefault(j, set()).add(i)
    tri = None
    for i, j in edges:
        common = adj[i] & adj[j]
        if common:
            tri = (i, j, min(common))
            break
    nvars, cls = color_cnf(len(pts), edges, 4, sym_clique=tri)
    status, model = solve(nvars, cls, timeout=7200)
    print(f"t={t}: 4-colorability -> {status}", flush=True)


if __name__ == "__main__":
    main()

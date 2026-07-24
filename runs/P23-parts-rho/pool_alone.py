"""SAT-test 4-colorability of a single (unrotated) base pool of radius r.
Usage: pool_alone.py <r>
"""
import math
import pickle
import sys

import numpy as np

import build_pool_r
import lattice
from sat import color_cnf, solve


def main():
    r = float(sys.argv[1])
    pool = build_pool_r.build(r + 1e-9)
    Z = np.array([lattice.to_complex(p) for p in pool])
    n = len(pool)
    edges = []
    for i0 in range(0, n, 256):
        D = np.abs(Z[i0:i0 + 256, None] - Z[None, :])
        ii, jj = np.nonzero(np.abs(D - 1.0) < 1e-6)
        for i, j in zip(ii, jj):
            i, j = i0 + int(i), int(j)
            if i < j and lattice.is_unit(pool[i], pool[j]):
                edges.append((i, j))
    print(f"r={r}: {n} vertices, {len(edges)} edges", flush=True)
    adj = {}
    for i, j in edges:
        adj.setdefault(i, set()).add(j)
        adj.setdefault(j, set()).add(i)
    tri = None
    for i, j in edges:
        c = adj[i] & adj[j]
        if c:
            tri = (i, j, min(c))
            break
    nvars, cls = color_cnf(n, edges, 4, sym_clique=tri)
    status, _ = solve(nvars, cls, timeout=7200)
    print(f"r={r}: single-copy 4-colorability -> {status}", flush=True)


if __name__ == "__main__":
    main()

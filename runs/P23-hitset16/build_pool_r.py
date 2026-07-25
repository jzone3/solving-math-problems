"""Build base-graph pool of radius r: vertices of +^n H^2 (n = ceil(r)) with
min conjugate radius <= r, orbit-closed.  Usage: build_pool_r.py <r> <out.pkl>
"""
import math
import pickle
import sys

import lattice


def build(rmax):
    lim = 144.0 * rmax * rmax + 1e-6
    n = max(4, math.ceil(rmax))
    H2 = lattice.Hm(2)
    cur = {(0, 0, 0, 0)}
    for k in range(n):
        slack = n - (k + 1)
        klim = 144.0 * (rmax + slack) ** 2 + 1e-6
        cur = {lattice.add(p, q) for p in cur for q in H2
               if min(lattice.radius2_144(lattice.add(p, q))) <= klim}
    pool = set()
    for p in cur:
        if min(lattice.radius2_144(p)) <= lim:
            pool |= lattice.orbit24(p)
    return sorted(pool)


if __name__ == "__main__":
    r = float(sys.argv[1])
    out = sys.argv[2]
    pool = build(r)
    print(f"r={r}: {len(pool)} vertices")
    with open(out, "wb") as f:
        pickle.dump(pool, f)

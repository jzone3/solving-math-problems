"""Build the base-graph pool: vertices of B = +^4 H^2 whose min conjugate
radius is <= RMAX (Parts used the disk r = 2), orbit-closed under the
order-24 base symmetry group.  Saves pool.pkl (sorted list of int 4-tuples).
"""
import pickle
import sys

import lattice

RMAX = 2.0
LIM = 144.0 * RMAX * RMAX + 1e-6


def keep(p, slack):
    r1, r2 = lattice.radius2_144(p)
    lim = 144.0 * (RMAX + slack) ** 2 + 1e-6
    return min(r1, r2) <= lim


def main():
    H2 = lattice.Hm(2)
    print("H^2:", len(H2))
    cur = {(0, 0, 0, 0)}
    for k in range(4):
        slack = 4 - (k + 1)  # remaining summands each have radius <= 1
        nxt = set()
        for p in cur:
            for q in H2:
                s = lattice.add(p, q)
                if keep(s, slack):
                    nxt.add(s)
        cur = nxt
        print(f"after {k + 1} summands: {len(cur)}")
    # orbit closure
    pool = set()
    for p in cur:
        if min(lattice.radius2_144(p)) <= LIM:
            pool |= lattice.orbit24(p)
    pool = sorted(pool)
    for p in pool:
        assert lattice.check_lattice(p), p
    # orbit count
    seen, orbits = set(), 0
    for p in pool:
        if p not in seen:
            orbits += 1
            seen |= lattice.orbit24(p)
    print(f"pool: {len(pool)} vertices in {orbits} base orbits")
    with open("pool.pkl", "wb") as f:
        pickle.dump(pool, f)


if __name__ == "__main__":
    main()

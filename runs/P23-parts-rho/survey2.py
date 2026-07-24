"""Per-t cross-edge survey with pool radius sqrt(t) (so that the reference
orbit at radius sqrt(t) is included, exactly as Parts' r=2 disk includes the
(0,4,4,0) reference orbit for t=4).

For each t: pool P_t = base lattice points with min conjugate radius <=
sqrt(t) (+EPS), cross pairs (u, omega_t v) with u,v in P_t, u,v != 0,
|u - omega_t v| = 1 verified in exact integer arithmetic.

Output: for each t, total cross edges, kinds (144|u|^2,144|v|^2) with counts,
number of reference edges (|u|^2=|v|^2=t).  Results -> survey2.pkl
"""
import math
import pickle
import sys

import numpy as np

import build_pool_r
import lattice

EPS = 1e-9
TS = [int(x) for x in sys.argv[1:]] or list(range(1, 26))
OUT = "survey2b.pkl" if sys.argv[1:] else "survey2.pkl"


def cross_pairs(pool, t):
    e, s = lattice.squarefree_split(4 * t - 1)
    Z = np.array([lattice.to_complex(p) for p in pool])
    om = complex((2 * t - 1) / (2 * t), math.sqrt(4 * t - 1) / (2 * t))
    W = Z * om
    n = len(pool)
    out = []
    B = 256
    for i0 in range(0, n, B):
        D = np.abs(Z[i0:i0 + B, None] - W[None, :])
        ii, jj = np.nonzero(np.abs(D - 1.0) < 1e-6)
        for i, j in zip(ii, jj):
            u, v = pool[i0 + int(i)], pool[int(j)]
            if u == (0, 0, 0, 0) or v == (0, 0, 0, 0):
                continue
            if lattice.cross_is_unit(u, v, t, (e, s)):
                out.append((i0 + int(i), int(j)))
    return out


def main():
    results = {}
    pools = {}
    for t in TS:
        r = math.sqrt(t) + EPS
        key = round(r, 6)
        if key not in pools:
            pools[key] = build_pool_r.build(r)
        pool = pools[key]
        pairs = cross_pairs(pool, t)
        norms = [lattice.norm144(p) for p in pool]
        kinds = {}
        nref = 0
        for i, j in pairs:
            k = tuple(sorted((norms[i], norms[j])))
            kinds[k] = kinds.get(k, 0) + 1
            if norms[i] == (144 * t, 0) and norms[j] == (144 * t, 0):
                nref += 1
        e, s = lattice.squarefree_split(4 * t - 1)
        native = e in (3, 11)
        results[t] = dict(t=t, e=e, s=s, native=native, pool=len(pool),
                          cross=len(pairs), ref=nref, nkinds=len(kinds),
                          kinds=kinds)
        top = sorted(kinds.items(), key=lambda kv: -kv[1])[:5]
        print(f"t={t:2d}{' NATIVE' if native else '':7s} pool={len(pool):6d} "
              f"cross={len(pairs):7d} ref={nref:5d} kinds={len(kinds):4d} "
              f"top={[c for _, c in top]}", flush=True)
        with open(OUT, "wb") as f:
            pickle.dump(results, f)


if __name__ == "__main__":
    main()

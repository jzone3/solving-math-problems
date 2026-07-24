"""Cross-edge survey: for each rotation omega_t (t = 1..TMAX), measure how
rich the cross-edge structure of  B  union  omega_t * B  is, where B is the
radius-2 base-graph pool (pool.pkl).

For each t reports:
  - n_sqrt_t : number of pool points u with |u|^2 == t exactly (each gives a
    'reference' cross edge u -- omega_t u)
  - cross    : number of exact cross unit pairs (u, omega_t v), u,v in pool
    (excluding u=v=0)
  - kinds    : number of distinct triangle shapes (144|u|^2, 144|v|^2) among
    cross edges, and the multiset of counts per kind
Floats (numpy) are only a prefilter; every reported edge passes the exact
integer test lattice.cross_is_unit.
"""
import pickle
import sys

import numpy as np

import lattice

TMAX = 32
TOL = 1e-6


def main():
    with open("pool.pkl", "rb") as f:
        pool = pickle.load(f)
    n = len(pool)
    Z = np.array([lattice.to_complex(p) for p in pool])
    norms = [lattice.norm144(p) for p in pool]
    print(f"pool: {n} points")
    results = {}
    for t in range(1, TMAX + 1):
        e, s = lattice.squarefree_split(4 * t - 1)
        om = complex((2 * t - 1) / (2 * t), (4 * t - 1) ** 0.5 / (2 * t))
        W = Z * om
        cand = []
        B = 512
        for i0 in range(0, n, B):
            D = np.abs(Z[i0:i0 + B, None] - W[None, :])
            ii, jj = np.nonzero(np.abs(D - 1.0) < TOL)
            for i, j in zip(ii, jj):
                cand.append((i0 + int(i), int(j)))
        exact = [(i, j) for i, j in cand
                 if lattice.cross_is_unit(pool[i], pool[j], t, (e, s))]
        nref = sum(1 for N, M in norms if M == 0 and N == 144 * t)
        kinds = {}
        for i, j in exact:
            k = tuple(sorted((norms[i], norms[j])))
            kinds[k] = kinds.get(k, 0) + 1
        native = e in (3, 11)
        results[t] = dict(t=t, e=e, s=s, native=native, nref=nref,
                          cross=len(exact), nkinds=len(kinds), kinds=kinds)
        top = sorted(kinds.items(), key=lambda kv: -kv[1])[:6]
        print(f"t={t:2d} 4t-1={e}*{s}^2{' NATIVE' if native else '':7s} "
              f"|u|^2=t pts: {nref:5d}  cross: {len(exact):7d}  "
              f"kinds: {len(kinds):4d}  top: {[c for _, c in top]}")
        sys.stdout.flush()
    with open("survey.pkl", "wb") as f:
        pickle.dump(results, f)


if __name__ == "__main__":
    main()

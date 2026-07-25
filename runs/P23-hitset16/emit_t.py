"""Emit an induced subgraph of W_t (wt_<t>.pkl) as exact multiquadratic field
points + edges for independent verification with verify_m.py.

Usage: emit_t.py <t> <subset.pkl|-> <out.pkl>
  subset.pkl = sorted list of vertex ids into wt_<t>.pkl points ('-' = all)
Output pkl: (points, edges) with points = pairs of MField elements over
primes {3,11} u primefactors(e), 4t-1 = e*s^2.
"""
import pickle
import sys
from fractions import Fraction as F

import sympy as sp

import lattice
from mfield import MField


def field_for_t(t):
    e, s = lattice.squarefree_split(4 * t - 1)
    gens = sorted(set([3, 11]) | set(sp.factorint(e).keys()))
    return MField(tuple(gens)), e, s


def elem(K, coeffs):
    """coeffs: dict radicand-> Fraction."""
    out = [F(0)] * K.N
    for rad, c in coeffs.items():
        m = next(m for m in range(K.N) if K._radval[m] == rad)
        out[m] += c
    return tuple(out)


def point_field(K, t, e, s, side, p):
    a, b, c, d = p
    re = elem(K, {1: F(a, 12), 33: F(b, 12)})
    im = elem(K, {3: F(c, 12), 11: F(d, 12)})
    if side == "B":
        # multiply by omega_t = (2t-1)/(2t) + i * s*sqrt(e)/(2t)
        wr = elem(K, {1: F(2 * t - 1, 2 * t)})
        wi = elem(K, {e: F(s, 2 * t)})
        re, im = (K.sub(K.mul(re, wr), K.mul(im, wi)),
                  K.add(K.mul(re, wi), K.mul(im, wr)))
    return (re, im)


def main():
    t = int(sys.argv[1])
    pts, edges = pickle.load(open(f"wt_{t}.pkl", "rb"))
    if sys.argv[2] == "-":
        sub = list(range(len(pts)))
    else:
        sub = pickle.load(open(sys.argv[2], "rb"))
    K, e, s = field_for_t(t)
    remap = {v: i for i, v in enumerate(sub)}
    fpts = [point_field(K, t, e, s, *pts[v]) for v in sub]
    fedges = sorted((remap[u], remap[v]) for u, v in edges
                    if u in remap and v in remap)
    pickle.dump((fpts, fedges), open(sys.argv[3], "wb"))
    print(f"t={t} primes={K.primes}: {len(fpts)} pts, {len(fedges)} edges "
          f"-> {sys.argv[3]}")


if __name__ == "__main__":
    main()

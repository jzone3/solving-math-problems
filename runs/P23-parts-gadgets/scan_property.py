"""Scan gadget-property existence over the base graph.

For each candidate distance d (rational d^2, lattice-representable) and each
placement orbit, test on pool = clip(oplus^N H^M, R2 around pair midpoint):
  - mono property   (UNSAT of 4col + u,v forced different)
  - nonmono property(UNSAT of 4col + u,v forced equal)
A distance admitting BOTH (in any placements) yields a 5-chromatic union
directly: union of the two gadget graphs sharing the two endpoints.

Usage: python3 scan_property.py   (env N,M,R2,DEGMIN as usual)
"""
import os
import sys
import time
from fractions import Fraction as F

from lattice import int_to_frac, to_float, orbit, scale
from pools import build_pool, find_radius_points
from gadget import GadgetInstance

DISTANCES = [
    ("1/3", F(1, 9)), ("2/3", F(4, 9)), ("1", F(1)), ("4/3", F(16, 9)),
    ("5/3", F(25, 9)), ("2", F(4)), ("7/3", F(49, 9)), ("8/3", F(64, 9)),
    ("3", F(9)), ("10/3", F(100, 9)),
    ("sqrt(1/3)", F(1, 3)), ("sqrt(4/3)", F(4, 3)), ("sqrt(7/3)", F(7, 3)),
    ("sqrt(11/3)", F(11, 3)), ("sqrt3", F(3)), ("sqrt(16/3)", F(16, 3)),
    ("sqrt(19/3)", F(19, 3)), ("sqrt5", F(5)), ("sqrt7", F(7)),
    ("sqrt(25/3)", F(25, 3)), ("sqrt(64/3)", F(64, 3)),
    ("sqrt2", F(2)), ("sqrt(8/3)", F(8, 3)), ("sqrt6", F(6)), ("sqrt8", F(8)),
    ("sqrt(5/3)", F(5, 3)), ("sqrt(20/3)", F(20, 3)), ("sqrt11", F(11)),
    ("sqrt(11/12)", F(11, 12)), ("sqrt(33)/3", F(33, 9)),
]


def main():
    N = int(os.environ.get("N", 3))
    M = int(os.environ.get("M", 2))
    DEGMIN = int(os.environ.get("DEGMIN", 5)) or None
    PLIMIT = int(os.environ.get("PLIMIT", 4))
    for name, d2 in DISTANCES:
        vecs = find_radius_points(d2)
        reps = []
        seen = set()
        for v in vecs:
            r = min(orbit(v))
            if r not in seen:
                seen.add(r)
                reps.append(v)
        if not reps:
            print("d=%s: not lattice-representable" % name, flush=True)
            continue
        # pool radius: cover pair + margin 2 in every direction
        import math
        dd = math.sqrt(float(d2))
        R2 = F(int(math.ceil((dd / 2 + 1.6) ** 2 * 16)), 16)
        results = []
        for v in reps[:PLIMIT]:
            p0 = (F(0),) * 4
            p1 = int_to_frac(v)
            center = scale(p1, F(1, 2))
            pool, edges, gids = build_pool([p0, p1], R2, n=N, m=M,
                                           degmin=DEGMIN, center=center)
            mono = GadgetInstance(pool, edges, gids, "mono").holds()
            nonm = GadgetInstance(pool, edges, gids, "nonmono").holds()
            results.append((v, mono, nonm))
        summary = ", ".join("%s:mono=%s,nonmono=%s" % (v, m, nm)
                            for v, m, nm in results)
        both = any(m for _, m, _ in results) and any(nm for _, _, nm in results)
        print("d=%s (pool r2<=%s): %s%s" % (name, R2, summary,
              "   <== MONO+NONMONO" if both else ""), flush=True)


if __name__ == "__main__":
    main()

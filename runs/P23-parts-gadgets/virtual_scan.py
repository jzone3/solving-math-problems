"""Scan small base-lattice hosts for VIRTUAL EDGES (Polymath16 sense).

A host G has a virtual edge at distance d if EVERY proper 4-coloring of G
contains at least one monochromatic pair at distance exactly d. Refutation
CNF: 4-coloring clauses + for every d-pair (u,v) an "inequality" gadget
(u,v not both color k, for all k). SAT <=> some coloring avoids all mono
d-pairs <=> no virtual edge; UNSAT <=> virtual edge.

Devirtualization cost: clamping a non-mono-d gadget (size s_d) onto each of
the k d-pairs gives a non-4-colorable graph of size
    |G| + k*(s_d - 2) - (overlaps between gadget copies and host).
This script reports (host, d, k) so those totals can be bounded.
"""
import os
from fractions import Fraction as F

from lattice import to_float
from pools import oplus, clip
from gadget import build_cnf, solve, color_var
from lattice import unit_edges, pairs_at_dist2

# candidate virtual-edge distances with known non-mono gadgets (Parts sizes)
CAND = [("3", F(9), 214), ("7/3", F(49, 9), 319), ("5/3", F(25, 9), 315),
        ("1/3", F(1, 9), 312), ("sqrt(11/3)", F(11, 3), 308)]

HOSTS = [
    ("H^1", lambda: oplus(1, 1)),
    ("H^2", lambda: oplus(1, 2)),
    ("oplus2H^1", lambda: oplus(2, 1)),
    ("oplus2H^2_clip2", lambda: clip(oplus(2, 2), F(4))),
    ("oplus2H^2", lambda: oplus(2, 2)),
]


def has_virtual_edge(points, edges, pairs):
    cls = build_cnf(len(points), edges, [])
    for (u, v) in pairs:
        for k in range(4):
            cls.append([-color_var(u, k), -color_var(v, k)])
    return solve(cls, 4 * len(points)) == "UNSAT"


def main():
    for hname, hf in HOSTS:
        pts = hf()
        edges = unit_edges(pts)
        for dname, d2, gsize in CAND:
            pairs = pairs_at_dist2(pts, d2)
            if not pairs:
                continue
            ve = has_virtual_edge(pts, edges, pairs)
            k = len(pairs)
            if ve:
                naive = len(pts) + k * (gsize - 2)
                print("HOST %s (%d vtx): VIRTUAL EDGE at d=%s, k=%d pairs, "
                      "naive clamp total = %d" % (hname, len(pts), dname, k, naive),
                      flush=True)
            else:
                print("host %s (%d vtx): d=%s k=%d -- no virtual edge"
                      % (hname, len(pts), dname, k), flush=True)


if __name__ == "__main__":
    main()

"""Minimize a gadget graph. Usage:
  python3 run_gadget.py triple <circumradius^2 fraction>   (side^2 = 3*that)
  python3 run_gadget.py monopair|nonmonopair <d^2 fraction>
  python3 run_gadget.py monopair <d as fraction> ...
  python3 run_gadget.py nonmonopair <d as fraction> ...
Gadget placements are exact; pool = clip(oplus^n H^m, R2) with degree filter.
Env: N, M, R2 (fraction), DEGMIN, SEED.
"""
import os
import pickle
import sys
import time
from fractions import Fraction as F

from lattice import int_to_frac, to_float, unit_edges, orbit, scale, add
from pools import build_pool, equilateral_triples, find_radius_points
from gadget import GadgetInstance


def frac(s):
    return F(s)


def placements(kind, val):
    """Yield (gadget points, pool center) placements, one per lattice orbit."""
    if kind == "triple":
        seen = set()
        for tr in equilateral_triples(val):  # val = circumradius^2 = side^2/3
            rep = min(orbit(tr[0]))
            if rep in seen:
                continue
            seen.add(rep)
            yield [int_to_frac(t) for t in tr], None
    else:
        seen = set()
        for delta in find_radius_points(val):  # val = pair distance^2
            rep = min(orbit(delta))
            if rep in seen:
                continue
            seen.add(rep)
            p0 = (F(0), F(0), F(0), F(0))
            p1 = int_to_frac(delta)
            yield [p0, p1], scale(p1, F(1, 2))


def main():
    kind = sys.argv[1]
    val = frac(sys.argv[2])
    N = int(os.environ.get("N", 3))
    M = int(os.environ.get("M", 2))
    R2 = F(os.environ.get("R2", "4"))
    DEGMIN = int(os.environ.get("DEGMIN", 0)) or None
    SEED = int(os.environ.get("SEED", 0))
    PLIMIT = int(os.environ.get("PLIMIT", 8))
    t0 = time.time()
    gkind = "mono" if kind == "monopair" else "nonmono"

    inst = None
    for np, (pts, center) in enumerate(placements(kind, val)):
        if np >= PLIMIT:
            break
        print("placement %d: %s" % (np, [to_float(p) for p in pts]), flush=True)
        pool, edges, gids = build_pool(pts, R2, n=N, m=M, degmin=DEGMIN,
                                       center=center)
        print("pool: %d vertices, %d edges (%.1fs)" % (len(pool), len(edges), time.time() - t0), flush=True)
        cand = GadgetInstance(pool, edges, gids, gkind)
        if cand.holds():
            inst = cand
            break
        print("placement %d: property SAT, trying next" % np, flush=True)
    if inst is None:
        print("PROPERTY DOES NOT HOLD ON ANY PLACEMENT — enlarge pool", flush=True)
        return
    print("property holds on pool (UNSAT), %.1fs" % (time.time() - t0), flush=True)
    inst = inst.shrink_core()
    print("after core fixpoint: %d vertices (%.1fs)" % (len(inst.points), time.time() - t0), flush=True)
    inst = inst.greedy(seed=SEED, log=lambda s: print(s + " (%.1fs)" % (time.time() - t0), flush=True))
    print("FINAL: %d vertices, %d edges" % (len(inst.points), len(inst.edges)), flush=True)
    out = "gadget_%s_%s_seed%d.pkl" % (kind, str(val).replace("/", "_"), SEED)
    with open(out, "wb") as f:
        pickle.dump({"points": inst.points, "edges": inst.edges,
                     "gadget": inst.gadget, "kind": inst.kind}, f)
    print("saved", out, flush=True)


if __name__ == "__main__":
    main()

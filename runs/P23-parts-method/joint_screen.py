#!/usr/bin/env python3
"""Screen a simultaneous L/S expansion on the complete union."""
import argparse
import datetime
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor

from mring import orbit
from sat_parts import CNFTemplate, PartsGraph

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--l-rep", nargs=4, type=int, required=True)
    ap.add_argument("--s-rep", nargs=4, type=int, required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    d = pickle.load(open(os.path.join(HERE, "decomp509.pkl"), "rb"))
    old = PartsGraph.from_decomposition(d, "L")
    d2 = {
        "L": frozenset(set(d["L"]) | orbit(tuple(args.l_rep))),
        "S": frozenset(set(d["S"]) | orbit(tuple(args.s_rep))),
    }
    expanded = PartsGraph.from_decomposition(d2, "L")
    old_points = set(old.points)
    old_indices = [expanded.points.index(p) for p in old_points]
    clique = tuple(expanded.points.index(p) for p in (
        old.points[0],
        old.points[old.ring_points["clique"][1]],
        old.points[old.ring_points["clique"][2]],
    ))
    template = CNFTemplate(len(expanded.points), expanded.edges,
                           sym_clique=clique)
    baseline = template.solve(range(len(expanded.points)))

    def check(i):
        active = set(range(len(expanded.points))) - {i}
        return template.solve(active)

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(check, old_indices))
    indispensable = sum(r.status == "SAT" for r in results)
    freed = len(old_indices) - indispensable
    print({
        "L_added": len(set(d2["L"]) - set(d["L"])),
        "S_added": len(set(d2["S"]) - set(d["S"])),
        "vertices": len(expanded.points),
        "edges": len(expanded.edges),
        "baseline": baseline.status,
        "old_union": len(old_indices),
        "indispensable": indispensable,
        "freed": freed,
        "checks": len(results),
        "wall": round(time.perf_counter() - started, 1),
    })
    with open(os.path.join(HERE, "NOTES.md"), "a") as f:
        f.write("| " + " | ".join(map(str, (
            datetime.datetime.now().isoformat(timespec="seconds"),
            "joint",
            f"L{tuple(args.l_rep)}+S{tuple(args.s_rep)}",
            len(expanded.points),
            f"indispensable={indispensable};freed={freed}",
            indispensable, len(results),
            f"{time.perf_counter()-started:.1f}s", baseline.status))) + " |\n")


if __name__ == "__main__":
    main()

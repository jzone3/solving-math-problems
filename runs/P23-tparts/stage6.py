# Provenance: new stage-6 B-first frontier search using cegar.py and stage4.py.
"""B-first small-interface search with constructive A growth."""

from __future__ import annotations

import argparse
import math
import pickle
import time
from collections import Counter

import cegar
import univ


def _float_point(p):
    return univ.FIELD.to_float(p[0]), univ.FIELD.to_float(p[1])


def b_radius_ids(points, metadata, radius):
    """Select cached B points by the radius of their unrotated lattice point."""
    tx, ty = _float_point(univ.translation_field(metadata["translation"]))
    wr, wi = 7.0 / 8.0, math.sqrt(15.0) / 8.0
    out = set()
    for i in range(metadata["A_candidates"], len(points)):
        x, y = _float_point(points[i])
        dx, dy = x - tx, y - ty
        # conj(omega) * (q-T)
        px = wr * dx + wi * dy
        py = -wi * dx + wr * dy
        if px * px + py * py <= (radius + 1e-8) ** 2:
            out.add(i)
    return out


def record_s_ids(points, metadata):
    """Locate Parts' rotated S135 exactly in a cached universe."""
    data = pickle.load(univ.DECOMP.open("rb"))
    t = univ.translation_field(metadata["translation"])
    wanted = set()
    for p in data["S"]:
        q = univ.complex_add(
            t, univ.complex_mul(univ.OMEGA, univ.lattice_field(p))
        )
        wanted.add(q)
    lookup = {p: i for i, p in enumerate(points)}
    return {
        lookup[q] for q in wanted
        if q in lookup and lookup[q] >= metadata["A_candidates"]
    }


def run_case(cache, b_mode, seed=1, limit=10000):
    points, labels, metadata, a_pool, b_pool, _, _ = cegar.side_sets(
        cache, "full"
    )
    b_edges, cross = cegar.split_edges(labels, metadata)
    if b_mode == "record":
        S = record_s_ids(points, metadata)
    else:
        S = b_radius_ids(points, metadata, float(b_mode))
    interface = {a for a, b in cross if b in S}
    started = time.time()
    L, patterns, history, status = cegar.run_cegar(
        interface, S, a_pool, labels["AA"], b_edges, cross,
        batch=4, limit=limit,
    )
    core_size = None
    if status == "UNSAT":
        core = cegar.core_reduce(
            L, labels["AA"], patterns,
            {v for vs, _ in patterns for v in vs},
        )
        core_size = len(core)
        L = core
    return {
        "cache": cache,
        "b_mode": b_mode,
        "A_pool": len(a_pool),
        "B_pool": len(b_pool),
        "L": sorted(L),
        "S": sorted(S),
        "interface": len(interface),
        "cross": sum(1 for a, b in cross if b in S),
        "patterns": patterns,
        "orders": dict(Counter(len(vs) for vs, _ in patterns)),
        "status": status,
        "core_L": core_size,
        "total": len(L) + len(S),
        "history_events": Counter(h["event"] for h in history),
        "seconds": time.time() - started,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("--b", nargs="+", required=True,
                    help="record or one or more physical B radii")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=10000)
    args = ap.parse_args()
    modes = ["record" if x == "record" else float(x) for x in args.b]
    results = []
    for mode in modes:
        result = run_case(args.cache, mode, limit=args.limit)
        results.append(result)
        print({
            "b_mode": result["b_mode"],
            "A_pool": result["A_pool"],
            "B_pool": result["B_pool"],
            "A": len(result["L"]),
            "B": len(result["S"]),
            "interface": result["interface"],
            "cross": result["cross"],
            "orders": result["orders"],
            "status": result["status"],
            "core_L": result["core_L"],
            "total": result["total"],
            "history_events": dict(result["history_events"]),
            "seconds": result["seconds"],
        }, flush=True)
    pickle.dump(results, open(args.out, "wb"), protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()

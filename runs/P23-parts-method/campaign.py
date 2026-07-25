#!/usr/bin/env python3
"""Expansion/reduction campaign driver for one Parts subgraph leg."""
import argparse
import datetime
import os
import pickle
import time

from finesearch import FineConfig, FineSearch, expansion_reserve
from mring import orbit
from sat_parts import PartsGraph

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "decomp509.pkl")
NOTES = os.path.join(HERE, "NOTES.md")


def log(row):
    with open(NOTES, "a") as f:
        f.write("| " + " | ".join(map(str, row)) + " |\n")


def run_leg(leg, limit=6, max_checks=3000):
    original = pickle.load(open(CACHE, "rb"))
    A = set(original[leg])
    companion = original["S" if leg == "L" else "L"]
    if leg == "L":
        openers = [
            (0, 0, 12, 0), (0, 0, 2, 2), (4, 0, 10, 2),
            (10, 0, 2, 4), (0, 0, 0, 4), (0, 0, 6, 6),
            (4, 0, 0, 0),
        ]
        candidates = [(f"Parts opener {v}", orbit(v)) for v in openers]
    else:
        candidates = []
    reserve = expansion_reserve(A)
    for score, size, rep, vertices in reserve:
        if score >= 4 and vertices - A:
            candidates.append((f"reserve {rep} score={score}", vertices))
    seen = set()
    for label, added in candidates:
        added = frozenset(added - A)
        if not added or added in seen:
            continue
        seen.add(added)
        if len(seen) > limit:
            break
        started = time.perf_counter()
        expanded = A | set(added)
        d = {"L": expanded if leg == "L" else companion,
             "S": companion if leg == "L" else expanded}
        graph = PartsGraph.from_decomposition(d, leg)
        cfg = FineConfig(working=leg, max_degree=3 if leg == "L" else 4,
                         workers=4, max_checks=max_checks, grouped=True,
                         current_min=len(A))
        search = FineSearch(graph, cfg)
        baseline = search.baseline_check()
        hyper = search.discover_hyperedges()
        candidates2, minima = search.reduce(hyper)
        wall = time.perf_counter() - started
        counts = ",".join(f"{k}:{len(v)}" for k, v in hyper.items())
        log((datetime.datetime.now().isoformat(timespec="seconds"), leg,
             label, len(expanded), cfg.max_degree, counts,
             len(candidates2), search.check_count,
             ",".join(str(len(x)) for x in minima) or "-",
             f"{wall:.1f}s", baseline.status))
        print(leg, label, "|W|", len(expanded), counts,
              "phase2", len(candidates2), "minima",
              [len(x) for x in minima], "wall", round(wall, 1), flush=True)
        if minima:
            # A is the union of all minimal graphs, as in Parts' outer loop.
            A = set().union(*(set(graph.ring_points["W"][i] for i in m)
                              for m in minima))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=("L", "S"), required=True)
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--max-checks", type=int, default=3000)
    args = ap.parse_args()
    run_leg(args.leg, args.limit, args.max_checks)

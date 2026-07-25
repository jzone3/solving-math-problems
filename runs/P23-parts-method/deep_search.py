#!/usr/bin/env python3
"""Untruncated phase-2 reduction for a screened greedy expansion."""
import argparse
import datetime
import os
import pickle
import time

from finesearch import FineConfig, FineSearch
from mring import orbit
from sat_parts import PartsGraph

HERE = os.path.dirname(os.path.abspath(__file__))


def note(row):
    with open(os.path.join(HERE, "NOTES.md"), "a") as f:
        f.write("| " + " | ".join(map(str, row)) + " |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=("L", "S"), required=True)
    ap.add_argument("--max-degree", type=int, required=True)
    ap.add_argument("--reps", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    reps = [tuple(map(int, x.split(","))) for x in args.reps]
    d = pickle.load(open(os.path.join(HERE, "decomp509.pkl"), "rb"))
    expanded = set(d[args.leg])
    for rep in reps:
        expanded.update(orbit(rep))
    data = {"L": expanded if args.leg == "L" else d["L"],
            "S": d["S"] if args.leg == "L" else expanded}
    graph = PartsGraph.from_decomposition(data, args.leg)
    note((datetime.datetime.now().isoformat(timespec="seconds"), args.leg,
          f"deep-start {reps}", len(graph.W), args.max_degree,
          "untruncated", "-", "-", "-", "RUNNING"))
    cfg = FineConfig(working=args.leg, max_degree=args.max_degree,
                     workers=args.workers, max_checks=None, grouped=True,
                     current_min=len(d[args.leg]))
    search = FineSearch(graph, cfg)
    started = time.perf_counter()
    hyper = search.discover_hyperedges()
    candidates, minima = search.reduce(hyper)
    wall = time.perf_counter() - started
    print(args.leg, reps, {k: len(v) for k, v in hyper.items()},
          len(candidates), [len(m) for m in minima], search.check_count,
          round(wall, 1), flush=True)
    note((datetime.datetime.now().isoformat(timespec="seconds"), args.leg,
          f"deep-done {reps}", len(graph.W), args.max_degree,
          ",".join(f"{k}:{len(v)}" for k, v in hyper.items()),
          len(candidates), search.check_count,
          f"{wall:.1f}s", "COMPLETE"))


if __name__ == "__main__":
    main()

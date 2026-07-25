#!/usr/bin/env python3
"""Greedy multi-orbit expansion using the corrected freed-vertex objective."""
import argparse
import datetime
import os
import pickle
import time

from mring import orbit
from screening import append_note, screen_one

HERE = os.path.dirname(os.path.abspath(__file__))

S_REPS = [(12, 2, 2, 0), (6, 2, 4, 0), (1, 1, 3, 5),
          (4, 0, 2, 2), (6, 0, 4, 6), (2, 0, 4, 2),
          (12, 0, 2, 6), (0, 0, 6, 6)]
L_REPS = [(4, 0, 4, 4), (1, 1, 3, 5), (2, 0, 2, 4),
          (10, 0, 8, 2), (6, 2, 4, 0), (6, 2, 8, 0)]


def run(leg, workers, steps):
    d = pickle.load(open(os.path.join(HERE, "decomp509.pkl"), "rb"))
    reps = S_REPS if leg == "S" else L_REPS
    start = (6, 2, 4, 0)
    selected = [start]
    for step in range(steps):
        best = None
        for rep in reps:
            if rep in selected:
                continue
            additions = [orbit(x) for x in selected + [rep]]
            started = time.perf_counter()
            graph, baseline, indispensable, checks, freed = screen_one(
                d, leg, additions, workers)
            freed_count = len(d[leg]) - indispensable
            wall = time.perf_counter() - started
            label = f"greedy{step+1} {tuple(selected + [rep])}"
            append_note((datetime.datetime.now().isoformat(timespec="seconds"),
                         leg, label, len(graph.W),
                         f"indispensable={indispensable};freed={freed_count}",
                         indispensable, checks, f"{wall:.1f}s",
                         baseline.status))
            print(leg, label, "freed", freed_count, flush=True)
            if baseline.status == "UNSAT" and (
                    best is None or freed_count > best[0]):
                best = (freed_count, rep)
        if best is None:
            break
        selected.append(best[1])
        print(leg, "selected", selected, "freed", best[0], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=("L", "S"), required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--steps", type=int, default=2)
    args = ap.parse_args()
    run(args.leg, args.workers, args.steps)

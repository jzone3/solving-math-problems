#!/usr/bin/env python3
"""Cheap expansion screen: count old vertices freed by each expansion."""
import argparse
import datetime
import itertools
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor

from finesearch import FineConfig, FineSearch, expansion_reserve
from mring import orbit
from sat_parts import PartsGraph

HERE = os.path.dirname(os.path.abspath(__file__))
DECOMP = os.path.join(HERE, "decomp509.pkl")
NOTES = os.path.join(HERE, "NOTES.md")


def append_note(row):
    with open(NOTES, "a") as f:
        f.write("| " + " | ".join(map(str, row)) + " |\n")


def screen_one(decomp, leg, additions, workers=4, timeout=None):
    old = set(decomp[leg])
    expanded = old | set().union(*additions)
    other = decomp["S" if leg == "L" else "L"]
    data = {"L": expanded if leg == "L" else other,
            "S": other if leg == "L" else expanded}
    graph = PartsGraph.from_decomposition(data, leg)
    template = graph.template()
    baseline = template.solve(graph.W, timeout=timeout)
    if baseline.status != "UNSAT":
        return graph, baseline, len(old), 0, []

    def check(v):
        active = set(graph.W) - {graph.ring_points["W"].index(v)}
        return template.solve(active, timeout=timeout)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(check, sorted(old)))
    indispensable = [v for v, result in zip(sorted(old), results)
                     if result.status == "SAT"]
    freed = [v for v, result in zip(sorted(old), results)
             if result.status == "UNSAT"]
    return graph, baseline, len(indispensable), len(results), freed


def full_search(graph, leg, max_degree, workers, max_checks):
    cfg = FineConfig(working=leg, max_degree=max_degree, workers=workers,
                     max_checks=max_checks, grouped=True,
                     current_min=len(graph.W))
    search = FineSearch(graph, cfg)
    hyper = search.discover_hyperedges()
    candidates, minima = search.reduce(hyper)
    return hyper, candidates, minima, search.check_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=("L", "S"), required=True)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=None)
    ap.add_argument("--full-checks", type=int, default=1000)
    ap.add_argument("--no-combos", action="store_true")
    ap.add_argument("--screen-only", action="store_true")
    args = ap.parse_args()
    d = pickle.load(open(DECOMP, "rb"))
    base = set(d[args.leg])
    reserve = expansion_reserve(base)
    singles = [(rep, vertices) for score, size, rep, vertices in reserve
               if vertices - base][:args.top]
    rows = []
    ranked = []
    for rep, vertices in singles:
        started = time.perf_counter()
        graph, baseline, score, checks, freed = screen_one(
            d, args.leg, [vertices], args.workers, args.timeout)
        wall = time.perf_counter() - started
        old_count = len(base)
        freed_count = old_count - score
        row = (datetime.datetime.now().isoformat(timespec="seconds"),
               args.leg, f"screen {rep}", len(graph.W),
               f"indispensable={score};freed={old_count-score}",
               score, checks, f"{wall:.1f}s", baseline.status)
        append_note(row)
        print(row, "freed", freed_count, flush=True)
        ranked.append((score, rep, freed_count))
        if freed_count > 0 and not args.screen_only:
            hyper, candidates, minima, nchecks = full_search(
                graph, args.leg, 3 if args.leg == "L" else 4,
                args.workers, args.full_checks)
            print("FULL", rep, {k: len(v) for k, v in hyper.items()},
                  len(candidates), [len(m) for m in minima], nchecks,
                  flush=True)
    print("RANKED_SINGLES", sorted(ranked), flush=True)
    if args.no_combos:
        return
    # Pair/triple screen among the best reserve-ranked singles.
    combo_ranked = []
    for degree in (2, 3):
        for combo in itertools.combinations(singles, degree):
            reps = tuple(x[0] for x in combo)
            vertices = [x[1] for x in combo]
            started = time.perf_counter()
            graph, baseline, score, checks, freed = screen_one(
                d, args.leg, vertices, args.workers, args.timeout)
            wall = time.perf_counter() - started
            old_count = len(base)
            freed_count = old_count - score
            row = (datetime.datetime.now().isoformat(timespec="seconds"),
                   args.leg, f"screen {reps}", len(graph.W),
                   f"indispensable={score};freed={old_count-score}",
                   score, checks, f"{wall:.1f}s", baseline.status)
            append_note(row)
            print(row, "freed", freed_count, flush=True)
            combo_ranked.append((score, reps, freed_count))
            if freed_count > 0 and not args.screen_only:
                hyper, candidates, minima, nchecks = full_search(
                    graph, args.leg, 3 if args.leg == "L" else 4,
                    args.workers, args.full_checks)
                print("FULL", reps, {k: len(v) for k, v in hyper.items()},
                      len(candidates), [len(m) for m in minima], nchecks,
                      flush=True)
    print("RANKED_COMBOS", sorted(combo_ranked), flush=True)


if __name__ == "__main__":
    main()

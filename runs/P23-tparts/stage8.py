# Provenance: Stage-8 alternating descent combining stage5.py and stage7.py.
"""Uncapped alternating A/B descent for the best Stage-7 witnesses."""

from __future__ import annotations

import argparse
import pickle
import time
from collections import Counter

import cegar
import stage5
import stage7


def load_case(cache, initial_ids, pattern_pickle):
    points, labels, metadata, a_pool, b_pool, _, _ = cegar.side_sets(
        cache, "full"
    )
    b_edges, cross = cegar.split_edges(labels, metadata)
    raw_ids = pickle.load(open(initial_ids, "rb"))
    if isinstance(raw_ids, dict):
        L, S = set(raw_ids["L"]), set(raw_ids["S"])
    else:
        raise ValueError("initial_ids must be a dict with L and S")
    raw_patterns = pickle.load(open(pattern_pickle, "rb"))
    if isinstance(raw_patterns, dict):
        patterns = list(raw_patterns["patterns"])
    elif isinstance(raw_patterns, list) and raw_patterns and isinstance(
        raw_patterns[0], dict
    ):
        patterns = list(raw_patterns[0]["patterns"])
    else:
        patterns = list(raw_patterns)
    return points, labels, a_pool, b_edges, cross, L, S, patterns


def run(cache, initial_ids, pattern_pickle, rounds, seed, batch):
    points, labels, a_pool, b_edges, cross, L, S, patterns = load_case(
        cache, initial_ids, pattern_pickle
    )
    a_edges = labels["AA"]
    trajectory = []
    best = (len(L) + len(S), set(L), set(S), list(patterns))
    for rno in range(rounds):
        started = time.time()
        patterns = stage5.valid_patterns(S, b_edges, cross, patterns)
        if not patterns:
            trajectory.append({
                "round": rno, "status": "NO_VALID_PATTERNS",
                "A": len(L), "B": len(S),
            })
            break

        preserve = {v for vs, _ in patterns for v in vs}
        L, a_hist = stage7.core_jump(
            L, a_edges, patterns, preserve, seed=seed + rno
        )
        patterns, pstatus = stage5.prune_patterns_a(L, a_edges, patterns)
        before_b = len(S)
        S, removed_core = stage5.stage4.b_core_reduce(
            S, b_edges, cross, patterns
        )
        S, removed_greedy = stage5.b_greedy_batches(
            S, b_edges, cross, patterns, seed=seed + rno,
            batch=batch, repair=True,
        )
        refreshed = stage5.valid_patterns(S, b_edges, cross, patterns)
        if not refreshed:
            status = "PATTERNS_LOST"
            patterns = refreshed
        else:
            L, patterns, _, status = cegar.run_cegar(
                L, S, a_pool, a_edges, b_edges, cross, refreshed
            )
        total = len(L) + len(S)
        row = {
            "round": rno,
            "status": status,
            "A": len(L),
            "B": len(S),
            "total": total,
            "patterns": len(patterns),
            "orders": dict(Counter(len(vs) for vs, _ in patterns)),
            "pattern_core": pstatus,
            "A_history": a_hist,
            "removed_core": removed_core,
            "removed_greedy": removed_greedy,
            "B_before": before_b,
            "seconds": time.time() - started,
        }
        trajectory.append(row)
        print(row, flush=True)
        if total < best[0]:
            best = (total, set(L), set(S), list(patterns))
        if status != "UNSAT":
            break
        if rno and total >= trajectory[-2]["total"]:
            break
    return {
        "L": sorted(best[1]),
        "S": sorted(best[2]),
        "patterns": best[3],
        "trajectory": trajectory,
        "best_total": best[0],
        "seed": seed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("initial_ids")
    ap.add_argument("patterns")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run(
        args.cache, args.initial_ids, args.patterns,
        args.rounds, args.seed, args.batch,
    )
    pickle.dump(result, open(args.out, "wb"), protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Parts-expanded graph minimization using the legacy SAT-core/greedy engine."""
import argparse
import os
import pickle
import random
import sys
import time

FUSION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "P23-fusion1")
sys.path.insert(0, FUSION)


def minimize(pool, start, fixed, seed, timeout, output, log):
    os.environ["POOL"] = os.path.abspath(pool)
    from hybrid_core import solve_core
    points, _ = pickle.load(open(pool, "rb"))
    fixed = set(fixed)
    variable = set(start) - fixed
    active = set(start)
    rng = random.Random(seed)
    iteration = 0

    while True:
        iteration += 1
        began = time.perf_counter()
        status, core = solve_core(active, seed=seed * 1000 + iteration,
                                   timeout=timeout, tag=f"hy{seed}")
        elapsed = time.perf_counter() - began
        if status != "UNSAT":
            print(f"seed={seed} core={status} n={len(active)} "
                  f"elapsed={elapsed:.1f}s", file=log, flush=True)
            break
        core |= fixed
        print(f"seed={seed} core {len(active)} -> {len(core)} "
              f"elapsed={elapsed:.1f}s", file=log, flush=True)
        if len(core) >= len(active):
            active = core
            break
        active = core
        variable = active - fixed

    passes = 0
    while True:
        passes += 1
        removed = 0
        order = sorted(active - fixed)
        rng.shuffle(order)
        for vertex in order:
            candidate = active - {vertex}
            status, core = solve_core(candidate, seed=rng.randrange(10**9),
                                       timeout=timeout, tag=f"hy{seed}")
            if status == "UNSAT":
                active = core | fixed
                removed += 1
                print(f"seed={seed} pass={passes} delete={vertex} "
                      f"n={len(active)}", file=log, flush=True)
        print(f"seed={seed} pass={passes} removed={removed} "
              f"n={len(active)}", file=log, flush=True)
        if removed == 0:
            break

    pickle.dump(sorted(active), open(output, "wb"))
    print(f"seed={seed} FINAL {len(active)}", file=log, flush=True)
    return active


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--start", required=True,
                    help="pickle containing initial active indices")
    ap.add_argument("--fixed", required=True,
                    help="pickle containing indices that must remain active")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    minimize(args.pool,
             pickle.load(open(args.start, "rb")),
             pickle.load(open(args.fixed, "rb")),
             args.seed, args.timeout, args.output, sys.stdout)


if __name__ == "__main__":
    main()

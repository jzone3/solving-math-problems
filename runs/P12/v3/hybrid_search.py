#!/usr/bin/env python3
"""Algebraic attack part 4: algebraic seeds + free DFS completion.

Since fully-algebraic (symmetric / polynomial-orbit) T2(p) are provably or
empirically dead, try 'mostly algebraic' squares: pick a small compatible set
of polynomial-pool rows as a seed, then complete the remaining rows with the
generic pruned DFS (randomized restarts, per-seed time budget).

Usage: hybrid_search.py p total_seconds [seed_rows] [rng_seed]
Logs best depth reached; a full solution is written to found_p<p>.txt.
"""
import random
import sys
import time

sys.path.insert(0, ".")
from t2lib import dfs_t2, compatible_partial, check_t2
from poly_pool import build_pool


def main():
    p = int(sys.argv[1])
    total = float(sys.argv[2])
    k = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 12345)
    pool = build_pool(p)
    print(f"p={p} pool={len(pool)} seed_rows={k}", flush=True)
    t0 = time.time()
    best_overall = 0
    tries = 0
    while time.time() - t0 < total:
        tries += 1
        seed = []
        attempts = 0
        while len(seed) < k and attempts < 200:
            attempts += 1
            r = list(rng.choice(pool))
            if compatible_partial(seed + [r], p):
                seed.append(r)
        stats = {}
        sol = dfs_t2(p, fixed_rows=seed, time_budget=20, rng=rng, stats=stats)
        b = stats.get("best", len(seed))
        if b > best_overall:
            best_overall = b
            print(f"[{time.time()-t0:.0f}s] try {tries}: new best {b}/{p}", flush=True)
            if b >= p - 1 and stats.get("rows"):
                for r in stats["rows"]:
                    print("   ", r, flush=True)
        if sol:
            print("SOLUTION FOUND", flush=True)
            assert check_t2(sol, p)
            with open(f"found_p{p}.txt", "w") as f:
                for r in sol:
                    f.write(" ".join(map(str, r)) + "\n")
            return
    print(f"done: {tries} seeds, best {best_overall}/{p}", flush=True)


if __name__ == "__main__":
    main()

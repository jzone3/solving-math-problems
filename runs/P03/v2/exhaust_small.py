"""Phase-2 exhaustive check: Woodall for ALL weakly-connected simple
digraphs (2-cycles allowed) on n <= 6 vertices, via nauty:

    nauty-geng -c <n> | nauty-directg -T | python3 exhaust_small.py <n>

directg -T lines: "n m  u v u v ...".  For each digraph: dicuts via lower
sets of the condensation; skip tau <= 1 (trivial); ACZ rho shortcut
(rho <= 2, or rho = tau <= 3 with w=1 => packs); randomized greedy; exact
CBC ILP for greedy-resistant instances.
"""
import random
import sys
import time

import core
from search_general import dicut_masks, minimal_masks, greedy_pack


def main(tag):
    rng = random.Random(12345)
    stats = {"read": 0, "tau_ge2": 0, "rho_short": 0, "greedy": 0,
             "ilp": 0, "FAILURES": 0}
    t0 = time.time()
    for line in sys.stdin:
        parts = line.split()
        if not parts or not parts[0].isdigit():
            continue
        stats["read"] += 1
        n, m = int(parts[0]), int(parts[1])
        vals = list(map(int, parts[2:]))
        arcs = list(zip(vals[::2], vals[1::2]))
        assert len(arcs) == m
        masks = dicut_masks(n, arcs)
        if not masks:
            continue
        t = min(bin(x).count("1") for x in masks)
        if t < 2:
            continue
        stats["tau_ge2"] += 1
        r = core.rho(n, arcs, t)
        if r <= 2 or (t == 3 and r == 3):
            stats["rho_short"] += 1
            continue
        mmin = minimal_masks(masks)
        if greedy_pack(mmin, m, t, rng, tries=40):
            stats["greedy"] += 1
            continue
        stats["ilp"] += 1
        cuts = [frozenset(i for i in range(m) if (x >> i) & 1)
                for x in mmin]
        ok = core.packing_exists(n, arcs, t, cuts=cuts, time_limit=600)
        if not ok:
            stats["FAILURES"] += 1
            print("!!! EXHAUSTIVE FAILURE:", n, arcs, t, flush=True)
        if stats["read"] % 200000 == 0:
            print(f"[exhaust {tag}] {stats} {time.time()-t0:.0f}s",
                  flush=True)
    print(f"FINAL [exhaust {tag}] {stats} {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "?")

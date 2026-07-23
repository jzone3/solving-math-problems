"""Exact ILP certification of C-checker survivor lines (directg -T format).
Usage: python3 ilp_survivors.py surv_*.txt
"""
import sys

import core
from search_general import dicut_masks, minimal_masks


def main(paths):
    tested = failures = 0
    for path in paths:
        for line in open(path):
            parts = line.split()
            if not parts:
                continue
            n, m = int(parts[0]), int(parts[1])
            vals = list(map(int, parts[2:]))
            arcs = list(zip(vals[::2], vals[1::2]))
            assert len(arcs) == m
            masks = dicut_masks(n, arcs)
            t = min(bin(x).count("1") for x in masks)
            mmin = minimal_masks(masks)
            cuts = [frozenset(i for i in range(m) if (x >> i) & 1)
                    for x in mmin]
            ok = core.packing_exists(n, arcs, t, cuts=cuts, time_limit=600)
            tested += 1
            if not ok:
                failures += 1
                print("!!! FAILURE:", n, arcs, "tau", t, flush=True)
            if tested % 200 == 0:
                print(f"tested={tested} failures={failures}", flush=True)
    print(f"ILP-SURVIVORS FINAL tested={tested} failures={failures}",
          flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])

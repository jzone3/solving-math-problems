#!/usr/bin/env python3
"""Independent exhaustive nonexistence checker for (v,k)-PMDs.

Deliberately different from pmd_dlx.c: pure Python, no dancing links.
Backtracking on blocks: at each step take the lexicographically smallest
ordered pair (x,y) not yet covered at distance 1, and branch over every
cyclic block (x, y, z1, ..., z_{k-2}) (fixed to start at x,y — each cyclic
block containing x->y adjacent has exactly one such representation) whose
full coverage set (all distances 1..k-1) is disjoint from what is covered.
This is a complete search: every PMD contains exactly one block covering
each distance-1 pair, so the search tree contains every PMD exactly once.

Usage: exhaust_indep.py v k [--first-block]
  --first-block: additionally require the block starting (0,1,...) chosen for
  pair (0,1) to be exactly (0,1,2,...,k-1) — a WLOG relabelling restriction.
Prints the number of solutions found (existence oracle: >0 means exists).
"""
import sys
from itertools import permutations

def main():
    v, k = int(sys.argv[1]), int(sys.argv[2])
    first_block = "--first-block" in sys.argv
    b = v * (v - 1) // k
    covered = set()  # (d, x, y)
    nsol = 0
    nodes = 0

    def block_pairs(blk):
        out = []
        for d in range(1, k):
            for i in range(k):
                out.append((d, blk[i], blk[(i + d) % k]))
        return out

    def next_uncovered():
        for x in range(v):
            for y in range(v):
                if x != y and (1, x, y) not in covered:
                    return (x, y)
        return None

    def rec(depth, blocks):
        nonlocal nsol, nodes
        nodes += 1
        pr = next_uncovered()
        if pr is None:
            assert depth == b
            nsol += 1
            print("SOLUTION:", blocks)
            return
        x, y = pr
        rest = [z for z in range(v) if z != x and z != y]
        for tail in permutations(rest, k - 2):
            blk = (x, y) + tail
            if first_block and depth == 0 and blk != tuple(range(k)):
                continue
            prs = block_pairs(blk)
            if len(set(prs)) != len(prs):
                continue
            if any(p in covered for p in prs):
                continue
            covered.update(prs)
            rec(depth + 1, blocks + [blk])
            covered.difference_update(prs)

    rec(0, [])
    print(f"v={v} k={k} solutions={nsol} nodes={nodes}")

if __name__ == "__main__":
    main()

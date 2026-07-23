#!/usr/bin/env python3
"""Third independent nonexistence check for (v,6,1)-PMDs: exhaustive exact-cover DFS.

A (v,6,1)-PMD's blocks partition the 72 ordered distance-1 pairs (for v=9) into
b groups of 6, while also exactly covering every (pair, distance-t) slot for
t=2..5. Algorithm-X style search: repeatedly take the lexicographically first
uncovered distance-1 pair and branch over all blocks that cover it and conflict
with nothing chosen so far. Enumerates every design exactly once (as a set of
blocks); WLOG (relabeling) the block (0,1,..,5) is forced first.

Blocks are represented canonically (min element first). Slot universe:
slot(t,u,w) for t=1..5. Conflict test = bitmask AND.

Usage: pmd_dfs.py v   (practical for v=9; prints SOLUTION or 'UNSAT (exhausted)')
"""
import sys
from itertools import permutations

K = 6


def main(v):
    npairs = v * v

    def slot(t, u, w):
        return (t - 1) * npairs + u * v + w

    # all canonical blocks and their slot masks
    blocks = []
    syms = range(v)
    for rest in permutations(syms, K):
        if rest[0] != min(rest):
            continue
        mask = 0
        for t in range(1, K):
            for p in range(K):
                mask |= 1 << slot(t, rest[p], rest[(p + t) % K])
        blocks.append((rest, mask))
    # index blocks by each distance-1 pair they cover
    by_pair = {}
    for idx, (tup, mask) in enumerate(blocks):
        for p in range(K):
            by_pair.setdefault((tup[p], tup[(p + 1) % K]), []).append(idx)
    b_needed = v * (v - 1) // K
    all_d1 = [(u, w) for u in range(v) for w in range(v) if u != w]

    first = tuple(range(K))
    first_idx = next(i for i, (tup, _) in enumerate(blocks) if tup == first)
    chosen = [first]
    used = blocks[first_idx][1]
    nodes = 0

    def first_uncovered(used):
        for (u, w) in all_d1:
            if not (used >> slot(1, u, w)) & 1:
                return (u, w)
        return None

    def dfs(used, depth):
        nonlocal nodes
        nodes += 1
        if depth == b_needed:
            return True
        pair = first_uncovered(used)
        if pair is None:
            return False  # all d1 covered but too few blocks: impossible anyway
        for idx in by_pair[pair]:
            m = blocks[idx][1]
            if used & m:
                continue
            chosen.append(blocks[idx][0])
            if dfs(used | m, depth + 1):
                return True
            chosen.pop()
        return False

    if dfs(used, 1):
        print("SOLUTION")
        for tup in chosen:
            print(" ".join(map(str, tup)))
    else:
        print(f"UNSAT (exhausted search, {nodes} nodes)")


if __name__ == "__main__":
    main(int(sys.argv[1]))

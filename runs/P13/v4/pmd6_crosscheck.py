#!/usr/bin/env python3
"""Independent (second-implementation) exhaustive search for (v,6)-PMD.

Written separately from pmd6_search.c with different data structures, to
cross-check UNSAT claims.  Uses a set of covered (t,x,y) triples and a
different branching heuristic: it branches on the uncovered distance-1 pair
(x,y) with x of MAXIMUM remaining distance-1 out-degree deficiency ties broken
lexicographically -- i.e. a deliberately different node ordering from the C
searcher (which always picks the lexicographically smallest pair).

WLOG the first block is (0,1,2,3,4,5) (point relabeling maps any block there).

Usage: pmd6_crosscheck.py v
Prints SOLUTION ... or UNSAT, plus node count.
"""
import sys
from itertools import permutations

K = 6

def solve(v):
    b = v * (v - 1) // K
    covered = set()  # (t, x, y)
    blocks = []
    nodes = 0

    def mark(blk, add):
        for t in range(1, K):
            for i in range(K):
                trip = (t, blk[i], blk[(i + t) % K])
                if add:
                    covered.add(trip)
                else:
                    covered.remove(trip)

    def can_place(blk, z):
        p = len(blk)
        for q, e in enumerate(blk):
            d = p - q
            if (d, e, z) in covered or (K - d, z, e) in covered:
                return False
        return True

    first = (0, 1, 2, 3, 4, 5)
    mark(first, True)
    blocks.append(first)

    def pick_pair():
        # uncovered distance-1 pair whose x has the most uncovered out-slots
        best = None
        bestdef = -1
        for x in range(v):
            deficiency = sum(1 for y in range(v) if x != y and (1, x, y) not in covered)
            if deficiency > bestdef:
                for y in range(v):
                    if x != y and (1, x, y) not in covered:
                        best = (x, y)
                        bestdef = deficiency
                        break
        return best

    def rec():
        nonlocal nodes
        nodes += 1
        if len(blocks) == b:
            return list(blocks)
        pair = pick_pair()
        if pair is None:
            return None
        x, y = pair
        blk = [x, y]
        used = {x, y}

        def extend():
            if len(blk) == K:
                t = tuple(blk)
                mark(t, True)
                blocks.append(t)
                r = rec()
                blocks.pop()
                mark(t, False)
                return r
            for z in range(v):
                if z in used or not can_place(blk, z):
                    continue
                blk.append(z)
                used.add(z)
                r = extend()
                blk.pop()
                used.discard(z)
                if r:
                    return r
            return None

        return extend()

    sol = rec()
    return sol, nodes


if __name__ == "__main__":
    v = int(sys.argv[1])
    sol, nodes = solve(v)
    if sol:
        print(f"SOLUTION v={v} k={K} b={v*(v-1)//K}")
        for blk in sol:
            print(" ".join(map(str, blk)))
    else:
        print(f"UNSAT v={v} k={K} b={v*(v-1)//K} (exhaustive, first block fixed WLOG)")
    print(f"nodes={nodes}")

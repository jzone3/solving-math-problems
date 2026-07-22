#!/usr/bin/env python3
"""Independent verifier for a claimed Sheehan counterexample (P01).

Usage: python3 verify.py witness.json
witness.json: {"n": <int>, "edges": [[u,v], ...]}

Checks, with no external dependencies:
  1. graph is simple (no loops / parallel edges), on n vertices;
  2. every vertex has degree exactly 4;
  3. the graph has EXACTLY ONE Hamiltonian cycle (exact count by
     memoized DP over (visited-set, endpoint) states, anchored at vertex 0).

Prints PASS iff all checks hold; FAIL otherwise. Exit code 0 on PASS.
"""
import json
import sys
from functools import lru_cache


def count_hamiltonian_cycles(n, adjmask):
    """Exact HC count (undirected, so each cycle counted once).
    DP over subsets: paths starting at 0, state (mask, last). To count each
    undirected cycle once, require the neighbor of 0 chosen first to be the
    smaller-indexed of the two cycle-neighbors of 0: we count directed cycles
    and divide by 2 at the end.
    """
    full = (1 << n) - 1

    sys.setrecursionlimit(10000)

    @lru_cache(maxsize=None)
    def paths(mask, last):
        # number of ways to extend a path 0..last (visited=mask) into a
        # directed Hamiltonian cycle back to 0
        if mask == full:
            return 1 if (adjmask[last] >> 0) & 1 else 0
        total = 0
        cand = adjmask[last] & ~mask
        while cand:
            b = cand & -cand
            w = b.bit_length() - 1
            cand ^= b
            total += paths(mask | b, w)
        return total

    directed = paths(1, 0)
    assert directed % 2 == 0
    return directed // 2


def main():
    with open(sys.argv[1]) as f:
        w = json.load(f)
    n = w["n"]
    edges = set()
    for u, v in w["edges"]:
        if not (0 <= u < n and 0 <= v < n) or u == v:
            print("FAIL: bad edge", (u, v))
            return 1
        e = (min(u, v), max(u, v))
        if e in edges:
            print("FAIL: parallel edge", e)
            return 1
        edges.add(e)

    deg = [0] * n
    adjmask = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        adjmask[u] |= 1 << v
        adjmask[v] |= 1 << u
    if any(d != 4 for d in deg):
        print("FAIL: not 4-regular; degrees:", sorted(set(deg)))
        return 1

    cnt = count_hamiltonian_cycles(n, adjmask)
    print(f"n={n}, edges={len(edges)}, hamiltonian_cycle_count={cnt}")
    if cnt == 1:
        print("PASS")
        return 0
    print("FAIL: HC count != 1")
    return 1


if __name__ == "__main__":
    sys.exit(main())

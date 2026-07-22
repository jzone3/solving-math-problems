#!/usr/bin/env python3
"""Independent verifier for a claimed P05 counterexample (Gallai three longest paths).

Usage: python3 verify.py witness.json

witness.json format:
  {"adj": [[neighbors of 0], [neighbors of 1], ...],
   "paths": [[v0, v1, ...], [..], [..]]}   # three vertex sequences

Checks (all independent of the search code, plain recursion, no bitmask tricks):
  1. adj is a simple undirected connected graph.
  2. each of the 3 paths is a simple path in the graph.
  3. the three paths are pairwise distinct.
  4. every longest path in the graph has exactly len(paths[i]) vertices
     (i.e. the given paths ARE longest paths) — via exhaustive DFS.
  5. the three paths have NO common vertex.
Prints PASS if all hold, otherwise FAIL with the reason.
"""
import json, sys
sys.setrecursionlimit(100000)


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def main():
    w = json.load(open(sys.argv[1]))
    adj = [list(x) for x in w["adj"]]
    paths = [list(p) for p in w["paths"]]
    n = len(adj)

    # 1. simple undirected connected
    for v in range(n):
        if v in adj[v]:
            fail(f"self-loop at {v}")
        if len(set(adj[v])) != len(adj[v]):
            fail(f"multi-edge at {v}")
        for u in adj[v]:
            if not (0 <= u < n) or v not in adj[u]:
                fail(f"asymmetric/invalid edge {v}-{u}")
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    if len(seen) != n:
        fail("graph not connected")

    # 2-3. valid distinct simple paths
    if len(paths) != 3:
        fail("need exactly 3 paths")
    for p in paths:
        if len(set(p)) != len(p):
            fail("path repeats a vertex")
        for a, b in zip(p, p[1:]):
            if b not in adj[a]:
                fail(f"non-edge {a}-{b} used in a path")
    norm = {tuple(min(tuple(p), tuple(reversed(p)))) for p in paths}
    if len(norm) != 3:
        fail("paths not pairwise distinct")
    lens = {len(p) for p in paths}
    if len(lens) != 1:
        fail("paths have different lengths")
    L = lens.pop()

    # 4. exhaustive longest path (independent DFS, set-based)
    best = [0]

    def dfs(v, used, ln):
        if ln > best[0]:
            best[0] = ln
        for u in adj[v]:
            if u not in used:
                used.add(u)
                dfs(u, used, ln + 1)
                used.remove(u)

    for s in range(n):
        dfs(s, {s}, 1)
    if best[0] != L:
        fail(f"claimed paths have {L} vertices but longest path has {best[0]}")

    # 5. empty triple intersection
    common = set(paths[0]) & set(paths[1]) & set(paths[2])
    if common:
        fail(f"paths share vertices {sorted(common)}")

    print("PASS")


if __name__ == "__main__":
    main()

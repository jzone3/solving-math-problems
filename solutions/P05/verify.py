#!/usr/bin/env python3
"""Standalone verifier (stdlib only) for the P05 V4 byproduct claim:

The 12-vertex graph G12 = graph6 'K?AA@BOX?[SO' is connected, its longest
paths have EMPTY total intersection (no vertex lies on all longest paths),
yet every THREE longest paths share a vertex (so it is NOT a counterexample
to Gallai's 3-longest-paths question).

Everything is recomputed from scratch here by naive exhaustive enumeration
of all simple paths. Prints PASS iff all checks succeed.
"""
from itertools import combinations

G6 = "K?AA@BOX?[SO"


def parse_graph6(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for c in data[1:]:
        bits.extend((c >> k) & 1 for k in range(5, -1, -1))
    adj = [set() for _ in range(n)]
    idx = 0
    for i in range(1, n):
        for j in range(i):
            if bits[idx]:
                adj[i].add(j)
                adj[j].add(i)
            idx += 1
    return n, adj


def main():
    n, adj = parse_graph6(G6)
    assert n == 12

    # connectivity
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    assert len(seen) == n, "graph not connected"

    # enumerate ALL simple paths, track longest
    best = [1]
    sets = set()

    def dfs(v, visited):
        if len(visited) > best[0]:
            best[0] = len(visited)
            sets.clear()
        if len(visited) == best[0]:
            sets.add(frozenset(visited))
        for u in adj[v]:
            if u not in visited:
                visited.add(u)
                dfs(u, visited)
                visited.remove(u)

    for v in range(n):
        dfs(v, {v})

    L = best[0]
    slist = list(sets)
    assert L == 10, f"expected longest path on 10 vertices, got {L}"

    # empty total intersection
    total = set(range(n))
    for s in slist:
        total &= s
    assert not total, f"total intersection nonempty: {total}"

    # every triple of longest paths shares a vertex
    for a, b, c in combinations(slist, 3):
        assert a & b & c, f"empty triple: {sorted(a)}, {sorted(b)}, {sorted(c)}"

    print(f"checked: n={n}, L={L} vertices, {len(slist)} longest-path vertex sets")
    print("empty total intersection: yes; every 3 longest paths intersect: yes")
    print("PASS")


if __name__ == "__main__":
    main()

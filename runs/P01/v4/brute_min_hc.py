#!/usr/bin/env python3
"""Validation brute force: enumerate all Hamiltonian 4-regular graphs on n vertices
as cycle C_n + chord 2-factor, count HCs exactly, report the minimum nonzero HC count
and whether any graph has exactly 1 HC. Compare minima with GMZ Table 3:
n=5:12, 6:16, 7:23... wait Table3 col girth>=3: n=5:12, 6:16, 7:23, 8:29, 9:36, 10:36, 11:48.
Note Table 3 row n corresponds to order n; check n in 8..11 here.
"""
import sys
from itertools import combinations

def count_hc(n, adj, cutoff=None):
    # count Hamiltonian cycles: fix start 0, go to neighbor > last neighbor to avoid double count
    count = 0
    full = (1 << n) - 1
    sys.setrecursionlimit(10000)
    def dfs(v, visited):
        nonlocal count
        if visited == full:
            if 0 in adj[v]:
                count += 1
            return count is not None and cutoff is not None and count >= cutoff
        for w in adj[v]:
            if not (visited >> w) & 1:
                if dfs(w, visited | (1 << w)):
                    return True
        return False
    # avoid counting each cycle twice: force second vertex < last vertex
    # simpler: count directed cycles through 0 then divide by 2
    def dfs2(v, visited):
        nonlocal count
        if visited == full:
            if 0 in adj[v]:
                count += 1
            return
        for w in adj[v]:
            if not (visited >> w) & 1:
                dfs2(w, visited | (1 << w))
    dfs2(0, 1)
    assert count % 2 == 0
    return count // 2

def chord_2factors(n):
    """All 2-regular graphs on {0..n-1} whose edges avoid cycle edges (i,i+1 mod n)."""
    verts = list(range(n))
    def allowed(u, v):
        d = abs(u - v)
        return d != 1 and d != n - 1
    def rec(deg, edges, start):
        # find first vertex with deg<2
        v = next((x for x in verts if deg[x] < 2), None)
        if v is None:
            yield list(edges)
            return
        for u in range(v + 1, n):
            if deg[u] < 2 and allowed(v, u) and (v, u) not in edges:
                deg[v] += 1; deg[u] += 1; edges.add((v, u))
                yield from rec(deg, edges, v)
                deg[v] -= 1; deg[u] -= 1; edges.remove((v, u))
    yield from rec({v: 0 for v in verts}, set(), 0)

def main():
    for n in [int(a) for a in sys.argv[1:]]:
        best = None
        ones = 0
        total = 0
        for chords in chord_2factors(n):
            total += 1
            adj = [[(i - 1) % n, (i + 1) % n] for i in range(n)]
            for u, v in chords:
                adj[u].append(v); adj[v].append(u)
            c = count_hc(n, adj)
            assert c >= 1
            if c == 1:
                ones += 1
                print("UNIQUELY HAMILTONIAN FOUND", n, chords)
            if best is None or c < best:
                best = c
        print(f"n={n}: chord-2-factors={total}, min HC={best}, uniquely_ham={ones}")

if __name__ == "__main__":
    main()

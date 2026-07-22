#!/usr/bin/env python3
"""Independent brute-force cross-check for the Gallai 3-longest-paths property.

Reads graph6 lines on stdin. For each graph, enumerates ALL simple paths
naively, finds the longest length, collects all longest-path vertex sets,
and checks whether every triple of longest paths has a common vertex.
Prints per-graph: <graph6> L=<vertices> nsets=<k> gallai3=<OK|FAIL>
Slow; intended for cross-validating gallai_check.c on samples.
"""
import sys
from itertools import combinations


def parse_graph6(s):
    data = [ord(c) - 63 for c in s.strip()]
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


def all_longest_path_sets(n, adj):
    best = [1]
    sets = set()

    def dfs(v, visited, order_len):
        if order_len > best[0]:
            best[0] = order_len
            sets.clear()
        if order_len == best[0]:
            sets.add(frozenset(visited))
        for u in adj[v]:
            if u not in visited:
                visited.add(u)
                dfs(u, visited, order_len + 1)
                visited.remove(u)

    for v in range(n):
        dfs(v, {v}, 1)
    return best[0], sets


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, adj = parse_graph6(line)
        L, sets = all_longest_path_sets(n, adj)
        ok = True
        slist = list(sets)
        for a, b, c in combinations(slist, 3):
            if not (a & b & c):
                ok = False
                break
        print(f"{line} L={L} nsets={len(slist)} gallai3={'OK' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()

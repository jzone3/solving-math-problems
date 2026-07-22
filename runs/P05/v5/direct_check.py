#!/usr/bin/env python3
"""Direct (reduction-free) checker: build the 3-arm spider from a core graph
H + triple (a,b,c) and verify by brute force what the min triple intersection
of longest paths is in the actual spider graph.

Usage: direct_check.py <graph6> <a> <b> <c>
Enumerates ALL longest paths of the spider, then finds the minimum
|P1 & P2 & P3| over all triples of longest paths (early exit at 0).
"""
import sys
from itertools import combinations


def parse_graph6(line):
    data = [ord(ch) - 63 for ch in line.strip()]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def max_pair_len(n, adj, s, t):
    best = [-1]
    def dfs(v, mask, ln):
        if v == t:
            best[0] = max(best[0], ln)
            return
        for w in range(n):
            if adj[v] >> w & 1 and not mask >> w & 1:
                dfs(w, mask | 1 << w, ln + 1)
    dfs(s, 1 << s, 0)
    return best[0]


def all_longest_paths(n, adj):
    best = [0]
    paths = []
    def dfs(v, mask, ln):
        ext = False
        for w in range(n):
            if adj[v] >> w & 1 and not mask >> w & 1:
                ext = True
                dfs(w, mask | 1 << w, ln + 1)
        if not ext or True:
            if ln > best[0]:
                best[0] = ln
                paths.clear()
                paths.append(mask)
            elif ln == best[0]:
                paths.append(mask)
    for s in range(n):
        dfs(s, 1 << s, 0)
    return best[0], sorted(set(paths))


def main():
    g6, a, b, c = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    nh, edges = parse_graph6(g6)
    adjh = [0] * nh
    for u, v in edges:
        adjh[u] |= 1 << v
        adjh[v] |= 1 << u
    M_ab = max_pair_len(nh, adjh, a, b)
    M_bc = max_pair_len(nh, adjh, b, c)
    M_ac = max_pair_len(nh, adjh, a, c)
    # arm lengths: L_a - L_c = M_bc - M_ab ; L_b - L_c = M_ac - M_ab ; all >= nh
    L_c = nh + max(0, M_ab - M_bc, M_ab - M_ac)
    L_a = L_c + M_bc - M_ab
    L_b = L_c + M_ac - M_ab
    assert min(L_a, L_b, L_c) >= nh
    # build spider
    edges2 = list(edges)
    n = nh
    for root, L in ((a, L_a), (b, L_b), (c, L_c)):
        prev = root
        for _ in range(L):
            edges2.append((prev, n))
            prev = n
            n += 1
    adj = [0] * n
    for u, v in edges2:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    print(f"core n={nh} M=({M_ab},{M_bc},{M_ac}) arms=({L_a},{L_b},{L_c}) spider n={n}")
    best, paths = all_longest_paths(n, adj)
    print(f"longest path length {best}, {len(paths)} distinct longest-path vertex sets")
    expected = L_a + L_b + M_ab
    print(f"expected tip-to-tip length {expected} -> {'OK' if best == expected else 'MISMATCH'}")
    mn = 999
    for p1, p2, p3 in combinations(paths, 3):
        sz = bin(p1 & p2 & p3).count('1')
        if sz < mn:
            mn = sz
            if mn == 0:
                break
    print(f"min triple intersection over longest paths: {mn}")
    print("COUNTEREXAMPLE" if mn == 0 else "no counterexample (as expected if core had no hit)")


if __name__ == "__main__":
    main()

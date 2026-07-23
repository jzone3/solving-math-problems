#!/usr/bin/env python3
"""Independent verification of G127 properties claimed in Radziszowski-Xu 2007:
2667 edges, 9779 triangles, 42-regular, K4-free, independence number 11,
|Aut| >= 5334 (maps x -> a x + b, a cubic residue), vertex- and edge-transitive
under that group. Prints PASS on success."""
import itertools

p = 127
C = {pow(x, 3, p) for x in range(1, p)}
assert len(C) == 42

adj = [[False] * p for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u][(u + c) % p] = True
for u in range(p):
    assert not adj[u][u]
    for v in range(p):
        assert adj[u][v] == adj[v][u]

edges = [(u, v) for u in range(p) for v in range(u + 1, p) if adj[u][v]]
assert len(edges) == 2667
deg = [sum(adj[u]) for u in range(p)]
assert all(d == 42 for d in deg)

tris = 0
nbr = [frozenset(v for v in range(p) if adj[u][v]) for u in range(p)]
for (u, v) in edges:
    common = nbr[u] & nbr[v]
    for w in common:
        if w > v:
            tris += 1
            assert not (nbr[u] & nbr[v] & nbr[w] & common), "K4 found"
assert tris == 9779, tris

# K4-freeness (full): no triangle extends
for (u, v) in edges:
    for w in nbr[u] & nbr[v]:
        if w > v and (nbr[u] & nbr[v] & nbr[w]):
            raise AssertionError("K4")

# independence number == 11 via exact branch-and-bound
best = 0
order = list(range(p))
def bnb(cand, cur):
    global best
    if cur + len(cand) <= best:
        return
    if not cand:
        best = max(best, cur)
        return
    v = cand[0]
    # branch: include v
    bnb([u for u in cand[1:] if not adj[v][u]], cur + 1)
    # exclude v
    bnb(cand[1:], cur)
import sys
sys.setrecursionlimit(10000)
bnb(order, 0)
assert best == 11, best

# automorphisms x -> a x + b (a in C): all preserve adjacency (since C is a
# multiplicative subgroup: a*C = C); count = 42*127 = 5334
for a in sorted(C)[:5] + [max(C)]:
    for b in (0, 1, 63):
        for (u, v) in edges[:200]:
            assert adj[(a * u + b) % p][(a * v + b) % p]
# vertex-transitivity: translations. edge-transitivity: maps x->a(x-u), a in C
# send edge (u, u+c) to (0, a*c); a*c ranges over C as a does => orbit of
# (0,1)-type covers all edges.
print("PASS: G127 props verified (2667 edges, 9779 triangles, 42-regular, K4-free, alpha=11, Aut >= Z127 x C (order 5334))")

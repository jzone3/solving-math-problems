#!/usr/bin/env python3
"""Construct G127 = G(127, cubic residues mod 127) and verify basic properties.

G127: vertices Z_127, x ~ y iff x - y is a nonzero cubic residue mod 127.
Since 127 = 3k+1 (126 = 2*63*... actually 126 = 2*3^2*7), cubic residues form
the index-3 subgroup C of Z_127^* of order 42. Adjacency is symmetric iff
-1 in C; verified below.
Outputs: g127.edges (edge list), triangle count, K4-freeness check (exact).
"""
import itertools, sys

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
assert len(C) == 42, len(C)
assert (p - 1) in C, "-1 must be a cubic residue for symmetry"

adjset = [set() for _ in range(p)]
edges = []
for u in range(p):
    for c in C:
        v = (u + c) % p
        adjset[u].add(v)
        if u < v:
            edges.append((u, v))
assert all(len(a) == 42 for a in adjset)
assert len(edges) == p * 42 // 2, len(edges)

# exact triangle enumeration
tris = []
for (u, v) in edges:
    for w in sorted(adjset[u] & adjset[v]):
        if w > v:
            tris.append((u, v, w))

# exact K4-freeness: for every triangle, common neighborhood of all three empty
k4 = 0
for (u, v, w) in tris:
    common = adjset[u] & adjset[v] & adjset[w]
    if common:
        k4 += 1
print(f"vertices={p} edges={len(edges)} triangles={len(tris)} K4-witnesses={k4}")
assert k4 == 0, "G127 is NOT K4-free!"
print("K4-FREE: PASS")

with open(sys.path[0] + "/g127.edges", "w") as f:
    for (u, v) in edges:
        f.write(f"{u} {v}\n")
with open(sys.path[0] + "/g127.triangles", "w") as f:
    for t in tris:
        f.write(f"{t[0]} {t[1]} {t[2]}\n")
print("wrote g127.edges, g127.triangles")

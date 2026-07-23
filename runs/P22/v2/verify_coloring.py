#!/usr/bin/env python3
"""Independent verifier: given a 2-coloring of E(G127) (file: lines
"<edge_index> <color>" with edges ordered star-of-0 first, then sorted rest,
as in gen_cnf.py), rebuild G127 from scratch and check whether the coloring
has zero monochromatic triangles. Prints PASS (valid witness that
G127 -/-> (3,3)^e) or the number of mono triangles.
Usage: python3 verify_coloring.py best_coloring.txt
"""
import sys

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)

edges = sorted((0, c) for c in C) + sorted(
    (u, v) for u in range(1, p) for v in adj[u] if u < v)
assert len(edges) == 2667

col = {}
for line in open(sys.argv[1]):
    i, c = map(int, line.split())
    col[edges[i]] = c
assert len(col) == 2667

def ec(u, v):
    return col[(u, v) if u < v else (v, u)]

mono = 0
ntri = 0
for (u, v) in edges:
    for w in adj[u] & adj[v]:
        if w > v:
            ntri += 1
            if ec(u, v) == ec(u, w) == ec(v, w):
                mono += 1
assert ntri == 9779
if mono == 0:
    print("PASS: zero monochromatic triangles -- G127 does NOT arrow (3,3)^e")
else:
    print(f"FAIL: {mono} monochromatic triangles")
    sys.exit(1)

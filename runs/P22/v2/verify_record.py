#!/usr/bin/env python3
"""Independently verify a claimed near-miss coloring record file
(format: 'c nmono <k>' + one line of 2667 bits, edge order as in gen_cnf.py).
Rebuilds G127 from scratch and recounts monochromatic triangles.
Usage: verify_record.py <file>
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
var = {e: i for i, e in enumerate(edges)}

with open(sys.argv[1]) as f:
    lines = f.read().split()
claimed = None
bits = None
for i, tok in enumerate(lines):
    if tok == "nmono":
        claimed = int(lines[i + 1])
    if set(tok) <= {"0", "1"} and len(tok) == 2667:
        bits = tok
col = [int(b) for b in bits]

mono = 0
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            a, b, c = col[var[(u, v)]], col[var[(u, w)]], col[var[(v, w)]]
            if a == b == c:
                mono += 1
print(f"recomputed mono triangles: {mono} (claimed {claimed})")
assert claimed is None or mono == claimed, "MISMATCH"
print("PASS")

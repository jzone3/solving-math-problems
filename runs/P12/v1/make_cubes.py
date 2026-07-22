"""Cube-and-conquer splitter for the T2(n) CNF from gen_cnf.py.

Splits on the symbols in row 1, columns 1..depth (row 1 starts with symbol 1
by standard form; row 0 is the identity). Emits one CNF per cube consistent
with basic pair-availability pruning against row 0 (identity):
  - row 0 uses distance-1 pairs (i,i+1) and distance-2 pairs (i,i+2);
  - within the cube prefix (1, s1, s2, ...) all distance-1 pairs must be new
    and distinct, distance-2 pairs must avoid row 0's and each other.

Usage: python3 make_cubes.py n depth basecnf outdir
"""
import os
import sys
from itertools import permutations

n = int(sys.argv[1])
depth = int(sys.argv[2])
base = sys.argv[3]
outdir = sys.argv[4]
os.makedirs(outdir, exist_ok=True)

# variable numbering must match gen_cnf.py's IDPool: x vars were created
# first, in order (r, c, s) -> id = r*n*n + c*n + s + 1
xid = lambda r, c, s: r * n * n + c * n + s + 1

d1_used = {(i, i + 1) for i in range(n - 1)}
d2_used = {(i, i + 2) for i in range(n - 2)}

with open(base) as f:
    header = f.readline().split()
    nv, ncl = int(header[2]), int(header[3])
    body = f.read()

cubes = []
for tail in permutations([s for s in range(n) if s != 1], depth):
    prefix = (1,) + tail
    d1 = {(prefix[i], prefix[i + 1]) for i in range(depth)}
    d2 = {(prefix[i], prefix[i + 2]) for i in range(depth - 1)}
    if len(d1) != depth or d1 & d1_used:
        continue
    if len(d2) != depth - 1 or d2 & d2_used:
        continue
    cubes.append(prefix)

for idx, prefix in enumerate(cubes):
    units = [xid(1, c, s) for c, s in enumerate(prefix)]
    with open(os.path.join(outdir, f"cube{idx:04d}.cnf"), "w") as f:
        f.write(f"p cnf {nv} {ncl + len(units)}\n")
        f.write(body)
        for u in units:
            f.write(f"{u} 0\n")
print(f"{len(cubes)} cubes written to {outdir}")

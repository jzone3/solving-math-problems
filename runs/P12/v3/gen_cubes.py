#!/usr/bin/env python3
"""Cube-and-conquer splitter for the standard-form T2(n) encoding.

Cubes = assignments of row 1 (the row starting with symbol 1), positions
1..L, consistent with the identity row (distance-1 pairs (a,a+1) and
distance-2 pairs (a,a+2) already used) and with row-internal validity.
Emits one CNF per cube: base CNF + unit clauses.

Usage: gen_cubes.py n L basecnf outdir
"""
import os
import sys

n = int(sys.argv[1])
L = int(sys.argv[2])
base = sys.argv[3]
outdir = sys.argv[4]
os.makedirs(outdir, exist_ok=True)


def xvar(r, i, s):
    return r * n * n + i * n + s + 1


used1 = {(a, a + 1) for a in range(n - 1)}   # identity row dist-1
used2 = {(a, a + 2) for a in range(n - 2)}   # identity row dist-2

cubes = []


# row 1 starts with symbol 1 (standard form)
# note: symbol 0 CAN appear in row 1 at positions >=1; the x==0 skip above is
# wrong in general -- remove it.
def rec2(cur):
    if len(cur) == L + 1:
        cubes.append(list(cur))
        return
    prev = cur[-1]
    prev2 = cur[-2] if len(cur) >= 2 else None
    for x in range(n):
        if x in cur:
            continue
        if (prev, x) in used1:
            continue
        if prev2 is not None and (prev2, x) in used2:
            continue
        cur.append(x)
        rec2(cur)
        cur.pop()


rec2([1])

header = open(base).readline().split()
nv, nc = int(header[2]), int(header[3])
body = open(base).read().split("\n", 1)[1]

for ci, cube in enumerate(cubes):
    fn = os.path.join(outdir, f"cube{ci:05d}.cnf")
    units = [f"{xvar(1, i, s)} 0" for i, s in enumerate(cube)]
    with open(fn, "w") as f:
        f.write(f"p cnf {nv} {nc + len(units)}\n")
        f.write(body)
        f.write("\n".join(units) + "\n")
print(f"{len(cubes)} cubes -> {outdir}")

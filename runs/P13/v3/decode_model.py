#!/usr/bin/env python3
"""Decode kissat 'v' lines into a witness (blocks) for gen_cnf.py variable layout."""
import sys

K = 6
v = int(sys.argv[1])
b = v * (v - 1) // K
true = set()
for line in open(sys.argv[2]):
    if line.startswith("v"):
        for tok in line.split()[1:]:
            n = int(tok)
            if n > 0:
                true.add(n)
var = 0
blocks = []
for bl in range(b):
    row = []
    for p in range(K):
        sym = None
        for s in range(v):
            var += 1
            if var in true:
                sym = s
        row.append(sym)
    blocks.append(row)
for row in blocks:
    print(" ".join(map(str, row)))

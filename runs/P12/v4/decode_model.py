#!/usr/bin/env python3
"""Decode a kissat/cadical model (v-lines) into a T2 array. Usage: decode_model.py n solver_output witness_out"""
import sys

n = int(sys.argv[1])
true_vars = set()
for line in open(sys.argv[2]):
    if line.startswith("v"):
        for t in line.split()[1:]:
            v = int(t)
            if v > 0:
                true_vars.add(v)
arr = [[None] * n for _ in range(n)]
for r in range(n):
    for c in range(n):
        for s in range(n):
            if r * n * n + c * n + s + 1 in true_vars:
                arr[r][c] = s
with open(sys.argv[3], "w") as f:
    for row in arr:
        f.write(" ".join(map(str, row)) + "\n")
print("decoded ->", sys.argv[3])

#!/usr/bin/env python3
"""Kick a matrix: random in-row swaps (row compositions preserved). Usage: perturb.py in out nswaps seed"""
import sys, random
inp, out, ns, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rng = random.Random(seed)
M = [list(map(int, line.strip())) for line in open(inp) if line.strip()]
V, B = len(M), len(M[0])
for _ in range(ns):
    i = rng.randrange(V)
    j1, j2 = rng.randrange(B), rng.randrange(B)
    M[i][j1], M[i][j2] = M[i][j2], M[i][j1]
with open(out, "w") as f:
    for row in M:
        f.write("".join(map(str, row)) + "\n")

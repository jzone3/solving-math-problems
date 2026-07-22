#!/usr/bin/env python3
"""Decode kissat model (v-lines) + cnf map comments -> V x B matrix, print it."""
import sys

cnf, model = sys.argv[1], sys.argv[2]
rows = {}
for line in open(cnf):
    if line.startswith('c map '):
        parts = line.split()
        v = int(parts[2])
        rows[v] = [tuple(map(int, p.split(','))) for p in parts[3:]]

true = set()
for line in open(model):
    if line.startswith('v'):
        for tok in line.split()[1:]:
            n = int(tok)
            if n > 0:
                true.add(n)

V = len(rows)
for v in range(V):
    out = []
    for (a1, a2) in rows[v]:
        out.append((1 if a1 in true else 0) + (1 if a2 in true else 0))
    print(' '.join(map(str, out)))

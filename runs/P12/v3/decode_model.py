#!/usr/bin/env python3
"""Decode kissat model ('v' lines) for gen_cnf.py encoding; verify and print array."""
import sys

sys.path.insert(0, ".")
from t2lib import check_t2

n = int(sys.argv[1])
lits = set()
for line in open(sys.argv[2]):
    if line.startswith("v"):
        for tok in line.split()[1:]:
            v = int(tok)
            if v > 0:
                lits.add(v)


def xvar(r, i, s):
    return r * n * n + i * n + s + 1


rows = []
for r in range(n):
    row = []
    for i in range(n):
        syms = [s for s in range(n) if xvar(r, i, s) in lits]
        assert len(syms) == 1, (r, i, syms)
        row.append(syms[0])
    rows.append(row)
for row in rows:
    print(" ".join(map(str, row)))
print("valid T2:", check_t2(rows, n), file=sys.stderr)

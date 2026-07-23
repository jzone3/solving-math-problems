#!/usr/bin/env python3
"""Standalone BTD verifier. Usage: verify.py V B p1 p2 R K L matrix.txt
matrix.txt: V lines of B space-separated ints in {0,1,2}. Prints PASS or FAIL.
No dependencies beyond the standard library.
"""
import sys

V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
M = [list(map(int, line.split())) for line in open(sys.argv[8]) if line.strip()]

ok = True
def chk(cond, msg):
    global ok
    if not cond:
        ok = False
        print('FAIL:', msg)

chk(R == p1 + 2 * p2, 'R != p1+2*p2')
chk(len(M) == V, f'need {V} rows, got {len(M)}')
for i, row in enumerate(M):
    chk(len(row) == B, f'row {i} length')
    chk(all(x in (0, 1, 2) for x in row), f'row {i} entries')
    chk(sum(row) == R, f'row {i} sum != {R}')
    chk(row.count(1) == p1, f'row {i} multiplicity-1 count != {p1}')
    chk(row.count(2) == p2, f'row {i} multiplicity-2 count != {p2}')
for b in range(B):
    chk(sum(M[v][b] for v in range(V)) == K, f'col {b} sum != {K}')
for i in range(V):
    for j in range(i + 1, V):
        s = sum(M[i][b] * M[j][b] for b in range(B))
        chk(s == L, f'pair ({i},{j}) covered {s} != {L}')

print('PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)

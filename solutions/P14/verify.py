#!/usr/bin/env python3
"""Standalone verifier for BTD(V,B; p1,p2,R; K,L) witnesses.

A witness file contains V lines of B space-separated integers in {0,1,2}
(the incidence matrix: entry = multiplicity of element i in block j).
Checks (per Handbook ch. VI.2 / CPro1 problem_def.py definition):
  1. entries in {0,1,2}
  2. each row sums to R, with exactly p1 ones and p2 twos (R = p1 + 2*p2)
  3. each column sums to K
  4. for every pair of distinct rows i<k: sum_j m[i][j]*m[k][j] == L

Usage: verify.py V B p1 p2 R K L witness_file
Prints PASS or FAIL with reason. No dependencies.
"""
import sys


def verify(V, B, p1, p2, R, K, L, m):
    if R != p1 + 2 * p2:
        return "param inconsistency: R != p1 + 2*p2"
    if len(m) != V:
        return f"wrong number of rows: {len(m)} != {V}"
    for i, row in enumerate(m):
        if len(row) != B:
            return f"row {i} has {len(row)} entries != {B}"
        for x in row:
            if x not in (0, 1, 2):
                return f"row {i} entry {x} not in {{0,1,2}}"
        if sum(row) != R:
            return f"row {i} sum {sum(row)} != R={R}"
        if row.count(1) != p1:
            return f"row {i} has {row.count(1)} ones != p1={p1}"
        if row.count(2) != p2:
            return f"row {i} has {row.count(2)} twos != p2={p2}"
    for j in range(B):
        c = sum(m[i][j] for i in range(V))
        if c != K:
            return f"column {j} sum {c} != K={K}"
    for i in range(V):
        for k in range(i + 1, V):
            s = sum(m[i][j] * m[k][j] for j in range(B))
            if s != L:
                return f"pair ({i},{k}) inner product {s} != L={L}"
    return None


def main():
    if len(sys.argv) != 9:
        print("usage: verify.py V B p1 p2 R K L witness_file")
        sys.exit(2)
    V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
    with open(sys.argv[8]) as f:
        m = [[int(x) for x in line.split()] for line in f if line.strip()]
    err = verify(V, B, p1, p2, R, K, L, m)
    if err:
        print("FAIL:", err)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()

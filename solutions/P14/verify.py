#!/usr/bin/env python3
"""Standalone verifier for BTD(V,B; r1,r2,R; K,Lam) witnesses.

Witness JSON format: {"params": {"V":..,"B":..,"r1":..,"r2":..,"K":..,"Lam":..}, "matrix": [[...]]}
matrix is V x B over {0,1,2}: matrix[i][j] = multiplicity of element i in block j.

Checks:
  1. every entry in {0,1,2}
  2. every column sums to K (block size, counting multiplicity)
  3. every row has exactly r1 ones and r2 twos (so row sum R = r1 + 2*r2)
  4. for every unordered pair i<j: sum_b m[i][b]*m[j][b] == Lam

Usage: verify.py witness.json [witness2.json ...]  -> prints PASS/FAIL per file.
No dependencies beyond the standard library.
"""
import json, sys

def check(fn):
    d = json.load(open(fn))
    p = d["params"]
    V, B, r1, r2, K, Lam = p["V"], p["B"], p["r1"], p["r2"], p["K"], p["Lam"]
    M = d["matrix"]
    assert len(M) == V and all(len(row) == B for row in M), "matrix shape"
    for row in M:
        for x in row:
            assert x in (0, 1, 2), "entry not in {0,1,2}"
    for j in range(B):
        assert sum(M[i][j] for i in range(V)) == K, f"column {j} sum != K"
    for i in range(V):
        assert M[i].count(1) == r1, f"row {i} ones != r1"
        assert M[i].count(2) == r2, f"row {i} twos != r2"
    for i in range(V):
        for j in range(i + 1, V):
            s = sum(M[i][b] * M[j][b] for b in range(B))
            assert s == Lam, f"pair ({i},{j}) coverage {s} != Lam"
    return True

if __name__ == "__main__":
    ok = True
    for fn in sys.argv[1:]:
        try:
            check(fn)
            print(f"{fn}: PASS")
        except AssertionError as e:
            ok = False
            print(f"{fn}: FAIL ({e})")
    sys.exit(0 if ok else 1)

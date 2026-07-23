#!/usr/bin/env python3
"""Standalone BTD witness verifier (dependency-free).

Usage: python3 verify_witness.py <witness_file>
Witness file format:
  line 1: V B r1 r2 R K L
  lines 2..V+1: B digits from {0,1,2} (multiplicity matrix row)
Prints PASS or FAIL with reasons. Exit code 0 iff PASS.
"""
import sys

def main(path):
    with open(path) as f:
        toks = f.readline().split()
        V, B, r1, r2, R, K, L = map(int, toks)
        mat = []
        for _ in range(V):
            row = f.readline().strip()
            assert len(row) == B, f"row length {len(row)} != B={B}"
            mat.append([int(c) for c in row])
    errs = []
    for v in range(V):
        ones = sum(1 for x in mat[v] if x == 1)
        twos = sum(1 for x in mat[v] if x == 2)
        if ones != r1: errs.append(f"row {v}: {ones} ones != r1={r1}")
        if twos != r2: errs.append(f"row {v}: {twos} twos != r2={r2}")
        if any(x not in (0, 1, 2) for x in mat[v]): errs.append(f"row {v}: bad entry")
    for b in range(B):
        cs = sum(mat[v][b] for v in range(V))
        if cs != K: errs.append(f"col {b}: sum {cs} != K={K}")
    for v in range(V):
        for w in range(v+1, V):
            lam = sum(mat[v][b]*mat[w][b] for b in range(B))
            if lam != L: errs.append(f"pair ({v},{w}): {lam} != L={L}")
    if r1 + 2*r2 != R: errs.append(f"R mismatch: r1+2r2={r1+2*r2} != {R}")
    if errs:
        print("FAIL")
        for e in errs[:20]: print("  ", e)
        sys.exit(1)
    print(f"PASS: valid BTD({V},{B};{r1},{r2},{R};{K},{L})")

if __name__ == "__main__":
    main(sys.argv[1])

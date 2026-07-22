#!/usr/bin/env python3
"""Standalone verifier for Balanced Ternary Design witnesses (P14).

A BTD(V,B; rho1,rho2,R; K,Lambda) witness is a V x B matrix M over {0,1,2}:
  - every column sums to K (block size, counting multiplicity),
  - every row has exactly rho1 entries equal to 1 and rho2 entries equal to 2
    (hence row sum R = rho1 + 2*rho2),
  - for every pair of distinct rows i<k:  sum_j M[i][j]*M[k][j] == Lambda.

Usage:  verify.py <witness-file>
Witness file format: first line "V B rho1 rho2 R K Lambda",
then V lines of B space- or ''-separated digits in {0,1,2}.
Prints PASS or FAIL (with reasons). Pure stdlib.
"""
import sys


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <witness-file>")
        sys.exit(2)
    lines = [ln.strip() for ln in open(sys.argv[1]) if ln.strip()]
    V, B, rho1, rho2, R, K, Lam = map(int, lines[0].split())
    rows = lines[1:]
    ok = True

    def fail(msg):
        nonlocal ok
        ok = False
        print("FAIL:", msg)

    if R != rho1 + 2 * rho2:
        fail(f"parameter inconsistency: R={R} != rho1+2*rho2={rho1+2*rho2}")
    if len(rows) != V:
        fail(f"expected {V} rows, got {len(rows)}")
    M = []
    for i, ln in enumerate(rows):
        toks = ln.split() if " " in ln else list(ln)
        vals = [int(t) for t in toks]
        if len(vals) != B:
            fail(f"row {i}: expected {B} entries, got {len(vals)}")
        if any(v not in (0, 1, 2) for v in vals):
            fail(f"row {i}: entries outside {{0,1,2}}")
        M.append(vals)
    if not ok:
        print("FAIL")
        sys.exit(1)

    for i in range(V):
        c1 = sum(1 for v in M[i] if v == 1)
        c2 = sum(1 for v in M[i] if v == 2)
        if c1 != rho1:
            fail(f"row {i}: has {c1} ones, expected rho1={rho1}")
        if c2 != rho2:
            fail(f"row {i}: has {c2} twos, expected rho2={rho2}")
    for j in range(B):
        s = sum(M[i][j] for i in range(V))
        if s != K:
            fail(f"column {j}: sum {s}, expected K={K}")
    for i in range(V):
        for k in range(i + 1, V):
            p = sum(M[i][j] * M[k][j] for j in range(B))
            if p != Lam:
                fail(f"pair ({i},{k}): inner product {p}, expected Lambda={Lam}")

    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

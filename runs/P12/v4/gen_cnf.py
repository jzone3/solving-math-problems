#!/usr/bin/env python3
"""DIMACS CNF generator for T2(n) (Tuscan-2 square existence).

Variables:
  x[r][c][s]   : symbol s at row r column c            (n^3)
  z1[r][c][a][b]: x[r][c][a] & x[r][c+1][b]  (Tseitin, dist-1 pair at (r,c))
  z2[r][c][a][b]: x[r][c][a] & x[r][c+2][b]  (dist-2)

Constraints:
  each cell exactly one symbol; each symbol once per row (Latin rows);
  P1[r][a][b] <-> OR_c z1[r][c][a][b] (pair occurs in row r at dist 1); likewise P2.
  For each ordered pair (a,b): exactly one P1 over rows; at most one P2 over rows.
  (Within a row a pair can occur at most once at a given distance since each
  symbol appears once per row, so row-level AMO suffices.)
Symmetry breaking (valid up to symbol relabeling + row sorting):
  row 0 = identity; column 0 = identity (first column is a permutation).

Usage: gen_cnf.py n out.cnf [--cube ROW1_PREFIX]  (prefix = symbols of row 1, comma-sep)
"""
import sys


def main():
    n = int(sys.argv[1])
    out = sys.argv[2]
    cube = []
    if len(sys.argv) > 4 and sys.argv[3] == "--cube":
        cube = [int(t) for t in sys.argv[4].split(",")]

    nv = 0

    def new():
        nonlocal nv
        nv += 1
        return nv

    x = [[[new() for s in range(n)] for c in range(n)] for r in range(n)]
    cl = []
    # cell exactly one symbol
    for r in range(n):
        for c in range(n):
            cl.append([x[r][c][s] for s in range(n)])
            for s in range(n):
                for t in range(s + 1, n):
                    cl.append([-x[r][c][s], -x[r][c][t]])
    # each symbol once per row (at least once; at most follows from cell-exactly-one + counting, add pairwise anyway for propagation)
    for r in range(n):
        for s in range(n):
            cl.append([x[r][c][s] for c in range(n)])
            for c in range(n):
                for d in range(c + 1, n):
                    cl.append([-x[r][c][s], -x[r][d][s]])
    # pair aux vars
    z1 = {}
    z2 = {}
    for r in range(n):
        for c in range(n - 1):
            for a in range(n):
                for b in range(n):
                    if a == b:
                        continue
                    v = new()
                    z1[r, c, a, b] = v
                    cl.append([-v, x[r][c][a]])
                    cl.append([-v, x[r][c + 1][b]])
                    cl.append([v, -x[r][c][a], -x[r][c + 1][b]])
        for c in range(n - 2):
            for a in range(n):
                for b in range(n):
                    if a == b:
                        continue
                    v = new()
                    z2[r, c, a, b] = v
                    cl.append([-v, x[r][c][a]])
                    cl.append([-v, x[r][c + 2][b]])
                    cl.append([v, -x[r][c][a], -x[r][c + 2][b]])
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            p1 = []
            p2 = []
            for r in range(n):
                zs = [z1[r, c, a, b] for c in range(n - 1)]
                v = new()
                p1.append(v)
                for zz in zs:
                    cl.append([-zz, v])
                cl.append([-v] + zs)
                zs2 = [z2[r, c, a, b] for c in range(n - 2)]
                w = new()
                p2.append(w)
                for zz in zs2:
                    cl.append([-zz, w])
                cl.append([-w] + zs2)
            cl.append(p1)  # at least one row
            for i in range(n):
                for j in range(i + 1, n):
                    cl.append([-p1[i], -p1[j]])
                    cl.append([-p2[i], -p2[j]])
    # symmetry breaking
    for c in range(n):
        cl.append([x[0][c][c]])
    for r in range(n):
        cl.append([x[r][0][r]])
    # optional cube: fix a prefix of row 1 (columns 1..len)
    for i, s in enumerate(cube):
        cl.append([x[1][1 + i][s]])

    with open(out, "w") as f:
        f.write(f"p cnf {nv} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")
    print(f"n={n} vars={nv} clauses={len(cl)} -> {out}")
    # also emit decoder mapping info
    with open(out + ".map", "w") as f:
        f.write(f"{n}\n")


def decode(n, model_lits):
    """model_lits: set of true var ids; x vars are first n^3, id = r*n*n + c*n + s + 1."""
    arr = [[None] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            for s in range(n):
                if (r * n * n + c * n + s + 1) in model_lits:
                    arr[r][c] = s
    return arr


if __name__ == "__main__":
    main()

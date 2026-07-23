#!/usr/bin/env python3
"""DIMACS CNF generator for Tuscan-2 squares T2(n), standard form.

Encoding:
  cell vars  X[r][c][s]  (r,c,s in 0..n-1): symbol s at (r,c).
  - exactly-one symbol per cell (pairwise AMO + ALO);
  - each symbol once per row (pairwise AMO per (r,s) over c + ALO);
  - row 0 = identity, X[r][0]=r (units);
  - last column: pairwise AMO per symbol across rows (redundant strengthening);
  dist-1 pair vars P1[a][b][r][c] <-> X[r][c][a] & X[r][c+1][b]:
  - exactly-one over the n(n-1) slots for each ordered pair (a,b);
  dist-2 pair vars P2 defined only implicitly: at-most-one via direct clauses
    (~X[r][c][a] | ~X[r][c+2][b] | ~X[r'][c'][a] | ~X[r'][c'+2][b]) would be
    quadratic; instead use P2 vars with one-directional definition
    P2 >= X&X (clauses (~Xa | ~Xb | P2)) + pairwise AMO over P2s.
  For P1, one-directional (P1 => needed for ALO; AMO needs X&X => P1):
    use full equivalence for P1.

Usage: t2cnf.py n [cube_row1_file line_index] > out.cnf
  Optionally fix row 1 to a given permutation (cube): file has one
  space-separated permutation per line; line_index selects (0-based).
"""
import sys


def main():
    n = int(sys.argv[1])
    cube = None
    if len(sys.argv) > 3:
        with open(sys.argv[2]) as f:
            lines = f.read().split("\n")
        cube = [int(t) for t in lines[int(sys.argv[3])].split()]
        assert len(cube) == n and cube[0] == 1
    nv = 0
    def newvar():
        nonlocal nv
        nv += 1
        return nv
    X = [[[newvar() for s in range(n)] for c in range(n)] for r in range(n)]
    cls = []
    # cell constraints
    for r in range(n):
        for c in range(n):
            cls.append([X[r][c][s] for s in range(n)])
            for s1 in range(n):
                for s2 in range(s1 + 1, n):
                    cls.append([-X[r][c][s1], -X[r][c][s2]])
        for s in range(n):
            cls.append([X[r][c][s] for c in range(n)])
            for c1 in range(n):
                for c2 in range(c1 + 1, n):
                    cls.append([-X[r][c1][s], -X[r][c2][s]])
    # standard form units
    for c in range(n):
        cls.append([X[0][c][c]])
    for r in range(n):
        cls.append([X[r][0][r]])
    if cube:
        for c in range(n):
            cls.append([X[1][c][cube[c]]])
    # last column AMO per symbol (redundant)
    for s in range(n):
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                cls.append([-X[r1][n - 1][s], -X[r2][n - 1][s]])
    # dist-1: exactly one occurrence per ordered pair
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            occ = []
            for r in range(n):
                for c in range(n - 1):
                    v = newvar()
                    occ.append(v)
                    # v <-> Xa & Xb
                    cls.append([-v, X[r][c][a]])
                    cls.append([-v, X[r][c + 1][b]])
                    cls.append([v, -X[r][c][a], -X[r][c + 1][b]])
            cls.append(occ)  # ALO
            for i in range(len(occ)):
                for j in range(i + 1, len(occ)):
                    cls.append([-occ[i], -occ[j]])
    # dist-2: at most one occurrence per ordered pair
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            occ = []
            for r in range(n):
                for c in range(n - 2):
                    v = newvar()
                    occ.append(v)
                    cls.append([v, -X[r][c][a], -X[r][c + 2][b]])
            for i in range(len(occ)):
                for j in range(i + 1, len(occ)):
                    cls.append([-occ[i], -occ[j]])
    out = sys.stdout
    out.write(f"p cnf {nv} {len(cls)}\n")
    out.write("\n".join(" ".join(map(str, cl)) + " 0" for cl in cls))
    out.write("\n")
    # decode helper info on stderr
    sys.stderr.write(f"vars={nv} clauses={len(cls)} cellvar(r,c,s)=r*{n*n}+c*{n}+s+1\n")


if __name__ == "__main__":
    main()

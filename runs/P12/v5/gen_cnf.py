#!/usr/bin/env python3
"""CNF encoder for normalized Tuscan-2 squares T2(n) (cube-and-conquer attack).

Normalization (standard, WLOG — see NOTES.md):
  row 0 = identity 0..n-1; first column = 0..n-1 in order (row i starts with symbol i).

Variables: x(i,j,s) = 1 iff cell (i,j) holds symbol s  (i,j,s in 0..n-1).
Aux occurrence vars for distance-d pairs (d=1,2):
  o_d(a,b,i,j) <-> x(i,j)=a and x(i,j+d)=b.
Constraints:
  - each cell exactly one symbol; each row: each symbol at most once (=> permutation);
  - row 0 and first column fixed;
  - last column all-different (lemma: it is a permutation);
  - dist-1: for every ordered pair a!=b: exactly one occurrence;
  - dist-2: at most one occurrence.
Optional cube: --fix-row1 "s0 s1 ... s{n-1}" fixes row 1 completely.

Usage: gen_cnf.py n out.cnf [--fix-row1 "1 3 0 ..."]
Decode: gen_cnf.py n --decode model_file  (reads kissat "v ..." lines, prints square)
"""
import sys


def build(n, fix_row1=None):
    clauses = []
    nv = 0
    X = {}
    for i in range(n):
        for j in range(n):
            for s in range(n):
                nv += 1
                X[(i, j, s)] = nv

    def x(i, j, s):
        return X[(i, j, s)]

    # cell exactly-one symbol
    for i in range(n):
        for j in range(n):
            clauses.append([x(i, j, s) for s in range(n)])
            for s in range(n):
                for t in range(s + 1, n):
                    clauses.append([-x(i, j, s), -x(i, j, t)])
    # row: symbol at most once (with exactly-one cells this forces permutation rows)
    for i in range(n):
        for s in range(n):
            for j in range(n):
                for k in range(j + 1, n):
                    clauses.append([-x(i, j, s), -x(i, k, s)])
    # row 0 identity, first column fixed
    for j in range(n):
        clauses.append([x(0, j, j)])
    for i in range(n):
        clauses.append([x(i, 0, i)])
    # last column all-different
    for s in range(n):
        for i in range(n):
            for k in range(i + 1, n):
                clauses.append([-x(i, n - 1, s), -x(k, n - 1, s)])
    # optional cube: fix row 1
    if fix_row1 is not None:
        assert len(fix_row1) == n and fix_row1[0] == 1
        for j in range(n):
            clauses.append([x(1, j, fix_row1[j])])

    # occurrence vars and pair constraints
    for d, exact in ((1, True), (2, False)):
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                occ = []
                for i in range(n):
                    for j in range(n - d):
                        nv += 1
                        o = nv
                        occ.append(o)
                        clauses.append([-o, x(i, j, a)])
                        clauses.append([-o, x(i, j + d, b)])
                        clauses.append([o, -x(i, j, a), -x(i, j + d, b)])
                # at-most-one via sequential counter
                m = len(occ)
                prev = None
                for idx in range(m):
                    nv += 1
                    r = nv  # r_idx = at least one of occ[0..idx]
                    clauses.append([-occ[idx], r])
                    if prev is not None:
                        clauses.append([-prev, r])
                        clauses.append([-prev, -occ[idx]])  # AMO
                    prev = r
                if exact:
                    clauses.append(occ[:])  # at-least-one
    return nv, clauses


def main():
    n = int(sys.argv[1])
    if "--decode" in sys.argv:
        mf = sys.argv[sys.argv.index("--decode") + 1]
        pos = set()
        for line in open(mf):
            if line.startswith("v"):
                for tok in line.split()[1:]:
                    v = int(tok)
                    if v > 0:
                        pos.add(v)
        for i in range(n):
            row = []
            for j in range(n):
                for s in range(n):
                    if (i * n + j) * n + s + 1 in pos:
                        row.append(s)
            print(" ".join(map(str, row)))
        return
    out = sys.argv[2]
    fix = None
    if "--fix-row1" in sys.argv:
        fix = list(map(int, sys.argv[sys.argv.index("--fix-row1") + 1].split()))
    nv, clauses = build(n, fix)
    with open(out, "w") as f:
        f.write(f"p cnf {nv} {len(clauses)}\n")
        f.write("".join(" ".join(map(str, c)) + " 0\n" for c in clauses))
    print(f"wrote {out}: {nv} vars, {len(clauses)} clauses", file=sys.stderr)


if __name__ == "__main__":
    main()

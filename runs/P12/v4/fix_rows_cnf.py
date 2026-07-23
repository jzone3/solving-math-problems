#!/usr/bin/env python3
"""Complete SAT exhaustion of row-neighborhoods around an incumbent.

Given an incumbent array and a subset F of rows to free, emit the T2(n) CNF
with all rows outside F fixed to the incumbent (unit clauses), no symmetry
breaking. UNSAT certifies no valid T2(n) agrees with the incumbent on the
fixed rows; SAT yields a witness.

Usage: fix_rows_cnf.py incumbent_file free_rows_csv out.cnf
"""
import sys

sys.argv_backup = sys.argv


def gen(n, fixed_rows, out):
    nv = 0

    def new():
        nonlocal nv
        nv += 1
        return nv

    x = [[[new() for s in range(n)] for c in range(n)] for r in range(n)]
    cl = []
    for r in range(n):
        for c in range(n):
            cl.append([x[r][c][s] for s in range(n)])
            for s in range(n):
                for t in range(s + 1, n):
                    cl.append([-x[r][c][s], -x[r][c][t]])
    for r in range(n):
        for s in range(n):
            cl.append([x[r][c][s] for c in range(n)])
            for c in range(n):
                for d in range(c + 1, n):
                    cl.append([-x[r][c][s], -x[r][d][s]])
    z1, z2 = {}, {}
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
            p1, p2 = [], []
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
            cl.append(p1)
            for i in range(n):
                for j in range(i + 1, n):
                    cl.append([-p1[i], -p1[j]])
                    cl.append([-p2[i], -p2[j]])
    for r, row in fixed_rows.items():
        for c in range(n):
            cl.append([x[r][c][row[c]]])
    with open(out, "w") as f:
        f.write(f"p cnf {nv} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")


def main():
    inc_file, free_csv, out = sys.argv[1], sys.argv[2], sys.argv[3]
    arr = [[int(x) for x in l.split()] for l in open(inc_file) if l.strip()]
    n = len(arr)
    free = set(int(t) for t in free_csv.split(",")) if free_csv else set()
    fixed = {r: arr[r] for r in range(n) if r not in free}
    gen(n, fixed, out)


if __name__ == "__main__":
    main()

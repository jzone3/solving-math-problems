#!/usr/bin/env python3
"""Independent second CP-SAT model for BTD (differently written encoding),
used to confirm INFEASIBLE results from solve_cpsat.py.

Differences from solve_cpsat.py:
  - single IntVar m[i][j] in {0,1,2}; no boolean expansion
  - row multiplicity counts via m==1 / m==2 reified literals
  - pair inner products via AddMultiplicationEquality on m
  - symmetry breaking: same double-lex principle but implemented over
    base-3 channelled integers (each column of a row pair compared via
    a single big lex integer where V or B small enough, else pairwise).

Usage: solve_cpsat_alt.py V B p1 p2 R K L [max_seconds] [workers]
"""
import sys
from ortools.sat.python import cp_model


def main():
    V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
    assert R == p1 + 2 * p2
    max_s = float(sys.argv[8]) if len(sys.argv) > 8 else 3600
    workers = int(sys.argv[9]) if len(sys.argv) > 9 else 8

    md = cp_model.CpModel()
    m = [[md.NewIntVar(0, 2, f"m{i}_{j}") for j in range(B)] for i in range(V)]

    for i in range(V):
        md.Add(sum(m[i]) == R)
        ones = []
        twos = []
        for j in range(B):
            b1 = md.NewBoolVar("")
            md.Add(m[i][j] == 1).OnlyEnforceIf(b1)
            md.Add(m[i][j] != 1).OnlyEnforceIf(b1.Not())
            b2 = md.NewBoolVar("")
            md.Add(m[i][j] == 2).OnlyEnforceIf(b2)
            md.Add(m[i][j] != 2).OnlyEnforceIf(b2.Not())
            ones.append(b1)
            twos.append(b2)
        md.Add(sum(ones) == p1)
        md.Add(sum(twos) == p2)

    for j in range(B):
        md.Add(sum(m[i][j] for i in range(V)) == K)

    for i in range(V):
        for k in range(i + 1, V):
            prods = []
            for j in range(B):
                p = md.NewIntVar(0, 4, "")
                md.AddMultiplicationEquality(p, [m[i][j], m[k][j]])
                prods.append(p)
            md.Add(sum(prods) == L)

    # double-lex via ternary encoding chunks (pairwise scalar comparison)
    def lex_ge(u, v):
        n = len(u)
        pre = md.NewConstant(1)  # "all previous equal" literal
        pre_true = md.NewBoolVar("")
        md.Add(pre_true == 1)
        prev_eq = pre_true
        md.Add(u[0] >= v[0])
        for t in range(1, n):
            e = md.NewBoolVar("")
            md.Add(u[t - 1] == v[t - 1]).OnlyEnforceIf(e)
            md.Add(u[t - 1] != v[t - 1]).OnlyEnforceIf(e.Not())
            cur = md.NewBoolVar("")
            md.AddBoolAnd([prev_eq, e]).OnlyEnforceIf(cur)
            md.AddBoolOr([prev_eq.Not(), e.Not()]).OnlyEnforceIf(cur.Not())
            md.Add(u[t] >= v[t]).OnlyEnforceIf(cur)
            prev_eq = cur

    for i in range(V - 1):
        lex_ge(m[i], m[i + 1])
    for j in range(B - 1):
        lex_ge([m[i][j] for i in range(V)], [m[i][j + 1] for i in range(V)])

    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = max_s
    sv.parameters.num_workers = workers
    st = sv.Solve(md)
    print("status:", sv.StatusName(st), "wall:", round(sv.WallTime(), 1), "s")
    if st in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        for i in range(V):
            print(" ".join(str(sv.Value(m[i][j])) for j in range(B)))


if __name__ == "__main__":
    main()

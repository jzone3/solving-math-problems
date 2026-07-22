#!/usr/bin/env python3
"""V1 exact ILP/CP-SAT feasibility search for BTD(V,B; p1,p2,R; K,L).

Encoding: booleans x1[i][j] (multiplicity 1), x2[i][j] (multiplicity 2),
x1+x2 <= 1, m = x1 + 2*x2.
Constraints:
  - row i: sum_j x1 = p1, sum_j x2 = p2
  - col j: sum_i (x1 + 2*x2) = K
  - pair (i,k): sum_j [ a*a' + 2*a*b' + 2*b*a' + 4*b*b' ] = L
    where products of booleans are linearized via AND-aux variables.
Symmetry breaking: double-lex (rows non-increasing lexicographically on the
value vector, columns non-increasing lexicographically) — sound for the full
row-perm x col-perm symmetry group (any matrix can be double-lex ordered).

Usage: solve_cpsat.py V B p1 p2 R K L [max_seconds] [workers] [out_file]
Prints SAT + matrix (and writes witness file), UNSAT, or UNKNOWN.
"""
import sys
from ortools.sat.python import cp_model


def build(V, B, p1, p2, K, L, double_lex=True):
    md = cp_model.CpModel()
    x1 = [[md.NewBoolVar(f"x1_{i}_{j}") for j in range(B)] for i in range(V)]
    x2 = [[md.NewBoolVar(f"x2_{i}_{j}") for j in range(B)] for i in range(V)]
    m = [[md.NewIntVar(0, 2, f"m_{i}_{j}") for j in range(B)] for i in range(V)]
    for i in range(V):
        for j in range(B):
            md.Add(x1[i][j] + x2[i][j] <= 1)
            md.Add(m[i][j] == x1[i][j] + 2 * x2[i][j])
    for i in range(V):
        md.Add(sum(x1[i]) == p1)
        md.Add(sum(x2[i]) == p2)
    for j in range(B):
        md.Add(sum(m[i][j] for i in range(V)) == K)

    def AND(a, b):
        v = md.NewBoolVar("")
        md.AddBoolAnd([a, b]).OnlyEnforceIf(v)
        md.AddBoolOr([a.Not(), b.Not()]).OnlyEnforceIf(v.Not())
        return v

    for i in range(V):
        for k in range(i + 1, V):
            terms = []
            for j in range(B):
                a, b, c, d = x1[i][j], x2[i][j], x1[k][j], x2[k][j]
                terms.append(AND(a, c))
                terms.append(2 * AND(a, d))
                terms.append(2 * AND(b, c))
                terms.append(4 * AND(b, d))
            md.Add(sum(terms) == L)

    if double_lex:
        # rows: value vectors lexicographically non-increasing
        for i in range(V - 1):
            add_lex_ge(md, m[i], m[i + 1])
        # cols
        for j in range(B - 1):
            add_lex_ge(md, [m[i][j] for i in range(V)],
                       [m[i][j + 1] for i in range(V)])
    return md, m


def add_lex_ge(md, u, v):
    """u >= v lexicographically, u/v lists of int vars with small domains."""
    n = len(u)
    # eq[t] = (u[0..t] == v[0..t])
    eq = [md.NewBoolVar("") for _ in range(n)]
    for t in range(n):
        e = md.NewBoolVar("")
        md.Add(u[t] == v[t]).OnlyEnforceIf(e)
        md.Add(u[t] != v[t]).OnlyEnforceIf(e.Not())
        if t == 0:
            md.AddImplication(eq[0], e)
            md.AddImplication(e, eq[0])
        else:
            md.AddBoolAnd([eq[t - 1], e]).OnlyEnforceIf(eq[t])
            md.AddBoolOr([eq[t - 1].Not(), e.Not()]).OnlyEnforceIf(eq[t].Not())
    # u[0] >= v[0]; and eq[t-1] -> u[t] >= v[t]
    md.Add(u[0] >= v[0])
    for t in range(1, n):
        md.Add(u[t] >= v[t]).OnlyEnforceIf(eq[t - 1])


def main():
    V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
    assert R == p1 + 2 * p2
    max_s = float(sys.argv[8]) if len(sys.argv) > 8 else 600
    workers = int(sys.argv[9]) if len(sys.argv) > 9 else 8
    out = sys.argv[10] if len(sys.argv) > 10 else None
    md, m = build(V, B, p1, p2, K, L)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = max_s
    sv.parameters.num_workers = workers
    sv.parameters.log_search_progress = True
    st = sv.Solve(md)
    print("status:", sv.StatusName(st), "wall:", round(sv.WallTime(), 1), "s")
    if st in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        rows = [" ".join(str(sv.Value(m[i][j])) for j in range(B)) for i in range(V)]
        print("SAT")
        print("\n".join(rows))
        if out:
            with open(out, "w") as f:
                f.write("\n".join(rows) + "\n")
    elif st == cp_model.INFEASIBLE:
        print("UNSAT (with double-lex symmetry breaking — sound, so truly nonexistent)")
    else:
        print("UNKNOWN")


if __name__ == "__main__":
    main()

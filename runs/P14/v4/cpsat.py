#!/usr/bin/env python3
"""P14: complete CP-SAT feasibility for BTD(V,B; rho1,rho2,R; K,Lam).

Boolean multiplicity expansion: per cell, a[i][j] = [m>=1], b[i][j] = [m==2],
b <= a, m = a + b.
Constraints:
  rows: sum_j a = rho1+rho2, sum_j b = rho2
  cols: sum_i (a+b) = K
  pairs i<k: sum_j (a_i+b_i)(a_k+b_k) = Lam, linearized with AND aux vars
    per (pair, column): m_i*m_k = aa + ab + ba + bb where each term is an AND.
Symmetry breaking: rows and columns are interchangeable -> double-lex:
  adjacent rows lex >=, adjacent columns lex >= on the (a,b) encoding as
  digit m in {0,1,2}.
Usage: cpsat.py V B rho1 rho2 K Lam [max_seconds] [workers]
Prints SOLVED + matrix, INFEASIBLE (=> nonexistence!), or UNKNOWN.
"""
import sys
from ortools.sat.python import cp_model


def main():
    V, B, r1, r2, K, Lam = map(int, sys.argv[1:7])
    max_s = float(sys.argv[7]) if len(sys.argv) > 7 else 3600.0
    workers = int(sys.argv[8]) if len(sys.argv) > 8 else 8
    m = cp_model.CpModel()
    a = [[m.NewBoolVar(f"a{i}_{j}") for j in range(B)] for i in range(V)]
    b = [[m.NewBoolVar(f"b{i}_{j}") for j in range(B)] for i in range(V)]
    for i in range(V):
        for j in range(B):
            m.AddImplication(b[i][j], a[i][j])
        m.Add(sum(a[i]) == r1 + r2)
        m.Add(sum(b[i]) == r2)
    for j in range(B):
        m.Add(sum(a[i][j] + b[i][j] for i in range(V)) == K)
    # pair constraints
    for i in range(V):
        for k in range(i + 1, V):
            terms = []
            for j in range(B):
                # product (a_i+b_i)*(a_k+b_k); note b<=a so m in {0,1,2}
                for (x, y) in ((a[i][j], a[k][j]), (a[i][j], b[k][j]),
                               (b[i][j], a[k][j]), (b[i][j], b[k][j])):
                    t = m.NewBoolVar("")
                    m.AddMultiplicationEquality(t, [x, y])
                    terms.append(t)
            m.Add(sum(terms) == Lam)
    # cell value as integer digit for lex ordering
    val = [[m.NewIntVar(0, 2, f"v{i}_{j}") for j in range(B)] for i in range(V)]
    for i in range(V):
        for j in range(B):
            m.Add(val[i][j] == a[i][j] + b[i][j])
    # double lex: rows non-increasing, columns non-increasing
    def lex_ge(xs, ys):
        # xs >=lex ys via prefix equality booleans
        n = len(xs)
        eq = m.NewBoolVar("")  # dummy pattern below instead
        # standard encoding: e_0..e_n, e_0 = true; e_t & (x_t >= y_t); e_{t+1} <-> e_t & x_t==y_t
        e_prev = None
        for t in range(n):
            if e_prev is None:
                m.Add(xs[t] >= ys[t])
                e = m.NewBoolVar("")
                m.Add(xs[t] == ys[t]).OnlyEnforceIf(e)
                m.Add(xs[t] != ys[t]).OnlyEnforceIf(e.Not())
                e_prev = e
            else:
                m.Add(xs[t] >= ys[t]).OnlyEnforceIf(e_prev)
                e = m.NewBoolVar("")
                eq_t = m.NewBoolVar("")
                m.Add(xs[t] == ys[t]).OnlyEnforceIf(eq_t)
                m.Add(xs[t] != ys[t]).OnlyEnforceIf(eq_t.Not())
                m.AddBoolAnd([e_prev, eq_t]).OnlyEnforceIf(e)
                m.AddBoolOr([e_prev.Not(), eq_t.Not()]).OnlyEnforceIf(e.Not())
                e_prev = e
    for i in range(V - 1):
        lex_ge([val[i][j] for j in range(B)], [val[i + 1][j] for j in range(B)])
    for j in range(B - 1):
        lex_ge([val[i][j] for i in range(V)], [val[i][j + 1] for i in range(V)])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_s
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = True
    st = solver.Solve(m)
    if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
        print("SOLVED")
        for i in range(V):
            print("".join(str(solver.Value(val[i][j])) for j in range(B)))
    elif st == cp_model.INFEASIBLE:
        print("INFEASIBLE")
    else:
        print("UNKNOWN")


if __name__ == "__main__":
    main()

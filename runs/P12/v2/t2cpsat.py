#!/usr/bin/env python3
"""CP-SAT model for Tuscan-2 squares T2(n) in standard form.

Standard form (complete for existence, see NOTES.md): row 0 = identity,
row r starts with symbol r (first column of any T2 square is a permutation
after relabelling + row sorting).

Variables: x[r][c] = symbol at row r, column c (integer 0..n-1), with
boolean channeling b[r][c][s]. Constraints:
  - AllDifferent per row; x[r][0] = r; row 0 fixed to identity.
  - dist-1: for each ordered pair (a,b), exactly one (r,c) with x[r][c]=a,
    x[r][c+1]=b  (pair indicator literals via AddBoolAnd/reification).
  - dist-2: at most one occurrence.
  - last column all-different (implied, added as redundant strengthening).

Usage: t2cpsat.py n [time_limit_s] [workers] [seed]
Prints solution rows if found; exit status prints SAT/UNSAT/UNKNOWN.
"""
import sys
from ortools.sat.python import cp_model


def build(n):
    m = cp_model.CpModel()
    x = [[m.NewIntVar(0, n - 1, f"x{r}_{c}") for c in range(n)] for r in range(n)]
    b = [[[m.NewBoolVar(f"b{r}_{c}_{s}") for s in range(n)] for c in range(n)]
         for r in range(n)]
    for r in range(n):
        m.AddAllDifferent(x[r])
        for c in range(n):
            # channeling
            for s in range(n):
                m.Add(x[r][c] == s).OnlyEnforceIf(b[r][c][s])
                m.Add(x[r][c] != s).OnlyEnforceIf(b[r][c][s].Not())
            m.AddExactlyOne(b[r][c])
    # standard form
    for c in range(n):
        m.Add(x[0][c] == c)
    for r in range(n):
        m.Add(x[r][0] == r)
    # redundant: each column-0 / column-(n-1) permutation
    m.AddAllDifferent([x[r][n - 1] for r in range(n)])
    # pair occurrence literals
    for a in range(n):
        for bb in range(n):
            if a == bb:
                continue
            occ1 = []
            occ2 = []
            for r in range(n):
                for c in range(n - 1):
                    v = m.NewBoolVar(f"p1_{a}_{bb}_{r}_{c}")
                    m.AddBoolAnd([b[r][c][a], b[r][c + 1][bb]]).OnlyEnforceIf(v)
                    m.AddBoolOr([b[r][c][a].Not(), b[r][c + 1][bb].Not()]).OnlyEnforceIf(v.Not())
                    occ1.append(v)
                for c in range(n - 2):
                    v = m.NewBoolVar(f"p2_{a}_{bb}_{r}_{c}")
                    m.AddBoolAnd([b[r][c][a], b[r][c + 2][bb]]).OnlyEnforceIf(v)
                    m.AddBoolOr([b[r][c][a].Not(), b[r][c + 2][bb].Not()]).OnlyEnforceIf(v.Not())
                    occ2.append(v)
            m.AddExactlyOne(occ1)
            m.AddAtMostOne(occ2)
    return m, x


def main():
    n = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 3600
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    m, x = build(n)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.log_search_progress = True
    st = solver.Solve(m)
    print("status:", solver.StatusName(st))
    if st in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        for r in range(n):
            print(" ".join(str(solver.Value(x[r][c])) for c in range(n)))


if __name__ == "__main__":
    main()

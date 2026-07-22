#!/usr/bin/env python3
"""Exact CP-SAT decision model for T2(n).

Encoding: pos[r][a] = column of symbol a in row r (AllDifferent per row).
Booleans adj1[r][a][b] <=> pos[r][b] == pos[r][a] + 1; sum_r adj1 == 1 per pair.
Booleans adj2[r][a][b] <=> pos[r][b] == pos[r][a] + 2; sum_r adj2 <= 1 per pair.

Symmetry breaking (valid up to symbol relabeling + row permutation):
  - row 0 is the identity permutation  => pos[0][a] = a
  - column 0 is the identity           => pos[r][r] = 0
(first column of any T2(n) is a permutation: each symbol has in-degree n-1
at distance 1, appears n times, hence is row-initial exactly once.)

Usage: cpsat_exact.py n [time_limit_s] [workers]
Exit prints SAT + witness file, UNSAT (proved), or UNKNOWN.
"""
import sys

from ortools.sat.python import cp_model

from t2_common import write_witness


def build(n, sym_break=True):
    m = cp_model.CpModel()
    pos = [[m.NewIntVar(0, n - 1, f"p{r}_{a}") for a in range(n)] for r in range(n)]
    for r in range(n):
        m.AddAllDifferent(pos[r])
    if sym_break:
        for a in range(n):
            m.Add(pos[0][a] == a)
        for r in range(1, n):
            m.Add(pos[r][r] == 0)
            m.Add(pos[r][0] != 0)
    adj1 = {}
    adj2 = {}
    for r in range(n):
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                v1 = m.NewBoolVar(f"a1_{r}_{a}_{b}")
                m.Add(pos[r][b] - pos[r][a] == 1).OnlyEnforceIf(v1)
                m.Add(pos[r][b] - pos[r][a] != 1).OnlyEnforceIf(v1.Not())
                adj1[r, a, b] = v1
                v2 = m.NewBoolVar(f"a2_{r}_{a}_{b}")
                m.Add(pos[r][b] - pos[r][a] == 2).OnlyEnforceIf(v2)
                m.Add(pos[r][b] - pos[r][a] != 2).OnlyEnforceIf(v2.Not())
                adj2[r, a, b] = v2
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            m.AddExactlyOne([adj1[r, a, b] for r in range(n)])
            m.AddAtMostOne([adj2[r, a, b] for r in range(n)])
    return m, pos


def main():
    n = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 3600
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    m, pos = build(n)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tl
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = True
    res = s.Solve(m)
    print("status:", s.StatusName(res), "walltime:", s.WallTime())
    if res in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        arr = [[0] * n for _ in range(n)]
        for r in range(n):
            for a in range(n):
                arr[r][s.Value(pos[r][a])] = a
        out = f"witness_T2_{n}.txt"
        write_witness(arr, out)
        print("SAT — witness written to", out)
    elif res == cp_model.INFEASIBLE:
        print(f"UNSAT — T2({n}) does not exist (with symmetry breaking; valid up to iso)")
    else:
        print("UNKNOWN — time limit reached")


if __name__ == "__main__":
    main()

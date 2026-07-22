#!/usr/bin/env python3
"""CP-SAT optimization model for T2(n): minimize violation count.

Same pos/adj encoding as cpsat_exact.py, but exactly-once/at-most-once are
softened: for each ordered pair, excess1 >= (#dist-1 occurrences) - 1 and
excess2 >= (#dist-2 occurrences) - 1; minimize sum(excess1) + sum(excess2).
Objective 0 <=> valid T2(n). Supports hinting from a witness/partial file
(anneal output) so CP-SAT's built-in LNS workers repair near-solutions.

Usage: cpsat_opt.py n [time_limit_s] [workers] [hint_file]
"""
import sys

from ortools.sat.python import cp_model

from t2_common import write_witness


def main():
    n = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 3600
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    hint_file = sys.argv[4] if len(sys.argv) > 4 else None

    m = cp_model.CpModel()
    pos = [[m.NewIntVar(0, n - 1, f"p{r}_{a}") for a in range(n)] for r in range(n)]
    for r in range(n):
        m.AddAllDifferent(pos[r])
    adj1, adj2 = {}, {}
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
    penalties = []
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            e1 = m.NewIntVar(0, n, f"e1_{a}_{b}")
            m.Add(sum(adj1[r, a, b] for r in range(n)) - 1 <= e1)
            penalties.append(e1)
            e2 = m.NewIntVar(0, n, f"e2_{a}_{b}")
            m.Add(sum(adj2[r, a, b] for r in range(n)) - 1 <= e2)
            penalties.append(e2)
    m.Minimize(sum(penalties))

    if hint_file:
        with open(hint_file) as f:
            arr = [[int(x) for x in line.split()] for line in f if line.strip()]
        for r in range(n):
            for c in range(n):
                m.AddHint(pos[r][arr[r][c]], c)

    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tl
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = True
    res = s.Solve(m)
    print("status:", s.StatusName(res), "obj:", s.ObjectiveValue() if res in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
          "bound:", s.BestObjectiveBound(), "walltime:", s.WallTime())
    if res in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        arr = [[0] * n for _ in range(n)]
        for r in range(n):
            for a in range(n):
                arr[r][s.Value(pos[r][a])] = a
        out = f"opt_T2_{n}_obj{int(s.ObjectiveValue())}.txt"
        write_witness(arr, out)
        print("best array written to", out)
        if s.ObjectiveValue() == 0:
            print("SOLVED — objective 0, valid T2 witness")


if __name__ == "__main__":
    main()

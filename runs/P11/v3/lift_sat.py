#!/usr/bin/env python3
"""ICW-lift search for CW(n, k) via CP-SAT.

Fix a contraction w (an ICW_d(m,k), n = d*m) and search for a ternary vector a
on Z_n with fiber sums sum_{i ≡ j mod m} a_i = w_j and all PACF(t) = 0.
Because every CW(n,k) contracts to SOME ICW, running over all inequivalent
contraction ICWs is a complete search of the cell (soundness of the multiplier
normalization comes from AGZ Thm 4.1: some translate/multiplier image of the
contraction is <t>-fixed, and translating/multiplier-imaging the full CW
realizes exactly that action on the contraction... more precisely the Z_n
multiplier u acts as u mod m and the shift s acts as s mod m on w; shifts by
multiples of m and multipliers ≡ 1 mod m stabilize w, so we must ALSO consider
inequivalent w under the lifted action — we simply run all <t>-fixed w's,
which covers every equivalence class).

Usage: python3 lift_sat.py n m k icw_index [timeout_s]
  (enumerates <t>-fixed ICWs internally, t auto-chosen; icw_index=-1 -> all)
"""
import sys
from ortools.sat.python import cp_model
from icw_enum import enum_fixed

sys.path.insert(0, "../../../solutions/P11")
from verify import check, is_proper

MULT = {(35, 36): 4, (13, 36): 3, (7, 36): 2, (120, 49): 7}


def solve(n, m, k, w, timeout=600, workers=3):
    d = n // m
    model = cp_model.CpModel()
    a = [model.NewIntVar(-1, 1, f"a{i}") for i in range(n)]
    for j in range(m):
        model.Add(sum(a[i] for i in range(j, n, m)) == w[j])
    # products via aux int vars
    prod = {}
    for t in range(1, n // 2 + 1):
        terms = []
        for i in range(n):
            key = tuple(sorted((i, (i + t) % n)))
            if key not in prod:
                p = model.NewIntVar(-1, 1, f"p{key}")
                model.AddMultiplicationEquality(p, [a[key[0]], a[key[1]]])
                prod[key] = p
            terms.append(prod[key])
        model.Add(sum(terms) == 0)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = workers
    st = solver.Solve(model)
    if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
        av = [solver.Value(x) for x in a]
        P = [i for i, v in enumerate(av) if v == 1]
        N = [i for i, v in enumerate(av) if v == -1]
        check(n, k, P, N, proper=False)
        return P, N, is_proper(n, P, N)
    return "UNSAT" if st == cp_model.INFEASIBLE else "UNKNOWN"


if __name__ == "__main__":
    n, m, k = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    idx = int(sys.argv[4]) if len(sys.argv) > 4 else -1
    tmo = float(sys.argv[5]) if len(sys.argv) > 5 else 600
    t = MULT[(m, k)]
    _, sols = enum_fixed(m, n // m, k, t)
    print(f"{len(sols)} <{t}>-fixed ICW_{n//m}({m},{k}) contractions")
    todo = sols if idx < 0 else [sols[idx]]
    for wi, w in enumerate(todo):
        r = solve(n, m, k, list(w), timeout=tmo)
        print(f"ICW #{wi} {w}: ", end="")
        if isinstance(r, str):
            print(r, flush=True)
        else:
            print(f"SOLVED proper={r[2]} P={r[0]} N={r[1]}", flush=True)

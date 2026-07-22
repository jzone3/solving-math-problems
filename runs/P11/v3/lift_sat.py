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
    # weight constraint: sum |a_i| = k  (PACF(0) = k)
    absv = []
    for i in range(n):
        b = model.NewIntVar(0, 1, f"b{i}")
        model.AddAbsEquality(b, a[i])
        absv.append(b)
    model.Add(sum(absv) == k)
    # implied: for EVERY proper divisor m2 of n, the mod-m2 contraction is an
    # ICW_{n/m2}(m2, k): all characters of Z_m2 lift, so |contraction-hat|^2 = k
    # everywhere (DC included: row sum = ±s), i.e. autocorrelation = k*delta_0.
    s = int(round(k ** 0.5))
    rs = model.NewIntVar(-s, s, "rowsum")
    model.Add(rs == sum(a))
    model.AddAllowedAssignments([rs], [(-s,), (s,)])
    for m2 in range(2, n):
        if n % m2:
            continue
        d2 = n // m2
        c = [model.NewIntVar(-d2, d2, f"c{m2}_{j}") for j in range(m2)]
        for j in range(m2):
            model.Add(c[j] == sum(a[i] for i in range(j, n, m2)))
        cp = {}
        for t in range(0, m2 // 2 + 1):
            terms = []
            for i in range(m2):
                kk = tuple(sorted((i, (i + t) % m2)))
                if kk not in cp:
                    p = model.NewIntVar(-d2 * d2, d2 * d2, f"cp{m2}_{kk}")
                    model.AddMultiplicationEquality(p, [c[kk[0]], c[kk[1]]])
                    cp[kk] = p
                terms.append(cp[kk])
            model.Add(sum(terms) == (k if t == 0 else 0))
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

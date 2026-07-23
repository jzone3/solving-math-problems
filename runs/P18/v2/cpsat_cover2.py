#!/usr/bin/env python3
"""CP-SAT model with the exact linear density cut (round 2).

Sound strengthening: any covering of Z/L satisfies Sum_{used m} L/m >= L
(union bound, exact integers since m | L). Added as a single linear constraint,
which subsumes all forced-use / knapsack clauses and lets CP-SAT propagate the
density budget globally. Plus the same symmetry breaking as before.

Usage: python3 cpsat_cover2.py L max_seconds workers
"""
import sys
from fractions import Fraction
from sympy import isprime, divisors
from ortools.sat.python import cp_model

def main():
    L = int(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    P = sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)
    dens = sum(Fraction(1, m) for m in P)
    print(f"L={L} |pool|={len(P)} density={float(dens):.6f}", flush=True)
    if dens < 1:
        print("RESULT UNSAT trivially (density < 1)")
        return
    md = cp_model.CpModel()
    sel, used = {}, {}
    for m in P:
        if m == P[0]:
            allowed = [0]
        elif len(P) > 1 and m == P[1] and P[0] == 4 and P[1] == 6:
            allowed = [0, 1]
        else:
            allowed = range(m)
        lits = []
        for a in allowed:
            v = md.NewBoolVar(f"s{m}_{a}")
            sel[(m, a)] = v
            lits.append(v)
        md.AddAtMostOne(lits)
        u = md.NewBoolVar(f"u{m}")
        used[m] = u
        md.AddBoolOr(lits).OnlyEnforceIf(u)
        md.Add(sum(lits) == 0).OnlyEnforceIf(u.Not())
    # exact density cut
    md.Add(sum(used[m] * (L // m) for m in P) >= L)
    for x in range(L):
        md.AddBoolOr([sel[(m, x % m)] for m in P if (m, x % m) in sel])
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = budget
    sol.parameters.num_workers = workers
    st = sol.Solve(md)
    name = sol.StatusName(st)
    print(f"status={name} wall={sol.WallTime():.1f}s", flush=True)
    if name == "INFEASIBLE":
        print(f"RESULT UNSAT: no covering with distinct p-1 moduli (p>=5) dividing {L}")
    elif name in ("FEASIBLE", "OPTIMAL"):
        W = sorted(((a, m) for (m, a), v in sel.items() if sol.Value(v)), key=lambda t: t[1])
        print("witness:", W)
        covered = bytearray(L)
        ms = [m for _, m in W]
        assert len(set(ms)) == len(ms)
        for a, m in W:
            for x in range(a, L, m):
                covered[x] = 1
        print("independent re-verification:", "PASS" if all(covered) else "FAIL")
    else:
        print("RESULT UNKNOWN (timeout)")

if __name__ == "__main__":
    main()

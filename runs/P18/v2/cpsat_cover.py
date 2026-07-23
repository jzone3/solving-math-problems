#!/usr/bin/env python3
"""CP-SAT (OR-Tools) variant of the Z/L covering search — independent second engine.

Same semantics as sat_cover.py: does a covering system with distinct moduli
(all m | L, m = p-1, p prime >= 5) exist? Integer model:
  * for each pool modulus m: use[m] in {0,1}, res[m] in [0, m-1];
  * coverage: for each x in Z/L: sum over m of (use[m] AND res[m] == x mod m) >= 1,
    channelled through literals sel[m][a] <=> (use[m] & res[m]==a).
Symmetry breaking identical to sat_cover.py (a_4 = 0; a_6 in {0,1}).
If SAT, prints witness and re-verifies exactly.

Usage: python3 cpsat_cover.py L [max_seconds] [workers]
"""
import sys
from fractions import Fraction
from sympy import isprime, divisors
from ortools.sat.python import cp_model

def pool_for(L):
    return sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)

def main():
    L = int(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 3600.0
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    P = pool_for(L)
    dens = sum(Fraction(1, m) for m in P)
    print(f"L={L} |pool|={len(P)} density={float(dens):.6f}", flush=True)
    if dens < 1:
        print("RESULT UNSAT trivially (density < 1)")
        return
    md = cp_model.CpModel()
    sel = {}
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

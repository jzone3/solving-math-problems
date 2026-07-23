#!/usr/bin/env python3
"""LNS-style two-phase search for (v,6,1)-PMDs (P13 V3).

Phase 1 (packing relaxation): same block structure, but each (ordered pair,
distance) may be covered AT MOST once; maximize the number of covered
(pair,distance) slots. CP-SAT's internal portfolio (incl. LNS workers) drives
this. A perfect packing (objective == 5*v*(v-1)) IS a PMD.

Phase 2: feed the best packing found as hints to the exact model
(pmd_cpsat.solve) and run it hard.

Usage: pmd_lns.py v [t1] [t2] [workers] [seed]
"""
import sys
from ortools.sat.python import cp_model
import pmd_cpsat

K = 6


def pack(v, time_limit, workers, seed):
    b = v * (v - 1) // K
    m = cp_model.CpModel()
    x = [[[m.NewBoolVar("") for s in range(v)] for p in range(K)] for bl in range(b)]
    for bl in range(b):
        for p in range(K):
            m.AddExactlyOne(x[bl][p])
        for s in range(v):
            m.AddAtMostOne(x[bl][p][s] for p in range(K))
    c = [[m.NewIntVar(0, v - 1, "") for p in range(K)] for bl in range(b)]
    for bl in range(b):
        for p in range(K):
            m.Add(c[bl][p] == sum(s * x[bl][p][s] for s in range(v)))
    cov = []
    for t in range(1, K):
        for u in range(v):
            for w in range(v):
                if u == w:
                    continue
                lits = []
                for bl in range(b):
                    for p in range(K):
                        e = m.NewBoolVar("")
                        m.AddBoolAnd([x[bl][p][u], x[bl][(p + t) % K][w]]).OnlyEnforceIf(e)
                        m.AddBoolOr([x[bl][p][u].Not(), x[bl][(p + t) % K][w].Not(), e])
                        lits.append(e)
                m.AddAtMostOne(lits)
                g = m.NewBoolVar("")
                m.AddMaxEquality(g, lits)
                cov.append(g)
    for p in range(K):
        m.Add(c[0][p] == p)
    for bl in range(1, b):
        for p in range(1, K):
            m.Add(c[bl][0] < c[bl][p])
    m.Maximize(sum(cov))
    return m, c, cov, b


def pack_soft(v, time_limit, workers, seed):
    """Soft variant: coverage counts unconstrained; minimize sum |count(pair,t) - 1|.
    Always feasible, so LNS can walk toward deviation 0 (= a PMD)."""
    b = v * (v - 1) // K
    m = cp_model.CpModel()
    x = [[[m.NewBoolVar("") for s in range(v)] for p in range(K)] for bl in range(b)]
    for bl in range(b):
        for p in range(K):
            m.AddExactlyOne(x[bl][p])
        for s in range(v):
            m.AddAtMostOne(x[bl][p][s] for p in range(K))
    c = [[m.NewIntVar(0, v - 1, "") for p in range(K)] for bl in range(b)]
    for bl in range(b):
        for p in range(K):
            m.Add(c[bl][p] == sum(s * x[bl][p][s] for s in range(v)))
    devs = []
    for t in range(1, K):
        for u in range(v):
            for w in range(v):
                if u == w:
                    continue
                lits = []
                for bl in range(b):
                    for p in range(K):
                        e = m.NewBoolVar("")
                        m.AddBoolAnd([x[bl][p][u], x[bl][(p + t) % K][w]]).OnlyEnforceIf(e)
                        m.AddBoolOr([x[bl][p][u].Not(), x[bl][(p + t) % K][w].Not(), e])
                        lits.append(e)
                cnt = m.NewIntVar(0, b * K, "")
                m.Add(cnt == sum(lits))
                d = m.NewIntVar(0, b * K, "")
                m.Add(d >= cnt - 1)
                m.Add(d >= 1 - cnt)
                devs.append(d)
    for p in range(K):
        m.Add(c[0][p] == p)
    for bl in range(1, b):
        for p in range(1, K):
            m.Add(c[bl][0] < c[bl][p])
    m.Minimize(sum(devs))
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_limit
    sol.parameters.num_workers = workers
    sol.parameters.random_seed = seed
    st = sol.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        obj = int(sol.ObjectiveValue())
        blocks = [[sol.Value(c[bl][p]) for p in range(K)] for bl in range(b)]
        return obj, blocks
    return None, None


if __name__ == "__main__":
    v = int(sys.argv[1])
    t1 = float(sys.argv[2]) if len(sys.argv) > 2 else 1200
    t2 = float(sys.argv[3]) if len(sys.argv) > 3 else 1800
    wk = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    obj, blocks = pack_soft(v, t1, wk, seed)
    print(f"v={v} soft-packing deviation={obj} (0 would be a PMD)", flush=True)
    if obj == 0:
        print("SOLUTION (deviation 0)")
        for blk in blocks:
            print(" ".join(map(str, blk)))
        sys.exit(0)
    res, sol_blocks, wt = pmd_cpsat.solve(v, t2, wk, first_occ=False, seed=seed,
                                          hint_blocks=blocks)
    print(f"v={v} exact-with-hint result={res} wall={wt:.1f}s")
    if sol_blocks:
        print("SOLUTION")
        for blk in sol_blocks:
            print(" ".join(map(str, blk)))

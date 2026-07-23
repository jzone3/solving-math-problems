#!/usr/bin/env python3
"""CP-SAT model for (v,6,1)-perfect Mendelsohn designs (P13, variant V3: CP + LNS).

A (v,k,1)-PMD is a collection of b = v(v-1)/k cyclically ordered k-tuples of a
v-set such that for every t = 1..k-1, every ordered pair (x,y) of distinct
points is t-apart in exactly one block.

Encoding (booleans): x[b][p][s] <=> block b position p holds symbol s.
 - one symbol per cell, all symbols in a block distinct
 - each symbol used exactly v-1 times globally
 - for each t in 1..5 and ordered pair (u,w), u != w:
     exactly one (b,p) with x[b][p][u] and x[b][(p+t)%6][w]
   via product aux vars e[b][p][t][u][w].
Symmetry breaking:
 - block 0 fixed to (0,1,2,3,4,5)
 - each block rotated so position 0 is the block minimum
 - blocks strictly ordered by (cell0, cell1) (valid: distance-1 pairs unique)
 - optional: symbols >= 6 first appear in increasing order

Usage: pmd_cpsat.py v [time_limit_s] [workers] [--no-firstocc] [--seed N] [--hint file]
Prints SOLUTION rows (one block per line) on success, or UNSAT/UNKNOWN.
"""
import sys
import json
from ortools.sat.python import cp_model

K = 6


def build(v, first_occ=True):
    b = v * (v - 1) // K
    m = cp_model.CpModel()
    x = [[[m.NewBoolVar(f"x_{bl}_{p}_{s}") for s in range(v)] for p in range(K)]
         for bl in range(b)]
    # one-hot cells
    for bl in range(b):
        for p in range(K):
            m.AddExactlyOne(x[bl][p])
    # distinct symbols within a block
    for bl in range(b):
        for s in range(v):
            m.AddAtMostOne(x[bl][p][s] for p in range(K))
    # symbol counts: each symbol in exactly v-1 cells
    for s in range(v):
        m.Add(sum(x[bl][p][s] for bl in range(b) for p in range(K)) == v - 1)
    # integer views for ordering constraints
    c = [[m.NewIntVar(0, v - 1, f"c_{bl}_{p}") for p in range(K)] for bl in range(b)]
    for bl in range(b):
        for p in range(K):
            m.Add(c[bl][p] == sum(s * x[bl][p][s] for s in range(v)))
    # pair coverage
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
                m.AddExactlyOne(lits)
    # symmetry breaking
    for p in range(K):  # block 0 = (0..5)
        m.Add(c[0][p] == p)
    for bl in range(1, b):  # rotation: pos 0 is block min
        for p in range(1, K):
            m.Add(c[bl][0] < c[bl][p])
    keys = [m.NewIntVar(0, v * v - 1, f"key_{bl}") for bl in range(b)]
    for bl in range(b):
        m.Add(keys[bl] == c[bl][0] * v + c[bl][1])
    for bl in range(b - 1):
        m.Add(keys[bl] < keys[bl + 1])
    if first_occ and v > K:
        # symbols 6..v-1 first appear in increasing order across flattened cells
        n = b * K
        seen = [[m.NewBoolVar(f"seen_{s}_{t}") for t in range(n)] for s in range(K, v)]
        for si, s in enumerate(range(K, v)):
            for t in range(n):
                bl, p = divmod(t, K)
                prev = seen[si][t - 1] if t > 0 else None
                # seen[s][t] == prev OR x[bl][p][s]
                terms = [x[bl][p][s]] + ([prev] if prev is not None else [])
                m.AddMaxEquality(seen[si][t], terms)
        for si in range(1, v - K):
            for t in range(n):
                m.AddImplication(seen[si][t], seen[si - 1][t])
    return m, x, c, b


def solve(v, time_limit=600, workers=8, first_occ=True, seed=0, hint_blocks=None,
          log=False):
    m, x, c, b = build(v, first_occ)
    if hint_blocks:
        for bl, blk in enumerate(hint_blocks):
            for p, s in enumerate(blk):
                m.AddHint(c[bl][p], s)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_limit
    sol.parameters.num_workers = workers
    sol.parameters.random_seed = seed
    sol.parameters.log_search_progress = log
    st = sol.Solve(m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        blocks = [[sol.Value(c[bl][p]) for p in range(K)] for bl in range(b)]
        return "SAT", blocks, sol.WallTime()
    if st == cp_model.INFEASIBLE:
        return "UNSAT", None, sol.WallTime()
    return "UNKNOWN", None, sol.WallTime()


if __name__ == "__main__":
    v = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    wk = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    fo = "--no-firstocc" not in sys.argv
    seed = 0
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])
    hint = None
    if "--hint" in sys.argv:
        hint = json.load(open(sys.argv[sys.argv.index("--hint") + 1]))
    res, blocks, wt = solve(v, tl, wk, fo, seed, hint, log=("--log" in sys.argv))
    print(f"v={v} result={res} wall={wt:.1f}s")
    if blocks:
        print("SOLUTION")
        for blk in blocks:
            print(" ".join(map(str, blk)))

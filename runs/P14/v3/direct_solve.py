#!/usr/bin/env python3
"""Direct V x B matrix CP-SAT model for the open BTD instances, with double-lex
symmetry breaking (columns non-increasing lexicographically, rows likewise).

Usage: direct_solve.py INSTANCE TIMELIMIT_S [WORKERS]
"""
import sys, json, os
from ortools.sat.python import cp_model
from km_solve import INSTANCES

def solve(inst_id, tl, workers=8):
    p = INSTANCES[inst_id]
    V, B, r1, r2, K, Lam = p['V'], p['B'], p['r1'], p['r2'], p['K'], p['Lam']
    model = cp_model.CpModel()
    a = [[model.NewBoolVar(f"a{i}_{j}") for j in range(B)] for i in range(V)]  # mult==1
    b = [[model.NewBoolVar(f"b{i}_{j}") for j in range(B)] for i in range(V)]  # mult==2
    m = [[model.NewIntVar(0, 2, f"m{i}_{j}") for j in range(B)] for i in range(V)]
    for i in range(V):
        for j in range(B):
            model.Add(a[i][j] + b[i][j] <= 1)
            model.Add(m[i][j] == a[i][j] + 2 * b[i][j])
    for j in range(B):
        model.Add(sum(m[i][j] for i in range(V)) == K)
    for i in range(V):
        model.Add(sum(a[i]) == r1)
        model.Add(sum(b[i]) == r2)
    # pairwise inner products
    for i in range(V):
        for k in range(i + 1, V):
            terms = []
            for j in range(B):
                for (x, wx) in ((a[i][j], 1), (b[i][j], 2)):
                    for (y, wy) in ((a[k][j], 1), (b[k][j], 2)):
                        t = model.NewBoolVar("")
                        model.AddBoolAnd([x, y]).OnlyEnforceIf(t)
                        model.AddBoolOr([x.Not(), y.Not()]).OnlyEnforceIf(t.Not())
                        terms.append(wx * wy * t)
            model.Add(sum(terms) == Lam)
    # double-lex symmetry breaking: adjacent columns and adjacent rows
    def lex_ge(seq1, seq2):  # seq1 >= seq2 lexicographically, entries IntVars in 0..2
        # compare base-3 numbers chunkwise (3^18 < 2^29 keeps coefficients safe)
        n = len(seq1)
        CH = 18
        prev_eq = model.NewConstant(1)
        for s in range(0, n, CH):
            c1 = seq1[s:s + CH]; c2 = seq2[s:s + CH]
            w = [3 ** (len(c1) - 1 - t) for t in range(len(c1))]
            n1 = sum(wi * v for wi, v in zip(w, c1))
            n2 = sum(wi * v for wi, v in zip(w, c2))
            ge = model.NewBoolVar(""); gt = model.NewBoolVar(""); eqv = model.NewBoolVar("")
            model.Add(n1 >= n2).OnlyEnforceIf(ge)
            model.Add(n1 < n2).OnlyEnforceIf(ge.Not())
            model.Add(n1 > n2).OnlyEnforceIf(gt)
            model.Add(n1 <= n2).OnlyEnforceIf(gt.Not())
            model.Add(n1 == n2).OnlyEnforceIf(eqv)
            model.Add(n1 != n2).OnlyEnforceIf(eqv.Not())
            # if all previous chunks equal, this chunk must be >=
            model.AddImplication(prev_eq, ge)
            new_eq = model.NewBoolVar("")
            model.AddBoolAnd([prev_eq, eqv]).OnlyEnforceIf(new_eq)
            model.AddBoolOr([prev_eq.Not(), eqv.Not()]).OnlyEnforceIf(new_eq.Not())
            prev_eq = new_eq
    for j in range(B - 1):
        lex_ge([m[i][j] for i in range(V)], [m[i][j + 1] for i in range(V)])
    for i in range(V - 1):
        lex_ge(m[i], m[i + 1])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_workers = workers
    st = solver.Solve(model)
    name = solver.StatusName(st)
    print(f"direct inst{inst_id} status={name} time={solver.WallTime():.1f}s", flush=True)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        mat = [[solver.Value(m[i][j]) for j in range(B)] for i in range(V)]
        fn = f"witness_inst{inst_id}_direct.json"
        json.dump(dict(params=p, matrix=mat, group="trivial-direct"), open(fn, 'w'))
        print(f"WITNESS -> {fn}", flush=True)
    return name

if __name__ == '__main__':
    inst = int(sys.argv[1]); tl = float(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else int(os.environ.get('WORKERS', '8'))
    solve(inst, tl, w)

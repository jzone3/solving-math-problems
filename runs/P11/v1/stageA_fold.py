#!/usr/bin/env python3
"""Stage A: enumerate all folded images b in Z^d of a hypothetical CW(n,k)
(d | n, B = n/d entry bound): PAF_t(b)=0 for t=1..d-1, sum b = s, sum b^2 = k.
Reduce modulo the equivalence group (rotations of Z_d x units of Z_d) and
write canonical representatives to JSON.

Usage: python3 stageA_fold.py n k d out.json [max_solutions]
"""
import json, math, sys
from ortools.sat.python import cp_model


def canon(b, d):
    best = None
    units = [u for u in range(1, d) if math.gcd(u, d) == 1]
    for u in units:
        dec = [b[(u * j) % d] for j in range(d)]
        for r in range(d):
            cand = tuple(dec[(j + r) % d] for j in range(d))
            if best is None or cand > best:
                best = cand
    return best


class Collector(cp_model.CpSolverSolutionCallback):
    def __init__(self, bvars, d, maxsol):
        super().__init__()
        self.bvars = bvars; self.d = d; self.maxsol = maxsol
        self.raw = 0
        self.classes = set()

    def on_solution_callback(self):
        b = [self.Value(v) for v in self.bvars]
        self.raw += 1
        self.classes.add(canon(b, self.d))
        if self.raw % 5000 == 0:
            print(f"  raw={self.raw} classes={len(self.classes)}", flush=True)
        if self.raw >= self.maxsol:
            self.StopSearch()


def main():
    n, k, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out = sys.argv[4]
    maxsol = int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 7
    s = math.isqrt(k)
    B = n // d
    m = cp_model.CpModel()
    b = [m.NewIntVar(-B, B, f"b{j}") for j in range(d)]
    m.Add(sum(b) == s)
    sq = []
    for j in range(d):
        v = m.NewIntVar(0, B * B, f"sq{j}")
        m.AddMultiplicationEquality(v, [b[j], b[j]])
        sq.append(v)
    m.Add(sum(sq) == k)
    prodc = {}
    def prod(i, j):
        key = (min(i, j), max(i, j))
        if key not in prodc:
            v = m.NewIntVar(-B * B, B * B, f"pr{key[0]}_{key[1]}")
            m.AddMultiplicationEquality(v, [b[key[0]], b[key[1]]])
            prodc[key] = v
        return prodc[key]
    for t in range(1, d // 2 + 1):
        m.Add(sum(prod(i, (i + t) % d) for i in range(d)) == 0)
    sol = cp_model.CpSolver()
    sol.parameters.enumerate_all_solutions = True
    sol.parameters.num_workers = 1
    coll = Collector(b, d, maxsol)
    st = sol.Solve(m, coll)
    print("status:", sol.StatusName(st), "raw:", coll.raw, "classes:", len(coll.classes))
    json.dump(sorted(coll.classes), open(out, "w"))
    print("wrote", out)


if __name__ == "__main__":
    main()

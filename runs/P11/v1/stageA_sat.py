#!/usr/bin/env python3
"""Stage A via incremental SAT (pysat Cadical195): enumerate integer vectors
b in [-B,B]^d with sum b = s, sum b^2 = k, PAF_t(b) = 0 for t=1..d-1.

Unit-literal encoding: b_j = sum of B "+units" minus B "-units", with
monotone chains u_{j,1} >= u_{j,2} >= ... and sign exclusivity.

Blocking clauses over unit literals enumerate all solutions; canonical class
reduction (rotations x units of Z_d) done in Python.

Usage: python3 stageA_sat.py n k d out.json [max_raw]
"""
import json, math, sys, time
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from cw_cnf import tot_outputs, link_offset
from stageA_fold import canon


def build(n, k, d, subfolds=()):
    s = math.isqrt(k)
    B = n // d
    pool = IDPool()
    cnf = CNF()
    U = [[pool.id(("u", j, r)) for r in range(B)] for j in range(d)]
    V = [[pool.id(("v", j, r)) for r in range(B)] for j in range(d)]
    for j in range(d):
        for r in range(1, B):
            cnf.append([-U[j][r], U[j][r - 1]])
            cnf.append([-V[j][r], V[j][r - 1]])
        cnf.append([-U[j][0], -V[j][0]])
    # sum b = s : count(+units) - count(-units) = s
    au = [l for j in range(d) for l in U[j]]
    av = [l for j in range(d) for l in V[j]]
    link_offset(cnf, pool, au, av, s, "RS")
    # sum b^2 = k : sum q_j + 2*[q>=2] + 4*[q>=3] + ... with q_j = |b_j|
    wlits = []
    for j in range(d):
        for r in range(B):
            q = pool.id(("q", j, r))  # q_j >= r+1
            cnf.append([-U[j][r], q]); cnf.append([-V[j][r], q])
            cnf.append([-q, U[j][r], V[j][r]])
            wlits.append(q)          # weight 1 for q>=1 level r contributes...
            for _ in range(2 * r):   # (r+1)^2 - r^2 = 2r+1 -> add extra 2r copies
                wlits.append(q)
    ok = tot_outputs(cnf, pool, wlits, k + 1, "SQ")
    cnf.append([ok[k - 1]])
    if len(ok) > k:
        cnf.append([-ok[k]])
    # PAF_t = 0 for t=1..d//2 : signed unit-product counts equal
    for t in range(1, d // 2 + 1):
        seen = set()
        plits, mlits = [], []
        for i in range(d):
            jj = (i + t) % d
            key = (min(i, jj), max(i, jj))
            if key in seen:
                continue
            seen.add(key)
            a_, b_ = key
            for ra in range(B):
                for rb in range(B):
                    for (la, lb, pos) in ((U[a_][ra], U[b_][rb], True),
                                          (V[a_][ra], V[b_][rb], True),
                                          (U[a_][ra], V[b_][rb], False),
                                          (V[a_][ra], U[b_][rb], False)):
                        w = pool.id(("w", t, a_, b_, la, lb))
                        cnf.append([-w, la]); cnf.append([-w, lb])
                        cnf.append([w, -la, -lb])
                        (plits if pos else mlits).append(w)
        cap = k // 2 + 1
        op = tot_outputs(cnf, pool, plits, cap + 1, f"OP{t}")
        om = tot_outputs(cnf, pool, mlits, cap + 1, f"OM{t}")
        if len(op) > cap:
            cnf.append([-op[cap]])
        if len(om) > cap:
            cnf.append([-om[cap]])
        for j in range(min(len(op), len(om), cap)):
            cnf.append([-op[j], om[j]])
            cnf.append([-om[j], op[j]])
    for (d2, c) in subfolds:
        assert d % d2 == 0 and len(c) == d2
        for j2 in range(d2):
            au2 = [l for j in range(j2, d, d2) for l in U[j]]
            av2 = [l for j in range(j2, d, d2) for l in V[j]]
            link_offset(cnf, pool, au2, av2, c[j2], f"SF{d2}_{j2}")
    units = [l for j in range(d) for l in U[j] + V[j]]
    return cnf, U, V, units


def main():
    n, k, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    out = sys.argv[4]
    max_raw = 10 ** 8
    subfolds = []
    for arg in sys.argv[5:]:
        if arg.startswith("--subfold="):
            spec = arg.split("=")[1]
            d2, vals = spec.split(":")
            subfolds.append((int(d2), [int(v) for v in vals.split(",")]))
        elif arg.isdigit():
            max_raw = int(arg)
    B = n // d
    cnf, U, V, units = build(n, k, d, subfolds)
    print(f"cnf: {cnf.nv} vars {len(cnf.clauses)} clauses", flush=True)
    solver = Cadical195(bootstrap_with=cnf.clauses)
    raw = 0
    classes = set()
    t0 = time.time()
    while solver.solve():
        mdl = set(l for l in solver.get_model() if l > 0)
        b = []
        for j in range(d):
            val = sum(1 for l in U[j] if l in mdl) - sum(1 for l in V[j] if l in mdl)
            b.append(val)
        raw += 1
        classes.add(canon(b, d))
        solver.add_clause([-l if l in mdl else l for l in units])
        if raw % 50 == 0:
            print(f"raw={raw} classes={len(classes)} t={time.time()-t0:.0f}s", flush=True)
            json.dump(sorted(classes), open(out, "w"))
        if raw >= max_raw:
            break
    json.dump(sorted(classes), open(out, "w"))
    print(f"DONE raw={raw} classes={len(classes)} t={time.time()-t0:.0f}s", flush=True)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()

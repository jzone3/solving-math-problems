#!/usr/bin/env python3
"""Joint cyclic/negacyclic (b,c) decomposition attack on CW(n=2d, k).

For even n = 2d, set b_j = a_j + a_{j+d}, c_j = a_j - a_{j+d} (j in Z_d).
Then a is a CW(n,k) first row iff:
  - b_j, c_j in [-2,2], |b_j| = 2 -> c_j = 0, |c_j| = 2 -> b_j = 0,
    |b_j| = 1 <-> |c_j| = 1  (parity/ternary coupling; a_j = (b_j+c_j)/2)
  - sum b = sqrt(k)   (WLOG +)
  - sum b^2 = sum c^2 = k
  - PAF_b(t) = 0 for t = 1..d-1   (cyclic)
  - NAF_c(t) = 0 for t = 1..d-1   (negacyclic: wrap terms flip sign)
This is a bijection: solving (b,c) fully determines a — no lift needed.

Usage: bc_sat.py n k out.cnf [--subfold=d2:v0,...]   (encode)
       bc_sat.py n k out.cnf --solve [timeout]        (encode+kissat+decode+verify)
"""
import json, math, os, subprocess, sys, time
from pysat.formula import CNF, IDPool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cw_cnf import tot_outputs, link_offset

KISSAT = os.path.expanduser("~/bin/kissat")


def build(n, k, subfolds=()):
    assert n % 2 == 0
    d = n // 2
    s = math.isqrt(k)
    assert s * s == k
    pool = IDPool()
    cnf = CNF()
    # unit chains: Xb[j][r] = (b_j >= r+1 positives), Yb = negatives; same for c
    Xb = [[pool.id(("xb", j, r)) for r in range(2)] for j in range(d)]
    Yb = [[pool.id(("yb", j, r)) for r in range(2)] for j in range(d)]
    Xc = [[pool.id(("xc", j, r)) for r in range(2)] for j in range(d)]
    Yc = [[pool.id(("yc", j, r)) for r in range(2)] for j in range(d)]
    for j in range(d):
        for X, Y in ((Xb[j], Yb[j]), (Xc[j], Yc[j])):
            cnf.append([-X[1], X[0]])
            cnf.append([-Y[1], Y[0]])
            cnf.append([-X[0], -Y[0]])
    # coupling per j: |b|>=2 -> |c|=0 ; |c|>=2 -> |b|=0 ; |b|=1 <-> |c|=1
    for j in range(d):
        mb1 = pool.id(("mb1", j)); mb2 = pool.id(("mb2", j))
        mc1 = pool.id(("mc1", j)); mc2 = pool.id(("mc2", j))
        for m1, m2, X, Y in ((mb1, mb2, Xb[j], Yb[j]), (mc1, mc2, Xc[j], Yc[j])):
            # m1 <-> X0 | Y0 ; m2 <-> X1 | Y1
            cnf.append([-m1, X[0], Y[0]]); cnf.append([-X[0], m1]); cnf.append([-Y[0], m1])
            cnf.append([-m2, X[1], Y[1]]); cnf.append([-X[1], m2]); cnf.append([-Y[1], m2])
        cnf.append([-mb2, -mc1])
        cnf.append([-mc2, -mb1])
        # (mb1 & ~mb2) <-> (mc1 & ~mc2)
        cnf.append([-mb1, mb2, mc1])
        cnf.append([-mb1, mb2, -mc2])
        cnf.append([-mc1, mc2, mb1])
        cnf.append([-mc1, mc2, -mb2])
    # sum b = s
    bu = [l for j in range(d) for l in Xb[j]]
    bv = [l for j in range(d) for l in Yb[j]]
    link_offset(cnf, pool, bu, bv, s, "RS")
    # sum b^2 = k and sum c^2 = k (weights 1 for level0, 3 extra for level1: 4=2^2)
    for name, X, Y in (("QB", Xb, Yb), ("QC", Xc, Yc)):
        wl = []
        for j in range(d):
            q0 = pool.id((name, j, 0)); q1 = pool.id((name, j, 1))
            cnf.append([-X[j][0], q0]); cnf.append([-Y[j][0], q0]); cnf.append([-q0, X[j][0], Y[j][0]])
            cnf.append([-X[j][1], q1]); cnf.append([-Y[j][1], q1]); cnf.append([-q1, X[j][1], Y[j][1]])
            wl.append(q0)
            wl += [q1] * 3
        ok = tot_outputs(cnf, pool, wl, k + 1, name)
        cnf.append([ok[k - 1]])
        if len(ok) > k:
            cnf.append([-ok[k]])
    # autocorrelations: cyclic for b, negacyclic for c
    for t in range(1, d):
        for name, X, Y, nega in (("PB", Xb, Yb, False), ("PC", Xc, Yc, True)):
            if not nega and t > d // 2:
                continue  # cyclic PAF symmetric: t and d-t identical
            seen = set()
            plits, mlits = [], []
            for i in range(d):
                jj = i + t
                flip = False
                if jj >= d:
                    jj -= d
                    flip = nega
                key = (min(i, jj), max(i, jj), flip) if not nega else (i,)
                if not nega:
                    if key in seen:
                        continue
                    seen.add(key)
                a_, b_ = (min(i, jj), max(i, jj)) if not nega else (i, jj)
                for ra in range(2):
                    for rb in range(2):
                        for (la, lb, pos) in ((X[a_][ra], X[b_][rb], True),
                                              (Y[a_][ra], Y[b_][rb], True),
                                              (X[a_][ra], Y[b_][rb], False),
                                              (Y[a_][ra], X[b_][rb], False)):
                            key = ("W", la, lb) if la <= lb else ("W", lb, la)
                            fresh = key not in pool.obj2id
                            w = pool.id(key)
                            if fresh:
                                cnf.append([-w, la]); cnf.append([-w, lb]); cnf.append([w, -la, -lb])
                            if flip:
                                pos = not pos
                            (plits if pos else mlits).append(w)
            cap = k // 2
            op = tot_outputs(cnf, pool, plits, cap + 1, f"{name}P{t}")
            om = tot_outputs(cnf, pool, mlits, cap + 1, f"{name}M{t}")
            if len(op) > cap:
                cnf.append([-op[cap]])
            if len(om) > cap:
                cnf.append([-om[cap]])
            for r in range(min(len(op), len(om), cap)):
                cnf.append([-op[r], om[r]])
                cnf.append([-om[r], op[r]])
    # propriety mod 2 (only relevant improper divisor pattern): support must not
    # avoid all odd positions nor all even positions of Z_n. position j+d has the
    # same parity as j iff d even (true for n=96,112). nonzero at j or j+d <-> mb1|mc1
    if (n // 2) % 2 == 0:
        for par in (0, 1):
            cnf.append([pool.id(("mb1", j)) for j in range(d) if j % 2 == par] +
                       [pool.id(("mc1", j)) for j in range(d) if j % 2 == par])
    # optional subfold streamliner on b (cyclic fold of a mod d2 where d2 | d)
    for (d2, vals) in subfolds:
        assert d % d2 == 0
        for j2 in range(d2):
            au = [l for j in range(j2, d, d2) for l in Xb[j]]
            av = [l for j in range(j2, d, d2) for l in Yb[j]]
            link_offset(cnf, pool, au, av, vals[j2], f"SF{j2}")
    return cnf, pool, Xb, Yb, Xc, Yc


def decode(model_pos, d, Xb, Yb, Xc, Yc):
    b, c = [], []
    for j in range(d):
        b.append(sum(1 for l in Xb[j] if l in model_pos) - sum(1 for l in Yb[j] if l in model_pos))
        c.append(sum(1 for l in Xc[j] if l in model_pos) - sum(1 for l in Yc[j] if l in model_pos))
    a = [0] * (2 * d)
    for j in range(d):
        a[j] = (b[j] + c[j]) // 2
        a[j + d] = (b[j] - c[j]) // 2
    return a


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    out = sys.argv[3]
    solve = "--solve" in sys.argv
    tl = 3600
    subfolds = []
    for arg in sys.argv[4:]:
        if arg.startswith("--subfold="):
            d2, vals = arg.split("=")[1].split(":")
            subfolds.append((int(d2), [int(v) for v in vals.split(",")]))
        elif arg.isdigit():
            tl = int(arg)
    d = n // 2
    cnf, pool, Xb, Yb, Xc, Yc = build(n, k, subfolds)
    cnf.to_file(out)
    print(f"wrote {out}: {cnf.nv} vars {len(cnf.clauses)} clauses", flush=True)
    if not solve:
        return
    t0 = time.time()
    r = subprocess.run(["timeout", str(tl), KISSAT, "-q", out], capture_output=True, text=True)
    el = int(time.time() - t0)
    if r.returncode == 20:
        print(f"UNSAT ({el}s)", flush=True)
        return
    if r.returncode != 10:
        print(f"TIMEOUT ({el}s)", flush=True)
        return
    mdl = set()
    for line in r.stdout.splitlines():
        if line.startswith("v"):
            mdl.update(int(t) for t in line.split()[1:] if int(t) > 0)
    a = decode(mdl, d, Xb, Yb, Xc, Yc)
    print(f"SAT ({el}s)")
    print("ROW", json.dumps(a), flush=True)
    # self-check
    assert sum(v * v for v in a) == k
    for t in range(1, n):
        assert sum(a[i] * a[(i + t) % n] for i in range(n)) == 0, t
    wp = os.path.join(HERE, f"witness_bc_{n}_{k}.json")
    json.dump({"n": n, "k": k, "row": a}, open(wp, "w"))
    print(f"WITNESS WRITTEN {wp} (self-check passed)", flush=True)


if __name__ == "__main__":
    main()

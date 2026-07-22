#!/usr/bin/env python3
"""P15 V3: SAT search for covering systems with distinct moduli and min modulus >= m.

Encoding: fix smooth lcm N. Vars x[n][a] for divisors n>=m of N.
 - at-most-one residue per modulus (distinct moduli)
 - every t in Z_N covered by some chosen class
Symmetry break: smallest usable divisor, if used, has residue 0.
"""
import argparse, json, sys, time
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose4


def divisors(N):
    ds = []
    i = 1
    while i * i <= N:
        if N % i == 0:
            ds.append(i)
            if i != N // i:
                ds.append(N // i)
        i += 1
    return sorted(ds)


def build(N, m, pool):
    cnf = CNF()
    mods = [d for d in divisors(N) if d >= m and d > 1]
    x = {}
    for n in mods:
        x[n] = [pool.id(("x", n, a)) for a in range(n)]
        # at-most-one via pairwise for small n, ladder otherwise
        if n <= 8:
            for i in range(n):
                for j in range(i + 1, n):
                    cnf.append([-x[n][i], -x[n][j]])
        else:
            amo = CardEnc.atmost(lits=x[n], bound=1, vpool=pool, encoding=EncType.ladder)
            cnf.extend(amo.clauses)
    # coverage
    for t in range(N):
        cnf.append([x[n][t % n] for n in mods])
    # symmetry: translation — smallest modulus, if used, residue 0
    d1 = mods[0]
    for a in range(1, d1):
        cnf.append([-x[d1][a]])
    return cnf, mods, x


def solve(N, m, timeout=None, verbose=True):
    recip = sum(1.0 / d for d in divisors(N) if d >= m and d > 1)
    if verbose:
        print(f"N={N} m={m} reciprocal-sum={recip:.4f}", flush=True)
    if recip < 1.0:
        return "INFEASIBLE(recip<1)", None
    pool = IDPool()
    t0 = time.time()
    cnf, mods, x = build(N, m, pool)
    if verbose:
        print(f"  mods={len(mods)} vars={pool.top} clauses={len(cnf.clauses)} "
              f"build={time.time()-t0:.1f}s", flush=True)
    with Glucose4(bootstrap_with=cnf.clauses) as s:
        t0 = time.time()
        if timeout:
            # wall-clock timers don't work (C solve holds the GIL): use
            # conflict-budget chunks and check the clock between calls
            res = None
            while res is None and time.time() - t0 < timeout:
                s.conf_budget(100000)
                res = s.solve_limited()
        else:
            res = s.solve()
        dt = time.time() - t0
        if res is None:
            return f"TIMEOUT({dt:.0f}s)", None
        if not res:
            return f"UNSAT({dt:.0f}s)", None
        model = set(l for l in s.get_model() if l > 0)
        sol = []
        for n in mods:
            for a in range(n):
                if x[n][a] in model:
                    sol.append((a, n))
        return f"SAT({dt:.0f}s)", sol


def check(sol, N):
    cov = bytearray(N)
    mods = set()
    for a, n in sol:
        assert n not in mods, f"duplicate modulus {n}"
        mods.add(n)
        for t in range(a % n, N, n):
            cov[t] = 1
    return all(cov)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("m", type=int)
    ap.add_argument("--timeout", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    status, sol = solve(args.N, args.m, timeout=args.timeout)
    print("STATUS", status, flush=True)
    if sol:
        assert check(sol, args.N), "verification failed!"
        print(f"cover verified: {len(sol)} congruences, min modulus {min(n for _,n in sol)}")
        if args.out:
            with open(args.out, "w") as f:
                json.dump({"N": args.N, "m": args.m, "cover": sol}, f)
            print("written", args.out)

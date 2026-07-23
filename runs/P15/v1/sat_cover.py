#!/usr/bin/env python3
"""
SAT encoding of the finite-LCM distinct-moduli covering problem (P15 V1).

Cover Z_N with residue classes a (mod n), n | N, n >= M, each modulus used
at most once. Variables x_{n,a} = "class a mod n selected".
Clauses: (1) for each cell x: OR_{n} x_{n, x mod n}   (coverage)
         (2) for each n: at-most-one over {x_{n,a}}   (distinct moduli)

Usage: sat_cover.py M N [solver]
Writes /tmp/sat_M{M}_N{N}.json on success.
"""
import json
import sys
import time

from pysat.solvers import Cadical195
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


def solve(M, N, verbose=True):
    mods = [d for d in divisors(N) if d >= M and d > 1]
    r = sum(1.0 / d for d in mods)
    pool = IDPool()
    var = {}
    for n in mods:
        for a in range(n):
            var[(n, a)] = pool.id(("x", n, a))
    cls = []
    for x in range(N):
        cls.append([var[(n, x % n)] for n in mods])
    for n in mods:
        lits = [var[(n, a)] for a in range(n)]
        amo = CardEnc.atmost(lits, bound=1, vpool=pool,
                             encoding=EncType.seqcounter)
        cls.extend(amo.clauses)
    if verbose:
        print("M=%d N=%d mods=%d recip=%.3f vars=%d clauses=%d"
              % (M, N, len(mods), r, pool.top, len(cls)), flush=True)
    t0 = time.time()
    with Cadical195(bootstrap_with=cls) as s:
        sat = s.solve()
        t = time.time() - t0
        if not sat:
            print("UNSAT (%.1fs) — N=%d admits NO M=%d cover" % (t, N, M))
            return None
        model = set(l for l in s.get_model() if l > 0)
    congs = [(a, n) for (n, a), v in var.items() if v in model]
    congs.sort(key=lambda x: x[1])
    print("SAT (%.1fs): %d congruences" % (t, len(congs)))
    return congs


def main():
    M, N = int(sys.argv[1]), int(sys.argv[2])
    congs = solve(M, N)
    if congs:
        fn = "/tmp/sat_M%d_N%d.json" % (M, N)
        json.dump({"minmod": M,
                   "congruences": [[int(a), int(n)] for a, n in congs]},
                  open(fn, "w"))
        print("wrote", fn)


if __name__ == "__main__":
    main()

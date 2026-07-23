#!/usr/bin/env python3
"""
Cap-bounded Erdős #273 decision via projection + complete DFS.

For cap B, pool = {n : 4 <= n <= B, n+1 prime}. Projection lemma: if a
prime p has at most p-1 multiples in the pool, choose a residue c_p mod
p avoiding the mod-p class of every such multiple; the progression
{x ≡ c (mod prod p)} (CRT) is untouched by those moduli and is ≅ Z,
with every remaining modulus (coprime to all chosen p) inducing the
same modulus on it. Iterate to a fixpoint. Hence a cap-B covering
exists ONLY IF the residual (smooth) pool covers Z. If residual mass
< 1: impossible. Else decide by complete element-branching DFS over
Z/lcm(residual) with exact Fraction mass prune.

If the DFS finds a cover of the residual pool, that IS a genuine #273
witness (all moduli admissible, distinct): it is written to
witness_cap_B{B}.json — verify with solutions/P18/verify.py.

Usage: cap_project.py B [time_limit_s]
"""
import json
import sys
import time
from fractions import Fraction
from math import lcm

import numpy as np

from twophase import is_prime


def prime_factors(n):
    ps = set()
    x, f = n, 2
    while f * f <= x:
        if x % f == 0:
            ps.add(f)
            while x % f == 0:
                x //= f
        f += 1
    if x > 1:
        ps.add(x)
    return ps


def project(pool):
    cur = list(pool)
    S = []
    changed = True
    while changed:
        changed = False
        primes = set()
        for n in cur:
            primes |= prime_factors(n)
        for p in sorted(primes, reverse=True):
            mult = [n for n in cur if n % p == 0]
            if mult and len(mult) <= p - 1:
                S.append(p)
                cur = [n for n in cur if n % p != 0]
                changed = True
    return sorted(S), cur


def decide(residual, B, tl, l1=None):
    L = lcm(*residual)
    mass = sum(Fraction(1, n) for n in residual)
    print("B=%d residual=%d moduli L=%d mass=%s (%.6f)"
          % (B, len(residual), L, mass, float(mass)), flush=True)
    if mass < 1:
        print("B=%d KILLED (residual mass < 1). Definitive." % B, flush=True)
        return "killed"
    unc = np.ones(L, dtype=bool)
    cnt = [L]
    unused = sorted(residual)
    chosen = []
    t0 = time.time()
    nodes = [0]
    last = [t0]
    recip = {n: Fraction(1, n) for n in residual}
    slack = sum(recip.values()) - 1
    slackL = int(slack * L) + 1  # congruence overlapping > slack*L is dead

    def rec(budget):
        nodes[0] += 1
        if cnt[0] == 0:
            return True
        now = time.time()
        if now - t0 > tl:
            raise TimeoutError
        if now - last[0] > 60:
            last[0] = now
            print("... nodes=%d depth=%d unc=%d %.1fs"
                  % (nodes[0], len(chosen), cnt[0], now - t0), flush=True)
        if budget < Fraction(cnt[0], L):
            return False
        # lookahead: each large unused modulus still needs a residue class
        # that is almost entirely fresh (within the remaining waste budget)
        remL = int((budget - Fraction(cnt[0], L)) * L) + 1
        deficit = 0
        cnts = {}
        for n in unused[::-1]:
            counts = unc.reshape(L // n, n).sum(axis=0, dtype=np.int64)
            cnts[n] = counts
            deficit += max(0, L // n - int(counts.max()))
            if deficit > remL:
                return False
        r = int(np.argmax(unc))
        cands = []
        for n in list(unused):
            a = r % n
            g = int(cnts[n][a])
            if g >= L // n - remL:  # otherwise immediate waste overflow
                cands.append((-g, n, a))
        cands.sort()
        if l1 is not None and len(chosen) == 1:
            cands = [c for c in cands if c[1] == l1]
        for _, n, a in cands:
            view = unc[a::n]
            mask = view.copy()
            view[:] = False
            k = int(mask.sum())
            cnt[0] -= k
            chosen.append((a, n))
            unused.remove(n)
            if rec(budget - recip[n]):
                return True
            unused.append(n)
            unused.sort()
            chosen.pop()
            unc[a::n][mask] = True
            cnt[0] += k
        return False

    # WLOG normalization: every cover must use ALL moduli (slack < 1/max n),
    # in particular the smallest modulus n0; translating x -> x - a0 puts its
    # congruence at residue 0. So fix (0 mod n0) at the root.
    budget0 = sum(recip.values())
    if Fraction(1, min(residual)) > slack:  # smallest modulus is forced
        n0 = unused[0]
        unc[0::n0] = False
        cnt[0] -= L // n0
        chosen.append((0, n0))
        unused.remove(n0)
        budget0 -= recip[n0]
        print("normalized: fixed (0 mod %d) at root" % n0, flush=True)
    try:
        ok = rec(budget0)
    except TimeoutError:
        print("B=%d TIMEOUT (undecided) nodes=%d %.1fs"
              % (B, nodes[0], time.time() - t0), flush=True)
        return "timeout"
    if ok:
        fn = "witness_cap_B%d.json" % B
        json.dump({"congruences": [[a, n] for a, n in chosen]}, open(fn, "w"))
        print("B=%d SUCCESS!!! %d congruences -> %s"
              % (B, len(chosen), fn), flush=True)
        return "witness"
    print("B=%d KILLED by complete DFS (residual pool cannot cover). "
          "Definitive. nodes=%d %.1fs" % (B, nodes[0], time.time() - t0),
          flush=True)
    return "killed"


def main():
    B = int(sys.argv[1])
    tl = float(sys.argv[2]) if len(sys.argv) > 2 else 86400.0
    l1 = int(sys.argv[3]) if len(sys.argv) > 3 else None
    pool = [n for n in range(4, B + 1) if is_prime(n + 1)]
    mass = sum(Fraction(1, n) for n in pool)
    S, residual = project(pool)
    print("B=%d pool=%d mass=%.6f projected primes S=%s"
          % (B, len(pool), float(mass), S), flush=True)
    print("residual pool: %s" % residual, flush=True)
    if l1 is not None:
        print("level-1 branch restricted to modulus %d" % l1, flush=True)
    decide(residual, B, tl, l1)


if __name__ == "__main__":
    main()

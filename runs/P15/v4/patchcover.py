#!/usr/bin/env python3
"""
P15 V4 phase 6: DIRECT SEARCH for a T=43 patch of Owens's system.

Fact (thesis + our ledger replay): Owens's T=42 covering system has a
UNIQUE congruence with modulus 42; removing it leaves uncovered a SUBSET
of one class mod 42. Hence:

    If we cover one full class mod 42 by congruences whose (distinct)
    moduli are >= 43 and NOT used by Owens, then Owens-minus-42 plus the
    patch is a covering system with distinct moduli, minimum modulus 43.

Inner coordinates: x = a* + 42k, k in Z. Inner congruence k = r (mod n)
is realized by actual modulus M = n*g for any g | 42 with gcd(M,42) = g
and M >= 43 (then x = a* + 42r (mod M) covers a superset of the inner
class - safe). Each distinct M is usable once.

Free-modulus budget (machine-derived, owens_smooth.py):
  * 7-smooth M: free iff M not in the faithful enumeration of sections
    3.1-3.4 (conservative for 2/3/5-smooth: ALL marked used).
  * M with a prime factor >= 97: always free (Owens is 89-smooth).
  * M with largest prime in [11, 89]: clearance unknown (would need the
    Nielsen-import reconstruction) -> NOT used.

Search: exact hole-class counting over a CRT window (cover4-style), with
per-inner-n multiplicity budgets = number of free realizations. Emits a
witness JSON with actual (a, M) congruences; verified by
solutions/P15/verify_patch.py (explicit finite check over lcm when
feasible, else structured replay).
"""
import json
import sys
import time
from math import gcd

import numpy as np

from owens_smooth import used_smooth

UCAP = 10**9
U = used_smooth(UCAP)
GS = (1, 2, 3, 6, 7, 14, 21, 42)
SAFE_PRIMES = [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
               157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def is_7smooth(n):
    for p in (2, 3, 5, 7):
        while n % p == 0:
            n //= p
    return n == 1


def free_realizations(n):
    """List of free actual moduli M = n*g for inner modulus n."""
    out = []
    big = max_prime_factor(n)
    for g in GS:
        M = n * g
        if gcd(M, 42) != g or M < 43:
            continue
        if big >= 97:
            out.append(M)                    # Owens is 89-smooth
        elif big <= 7:
            if M <= UCAP and M not in U:
                out.append(M)                # machine-checked free
        # 11 <= big <= 89: unknown clearance -> skip
    return out


def max_prime_factor(n):
    b = 1
    d = 2
    while d * d <= n:
        while n % d == 0:
            b = d
            n //= d
        d += 1
    return max(b, n) if n > 1 else b


class PatchBuilder:
    def __init__(self, hcap=3_000_000, verbose=True, seed=0):
        self.hcap = hcap
        self.verbose = verbose
        self.rng = np.random.default_rng(seed)
        self.win = {}
        self.wprimes = []
        self.comps = None
        self.counts = [1]
        self.budget = {}        # inner n -> list of unused free M
        self.emitted = []       # (r, n, M): inner congruence + realization
        self.ok = True

    def log(self, *a):
        if self.verbose:
            print(*a, flush=True)

    def key_for(self, comps, nfact):
        key = np.zeros(comps.shape[0], dtype=np.int64)
        for p, k in nfact.items():
            i = self.wprimes.index(p)
            key = key * p**k + comps[:, i] % p**k
        return key

    def process(self, p):
        t0 = time.time()
        H = len(self.counts)
        e_old = self.win.get(p, 0)
        if p not in self.win:
            self.win[p] = 0
            self.wprimes.append(p)
            pad = np.zeros((H, 1), dtype=np.int64)
            self.comps = (pad if self.comps is None
                          else np.hstack([self.comps, pad]))
        pi = self.wprimes.index(p)
        cells = np.repeat(self.comps, p, axis=0)
        s = np.tile(np.arange(p, dtype=np.int64), H)
        cells[:, pi] += p**e_old * s
        ccounts = [n for n in self.counts for _ in range(p)]
        self.win[p] = e_old + 1

        # candidate inner moduli: divisors n of window product with free
        # realizations remaining
        divs = [1]
        for q, e in self.win.items():
            divs = [d * q**k for d in divs for k in range(e + 1)
                    if d * q**k <= 10**9]
        cands = []
        for n in sorted(set(divs)):
            if n == 1:
                continue
            if n not in self.budget:
                self.budget[n] = free_realizations(n)
            if self.budget[n]:
                cands.append(n)

        def nfact_of(n):
            f = {}
            for q in self.wprimes:
                k = 0
                while n % q == 0:
                    n //= q
                    k += 1
                if k:
                    f[q] = k
            return f

        facts = {n: nfact_of(n) for n in cands}
        maxbits = max(x.bit_length() for x in ccounts)
        shift = max(0, maxbits - 500)
        w = np.array([float(x >> shift) if (x >> shift) else 5e-324
                      for x in ccounts])
        act = np.ones(len(ccounts), dtype=bool)
        kcache = {}

        def keys(n):
            if n not in kcache:
                if len(kcache) > 64:
                    kcache.pop(next(iter(kcache)))
                kcache[n] = self.key_for(cells, facts[n])
            return kcache[n]

        def best(n):
            km = keys(n)
            vals, inv = np.unique(km, return_inverse=True)
            g = np.bincount(inv, weights=act * w, minlength=len(vals))
            k = int(g.argmax())
            return float(g[k]), int(vals[k])

        from heapq import heappush, heappop
        heap = []
        for n in cands:
            gv, a = best(n)
            if gv > 0:
                heappush(heap, (-gv / n, self.rng.random(), n))
        while heap:
            _, _, n = heappop(heap)
            if not self.budget[n]:
                continue
            gv, a = best(n)
            if gv <= 0:
                continue
            if heap and -heap[0][0] > (gv / n) * 1.0000001:
                heappush(heap, (-gv / n, self.rng.random(), n))
                continue
            act &= keys(n) != a
            M = self.budget[n].pop(0)
            self.emitted.append((a, n, M))

        idx = np.nonzero(act)[0]
        cells = cells[idx]
        ccounts = [ccounts[i] for i in idx.tolist()]
        if len(cells):
            order = np.lexsort(cells.T)
            cells = cells[order]
            ccounts = [ccounts[i] for i in order.tolist()]
            uniq = np.ones(len(cells), dtype=bool)
            uniq[1:] = np.any(cells[1:] != cells[:-1], axis=1)
            nc, nn = [], []
            for i, u in enumerate(uniq.tolist()):
                if u:
                    nc.append(cells[i])
                    nn.append(ccounts[i])
                else:
                    nn[-1] += ccounts[i]
            cells = np.array(nc, dtype=np.int64)
            ccounts = nn
        self.comps = (cells if len(ccounts)
                      else np.zeros((0, len(self.wprimes)), dtype=np.int64))
        self.counts = ccounts
        tot = sum(ccounts) if ccounts else 0
        self.log(f"level {p}: emitted so far {len(self.emitted)}, "
                 f"classes={len(ccounts)}, holes={tot}, "
                 f"t={time.time()-t0:.1f}s")
        return tot


def run(levels, out=None, seed=0):
    b = PatchBuilder(seed=seed)
    tot = 1
    for p in levels:
        tot = b.process(p)
        if tot == 0:
            b.log("HOLE FULLY COVERED - patch complete!")
            break
    Ms = [M for _, _, M in b.emitted]
    ok = tot == 0 and len(set(Ms)) == len(Ms) and min(Ms, default=99) >= 43
    print(f"FINAL: holes={tot}, congs={len(b.emitted)}, "
          f"distinct={len(set(Ms)) == len(Ms)}, "
          f"minM={min(Ms, default=None)}, SUCCESS={ok}")
    if out:
        with open(out, "w") as f:
            json.dump({"a_star": 2,
                       "patch": [[int(a), int(n), int(M)]
                                 for a, n, M in b.emitted],
                       "levels": levels, "success": ok}, f)
    return ok, tot, b


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    levels = ([7] * 4 + [2] * 3 + [5] * 2 + [3] * 2 + [7] * 2
              + SAFE_PRIMES[:8])
    run(levels, out="patch43_witness.json", seed=seed)

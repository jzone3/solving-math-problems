#!/usr/bin/env python3
"""
Count-minimizing CRT/tree greedy cover builder.

Fixes fc_tree's sampling blindness: uncovered fragments are grouped by
their modulus m (m | N), each group stored as a numpy residue array.
For a candidate modulus n the exact covered-mass profile over residues
a mod n is

    G_n[a] = sum over fragment groups m of
             (1/lcm(m,n)) * cnt_{m,gcd(m,n)}[a mod gcd(m,n)]

where cnt_{m,g} = bincount of the group's residues mod g. This is a CRT
convolution keyed on DISTINCT fragment moduli (dozens), not fragments
(millions), so it is exact and fast. This variant minimizes the exact
number of surviving fragment classes first, breaking ties by covered
measure. For a candidate n and residual group m, g = gcd(m,n) and
q = lcm(m,n)/m = n/g; each hit fragment changes the count by q-2.

Usage: fc_tree2_countmin.py M [fact] [time_limit]
Writes /tmp/fct2_countmin_M{M}.json on success.
"""
import json
import sys
import time
from math import gcd

import numpy as np

DEFAULT_FACT = "2^7,3^5,5^3,7^2,11,13,17,19"
ARRAY_CAP = 200000


def parse_fact(s):
    pps = []
    for part in s.split(","):
        if "^" in part:
            p, e = part.split("^")
            pps.append((int(p), int(e)))
        else:
            pps.append((int(part), 1))
    return pps


def divisors_of(pps, lo):
    ds = [1]
    for p, e in pps:
        ds = [d * p**k for d in ds for k in range(e + 1)]
    return sorted(d for d in ds if d >= lo)


def lcm(a, b):
    return a // gcd(a, b) * b


class Builder:
    def __init__(self, M, pps, rng=None):
        self.M = M
        self.pps = pps
        self.N = 1
        for p, e in pps:
            self.N *= p**e
        self.mods = divisors_of(pps, M)
        self.unused = set(self.mods)
        self.frags = {1: np.zeros(1, dtype=np.int64)}   # m -> residues
        self.chosen = []
        self.rng = rng
        self.cnt_cache = {}      # (m, g) -> bincount of frags[m] % g
        self.cache_size = 0

    CACHE_BUDGET = 2 * 10**8   # total cached elements (~1.6 GB)

    def cnt(self, m, g):
        key = (m, g)
        c = self.cnt_cache.get(key)
        if c is None:
            c = np.bincount(self.frags[m] % g, minlength=g)
            if self.cache_size + g > self.CACHE_BUDGET:
                self.cnt_cache.clear()
                self.cache_size = 0
            self.cnt_cache[key] = c
            self.cache_size += g
        return c

    def mass(self):
        return sum(len(r) / m for m, r in self.frags.items())

    def nfrags(self):
        return sum(len(r) for r in self.frags.values())

    def gain_profile(self, n):
        """Exact G_n over residues a mod n (n <= ARRAY_CAP)."""
        G = np.zeros(n)
        for m, R in self.frags.items():
            if len(R) == 0:
                continue
            g = gcd(m, n)
            w = 1.0 / lcm(m, n)
            G += w * np.tile(self.cnt(m, g), n // g)
        return G

    def count_profile(self, n):
        """Exact integer fragment-count delta for each residue class."""
        D = np.zeros(n, dtype=np.int64)
        for m, R in self.frags.items():
            if len(R) == 0:
                continue
            g = gcd(m, n)
            q = n // g
            D += (q - 2) * np.tile(self.cnt(m, g), n // g)
        return D

    def count_gain(self, n, a):
        """Exact (count delta, measure gain) for one residue class."""
        delta = 0
        gain = 0.0
        for m, R in self.frags.items():
            if len(R) == 0:
                continue
            g = gcd(m, n)
            hits = int(self.cnt(m, g)[a % g])
            if hits:
                delta += hits * (n // g - 2)
                gain += hits / (m // g * n)
        return delta, gain

    def best_class(self, n):
        """(count delta, residue, measure gain), exact count-first."""
        if n <= ARRAY_CAP:
            D = self.count_profile(n)
            G = self.gain_profile(n)
            positive = np.flatnonzero(G > 0)
            if len(positive) == 0:
                return None, None, 0.0
            dmin = int(D[positive].min())
            tied = positive[D[positive] == dmin]
            a = int(tied[G[tied].argmax()])
            return dmin, a, float(G[a])
        # pinned candidates from residues of the biggest groups
        cands = set()
        for m in sorted(self.frags, key=lambda m: m):
            R = self.frags[m]
            if len(R) == 0:
                continue
            take = min(len(R), 40)
            for r in R[:take]:
                cands.add(int(r) % gcd(m, n))
            if len(cands) > 120:
                break
        best = None
        for a in cands:
            delta, gain = self.count_gain(n, a)
            if gain <= 0:
                continue
            key = (delta, -gain)
            if best is None or key < best[0]:
                best = (key, delta, a, gain)
        if best is None:
            return None, None, 0.0
        return best[1], best[2], best[3]

    def apply(self, a, n):
        newfrags = {}
        changed = set()
        for m, R in self.frags.items():
            g = gcd(m, n)
            L = lcm(m, n)
            hit = (R - a) % g == 0
            keep = R[~hit]
            if len(keep):
                prev = newfrags.get(m)
                newfrags[m] = keep if prev is None else \
                    np.concatenate([prev, keep])
            sel = R[hit]
            if len(sel) == 0:
                continue
            changed.add(m)
            changed.add(L)
            q = L // m
            # children rr = r + t*m, t in 0..q-1; exclude rr ≡ a (mod n)
            children = (sel[:, None] + np.arange(q)[None, :] * m).ravel()
            surv = children[(children - a) % n != 0]
            if len(surv):
                prev = newfrags.get(L)
                newfrags[L] = surv if prev is None else \
                    np.concatenate([prev, surv])
        self.frags = newfrags
        self.cnt_cache = {k: v for k, v in self.cnt_cache.items()
                          if k[0] not in changed}
        self.cache_size = sum(k[1] for k in self.cnt_cache)
        self.chosen.append((a, n))
        self.unused.discard(n)

    def run(self, time_limit=3600, report=15.0):
        t0 = time.time()
        last = t0
        while self.frags and any(len(v) for v in self.frags.values()):
            if time.time() - t0 > time_limit:
                print("TIMEOUT mass=%.4g frags=%d chosen=%d"
                      % (self.mass(), self.nfrags(), len(self.chosen)),
                      flush=True)
                return False
            best = None
            for n in self.unused:
                delta, a, gain = self.best_class(n)
                if a is None or gain <= 0:
                    continue
                key = (delta, -gain)
                if best is None or key < best[0]:
                    best = (key, n, a)
            if best is None:
                print("EXHAUSTED mods: mass=%.4g frags=%d"
                      % (self.mass(), self.nfrags()), flush=True)
                return False
            _, n, a = best
            self.apply(a, n)
            if time.time() - last > report:
                print("  chosen=%d mass=%.5g frags=%d unused=%d t=%.0fs"
                      % (len(self.chosen), self.mass(), self.nfrags(),
                         len(self.unused), time.time() - t0), flush=True)
                last = time.time()
        return True


def main():
    M = int(sys.argv[1])
    fact = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FACT
    tl = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    pps = parse_fact(fact)
    b = Builder(M, pps)
    print("M=%d N=%d mods=%d recip=%.3f"
          % (M, b.N, len(b.mods), sum(1.0 / n for n in b.mods)), flush=True)
    ok = b.run(tl)
    if ok:
        congs = sorted(b.chosen, key=lambda t: t[1])
        fn = "/tmp/fct2_countmin_M%d.json" % M
        json.dump({"minmod": M,
                   "congruences": [[int(a), int(n)] for a, n in congs]},
                  open(fn, "w"))
        print("SUCCESS M=%d congs=%d -> %s" % (M, len(congs), fn))
    elif b.nfrags() <= 100000:
        fn = "/tmp/fct2_countmin_state_M%d.json" % M
        json.dump({
            "minmod": M,
            "factorization": fact,
            "N": b.N,
            "congruences": [[int(a), int(n)] for a, n in b.chosen],
            "frags": {str(int(m)): [int(x) for x in R]
                      for m, R in b.frags.items()},
        }, open(fn, "w"))
        print("STATE M=%d frags=%d -> %s" % (M, b.nfrags(), fn))


if __name__ == "__main__":
    main()

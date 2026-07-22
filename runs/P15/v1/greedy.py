#!/usr/bin/env python3
"""
Global priority-queue greedy constructor for covering systems with
min modulus >= M (P15 variant V1: machine optimization of the
prime-by-prime hole-filling method).

Key primitives
--------------
1. SPLIT/EMIT (zero waste): for a hole H = (r mod m), pick t >= 1 with
   n = m*t unused and n >= M.  Emit the class (r mod n)  (covers exactly
   1/t of H, entirely inside H) and enqueue the remaining t-1 subclasses
   (r + m*i mod n).  If t == 1 the hole is closed outright.

2. FINITIZE (small waste): pick a prime q not dividing m, and q distinct
   divisors d_0..d_{q-1} of m with q*d_i unused and >= M.  Emit classes
   (i mod q) CRT (r mod d_i).  Every x in H satisfies x = r (mod d_i) for
   all i, and lies in some class i mod q, so H is fully covered.  This is
   the Nielsen finitization p(2^n, 2^{n-1}, ...) generalized to divisor
   chains, with no ancestor bookkeeping needed.
   Waste = (1/q) * sum_i 1/d_i - 1/m  (measure spent outside the hole).

Strategy: process holes largest-first (smallest m).  Big holes take the
cheapest multiples; dust is closed by finitization when its relative waste
is acceptable.  All arithmetic exact (integers / Fraction).
"""
import heapq
import json
import random
import sys
import time
from fractions import Fraction
from math import gcd

def primes_up_to(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = bytearray(len(sieve[i * i:: i]))
    return [i for i in range(2, n + 1) if sieve[i]]

PRIMES = primes_up_to(10000)
PRIMESET = set(PRIMES)


def crt(r1, m1, r2, m2):
    # gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + (r2 - r1) * inv % m2 * m1) % (m1 * m2)


class Failure(Exception):
    pass


class Greedy:
    def __init__(self, M, tmax=64, abs_waste_cap=Fraction(1, 10**7),
                 fin_min_m=None, seed=None, t_choices=1, max_congs=5_000_000):
        self.M = M
        self.tmax = tmax
        # Finitization is allowed only when its ABSOLUTE wasted measure is
        # below this cap (Nielsen's finitizations happen at great depth, so
        # their absolute waste is negligible even though relative waste is
        # huge).  Total waste ~ (#finitizations) * cap.
        self.abs_waste_cap = Fraction(abs_waste_cap)
        self.fin_min_m = fin_min_m or max(4 * M * M,
                                          int(1 / self.abs_waste_cap) // 4)
        self.rng = random.Random(seed) if seed is not None else None
        self.t_choices = t_choices             # randomize among best k splits
        self.max_congs = max_congs
        self.used = set()
        self.congs = []
        self.waste = Fraction(0)
        self.stats = {"emit": 0, "close": 0, "finitize": 0, "fin_classes": 0}

    def emit(self, a, n):
        assert n >= self.M and n not in self.used, (a, n)
        self.used.add(n)
        self.congs.append((a % n, n))
        if len(self.congs) > self.max_congs:
            raise Failure("too many congruences")

    # ------------------------------------------------------------------
    _div_cache = {}

    @classmethod
    def divisors_desc(cls, m):
        """All divisors of m, descending (m is smooth by construction)."""
        ds = cls._div_cache.get(m)
        if ds is not None:
            return ds
        n = m
        fac = []
        for p in PRIMES:
            if p * p > n:
                break
            if n % p == 0:
                e = 0
                while n % p == 0:
                    n //= p
                    e += 1
                fac.append((p, e))
        if n > 1:
            fac.append((n, 1))
        divs = [1]
        for p, e in fac:
            divs = [d * p ** k for d in divs for k in range(e + 1)]
        divs.sort(reverse=True)
        if len(cls._div_cache) < 200000:
            cls._div_cache[m] = divs
        return divs

    def small_divisors(self, m, bound=512):
        """Ascending divisors s of m with s <= bound."""
        return [s for s in range(1, bound + 1) if m % s == 0]

    def divisor_chain(self, m, q, small):
        """Largest q divisors d = m/s of m (s ascending) with q*d unused."""
        out = []
        for s in small:
            d = m // s
            v = q * d
            if v >= self.M and v not in self.used:
                out.append(d)
                if len(out) == q:
                    break
        return out

    def try_finitize(self, r, m):
        if m < self.fin_min_m:
            return False
        small = self.small_divisors(m)
        for q in PRIMES[:25]:
            if m % q == 0:
                continue
            ds = self.divisor_chain(m, q, small)
            if len(ds) < q:
                continue
            waste = Fraction(1, q) * sum(Fraction(1, d) for d in ds) - Fraction(1, m)
            if waste > self.abs_waste_cap:
                continue
            for i, d in enumerate(ds):
                self.emit(crt(r % d, d, i, q), q * d)
            self.waste += waste
            self.stats["finitize"] += 1
            self.stats["fin_classes"] += q
            return True
        return False

    # ------------------------------------------------------------------
    def split_candidates(self, m):
        """t values (ascending n=m*t) that are usable."""
        lo = max(2, -(-self.M // m))   # smallest t with m*t >= M
        if m >= self.M:
            lo = 1
        cands = []
        t = lo
        while len(cands) < self.t_choices and t <= max(self.tmax, lo + self.tmax):
            n = m * t
            if n >= self.M and n not in self.used:
                cands.append(t)
            t += 1
        return cands

    def step(self, r, m, heap):
        # 1. whole-hole close
        if m >= self.M and m not in self.used:
            self.emit(r, m)
            self.stats["close"] += 1
            return
        # 2. finitize dust
        if self.try_finitize(r, m):
            return
        # 3. split
        cands = self.split_candidates(m)
        if not cands:
            raise Failure("stuck: no usable multiple for hole mod %d" % m)
        if self.rng and len(cands) > 1:
            t = self.rng.choice(cands)
        else:
            t = cands[0]
        n = m * t
        self.emit(r, n)
        self.stats["emit"] += 1
        for i in range(1, t):
            heapq.heappush(heap, (n, r + m * i))

    def run(self, verbose=False):
        t0 = time.time()
        heap = [(1, 0)]
        steps = 0
        while heap:
            m, r = heapq.heappop(heap)
            self.step(r, m, heap)
            steps += 1
            if verbose and steps % 100000 == 0:
                print("  steps=%d congs=%d holes=%d cur_m=%d waste=%.3g t=%.0fs"
                      % (steps, len(self.congs), len(heap), m,
                         float(self.waste), time.time() - t0), flush=True)
        self.time = time.time() - t0
        return self.congs


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    g = Greedy(M)
    try:
        congs = g.run(verbose=True)
    except Failure as e:
        print("FAILURE:", e, g.stats, "congs:", len(g.congs))
        sys.exit(1)
    mods = [n for _, n in congs]
    print("M=%d: %d congruences, minmod=%d, maxmod=%d (~2^%d), waste=%.4g, "
          "stats=%s, %.1fs"
          % (M, len(congs), min(mods), max(mods), max(mods).bit_length(),
             float(g.waste), g.stats, g.time))
    fn = "/tmp/cover_M%d.json" % M
    with open(fn, "w") as f:
        json.dump({"minmod": M, "congruences": [[a, n] for a, n in congs]}, f)
    print("wrote", fn)


if __name__ == "__main__":
    main()

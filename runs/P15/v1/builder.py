#!/usr/bin/env python3
"""
Explicit mechanized Nielsen/Owens-style builder (P15 variant V1).

Recursive tree construction with a global distinct-modulus registry:

cover_class(r, m):  cover the class r (mod m) completely.
  1. DIRECT: if some divisor d | m with d >= M, d unused, and small
     overshoot waste, emit (r mod d, d).
  2. TREE: pick a prime q; run a q^ chain: at level k (=1..K) the slot
     classes mod m*q^k (q-1 of them) are covered by recursive calls,
     one class continues downward.  After K levels, FINITIZE the leftover
     class mod m*q^K with a fresh-prime divisor chain (Nielsen's
     finitization, generalized).

The structure of real covering systems (Owens's frame) emerges organically:
at the top, only deep 2/3-chains have moduli >= M, producing exactly the
"remove small moduli, fill holes with bigger primes" pattern.

All output is explicit congruences; correctness rests on verify.py alone.
"""
import json
import sys
import time
from fractions import Fraction

sys.setrecursionlimit(100000)


def primes_up_to(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = bytearray(len(sieve[i * i:: i]))
    return [i for i in range(2, n + 1) if sieve[i]]

PRIMES = primes_up_to(100000)


def crt(r1, m1, r2, m2):
    inv = pow(m1, -1, m2)
    return (r1 + (r2 - r1) * inv % m2 * m1) % (m1 * m2)


class Failure(Exception):
    pass


class Builder:
    def __init__(self, M, tree_primes=None, fin_primes=None,
                 fin_target=10 ** 9, beta=7.0, waste_budget=0.9, fin_waste=1e-7,
                 max_depth=200, max_congs=3_000_000, verbose=False):
        self.M = M
        self.TP = tree_primes or PRIMES[:60]
        # finitization primes: small q first (waste ~ q/m is tiny at the
        # chain bottom); registry keeps them from colliding with tree use
        self.FIN = fin_primes or [p for p in PRIMES if p >= 3]
        self.fin_target = fin_target       # chain depth before finitizing
        self.beta = beta                   # allowed relative overshoot
        self.waste_budget = waste_budget   # global absolute waste budget
        self.fin_waste = fin_waste
        self.max_depth = max_depth
        self.max_congs = max_congs
        self.verbose = verbose
        self.used = set()
        self.congs = []
        self.waste = 0.0
        self.fin_idx = 0
        self.chain_radicals = set()   # radicals of existing q^K chains
        self.stats = {"direct": 0, "tree": 0, "finitize": 0}

    @staticmethod
    def radical(n):
        r = 1
        for p in PRIMES:
            if p * p > n:
                break
            if n % p == 0:
                r *= p
                while n % p == 0:
                    n //= p
        return r * (n if n > 1 else 1)

    def emit(self, a, n):
        assert n >= self.M and n not in self.used
        self.used.add(n)
        self.congs.append((a % n, n))
        if len(self.congs) > self.max_congs:
            raise Failure("cong cap")

    # -------------------------------------------------- direct
    def small_divisors(self, m, bound=2048):
        return [s for s in range(1, bound + 1) if m % s == 0]

    @staticmethod
    def divisors_from_fac(fac, bound=10 ** 6, cap=4000):
        """Ascending divisors <= bound generated from a factorization."""
        divs = [1]
        for p, e in fac.items():
            new = []
            for d in divs:
                v = d
                for _ in range(e):
                    v *= p
                    if v > bound:
                        break
                    new.append(v)
            divs += new
            if len(divs) > cap:
                divs = sorted(divs)[:cap]
        return sorted(divs)[:cap]

    def try_direct(self, r, m, fac=None):
        # d = m / s for small s; waste = 1/d - 1/m
        small = (self.divisors_from_fac(fac) if fac
                 else self.small_divisors(m, 64))
        for s in small:
            d = m // s
            if d < self.M:
                break
            if d not in self.used:
                if m < 10 ** 18:
                    w = 1.0 / d - 1.0 / m
                    ok = (w <= self.beta / m
                          and self.waste + w <= self.waste_budget)
                else:
                    w, ok = 0.0, True   # absolute waste < 4e9/1e18
                if s == 1 or ok:
                    self.emit(r % d, d)
                    self.waste += w
                    self.stats["direct"] += 1
                    return True
        return False

    # -------------------------------------------------- finitize
    def try_finitize(self, r, m, fac=None):
        small = (self.divisors_from_fac(fac) if fac
                 else self.small_divisors(m))
        for q in self.FIN[:2000]:
            if m % q == 0:
                continue
            picked = []
            for s in small:
                d = m // s
                v = q * d
                if v >= self.M and v not in self.used:
                    picked.append(d)
                    if len(picked) == q:
                        break
            if len(picked) < q:
                continue
            ssum = sum(m // d for d in picked)
            if m < 10 ** 18:
                if ssum > 30 * q:    # relative waste ~ ssum/q vs chain ratio
                    continue
                w = (ssum / q - 1.0) / m
            else:
                w = 0.0   # true waste <= (cap*bound)/m <= 4e9/1e18
            if self.waste + w > self.waste_budget:
                continue
            for i, d in enumerate(picked):
                self.emit(crt(r % d, d, i, q), q * d)
            self.waste += w
            self.stats["finitize"] += 1
            
            return True
        return False

    # -------------------------------------------------- tree prime choice
    def level1_avail(self, m, q):
        """How many level-1 slots of a q-tree on (mod m) can emit directly."""
        n1 = m * q
        c = 0
        for s in self.small_divisors(n1, 64):
            d = n1 // s
            if d < self.M:
                break
            if d not in self.used and s <= self.beta + 1:
                c += 1
        return c

    def choose_tree_prime(self, m, depth):
        best, best_score = None, None
        for q in self.TP:
            need = q - 1
            avail = self.level1_avail(m, q)
            deficit = max(0, need - avail)
            # if the chain spine m*q^k collides with used moduli, this
            # q-direction is contested: penalize hard
            dup = 1 if any(m * q ** k in self.used for k in (1, 2, 3)) else 0
            score = (dup, deficit, q)
            if best is None or score < best_score:
                best, best_score = q, score
            if deficit == 0 and dup == 0:
                break
        return best

    # -------------------------------------------------- main
    def cover_class(self, r, m, depth=0, fac=None):
        fac = fac or {}
        if self.try_direct(r, m, fac):
            return
        # deep tiny slots: close them with a divisor chain instead of
        # spawning ever-deeper trees (guarantees termination)
        if m >= 10 ** 5 and self.try_finitize(r, m, fac):
            return
        if depth >= self.max_depth:
            if self.try_finitize(r, m, fac):
                return
            raise Failure("depth %d stuck at m=%d" % (depth, m))
        q = self.choose_tree_prime(m, depth)
        self.stats["tree"] += 1
        if self.verbose and (self.stats["tree"] % 500 == 0 or depth > 80):
            print("  tree#%d depth=%d q=%d mbits=%d congs=%d waste=%.3f"
                  % (self.stats["tree"], depth, q, m.bit_length(),
                     len(self.congs), self.waste))
        # chain depth: go until m*q^K >= fin_target (relative to m)
        K = 1
        mk = m * q
        fin_at = max(10 ** 5, m * 300)
        while mk < fin_at:
            K += 1
            mk *= q
        rr, mm = r, m
        kf = dict(fac)
        for k in range(1, K + 1):
            n = mm * q
            kf = dict(kf)
            kf[q] = kf.get(q, 0) + 1
            # q children: cover q-1, continue into child 0
            for i in range(1, q):
                self.cover_class(rr + mm * i, n, depth + 1, kf)
            mm = n
        # extend the chain until finitization succeeds
        for extra in range(64):
            if self.try_finitize(rr, mm, kf):
                return
            n = mm * q
            kf = dict(kf)
            kf[q] = kf.get(q, 0) + 1
            for i in range(1, q):
                self.cover_class(rr + mm * i, n, depth + 1, kf)
            mm = n
        # last resort: treat the chain bottom as a fresh hole (another
        # tree prime will be chosen for it)
        self.cover_class(rr, mm, depth + 1, kf)

    def run(self):
        t0 = time.time()
        self.cover_class(0, 1, 0)
        self.time = time.time() - t0
        return self.congs


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    b = Builder(M, verbose=True)
    try:
        congs = b.run()
    except Failure as e:
        print("FAILURE:", e, b.stats, len(b.congs))
        sys.exit(1)
    mods = [n for _, n in congs]
    print("M=%d: %d congruences minmod=%d maxmod~2^%d waste=%.3g stats=%s %.1fs"
          % (M, len(congs), min(mods), max(mods).bit_length(), b.waste,
             b.stats, b.time))
    fn = "/tmp/builder_M%d.json" % M
    json.dump({"minmod": M, "congruences": [[a, n] for a, n in congs]},
              open(fn, "w"))
    print("wrote", fn)


if __name__ == "__main__":
    main()

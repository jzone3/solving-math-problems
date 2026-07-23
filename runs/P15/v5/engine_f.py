"""Engine F: breadth-first layered chain construction with deferral.

Global architecture of Nielsen's hand constructions, mechanized without DFS
backtracking: a work-queue of uncovered cells, processed smallest-modulus
first.  For each cell try, in order:
  1. inherit  (cell inside an already-placed class),
  2. base     (unused modulus M >= L, or an unused divisor >= L),
  3. chain+tail (pick q, p minimizing modulus waste; place tail first),
  4. defer    (split along the cheapest prime and push children).
No rollback: every placed class stays; failures just split cells finer.
Cells are processed globally, so modulus allocation is a single greedy
bin-packing over the whole tree rather than per-branch DFS.
"""
import argparse
import json
import random
import sys
import time
from bisect import bisect_right, insort
from heapq import heappush, heappop
from math import gcd

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
          139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def crt(r1, m1, r2, m2):
    assert gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


class Builder:
    def __init__(self, L, caps, max_mod=10**12, rng=None):
        self.L = L
        self.caps = caps
        self.max_mod = max_mod
        self.rng = rng
        self.used = set()
        self.by_mod = {}
        self.mods = []  # sorted list of placed moduli
        self.out = []

    def padic(self, n, p):
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        return e

    def mod_ok(self, m):
        if m in self.used or m > self.max_mod:
            return False
        mm = m
        for p in PRIMES:
            if p * p > mm:
                break
            e = 0
            while mm % p == 0:
                mm //= p
                e += 1
            if e > self.caps.get(p, 0):
                return False
        if mm > 1:
            if self.caps.get(mm, 0) < 1:
                return False
        return True

    def take(self, a, m):
        self.used.add(m)
        self.by_mod[m] = a % m
        insort(self.mods, m)
        self.out.append((a % m, m))

    def inherited(self, a, M):
        for m in self.mods[:bisect_right(self.mods, M)]:
            if M % m == 0 and a % m == self.by_mod[m]:
                return True
        return False

    def divisors(self, n):
        divs = [1]
        nn = n
        for p in PRIMES:
            if p * p > nn:
                break
            e = 0
            while nn % p == 0:
                nn //= p
                e += 1
            if e:
                divs = [d * p**k for d in divs for k in range(e + 1)]
        if nn > 1:
            divs = [d * nn for d in divs] + divs
        return divs

    def split_hint(self, a, M):
        best = None
        for m in self.mods[:bisect_right(self.mods, 64 * M)]:
            r = self.by_mod[m]
            if M % m == 0:
                continue
            g = gcd(m, M)
            if a % g != (r % g):
                continue
            ratio = m // g
            if ratio <= 64 and (best is None or ratio < best[0]):
                for q in PRIMES:
                    if ratio % q == 0:
                        best = (ratio, q)
                        break
        return best[1] if best else None

    def try_base(self, a, M):
        if M >= self.L and self.mod_ok(M):
            self.take(a, M)
            return True
        if M >= self.L:
            for d in sorted(self.divisors(M), reverse=True):
                if d >= self.L and self.mod_ok(d):
                    self.take(a % d, d)
                    return True
        return False

    def try_chain(self, a, M, pending):
        """Place a q-chain with p-tail on the cell; push children cells to
        pending. Returns True if a (q,p,K) with valid, unused tail moduli was
        found."""
        L = self.L
        cands = []
        for q in PRIMES:
            if self.padic(M, q) >= self.caps.get(q, 0):
                continue
            for p in PRIMES:
                if p == q or M % p == 0 or self.caps.get(p, 0) < 1:
                    continue
                K = p - 1
                while p * M * q ** (K + 1 - p) < L:
                    K += 1
                if self.padic(M, q) + K > self.caps.get(q, 0):
                    continue
                if M * q ** K * p > self.max_mod:
                    continue
                tail = [p * M * q ** (K + 1 - j) for j in range(1, p + 1)]
                if len(set(tail)) != len(tail):
                    continue
                if not all(self.mod_ok(m) for m in tail):
                    continue
                # waste = sum of reciprocals of tail moduli relative to the
                # covered measure (1/M); prefer small p, small q^K
                waste = sum(1.0 / m for m in tail) * M
                cands.append((waste, q, p, K, tail))
            if len(cands) >= 8:
                break
        if not cands:
            return False
        cands.sort()
        if self.rng is not None and len(cands) > 1:
            i = min(int(self.rng.expovariate(1.5)), len(cands) - 1)
        else:
            i = 0
        _, q, p, K, tail = cands[i]
        b = a
        for j in range(1, p + 1):
            anc = M * q ** (K + 1 - j)
            self.take(crt(b % anc, anc, j % p, p), p * anc)
        for k in range(1, K + 1):
            step = M * q ** (k - 1)
            mod_k = M * q ** k
            for i2 in range(1, q):
                heappush(pending, (mod_k, (b + i2 * step) % mod_k))
        return True

    def build(self, verbose=True):
        pending = [(1, 0)]
        steps = 0
        while pending:
            steps += 1
            M, a = heappop(pending)
            if verbose and steps % 20000 == 0:
                print(f"  steps {steps}, placed {len(self.out)}, "
                      f"pending {len(pending)}, front M={M}", flush=True)
            if self.inherited(a, M):
                continue
            if self.try_base(a, M):
                continue
            hint = self.split_hint(a, M)
            if hint is not None and M * hint <= self.max_mod \
                    and self.padic(M, hint) < self.caps.get(hint, 0):
                for i in range(hint):
                    heappush(pending, (M * hint, (a + i * M) % (M * hint)))
                continue
            if self.try_chain(a, M, pending):
                continue
            # defer: split along cheapest usable prime
            for q in PRIMES:
                if self.padic(M, q) < self.caps.get(q, 0) \
                        and M * q <= self.max_mod:
                    for i in range(q):
                        heappush(pending, (M * q, (a + i * M) % (M * q)))
                    break
            else:
                return False, len(pending)
            if steps > 3_000_000 or len(pending) > 2_000_000:
                return False, len(pending)
        return True, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--caps", default="2:24,3:15,5:10,7:8,11:6,13:6,17:4,19:4,"
                    "23:3,29:3,31:3,37:2,41:2,43:2,47:2,53:2,59:2,61:2,67:2,"
                    "71:1,73:1,79:1,83:1,89:1,97:1,101:1,103:1")
    ap.add_argument("--max-mod", type=float, default=1e12)
    ap.add_argument("--restarts", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    caps = {}
    for tok in a.caps.split(","):
        p, e = tok.split(":")
        caps[int(p)] = int(e)
    t0 = time.time()
    for it in range(a.restarts):
        rng = random.Random(a.seed + it) if it > 0 else None
        b = Builder(a.L, caps, max_mod=int(a.max_mod), rng=rng)
        ok, left = b.build()
        if ok:
            mods = [m for _, m in b.out]
            assert len(set(mods)) == len(mods)
            print(f"SUCCESS: {len(b.out)} congruences, min modulus "
                  f"{min(mods)}, max modulus {max(mods)}, "
                  f"{time.time()-t0:.1f}s")
            out = a.out or f"witness_F_L{a.L}.json"
            with open(out, "w") as f:
                json.dump({"L": a.L,
                           "congruences": [[r, m] for r, m in b.out]}, f)
            print(f"wrote {out}")
            return
        print(f"restart {it} FAILED ({len(b.out)} placed, {left} pending, "
              f"{time.time()-t0:.1f}s)", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()

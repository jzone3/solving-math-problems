#!/usr/bin/env python3
"""
CRT/tree-structured greedy cover builder (P15 V1, fourth push).

No cell arrays: the uncovered set is a list of residue-class fragments
(r, m) with m | N, refined lazily (exactly the covers_all structure in
solutions/P15/verify.py, run constructively). N can therefore be
astronomically rich in reciprocal slack (primes up to 19/23), which the
array engines could never afford.

Greedy loop: take the largest uncovered fragment (min m); pick an unused
modulus n preferring small lcm(m, n)/m (least splitting) and small waste;
the congruence a is pinned on gcd(m, n) to lie inside the fragment and
its free CRT coordinates are chosen to hit as many other big fragments
as possible. Applying congruence (a, n) refines each intersecting
fragment: the fragment is split along the primes of lcm and the covered
sub-fragment removed.

Usage: fc_tree.py M [factorization like "2^7,3^5,5^3,7^2,11,13,17,19"]
Writes /tmp/fct_M{M}.json on success.
"""
import heapq
import json
import sys
import time
from math import gcd

DEFAULT_FACT = "2^7,3^5,5^3,7^2,11,13,17,19"


def parse_fact(s):
    pps = []
    for part in s.split(","):
        if "^" in part:
            p, e = part.split("^")
            pps.append((int(p), int(e)))
        else:
            pps.append((int(part), 1))
    return pps


def divisors_of(pps, lo, hi):
    ds = [1]
    for p, e in pps:
        ds = [d * p**k for d in ds for k in range(e + 1)]
    return sorted(d for d in ds if lo <= d <= hi)


def lcm(a, b):
    return a // gcd(a, b) * b


class Builder:
    def __init__(self, M, pps, max_mod=None):
        self.M = M
        self.pps = pps
        self.N = 1
        for p, e in pps:
            self.N *= p**e
        self.max_mod = max_mod or self.N
        self.mods = divisors_of(pps, M, self.max_mod)
        self.unused = set(self.mods)
        # uncovered fragments: dict m -> set of residues r
        self.frags = {1: {0}}
        self.mass = 1.0          # total uncovered density
        self.chosen = []

    def prime_split(self, m, n):
        """Smallest m' with m | m', n | m', m' | N, as a chain from m."""
        return lcm(m, n)

    def refine(self, r, m, mm):
        """Split fragment (r, m) into fragments mod mm (m | mm)."""
        q = mm // m
        return [r + t * m for t in range(q)]

    def apply(self, a, n):
        """Remove intersection of class (a, n) from all fragments."""
        newfrags = {}
        for m, rs in self.frags.items():
            g = gcd(m, n)
            L = lcm(m, n)
            keep = set()
            for r in rs:
                if (r - a) % g != 0:
                    keep.add(r)
                    continue
                # fragment intersects the congruence; split to mod L
                for rr in self.refine(r, m, L):
                    if (rr - a) % n != 0:
                        newfrags.setdefault(L, set()).add(rr)
                self.mass -= 1.0 / L
            if keep:
                newfrags.setdefault(m, set()).update(keep)
        # merge duplicate moduli entries
        self.frags = newfrags
        self.chosen.append((a, n))
        self.unused.discard(n)

    def biggest_frag(self):
        m = min(self.frags)
        r = next(iter(self.frags[m]))
        return r, m

    def pick_mod(self, r, m):
        """Unused modulus n minimizing split factor lcm(m,n)/m, then n."""
        best = None
        for n in self.unused:
            L = lcm(m, n)
            if L > self.N:
                continue
            key = (L // m, n)
            if best is None or key < best[0]:
                best = (key, n)
        return None if best is None else best[1]

    def choose_residue(self, r, m, n):
        """Pin a inside fragment (r, m); pick free coordinates to also hit
        the largest other fragments."""
        g = gcd(m, n)
        # candidates: residues a mod n with a ≡ r (mod g)
        cands = [r % g + t * g for t in range(n // g)]
        if len(cands) == 1:
            return cands[0]
        # score candidates by mass hit across current fragments (sampled)
        items = []
        for mm, rs in self.frags.items():
            w = 1.0 / mm
            for rr in rs:
                items.append((w, rr, mm))
        items.sort(reverse=True)
        items = items[:2000]
        best_a, best_s = cands[0], -1.0
        for a in cands:
            s = 0.0
            for w, rr, mm in items:
                gg = gcd(mm, n)
                if (rr - a) % gg == 0:
                    s += 1.0 / lcm(mm, n)
            if s > best_s:
                best_s, best_a = s, a
        return best_a

    def top_items(self, K):
        items = []
        for mm, rs in self.frags.items():
            w = 1.0 / mm
            for rr in rs:
                items.append((w, rr, mm))
        items.sort(reverse=True)
        return items[:K]

    def best_class_for(self, n, items):
        """Best residue a mod n by covered-mass over sampled fragments.
        Candidate a's are pinned from the fragments themselves."""
        cands = {}
        for w, rr, mm in items:
            g = gcd(mm, n)
            cands.setdefault(rr % g if g else 0, None)
            a = rr % n if mm % n == 0 or n <= mm else rr % g
            cands[a] = None
            if len(cands) >= 48:
                break
        best_a, best_s = None, 0.0
        for a in cands:
            s = 0.0
            for w, rr, mm in items:
                g = gcd(mm, n)
                if (rr - a) % g == 0:
                    s += 1.0 / lcm(mm, n)
            if s > best_s:
                best_s, best_a = s, a
        return best_a, best_s

    def run(self, time_limit=3600, report=15.0, K=400):
        """Gain-density greedy over unused moduli, sparse fragments."""
        t0 = time.time()
        last = t0
        while self.frags:
            if time.time() - t0 > time_limit:
                print("TIMEOUT: mass=%.3g frags=%d chosen=%d"
                      % (self.mass, sum(len(v) for v in self.frags.values()),
                         len(self.chosen)), flush=True)
                return False
            if not self.unused:
                print("EXHAUSTED mods: mass=%.3g frags=%d"
                      % (self.mass,
                         sum(len(v) for v in self.frags.values())),
                      flush=True)
                return False
            items = self.top_items(K)
            # evaluate a shortlist of moduli: the smallest unused ones plus
            # divisors aligned with the biggest fragment
            r0, m0 = self.biggest_frag()
            small = sorted(self.unused)[:24]
            aligned = [n for n in self.unused
                       if lcm(m0, n) // m0 <= 4][:24]
            best = None
            for n in set(small + aligned):
                a, s = self.best_class_for(n, items)
                if a is None:
                    continue
                key = s / n
                if best is None or key > best[0]:
                    best = (key, a, n)
            if best is None:
                print("STUCK: no productive modulus; mass=%.3g" % self.mass,
                      flush=True)
                return False
            _, a, n = best
            self.apply(a, n)
            if time.time() - last > report:
                print("  chosen=%d mass=%.4g frags=%d unused=%d"
                      % (len(self.chosen), self.mass,
                         sum(len(v) for v in self.frags.values()),
                         len(self.unused)), flush=True)
                last = time.time()
        return True


def main():
    M = int(sys.argv[1])
    fact = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FACT
    tl = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    pps = parse_fact(fact)
    b = Builder(M, pps)
    print("M=%d N=%d mods=%d recip=%.3f"
          % (M, b.N, len(b.mods), sum(1.0 / n for n in b.mods)), flush=True)
    ok = b.run(tl, K=K)
    if ok:
        congs = sorted(b.chosen, key=lambda t: t[1])
        fn = "/tmp/fct_M%d.json" % M
        json.dump({"minmod": M,
                   "congruences": [[int(a), int(n)] for a, n in congs]},
                  open(fn, "w"))
        print("SUCCESS M=%d congs=%d -> %s" % (M, len(congs), fn))


if __name__ == "__main__":
    main()

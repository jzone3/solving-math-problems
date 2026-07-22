#!/usr/bin/env python3
"""
Mechanized Nielsen/Owens-style covering-system constructor (P15, variant V1).

Idea: generalize the hand "up-arrow + finitization" method into a uniform
recursive engine:

  cover(hole H = (r mod m), ancestors = nested enclosing holes):
    1. If modulus m is >= M and globally unused: emit (r, m).            [direct]
    2. Else, if the ancestor chain is deep enough, FINITIZE: choose a
       prime q not dividing m and q nested ancestor classes A_1..A_q
       (deepest available, including H itself) with all moduli q*n_i
       unused; emit the q classes (i mod q) CRT (A_i).  Every x in H
       falls in some i mod q and x is in every ancestor, so H is covered.
       This is exactly Nielsen's finitization p(2^n, 2^{n-1}, ...),
       generalized to arbitrary mixed-radix chains.                      [finitize]
    3. Else split H into p children mod m*p for a chosen prime p and
       recurse.                                                          [split]

Distinct moduli are enforced by a global registry.  The waste of a
finitization relative to the hole size is ~ sum m/(q*n_i), controlled by
requiring deep chains before finitizing.

This always terminates *if* moduli remain available; contention for modulus
values is the real obstruction, mirroring the difficulty of the hand method.
"""
import json
import sys
import time
from math import gcd

# ---------------------------------------------------------------------------

def primes_up_to(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = bytearray(len(sieve[i * i:: i]))
    return [i for i in range(2, n + 1) if sieve[i]]


def crt(r1, m1, r2, m2):
    """solve x=r1 (m1), x=r2 (m2), gcd(m1,m2)=1"""
    g, x, _ = ext_gcd(m1, m2)
    assert g == 1
    lcm = m1 * m2
    return (r1 + (r2 - r1) * x % m2 * m1) % lcm


def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y


class Failure(Exception):
    pass


class Engine:
    def __init__(self, M, structural_primes, fresh_primes, depth_slack=6,
                 max_depth=300, max_congs=2_000_000, rng=None):
        self.M = M
        self.SP = structural_primes           # primes used for splitting
        self.FP = fresh_primes                # extra primes for finitization
        self.used = set()                     # modulus registry
        self.congs = []                       # list of (a, n)
        self.depth_slack = depth_slack        # extra depth beyond q before finitize
        self.max_depth = max_depth
        self.max_congs = max_congs
        self.rng = rng
        self.waste_per_call = 1e-4
        self.total_waste = 0.0
        self.stats = {"direct": 0, "finitize": 0, "split": 0, "fin_classes": 0}

    def emit(self, a, n):
        assert n >= self.M and n not in self.used
        self.used.add(n)
        self.congs.append((a % n, n))
        if len(self.congs) > self.max_congs:
            raise Failure("too many congruences")

    # -- finitization ------------------------------------------------------
    def try_finitize(self, r, m, anc):
        """anc: list of (res, mod) nested, outermost first. Hole itself
        counts as deepest.  Returns True on success."""
        chain = anc + [(r, m)]
        depth = len(chain)
        # candidate primes: q not dividing m, need q + depth_slack <= depth
        cands = [q for q in (self.SP + self.FP)
                 if m % q != 0 and q + self.depth_slack <= depth]
        for q in cands:
            # choose the q deepest chain entries with q*n unused
            picked = []
            for (rr, nn) in reversed(chain):
                if nn % q == 0:
                    continue
                v = q * nn
                if v >= self.M and v not in self.used and v not in [q * x[1] for x in picked]:
                    picked.append((rr, nn))
                    if len(picked) == q:
                        break
            if len(picked) < q:
                continue
            # waste check: ABSOLUTE extra measure consumed by this
            # finitization (the classes live inside ancestors, mostly
            # already covered).  Keep a global waste ledger.
            overhead = sum(1.0 / (q * nn) for _, nn in picked) - 1.0 / m
            if overhead > self.waste_per_call:
                continue
            # emit: residue classes i (mod q) intersect picked[i]
            for i, (rr, nn) in enumerate(picked):
                a = crt(rr, nn, i, q)
                self.emit(a, q * nn)
            self.stats["finitize"] += 1
            self.stats["fin_classes"] += q
            self.total_waste += overhead
            return True
        return False

    # -- split prime choice -------------------------------------------------
    def choose_split_prime(self, m, depth):
        # prefer smallest structural prime whose next modulus is unused;
        # tie-break to 2 to build cheap deep chains for finitization
        best = None
        for p in self.SP:
            if m * p not in self.used:
                return p
            if best is None:
                best = p
        return best or self.SP[0]

    # -- main recursion ------------------------------------------------------
    def cover(self, r, m, anc):
        if m >= self.M and m not in self.used:
            self.used.add(m)
            self.congs.append((r % m, m))
            self.stats["direct"] += 1
            if len(self.congs) > self.max_congs:
                raise Failure("too many congruences")
            return
        if self.try_finitize(r, m, anc):
            return
        if len(anc) >= self.max_depth:
            raise Failure("max depth exceeded at modulus %d" % m)
        p = self.choose_split_prime(m, len(anc))
        self.stats["split"] += 1
        anc2 = anc + [(r, m)]
        order = list(range(p))
        if self.rng:
            self.rng.shuffle(order)
        for i in order:
            self.cover(r + m * i, m * p, anc2)

    def run(self):
        sys.setrecursionlimit(100000)
        t0 = time.time()
        self.cover(0, 1, [])
        self.time = time.time() - t0
        return self.congs


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    sp_bound = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    slack = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    ps = primes_up_to(5000)
    SP = [p for p in ps if p <= sp_bound]
    FP = [p for p in ps if p > sp_bound]
    eng = Engine(M, SP, FP, depth_slack=slack)
    try:
        congs = eng.run()
    except Failure as e:
        print("FAILURE:", e, eng.stats, "congs so far:", len(eng.congs))
        sys.exit(1)
    mods = [n for _, n in congs]
    print("built cover: M=%d congs=%d minmod=%d maxmod~2^%d stats=%s time=%.1fs"
          % (M, len(congs), min(mods), max(mods).bit_length(), eng.stats, eng.time))
    out = {"minmod": M, "congruences": [[a, n] for a, n in congs]}
    fn = "/tmp/cover_M%d.json" % M
    with open(fn, "w") as f:
        json.dump(out, f)
    print("wrote", fn)


if __name__ == "__main__":
    main()

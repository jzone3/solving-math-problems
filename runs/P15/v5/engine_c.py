"""Engine C: faithful mechanization of the Nielsen arrow calculus.

A cover of Z with min modulus Lmin (moduli coprime to `forb`, and every emitted
modulus m reserved globally as {mu*m : mu in muls}) is built as
    s-arrow: s^chain with inputs alpha_1..alpha_{s-1}, where input j is a
    RECIPE R_j (itself a cover of Z, built recursively with Lmin/s and
    forb+{s}) applied at EVERY level k: classes CRT(j*s^{k-1} mod s^k, r mod m)
    with modulus s^k*m.  The SAME recipe serves all K levels -- this reuse is
    the whole point of the arrow notation (Nielsen 2009 sec. 2), and is what
    flat per-cell recursion (engine_b) fatally lacks.
    Tail: the last cell 0 mod s^K is finitized with a prime p (coprime),
    K >= p-1, classes CRT(0 mod s^{K+1-j}, j mod p), moduli p*s^{K+1-j}.
Global registry of actual moduli guarantees distinctness.
"""
import argparse
import json
import random
import sys
import time
from math import gcd

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
          139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def crt(r1, m1, r2, m2):
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


class Fail(Exception):
    pass


class Builder:
    def __init__(self, L, max_mod=10**14, s_tries=5, p_tries=4, k_tries=2,
                 rng=None):
        self.L = L
        self.max_mod = max_mod
        self.s_tries = s_tries
        self.p_tries = p_tries
        self.k_tries = k_tries
        self.rng = rng
        self.verbose = False
        self.used = set()

    def reserve(self, m, muls, log):
        acts = [mu * m for mu in muls]
        if any(a in self.used or a > self.max_mod for a in acts):
            raise Fail("reserve")
        for a in acts:
            self.used.add(a)
            log.append(a)

    def unreserve(self, log, mark):
        for a in log[mark:]:
            self.used.discard(a)
        del log[mark:]

    def build(self, Lmin, forb, muls, depth=0):
        """Return list of (r, m): cover of Z, m coprime to forb, m >= Lmin,
        reserving {mu*m} globally.  Raises Fail."""
        if depth > 12:
            raise Fail("depth")
        log = []
        # base case: trivial cover 0 mod 1 (the chain class itself)
        if Lmin <= 1:
            try:
                self.reserve(1, muls, log)
                return [(0, 1)]
            except Fail:
                self.unreserve(log, 0)
        cands = [s for s in PRIMES if s not in forb]
        if self.rng is not None:
            head = cands[:5]
            self.rng.shuffle(head)
            cands = head + cands[5:]
        tried_s = 0
        for s in cands:
            if tried_s >= self.s_tries:
                break
            tried_s += 1
            tried_p = 0
            for p in PRIMES:
                if p == s or p in forb:
                    continue
                if tried_p >= self.p_tries:
                    break
                tried_p += 1
                # minimal K: K >= p-1 and p*s^{K+1-p} >= Lmin
                for extra in range(self.k_tries):
                    K = p - 1
                    while p * s ** (K + 1 - p) < Lmin:
                        K += 1
                    K += extra
                    mark = len(log)
                    try:
                        cover = []
                        # tail classes
                        for j in range(1, p + 1):
                            m = p * s ** (K + 1 - j)
                            if m < Lmin:
                                raise Fail("tailmin")
                            self.reserve(m, muls, log)
                            cover.append(
                                (crt(0, s ** (K + 1 - j), j % p, p), m))
                        # inputs: recipe for each residue j=1..s-1, reused at
                        # all levels k=1..K
                        inner_muls = [mu * s ** k for mu in muls
                                      for k in range(1, K + 1)]
                        Linner = (Lmin + s - 1) // s
                        for j in range(1, s):
                            R = self.build(Linner, forb | {s}, inner_muls,
                                           depth + 1)
                            for k in range(1, K + 1):
                                cell_r = j * s ** (k - 1)
                                cell_m = s ** k
                                for r, m in R:
                                    if m == 1:
                                        cover.append((cell_r, cell_m))
                                    else:
                                        cover.append(
                                            (crt(cell_r, cell_m, r, m),
                                             cell_m * m))
                        return cover
                    except Fail as e:
                        if self.verbose:
                            print(f"{'  '*depth}d{depth} s={s} p={p} K={K} "
                                  f"-> {e}", flush=True)
                        self.unreserve(log, mark)
                        continue
        raise Fail(f"build Lmin={Lmin} forb={sorted(forb)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--max-mod", type=float, default=1e14)
    ap.add_argument("--restarts", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sys.setrecursionlimit(100000)
    t0 = time.time()
    cover = None
    for it in range(a.restarts):
        rng = random.Random(a.seed + it) if it > 0 else None
        b = Builder(a.L, max_mod=int(a.max_mod), rng=rng)
        try:
            cover = b.build(a.L, frozenset(), [1])
            break
        except Fail as e:
            print(f"restart {it} FAILED: {e} ({time.time()-t0:.1f}s)",
                  flush=True)
    if cover is None:
        print("FAILED all restarts")
        sys.exit(1)
    mods = [m for _, m in cover]
    assert len(set(mods)) == len(mods)
    print(f"SUCCESS: {len(cover)} congruences, min modulus {min(mods)}, "
          f"max modulus {max(mods)}, {time.time()-t0:.1f}s")
    out = a.out or f"witness_C_L{a.L}.json"
    with open(out, "w") as f:
        json.dump({"L": a.L, "congruences": [[r, m] for r, m in cover]}, f)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

"""Engine H: Engine G's exact planning + the missing 'x'-mark ingredient.

Tower-packing diagnosis (NOTES.md Section 14): chain inputs starve because
each demands its own prime-power tower of distinct moduli.  The literature's
'x' entries let inputs SHARE towers: a cell already covered by a previously
placed class costs nothing.  Engine E had this inheritance but starved at
L=10 anyway, because its small-p tails wasted ~1/3 of every chain's measure.
Engine H combines:

  - concrete (residue-aware) DFS cover of cells, with rollback;
  - inheritance: a cell contained in any placed class is free ('x');
  - waste-aware tails: tail prime p and depth K chosen so the tail's
    absolute measure is below eps -- chains become nearly lossless;
  - fat-first hole ordering over a thinned 2-adic skeleton;
  - global registry of distinct moduli (all > = L).

Transactional: covering a hole either commits a full plan or rolls back.
"""
import argparse
import json
import sys
import time
from bisect import bisect_right, insort
from math import gcd

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131]


def crt(r1, m1, r2, m2):
    assert gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


class Fail(Exception):
    pass


class Builder:
    def __init__(self, L, max_mod=10**22, eps=0.02, max_depth=24):
        self.L = L
        self.max_mod = max_mod
        self.eps = eps
        self.max_depth = max_depth
        self.used = set()
        self.by_mod = {}
        self.mods = []          # sorted moduli, for inheritance scans
        self.out = []
        self.calls = 0

    # -- registry ----------------------------------------------------------
    def take(self, r, m, log):
        if m < self.L or m > self.max_mod or m in self.used:
            raise Fail("mod")
        self.used.add(m)
        self.by_mod[m] = r % m
        insort(self.mods, m)
        self.out.append((r % m, m))
        log.append(m)

    def rollback(self, log, n_out):
        for m in log:
            self.used.discard(m)
            self.by_mod.pop(m, None)
            self.mods.remove(m)
        del self.out[n_out:]

    def inherited(self, a, M):
        for m in self.mods[:bisect_right(self.mods, M)]:
            if M % m == 0 and a % m == self.by_mod[m]:
                return True
        return False

    # -- cover -------------------------------------------------------------
    def cover(self, a, M, depth, log):
        """Cover cell (a mod M) completely, else raise Fail."""
        self.calls += 1
        if self.calls % 200000 == 0:
            print(f"  calls {self.calls} (M~1e{len(str(M))-1}, d={depth})",
                  flush=True)
        if self.inherited(a, M):
            return
        if depth > self.max_depth:
            raise Fail("depth")
        if M >= self.L and M not in self.used:
            self.take(a, M, log)
            return
        # try q-chains, smallest q first (fattest coverage per class)
        last = None
        for q in PRIMES[:10]:
            if M % q == 0 and q != 2:
                # allowed: chain along q even if q | M (levels use q^k * M)
                pass
            mark = len(log)
            n_out = len(self.out)
            try:
                self.chain(a, M, q, depth, log)
                return
            except Fail as e:
                last = e
                self.rollback(log[mark:], n_out)
                del log[mark:]
        raise last or Fail("no-q")

    def chain(self, a, M, q, depth, log):
        # pick tail prime p (coprime to q*M) and depth K, waste-aware
        cands = []
        for p in PRIMES:
            if p == q or M % p == 0:
                continue
            K = max(p - 1, 1)
            while p * q ** (K + 1 - p) * M < self.L:
                K += 1
            if M * q ** K * p > self.max_mod:
                continue
            waste = sum(1.0 / (p * q ** (K + 1 - j))
                        for j in range(1, p + 1)) / M
            cands.append((waste > self.eps, p, K, waste))
        if not cands:
            raise Fail("tail")
        cands.sort(key=lambda t: (t[0], t[1]))
        errs = 0
        for _, p, K, _w in cands:
            mark = len(log)
            n_out = len(self.out)
            try:
                # tail first (children inherit from it)
                for j in range(1, p + 1):
                    anc = M * q ** (K + 1 - j)
                    self.take(crt(a % anc, anc, j % p, p), p * anc, log)
                # levels
                for k in range(1, K + 1):
                    step = M * q ** (k - 1)
                    mod_k = M * q ** k
                    for i in range(1, q):
                        self.cover(a + i * step, mod_k, depth + 1, log)
                return
            except Fail:
                errs += 1
                self.rollback(log[mark:], n_out)
                del log[mark:]
                if errs >= 4:
                    break
        raise Fail("chain")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--eps", type=float, default=0.02)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    L = a.L
    t0 = time.time()
    bld = Builder(L, eps=a.eps)
    k0 = 1
    while 2 ** k0 < L:
        k0 += 1
    n = k0 + 6
    log = []
    holes = []
    for k in range(1, n + 1):
        child = 2 ** (k - 1)
        if k >= k0:
            bld.take(child, 2 ** k, log)
        else:
            holes.append((child, 2 ** k))
    holes.append((0, 2 ** n))
    holes.sort(key=lambda t: t[1])
    for (a_, M) in holes:
        try:
            bld.cover(a_, M, 0, log)
        except Fail as e:
            print(f"FAILED at hole {a_} mod {M}: {e}")
            sys.exit(1)
        print(f"hole {a_} mod {M}: done, {len(bld.out)} classes so far",
              flush=True)
    mods = [m for _, m in bld.out]
    assert len(set(mods)) == len(mods)
    print(f"SUCCESS: {len(bld.out)} congruences, min modulus {min(mods)}, "
          f"max modulus {max(mods):.3e}, {time.time()-t0:.1f}s"
          .replace("e+", "e"))
    out = a.out or f"witness_H_L{L}.json"
    with open(out, "w") as f:
        json.dump({"L": L, "congruences": [[r, m] for r, m in bld.out]}, f)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

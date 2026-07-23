"""Engine E: Engine B's q-arrow chains PLUS inherited-coverage bookkeeping
(the 'x' marks of Nielsen/Owens tables) — the ingredient whose absence made
Engines B/C starve (NOTES.md Section 7).

New over Engine B, in cover_cell(a, M):
  inherit:  if any placed class (r, m) with m | M and a = r (mod m) already
            contains the cell, return at zero cost.  Tail classes placed in
            other branches thus cover cells here for free.
  guided split: if a placed class (r, m) intersects the cell (a = r mod
            gcd(m, M)) with small lcm(m, M)/M, split the cell along a prime
            of m / gcd and recurse: the sub-cell inside the class inherits.
Backtracking DFS over q, p, and split choices with a global modulus registry.
"""
import argparse
import json
import random
import sys
import time

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
          139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def crt(r1, m1, r2, m2):
    # gcd(m1, m2) == 1
    from math import gcd
    assert gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


class Fail(Exception):
    pass


class Builder:
    def __init__(self, L, caps, max_mod=10**13, max_depth=40,
                 q_tries=10, p_tries=8, rng=None):
        self.rng = rng
        self.L = L
        self.caps = caps
        self.max_mod = max_mod
        self.max_depth = max_depth
        self.q_tries = q_tries
        self.p_tries = p_tries
        self.used = set()
        self.out = []
        self.calls = 0
        self.by_mod = {}  # m -> residue r (moduli are distinct)

    def _divisors(self, n):
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
            divs = [d * nn**k for d in divs for k in range(2)]
        return divs

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
        if mm > 1:  # leftover prime
            if mm not in self.caps or self.caps[mm] < 1:
                return False
        return True

    def take(self, a, m, log):
        self.used.add(m)
        self.by_mod[m] = a % m
        self.out.append((a % m, m))
        log.append(m)

    def rollback(self, n_out):
        for rr, mm in self.out[n_out:]:
            self.used.discard(mm)
            self.by_mod.pop(mm, None)
        del self.out[n_out:]

    def inherited(self, a, M):
        # cell (a mod M) fully inside an already-placed class?
        for m, r in self.by_mod.items():
            if M % m == 0 and a % m == r:
                return True
        return False

    def split_hint(self, a, M):
        # placed class partially intersecting the cell, covering the largest
        # fraction: returns prime to split along, or None
        from math import gcd
        best = None
        for m, r in self.by_mod.items():
            if M % m == 0:
                continue
            g = gcd(m, M)
            if a % g != (r % g):
                continue
            ratio = m // g  # lcm/M; class covers 1/ratio of the cell
            if ratio <= 256 and (best is None or ratio < best[0]):
                for q in PRIMES:
                    if ratio % q == 0:
                        best = (ratio, q)
                        break
        return best[1] if best else None

    def cover_cell(self, a, M, depth=0):
        self.calls += 1
        if self.calls % 20000 == 0:
            print(f"  calls {self.calls}, out {len(self.out)}, cell {a} mod {M} "
                  f"depth {depth}", flush=True)
        if depth > self.max_depth:
            raise Fail("depth")
        L = self.L
        if self.inherited(a, M):
            return
        if M >= L and self.mod_ok(M):
            log = []
            self.take(a, M, log)
            return
        # overlap base case: any unused divisor d | M with d >= L covers the
        # whole cell (with overlap) via class a mod d
        if M >= L:
            for d in sorted(self._divisors(M), reverse=True):
                if d >= L and self.mod_ok(d):
                    log = []
                    self.take(a % d, d, log)
                    return
        # guided split toward a partially-covering placed class
        hint = self.split_hint(a, M)
        if hint is not None and M * hint <= self.max_mod:
            n_out = len(self.out)
            try:
                for i in range(hint):
                    self.cover_cell(a + i * M, M * hint, depth + 1)
                return
            except Fail:
                self.rollback(n_out)
        # chain on prime q: prefer primes not dividing M (diversification,
        # mirroring the literature's prime-per-branch structure)
        tried = 0
        fresh = [q for q in PRIMES if M % q != 0]
        stale = [q for q in PRIMES if M % q == 0]
        if self.rng is not None:
            head = fresh[:6]
            self.rng.shuffle(head)
            fresh = head + fresh[6:]
        q_order = fresh + stale
        for q in q_order:
            if tried >= self.q_tries:
                break
            if q not in self.caps:
                continue
            eq = self.padic(M, q)
            if eq >= self.caps[q]:
                continue
            tried += 1
            p_tried = 0
            # candidate finitizing primes p (small, coprime to M*q)
            for p in PRIMES:
                if p_tried >= self.p_tries:
                    break
                if p == q or M % p == 0 or self.caps.get(p, 0) < 1:
                    continue
                # K >= p-1 and p*M*q^{K+1-p} >= L; take minimal such K
                K = p - 1
                while p * M * q ** (K + 1 - p) < L:
                    K += 1
                if eq + K > self.caps[q] or M * q**K > self.max_mod:
                    continue
                tail_mods = [p * M * q ** (K + 1 - j) for j in range(1, p + 1)]
                if not all(self.mod_ok(m) for m in tail_mods):
                    continue
                if len(set(tail_mods)) != len(tail_mods):
                    continue
                p_tried += 1
                # attempt
                n_out = len(self.out)
                log = []
                try:
                    b = a
                    # tail fill FIRST: these classes partially cover the
                    # chain's children, so the recursion below inherits
                    for j in range(1, p + 1):
                        anc_mod = M * q ** (K + 1 - j)
                        r = crt(b % anc_mod, anc_mod, j % p, p)
                        m = p * anc_mod
                        if not self.mod_ok(m):
                            raise Fail("tailmod")
                        self.take(r, m, log)
                    for k in range(1, K + 1):
                        # children of level k-1 tail: residues b + i*M*q^{k-1}
                        step = M * q ** (k - 1)
                        mod_k = M * q ** k
                        for i in range(1, q):
                            self.cover_cell(b + i * step, mod_k, depth + 1)
                        # tail child keeps residue b
                    return
                except Fail:
                    self.rollback(n_out)
                    continue
        raise Fail(f"cell {a} mod {M}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--caps", default="2:24,3:15,5:10,7:8,11:6,13:6,17:4,19:4,"
                    "23:3,29:3,31:3,37:2,41:2,43:2,47:2,53:2,59:2,61:2,67:2,"
                    "71:1,73:1,79:1,83:1,89:1,97:1,101:1,103:1")
    ap.add_argument("--max-mod", type=float, default=1e13)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    caps = {}
    for tok in a.caps.split(","):
        p, e = tok.split(":")
        caps[int(p)] = int(e)
    sys.setrecursionlimit(100000)
    t0 = time.time()
    b = None
    for it in range(a.restarts):
        rng = random.Random(a.seed + it) if it > 0 else None
        b = Builder(a.L, caps, max_mod=int(a.max_mod), rng=rng)
        try:
            b.cover_cell(0, 1)
            break
        except Fail as e:
            print(f"restart {it} FAILED: {e} ({len(b.out)} classes, "
                  f"{b.calls} calls, {time.time()-t0:.1f}s)", flush=True)
            b = None
    if b is None:
        print("FAILED all restarts")
        sys.exit(1)
    mods = [m for _, m in b.out]
    print(f"SUCCESS: {len(b.out)} congruences, min modulus {min(mods)}, "
          f"max modulus {max(mods)}, {time.time()-t0:.1f}s")
    out = a.out or f"witness_E_L{a.L}.json"
    with open(out, "w") as f:
        json.dump({"L": a.L, "congruences": [[r, m] for r, m in b.out]}, f)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

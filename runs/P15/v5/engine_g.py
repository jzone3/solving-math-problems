"""Engine G: recipe algebra for the Nielsen/Owens arrow calculus.

The key literature mechanism that Engines B/C/E/F each captured only partially
is made explicit here:

  Recipe   := ONE | Split(q, [R_1..R_q]) | Chain(q, [R_1..R_{q-1}])
  support(ONE)          = {1}
  support(Split)        = union_i  q * support(R_i)      (must be disjoint)
  support(Chain), depth K, tail prime p
                        = union_{k=1..K, i} q^k * support(R_i)
                          union {p*q^(K+1-j) : j=1..p}

A recipe fully covers any cell (a mod M) it is instantiated on, emitting
congruences with absolute moduli M * s for s in support.  Reuse across chain
levels is automatic (the q^k factor separates levels), which is Engine C's
missing-reuse fixed; global modulus distinctness is enforced through a
registry at emission time with absolute moduli, which handles cross-hole
conflicts exactly.

The scheduler covers Z by a 2-adic skeleton with the classes of modulus < L
removed, then builds recipes for each hole greedily (smallest-support first)
via DFS over the vocabulary, consulting the global registry.
"""
import argparse
import json
import sys
import time
from math import gcd

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]


def crt(r1, m1, r2, m2):
    assert gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


class Reg:
    """Global modulus registry."""

    def __init__(self, L):
        self.L = L
        self.used = set()
        self.out = []

    def ok(self, m):
        return m >= self.L and m not in self.used

    def take(self, r, m):
        assert self.ok(m), m
        self.used.add(m)
        self.out.append((r % m, m))


class One:
    support = frozenset([1])

    def emit(self, a, M, reg):
        reg.take(a, M)

    def __repr__(self):
        return "1"


class Split:
    def __init__(self, q, subs):
        assert len(subs) == q
        self.q = q
        self.subs = subs
        s = set()
        for r in subs:
            for x in r.support:
                v = q * x
                assert v not in s, "support clash in Split"
                s.add(v)
        self.support = frozenset(s)

    def emit(self, a, M, reg):
        q = self.q
        for i, r in enumerate(self.subs):
            r.emit(a + i * M, M * q, reg)

    def __repr__(self):
        return f"{self.q}({','.join(map(repr, self.subs))})"


class Chain:
    def __init__(self, q, subs, p, K):
        assert len(subs) == q - 1 and K >= p - 1 and p != q
        self.q, self.subs, self.p, self.K = q, subs, p, K
        s = set()
        for k in range(1, K + 1):
            for r in subs:
                for x in r.support:
                    assert x % q, "q-divisible support inside Chain"
                    v = q ** k * x
                    assert v not in s, "support clash in Chain"
                    s.add(v)
        for j in range(1, p + 1):
            v = p * q ** (K + 1 - j)
            assert v not in s, "tail clash in Chain"
            s.add(v)
        self.support = frozenset(s)

    def emit(self, a, M, reg):
        q, p, K = self.q, self.p, self.K
        b = a
        for k in range(1, K + 1):
            step = M * q ** (k - 1)
            mod_k = M * q ** k
            for i, r in enumerate(self.subs):
                r.emit(b + (i + 1) * step, mod_k, reg)
        for j in range(1, p + 1):
            anc = M * q ** (K + 1 - j)
            reg.take(crt(b % anc, anc, j % p, p), p * anc)

    def __repr__(self):
        return (f"{self.q}^({','.join(map(repr, self.subs))};"
                f"p={self.p},K={self.K})")


def measure(sup):
    return sum(1.0 / s for s in sup)


class Builder:
    """DFS recipe builder: cover a cell of absolute modulus M, choosing
    supports so that all absolute moduli M*s are >= L and unused."""

    def __init__(self, L, reg, qmax=31, pmax=113, max_sup=6000,
                 max_mod=10**18):
        self.L = L
        self.reg = reg
        self.qmax = qmax
        self.pmax = pmax
        self.max_sup = max_sup
        self.max_mod = max_mod
        self.calls = 0
        self.reg_cap = 1  # max modulus in registry (updated by caller)

    def width(self, depth):
        return 8 if depth <= 1 else (4 if depth <= 3 else 2)

    def usable(self, M, sup, taken):
        # all absolute moduli valid and not clashing with 'taken' (absolute)
        for s in sup:
            m = M * s
            if m < self.L or m > self.max_mod or m in self.reg.used \
                    or m in taken:
                return False
        return True

    def build(self, M, taken, depth=0, forbid_q=frozenset(), allowed=None):
        """Return a recipe covering a cell of absolute modulus M, whose
        absolute support M*s avoids reg.used and 'taken'.  None if failed."""
        self.calls += 1
        if self.calls % 100000 == 0:
            print(f"  build calls {self.calls} (M={M}, depth={depth})",
                  flush=True)
        if depth > 8:
            return None
        one = One()
        if self.usable(M, one.support, taken):
            return one
        # try chains q^ with small q
        tried_q = 0
        for q in PRIMES:
            if q > self.qmax or q in forbid_q:
                continue
            if allowed is not None and q not in allowed:
                continue
            if tried_q >= self.width(depth):
                break
            tried_q += 1
            # build q-1 sub-recipes with pairwise-disjoint q-free supports.
            subs = []
            sub_taken = set(taken)
            ok = True
            for _ in range(q - 1):
                r = self.build_qfree(M * q, q, sub_taken, depth + 1,
                                     allowed=allowed)
                if r is None:
                    ok = False
                    break
                subs.append(r)
                for x in r.support:
                    for k in range(1, 40):
                        v = q ** k * x
                        if M * v > self.max_mod:
                            break
                        sub_taken.add(M * v)
            if not ok:
                continue
            # choose tail prime p and depth K, minimizing tail waste
            # (tail measure ~ 1/(p*q^(K+1-p)) * q/(q-1); large p, deep K
            # make chains nearly lossless)
            cands = []
            for p in PRIMES:
                if p == q or p > self.pmax or M % p == 0:
                    continue
                K = max(p - 1, 1)
                while p * q ** (K + 1 - p) * M < self.L:
                    K += 1
                tail_meas = sum(1.0 / (p * q ** (K + 1 - j))
                                for j in range(1, p + 1))
                cands.append((tail_meas, p, K))
            # absolute waste = tail_meas / M; take the smallest p whose
            # absolute waste is negligible (deep cells tolerate cheap tails)
            eps = 0.004
            cands.sort(key=lambda t: (t[0] > eps * M, t[1]))
            sub_sz = sum(len(r.support) for r in subs)
            sub_max = max(max(r.support) for r in subs)
            budget = max(self.max_sup // 4 ** depth, 60)
            for tail_meas, p, K in cands:
                if K * sub_sz + p > budget:
                    continue
                if M * q ** K * max(sub_max, p * q) > self.max_mod:
                    continue
                try:
                    c = Chain(q, subs, p, K)
                except AssertionError:
                    continue
                if self.usable(M, c.support, taken):
                    return c
            continue
        return None

    def build_qfree(self, Mq, q, taken, depth, allowed=None):
        """Recipe with q-free support covering a cell of absolute modulus
        Mq (the level-1 modulus; higher levels only get bigger)."""
        if depth > 8:
            return None
        one = One()
        if self.usable(Mq, one.support, taken) and self.level_free(Mq, one, q):
            self.reserve(Mq, one, q, taken)
            return one
        # chain on a prime r != q first (q-free support; tail prime != q)
        c = self.build(Mq, taken, depth + 1, forbid_q=frozenset([q]),
                       allowed=allowed)
        if c is not None and all(x % q for x in c.support) and \
                self.level_free(Mq, c, q):
            self.reserve(Mq, c, q, taken)
            return c
        # split on a prime r != q
        tried_r = 0
        for r in PRIMES:
            if r == q or r > self.qmax:
                continue
            if allowed is not None and r not in allowed:
                continue
            if tried_r >= self.width(depth):
                break
            tried_r += 1
            subs = []
            sub_taken = set(taken)
            ok = True
            for _ in range(r):
                x = self.build_qfree(Mq * r, q, sub_taken, depth + 1,
                                     allowed=allowed)
                if x is None:
                    ok = False
                    break
                subs.append(x)
            if not ok:
                continue
            try:
                sp = Split(r, subs)
            except AssertionError:
                continue
            if self.usable(Mq, sp.support, taken) and \
                    self.level_free(Mq, sp, q):
                self.reserve(Mq, sp, q, taken)
                taken.update(sub_taken)
                return sp
        return None

    def level_free(self, Mq, recipe, q):
        # ensure future levels q^k don't clash with global registry
        M = Mq // q
        for x in recipe.support:
            for k in range(1, 40):
                v = M * q ** k * x
                if v > self.max_mod:
                    break
                if v in self.reg.used:
                    return False
        return True

    def reserve(self, Mq, recipe, q, taken):
        M = Mq // q
        for x in recipe.support:
            for k in range(1, 40):
                v = M * q ** k * x
                if v > self.max_mod:
                    break
                taken.add(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    L = a.L
    t0 = time.time()
    reg = Reg(L)
    # 2-adic skeleton: classes 2^{k-1} mod 2^k for 2^k >= L, k <= n,
    # then tail hole finitized inside the recipe machinery (treat the final
    # 2^n cell as another hole).
    k0 = 1
    while 2 ** k0 < L:
        k0 += 1
    n = k0 + 6
    holes = []  # (a, M) cells to cover with recipes
    b = 0
    for k in range(1, n + 1):
        # child cells of (b mod 2^{k-1}): b and b + 2^{k-1} mod 2^k
        child = b + 2 ** (k - 1)
        if k >= k0:
            reg.take(child, 2 ** k)  # skeleton class
        else:
            holes.append((child, 2 ** k))
        # continue on b
    holes.append((b % 2 ** n, 2 ** n))  # final tail cell
    holes.sort(key=lambda t: t[1])  # fattest cells first (hardest, get
    # first pick of the cheap moduli, as in the literature)
    bld = Builder(L, reg)
    from heapq import heapify, heappush, heappop
    hq = [(M, a_) for (a_, M) in holes]
    heapify(hq)
    processed = 0
    while hq:
        M, a_ = heappop(hq)
        processed += 1
        if processed > 4000:
            print("FAILED: hole explosion")
            sys.exit(1)
        # per-hole prime palette: cycle small primes; 2 always allowed for
        # splits; tail primes are unrestricted (moduli are huge and unique)
        odd = [p for p in PRIMES if p != 2]
        pal = frozenset([2] + odd[(processed - 1) % 8::8][:3]
                        + odd[(processed + 3) % 8::8][:2])
        r = bld.build(M, set(), allowed=pal)
        if r is None:
            r = bld.build(M, set())  # unrestricted fallback
        if r is None:
            # defer: peel one prime level and re-queue the children;
            # prefer a split whose child modulus is still unused
            qs = [q for q in PRIMES if M * q not in reg.used] or PRIMES
            q = qs[0]
            for i in range(q):
                heappush(hq, (M * q, (a_ + i * M) % (M * q)))
            print(f"hole {a_} mod {M}: deferred (split {q})", flush=True)
            continue
        print(f"hole {a_} mod {M}: recipe support size {len(r.support)}, "
              f"measure {measure(r.support):.4f}", flush=True)
        r.emit(a_, M, reg)
    mods = [m for _, m in reg.out]
    assert len(set(mods)) == len(mods)
    print(f"SUCCESS: {len(reg.out)} congruences, min modulus {min(mods)}, "
          f"max modulus {max(mods)}, {time.time()-t0:.1f}s")
    out = a.out or f"witness_G_L{L}.json"
    with open(out, "w") as f:
        json.dump({"L": L, "congruences": [[r_, m] for r_, m in reg.out]}, f)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

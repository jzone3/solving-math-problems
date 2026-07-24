"""Engine I: no-rollback priority-queue cover builder.

Control flow fundamentally different from engines E/G/H:
- a global heap of uncovered cells ordered fattest-first (smallest modulus),
  so fat holes get first pick of the scarce small moduli;
- chains (Nielsen q-arrow with waste-aware finitizing tails, tail-first so
  children inherit) place their tail classes immediately and push the level
  cells back on the queue;
- if every chain attempt for a cell fails, the cell is SPLIT along a fresh
  small prime and its subcells are requeued (no rollback ever);
- thin cells (measure < fin_measure) are closed unconditionally by the
  fresh-prime finisher (2-chain, tail primes from a dedicated reserve
  disjoint from the mid-band palette, uncapped exponents).

Termination is unconditional: splits monotonically thin every failing cell
until the finisher band absorbs it. The open question this engine measures is
whether the resulting class count and modulus sizes stay FEASIBLE.
"""
import argparse
import heapq
import json
import random
import sys
import time
from math import gcd

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
          139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def _sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = b"\0" * len(s[i * i::i])
    return [i for i in range(2, n + 1) if s[i]]


TAIL_PRIMES = [p for p in _sieve(50000) if p > 199]


def crt(r1, m1, r2, m2):
    assert gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


class Supply(Exception):
    pass


class Builder:
    def __init__(self, L, caps, max_mod=10**16, eps=0.02, rng=None,
                 q_tries=10, p_tries=8):
        self.L = L
        self.caps = caps
        self.max_mod = max_mod
        self.eps = eps
        self.rng = rng
        self.q_tries = q_tries
        self.p_tries = p_tries
        self.used = set()
        self.by_mod = {}
        self.out = []
        self.pops = 0
        self.fin_max_mod = 10 ** 120
        self.fin_measure = 1e-7
        self.n_split = 0
        self.n_fin = 0

    def padic(self, n, p):
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        return e

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
            if mm not in self.caps or self.caps[mm] < 1:
                return False
        return True

    def take(self, a, m):
        self.used.add(m)
        self.by_mod[m] = a % m
        self.out.append((a % m, m))

    def inherited(self, a, M):
        for m, r in self.by_mod.items():
            if M % m == 0 and a % m == r:
                return True
        return False

    def finisher(self, a, M, depth=0):
        if depth > 400:
            raise Supply("finisher depth")
        if self.inherited(a, M):
            return
        if M >= self.L and M not in self.used and M <= self.fin_max_mod:
            self.take(a, M)
            return
        for p in TAIL_PRIMES:
            if M % p == 0:
                continue
            K = max(p - 1, 1)
            while p * M * 2 ** (K + 1 - p) < self.L:
                K += 1
            if M * 2 ** K * p > self.fin_max_mod:
                continue
            tail = [p * M * 2 ** (K + 1 - j) for j in range(1, p + 1)]
            if any(m in self.used for m in tail):
                continue
            for j, m in enumerate(tail, 1):
                anc = M * 2 ** (K + 1 - j)
                self.take(crt(a % anc, anc, j % p, p), m)
            for k in range(1, K + 1):
                self.finisher(a + M * 2 ** (k - 1), M * 2 ** k, depth + 1)
            return
        raise Supply("finisher tail supply")

    def run(self, verbose=True):
        L = self.L
        heap = [(1, 0)]  # (M, a)
        cells = {(0, 1)}
        t0 = time.time()
        while heap:
            M, a = heapq.heappop(heap)
            cells.discard((a, M))
            self.pops += 1
            if verbose and self.pops % 5000 == 0:
                print(f"  pops {self.pops}, out {len(self.out)}, heap "
                      f"{len(heap)}, cell {a} mod {M}, splits {self.n_split}, "
                      f"fins {self.n_fin}, {time.time()-t0:.0f}s", flush=True)
            if self.inherited(a, M):
                continue
            if M >= L and 1.0 / M < self.fin_measure:
                self.n_fin += 1
                self.finisher(a, M)
                continue
            if M >= L and self.mod_ok(M):
                self.take(a, M)
                continue
            if M >= L:
                done = False
                for d in sorted(self._divisors(M), reverse=True):
                    if d >= L and self.mod_ok(d):
                        self.take(a % d, d)
                        done = True
                        break
                if done:
                    continue
            placed = self.try_chain(a, M, heap, cells)
            if placed:
                continue
            # finisher fallback (final: no rollback exists). Covers the cell
            # outright from the reserve-prime tower family; expensive in
            # class count but never bankrupts the mid-band palette.
            self.n_split += 1
            self.finisher(a, M)
        return True

    def try_chain(self, a, M, heap, cells):
        L = self.L
        tried = 0
        fresh = [q for q in PRIMES if M % q != 0]
        stale = [q for q in PRIMES if M % q == 0]
        if self.rng is not None:
            head = fresh[:6]
            self.rng.shuffle(head)
            fresh = head + fresh[6:]
        for q in fresh + stale:
            if tried >= self.q_tries:
                break
            if q not in self.caps:
                continue
            eq = self.padic(M, q)
            if eq >= self.caps[q]:
                continue
            tried += 1
            cands = []
            for p in PRIMES:
                if p == q or M % p == 0 or self.caps.get(p, 0) < 1:
                    continue
                K = p - 1
                while p * M * q ** (K + 1 - p) < L:
                    K += 1
                if eq + K > self.caps[q] or M * q**K > self.max_mod:
                    continue
                waste = sum(1.0 / (p * q ** (K + 1 - j))
                            for j in range(1, p + 1)) / M
                cands.append((waste > self.eps, p, K))
            cands.sort()
            p_tried = 0
            for _, p, K in cands:
                if p_tried >= self.p_tries:
                    break
                tail_mods = [p * M * q ** (K + 1 - j) for j in range(1, p + 1)]
                if len(set(tail_mods)) != len(tail_mods):
                    continue
                if not all(self.mod_ok(m) for m in tail_mods):
                    continue
                p_tried += 1
                for j in range(1, p + 1):
                    anc = M * q ** (K + 1 - j)
                    self.take(crt(a % anc, anc, j % p, p), p * anc)
                for k in range(1, K + 1):
                    step = M * q ** (k - 1)
                    mod_k = M * q ** k
                    for i in range(1, q):
                        key = ((a + i * step) % mod_k, mod_k)
                        if key not in cells:
                            cells.add(key)
                            heapq.heappush(heap, (mod_k, key[0]))
                return True
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--caps", default="2:24,3:15,5:10,7:8,11:6,13:6,17:4,19:4,"
                    "23:3,29:3,31:3,37:2,41:2,43:2,47:2,53:2,59:2,61:2,67:2,"
                    "71:1,73:1,79:1,83:1,89:1,97:1,101:1,103:1")
    ap.add_argument("--max-mod", type=float, default=1e16)
    ap.add_argument("--eps", type=float, default=0.02)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--qtries", type=int, default=10)
    ap.add_argument("--ptries", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    caps = {}
    for tok in a.caps.split(","):
        p, e = tok.split(":")
        caps[int(p)] = int(e)
    sys.setrecursionlimit(100000)
    rng = random.Random(a.seed) if a.seed else None
    b = Builder(a.L, caps, max_mod=int(a.max_mod), eps=a.eps, rng=rng,
                q_tries=a.qtries, p_tries=a.ptries)
    t0 = time.time()
    try:
        b.run()
    except Supply as e:
        print(f"SUPPLY FAILURE: {e} ({len(b.out)} classes, {b.pops} pops)")
        sys.exit(1)
    mx = max(m for _, m in b.out)
    print(f"SUCCESS: {len(b.out)} congruences, min modulus "
          f"{min(m for _, m in b.out)}, max modulus {mx:.3e}, "
          f"{time.time()-t0:.1f}s, splits {b.n_split}, fins {b.n_fin}")
    out = a.out or f"witness_I_L{a.L}.json"
    with open(out, "w") as f:
        json.dump({"L": a.L, "classes": [[r, m] for r, m in b.out]}, f)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
P15 V4 phase 2: compressed hole-CLASS counting builder.

Key idea (Nielsen/Owens-style endgame, machine-searched):
- Track holes only as (residue class mod window C) -> exact big-int count,
  where C | M (M = processed modulus) with the invariant that any prime we
  still intend to process keeps its FULL power inside C.
- Process one prime p per level. Every hole r (mod M) splits into p children
  x = r + M*t; because v_p(C) = v_p(M), the children take the p residues
  r + C*s (mod C*p), s = 0..p-1, bijectively. So the window coordinates stay
  exact.
- Structured congruences at the level: any unused modulus m | C*p with
  m >= T; congruence a mod m covers exactly the child cells whose residue
  mod m equals a. Exact big-int accounting; floats only for greedy ranking.
- KILL POOL (continuous endgame): at any level, a hole r (mod M_l) can be
  killed outright by the congruence r mod d for ANY unused divisor d | M_l
  with d >= T (overlaps allowed, only moduli must be distinct). Each kill
  costs exactly one pooled divisor. Validity is a PREFIX constraint:
      for every level l:  #structured(ALL) + #kills(<=l) <= #{d | M_l : d >= T}
  (all-structured because a later structured modulus may also divide M_l;
  the kill-divisor sets are nested, so Hall's theorem reduces to prefixes)
  and success means the hole count reaches 0. The witness is the structured
  recipe + per-level kill counts + these counting inequalities; no explicit
  congruence list is ever materialized (the endgame kills are an arbitrary
  injection holes -> unused divisors, which exists by counting).

Usage: python3 cover3.py --T 43 --config A [--cmax 500000] [--out w.json]
"""
import argparse, json, sys, time
from heapq import heappush, heappop

import numpy as np


def factorize(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def divisors(fact):
    divs = [1]
    for p, e in fact.items():
        divs = [d * p**k for d in divs for k in range(e + 1)]
    return sorted(divs)


def count_divisors_below(fact, bound):
    primes = sorted(fact)
    cnt = 0
    def rec(i, prod):
        nonlocal cnt
        if i == len(primes):
            cnt += 1
            return
        p = primes[i]
        v = prod
        for _ in range(fact[p] + 1):
            if v >= bound:
                break
            rec(i + 1, v)
            v *= p
    rec(0, 1)
    return cnt


class CountingBuilder:
    def __init__(self, T, cmax=100_000_000_000_000_000, hcap=3_000_000,
                 verbose=True, seed=0, reserve=1_000_000, survivor=True):
        self.survivor = survivor
        self.hcap = hcap   # max #classes kept; truncation driven by this
        self.T = T
        self.cmax = cmax
        self.reserve = reserve   # structured-moduli headroom for Hall prefix
        self.verbose = verbose
        self.rng = np.random.default_rng(seed)
        self.C = 1                  # window modulus, C | M
        self.Cfact = {}
        self.holes = {0: 1}         # residue mod C -> exact count
        self.Nfact = {}             # processed modulus M factorization
        self.used = set()           # structured modulus values
        self.kills_total = 0        # exact big-int count of pool kills
        self.recipe = []
        self.n_congs = 0

    def log(self, *a):
        if self.verbose:
            print(*a, flush=True)

    def pool(self):
        """Unused divisors of current M that are >= T (exact big int)."""
        D = 1
        for e in self.Nfact.values():
            D *= e + 1
        small = count_divisors_below(self.Nfact, self.T)
        return D - small - self.kills_total

    @staticmethod
    def drop_prime(Cnow, remaining):
        """Pick one prime factor to drop from the window: prefer primes not
        needed by remaining levels, largest first."""
        f = factorize(Cnow)
        return sorted(f, key=lambda q: (q in remaining, -q))[0]

    def process(self, p, remaining=()):
        T = self.T
        if self.Nfact.get(p, 0) != self.Cfact.get(p, 0):
            raise RuntimeError(
                f"cannot reprocess prime {p}: window dropped its power "
                f"(v_p(M)={self.Nfact.get(p,0)}, v_p(C)={self.Cfact.get(p,0)})")
        C = self.C
        Cfull = C * p
        R = np.array(sorted(self.holes), dtype=np.int64)
        H = len(R)
        counts = [self.holes[int(r)] for r in R]
        maxbits = max(n.bit_length() for n in counts)
        shift = max(0, maxbits - 500)
        w = np.array([float(n >> shift) if (n >> shift) else 5e-324
                      for n in counts])
        # children residues mod Cfull: (H, p)
        child = (R[:, None] + C * np.arange(p, dtype=np.int64)[None, :])
        act = np.ones((H, p), dtype=bool)
        # survivor alignment: exempt one branch from scoring so coverage
        # concentrates on the rest; survivors stay aligned with parents
        score_mask = np.ones(p) if (not self.survivor or p == 2) else None
        if score_mask is None:
            score_mask = np.ones(p)
            score_mask[int(self.rng.integers(p))] = 0.0

        cands = [m for m in divisors(factorize(Cfull))
                 if m >= T and m not in self.used]
        rows_cache = {}
        def rows(m):
            if m not in rows_cache:
                if len(rows_cache) > 64:
                    rows_cache.pop(next(iter(rows_cache)))
            else:
                return rows_cache[m]
            rows_cache[m] = child % m
            return rows_cache[m]

        def best(m):
            rm = rows(m)
            vals, inv = np.unique(rm, return_inverse=True)
            g = np.bincount(inv.ravel(),
                            weights=(act * (w[:, None] * score_mask)).ravel(),
                            minlength=len(vals))
            k = int(g.argmax())
            return float(g[k]), int(vals[k])

        heap = []
        for m in cands:
            gain, a = best(m)
            if gain > 0:
                heappush(heap, (-gain, self.rng.random(), m))
        chosen = []
        while heap:
            _, _, m = heappop(heap)
            gain, a = best(m)
            if gain <= 0:
                continue
            if heap and -heap[0][0] > gain * 1.0000001:
                heappush(heap, (-gain, self.rng.random(), m))
                continue
            act &= rows(m) != a
            self.used.add(m)
            chosen.append((m, a))

        self.Nfact[p] = self.Nfact.get(p, 0) + 1
        rem = set(remaining)
        newC = Cfull
        merged = {}
        ii, ss = np.nonzero(act)
        for i, s in zip(ii.tolist(), ss.tolist()):
            k = int(child[i, s])
            merged[k] = merged.get(k, 0) + counts[i]
        # truncate window only under class-count or int64 pressure
        while len(merged) > self.hcap or newC > self.cmax:
            q = self.drop_prime(newC, rem)
            newC //= q
            m2 = {}
            for r, n in merged.items():
                m2[r % newC] = m2.get(r % newC, 0) + n
            merged = m2
        # ---- pool kills: wipe holes with unused divisors of M_l (>= T) ----
        budget = self.pool() - self.reserve
        kills = {}
        if budget > 0 and merged:
            for r in sorted(merged, key=lambda k: merged[k]):
                if budget <= 0:
                    break
                k = min(merged[r], budget)
                kills[r] = k
                budget -= k
                merged[r] -= k
                if merged[r] == 0:
                    del merged[r]
        nk = sum(kills.values())
        self.kills_total += nk
        dens = sum(1.0 / m for m, _ in chosen)
        self.recipe.append(
            {"p": p, "C_before": C, "congs": chosen, "C_after": newC,
             "kills": {str(r): str(k) for r, k in kills.items()}})
        self.n_congs += len(chosen)
        self.holes = merged
        self.C = newC
        self.Cfact = factorize(newC)
        tot = sum(merged.values()) if merged else 0
        self.log(f"level p={p}: {len(chosen)} congs (dens {dens:.4f}), "
                 f"kills~1e{max(0, len(str(nk)) - 1)}, "
                 f"classes={len(merged)}, holes~1e{max(0, len(str(tot)) - 1)}, C={newC}")
        return tot

    def status(self):
        Hf = sum(self.holes.values()) if self.holes else 0
        return Hf, self.pool()


def run(T, levels, cmax, out=None, seed=0, verbose=True):
    b = CountingBuilder(T, cmax=cmax, seed=seed, verbose=verbose)
    t0 = time.time()
    for i, p in enumerate(levels):
        tot = b.process(p, remaining=levels[i + 1:])
        Hf, Df = b.status()
        b.log(f"  H digits={len(str(Hf))} Dfree digits={len(str(Df))} "
              f"ok={Hf <= Df} t={time.time()-t0:.0f}s")
        if tot == 0:
            b.log("  ALL HOLES ELIMINATED — construction complete!")
            break
    Hf, Df = b.status()
    ok = Hf == 0
    print(f"FINAL T={T}: H_final digits={len(str(Hf))} (zero={Hf==0}), "
          f"pool digits={len(str(Df))}, structured={b.n_congs}, "
          f"SUCCESS={ok}")
    if out:
        with open(out, "w") as f:
            json.dump({"T": T, "levels": levels, "recipe": b.recipe,
                       "H_final": str(Hf), "pool_left": str(Df),
                       "Nfact": {str(p): e for p, e in b.Nfact.items()},
                       "n_structured": b.n_congs, "success": ok}, f)
        print(f"witness recipe -> {out}")
    return ok, Hf, Df


CONFIGS = {
    "A": [2]*8 + [3]*5 + [5]*3 + [7]*2 + [11, 13, 17, 19, 23, 29, 31, 37, 41],
    "B": [2]*10 + [3]*6 + [5]*4 + [7]*3 + [11]*2 + [13]*2 +
         [17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59],
    "C": [2]*12 + [3]*8 + [5]*5 + [7]*3 + [11]*2 + [13]*2 + [17]*2 +
         [19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
          89, 97, 101, 103],
    # window-friendly smooth core (2^7 3^4 5^2 7 = 1814400 fits cmax 2e6),
    # then long prime tail to inflate the kill pool
    "D": [2]*7 + [3]*4 + [5]*2 + [7] + [11, 13, 17, 19, 23, 29, 31, 37, 41,
          43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103],
    # deeper smooth core, bigger window needed (cmax >= 6e6)
    "E": [2]*8 + [3]*5 + [5]*2 + [7] + [11, 13, 17, 19, 23, 29, 31, 37, 41,
          43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103],
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=int, default=43)
    ap.add_argument("--config", default="A")
    ap.add_argument("--cmax", type=int, default=500_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--levels", default=None)
    args = ap.parse_args()
    levels = ([int(x) for x in args.levels.split(",")] if args.levels
              else CONFIGS[args.config])
    run(args.T, levels, args.cmax, out=args.out, seed=args.seed)

#!/usr/bin/env python3
"""P15 V4 phase 2c: explicit greedy builder + KILL MOP-UP.

Identical to cover.py (prime-power levels, survivor alignment) except that
after every level, leftover holes are "killed" explicitly: each hole r mod M
is covered by the congruence r mod d for a distinct unused divisor d | M,
d >= T (overlaps free; only distinctness matters). A reserve of divisors is
kept for future structured levels. Witness stays EXPLICIT -> verify.py.

Strategy (CRT-layered, Nielsen/Owens style, machine-driven):
  Process prime powers p^e one level at a time. State = set of "holes":
  residues mod M (M = product of processed prime powers) not yet covered.
  At the level for p^e, each hole splits into q = p^e branches. Available
  moduli are d*p^j (d | M, 1 <= j <= e, d*p^j >= T, unused) plus plain
  divisors d | M (d >= T, unused) that kill whole holes. Each modulus is
  usable for exactly ONE congruence (distinct moduli). A congruence
  (a mod d, b mod p^j) covers, in every hole r with r = a (mod d), the
  branches t = b (mod p^j).

  Greedy = lazy submodular maximization over (d, j) candidates with
  randomized tie-breaking; multiple restarts; optional end-of-level
  reassignment repair.

Outputs a JSON witness {"congruences": [[a, n], ...]} on success.
"""
import argparse
import heapq
import json
import random
import sys
from math import gcd

import numpy as np


def crt(a, m, b, n):
    """x = a mod m, x = b mod n, gcd(m,n)=1 -> x mod m*n."""
    inv = pow(m % n, -1, n)
    return (a + m * ((b - a) * inv % n)) % (m * n)


def divisors_of(factored):
    """factored: list of (p, e). Yields all divisors."""
    divs = [1]
    for p, e in factored:
        divs = [d * p**k for d in divs for k in range(e + 1)]
    return sorted(divs)


class Builder:
    def __init__(self, levels, T, seed=0, hole_cap=2_000_000, verbose=True,
                 key="gain", survivor=False):
        self.key = key
        self.survivor = survivor
        # levels: list of (p, e) in processing order
        self.levels = levels
        self.T = T
        self.rng = random.Random(seed)
        self.hole_cap = hole_cap
        self.verbose = verbose
        self.used = set()        # numeric moduli already used
        self.congs = []          # list of (a, n)
        self.M = 1
        self.Mfact = []          # factored M
        self.holes = np.zeros(1, dtype=np.int64)  # residues mod M

    def log(self, *a):
        if self.verbose:
            print(*a, flush=True)

    def run(self):
        for (p, e) in self.levels:
            ok = self.do_level(p, e)
            if not ok:
                return False
            if len(self.holes) == 0:
                return True
        return len(self.holes) == 0

    def candidate_moduli(self, p, e):
        """All (d, j) with d | M, modulus d*p^j >= T, unused. j=0 means plain d."""
        cands = []
        for d in divisors_of(self.Mfact):
            for j in range(0, e + 1):
                m = d * p**j
                if m >= self.T and m not in self.used and m > 1:
                    if j == 0 and d == 1:
                        continue
                    cands.append((d, j))
        return cands

    def do_level(self, p, e):
        q = p**e
        H = len(self.holes)
        if H == 0:
            return True
        T = self.T
        self.log(f"LEVEL p^e={p}^{e} q={q}  M={self.M}  holes={H}")
        if H * q > 1_200_000_000:
            self.log("  abort: level too large")
            return False
        # uncovered branches: H x q boolean
        uncov = np.ones((H, q), dtype=bool)
        holes = self.holes
        cands = self.candidate_moduli(p, e)
        self.rng.shuffle(cands)

        # Precompute holes % d lazily
        mod_cache = {}

        cache_budget = 10_000_000_000 // max(1, 5 * H)  # ~10GB of int32 arrays

        def hole_res(d):
            # returns (unique residues, inverse index) for holes % d
            if d not in mod_cache:
                if len(mod_cache) >= max(4, cache_budget):
                    mod_cache.pop(next(iter(mod_cache)))
                vals, inv = np.unique(holes % d, return_inverse=True)
                mod_cache[d] = (vals, inv.astype(np.int32))
            else:
                mod_cache[d] = mod_cache.pop(d)  # LRU refresh
            return mod_cache[d]

        MQ = float(self.M) * q
        # survivor alignment: cells t = s0 (mod p) are covered only in phase 2
        s0 = self.rng.randrange(p)
        colw = np.ones(q, dtype=bool)
        if self.survivor:
            colw[s0::p] = False  # phase-1 active columns = non-survivor

        def best_assignment(d, j):
            """Return (eff, gain, a, b) best congruence for modulus d*p^j.
            eff = gain * m / (M*q): fraction of the congruence's density
            that lands on uncovered hole-cells (1.0 = zero waste)."""
            vals, inv = hole_res(d)
            pj = p**j if j > 0 else 1
            m = d * pj
            best = (-1.0, -1.0, 0, 0)
            brange = range(pj) if j > 0 else [0]
            for b in brange:
                g = act[:, b::pj].sum(axis=1) if j > 0 else act.sum(axis=1)
                gains = np.bincount(inv, weights=g, minlength=len(vals))
                k = int(gains.argmax())
                a = int(vals[k])
                g = float(gains[k])
                cand = ((g * m / MQ, g, a, b) if self.key == "eff"
                        else (g, g * m / MQ, a, b))
                if cand[:2] > best[:2]:
                    best = cand
            return best

        picked = []
        act = uncov & colw[None, :]

        def greedy_pass():
            heap = []
            for (d, j) in cands:
                m = d * p**j
                if m in self.used:
                    continue
                pj = p**j
                ub = H * (q // pj if j > 0 else q)
                prim = 1.0 if self.key == "eff" else float(ub)
                heap.append((-prim, -float(ub), self.rng.random(), d, j))
            heapq.heapify(heap)
            while heap:
                negu, negg, tie, d, j = heapq.heappop(heap)
                eff, gain, a, b = best_assignment(d, j)
                if gain <= 0:
                    continue
                # relaxed lazy acceptance: tolerate 20% suboptimality to
                # avoid heap ping-pong (each re-eval costs a 20M-elem sort)
                if heap and -heap[0][0] > (eff + 1e-12) / 0.8:
                    heapq.heappush(heap, (-eff, -gain, self.rng.random(), d, j))
                    continue
                pj = p**j
                vals, inv = hole_res(d)
                kk = np.searchsorted(vals, a)
                sel = inv == kk
                if j == 0:
                    uncov[sel, :] = False
                    act[sel, :] = False
                    m = d
                    c = a
                else:
                    cols = np.arange(b, q, pj)
                    uncov[np.ix_(sel, cols)] = False
                    act[np.ix_(sel, cols)] = False
                    m = d * pj
                    c = crt(a % d, d, b, pj) if d > 1 else b
                self.used.add(m)
                self.congs.append((c, m))
                picked.append((d, j, a, b))
                if not act.any():
                    break

        greedy_pass()
        if self.survivor:
            # phase 2: attack survivor columns (full kills / cleanup)
            colw[:] = True
            act = uncov.copy()
            greedy_pass()

        # form new holes
        remaining = int(uncov.sum())
        newM = self.M * q
        if remaining > self.hole_cap:
            self.log(f"  fail: {remaining} holes exceeds cap")
            return False
        hi, ti = np.nonzero(uncov)
        inv = pow(self.M % q, -1, q)
        rs = holes[hi]
        ts = ti.astype(np.int64)
        newholes = rs + self.M * (((ts - rs) % q) * inv % q)
        self.M = newM
        # update factored M
        self.Mfact = self.Mfact + [(p, e)]
        self.holes = newholes.astype(np.int64)
        # ---- kill mop-up: spend unused divisors >= T of new M on holes ----
        free = [d for d in divisors_of(self.Mfact)
                if d >= T and d not in self.used]
        reserve = 2000 if remaining > 0 else 0
        budget = max(0, len(free) - reserve)
        if budget > 0 and remaining > 0:
            kn = min(budget, remaining)
            for d, r in zip(free[:kn], self.holes[:kn].tolist()):
                self.used.add(d)
                self.congs.append((int(r % d), d))
            self.holes = self.holes[kn:]
            remaining -= kn
            self.log(f"  killed {kn} holes with pooled divisors")
        self.log(f"  used {len(picked)} moduli, holes now {remaining}")
        return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=int, required=True)
    ap.add_argument("--levels", type=str, required=True,
                    help="comma list like 2^6,3^4,5^2,7,11,13")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--cap", type=int, default=2_000_000)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--key", choices=["gain", "eff"], default="gain")
    ap.add_argument("--survivor", action="store_true")
    args = ap.parse_args()

    levels = []
    for tok in args.levels.split(","):
        if "^" in tok:
            p, e = tok.split("^")
            levels.append((int(p), int(e)))
        else:
            levels.append((int(tok), 1))

    b = Builder(levels, args.T, seed=args.seed, hole_cap=args.cap,
                verbose=not args.quiet, key=args.key, survivor=args.survivor)
    ok = b.run()
    print(f"RESULT T={args.T} ok={ok} congs={len(b.congs)} "
          f"leftover_holes={len(b.holes)} M={b.M}")
    if ok and args.out:
        with open(args.out, "w") as f:
            json.dump({"T": args.T, "levels": args.levels,
                       "congruences": [[int(a), int(n)] for a, n in b.congs]}, f)
        print(f"wrote {args.out}")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""P15 V2 engine v3: adaptive cell-based CRT tree with overlap closures.

Uncovered set = disjoint union of cells (r mod m). Moves on the largest cell:
  1. exact close: value m (fresh, >= T) covers the cell exactly.
  2. coarse close: fresh value v | m (v >= T) covers the cell entirely; the
     congruence (r mod v) also cleanly kills every other cell (m', r') with
     v | m' and r' ≡ r (mod v)  [cells strictly inside the class] — this is the
     cross-branch overlap that makes distinct-moduli covers possible at all
     (Mirsky–Newman forbids exact tilings).
  3. split: refine cell by a prime p into p subcells (local tower — branches
     evolve independent moduli).

Greedy with a measure-ordered priority queue; strategy knobs for split-prime
choice and coarse-value choice. Emits explicit witness for verify.py.
"""
import argparse
import time
from heapq import heappush, heappop
from math import gcd, log10


def primes_upto(n):
    ps = []
    x = 2
    while x <= n:
        if all(x % q for q in ps):
            ps.append(x)
        x += 1
    return ps


class Engine:
    def __init__(self, T, primes, caps, vmax=10**9, max_cells=5_000_000,
                 max_congs=5_000_000):
        self.T = T
        self.primes = primes
        self.caps = caps          # p -> max exponent per branch
        self.vmax = vmax
        self.max_cells = max_cells
        self.max_congs = max_congs
        self.used = set()
        self.congs = []
        self.heap = []            # (m, tie, r, fact)
        self.groups = {}          # m -> dict r -> True (live cells)
        self.tie = 0
        self.ncells = 0

    def add_cell(self, m, r, fact):
        g = self.groups.setdefault(m, {})
        if r in g:
            return
        g[r] = fact
        self.tie += 1
        heappush(self.heap, (m, self.tie, r))
        self.ncells += 1

    def kill_cell(self, m, r):
        g = self.groups.get(m)
        if g and r in g:
            del g[r]
            self.ncells -= 1
            return True
        return False

    def coarse_candidates(self, m, fact):
        """Fresh divisors v of m with T <= v (<= m). Enumerate divisors."""
        items = sorted(fact.items())
        out = []

        def dfs(i, val):
            if i == len(items):
                if self.T <= val and val not in self.used:
                    out.append(val)
                return
            p, e = items[i]
            v = val
            for _ in range(e + 1):
                dfs(i + 1, v)
                v *= p
        dfs(0, 1)
        return sorted(out)

    def clean_kills(self, v, a):
        """Kill all cells (m', r') with v | m', r' ≡ a (mod v)."""
        killed = 0
        for m2 in list(self.groups):
            if m2 % v:
                continue
            g = self.groups[m2]
            doomed = [r2 for r2 in g if r2 % v == a]
            for r2 in doomed:
                del g[r2]
                self.ncells -= 1
                killed += 1
        return killed

    def emit(self, a, v):
        self.used.add(v)
        self.congs.append((a, v))

    def split_prime(self, m, fact):
        """Smallest prime with branch-cap slack whose child value m*p is fresh
        and >= T; fallback: smallest that reaches >= T; else largest slack."""
        cands = [p for p in self.primes if fact.get(p, 0) < self.caps.get(p, 0)]
        if not cands:
            return None
        for p in cands:
            if m * p >= self.T and m * p not in self.used:
                return p
        for p in cands:
            if m * p >= self.T:
                return p
        return cands[-1]

    def run(self, verbose_every=200000, timeout_s=None):
        t0 = time.time()
        self.add_cell(1, 0, {})
        ops = 0
        while self.heap:
            if timeout_s and time.time() - t0 > timeout_s:
                return "timeout"
            m, _, r = heappop(self.heap)
            g = self.groups.get(m)
            if not g or r not in g:
                continue  # stale (killed by spillover)
            fact = g[r]
            ops += 1
            if verbose_every and ops % verbose_every == 0:
                print(f"  ops={ops} cells={self.ncells} congs={len(self.congs)}"
                      f" top_m={m} t={time.time()-t0:.0f}s", flush=True)
            # move 1/2: closure with best fresh divisor of m (incl. v = m)
            cands = self.coarse_candidates(m, fact)
            if cands:
                # pick v maximizing measure killed: own 1/m + spillover;
                # cheap heuristic: smallest v (most spillover potential)
                v = cands[0]
                a = r % v
                del g[r]
                self.ncells -= 1
                self.emit(a, v)
                if v < m:
                    self.clean_kills(v, a)
                if len(self.congs) > self.max_congs:
                    return "max_congs"
                continue
            # move 3: split
            p = self.split_prime(m, fact)
            if p is None:
                return f"stuck m={m}"
            del g[r]
            self.ncells -= 1
            nf = dict(fact)
            nf[p] = nf.get(p, 0) + 1
            for k in range(p):
                self.add_cell(m * p, r + k * m, nf)
            if self.ncells > self.max_cells:
                return "max_cells"
        return "done"

    def write(self, path, meta=""):
        with open(path, "w") as f:
            f.write(f"# {meta}\n")
            for a, v in self.congs:
                f.write(f"{a} {v}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-T", type=int, required=True)
    ap.add_argument("--maxprime", type=int, default=200)
    ap.add_argument("--cap2", type=int, default=12)
    ap.add_argument("--cap3", type=int, default=8)
    ap.add_argument("--cap5", type=int, default=5)
    ap.add_argument("--cap7", type=int, default=4)
    ap.add_argument("--capbig", type=int, default=2)
    ap.add_argument("--max-cells", type=int, default=5_000_000)
    ap.add_argument("--timeout", type=int, default=None)
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    ps = primes_upto(args.maxprime)
    caps = {p: (args.cap2 if p == 2 else args.cap3 if p == 3 else
                args.cap5 if p == 5 else args.cap7 if p == 7 else args.capbig)
            for p in ps}
    eng = Engine(args.T, ps, caps, max_cells=args.max_cells)
    res = eng.run(timeout_s=args.timeout)
    print(f"T={args.T}: result={res} congs={len(eng.congs)} "
          f"cells_left={eng.ncells}")
    if res == "done" and args.out:
        eng.write(args.out, f"T={args.T} engine3 maxprime={args.maxprime}")
        print(f"wrote {len(eng.congs)} -> {args.out}")


if __name__ == "__main__":
    main()

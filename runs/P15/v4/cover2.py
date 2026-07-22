#!/usr/bin/env python3
"""P15 V4, structured builder v2: forced-alignment greedy.

Per level p^e (q = p^e), every hole keeps a COMMON survivor chain:
slots (j, b) with b = c*p^(j-1), c in 1..p-1, j = 1..e kill the whole
subtree b mod p^j of every hole; survivor cell 0 mod q lifts to the next
level (so holes stay CRT-aligned and classes stay dense). On the final
level the survivor slot (e, 0) is killed too.

Each slot is a mandatory set cover of the current hole set by residue
classes a mod d (moduli d*p^j >= T, each numeric modulus used once).
Slot-cover greedy: maximize covered*d (density efficiency), tie by count.
Holes a slot cannot finish keep that subtree -> extra holes (tracked).

Randomization: seed shuffles equal-score choices; restarts vary.
"""
import argparse
import json
import random
import sys

import numpy as np


def crt(a, m, b, n):
    inv = pow(m % n, -1, n)
    return (a + m * ((b - a) * inv % n)) % (m * n)


def divisors_of(fact):
    divs = [1]
    for p, e in fact:
        divs = [d * p**k for d in divs for k in range(e + 1)]
    return sorted(divs)


class Builder:
    def __init__(self, levels, T, seed=0, hole_cap=5_000_000, verbose=True,
                 survivor_kill_last=True):
        self.levels = levels
        self.T = T
        self.rng = random.Random(seed)
        self.hole_cap = hole_cap
        self.verbose = verbose
        self.survivor_kill_last = survivor_kill_last
        self.used = set()
        self.congs = []
        self.M = 1
        self.Mfact = []
        self.holes = np.zeros(1, dtype=np.int64)

    def log(self, *a):
        if self.verbose:
            print(*a, flush=True)

    def slot_cover(self, p, j, b, holes):
        """Cover cell-class (b mod p^j) of every hole in `holes`.
        Returns (list of congruences committed, uncovered hole indices)."""
        pj = p**j
        divs = [d for d in divisors_of(self.Mfact)
                if d * pj >= self.T and (d * pj) not in self.used]
        alive = np.ones(len(holes), dtype=bool)
        out = []
        while alive.any():
            best = None  # (eff, count, d, a)
            hh = holes[alive]
            for d in divs:
                if (d * pj) in self.used:
                    continue
                vals, cnts = np.unique(hh % d, return_counts=True)
                k = int(cnts.argmax())
                a, c = int(vals[k]), int(cnts[k])
                eff = c * d
                key = (eff, c, self.rng.random())
                if best is None or key > best[0]:
                    best = (key, d, a)
            if best is None:
                break
            _, d, a = best
            m = d * pj
            self.used.add(m)
            cfull = crt(a % d, d, b % pj, pj)
            self.congs.append((cfull, m))
            out.append((d, a))
            idx = np.nonzero(alive)[0]
            alive[idx[(holes[idx] % d) == a]] = False
        return out, np.nonzero(alive)[0]

    def do_level(self, p, e, is_last):
        q = p**e
        holes = self.holes
        H = len(holes)
        self.log(f"LEVEL {p}^{e} M={self.M} holes={H}")
        if H == 0:
            return True
        # survivor cells per hole: dict hole_index -> list of (j, b) subtrees kept
        kept = [[] for _ in range(H)]
        slots = [(j, c * p**(j - 1)) for j in range(1, e + 1)
                 for c in range(1, p)]
        if is_last and self.survivor_kill_last:
            slots.append((e, 0))
        for (j, b) in slots:
            _, unc = self.slot_cover(p, j, b, holes)
            for i in unc:
                kept[i].append((j, b))
            self.log(f"  slot j={j} b={b}: uncovered holes {len(unc)}")
        if not (is_last and self.survivor_kill_last):
            for i in range(H):
                kept[i].append((e, 0))
        # build new holes
        newholes = []
        Mq = self.M * q
        inv = pow(self.M % q, -1, q)
        for i in range(H):
            r = int(holes[i])
            for (j, b) in kept[i]:
                pj = p**j
                # subtree b mod p^j: cells t = b + s*p^j, s in [0, q/pj)
                for s in range(q // pj):
                    t = b + s * pj
                    newholes.append(r + self.M * (((t - r) % q) * inv % q))
        if len(newholes) > self.hole_cap:
            self.log(f"  fail: {len(newholes)} holes > cap")
            return False
        self.M = Mq
        self.Mfact.append((p, e))
        self.holes = np.array(sorted(set(newholes)), dtype=np.int64) \
            if newholes else np.zeros(0, dtype=np.int64)
        self.log(f"  holes now {len(self.holes)}")
        return True

    def run(self):
        for i, (p, e) in enumerate(self.levels):
            if not self.do_level(p, e, i == len(self.levels) - 1):
                return False
            if len(self.holes) == 0:
                return True
        return len(self.holes) == 0


def parse_levels(s):
    out = []
    for tok in s.split(","):
        if "^" in tok:
            p, e = tok.split("^")
            out.append((int(p), int(e)))
        else:
            out.append((int(tok), 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", type=int, required=True)
    ap.add_argument("--levels", type=str, required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--cap", type=int, default=5_000_000)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    b = Builder(parse_levels(args.levels), args.T, seed=args.seed,
                hole_cap=args.cap, verbose=not args.quiet)
    ok = b.run()
    print(f"RESULT T={args.T} ok={ok} congs={len(b.congs)} "
          f"leftover_holes={len(b.holes)} M={b.M}")
    if ok and args.out:
        with open(args.out, "w") as f:
            json.dump({"T": args.T, "levels": args.levels,
                       "congruences": [[int(a), int(n)] for a, n in b.congs]},
                      f)
        print(f"wrote {args.out}")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()

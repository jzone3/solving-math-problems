"""Engine A: exact greedy covering-system search over a smooth universe.

Universe: Z_N with N = prod p_i^{e_i}. Usable moduli: divisors d of N with
d >= L (target minimum modulus), each usable at most once, one residue class each.
Greedy variants pick (d, r) to maximize newly covered residues.

Counting trick: uncovered.reshape(N//d, d).sum(axis=0) gives per-residue-mod-d
uncovered counts in one vectorized pass.

Outputs witness JSON {"N":..,"L":..,"congruences":[[r,d],..]} on success.
"""
import argparse
import json
import sys
import time
from functools import reduce

import numpy as np


def divisors(factors):
    divs = [1]
    for p, e in factors:
        divs = [d * p**k for d in divs for k in range(e + 1)]
    return sorted(divs)


def greedy(N, L, divs, strategy="asc", rng=None, verbose=False):
    """Returns (list of (r,d), n_uncovered_left)."""
    unc = np.ones(N, dtype=bool)
    chosen = []
    usable = [d for d in divs if d >= L and d < N + 1]
    if strategy == "asc":
        order = sorted(usable)
        for d in order:
            counts = unc.reshape(N // d, d).sum(axis=0)
            best = int(counts.max())
            if best == 0:
                continue
            cand = np.flatnonzero(counts == best)
            r = int(cand[0] if rng is None else rng.choice(cand))
            unc.reshape(N // d, d)[:, r] = False
            chosen.append((r, d))
            if not unc.any():
                break
    elif strategy == "bestfirst":
        remaining = set(usable)
        while unc.any() and remaining:
            best_gain, best_rd = 0, None
            tot = int(unc.sum())
            # prefer small moduli on ties (they're scarcer for future? actually
            # large moduli are plentiful; spend small ones only when efficient)
            for d in sorted(remaining):
                counts = unc.reshape(N // d, d).sum(axis=0)
                g = int(counts.max())
                # efficiency = fraction of the class that is new = g/(N/d)
                if g * 1.0 / (N // d) > best_gain:
                    best_gain = g * 1.0 / (N // d)
                    r = int(np.flatnonzero(counts == g)[0])
                    best_rd = (r, d)
            if best_rd is None:
                break
            r, d = best_rd
            unc.reshape(N // d, d)[:, r] = False
            remaining.discard(d)
            chosen.append((r, d))
            if verbose and len(chosen) % 25 == 0:
                print(f"  {len(chosen)} classes, uncovered {int(unc.sum())}/{N}",
                      flush=True)
    else:
        raise ValueError(strategy)
    return chosen, int(unc.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factors", required=True,
                    help="e.g. 2^5,3^3,5^2,7,11,13")
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--strategy", default="asc")
    ap.add_argument("--restarts", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    factors = []
    for tok in a.factors.split(","):
        if "^" in tok:
            p, e = tok.split("^")
            factors.append((int(p), int(e)))
        else:
            factors.append((int(tok), 1))
    N = reduce(lambda x, y: x * y, (p**e for p, e in factors))
    divs = divisors(factors)
    usable = [d for d in divs if d >= a.L]
    budget = sum(1.0 / d for d in usable)
    print(f"N={N} ({len(divs)} divisors, {len(usable)} usable >= {a.L}, "
          f"budget {budget:.3f})", flush=True)
    if budget < 1:
        print("budget < 1: provably infeasible with this universe")
        sys.exit(2)

    best = None
    for it in range(a.restarts):
        rng = np.random.default_rng(a.seed + it) if a.restarts > 1 else None
        t0 = time.time()
        chosen, left = greedy(N, a.L, divs, a.strategy, rng,
                              verbose=(it == 0))
        print(f"restart {it}: {len(chosen)} classes, uncovered {left}, "
              f"{time.time()-t0:.1f}s", flush=True)
        if best is None or left < best[1]:
            best = (chosen, left)
        if left == 0:
            break

    chosen, left = best
    if left == 0:
        print(f"SUCCESS: covering of Z_{N} with min modulus "
              f"{min(d for _, d in chosen)} using {len(chosen)} classes")
        out = a.out or f"witness_L{a.L}_N{N}.json"
        with open(out, "w") as f:
            json.dump({"N": N, "L": a.L,
                       "congruences": [[r, d] for r, d in chosen]}, f)
        print(f"wrote {out}")
    else:
        print(f"FAILED: {left} residues uncovered (density {left/N:.3e})")
        sys.exit(1)


if __name__ == "__main__":
    main()

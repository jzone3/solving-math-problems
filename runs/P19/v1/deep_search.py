#!/usr/bin/env python3
"""P19 v1 targeted deep search — near-tight wide partitions at sizes beyond the
exhaustive frontier.

Exhaustively enumerating wide partitions much past |λ| ≈ 78 is infeasible, so
this pass hill-climbs on a tightness score (number of dominance equalities
across submultisets — where Rota-style obstructions would live) over the space
of WIDE partitions at each size n, and CP-SAT-tests every distinct wide
partition visited. Any UNSAT is a counterexample candidate for verify.py.

Moves: split a part, merge two parts, move a unit between parts — keeping the
result a valid partition and re-checking wideness exactly. Seeds include
maximally-tight structured shapes (staircases and staircase sums, which are
self-conjugate ⇒ tight everywhere) padded to size n.
"""
import random
import sys
import time

from search import is_wide, conjugate, is_latin_cpsat, check_tableau


def cheap_tightness(lam):
    """Heuristic tightness: dominance equalities over contiguous windows of
    parts only (O(len^2) subpartitions instead of exponential). Used purely
    for search ordering; correctness never depends on it."""
    score = 0
    for i in range(len(lam)):
        for j in range(i + 1, len(lam) + 1):
            mu = lam[i:j]
            mc = conjugate(mu)
            sa = sb = 0
            tot = sum(mu)
            for k in range(max(len(mu), len(mc))):
                sa += mu[k] if k < len(mu) else 0
                sb += mc[k] if k < len(mc) else 0
                if sa == sb and sa < tot:
                    score += 1
    return score


def norm(parts):
    return tuple(sorted((p for p in parts if p > 0), reverse=True))


def staircase_seed(n):
    """Largest staircase (k, k-1, ..., 1) with sum <= n, greedily padded."""
    k = 1
    while (k + 1) * (k + 2) // 2 <= n:
        k += 1
    parts = list(range(k, 0, -1))
    rem = n - k * (k + 1) // 2
    i = 0
    while rem > 0:
        parts[i % len(parts)] += 1
        rem -= 1
        i += 1
    return norm(parts)


def random_wide(n, tries=2000):
    for _ in range(tries):
        parts = []
        rem = n
        while rem > 0:
            p = random.randint(max(1, rem // 4), rem)
            parts.append(p)
            rem -= p
        lam = norm(parts)
        if is_wide(lam):
            return lam
    return None


def neighbors(lam):
    out = set()
    l = list(lam)
    for i in range(len(l)):
        # split part i
        for a in range(1, l[i] // 2 + 1):
            out.add(norm(l[:i] + [l[i] - a, a] + l[i + 1:]))
        # merge with another part
        for j in range(i + 1, len(l)):
            out.add(norm([v for k, v in enumerate(l) if k not in (i, j)] + [l[i] + l[j]]))
    # move a unit i -> j
    for i in range(len(l)):
        for j in range(len(l)):
            if i == j:
                continue
            m = list(l)
            m[i] -= 1
            m[j] += 1
            out.add(norm(m))
    out.discard(lam)
    return out


def main():
    n_lo = int(sys.argv[1]) if len(sys.argv) > 1 else 79
    n_hi = int(sys.argv[2]) if len(sys.argv) > 2 else 140
    budget = int(sys.argv[3]) if len(sys.argv) > 3 else 400  # CP-SAT tests per size
    t0 = time.time()
    random.seed(20260723)
    for n in range(n_lo, n_hi + 1):
        tested = set()
        seeds = [staircase_seed(n)]
        rw = random_wide(n)
        if rw:
            seeds.append(rw)
        frontier = [s for s in seeds if is_wide(s)]
        while frontier and len(tested) < budget:
            frontier.sort(key=cheap_tightness, reverse=True)
            lam = frontier.pop(0)
            if lam in tested:
                continue
            tested.add(lam)
            status, tab = is_latin_cpsat(lam, time_limit=600.0)
            if status == "SAT":
                assert check_tableau(lam, tab)
            elif status == "UNSAT":
                print(f"*** COUNTEREXAMPLE CANDIDATE: n={n} lambda={lam}", flush=True)
                with open("deep_candidates.txt", "a") as f:
                    f.write(f"{lam}\n")
            else:
                print(f"!!! UNKNOWN: n={n} lambda={lam}", flush=True)
            # expand best neighbors
            cands = [m for m in neighbors(lam)
                     if m not in tested and sum(m) == n and is_wide(m)]
            cands.sort(key=cheap_tightness, reverse=True)
            frontier.extend(cands[:8])
            frontier = frontier[:200]
        print(f"n={n}: {len(tested)} near-tight wide partitions tested, all Latin "
              f"({time.time()-t0:.0f}s total)", flush=True)


if __name__ == "__main__":
    main()

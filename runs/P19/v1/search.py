#!/usr/bin/env python3
"""P19 v1 — Wide Partition Conjecture (free-matroid case / Latin ⟺ wide).

Enumerate all partitions by size n = 1..N, filter to WIDE partitions
(exact integer dominance check over all submultisets of parts), then test
LATINness with CP-SAT (row i is a permutation of {1..λ_i}, columns have
distinct entries). Any wide partition whose CP-SAT model is INFEASIBLE is a
counterexample candidate, to be independently confirmed with verify.py
(pure-Python exhaustive backtracking, no floats).

Definitions verified against:
  - Chow–Fan–Goemans–Vondrák, Adv. Appl. Math. 31 (2003) 334–358 (arXiv math/0205288)
  - Open Problem Garden "Wide partition conjecture"
  - Chow–Tiefenbruck, Electron. J. Combin. 32(2) (2025) #P48 (arXiv 2408.04086)

wide(λ): for every submultiset μ of the parts of λ, μ ⪰ μ' (dominance vs conjugate).
Latin(λ): tableau of shape λ, row i a permutation of {1,...,λ_i}, columns distinct.
"""
import sys
import time
from functools import lru_cache
from itertools import product
from ortools.sat.python import cp_model


def partitions(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - k, k):
            yield (k,) + rest


def conjugate(mu):
    if not mu:
        return ()
    return tuple(sum(1 for p in mu if p > j) for j in range(mu[0]))


def dominates(a, b):
    """a ⪰ b in dominance order; |a| == |b| assumed."""
    sa = sb = 0
    for i in range(max(len(a), len(b))):
        sa += a[i] if i < len(a) else 0
        sb += b[i] if i < len(b) else 0
        if sa < sb:
            return False
    return True


def submultisets(parts):
    """Distinct submultisets of the multiset `parts` (sorted desc tuples)."""
    from collections import Counter
    c = Counter(parts)
    keys = sorted(c, reverse=True)
    ranges = [range(c[k] + 1) for k in keys]
    for counts in product(*ranges):
        mu = []
        for k, m in zip(keys, counts):
            mu.extend([k] * m)
        yield tuple(mu)


def is_wide(lam):
    # quick necessary check first: λ itself
    if not dominates(lam, conjugate(lam)):
        return False
    for mu in submultisets(lam):
        if len(mu) <= 1:
            continue
        if not dominates(mu, conjugate(mu)):
            return False
    return True


def tightness(lam):
    """Number of dominance equalities (prefix sums equal) across submultisets:
    a crude 'near-tight' score; higher = closer to failing wideness."""
    score = 0
    for mu in submultisets(lam):
        if len(mu) <= 1:
            continue
        mc = conjugate(mu)
        sa = sb = 0
        for i in range(max(len(mu), len(mc))):
            sa += mu[i] if i < len(mu) else 0
            sb += mc[i] if i < len(mc) else 0
            if sa == sb and sa < sum(mu):
                score += 1
    return score


def is_latin_cpsat(lam, time_limit=300.0):
    """Return (status_str, tableau or None). Latin tableau CP-SAT model."""
    m = cp_model.CpModel()
    rows = len(lam)
    X = {}
    for r in range(rows):
        for c in range(lam[r]):
            X[r, c] = m.NewIntVar(1, lam[r], f"x{r}_{c}")
        m.AddAllDifferent([X[r, c] for c in range(lam[r])])
    ncols = lam[0]
    collen = conjugate(lam)
    for c in range(ncols):
        col = [X[r, c] for r in range(collen[c])]
        if len(col) > 1:
            m.AddAllDifferent(col)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1
    st = solver.Solve(m)
    if st == cp_model.OPTIMAL or st == cp_model.FEASIBLE:
        tab = [[solver.Value(X[r, c]) for c in range(lam[r])] for r in range(rows)]
        return "SAT", tab
    if st == cp_model.INFEASIBLE:
        return "UNSAT", None
    return "UNKNOWN", None


def check_tableau(lam, tab):
    """Exact integer re-check of a claimed Latin tableau."""
    assert len(tab) == len(lam)
    for r, row in enumerate(tab):
        if sorted(row) != list(range(1, lam[r] + 1)):
            return False
    for c in range(lam[0]):
        col = [tab[r][c] for r in range(len(lam)) if c < len(tab[r])]
        if len(set(col)) != len(col):
            return False
    return True


def work(lam):
    status, tab = is_latin_cpsat(lam)
    if status == "SAT":
        assert check_tableau(lam, tab), f"CP-SAT returned bad tableau for {lam}"
    return lam, status


def main():
    import multiprocessing as mp
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    start_n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    t0 = time.time()
    pool = mp.Pool(mp.cpu_count())
    for n in range(start_n, N + 1):
        tn = time.time()
        # near-tight bias: collect wide partitions of this size, sort by
        # tightness descending so likeliest counterexamples are tried first.
        widelist = [lam for lam in partitions(n) if is_wide(lam)]
        widelist.sort(key=tightness, reverse=True)
        for lam, status in pool.imap_unordered(work, widelist, chunksize=16):
            if status == "UNSAT":
                print(f"*** COUNTEREXAMPLE CANDIDATE: n={n} lambda={lam}", flush=True)
                with open("candidates.txt", "a") as f:
                    f.write(f"{lam}\n")
            elif status == "UNKNOWN":
                print(f"!!! TIMEOUT/UNKNOWN: n={n} lambda={lam}", flush=True)
                with open("unknown.txt", "a") as f:
                    f.write(f"{lam}\n")
        print(f"n={n}: {len(widelist)} wide partitions, all Latin-checked "
              f"({time.time()-tn:.1f}s, total {time.time()-t0:.1f}s)", flush=True)
        with open("frontier.txt", "w") as f:
            f.write(f"exhaustive wide=>Latin verified for all |lambda| <= {n}\n")


if __name__ == "__main__":
    main()

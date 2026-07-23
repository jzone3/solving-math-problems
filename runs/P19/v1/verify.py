#!/usr/bin/env python3
"""P19 independent verifier — pure Python, integers only, no external deps.

Usage:
  python3 verify.py "14,10,7,3"        # check one partition
  python3 verify.py --frontier N       # re-verify wide=>Latin for all |lambda|<=N

For a single partition λ it prints:
  WIDE/NOT-WIDE, and LATIN (with an explicit tableau, re-checked exactly)
  or NOT-LATIN (proved by exhaustive backtracking over all column-distinct
  row-permutation fillings).
A counterexample to the conjecture is confirmed iff output is
  "COUNTEREXAMPLE CONFIRMED: wide and not Latin".

All arithmetic on the accept path is exact integer arithmetic. This code is
written independently of search.py's CP-SAT model: Latinness is decided by a
depth-first search that fills the tableau cell by cell (row-major), keeping
per-row remaining-value sets and per-column used-value sets, with a simple
forward-checking prune.
"""
import sys
from itertools import product
from collections import Counter

sys.setrecursionlimit(100000)


def conjugate(mu):
    if not mu:
        return ()
    return tuple(sum(1 for p in mu if p > j) for j in range(mu[0]))


def dominates(a, b):
    sa = sb = 0
    for i in range(max(len(a), len(b))):
        sa += a[i] if i < len(a) else 0
        sb += b[i] if i < len(b) else 0
        if sa < sb:
            return False
    return True


def is_wide(lam):
    c = Counter(lam)
    keys = sorted(c, reverse=True)
    for counts in product(*[range(c[k] + 1) for k in keys]):
        mu = []
        for k, m in zip(keys, counts):
            mu.extend([k] * m)
        mu = tuple(mu)
        if len(mu) > 1 and not dominates(mu, conjugate(mu)):
            return False, mu
    return True, None


def latin_tableau(lam):
    """Return a Latin tableau (list of rows) or None if none exists.
    Exhaustive DFS with forward checking; exact, no floats."""
    rows = len(lam)
    cells = [(r, c) for r in range(rows) for c in range(lam[r])]
    tab = [[0] * lam[r] for r in range(rows)]
    col_used = [set() for _ in range(lam[0])]
    row_remaining = [set(range(1, lam[r] + 1)) for r in range(rows)]
    unfilled = set(cells)

    def dfs():
        if not unfilled:
            return True
        # MRV heuristic (exhaustive — only affects search order): pick the
        # unfilled cell with the fewest candidate values; 0 candidates prunes.
        best, best_opts = None, None
        for (r, c) in unfilled:
            opts = row_remaining[r] - col_used[c]
            if best_opts is None or len(opts) < len(best_opts):
                best, best_opts = (r, c), opts
                if not opts:
                    return False
                if len(opts) == 1:
                    break
        r, c = best
        unfilled.discard(best)
        for v in sorted(best_opts):
            tab[r][c] = v
            row_remaining[r].discard(v)
            col_used[c].add(v)
            if dfs():
                return True
            row_remaining[r].add(v)
            col_used[c].discard(v)
            tab[r][c] = 0
        unfilled.add(best)
        return False

    return tab if dfs() else None


def check_tableau(lam, tab):
    for r, row in enumerate(tab):
        if sorted(row) != list(range(1, lam[r] + 1)):
            return False
    for c in range(lam[0]):
        col = [tab[r][c] for r in range(len(lam)) if c < len(tab[r])]
        if len(set(col)) != len(col):
            return False
    return True


def verify_one(lam):
    wide, badmu = is_wide(lam)
    if wide:
        print(f"lambda={lam}: WIDE")
    else:
        print(f"lambda={lam}: NOT WIDE (violating submultiset {badmu}; "
              f"conjugate {conjugate(badmu)})")
    tab = latin_tableau(lam)
    if tab is not None:
        assert check_tableau(lam, tab), "internal error: bad tableau"
        print(f"lambda={lam}: LATIN, tableau={tab}")
    else:
        print(f"lambda={lam}: NOT LATIN (exhaustive search)")
    if wide and tab is None:
        print("COUNTEREXAMPLE CONFIRMED: wide and not Latin")
        return True
    if wide and tab is not None:
        print("PASS: wide and Latin (consistent with conjecture)")
    return False


def partitions(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - k, k):
            yield (k,) + rest


def frontier(N):
    for n in range(1, N + 1):
        cnt = 0
        for lam in partitions(n):
            wide, _ = is_wide(lam)
            if not wide:
                continue
            cnt += 1
            tab = latin_tableau(lam)
            if tab is None:
                print(f"*** COUNTEREXAMPLE: {lam}")
                return
            assert check_tableau(lam, tab)
        print(f"n={n}: {cnt} wide, all Latin — PASS", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--frontier":
        frontier(int(sys.argv[2]))
    else:
        lam = tuple(int(x) for x in sys.argv[1].replace(" ", "").split(","))
        assert all(lam[i] >= lam[i + 1] > 0 for i in range(len(lam) - 1)) and lam[-1] > 0
        verify_one(lam)

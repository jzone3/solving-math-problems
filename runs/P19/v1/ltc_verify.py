#!/usr/bin/env python3
"""Independent verifier for the Latin Tableau Conjecture reduction — pure
Python, integers only, no external deps, written independently of
ltc_search.py's CP-SAT model.

Usage:
  python3 ltc_verify.py "5,3,1"      # one shape: compute delta, decide type-delta tableau
  python3 ltc_verify.py --frontier N # re-verify LTC reduction for all |lambda| <= N

For shape λ it computes the chromatic difference sequence δ from first
principles (maximum union of r partial permutations via exhaustive corner
minimization, CT Theorem 1), then decides by exhaustive DFS whether a Latin
tableau of shape λ and type δ exists. Output "LTC COUNTEREXAMPLE CONFIRMED"
appears iff no such tableau exists (which by CT Prop. 2 refutes the LTC).
"""
import sys
from collections import Counter

sys.setrecursionlimit(100000)


def conjugate(mu):
    if not mu:
        return ()
    return tuple(sum(1 for p in mu if p > j) for j in range(mu[0]))


def alpha(lam, r):
    best = None
    for i in range(len(lam) + 1):
        tail = lam[i:]
        for j in range(lam[0] + 1):
            outside = sum(p - j for p in tail if p > j)
            v = r * (i + j) + outside
            if best is None or v < best:
                best = v
    return min(best, sum(lam))


def cds(lam):
    total = sum(lam)
    prev = 0
    delta = []
    r = 1
    while prev < total:
        a = alpha(lam, r)
        delta.append(a - prev)
        prev = a
        r += 1
    return tuple(delta)


def type_delta_tableau(lam, delta):
    """Exhaustive DFS: Latin tableau of shape λ whose color multiplicities are
    exactly delta (color k used delta[k] times). MRV cell order, plus one
    sound symmetry reduction: at any node, untouched colors (used nowhere in
    the current partial tableau) with equal multiplicity are interchangeable
    by relabeling, so only the first is branched on. A "no tableau" answer is
    therefore still an exhaustive proof."""
    rows = len(lam)
    ncol = len(delta)
    remaining = list(delta)
    tab = [[-1] * lam[r] for r in range(rows)]
    row_used = [set() for _ in range(rows)]
    col_used = [set() for _ in range(lam[0])]
    unfilled = {(r, c) for r in range(rows) for c in range(lam[r])}

    def options(r, c):
        opts = []
        seen_untouched = set()
        for k in range(ncol):
            if remaining[k] == 0 or k in row_used[r] or k in col_used[c]:
                continue
            if remaining[k] == delta[k]:
                # untouched colors with equal multiplicity are interchangeable:
                # keep only the first (existence-preserving symmetry reduction)
                if delta[k] in seen_untouched:
                    continue
                seen_untouched.add(delta[k])
            opts.append(k)
        return opts

    def dfs():
        if not unfilled:
            return True
        best, best_opts = None, None
        for cell in unfilled:
            opts = options(*cell)
            if best_opts is None or len(opts) < len(best_opts):
                best, best_opts = cell, opts
                if not opts:
                    return False
                if len(opts) == 1:
                    break
        r, c = best
        unfilled.discard(best)
        for k in best_opts:
            tab[r][c] = k
            remaining[k] -= 1
            row_used[r].add(k)
            col_used[c].add(k)
            if dfs():
                return True
            remaining[k] += 1
            row_used[r].discard(k)
            col_used[c].discard(k)
            tab[r][c] = -1
        unfilled.add(best)
        return False

    return tab if dfs() else None


def check(lam, delta, tab):
    assert [len(row) for row in tab] == list(lam)
    for row in tab:
        assert len(set(row)) == len(row)
    for c in range(lam[0]):
        col = [tab[r][c] for r in range(len(lam)) if c < len(tab[r])]
        assert len(set(col)) == len(col)
    counts = tuple(sorted(Counter(v for row in tab for v in row).values(),
                          reverse=True))
    assert counts == tuple(delta), (counts, delta)


def verify_one(lam):
    delta = cds(lam)
    print(f"lambda={lam}: delta={delta}")
    tab = type_delta_tableau(lam, delta)
    if tab is None:
        print("LTC COUNTEREXAMPLE CONFIRMED: no Latin tableau of shape "
              f"{lam} and type {delta} (exhaustive search)")
        return True
    check(lam, delta, tab)
    print(f"PASS: tableau of type delta exists: {tab}")
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
            cnt += 1
            delta = cds(lam)
            tab = type_delta_tableau(lam, delta)
            if tab is None:
                print(f"*** LTC COUNTEREXAMPLE: {lam} delta={delta}")
                return
            check(lam, delta, tab)
        print(f"n={n}: {cnt} shapes — PASS", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--frontier":
        frontier(int(sys.argv[2]))
    else:
        lam = tuple(int(x) for x in sys.argv[1].replace(" ", "").split(","))
        assert all(lam[i] >= lam[i + 1] for i in range(len(lam) - 1)) and lam[-1] > 0
        verify_one(lam)

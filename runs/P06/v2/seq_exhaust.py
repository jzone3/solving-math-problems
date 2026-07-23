"""Exhaustively verify the relaxed inequality dev(d) <= R_LP(d) for ALL degree
multisets (not just graphical ones) with n <= NMAX total vertices.

If it holds on all sequences (any n), conjecture 129 follows via the
transportation bound (see seq_search.py docstring). This scans small n
exhaustively and reports max dev - R_LP and the top near-misses.
"""
import math
import sys
from itertools import combinations_with_replacement

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def dev_minus_rlp(degs, n):
    m2 = sum(degs)
    m = m2 // 2
    S = sum(d * d for d in degs)
    var = (S + 2 * m) / n - (2 * m / n) ** 2
    dev = math.sqrt(max(var, 0.0))
    stubs = []
    for d in degs:
        stubs.extend([d] * d)
    stubs.sort()
    rlp = 0.0
    for i in range(m):
        rlp += 1.0 / math.sqrt(stubs[i] * stubs[m2 - 1 - i])
    return dev - rlp


for n in range(2, NMAX + 1):
    best, barg = -1e9, None
    cnt = 0
    eq = 0
    for degs in combinations_with_replacement(range(1, n), n):
        # trailing zeros are implicit: also consider multisets of size < n
        # handled by allowing degree-0? enumerate positive part sizes k <= n:
        pass
    for k in range(1, n + 1):
        for degs in combinations_with_replacement(range(1, n), k):
            if sum(degs) % 2:
                continue
            cnt += 1
            v = dev_minus_rlp(degs, n)
            if v > 1e-9:
                print(f"VIOLATION n={n} degs={degs} dev-R_LP={v}")
            if v > -1e-9:
                eq += 1
            if v > best:
                best, barg = v, degs
    print(f"n={n:3d}: {cnt} sequences, max dev-R_LP = {best:+.9f} at {barg}, "
          f"equality count = {eq}", flush=True)

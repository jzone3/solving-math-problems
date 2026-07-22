"""Shared helpers for P13 (perfect Mendelsohn designs), variant V5.

Semantics (matches CPro1 problem_def.py and Handbook VI.35):
A (v,k,lam)-PMD is a collection of blocks, each a cyclically ordered k-tuple of
distinct points, such that for every t in 1..k-1 every ordered pair (x,y) of
distinct points appears t-apart (y = block[(i+t) mod k] when x = block[i]) in
exactly lam blocks.
"""

INF = "inf"  # infinity point marker for difference constructions


def check_pmd(blocks, v, k, lam=1):
    """Return (ok, msg). Points must be hashable; there must be exactly v of them."""
    pts = set()
    for b in blocks:
        if len(b) != k or len(set(b)) != k:
            return False, f"bad block {b}"
        pts.update(b)
    if len(pts) != v:
        return False, f"point count {len(pts)} != v={v}"
    expected = lam * v * (v - 1) // k
    if lam * v * (v - 1) % k or len(blocks) != expected:
        return False, f"block count {len(blocks)} != {expected}"
    from collections import Counter
    cnt = Counter()
    for b in blocks:
        for t in range(1, k):
            for i in range(k):
                cnt[(t, b[i], b[(i + t) % k])] += 1
    for t in range(1, k):
        for x in pts:
            for y in pts:
                if x == y:
                    continue
                if cnt[(t, x, y)] != lam:
                    return False, f"pair ({x},{y}) t={t} occurs {cnt[(t,x,y)]} != {lam}"
    return True, "PASS"


def develop(base_blocks, m, increments=None):
    """Develop base blocks over Z_m (+ optional INF fixed points).

    increments: iterable of shifts to add (default range(m)).
    Elements that are ints get shifted mod m; non-int elements are fixed.
    """
    if increments is None:
        increments = range(m)
    out = []
    for s in increments:
        for b in base_blocks:
            out.append(tuple((x + s) % m if isinstance(x, int) else x for x in b))
    return out


def multiply(block, w, m):
    return tuple((x * w) % m if isinstance(x, int) else x for x in block)

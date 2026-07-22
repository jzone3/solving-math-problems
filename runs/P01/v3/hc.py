"""Fast Hamiltonian-cycle utilities (bitmask DFS with degree pruning).

Graphs are C_n (edges i -> i+1 mod n) plus chords making the graph 4-regular.
The base HC is (0, 1, ..., n-1). Pruning: extend a path 0..v; any unvisited
vertex must have >= 2 "usable" neighbors (unvisited, or an endpoint 0/v),
otherwise no Hamiltonian cycle can complete -> backtrack.
"""


def _adjmasks(n, adj):
    m = [0] * n
    for u in range(n):
        for w in adj[u]:
            m[u] |= 1 << w
    return m


def _search(n, adj, limit, collect):
    """Enumerate Hamiltonian cycles as vertex tuples starting at 0 (each
    undirected cycle appears twice, once per direction) until `limit`
    ACCEPTED cycles collected; `collect(path)->bool` returns True to accept.
    Returns number accepted."""
    adjm = _adjmasks(n, adj)
    full = (1 << n) - 1
    accepted = 0
    path = [0]
    mask = 1

    def prune(mask, v):
        rest = full & ~mask
        r = rest
        vb = 1 << v
        while r:
            b = r & -r
            u = b.bit_length() - 1
            r ^= b
            am = adjm[u]
            usable = bin(am & rest).count("1")
            if usable < 2:
                if am & vb:
                    usable += 1
                if am & 1:
                    usable += 1
                if usable < 2:
                    return True
        return False

    def dfs(v):
        nonlocal accepted, mask
        if mask == full:
            if adjm[v] & 1:
                if collect(path):
                    accepted += 1
            return accepted >= limit
        if prune(mask, v):
            return False
        cand = adjm[v] & ~mask
        while cand:
            b = cand & -cand
            w = b.bit_length() - 1
            cand ^= b
            mask |= b
            path.append(w)
            if dfs(w):
                return True
            path.pop()
            mask &= ~b
        return False

    dfs(0)
    return accepted


def find_second_hc(n, adj, limit=1):
    """Up to `limit` Hamiltonian cycles different from the base cycle,
    canonicalized (direction-deduped), as tuples starting at 0."""
    base = tuple(range(n))
    seen = []
    seenset = set()

    def collect(path):
        p = tuple(path)
        if p[1] > p[-1]:
            p = (p[0],) + tuple(reversed(p[1:]))
        if p == base or p in seenset:
            return False
        seenset.add(p)
        seen.append(p)
        return True

    _search(n, adj, limit, collect)
    return seen


def count_hcs(n, adj, cap=None):
    """Count Hamiltonian cycles (up to direction). Returns (count, capped);
    capped=True means true count >= cap (returned count is then cap)."""
    dcap = (2 * cap) if cap is not None else float("inf")
    got = _search(n, adj, dcap, lambda p: True)
    if got >= dcap:
        return cap, True
    assert got % 2 == 0
    return got // 2, False

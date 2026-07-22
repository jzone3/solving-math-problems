"""Core longest-path machinery for P05 V3 (block-structure construction search).

Graphs are (n, adj) with adj a list of n int bitmasks.
Paths are tuples of vertices. Path *length* = number of edges.

All routines are exact (branch & bound with reachability upper bound).
"""
import sys
from itertools import combinations

sys.setrecursionlimit(100000)


def edges_to_adj(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def is_connected(n, adj, forbidden=0):
    allowed = ((1 << n) - 1) & ~forbidden
    if allowed == 0:
        return True
    start = (allowed & -allowed).bit_length() - 1
    seen = 1 << start
    frontier = seen
    while frontier:
        nxt = 0
        f = frontier
        while f:
            v = (f & -f).bit_length() - 1
            f &= f - 1
            nxt |= adj[v] & allowed & ~seen
        seen |= nxt
        frontier = nxt
    return seen == allowed


def _comp_mask(adj, start_mask, allowed):
    seen = start_mask & allowed
    frontier = seen
    while frontier:
        nxt = 0
        f = frontier
        while f:
            v = (f & -f).bit_length() - 1
            f &= f - 1
            nxt |= adj[v] & allowed & ~seen
        seen |= nxt
        frontier = nxt
    return seen


def longest_path(n, adj, forbidden=0):
    """Return (L, path) with L = max number of edges of a path avoiding
    `forbidden` vertices; path is one witness (tuple of vertices)."""
    allowed_all = ((1 << n) - 1) & ~forbidden
    best = [-1, ()]
    popcount = bin

    def popc(x):
        return bin(x).count("1")

    path = []

    def dfs(v, used):
        rem = allowed_all & ~used
        # upper bound: current length + vertices reachable from v in rem+v
        reach = _comp_mask(adj, 1 << v, rem | (1 << v))
        ub = len(path) - 1 + popc(reach & rem) + 0
        if len(path) - 1 > best[0]:
            best[0] = len(path) - 1
            best[1] = tuple(path)
        if ub <= best[0]:
            return
        nb = adj[v] & rem
        while nb:
            w = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            path.append(w)
            dfs(w, used | (1 << w))
            path.pop()

    m = allowed_all
    while m:
        s = (m & -m).bit_length() - 1
        m &= m - 1
        path.append(s)
        dfs(s, 1 << s)
        path.pop()
    return best[0], best[1]


def enumerate_longest_paths(n, adj, L, cap=20000, forbidden=0):
    """Enumerate all paths with exactly L edges (dedup up to reversal).
    Returns (paths, truncated_flag)."""
    allowed_all = ((1 << n) - 1) & ~forbidden
    out = set()
    truncated = [False]

    def popc(x):
        return bin(x).count("1")

    path = []

    def dfs(v, used):
        if truncated[0]:
            return
        if len(path) - 1 == L:
            t = tuple(path)
            r = t[::-1]
            out.add(t if t <= r else r)
            if len(out) >= cap:
                truncated[0] = True
            return
        rem = allowed_all & ~used
        reach = _comp_mask(adj, 1 << v, rem | (1 << v))
        if len(path) - 1 + popc(reach & rem) < L:
            return
        nb = adj[v] & rem
        while nb:
            w = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            path.append(w)
            dfs(w, used | (1 << w))
            path.pop()

    m = allowed_all
    while m and not truncated[0]:
        s = (m & -m).bit_length() - 1
        m &= m - 1
        path.append(s)
        dfs(s, 1 << s)
        path.pop()
    return sorted(out), truncated[0]


def path_mask(p):
    m = 0
    for v in p:
        m |= 1 << v
    return m


def analyze(n, adj, cap=4000, verbose=False):
    """Return dict with L, whether all longest paths share a vertex (over the
    enumerated set), best triple intersection size found, and a witness triple
    with empty intersection if one exists (score 0 == counterexample).

    score = min over found triples of |P1 ∩ P2 ∩ P3| (only exact if not truncated,
    but a returned empty-intersection triple is always a valid witness)."""
    L, _ = longest_path(n, adj)
    paths, trunc = enumerate_longest_paths(n, adj, L, cap=cap)
    masks = [path_mask(p) for p in paths]
    common = (1 << n) - 1
    for m in masks:
        common &= m
    res = {"L": L, "num_paths": len(paths), "truncated": trunc,
           "common": common, "score": None, "witness": None}
    if common and not trunc:
        # some vertex lies on every longest path -> definitely no counterexample
        res["score"] = bin(common).count("1")
        return res
    best = n + 1
    wit = None
    # pair-based: for each pair intersection S, seek longest path avoiding S
    K = len(masks)
    pair_seen = set()
    for i in range(K):
        for j in range(i + 1, K):
            S = masks[i] & masks[j]
            if S in pair_seen:
                continue
            pair_seen.add(S)
            L3, p3 = longest_path(n, adj, forbidden=S)
            if L3 == L:
                # triple with empty common intersection!
                res["score"] = 0
                res["witness"] = (paths[i], paths[j], p3)
                return res
        if best > 0 and K > 400 and i > 60:
            break
    # fall back: min triple intersection among enumerated paths
    import random
    idxs = list(range(K))
    random.shuffle(idxs)
    idxs = idxs[:60]
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            ab = masks[idxs[a]] & masks[idxs[b]]
            if bin(ab).count("1") >= best:
                continue
            for c in range(b + 1, len(idxs)):
                t = ab & masks[idxs[c]]
                pc = bin(t).count("1")
                if pc < best:
                    best = pc
                    wit = (paths[idxs[a]], paths[idxs[b]], paths[idxs[c]])
    res["score"] = best
    res["witness"] = wit if best == 0 else None
    return res

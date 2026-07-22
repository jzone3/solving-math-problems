"""Core longest-path machinery for P05 V1 (hypotraceable-seed search).

Graphs are adjacency lists (list of sorted lists). Vertex sets are Python int bitmasks.
"""
import json, random, sys
from functools import lru_cache

def to_masks(adj):
    return [sum(1 << u for u in nb) for nb in adj]

def popcount(x):
    return bin(x).count('1')

def is_connected(adj):
    n = len(adj)
    if n == 0:
        return True
    masks = to_masks(adj)
    seen = 1
    frontier = 1
    while frontier:
        nxt = 0
        f = frontier
        while f:
            v = (f & -f).bit_length() - 1
            f &= f - 1
            nxt |= masks[v]
        frontier = nxt & ~seen
        seen |= nxt
    return seen == (1 << n) - 1


def reach_mask(masks, start_mask, allowed):
    """Vertices reachable from any vertex in start_mask staying inside allowed."""
    seen = start_mask & allowed
    frontier = seen
    while frontier:
        nxt = 0
        f = frontier
        while f:
            v = (f & -f).bit_length() - 1
            f &= f - 1
            nxt |= masks[v]
        frontier = nxt & allowed & ~seen
        seen |= frontier
    return seen


def longest_paths(adj, cap=200000, node_budget=None):
    """Enumerate all longest paths (by vertex count). Returns (L_vertices, list of
    (tuple(path), vertex_bitmask)). Dedupes reversals by requiring start <= end.
    cap: max number of longest paths stored (search still finds the true length).
    node_budget: optional limit on DFS node expansions; returns None if exceeded."""
    n = len(adj)
    masks = to_masks(adj)
    full = (1 << n) - 1
    best = [0]
    out = []
    budget = [node_budget if node_budget is not None else float('inf')]

    def dfs(v, used, path):
        budget[0] -= 1
        if budget[0] < 0:
            raise TimeoutError
        L = len(path)
        if L > best[0]:
            best[0] = L
            out.clear()
        if L == best[0]:
            if len(out) < cap and path[0] <= path[-1]:
                out.append((tuple(path), used))
        avail = masks[v] & ~used
        # prune: upper bound = current + reachable vertices from v in unused
        if avail:
            rm = reach_mask(masks, avail, ~used & full)
            if L + popcount(rm) < best[0]:
                return
        a = avail
        while a:
            u = (a & -a).bit_length() - 1
            a &= a - 1
            path.append(u)
            dfs(u, used | (1 << u), path)
            path.pop()

    try:
        for s in range(n):
            dfs(s, 1 << s, [s])
    except TimeoutError:
        return None
    return best[0], out


def min_triple_intersection(paths, sample_pairs=None):
    """paths: list of (path, mask). Returns (min |P1&P2&P3| over triples, witness triple or None).
    Uses masks; for each pair mask m, find path mask disjoint from m (or minimizing overlap)."""
    ms = sorted(set(m for _, m in paths))
    k = len(ms)
    best = None
    wit = None
    pairs = []
    if sample_pairs is not None and k * (k - 1) // 2 > sample_pairs:
        for _ in range(sample_pairs):
            i = random.randrange(k); j = random.randrange(k)
            if i != j:
                pairs.append((min(i, j), max(i, j)))
    else:
        pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    for i, j in pairs:
        m = ms[i] & ms[j]
        pc_m = popcount(m)
        if best is not None and pc_m >= best:
            # even best third path can't beat current best only if 0; still try to find small
            pass
        for l in range(k):
            if l == i or l == j:
                continue
            c = popcount(m & ms[l])
            if best is None or c < best:
                best = c
                wit = (ms[i], ms[j], ms[l])
                if best == 0:
                    return 0, wit
    return best, wit


def has_ham_path(adj, node_budget=5_000_000):
    n = len(adj)
    r = longest_paths(adj, cap=1, node_budget=node_budget)
    if r is None:
        return None
    return r[0] == n


def is_hypotraceable(adj):
    n = len(adj)
    if has_ham_path(adj):
        return False
    for v in range(n):
        sub = [[u - (u > v) for u in adj[w] if u != v] for w in range(n) if w != v]
        if not is_connected(sub):
            return False
        if not has_ham_path(sub):
            return False
    return True


def load_seeds(path='seeds.jsonl'):
    seeds = {}
    for line in open(path):
        d = json.loads(line)
        seeds[d['name']] = d['adj']
    return seeds

"""Dependency-light verification of the P03 fusion1 machinery.

Run with plain ``python3 solutions/P03/verify.py``.  This intentionally uses
only the standard library: the partition checker is compared with literal
color enumeration on small random DAGs, and representative n=16 cubic
orientations are reconstructed from the tracked high-girth graph6 list.
"""

import random
import sys


def closed_sets(n, arcs):
    incoming = [0] * n
    for u, v in arcs:
        incoming[v] |= 1 << u
    for mask in range(1, (1 << n) - 1):
        if all(not (incoming[v] & ~mask)
               for v in range(n) if mask & (1 << v)):
            yield mask


def cut(mask, arcs):
    return frozenset(i for i, (u, v) in enumerate(arcs)
                     if mask & (1 << u) and not (mask & (1 << v)))


def minimal_cuts(n, arcs):
    cuts = sorted(set(cut(mask, arcs) for mask in closed_sets(n, arcs)),
                  key=len)
    out = []
    for c in cuts:
        if not any(x < c for x in out):
            out.append(c)
    return out


def exact_partition(n, arcs, k):
    cuts = [tuple(c) for c in minimal_cuts(n, arcs)]
    if any(not c for c in cuts):
        return False
    arc_cuts = [[] for _ in arcs]
    for ci, c in enumerate(cuts):
        for i in c:
            arc_cuts[i].append(ci)
    order = sorted(range(len(arcs)),
                   key=lambda i: min((len(cuts[c]) for c in arc_cuts[i]),
                                     default=99))
    used = [0] * len(cuts)
    left = [len(c) for c in cuts]

    def rec(pos):
        if pos == len(order):
            return True
        i = order[pos]
        colors = range(k) if pos else (0,)
        for color in colors:
            changed = []
            good = True
            for ci in arc_cuts[i]:
                old = used[ci]
                used[ci] |= 1 << color
                left[ci] -= 1
                changed.append((ci, old))
                if k - bin(used[ci]).count("1") > left[ci]:
                    good = False
                    break
            if good and rec(pos + 1):
                return True
            for ci, old in changed:
                used[ci] = old
                left[ci] += 1
        return False

    return rec(0)


def brute_partition(n, arcs, k):
    colors = [0] * len(arcs)

    def strong_with_color(class_color):
        adj = [[] for _ in range(n)]
        for i, (u, v) in enumerate(arcs):
            adj[u].append(v)
            if colors[i] == class_color:
                adj[v].append(u)
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        if len(seen) != n:
            return False
        radj = [[] for _ in range(n)]
        for u in range(n):
            for v in adj[u]:
                radj[v].append(u)
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in radj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == n

    def rec(i):
        if i == len(arcs):
            return all(strong_with_color(c) for c in range(k))
        for c in range(k):
            colors[i] = c
            if rec(i + 1):
                return True
        return False

    return rec(0)


def graph6_edges(data):
    """Decode graph6 for the n<=62 representative inputs."""
    vals = [ord(c) - 63 for c in data.rstrip("\n")]
    n = vals[0]
    bits = []
    for value in vals[1:]:
        bits.extend((value >> shift) & 1 for shift in (5, 4, 3, 2, 1, 0))
    edges = []
    p = 0
    for i in range(n):
        for j in range(i + 1, n):
            if bits[p]:
                edges.append((i, j))
            p += 1
    return n, edges


def tau(n, arcs):
    cuts = [len(cut(mask, arcs)) for mask in closed_sets(n, arcs)]
    return min(cuts) if cuts else None


def representative_checks():
    path = "runs/P03/fusion1/higirth16.kept.jsonl"
    records = []
    with open(path) as f:
        for line in f:
            if len(records) == 2:
                break
            rec = __import__("json").loads(line)
            records.append(rec)
    for rec in records:
        n = len(rec["edges"]) * 2 // 3
        edges = [tuple(e) for e in rec["edges"]]
        arcs = [(u, v) for u, v in edges]
        assert tau(n, arcs) == 3, (n, tau(n, arcs))
        assert exact_partition(n, arcs, 3), rec["g6"]


def main():
    rng = random.Random(20240724)
    for k in (3, 4):
        checked = 0
        while checked < 80:
            n = rng.randrange(4, 7)
            possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
            rng.shuffle(possible)
            arcs = possible[:rng.randrange(1, min(9, len(possible) + 1))]
            if exact_partition(n, arcs, k) != brute_partition(n, arcs, k):
                raise AssertionError((k, n, arcs))
            checked += 1
        print(f"PASS k={k}: {checked} exact-vs-brute checks")
    representative_checks()
    print("PASS representative high-girth n=16 tau=3 packing checks")
    print("PASS")


if __name__ == "__main__":
    main()

"""Deterministic local-optimality check around known equality cases.

Equality holds for Turan graphs T(n,w) (l2=0) and for disjoint unions of two complete
bipartite graphs (l1^2+l2^2 = m, w=2). If the conjecture were false near these, some small
edge perturbation would push score > 0. We exhaust ALL single edge flips and ALL double
flips (for moderate sizes) and record the max score found.
"""
import itertools
import sys

from bn_core import evaluate

def turan(n, w):
    part = [n // w + (1 if i < n % w else 0) for i in range(w)]
    label = []
    for pi, sz in enumerate(part):
        label += [pi] * sz
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if label[i] != label[j]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return adj


def union_kab(a, b, c, d):
    n = a + b + c + d
    adj = [0] * n
    for i in range(a):
        for j in range(a, a + b):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    off = a + b
    for i in range(off, off + c):
        for j in range(off + c, off + c + d):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    return n, adj


def flip(adj, i, j):
    adj[i] ^= 1 << j
    adj[j] ^= 1 << i


def scan(name, n, adj, do_double):
    base = evaluate(n, adj)[0]
    pairs = list(itertools.combinations(range(n), 2))
    best1 = -1e18
    for i, j in pairs:
        flip(adj, i, j)
        s = evaluate(n, adj)[0]
        best1 = max(best1, s)
        flip(adj, i, j)
    best2 = None
    if do_double:
        best2 = -1e18
        for (i, j), (k, l) in itertools.combinations(pairs, 2):
            flip(adj, i, j)
            flip(adj, k, l)
            s = evaluate(n, adj)[0]
            best2 = max(best2, s)
            flip(adj, k, l)
            flip(adj, i, j)
    print(f"{name}: base={base:.3e} best-1flip={best1:.6f}"
          + (f" best-2flip={best2:.6f}" if best2 is not None else ""), flush=True)
    return best1, best2


def main():
    viol = False
    for n in [12, 15, 18, 21, 24, 30, 36, 40]:
        for w in [2, 3, 4, 5, 6, 8]:
            if w >= n:
                continue
            adj = turan(n, w)
            b1, b2 = scan(f"T({n},{w})", n, adj, do_double=(n <= 18))
            if b1 > 1e-6 or (b2 or -1) > 1e-6:
                viol = True
    for (a, b, c, d) in [(3, 4, 2, 5), (4, 4, 3, 3), (5, 5, 4, 4), (6, 7, 5, 5), (8, 8, 6, 6)]:
        n, adj = union_kab(a, b, c, d)
        b1, b2 = scan(f"K{a},{b}+K{c},{d}", n, adj, do_double=(n <= 18))
        if b1 > 1e-6 or (b2 or -1) > 1e-6:
            viol = True
    print("VIOLATION FOUND" if viol else "NO VIOLATION in any perturbation")


if __name__ == "__main__":
    main()

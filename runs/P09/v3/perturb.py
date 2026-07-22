#!/usr/bin/env python3
"""Exhaustive 1- and 2-edge-flip perturbation scan around the lambda2>0
equality family: G0 = T(n1,w) disjoint-union T(n2,w) (both balanced).

For each flip set, recompute exact clique number (bitset BB) and ratio
(lam1^2+lam2^2)/(2m(1-1/w)); record any ratio > 1 (up to tolerance) among
graphs with clique number exactly w. Prints the max ratio seen.
"""
import argparse, itertools, json
import numpy as np
from search import has_clique, adj_to_matrix, score


def clique_number(adj, n):
    full = (1 << n) - 1
    k = 1
    while has_clique(adj, full, k + 1):
        k += 1
    return k


def build(n1, n2, w):
    n = n1 + n2
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            same = (i < n1) == (j < n1)
            ii, jj = (i, j) if i < n1 else (i - n1, j - n1)
            if same and ii % w != jj % w:
                adj[i] |= 1 << j; adj[j] |= 1 << i
    return adj, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omega", type=int, required=True)
    ap.add_argument("--n1", type=int, required=True)
    ap.add_argument("--n2", type=int, required=True)
    ap.add_argument("--depth", type=int, default=2, choices=[1, 2, 3])
    args = ap.parse_args()
    w = args.omega
    adj0, n = build(args.n1, args.n2, w)
    assert clique_number(adj0, n) == w
    r0, l1, l2 = score(adj_to_matrix(adj0, n), sum(bin(a).count("1") for a in adj0) // 2, w)
    print(f"base: n={n} ratio={r0:.12f} l1={l1:.4f} l2={l2:.4f}")
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    best = (r0, None)
    flip_sets = [(p,) for p in pairs]
    if args.depth >= 2:
        flip_sets += list(itertools.combinations(pairs, 2))
    if args.depth >= 3:
        flip_sets += list(itertools.combinations(pairs, 3))
    checked = 0
    for fs in flip_sets:
        adj = list(adj0)
        for (i, j) in fs:
            adj[i] ^= 1 << j; adj[j] ^= 1 << i
        if clique_number(adj, n) != w:
            continue
        m = sum(bin(a).count("1") for a in adj) // 2
        r, _, _ = score(adj_to_matrix(adj, n), m, w)
        checked += 1
        if r > best[0]:
            best = (r, fs)
        if r > 1 + 1e-9:
            print("CANDIDATE", fs, r)
    print(f"checked {checked} omega-preserving flip sets; max ratio {best[0]:.12f} at {best[1]}")


if __name__ == "__main__":
    main()

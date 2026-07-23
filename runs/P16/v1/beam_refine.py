#!/usr/bin/env python3
"""P16: integer beam search / hill climb around near-miss quotient states."""
import heapq
import sys
import itertools

import search_quotient as sq


def neighbors(n, B):
    k = len(n)
    out = []
    # size changes
    for i in range(k):
        for d in (-2, -1, 1, 2, 5, -5):
            nn = list(n)
            nn[i] += d
            if nn[i] >= 1:
                out.append((nn, [row[:] for row in B]))
    # off-diagonal changes (keep n_i b_ij = n_j b_ji)
    for i in range(k):
        for j in range(i + 1, k):
            for d in (-1, 1, 2, -2):
                BB = [row[:] for row in B]
                BB[i][j] = B[i][j] + d
                if BB[i][j] < 0:
                    continue
                if (n[i] * BB[i][j]) % n[j]:
                    continue
                BB[j][i] = n[i] * BB[i][j] // n[j]
                out.append((list(n), BB))
    # diagonal changes
    for i in range(k):
        for d in (-2, -1, 1, 2):
            BB = [row[:] for row in B]
            BB[i][i] = B[i][i] + d
            if BB[i][i] >= 0:
                out.append((list(n), BB))
    # add a pendant cell attached to cell i (w pendants per vertex)
    if k < 6:
        for i in range(k):
            for w in (1, 2, 3):
                nn = list(n) + [n[i] * w]
                BB = [row[:] + [0] for row in B]
                BB[i][k] = w
                BB.append([0] * k + [0])
                BB[k][i] = 1
                out.append((nn, BB))
    return out


def beam(which, seeds, width=60, iters=400):
    seen = set()
    cur = []
    for (n, B) in seeds:
        v = sq.margin(which, n, B)
        if v is not None:
            cur.append((v, n, B))
    best = max(cur, default=(-1e18, None, None))
    for it in range(iters):
        cand = []
        for (v, n, B) in cur:
            for (nn, BB) in neighbors(n, B):
                key = (tuple(nn), tuple(map(tuple, BB)))
                if key in seen:
                    continue
                seen.add(key)
                vv = sq.margin(which, nn, BB)
                if vv is not None:
                    cand.append((vv, nn, BB))
        if not cand:
            break
        cand.sort(key=lambda t: -t[0])
        cur = cand[:width]
        if cur[0][0] > best[0]:
            best = cur[0]
            print(f"[{which}] it={it} best margin={best[0]:.9f} n={best[1]} B={best[2]}", flush=True)
            if best[0] > 1e-9:
                print(f"[{which}] VIOLATION CANDIDATE ^^^", flush=True)
    print(f"[{which}] BEAM DONE best={best[0]:.9f} n={best[1]} B={best[2]}")
    return best


if __name__ == "__main__":
    which = int(sys.argv[1])
    seeds = [
        ([14, 14, 12], [[0, 1, 12], [1, 0, 0], [14, 0, 0]]),
        ([20, 20, 1], [[0, 20, 1], [20, 0, 0], [20, 0, 0]]),
        ([10, 10], [[0, 10], [10, 0]]),
        ([12, 12, 12], [[0, 6, 6], [6, 0, 6], [6, 6, 0]]),
        ([6, 6, 6, 6], [[0, 3, 0, 3], [3, 0, 3, 0], [0, 3, 0, 3], [3, 0, 3, 0]]),
    ]
    beam(which, seeds)

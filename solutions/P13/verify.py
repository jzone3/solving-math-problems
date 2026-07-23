#!/usr/bin/env python3
"""Standalone verifier for a (v,k,1)-perfect Mendelsohn design witness.

Input: text file, one block per line, k space-separated point labels
(integers). v is inferred from the set of labels; k from row width.
Checks: b = v(v-1)/k blocks, points distinct within a block, and for every
t = 1..k-1 every ordered pair of distinct points is t-apart in EXACTLY one
block (pair x,y t-apart in block B iff B[(p+t) mod k] = y where B[p] = x).
Prints PASS or FAIL with a reason. No dependencies beyond stdlib.

Usage: verify.py witness.txt
"""
import sys
from collections import Counter


def main(path):
    blocks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            blocks.append([int(z) for z in line.split()])
    if not blocks:
        return fail("no blocks")
    k = len(blocks[0])
    if any(len(b) != k for b in blocks):
        return fail("ragged block sizes")
    pts = sorted({p for b in blocks for p in b})
    v = len(pts)
    if pts != list(range(v)):
        return fail("labels are not 0..v-1")
    if len(blocks) * k != v * (v - 1):
        return fail(f"block count {len(blocks)} != v(v-1)/k = {v*(v-1)//k}")
    for b in blocks:
        if len(set(b)) != k:
            return fail(f"repeated point in block {b}")
    for t in range(1, k):
        cnt = Counter()
        for b in blocks:
            for p in range(k):
                cnt[(b[p], b[(p + t) % k])] += 1
        for x in range(v):
            for y in range(v):
                if x == y:
                    continue
                if cnt[(x, y)] != 1:
                    return fail(f"pair ({x},{y}) at distance {t} covered {cnt[(x,y)]} times")
    print(f"PASS: valid ({v},{k},1)-PMD with {len(blocks)} blocks")
    return 0


def fail(msg):
    print("FAIL:", msg)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

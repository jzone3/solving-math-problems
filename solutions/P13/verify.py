#!/usr/bin/env python3
"""Standalone verifier for (v,k,1)-perfect Mendelsohn designs.

Usage: python3 verify.py <blocksfile> [k]
  blocksfile: one block per line, k space-separated point labels (integers).
  k defaults to the length of the first line.

Checks:
  - all blocks have k distinct points; points form {0..v-1} (v inferred);
  - number of blocks == v(v-1)/k;
  - for every t in 1..k-1, every ordered pair of distinct points appears
    t-apart (block[i], block[(i+t) % k]) in EXACTLY one block.
Prints PASS or FAIL with a reason. No dependencies.
"""
import sys
from collections import Counter

def main():
    blocks = []
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            blocks.append([int(t) for t in line.split()])
    if not blocks:
        print('FAIL: no blocks')
        return 1
    k = int(sys.argv[2]) if len(sys.argv) > 2 else len(blocks[0])
    pts = set()
    for bl in blocks:
        if len(bl) != k or len(set(bl)) != k:
            print('FAIL: block not %d distinct points: %s' % (k, bl))
            return 1
        pts.update(bl)
    v = len(pts)
    if pts != set(range(v)):
        print('FAIL: points are not 0..v-1')
        return 1
    if v * (v - 1) % k != 0 or len(blocks) != v * (v - 1) // k:
        print('FAIL: expected %s blocks, got %d' % (v * (v - 1) / k, len(blocks)))
        return 1
    for t in range(1, k):
        cnt = Counter()
        for bl in blocks:
            for i in range(k):
                cnt[(bl[i], bl[(i + t) % k])] += 1
        for x in range(v):
            for y in range(v):
                if x == y:
                    continue
                if cnt[(x, y)] != 1:
                    print('FAIL: pair (%d,%d) at distance %d appears %d times'
                          % (x, y, t, cnt[(x, y)]))
                    return 1
    print('PASS: valid (%d,%d,1)-PMD with %d blocks' % (v, k, len(blocks)))
    return 0

if __name__ == '__main__':
    sys.exit(main())

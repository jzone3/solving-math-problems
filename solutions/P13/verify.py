#!/usr/bin/env python3
"""Independent verifier for (v,k)-PMD witnesses.

A (v,k)-PMD: b = v(v-1)/k blocks, each a k-tuple of distinct points from
{0..v-1}, such that for every distance i in 1..k-1, every ordered pair (x,y)
of distinct points appears at cyclic distance i (y = k-tuple element i steps
cyclically after x) in exactly one block.

Usage: verify.py v k <witness-file>
Witness file: b lines of k whitespace-separated integers. Lines that don't
start with a digit are ignored. Prints PASS or FAIL.
"""
import sys

def main():
    v, k = int(sys.argv[1]), int(sys.argv[2])
    blocks = []
    for line in open(sys.argv[3]):
        parts = line.split()
        if not parts or not parts[0].lstrip('-').isdigit():
            continue
        blocks.append([int(x) for x in parts])
    b = v * (v - 1) // k
    if v * (v - 1) % k != 0:
        print("FAIL: k does not divide v(v-1)"); sys.exit(1)
    if len(blocks) != b:
        print(f"FAIL: expected {b} blocks, got {len(blocks)}"); sys.exit(1)
    for r in blocks:
        if len(r) != k:
            print("FAIL: bad block length", r); sys.exit(1)
        if any(x < 0 or x >= v for x in r):
            print("FAIL: element out of range", r); sys.exit(1)
        if len(set(r)) != k:
            print("FAIL: repeated element in block", r); sys.exit(1)
    seen = set()
    for r in blocks:
        for d in range(1, k):
            for i in range(k):
                key = (d, r[i], r[(i + d) % k])
                if key in seen:
                    print("FAIL: duplicate coverage", key); sys.exit(1)
                seen.add(key)
    if len(seen) != (k - 1) * v * (v - 1):
        print("FAIL: coverage incomplete"); sys.exit(1)
    print("PASS")

if __name__ == "__main__":
    main()

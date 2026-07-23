#!/usr/bin/env python3
"""Standalone verifier for P13 (perfect Mendelsohn designs, block size k).

Verifies a claimed (v,k)-PMD witness: a b x k array (b = v(v-1)/k) of blocks,
each a cyclically ordered k-tuple of distinct points from {0..v-1}, such that
for every t = 1..k-1 every ordered pair (x,y) of distinct points is t-apart
in exactly one block (x at position i, y at position (i+t) mod k).

Usage: verify.py <witness-file>
  Witness file format: first line "v k", then b lines of k space-separated ints.
Prints PASS or FAIL with a reason.  No dependencies beyond the stdlib.

NOTE on the (9,6) result: the V4 run's main result is NONEXISTENCE of a
(9,6)-PMD, established by two independently written exhaustive searches
(runs/P13/v4/pmd6_search.c and runs/P13/v4/pmd6_crosscheck.py).  Nonexistence
has no finite witness for this script; this verifier is provided for any
positive witnesses (e.g. sanity-check designs found for known-existing v).
"""
import sys


def verify(v, k, blocks, packing=False):
    b_expected = v * (v - 1) // k
    if v * (v - 1) % k != 0:
        return False, f"v(v-1)={v*(v-1)} not divisible by k={k}"
    if not packing and len(blocks) != b_expected:
        return False, f"expected b={b_expected} blocks, got {len(blocks)}"
    seen = set()
    for r, blk in enumerate(blocks):
        if len(blk) != k:
            return False, f"block {r} has length {len(blk)} != k={k}"
        if any(x < 0 or x >= v for x in blk):
            return False, f"block {r} has out-of-range element"
        if len(set(blk)) != k:
            return False, f"block {r} has repeated element"
        for t in range(1, k):
            for i in range(k):
                trip = (t, blk[i], blk[(i + t) % k])
                if trip in seen:
                    return False, f"pair {trip[1:]} covered twice at distance {t}"
                seen.add(trip)
    if packing:
        return True, (f"valid partial packing of {len(blocks)} blocks "
                      f"(perfect design would need {b_expected}); no slot covered twice")
    if len(seen) != (k - 1) * v * (v - 1):
        return False, "coverage count mismatch"
    return True, "all (k-1)*v*(v-1) ordered-pair/distance slots covered exactly once"


def main():
    args = [a for a in sys.argv[1:] if a != "--packing"]
    packing = "--packing" in sys.argv[1:]
    if len(args) != 1:
        print("usage: verify.py [--packing] <witness-file>")
        sys.exit(2)
    with open(args[0]) as f:
        toks = f.read().split()
    v, k = int(toks[0]), int(toks[1])
    rest = list(map(int, toks[2:]))
    if len(rest) % k != 0:
        print("FAIL: witness body not a multiple of k")
        sys.exit(1)
    blocks = [rest[i:i + k] for i in range(0, len(rest), k)]
    ok, msg = verify(v, k, blocks, packing=packing)
    print(("PASS" if ok else "FAIL") + ": " + msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

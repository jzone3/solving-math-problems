#!/usr/bin/env python3
"""Standalone verifier for ternary covering codes of length 6, radius 1.

Usage: python3 verify.py CODEFILE
CODEFILE: one codeword per line, 6 characters from {0,1,2}.
Prints PASS if every word of {0,1,2}^6 is within Hamming distance 1 of some
codeword, plus the code size. No dependencies beyond the standard library.
"""
import itertools
import sys

def main():
    words = [line.strip() for line in open(sys.argv[1]) if line.strip()]
    for w in words:
        assert len(w) == 6 and all(c in "012" for c in w), f"bad codeword: {w!r}"
    code = [tuple(int(c) for c in w) for w in words]
    uncovered = 0
    for x in itertools.product(range(3), repeat=6):
        if not any(sum(a != b for a, b in zip(x, c)) <= 1 for c in code):
            uncovered += 1
    print(f"code size = {len(code)} (distinct: {len(set(code))})")
    if uncovered == 0:
        print("PASS: every word of {0,1,2}^6 is covered within Hamming distance 1")
    else:
        print(f"FAIL: {uncovered} uncovered words")
        sys.exit(1)

if __name__ == "__main__":
    main()

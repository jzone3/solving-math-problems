#!/usr/bin/env python3
"""Standalone verifier for a circulant weighing matrix witness CW(n,k).

Input: a string over {+,-,0} of length n (first row of the circulant matrix),
and k. Checks weight == k and all nontrivial periodic autocorrelations == 0,
i.e. W W^T = k I for the circulant W. Pure Python, no deps.

Usage: verify.py <k> <vector-string>
"""
import sys

def verify(k, vec):
    n = len(vec)
    a = []
    for c in vec:
        if c == '+': a.append(1)
        elif c == '-': a.append(-1)
        elif c == '0': a.append(0)
        else: raise ValueError(f"bad char {c!r}")
    w = sum(x*x for x in a)
    if w != k:
        return False, f"weight {w} != k {k}"
    for t in range(1, n):
        r = sum(a[i]*a[(i+t) % n] for i in range(n))
        if r != 0:
            return False, f"autocorrelation at shift {t} is {r}"
    return True, f"CW({n},{k}) witness valid"

if __name__ == "__main__":
    k = int(sys.argv[1]); vec = sys.argv[2]
    ok, msg = verify(k, vec)
    print(("PASS: " if ok else "FAIL: ") + msg)
    sys.exit(0 if ok else 1)

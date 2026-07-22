#!/usr/bin/env python3
"""Independent verifier for circulant weighing matrix witnesses CW(n, k).

A witness is a ternary first-row vector a[0..n-1] in {0, +1, -1}, given as two
disjoint index sets P (positions of +1) and N (positions of -1) in Z_n.
It is a valid CW(n, k) first row iff
  * |P| + |N| = k, and
  * all nontrivial periodic autocorrelations vanish:
      sum_i a[i] * a[(i+t) mod n] == 0  for t = 1..n-1.

The La Jolla CWM repository statuses refer to PROPER CWMs: ones not obtained
from a CW(m, k) with m | n, m < n by the padding map x -> x^{n/m} (up to cyclic
shift). A first row is improper iff some cyclic shift of it has its support
contained in a proper subgroup dZ_n; we check properness too.

Usage:
  python3 verify.py witness.json
where witness.json = {"n": n, "k": k, "P": [...], "N": [...]}
or import and call check(n, k, P, N).

No dependencies beyond the standard library.
"""
import json
import sys


def is_proper(n, P, N):
    supp = set(P) | set(N)
    for d in range(2, n + 1):
        if n % d:
            continue
        # improper iff supp lies in one coset a + dZ_n of the subgroup dZ_n,
        # i.e. all support elements share the same residue mod d
        if len({x % d for x in supp}) == 1:
            return False
    return True


def check(n, k, P, N, proper=True):
    P, N = list(P), list(N)
    assert all(0 <= x < n for x in P + N), "index out of range"
    assert len(set(P)) == len(P) and len(set(N)) == len(N), "duplicate indices"
    assert not (set(P) & set(N)), "P and N overlap"
    assert len(P) + len(N) == k, f"weight {len(P)+len(N)} != k={k}"
    a = [0] * n
    for x in P:
        a[x] = 1
    for x in N:
        a[x] = -1
    for t in range(1, n):
        c = sum(a[i] * a[(i + t) % n] for i in range(n))
        assert c == 0, f"autocorrelation at shift {t} is {c}, not 0"
    if proper:
        assert is_proper(n, P, N), "witness is IMPROPER (padded from a divisor)"
    return True


if __name__ == "__main__":
    w = json.load(open(sys.argv[1]))
    proper = w.get("proper", True)
    check(w["n"], w["k"], w["P"], w["N"], proper=proper)
    print("PASS" if proper else "PASS (valid CWM but IMPROPER; does not settle the repo cell)")

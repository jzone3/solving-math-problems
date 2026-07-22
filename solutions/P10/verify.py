#!/usr/bin/env python3
"""Independent verifier for P10 (Brouwer's conjecture) witnesses.

A witness is a JSON file: {"n": int, "t": int, "edges": [[u,v], ...]} claiming
sum of the t largest Laplacian eigenvalues > m + t(t+1)/2.

Checks the claim with high-precision arithmetic (mpmath, 60 digits) built from
first principles (no numpy eigensolver trusted for the final verdict).
Prints PASS if the witness violates Brouwer's bound, FAIL otherwise.

Usage: verify.py witness.json
"""
import sys, json
from mpmath import mp, mpf, matrix, eigsy

mp.dps = 60

def main():
    w = json.load(open(sys.argv[1]))
    n, t, edges = w["n"], w["t"], w["edges"]
    assert 1 <= t <= n
    es = set()
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n and u != v
        es.add((min(u, v), max(u, v)))
    assert len(es) == len(edges), "duplicate edges"
    m = len(es)
    L = matrix(n, n)
    for u, v in es:
        L[u, u] += 1; L[v, v] += 1
        L[u, v] -= 1; L[v, u] -= 1
    mu = sorted(eigsy(L, eigvals_only=True), reverse=True)
    s = sum(mu[:t])
    bound = mpf(m) + mpf(t * (t + 1)) / 2
    print(f"n={n} m={m} t={t}")
    print(f"sum_top_t = {mp.nstr(s, 30)}")
    print(f"bound     = {mp.nstr(bound, 30)}")
    print(f"excess    = {mp.nstr(s - bound, 30)}")
    if s - bound > mpf(10) ** -20:
        print("PASS: witness violates Brouwer's bound (conjecture false)")
    else:
        print("FAIL: witness does NOT violate Brouwer's bound")

if __name__ == "__main__":
    main()

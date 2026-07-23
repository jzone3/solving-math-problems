#!/usr/bin/env python3
"""Exact verifier for P17 (WoW 20 / 21). NO FLOATS on the accept path.

WoW 20: n+(G) <= sum of positive adjacency eigenvalues
WoW 21: n-(G) <= sum of positive adjacency eigenvalues

Given a graph (graph6 string or edge list), computes the characteristic
polynomial over ZZ, isolates all real roots with rational isolating intervals
(sympy dup_isolate_real_roots, pure rational arithmetic), counts n+/n- with
multiplicity, and brackets sum_{lambda>0} lambda in a rational interval refined
until it separates from the integer comparands (or until eps floor, in which
case it reports TIGHT and attempts an exact rational-spectrum decision).

Usage:
  python3 verify.py --g6 'F~~~w'
  python3 verify.py --edges '0-1,1-2,...'
Exit code 0, prints PASS/VIOLATION/TIGHT verdicts for both conjectures.
"""
import sys
import argparse
from fractions import Fraction

from sympy import Matrix, Poly, Symbol, QQ, ZZ, Rational, Integer
from sympy.polys.rootisolation import dup_isolate_real_roots
from sympy.polys.densetools import dup_clear_denoms


def g6_to_edges(s):
    data = [ord(c) - 63 for c in s.strip()]
    assert all(0 <= d < 64 for d in data), "invalid graph6"
    if data[0] == 63:
        raise NotImplementedError("large n")
    n = data[0]
    bits = []
    for d in data[1:]:
        bits.extend((d >> k) & 1 for k in range(5, -1, -1))
    edges, idx = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def charpoly_coeffs(n, edges):
    A = [[0] * n for _ in range(n)]
    for u, v in edges:
        A[u][v] = A[v][u] = 1
    M = Matrix(A)
    x = Symbol('x')
    p = M.charpoly(x)
    return Poly(p.as_expr(), x, domain=ZZ)


def analyze(n, edges):
    p = charpoly_coeffs(n, edges)
    x = p.gen
    # strip zero roots exactly
    coeffs = p.all_coeffs()
    nz = 0
    while coeffs[-1] == 0:
        coeffs = coeffs[:-1]
        nz += 1
    q = [QQ(int(c)) for c in coeffs]  # dense, descending -> dup wants descending too
    deg = len(q) - 1
    assert deg + nz == n
    eps = QQ(1, 10**6)
    while True:
        roots = dup_isolate_real_roots(q, QQ, eps=eps)
        # roots: list of ((a, b), multiplicity) with a<=root<=b, rational
        total_mult = sum(m for (_, _m) in [(r, 0) for r in roots] for m in [_m]) if False else sum(m for (_iv, m) in roots)
        assert total_mult == deg, f"nonreal roots?! {total_mult} != {deg}"
        if any(a < 0 < b or a == 0 or b == 0 for ((a, b), m) in roots):
            eps = eps / 10**3
            continue
        npos = sum(m for ((a, b), m) in roots if a > 0)
        nneg = sum(m for ((a, b), m) in roots if b < 0)
        lo = sum(a * m for ((a, b), m) in roots if a > 0)
        hi = sum(b * m for ((a, b), m) in roots if a > 0)
        # decide both conjectures
        res = {}
        undecided = False
        for name, target in (("WoW20", npos), ("WoW21", nneg)):
            if lo >= target:
                res[name] = ("PASS", f"sumpos in [{lo},{hi}] >= {target}")
            elif hi < target:
                res[name] = ("VIOLATION", f"sumpos in [{lo},{hi}] < {target}")
            else:
                undecided = True
        if not undecided:
            return npos, nneg, (lo, hi), res
        # possible equality: try exact rational spectrum
        pr = Poly([int(c) for c in coeffs], x, domain=ZZ)
        rr = pr.rat_roots() if hasattr(pr, 'rat_roots') else []
        facs = pr.factor_list()[1]
        if all(f.degree() == 1 for f, m in facs):
            sumpos_exact = sum(Rational(-f.all_coeffs()[1], f.all_coeffs()[0]) * m
                               for f, m in facs
                               if Rational(-f.all_coeffs()[1], f.all_coeffs()[0]) > 0)
            res = {}
            for name, target in (("WoW20", npos), ("WoW21", nneg)):
                if sumpos_exact > target:
                    res[name] = ("PASS", f"exact sumpos {sumpos_exact} > {target}")
                elif sumpos_exact == target:
                    res[name] = ("PASS-EQUALITY", f"exact sumpos {sumpos_exact} == {target}")
                else:
                    res[name] = ("VIOLATION", f"exact sumpos {sumpos_exact} < {target}")
            return npos, nneg, (sumpos_exact, sumpos_exact), res
        if eps < QQ(1, 10**60):
            res = {}
            for name, target in (("WoW20", npos), ("WoW21", nneg)):
                if lo >= target:
                    res[name] = ("PASS", f"sumpos in [{lo},{hi}] >= {target}")
                elif hi < target:
                    res[name] = ("VIOLATION", f"sumpos in [{lo},{hi}] < {target}")
                else:
                    res[name] = ("TIGHT-UNDECIDED", f"sumpos in [{lo},{hi}], target {target}")
            return npos, nneg, (lo, hi), res
        eps = eps / 10**6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--g6')
    ap.add_argument('--edges')
    ap.add_argument('--n', type=int)
    a = ap.parse_args()
    if a.g6:
        n, edges = g6_to_edges(a.g6)
    else:
        edges = [tuple(map(int, e.split('-'))) for e in a.edges.split(',')]
        n = a.n or (max(max(e) for e in edges) + 1)
    npos, nneg, (lo, hi), res = analyze(n, edges)
    print(f"n={n} m={len(edges)} n+={npos} n-={nneg} sumpos in [{lo}, {hi}]")
    ok = True
    for name in ("WoW20", "WoW21"):
        v, why = res[name]
        print(f"{name}: {v}  ({why})")
        if v.startswith("VIOLATION"):
            ok = False
    print("OVERALL:", "PASS (no violation)" if ok else "COUNTEREXAMPLE FOUND")


if __name__ == '__main__':
    main()

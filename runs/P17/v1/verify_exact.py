#!/usr/bin/env python3
"""Exact verifier for a claimed WoW 20/21 counterexample (P17).

Usage: python3 verify_exact.py <20|21> <edges-json-file>
  edges-json-file: JSON {"n": int, "edges": [[i,j],...]}

Checks with NO floats on the accept path:
  - characteristic polynomial of adjacency matrix over ZZ (sympy, Bareiss)
  - n+ / n- via exact Sturm root counting (sympy count_roots on (0,oo)/(-oo,0))
  - sum of positive roots enclosed in rational interval via
    RootOf.eval_rational (certified rational isolation), refined until the
    comparison against the integer count is decided.
Prints PASS if the graph violates the stated conjecture, FAIL otherwise.
"""
import sys, json
import sympy as sp
from fractions import Fraction

def check(n, edges, which):
    A = sp.zeros(n, n)
    for i, j in edges:
        assert 0 <= i < n and 0 <= j < n and i != j
        A[i, j] = A[j, i] = 1
    x = sp.Symbol('x')
    p = A.charpoly(x)                      # exact over ZZ
    poly = sp.Poly(p.as_expr(), x)
    # exact Sturm counts, WITH multiplicity via square-free decomposition
    npos = nneg = 0
    for fac, mult in poly.factor_list()[1]:
        fp = sp.Poly(fac, x)
        npos += mult * fp.count_roots(0, sp.oo)
        nneg += mult * fp.count_roots(-sp.oo, 0)
    # exact enclosure of sum of positive roots via rational root isolation
    target = npos if which == 20 else nneg
    for prec_exp in range(6, 60, 6):
        dx = sp.Rational(1, 10 ** prec_exp)
        lo = sp.Integer(0); hi = sp.Integer(0)
        cnt = 0; straddle = False
        for (a, b), mult in poly.intervals(eps=dx, sqf=False):
            if b <= 0:
                continue
            if a <= 0 < b and not (a == b == 0):
                if poly.count_roots(a, b) and poly.count_roots(0, b):
                    if a < 0:      # ambiguous: refine at next precision
                        straddle = True
                        break
            if a == b == 0:
                continue
            lo += mult * a; hi += mult * b; cnt += mult
        if straddle:
            continue
        assert cnt == npos, (cnt, npos)
        # violation iff target > sum_pos: certified if hi < target
        if hi < target:
            return True, (npos, nneg, sp.nsimplify(lo), sp.nsimplify(hi))
        if lo > target or lo == target == hi:
            return False, (npos, nneg, lo, hi)
        if lo >= target and hi > target:
            continue
        if hi <= target and lo < target:
            # sum could equal target (equality case) -> not a violation unless strict
            # decide exactly: check whether sum of positive roots == target via
            # symmetric-function test: compare after further refinement; if the
            # enclosure keeps straddling, fall through to tighter dx.
            continue
    return None, "undecided at max precision"

if __name__ == '__main__':
    which = int(sys.argv[1]); assert which in (20, 21)
    d = json.load(open(sys.argv[2]))
    ok, info = check(d["n"], [tuple(e) for e in d["edges"]], which)
    print(f"n+={info[0]} n-={info[1]} sum_pos in [{info[2]}, {info[3]}]" if ok is not None else info)
    if ok:
        print(f"PASS: graph violates WoW {which} "
              f"({'n+' if which==20 else 'n-'} > sum of positive eigenvalues)")
    else:
        print(f"FAIL: no violation of WoW {which}")
        sys.exit(1)

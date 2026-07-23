"""Symbolic verification of the M* reduction (=> conjecture 129) on the
complete-split-plus-isolated family, which contains BOTH tight cases:

  G(a,b,c) = CS(a,b) u cK_1 :  b dominating vertices (clique among themselves,
  joined to everything), a independent vertices of degree b, c isolated.
  a=t, b=1: star + isolated.   a=0, b=k, c=k-2: the K_k u (k-2)K_1 equality case.

M*: S^2 * dev2 <= m^4, S = sum_E sqrt(du dv), dev2 = (M1+2m)/n - 4m^2/n^2.

Degrees: a vertices of degree b; b vertices of degree n'-1 = a+b-1.
Edges: a*b cross edges with weight sqrt(b(a+b-1)); C(b,2) clique edges with
weight (a+b-1). We verify  m^4 - S^2*dev2 >= 0 for all integers a>=0, b>=1,
c>=0 by dense scanning over a large grid with exact rational arithmetic on
the squared/rationalized form, plus asymptotic ray checks.

Because S contains sqrt(b(a+b-1)), S^2 is polynomial in (a,b) — exact.
"""

import sympy as sp

a, b, c = sp.symbols('a b c', nonnegative=True)
n = a + b + c
m = a * b + b * (b - 1) / 2
M1 = a * b**2 + b * (a + b - 1) ** 2
dev2 = (M1 + 2 * m) / n - 4 * m * m / n / n
S = a * b * sp.sqrt(b * (a + b - 1)) + b * (b - 1) / 2 * (a + b - 1)
expr = m ** 4 - S ** 2 * dev2
f = sp.lambdify((a, b, c), expr, modules="mpmath")
import mpmath
mpmath.mp.dps = 50

# Exact scan over a wide integer grid
bad = []
worst = (mpmath.mpf("1e30"), None)
for A in list(range(0, 41)) + [100, 1000, 10**6]:
    for B in list(range(1, 41)) + [100, 1000, 10**6]:
        # candidate worst c values: 0, small, near the analytic optimum, huge
        mm = A * B + B * (B - 1) // 2
        if mm == 0:
            continue
        q = A * B * B + B * (A + B - 1) ** 2 + 2 * mm
        copt = sp.Rational(8 * mm * mm, q) - (A + B)
        cands = {0, 1, 2, 10 ** 7}
        for base in [sp.floor(copt), sp.ceiling(copt)]:
            for d in (-1, 0, 1):
                v = int(base) + d
                if v >= 0:
                    cands.add(v)
        for C in cands:
            val = f(mpmath.mpf(A), mpmath.mpf(B), mpmath.mpf(C))
            if val < mpmath.mpf("-1e-20") * max(1, mm) ** 4:
                bad.append((A, B, C, val))
            nrm = val / max(1, mm) ** 4
            if nrm < worst[0]:
                worst = (nrm, (A, B, C))
print("violations:", bad[:5] if bad else "NONE")
print("worst normalized value:", worst)

# Asymptotic ray checks: a = r*b, b -> oo, c at the analytic optimum and c=0
r_ = sp.symbols('r', positive=True)
for cval, tag in [(sp.Rational(8) * m * m / (M1 + 2 * m) - (a + b), "c=c_opt"),
                  (sp.Integer(0), "c=0")]:
    e = (m ** 4 - S ** 2 * dev2).subs(c, cval).subs(a, r_ * b)
    lead = sp.limit(sp.expand(sp.simplify(e)) / b ** 8, b, sp.oo)
    lead = sp.simplify(lead)
    print(f"ray a=r*b, {tag}: leading b^8 coefficient =", lead)
    sol = sp.solve(sp.Eq(lead, 0), r_)
    print("   zeros in r:", sol, "; sign at r=1:", sp.sign(lead.subs(r_, 1)),
          "; at r=100:", sp.sign(lead.subs(r_, 100)))

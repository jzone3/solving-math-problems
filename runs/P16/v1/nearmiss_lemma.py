#!/usr/bin/env python3
"""P16: exact symbolic LEMMA — the persistent near-miss family never violates.

Family F_a (a >= 1): G_a = K_{a,a} + one extra vertex w joined to every vertex
of one side. Equitable partition (A, B, {w}), sizes (a, a, 1), quotient
    B = [[0, a, 1], [a, 0, 0], [a, 0, 0]],
profiles (d_A, d_B, d_w) = (a+1, a, a), (m_A, m_B, m_w) = (a, a+1, a+1);
every edge has profile ((a+1, a), (a, a+1)) so each bound's RHS is one value.

Verified exactly below (sympy, no floats):
 1. charpoly of L_B is x (x^2 - (3a+1)x + a(2a+1)), whose largest root is
    exactly mu = 2a+1  (discriminant collapses: (3a+1)^2 - 4a(2a+1) = (a+1)^2).
    Since the partition is equitable, mu(G_a) >= 2a+1; and Anderson-Morley
    gives mu(G_a) <= max(d_u + d_v) = (a+1) + a = 2a+1. So mu(G_a) = 2a+1.
 2. Bound 44: inner44 = 2(a^2 + (a-1)^2) = (2a-1)^2 + 1 > (2a-1)^2,
    so f44 = 2 + sqrt(inner44) > 2a+1 = mu. STRICT for every a; margin -> 0-.
 3. Bound 46: inner46 - (2a-1)^2 = (2a+5)/(2a+1) > 0, so f46 > 2a+1 = mu.
Hence family F_a never violates either bound, for ALL a."""
import sympy as sp

a, x = sp.symbols("a x", positive=True)

B = sp.Matrix([[0, a, 1], [a, 0, 0], [a, 0, 0]])
s = sp.Matrix([a + 1, a, a])
LB = sp.diag(*s) - B
q = sp.expand((x * sp.eye(3) - LB).det())
assert sp.expand(q - x * (x ** 2 - (3 * a + 1) * x + a * (2 * a + 1))) == 0
# discriminant of the quadratic factor is a perfect square:
disc = sp.expand((3 * a + 1) ** 2 - 4 * a * (2 * a + 1))
assert sp.expand(disc - (a + 1) ** 2) == 0
mu = sp.simplify(((3 * a + 1) + (a + 1)) / 2)
assert sp.expand(mu - (2 * a + 1)) == 0
assert sp.simplify(q.subs(x, 2 * a + 1)) == 0
print("1. mu(quotient) = 2a+1 exactly (and = mu(G_a) by Anderson-Morley)  OK")

inner44 = 2 * (a ** 2 + (a - 1) ** 2)
assert sp.expand(inner44 - (2 * a - 1) ** 2 - 1) == 0
print("2. inner44 = (2a-1)^2 + 1  =>  f44 > 2a+1 = mu, strictly, all a  OK")

inner46 = 2 * ((a + 1) ** 2 + a ** 2) - 16 * a * (a + 1) / (2 * a + 1) + 4
gap = sp.simplify(inner46 - (2 * a - 1) ** 2)
assert sp.simplify(gap - (2 * a + 5) / (2 * a + 1)) == 0
print("3. inner46 - (2a-1)^2 = (2a+5)/(2a+1) > 0  =>  f46 > mu, all a  OK")
print("LEMMA PROVED: family F_a never violates bound 44 or 46, for all a >= 1.")

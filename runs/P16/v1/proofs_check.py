#!/usr/bin/env python3
"""P16: symbolic verification (sympy) of the algebraic identities behind the
partial proofs of bounds 44/46 (see NOTES.md, 'Partial proofs').
All checks are exact symbolic simplifications - no floats."""
import sympy as sp

a, b, du, dv, mu_, mv = sp.symbols("a b d_u d_v m_u m_v", positive=True)

# Lemma 1 (regular graphs, degree d): inner44 = 4(d-1)^2, inner46 = (2d-2)^2.
d = sp.Symbol("d", positive=True)
inner44_reg = 2 * ((d - 1) ** 2 + (d - 1) ** 2 + d * d - d * d)
assert sp.simplify(inner44_reg - 4 * (d - 1) ** 2) == 0
inner46_reg = 2 * (d ** 2 + d ** 2) - 16 * d * d / (d + d) + 4
assert sp.simplify(inner46_reg - (2 * d - 2) ** 2) == 0
print("Lemma 1 (regular): inner44 = 4(d-1)^2, inner46 = (2d-2)^2  OK")

# Lemma 2 (semiregular bipartite (a,b)): every edge has d_u=a, d_v=b, m_u=b, m_v=a.
# inner44 = 2((a-1)^2+(b-1)^2) >= (a+b-2)^2  <=>  (a-b)^2 >= 0.
inner44_sr = 2 * ((a - 1) ** 2 + (b - 1) ** 2 + b * a - a * b)
diff44 = sp.simplify(inner44_sr - (a + b - 2) ** 2)
assert sp.simplify(diff44 - (a - b) ** 2) == 0
# inner46 - (a+b-2)^2 = (a-b)^2 + 4(a-b)^2/(a+b) >= 0.
inner46_sr = 2 * (a ** 2 + b ** 2) - 16 * a * b / (a + b) + 4
diff46 = sp.simplify(inner46_sr - (a + b - 2) ** 2)
assert sp.simplify(diff46 - ((a - b) ** 2 + 4 * (a - b) ** 2 / (a + b))) == 0
print("Lemma 2 (semiregular bipartite): margins = (a-b)^2 [+ 4(a-b)^2/(a+b)]  OK")

# Lemma 3 (per-edge reduction to Anderson-Morley  mu <= max d_u+d_v):
# f44(uv) >= d_u+d_v  <=>  (d_u-d_v)^2 + 2(m_u m_v - d_u d_v) >= 0.
inner44_g = 2 * ((du - 1) ** 2 + (dv - 1) ** 2 + mu_ * mv - du * dv)
red44 = sp.simplify(inner44_g - (du + dv - 2) ** 2 - ((du - dv) ** 2 + 2 * (mu_ * mv - du * dv)))
assert red44 == 0
# f46(uv) >= d_u+d_v  <=>  (d_u-d_v)^2 + 4(d_u+d_v) - 16 d_u d_v/(m_u+m_v) >= 0.
inner46_g = 2 * (du ** 2 + dv ** 2) - 16 * du * dv / (mu_ + mv) + 4
red46 = sp.simplify(inner46_g - (du + dv - 2) ** 2
                    - ((du - dv) ** 2 + 4 * (du + dv) - 16 * du * dv / (mu_ + mv)))
assert red46 == 0
# Sufficient condition for 46: m_u+m_v >= d_u+d_v  =>  16 d_u d_v/(m_u+m_v)
# <= 16 d_u d_v/(d_u+d_v) <= 4(d_u+d_v)   (AM-GM: 4 d_u d_v <= (d_u+d_v)^2).
amgm = sp.simplify(4 * (du + dv) - 16 * du * dv / (du + dv) - 4 * (du - dv) ** 2 / (du + dv))
assert amgm == 0
print("Lemma 3 (reduction to Anderson-Morley): identities  OK")
print("All symbolic checks passed.")

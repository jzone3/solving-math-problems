#!/usr/bin/env python3
"""Explicit proper CW(96,36) from Schmidt-Smith (JCTA 2013), Theorems 6.7/6.8.

Group ring Z[C_96] written additively on Z_96. gamma = element of order 16,
alpha = order 3, C3 = <alpha>, C48 = index-2 subgroup.

  A1 = (1+g2+g6)(a - a2)          [g = gamma, a = alpha]
  A2 = (1-g2-g6)(a - a2)
  B  = -1 + (1-g4)(g+g3) + (a+a2)(1+g4)
  D  = (1+g8)B + (1-g8)(c*Ai + d*C3)

Theorem 6.8: D is a CW(96,36) iff supports of the three parts are disjoint,
iff one of conditions (i)-(v) holds; condition (iv) c in M1 u M1*g8, d not in
C48 yields PROPER matrices (Cor 6.9). We brute-force ALL (i, c, d) in
Z_96 x Z_96, machine-verify every valid outcome, and dump proper witnesses.
"""
import sys
import json
from collections import Counter

sys.path.insert(0, "../../../solutions/P11")
from verify import check, is_proper

n = 96
g = 6    # order 16
a = 32   # order 3


def add(*cs):
    """coefficient-preserving sum (Counter.__add__ drops negatives!)"""
    out = Counter()
    for c in cs:
        for x, v in c.items():
            out[x] += v
    return out


def gm(*termlists):
    """multiply group ring elements given as Counter{elt: coeff}"""
    out = termlists[0]
    for t in termlists[1:]:
        new = Counter()
        for x, cx in out.items():
            for y, cy in t.items():
                new[(x + y) % n] += cx * cy
        out = new
    return out


def C(d):  # Counter from list of (elt, coeff)
    c = Counter()
    for e, co in d:
        c[e % n] += co
    return c


one = C([(0, 1)])
A1 = gm(C([(0, 1), (2 * g, 1), (6 * g, 1)]), C([(a, 1), (2 * a, -1)]))
A2 = gm(C([(0, 1), (2 * g, -1), (6 * g, -1)]), C([(a, 1), (2 * a, -1)]))
B = add(C([(0, -1)]),
        gm(C([(0, 1), (4 * g, -1)]), C([(g, 1), (3 * g, 1)])),
        gm(C([(a, 1), (2 * a, 1)]), C([(0, 1), (4 * g, 1)])))
C3 = C([(0, 1), (a, 1), (2 * a, 1)])
onepg8 = C([(0, 1), (8 * g, 1)])
onemg8 = C([(0, 1), (8 * g, -1)])

found = []
for i, Ai in ((1, A1), (2, A2)):
    for c in range(n):
        for d in range(n):
            D = add(gm(onepg8, B), gm(onemg8, C([(c, 1)]), Ai),
                    gm(onemg8, C([(d, 1)]), C3))
            vals = [D.get(x, 0) for x in range(n)]
            if any(abs(v) > 1 for v in vals):
                continue
            P = [x for x, v in enumerate(vals) if v == 1]
            N = [x for x, v in enumerate(vals) if v == -1]
            if len(P) + len(N) != 36:
                continue
            try:
                check(n, 36, P, N, proper=False)
            except AssertionError as e:
                print(f"i={i} c={c} d={d}: disjoint but INVALID: {e}")
                continue
            pr = is_proper(n, P, N)
            found.append((i, c, d, pr, P, N))

print(f"valid CW(96,36) from the family: {len(found)}, "
      f"proper: {sum(1 for f in found if f[3])}")
prop = [f for f in found if f[3]]
if prop:
    i, c, d, pr, P, N = prop[0]
    w = {"n": 96, "k": 36, "P": P, "N": N, "proper": True,
         "construction": f"Schmidt-Smith JCTA 2013 Thm 6.7/6.8, i={i}, c={c}, d={d}, "
                         f"gamma={g}, alpha={a} (additive Z_96); proper by Cor 6.9"}
    json.dump(w, open("../../../solutions/P11/CW96_36_proper.json", "w"), indent=1)
    print("wrote solutions/P11/CW96_36_proper.json:", w)

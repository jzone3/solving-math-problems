#!/usr/bin/env python3
"""Mechanized re-check of AGZ (Crypt. Commun. 2021) Proposition 4.2:
no CW(132, 81) exists.

Their argument: contract a putative CW(132,81) through the subgroup of order 3
to get an ICW_3(44, 81): an integer vector w on Z_44 with |w_i| <= 3 and
w w* = 81 delta_0 (flat power spectrum |ŵ|^2 = 81). By McFarland's multiplier
theorem (AGZ Thm 4.1, gcd(44,81)=1, 81=3^4, t=3 satisfies t ≡ 3^1 mod 44),
t=3 is a multiplier, so some translate of w is fixed by x -> 3x, i.e. w is
constant on <3>-orbits of Z_44.

We exhaust ALL orbit-coefficient assignments c in [-3,3]^(#orbits) with
sum c_o^2 |o| = 81 and test the autocorrelation exactly (integer arithmetic).
If none exists, no CW(132,81) exists (modulo the published multiplier theorem).

Also independently: no CW(m,81) for m | 132, m < 132 exists (weight-81 cells
in DB: 91,121,182,312 — none divides 132), so nonexistence is total, matching
AGZ but contradicting the DB's "Open" for CW(132,9).
"""
from itertools import product

n = 44
K = 81

# <3>-orbits of Z_44
seen = set()
orbits = []
for x in range(n):
    if x in seen:
        continue
    o = []
    y = x
    while y not in o:
        o.append(y)
        y = (3 * y) % n
    orbits.append(sorted(o))
    seen.update(o)
print(f"{len(orbits)} orbits, sizes {[len(o) for o in orbits]}")

count_valid = 0
sols = []
sizes = [len(o) for o in orbits]
for cs in product(range(-3, 4), repeat=len(orbits)):
    if sum(c * c * s for c, s in zip(cs, sizes)) != K:
        continue
    count_valid += 1
    w = [0] * n
    for c, o in zip(cs, orbits):
        for x in o:
            w[x] = c
    ok = True
    for t in range(1, n):
        if sum(w[i] * w[(i + t) % n] for i in range(n)) != 0:
            ok = False
            break
    if ok:
        sols.append(cs)
        print("ICW FOUND:", cs)

print(f"orbit assignments with correct norm: {count_valid}; "
      f"flat-autocorrelation ICW_3(44,81) fixed by 3: {len(sols)}")
if not sols:
    print("CONFIRMED: no <3>-fixed ICW_3(44,81) => AGZ Prop 4.2 stands => "
          "no CW(132,81) exists")

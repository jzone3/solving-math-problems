"""Sanity: reproduce childK's key numbers.
1. F_14 with old sigma = d+m-4: min eig < 0 (approx -0.145).
2. F_k with sigma-hat (c=2, c=4): PSD for k up to 200.
3. n <= 8 exhaustive both caps: 0 failures (reproduce childK).
4. Degenerate-edge convention: enumerate n <= 8, every edge with a_e ~ 0 has
   d = m = 2 at both ends, hence sigma_c = 0 there for every c >= 0.
"""
import numpy as np
from common import (build_base, with_diag, sigma_cap, min_eig, geng,
                    g6_to_adj, windmill)

# 1
bd = build_base(windmill(14))
old = with_diag(bd, bd["d"] + bd["m"] - 4.0)
print("F_14 old sigma min eig:", min_eig(old["M"]))
for k in (13, 14):
    b = build_base(windmill(k))
    o = with_diag(b, b["d"] + b["m"] - 4.0)
    print(f"F_{k} old:", min_eig(o["M"]))

# 2
for c in (2.0, 4.0):
    worst = 1e18
    for k in list(range(2, 40)) + [60, 100, 150, 200]:
        b = build_base(windmill(k))
        e = min_eig(with_diag(b, sigma_cap(b["d"], b["m"], c))["M"])
        worst = min(worst, e)
    print(f"windmills c={c}: worst min eig {worst:.4f}")

# 3 + 4
for c in (2.0, 4.0):
    tot, bad, worst = 0, 0, 1e18
    degen_ok = True
    for n in range(3, 9):
        for g6 in geng(n):
            A = g6_to_adj(g6)
            b = build_base(A)
            s = sigma_cap(b["d"], b["m"], c)
            e = min_eig(with_diag(b, s)["M"])
            tot += 1
            worst = min(worst, e)
            if e < -1e-8:
                bad += 1
            for kk, (i, j) in enumerate(b["edges"]):
                if b["w"][kk] == 0.0 and (abs(s[i]) > 1e-12 or abs(s[j]) > 1e-12):
                    degen_ok = False
    print(f"n<=8 c={c}: tot={tot} bad={bad} worst={worst:.3e} "
          f"degenerate-edge sigma_c=0: {degen_ok}")

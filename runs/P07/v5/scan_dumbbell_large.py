"""Optimize dumbbell D(a,ell,b) ratio_rc at larger n (coarse then fine)."""
import sys
from score143 import stats143, dumbbell

for n in [80, 100, 150, 200, 300, 400, 600, 800]:
    best = None
    step = max(1, n // 40)
    for a in range(3, n - 6, step):
        for b in range(a, n - a - 2, step):
            ell = n - a - b
            if ell < 1:
                continue
            s = stats143(dumbbell(a, ell, b))
            if s and (best is None or s["ratio_rc"] > best[0]):
                best = (s["ratio_rc"], a, ell, b, s)
    # refine around best
    _, a0, _, b0, _ = best
    for a in range(max(3, a0 - step), min(n - 6, a0 + step + 1)):
        for b in range(max(3, b0 - step), min(n - a - 2, b0 + step + 1)):
            ell = n - a - b
            if ell < 1:
                continue
            s = stats143(dumbbell(a, ell, b))
            if s and s["ratio_rc"] > best[0]:
                best = (s["ratio_rc"], a, ell, b, s)
    r, a, ell, b, s = best
    print(f"n={n}: D({a},{ell},{b}) ratio_rc={r:.5f} ratio_pair={s['ratio_pair']:.5f} "
          f"a/n={a/n:.3f} b/n={b/n:.3f} p={s['p']} m={s['m']}", flush=True)

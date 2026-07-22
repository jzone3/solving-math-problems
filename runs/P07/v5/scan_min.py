"""Find minimal-n violations of conj 143 among lollipops L(a,ell) and dumbbells D(a,ell,b)."""
from score143 import stats143, lollipop, dumbbell

best_per_n = {}
for n in range(10, 61):
    loc = None
    for a in range(3, n - 1):
        s = stats143(lollipop(a, n - a))
        if s and (loc is None or s["ratio_rc"] > loc["ratio_rc"]):
            loc = dict(s, fam=f"L({a},{n-a})")
    for a in range(3, n - 4):
        for b in range(3, n - a - 1):
            ell = n - a - b
            if ell < 1:
                continue
            s = stats143(dumbbell(a, ell, b))
            if s and s["ratio_rc"] > loc["ratio_rc"]:
                loc = dict(s, fam=f"D({a},{ell},{b})")
    best_per_n[n] = loc
    flag = " *** VIOLATION ***" if loc["ratio_rc"] > 1 else ""
    print(f"n={n}: {loc['fam']} ratio_rc={loc['ratio_rc']:.5f} ratio_pair={loc['ratio_pair']:.5f}{flag}",
          flush=True)

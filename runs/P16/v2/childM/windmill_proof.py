"""Theorem M1: M(sigma_c)(F_k) is PSD for ALL k >= 2 and caps c in {2, 4}.

Exact sympy proof via the equitable-symmetry eigen-decomposition of the
windmill F_k (hub + k triangle pairs), valid for k >= c + 1 (cap active);
small k (cap inactive, sigma_c = sigma old) checked exactly separately.

Decomposition (S_k x Z_2 symmetry; standard, float-cross-checked below):
  - antisym within a pair (k-dim):      lam1 = Moo - Mpair
  - sym within pair, zero-sum (k-1-dim): lam2 = Moo + Mpair
  - 2x2 block on (hub, uniform outer):  [[Mhh, sqrt(2k) Mho], [., lam2]]
PSD <=> lam1 >= 0, lam2 >= 0, Mhh >= 0, Mhh*lam2 - 2k*Mho^2 >= 0.
"""
import sympy as sp
import numpy as np
from common import build_base, with_diag, sigma_cap, windmill

k = sp.symbols('k', positive=True)

def prove(c):
    print(f"=== cap c = {c} (assuming k >= {c+1}) ===")
    dh, mh = 2 * k, sp.Integer(2)
    do, mo = sp.Integer(2), k + 1
    sh = dh - 4 + sp.Min(mh, dh + c)          # = 2k - 2 for k >= 1
    sh = 2 * k - 2
    so = sp.Integer(c)                        # do - 4 + (do + c), cap active
    a_s = 2 * (dh**2 + do**2) - 16 * dh * do / (mh + mo)   # spoke arg46-4
    a_o = 2 * (do**2 + do**2) - 16 * do * do / (mo + mo)   # outer arg46-4
    ws, wo = 1 / a_s, 1 / a_o
    Mhh = 2 * sh + 4 - dh - sh**2 * (2 * k * ws)
    Moo = 2 * so + 4 - do - so**2 * (ws + wo)
    Mho = -(1 + sh * so * ws)
    Mpair = -(1 + so**2 * wo)
    lam1 = sp.simplify(Moo - Mpair)
    lam2 = sp.simplify(Moo + Mpair)
    det2 = sp.simplify(Mhh * lam2 - 2 * k * Mho**2)
    for name, expr in (("lam1", lam1), ("lam2", lam2), ("Mhh", sp.simplify(Mhh)),
                       ("det2*", det2)):
        num, den = sp.fraction(sp.together(expr))
        # substitute k = t + (c+1) and check all polynomial coeffs positive
        t = sp.symbols('t', nonnegative=True)
        nump = sp.Poly(sp.expand(num.subs(k, t + c + 1)), t)
        denp = sp.Poly(sp.expand(den.subs(k, t + c + 1)), t)
        cn, cd = nump.all_coeffs(), denp.all_coeffs()
        okn = all(x >= 0 for x in cn) and any(x > 0 for x in cn)
        okd = all(x >= 0 for x in cd) and any(x > 0 for x in cd)
        print(f"  {name}: >= 0 for all k >= {c+1}: "
              f"{'PROVED (coeff-positive)' if okn and okd else 'NOT by shift; coeffs num=' + str(cn)}")
        assert okn and okd, (name, cn, cd)
    # float cross-check of the decomposition for a few k
    for kk in (c + 1, 10, 25):
        A = windmill(kk)
        b = build_base(A)
        s = sigma_cap(b["d"], b["m"], float(c))
        M = with_diag(b, s)["M"]
        ev = np.linalg.eigvalsh(M)
        pred = [float(lam1.subs(k, kk)), float(lam2.subs(k, kk))]
        m2 = np.array([[float(Mhh.subs(k, kk)), np.sqrt(2 * kk) * float(Mho.subs(k, kk))],
                       [np.sqrt(2 * kk) * float(Mho.subs(k, kk)), float(lam2.subs(k, kk))]])
        pred += list(np.linalg.eigvalsh(m2))
        got = sorted(set(np.round(ev, 9)))
        want = sorted(set(np.round(pred, 9)))
        match = all(any(abs(g - w) < 1e-6 for g in got) for w in want)
        print(f"  k={kk}: decomposition matches full spectrum: {match} "
              f"(min eig {ev[0]:.6f})")
        assert match and ev[0] > -1e-9

for c in (2, 4):
    prove(c)

# small k (cap inactive: sigma_c = old sigma): exact check k = 2..(c+1)
print("=== small k, cap inactive: exact rational PSD check ===")
from fractions import Fraction
def exact_psd(A, c):
    nn = A.shape[0]
    d = [Fraction(int(A[i].sum())) for i in range(nn)]
    m = [sum(d[j] for j in range(nn) if A[i, j]) / d[i] for i in range(nn)]
    s = [d[i] - 4 + min(m[i], d[i] + c) for i in range(nn)]
    M = [[Fraction(0)] * nn for _ in range(nn)]
    for i in range(nn):
        M[i][i] = 2 * s[i] + 4 - d[i]
    for i in range(nn):
        for j in range(nn):
            if A[i, j] and j > i:
                a4 = 2 * (d[i]**2 + d[j]**2) - Fraction(16) * d[i] * d[j] / (m[i] + m[j])
                w = 0 if a4 == 0 else 1 / a4
                M[i][j] -= 1 + s[i] * s[j] * w
                M[j][i] = M[i][j]
                M[i][i] -= s[i]**2 * w
                M[j][j] -= s[j]**2 * w
    # exact LDL: all pivots >= 0 (Gaussian elimination, skipping zero rows)
    M = [row[:] for row in M]
    for p in range(nn):
        if M[p][p] < 0:
            return False
        if M[p][p] == 0:
            if any(M[p][q] != 0 for q in range(p, nn)):
                return False
            continue
        for r in range(p + 1, nn):
            f = M[r][p] / M[p][p]
            for q in range(p, nn):
                M[r][q] -= f * M[p][q]
    return True

for c in (2, 4):
    for kk in range(2, c + 2):
        r = exact_psd(windmill(kk), c)
        print(f"  c={c} k={kk}: PSD exact: {r}")
        assert r

print("\nTHEOREM M1 PROVED: M(sigma_c)(F_k) PSD for all k >= 2, c in {2,4}.")

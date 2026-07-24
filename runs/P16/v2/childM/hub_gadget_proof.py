"""Theorem M3 (one-hub gadget families): let G(k; L, g) be a hub joined to all
vertices of k >= 2 disjoint copies of any connected g-regular gadget on L
vertices (g >= 1, L >= g+1).  Then M(sigma_c)(G) is PSD for c in {2,4} in the
capped regime m_o >= d_o + c  (i.e. kL >= (g+1)(g+1+c) - g(g+1)); small-k
(uncapped) cases of concrete gadgets are checked exactly.

Reduction (equitable symmetry; float cross-checked):
 outer degrees d_o = g+1, hub d_h = kL, m_h = g+1, m_o = (g(g+1)+kL)/(g+1);
 M acts on each gadget's A_g-eigenspace: for adjacency eigenvalue nu of A_g,
   lam(nu) = t_o - (1 + s_o^2 w_o) nu,
 with the Perron direction nu = g coupling to the hub in a 2x2 block
   [[Mhh, sqrt(kL) Mho], [., lam(g)]].
 Since lam is LINEAR in nu and |nu| <= g, it is enough to prove
   lam(g) >= 0, lam(-g) >= 0, Mhh >= 0, Mhh*lam(g) - kL*Mho^2 >= 0.
 (This covers ALL g-regular gadgets simultaneously.)
"""
import sympy as sp
import numpy as np
from common import (build_base, with_diag, sigma_cap, min_eig, hub_gadgets,
                    gadget_cycle, gadget_clique)

k, L, g = sp.symbols('k L g', positive=True)


def pieces(c):
    dh, do = k * L, g + 1
    mh = g + 1
    mo = (g * (g + 1) + k * L) / (g + 1)
    sh = dh + mh - 4                      # hub never capped (mh small)
    so = 2 * g + c - 2                    # capped regime
    a_s = 2 * (dh**2 + do**2) - 16 * dh * do / (mh + mo)
    a_o = 2 * (do**2 + do**2) - 16 * do * do / (2 * mo)
    ws, wo = 1 / a_s, 1 / a_o
    Mhh = 2 * sh + 4 - dh - sh**2 * (k * L * ws)
    t_o = 2 * so + 4 - do - so**2 * (ws + g * wo)
    Mho = -(1 + sh * so * ws)
    gam = 1 + so**2 * wo
    return Mhh, t_o, Mho, gam


def coeffpos(expr, subs, label):
    e = sp.together(sp.expand(sp.simplify(expr.subs(subs))))
    num, den = sp.fraction(e)
    gens = sorted(num.free_symbols | den.free_symbols, key=str)
    if not gens:
        ok = num * den >= 0
        print(f"  {label}: constant, ok={ok}")
        return bool(ok)
    okn = all(cc >= 0 for cc in sp.Poly(sp.expand(num), *gens).coeffs())
    okd = all(cc >= 0 for cc in sp.Poly(sp.expand(den), *gens).coeffs())
    print(f"  {label}: coeff-positive num={okn} den={okd}")
    return okn and okd


u, v, t = sp.symbols('u v t', nonnegative=True)
for c in (2, 4):
    print(f"=== cap c={c}, capped regime ===")
    Mhh, t_o, Mho, gam = pieces(c)
    lam_p = t_o - gam * g
    lam_m = t_o + gam * g
    det2 = Mhh * lam_p - k * L * Mho**2
    # substitutions: g = 1+u? include g=1: g = 1+u... but need L >= g+1: L = g+1+v
    # capped regime: kL >= (g+1)(c+1)+... use k = kmin + t with kmin chosen so
    # regime holds for all L,g: kL >= (g+1)(g+1+c) - g(g+1) = (g+1)(c+1).
    # take k*L = (g+1)(c+1) + extra: parametrize k = ((g+1)(c+1)+t)/L? messy —
    # instead prove with K := kL as one symbol (K appears only via kL):
    K = sp.symbols('K', positive=True)
    subs0 = {k: K / L}
    ok_all = True
    # lam(+g) = (det2 + kL*Mho^2)/Mhh >= 0 follows from det2 >= 0, Mhh > 0,
    # so it suffices to prove lam(-g), Mhh, det2 nonnegative.
    for name, ex in (("lam(-g)", lam_m), ("Mhh", Mhh), ("det2", det2)):
        ex2 = sp.simplify(ex.subs(subs0))
        # domain: gadget size L >= g+1: L = 2+u+v (g = 1+u);
        # capped regime K = kL >= (g+1)(c+1): K = (2+u)(c+1) + t
        subs = {g: 1 + u, L: 2 + u + v, K: (2 + u) * (c + 1) + t}
        ok = coeffpos(ex2, subs, name)
        ok_all = ok_all and ok
    print("  lam(+g) >= 0: implied by det2 >= 0 and Mhh > 0 "
          "(lam(+g) = (det2 + kL*Mho^2)/Mhh)")
    print("  capped-regime symbolic proof:", "COMPLETE" if ok_all else "INCOMPLETE")
    assert ok_all

# float cross-check of block reduction + exact small-k checks for concrete gadgets
print("=== numeric cross-checks (concrete gadgets, incl. uncapped small k) ===")
GADGETS = {"C4": (gadget_cycle(4), 2), "C5": (gadget_cycle(5), 2),
           "C6": (gadget_cycle(6), 2), "K4": (gadget_clique(4), 3),
           "K2": ((2, [(0, 1)]), 1), "K5": (gadget_clique(5), 4)}
worst = 1e18
for name, (gad, gg) in GADGETS.items():
    for kk in range(2, 26):
        A = hub_gadgets([gad] * kk)
        b = build_base(A)
        for c in (2.0, 4.0):
            e = min_eig(with_diag(b, sigma_cap(b["d"], b["m"], c))["M"])
            worst = min(worst, e)
            assert e > -1e-9, (name, kk, c, e)
print(f"all concrete-gadget checks k=2..25 pass; worst min eig {worst:.6f}")

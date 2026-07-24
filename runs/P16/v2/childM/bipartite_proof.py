"""Theorem M2: M(sigma_c) PSD on every connected semiregular bipartite graph
with delta >= 2, for c in {2, 4}.

Class-A vertices have degree p, class-B degree q (p >= q >= 2); m_A = q,
m_B = p. All edges share a4 = 2(p^2+q^2) - 16pq/(p+q), w = 1/a4.
s_A = p - 4 + min(q, p + c) = p + q - 4  (q <= p < p + c: never capped),
s_B = q - 4 + min(p, q + c): capped iff p > q + c.

M = diag(t_A on A, t_B on B) - gamma * Adj,  gamma = 1 + s_A s_B w,
t_X = 2 s_X + 4 - d_X - s_X^2 w d_X.
Via SVD of the biadjacency, M PSD <=> t_A >= 0, t_B >= 0 and
t_A t_B >= gamma^2 mu^2 for every singular value mu; mu_max = sqrt(pq)
(Perron of biregular bipartite). So PSD <=> t_A, t_B >= 0, t_A t_B >= gamma^2 pq.

Uncapped case p <= q + c is childI Theorem T1 (sigma_c = sigma). Here we prove
the capped case p = q + c + r, r >= 1, q >= 2 symbolically, and re-verify the
uncapped case too.
"""
import sympy as sp
import numpy as np

q, r, u, v = sp.symbols('q r u v', positive=True)


def conditions(p_, q_, sA, sB):
    a4 = 2 * (p_**2 + q_**2) - 16 * p_ * q_ / (p_ + q_)
    w = 1 / a4
    gam = 1 + sA * sB * w
    tA = 2 * sA + 4 - p_ - sA**2 * w * p_
    tB = 2 * sB + 4 - q_ - sB**2 * w * q_
    det = tA * tB - gam**2 * p_ * q_
    return [("tA", tA), ("tB", tB), ("det", det)]


def coeff_positive(expr, subs, label, allow_zero=True):
    e = sp.together(sp.simplify(expr.subs(subs)))
    num, den = sp.fraction(e)
    num, den = sp.expand(num), sp.expand(den)
    gens = [g for g in (u, v) if num.has(g) or den.has(g)] or [u]
    okn = all(cc >= 0 for cc in sp.Poly(num, *gens).coeffs())
    okd = all(cc >= 0 for cc in sp.Poly(den, *gens).coeffs())
    print(f"  {label}: nonneg-coeff proof: num {okn}, den {okd}")
    return okn and okd


print("=== capped case: p = q + c + r (r >= 1, q >= 2) ===")
for c in (2, 4):
    p_ = q + c + r
    sA = p_ + q - 4
    sB = 2 * q - 4 + c
    print(f"cap c={c}:")
    all_ok = True
    for name, expr in conditions(p_, q, sA, sB):
        # shift q = u + 2, r = v + 1 -> need >= 0 for u, v >= 0
        ok = coeff_positive(expr, {q: u + 2, r: v + 1}, f"{name} (q>=2,r>=1)")
        all_ok = all_ok and ok
    assert all_ok, f"capped case c={c} not settled by coeff positivity"

print("=== uncapped case p = q + e, 0 <= e <= c (T1 re-proof) ===")
# sigma_c = sigma = p + q - 4 on both sides; childI T1 slack identity:
e = sp.symbols('e', nonnegative=True)
for c in (2, 4):
    ok = True
    for ee in range(0, c + 1):
        p_ = q + ee
        s_ = p_ + q - 4
        for name, expr in conditions(p_, q, s_, s_):
            ok = ok and coeff_positive(expr, {q: u + 2}, f"c={c} e={ee} {name}")
    assert ok

# float cross-check of block reduction on random biregular bipartite graphs
print("=== float cross-check (random biregular bipartite) ===")
import networkx as nx
rng = np.random.default_rng(1)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import build_base, with_diag, sigma_cap, min_eig

def biregular(p, q, copies):
    # nA * p = nB * q ; take nA = q*copies, nB = p*copies; random bipartite
    nA, nB = q * copies, p * copies
    while True:
        G = nx.bipartite.configuration_model([p] * nA, [q] * nB,
                                             create_using=nx.Graph())
        A = nx.to_numpy_array(G)
        d = A.sum(1)
        if (d[:nA] == p).all() and (d[nA:] == q).all() and \
                nx.is_connected(nx.from_numpy_array(A)):
            return A

for (p_, q_) in ((9, 2), (8, 3), (12, 2), (7, 4)):
    A = biregular(p_, q_, 2)
    b = build_base(A)
    for c in (2.0, 4.0):
        s = sigma_cap(b["d"], b["m"], c)
        eig = min_eig(with_diag(b, s)["M"])
        sA = p_ + q_ - 4
        sB = q_ - 4 + min(p_, q_ + c)
        conds = conditions(sp.Integer(p_), sp.Integer(q_), sp.Integer(sA),
                           sp.Rational(sB))
        vals = [float(sp.simplify(x[1])) for x in conds]
        print(f"  ({p_},{q_}) c={c}: min eig {eig:.6f}, tA={vals[0]:.4f} "
              f"tB={vals[1]:.4f} det={vals[2]:.4f}")
        assert eig > -1e-9 and all(vv >= -1e-9 for vv in vals)

print("\nTHEOREM M2 PROVED: M(sigma_c) PSD on all semiregular bipartite "
      "delta>=2 graphs, c in {2,4}.")

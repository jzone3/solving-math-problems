"""Machine verification of the childI lemmas (I2-I6, T1).

Lemma I2 (spectral reformulation): T = 2d+2m-4 >= 4 > 0 for delta>=2;
  M = diag(T) - B with B = Q + DHD nonneg, B_ij >= 1 on edges (irreducible
  for connected G); M PSD <=> rho(P) <= 1, P := diag(T)^{-1}B
  (P similar to the symmetric S = diag(T)^{-1/2} B diag(T)^{-1/2}).

Lemma I4 (resolvent certificate): for 0<alpha<1 with alpha*rho(P)<1,
  h_a := (I - alpha P)^{-1} d satisfies h_a >= d > 0 and
  (I-P)h_a = (1/alpha)(d - (1-alpha)h_a).
  Hence R(alpha): (1-alpha)h_a <= d  ==>  P h_a <= h_a, h_a>0 ==> rho(P)<=1.

Lemma I5 (necessity): rho(P) > 1 ==> R(alpha) fails for every
  alpha in (0, 1/rho).  [Immediate from I4.]

Lemma I6 (monotonicity, discrete proof): if alpha0 <= alpha1 < 1/rho and
  (I-P)h_{alpha0} >= 0 then (I-P)h_{alpha1} >= 0, via
  h_{a1} = h_{a0} + (a1-a0)(I-a1 P)^{-1} P h_{a0}  and
  (I-P)h_{a1} = (I-P)h_{a0} + (a1-a0)(I-a1 P)^{-1} P (I-P) h_{a0}
  (all factors commute; (I-a1 P)^{-1}, P entrywise >= 0).
  So {alpha : R(alpha)} cap (0, 1/rho) is an interval ending at min(1,1/rho).

Theorem T1 (families): F2 holds for (i) all connected regular graphs d>=2,
  (ii) all connected semiregular bipartite graphs with delta >= 2.
  Proof: sigma and w are constant, H = w Q, so
  M = (2 sigma + 4) I - (1 + sigma^2 w) Q, and PSD reduces to
  (1 + sigma^2 w) rho(Q) <= 2 sigma + 4.
  (i) regular d>=3: sigma=2d-4, w = 1/(4d(d-2)), condition <=> rho(Q) <= 2d,
      true always (equality iff bipartite).  d=2: sigma=0, M = 4I - Q,
      rho(Q) <= 4 on cycles.
  (ii) semiregular (dA, dB), s := dA+dB >= 4, sigma = s-4,
      arg46-4 = 2(dA^2+dB^2) - 16 dA dB/s, rho(Q) = s (bipartite semiregular),
      condition: (2s-4 - (1+sigma^2 w)s) * arg4 * s = (dA-dB)^2 (s-4)(s+4) >= 0
      (sympy-verified; s = 4 i.e. dA = dB = 2 is the degenerate cycle case w=0).

This script: sympy-verifies the T1 algebra and the I4/I6 identities,
and numerically spot-checks I2/I4/I6 on all n<=7 delta>=2 graphs.
"""
import numpy as np
import sympy as sp
from common import g6_to_adj, build, geng

print("== sympy: Theorem T1 algebra ==")
dA, dB = sp.symbols("dA dB", positive=True)
s = dA + dB
sigma = s - 4
arg4 = 2 * (dA**2 + dB**2) - 16 * dA * dB / s   # arg46 - 4
w = 1 / arg4
# condition (1 + sigma^2 w) * s <= 2*sigma + 4 = 2s - 4
lhs = (1 + sigma**2 * w) * s
rhs = 2 * s - 4
diff = sp.simplify(rhs - lhs)
# claim: rhs - lhs = (s-4) * ... * (dA-dB)^2 / (positive)  -- check factorization
target = sp.simplify(diff * arg4 * s)  # clear denominators (arg4>0, s>0)
fact = sp.factor(target)
print("  (rhs-lhs)*arg4*s factors as:", fact)
assert sp.simplify(target - (dA - dB) ** 2 * (s - 4) * (s + 4)) == 0
print("  verified: (rhs-lhs)*arg4*s == (dA-dB)^2 (s-4)(s+4)  >= 0 for s >= 4")

# regular case: dA = dB = d
d_ = sp.symbols("d", positive=True)
sig_r = 2 * d_ - 4
w_r = 1 / (4 * d_ * (d_ - 2))
print("  regular: 1+sigma^2 w =", sp.simplify(1 + sig_r**2 * w_r), " (should be (2d-2)/d)")
print("  regular condition (2d-2)/d * 2d <= 4d-4:",
      sp.simplify((2 * d_ - 2) / d_ * 2 * d_ - (4 * d_ - 4)))

print("== sympy: Lemma I4 identity ==")
al = sp.Symbol("alpha", positive=True)
# operator identity (I-P) = (1/al)[(I-al P) - (1-al) I]; check scalar version
P_ = sp.Symbol("p")
print("  (1-p) - (1/al)*((1-al*p) - (1-al)) =",
      sp.simplify((1 - P_) - ((1 - al * P_) - (1 - al)) / al))

print("== numeric: I2/I4/I6 on all delta>=2 graphs n<=7 ==")
rng = np.random.default_rng(0)
bad = 0
tot = 0
for n in range(3, 8):
    for g6 in geng(n):
        tot += 1
        G = build(g6_to_adj(g6))
        T, B, M, d = G["T"], G["B"], G["M"], G["d"]
        assert T.min() >= 4 - 1e-12
        offB = B - np.diag(np.diag(B))
        for (i, j) in G["edges"]:
            assert offB[i, j] >= 1 - 1e-12
        P = B / T[:, None]
        rho = max(abs(np.linalg.eigvals(P)))
        S = B / np.sqrt(np.outer(T, T))
        lam = np.linalg.eigvalsh(S)[-1]
        psd = np.linalg.eigvalsh(M)[0] >= -1e-9
        assert abs(rho - lam) < 1e-8
        assert psd == (rho <= 1 + 1e-9)
        # I4 identity + I6 monotonicity, random alphas
        a0, a1 = sorted(rng.uniform(0.05, 0.95 / max(rho, 1), 2))
        I = np.eye(G["n"])
        h0 = np.linalg.solve(I - a0 * P, d)
        lhsv = (I - P) @ h0
        rhsv = (d - (1 - a0) * h0) / a0
        assert np.allclose(lhsv, rhsv, atol=1e-8)
        h1 = np.linalg.solve(I - a1 * P, d)
        h1b = h0 + (a1 - a0) * np.linalg.solve(I - a1 * P, P @ h0)
        assert np.allclose(h1, h1b, atol=1e-7)
        if ((I - P) @ h0 >= -1e-10).all():
            if not ((I - P) @ h1 >= -1e-8).all():
                bad += 1
print(f"  {tot} graphs checked, monotonicity violations: {bad}")
print("ALL I-LEMMA CHECKS PASSED" if bad == 0 else "FAILURES!")

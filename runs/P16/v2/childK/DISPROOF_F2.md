# DISPROOF of Conjecture F2 — windmill graphs violate M(G) ⪰ 0

**Conjecture F2 (childF/childI) is FALSE.** The windmill (friendship) graphs
F_k = k triangles sharing one hub vertex are counterexamples for every
k ≥ 14. The smallest, F_14, has n = 29 vertices — just above the n ≤ 10
exhaustive verification range, and in a family missed by all random scans.

Notation exactly as childF/childI: for connected G with δ(G) ≥ 2,
σ_i = d_i + m_i − 4, w_e = 1/(arg46(e) − 4), H = R diag(w) Rᵀ,
Q = D_deg + A, D = diag(σ), M(G) = 2D + 4I − Q − DHD.

## 1. The data on F_k

F_k has hub h with d_h = 2k, m_h = 2, σ_h = 2k − 2, and 2k outer vertices
with d = 2, m = (2k + 2)/2 = k + 1, σ_o = k − 1. Edge weights
(w = 1/(arg46 − 4), exact rationals):

- spoke (hub–outer):  arg46 − 4 = 2(4k² + 4) − 64k/(k + 3)  ⇒
  w_s = (k + 3)/(8(k⁴ + 3k³ + k² − 5k + 3)/(k + 3))⁻¹-form, i.e.
  w_s = 1/(8k² + 8 − 64k/(k + 3));
- outer (outer–outer): arg46 − 4 = 16 − 64/(2k + 2)  ⇒
  w_o = 1/(16 − 32/(k + 1)).

## 2. Symbolic disproof (sym_disproof.py, sympy exact)

Restrict the quadratic form xᵀM(F_k)x to the symmetric quotient
x = (a on hub, b on all 2k outer vertices). Exact computation gives
xᵀMx = A a² + 2C ab + B b² with

- A = k(k² + 6k − 3)/(k² + 4k − 3) > 0,
- B = k(−k⁴ + 12k³ + 59k² − 78k + 24)/(4(k² + 4k − 3)),
- C = −k(5k² + 18k − 15)/(2(k² + 4k − 3)),
- **AB − C² = −k²(k − 1)(k³ − 9k² − 75k + 99) / (4(k² + 4k − 3)).**

The cubic k³ − 9k² − 75k + 99 has largest real root ≈ 13.849; it is
negative at k = 13 (−200) and positive at k = 14 (+29). Hence
AB − C² < 0, and since A > 0 the form is indefinite, **for every k ≥ 14**:
M(F_k) is NOT PSD, so F2 fails.

## 3. Explicit exact witness (k = 14, n = 29)

x = 1217/554 on the hub, 1 on all 28 outer vertices:

  xᵀ M(F_14) x = **−2639/554 ≈ −4.7635 < 0**   (exact rational arithmetic,
  `exact_witness.py`/`sym_disproof.py`; float cross-check −4.76353790…).

Additional exact rational witnesses verified at k = 16, 17, 18, 25
(`exact_witness.py`, independent full-matrix rational build, witnesses from
rationalized eigenvectors — all give exact negative rationals).

Float spectra (`windmill.py`): min eig M(F_k) = +1.027 (k=13), −0.145
(k=14), −5.25 (k=17), −4601 (k=200); ρ(P) = 1.137 at k = 17 and grows like
Θ(k^{1/2})-ish — the failure is not marginal.

For k ≤ 13 the symmetric quotient is PSD and float full spectra are
positive: F_14 is the minimal windmill counterexample. Wheels W_n (n ≥ ~40),
hub + k C_4, hub + k C_5, hub + k K_3 (k ≥ ~10–15) fail similarly
(`family_scan.py`, `upstream_check.py`) — the mechanism is one high-degree
hub whose low-degree neighbors have huge m (so huge σ = d + m − 4) and cheap
mutual edges: each outer edge uw contributes w_o(σ_u + σ_w)(σ_u d_u + σ_w d_w)
≈ k²/2 of "deficiency" while the global surplus is only 2d_h(d_h − 2) ≈ 8k².

## 4. Upstream conjectures SURVIVE (this does NOT break D1 / Bound 46)

Theorem F3 (childF) is one-directional: F2 ⇒ D1. On every failing family we
checked K = diag(arg46) − A_L² directly (`upstream_check.py`):

- min eig K(F_k) ∈ [14.0, 15.9] for k = 14…150 (D1 holds with growing margin);
- wheels, hub+kC_4, hub+kK_3 up to n = 161: min eig K ∈ [21, 27] (D1 holds);
- Bound 46 (ρ(Q)² ≤ max arg46) holds everywhere with large margin.

So the reduction D1 ⇒ F2 direction does not exist; the childF reduction
LOSES TOO MUCH exactly on hub-dominated graphs. D1 remains open and fully
consistent.

## 5. The rescue: the diagonal was wrong, not the reduction (Theorem K3)

Theorem F3 holds for ANY diagonal D ⪰ 0. The choice σ = d + m − 4 is what
fails. Two repairs, both machine-verified:

1. **Windmills are SDP-rescuable with an explicit diagonal.** For k ≥ 4 take
   s_hub = 4k, s_outer = 4. Then M(s) ⪰ 0, with fully symbolic proof
   (`windmill_rescue_proof.py`): M(s) diagonalizes into
   - λ_antisym = 11k³ + 33k² − 79k + 27 (>0, k ≥ 2) [mult k],
   - λ_sym0 = (k−1)(7k³ + 17k² − 67k + 27) (>0, k ≥ 2) [mult k−1],
   - a 2×2 hub block with trace > 0 and det = 8k(k−1)²(k²+4k−3)
     (3k⁵ + 9k⁴ − 82k³ + 58k² + 55k − 27) > 0 for k ≥ 4
   (all positivity by coefficient-positive shifts k = t + k₀, sympy exact;
   full-matrix float cross-check matches the predicted spectrum to 1e−12).

2. **A capped closed form passes every test that kills σ = d + m − 4:**

     **σ̂_i := d_i − 4 + min(m_i, d_i + c),  c ∈ {2, 4}**

   (equal to d + m − 4 whenever m ≤ d + c, in particular on regular graphs,
   preserving tightness on the equality manifold). See F2″ in NOTES.md:
   exhaustive n ≤ 10 (all 10,013,006 δ≥2 graphs, both caps, 0 failures),
   all families, skew K_{a,b}, 4,000 random/hybrid graphs to n ≈ 150.

**New crown statement (F2′):** for every connected δ ≥ 2 graph there exists
a diagonal s ≥ 0 with M(s) = 2 diag(s) + 4I − Q − diag(s) H diag(s) ⪰ 0
(SDP-representable via the Schur LMI, childF §5(ii)); the strengthened
closed-form version F2″ uses s = σ̂ (cap c). Either implies D1 by Theorem F3.

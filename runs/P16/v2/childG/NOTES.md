# P16 childG — the δ = 1 (pendant-vertex) case of Bound 46

Child session of runs/P16-v2, follow-up to childD §4. Task: prove

**Bound 46**: μ(G) ≤ RHS46(G) := max_{ij∈E} [ 2 + √(2(dᵢ²+dⱼ²) − 16dᵢdⱼ/(mᵢ+mⱼ) + 4) ]

for all connected graphs with a pendant vertex, ASSUMING it (or its ρ(Q)/D1
strengthening) for all δ ≥ 2 graphs (**Hypothesis D**, attacked separately).

**OUTCOME: NO complete conditional proof.** What this session delivers instead:
(i) an exact pendant-elimination reformulation (Lemma G1) that converts the δ=1
case into a diagonally-perturbed δ≥2 eigenvalue problem; (ii) three new rigorous
unconditional sufficient criteria (Theorems G2, G3, Lemma G5) that together cover
85% of all leafy graphs with n ≤ 9; (iii) a new degree-control lemma (G7,
one-line proof) that every future proof attempt will need; and (iv) proofs that
essentially every "black-box" use of Hypothesis D fails, with explicit
counterexample certificates — the reduction itself is where the difficulty lives.

Conventions as in the parent run: d = degree, m = average neighbour degree,
arg46(e) = the √-argument, negative argument ⇒ edge excluded; leaf = degree-1
vertex, support = its neighbour; H := G ∖ {leaves}; ℓ_i = # leaf-neighbours of
i in G; τ = τ(t) := t/(t−1). Numerics: float64, tol 1e-9, nauty-geng exhaustive.
All scripts in this directory; identities sympy-checked in `symbolic.py`.

## 1. Rigorous results (proofs complete, machine-verified)

### Lemma G1 (exact pendant elimination)
Let G be connected, n ≥ 3, and t > 1. Then

  μ(G) ≤ t  ⟺  λ_max( L(H) + τ(t)·diag(ℓ) ) ≤ t.

*Proof.* The leaf set S is independent (two adjacent leaves ⇒ G = K₂), so in
block form tI − L(G) has leaf block (t−1)I_S, H-block tI − L(H) − diag(ℓ)
(G-degrees of H-vertices are d^H + ℓ), and coupling C with one −1 per leaf
column. tI − L(G) ⪰ 0 ⟺ t−1 > 0 and the Schur complement
tI − L(H) − diag(ℓ) − (t−1)^{-1}CCᵀ ⪰ 0; CCᵀ = diag(ℓ) because distinct leaves
have distinct columns and each has a single support. Since 1 + 1/(t−1) = τ(t),
the complement is tI − L(H) − τ·diag(ℓ). ∎
(Machine-checked as an iff on all 411 leafy connected graphs n ≤ 7 at four
t-values each (μ±0.3, RHS46, μ+3): 0 discrepancies; `verify_G.py`.)

So the δ=1 case of Bound 46 is EXACTLY the statement: for every leafy G with
T := RHS46(G), the matrix L(H) + τ(T)diag(ℓ) — a Laplacian of a smaller graph
plus a diagonal load τℓ_c ≤ (4/3)ℓ_c concentrated on support vertices — has
λ_max ≤ T. This is the clean interface at which Hypothesis D must be injected;
everything below measures how much of the gap each tool closes.

### Theorem G2 (leaf-aware Merris; unconditional)
If every vertex i of H satisfies d_i^H + m_i^H + τ(t)·ℓ_i ≤ t (isolated
vertices of H: τℓ_i ≤ t), then μ(G) ≤ t.
*Proof.* Gershgorin applied to D⁻¹(L(H) + τdiag ℓ)D, D = diag(d^H), plus
Lemma G1. Row i has centre d_i^H + τℓ_i and radius Σ_{j∼i} d_j^H/d_i^H = m_i^H. ∎

Coverage at t = RHS46(G): **3,264 / 4,086 leafy graphs n ≤ 8 and
57,380 / 67,394 at n = 9 (85%)** — by far the strongest single unconditional
tool found for the leaf case. It needs NO Hypothesis D. Uncovered graphs are
those with a vertex where d^H + m^H is already within τℓ of T, i.e. the
"deficient" dense-neighbourhood configurations of childD §2.

### Theorem G3 (leafy extension of childD's Theorem D2; unconditional)
If every edge ij of G satisfies
  arg46(e) ≥ 4 + 2dᵢ(dᵢ−2)⁺ + 2dⱼ(dⱼ−2)⁺,
then Bound 46 holds for G (leaves allowed, unlike D2).
*Proof.* In childD's identity (†), the leaf terms enter as −2(dᵢ−2)Xᵢ² = +2Xᵢ²
≥ 0 and can be dropped; Cauchy–Schwarz Xᵢ² ≤ dᵢΣ_{e∋i}x_e² is applied only at
vertices with dᵢ ≥ 2. The per-edge condition then makes diag(arg) − A_L² ⪰ 0 on
the top eigenvector, and 2 + λ_max(A_L) = ρ(Q) ≥ μ finishes as in D1⇒46. ∎
For δ≥2 data this is exactly D2 (sympy identity, `symbolic.py` §3). New leaf-edge
content: a leaf edge satisfies the condition iff 2d_c² + 2d_c m_c − 7d_c + m_c ≥ 0,
i.e. ALWAYS for d_c ≥ 3, and for d_c = 2 iff m_c ≥ 6/5. Coverage is small
(37 / 67,394 at n = 9) — as with D2, the Dirichlet term is essential — but it
settles that D2's mechanism itself survives pendant vertices.

### Lemma G5 (Merris–leaf comparison region; symbolic)
For a support vertex c write (d,m) = (d_c, m_c). Then
  d + m ≤ t46(leaf edge at c) = 2 + √(2d² + 6 − 16d/(d+m))
  ⟺ p(d,m) := d³ − d²m + 4d² − 3dm² + 8dm − 14d − m³ + 4m² + 2m ≥ 0.
The positive boundary branch m*(d) is the unique positive root of the cubic;
m*(3) = 3 exactly (p(3,m) = −(m+7)(m+1)(m−3)), and m*(d)/d → √2 − 1
(leading form −(c+1)(c²+2c−1) at m = cd). Consequence (Perron localization):
if the maximiser u of y_i/d_i (y = Perron vector of Q) is a support vertex with
p(d_u, m_u) ≥ 0, then μ ≤ ρ(Q) ≤ d_u + m_u ≤ RHS46(G).
Caveat (tested): the maximiser is a support vertex in only ~34% of leafy n ≤ 8
graphs, and the region hypothesis genuinely fails on GTm|~{-type graphs
(min slack −0.545, `explore4.py`) — this is a partial tool only.

### Lemma G7 (degree forces RHS46; new, one-line proof)
For every vertex v with d_v ≥ 8: RHS46(G) ≥ 2 + √(2d_v² − 16d_v + 6).
*Proof.* Let u be a minimum-degree neighbour of v. Then m_v ≥ d_u, so
16 d_v d_u/(m_u + m_v) ≤ 16 d_v, and arg46(uv) ≥ 2d_v² + 2d_u² + 4 − 16d_v ≥
2d_v² − 16d_v + 6 > 0. ∎
Corollary (degree cap): Δ(G) ≤ 4 + √((T−2)²/2 + 13) with T = RHS46(G) — every
walk/pivot/Gershgorin argument gets its degree control from this. Verified with
slack ≥ 11.3 on all connected n ≤ 8, and the weaker −16d+4 form against RHS46
directly on all trees n ≤ 14, min gap 1.826 at P₃ (`g7_check.py`, g7_check.log).

### Theorem G4 (conditional core criterion; uses Hypothesis D)
Assume Hyp D (μ ≤ RHS46 for connected δ≥2 graphs). If H is connected with
δ(H) ≥ 2 and RHS46(H) + τ(T)·max_c ℓ_c ≤ T (T = RHS46(G)), then Bound 46 holds
for G. *Proof.* Lemma G1, Weyl's inequality λ_max(L(H)+τdiag ℓ) ≤ μ(H) + τ max ℓ, and
μ(H) ≤ RHS46(H) by Hyp D. ∎
Coverage 10,760 / 67,394 at n = 9 — and empirically a SUBSET of Theorem G2's
coverage (union = 57,398 ≈ G2 ∪ G3). Verdict: this naive injection of
Hypothesis D adds essentially nothing beyond the unconditional G2; the Weyl
step and the RHS46(H) ↔ RHS46(G) mismatch are both too lossy.

## 2. Negative results: every black-box reduction to Hypothesis D fails

All with explicit witnesses; scripts named.

1. **Leaf completion** (add edges at leaves to reach δ≥2, then Hyp D +
   μ-monotonicity): for 125 / 411 leafy graphs n ≤ 7 NO completion F (each new
   edge incident to a leaf) satisfies RHS46(G+F) ≤ RHS46(G) — exhaustive over
   ≤ 200k partner choices per graph (`explore3.py`). Witnesses include P₃ (BW).
2. **Supergraph routes fail on sparse graphs**: for the chain
   μ(G) ≤ μ(G*) ≤ RHS46(G*) ≤ RHS46(G) one needs a δ≥2 supergraph G* with
   RHS46(G*) ≤ RHS46(G); already for P₃ (RHS46 = 3.826) even the most
   conservative δ≥2 extension C₅ has RHS46 = 4. Constructions tested and refuted:
   mirror-doubling joined at leaves (min slack −0.494 at FCOf?, `explore5.py`),
   pendant-triangle-via-edge, leaf-triangle, common-apex (−1.12 / −1.46 / −0.98,
   `explore6.py`). Sparse leafy graphs have RHS46 too small to absorb ANY added
   structure.
3. **Single-leaf-deletion induction is dead broadly, not just on FCOf?**:
   201 / 4,086 leafy n ≤ 8 graphs are "stubborn" — EVERY leaf deletion strictly
   increases RHS46 (`explore7.py`). On 182 of them the direct leaf-edge bound
   μ ≤ max leaf-terms also fails (worst −2.17 at GCQdnk). So no per-leaf choice
   rule can rescue L4-style induction; the strengthened hypothesis must track
   more than RHS46 (Φ = min(RHS46, Merris) also fails: FCOf?).
4. **Restricted-PSD (Perron-only D1) fails for δ=1**: even zᵀKz ≥ 0 for the
   line-graph Perron vector z fails at P₄ (CU, −0.238; `explore5.py`) — the
   negative-argument middle edge kills it. Any D1-type extension must reweight
   or exclude such edges.
5. **childD's L1/B1-style shortcuts break at n = 9**: μ ≤ max(leaf terms ∪
   2-core edge terms) — true for ALL 4,086 leafy n ≤ 8 — FAILS at n = 9
   (H?`@?bo, −0.678; spiders S_k(2) with k ≥ 4 need the centre edges), and
   μ(tree) ≤ max leaf-terms fails identically (`explore2.py` at 9). Beware:
   n ≤ 8 evidence is NOT predictive for this problem family.
6. **Tree case cannot be closed by dominance**: on trees, min over
   {Merris, d_i+d_j, Guo–Das, √(2d(d+m))} still exceeds RHS46 on 27 trees
   n ≤ 14 (worst −0.310 at I?AA@_gw?; `trees_dom.py`).
7. **2-core / Merris localization**: RHS46(2-core) ≤ RHS46(G) fails (GCQbfk,
   −0.289); d_u+m_u ≤ RHS46 at the Q-Perron localizer u fails (FCOf?, −0.551)
   (`explore1.py`, `explore4.py`).

## 3. Quantitative map of the residual hard core

- Trees: min (RHS46 − μ) over ALL trees 7 ≤ n ≤ 14 is **0.0353, attained ONLY
  at the spider S(2,2,2) = FCOf?** (n=7); all other trees n ≤ 14 have slack
  ≥ 0.21, with no decreasing trend (0.25 at n = 14). Spider families move AWAY
  from tightness as legs lengthen or multiply (S(3,3,3): 0.46, S_k(2) k≥4:
  ≥ 0.64, growing). Bound 46 on trees looks uniformly slack outside one sporadic
  graph — a certificate proof with tolerance < 0.035 would suffice.
- Leafy graphs n = 9 not covered by G2 ∪ G3: 9,996 (15%). Their signature:
  a support-adjacent vertex with d^H + m^H within τℓ ≤ 4/3·ℓ of T — the
  leaf-loaded version of childD's deficient edges s(mᵢ+mⱼ) < 4p.
- The exact object to bound (Lemma G1) is L(H) + τdiag(ℓ) with τ ∈ (1, 4/3]
  for T ≥ 4: the leaf case of Bound 46 is a **diagonally-loaded δ≥2 problem
  with load ≤ 4ℓ/3 at supports**. A "Hypothesis D with diagonal room"
  (D1 for L(H) + W, W supported on any vertex set with explicit budget
  W_c ≤ (4/3)ℓ_c tied to arg46-slack of H-edges at c) would close the leaf case
  by Lemma G1 + iteration on pendant depth — this is the sharpest reformulation
  we can hand back to the δ≥2 program.

## 4. Suggested next steps

1. Prove **trees** unconditionally: Lemma G1 iterates to an exact leaf-to-root
   pivot recursion q_v = t − d_v − Σ_children 1/q_u > 0; Lemma G7 caps degrees
   by t. The only tight instance is S(2,2,2) (slack 0.035); a two-parameter
   pivot invariant q_v ≥ κ(d_v, dist-to-leaf) with the S(2,·,·) family handled
   exactly looks feasible and is a self-contained publishable piece.
2. Strengthen the δ≥2 target from D1 to **D1-with-diagonal-budget** (§3, last
   item). The budget τℓ_c is exactly what pendant elimination produces, and on
   the D1 side extra diagonal room is available wherever arg46 > 4 + local CS
   cost (Theorem G3's slack). This is the only route found here in which
   Hypothesis D composes with the leaf case without loss.
3. For the 15% residual: classify the n = 9 uncovered graphs (script hook in
   `verify_G.py`) by their loaded-vertex data (d^H, m^H, ℓ, T); childD's
   H := R diag(1/(arg−4)) Rᵀ spectral reformulation may absorb the diagonal
   load naturally.

## 5. Files

- `explore1.py` — A1–A6 shape tests (leaf terms, 2-core, ρ(Q) sanity)
- `explore2.py` — edge-class tests B1–B4 (+ `explore2_n9.log`: n=9 refutations)
- `explore3.py` — leaf-completion search (negative, 125 witnesses)
- `explore4.py` — Q-Perron/Merris localization tests C1–C5 (negative)
- `explore5.py` — mirror-doubling + restricted-PSD D1P (negative)
- `explore6.py` — pendant-triangle/apex constructions H2/H5/H6 (negative)
- `explore7.py` — stubborn-graph census, W1 (negative, 201 stubborn)
- `symbolic.py` — sympy: leaf-edge arg46, Lemma G5 cubic, G3 identity, Schur 3×3
- `verify_G.py` + `verify_G_n9.log` — Lemma G1 iff check (0 failures n ≤ 9),
  coverage of G2/G3/G4 (n ≤ 8: 3264/14/985 of 4086; n = 9: 57380/37/10760 of
  67394; union 57398)
- `g7_check.py`, g7_check.log — Lemma G7 numeric verification
- `trees_dom.py`, trees_dom_n14.log — tree dominance tests (negative)
- explore1_n8.log, explore4_n8.log, explore7_n8.log — archived runs

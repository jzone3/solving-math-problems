# P16 childD — proof attempt for BHS Bound 46 via a PSD reformulation on the line graph

Child session of runs/P16-v2 (builds on childB's Lemmas B1–B6). Task: complete,
rigorous proof of

**Bound 46**: μ(G) ≤ max_{ij∈E} [ 2 + √( 2(dᵢ² + dⱼ²) − 16dᵢdⱼ/(mᵢ+mⱼ) + 4 ) ]

(negative √-argument ⇒ edge term −∞, excluded). Notation as in childB:
s = dᵢ+dⱼ, p = dᵢdⱼ, Q_G = D+A (signless Laplacian of G), R = unoriented incidence
matrix (n×E), A_L = A(L(G)), λ = λ_max(A_L), arg46(e) = the √-argument,
RHS46 = max edge term. All numerics: float64, tol 1e-9, nauty-geng exhaustive.

**OUTCOME: no complete proof (and no counterexample). Main advance: an exact PSD
reformulation/strengthening of Bound 46 (Conjecture D1 below) that is verified
exhaustively for ALL connected δ≥2 graphs with n ≤ 9 and 175k random larger graphs,
plus new rigorous sufficient conditions (Theorems D2/D3) that subsume the equality
manifold, plus a precise map of which cases resist and why.**

## 1. The PSD reformulation (new; rigorous)

### Lemma D0 (factorization identity)
Let K := diag(arg46(e)) − A_L². Then

  K = diag(arg46(e) − 4) − Rᵀ (Q_G − 4I) R.

*Proof.* A_L = RᵀR − 2I and RRᵀ = Q_G, so
A_L² = RᵀRRᵀR − 4RᵀR + 4I = Rᵀ Q_G R − 4RᵀR + 4I = Rᵀ(Q_G − 4I)R + 4I. ∎

Equivalently, with X := Rx (so Xᵢ = Σ_{e∋i} x_e) and L_G = D−A:

  xᵀKx = Σ_e (arg46(e) − 4) x_e² − 2 Σ_i (dᵢ−2) Xᵢ² + Xᵀ L_G X        (†)

(using XᵀQ_GX = Σ_{ij∈E}(Xᵢ+Xⱼ)², XᵀL_GX = Σ_{ij∈E}(Xᵢ−Xⱼ)², and
Σ_e(Xᵢ+Xⱼ)² = 2Σᵢ dᵢXᵢ² − Σ_e(Xᵢ−Xⱼ)²). Identity (†) machine-checked on random
vectors for every connected graph n ≤ 7 (`psd_check.py ... check`).

### Theorem D1⇒46
If K ⪰ 0 then ρ(Q_G) ≤ RHS46 (hence μ ≤ RHS46, i.e. Bound 46 holds for G).
*Proof.* Let z be a unit eigenvector of A_L for λ ≥ 0. Then
λ² = zᵀA_L²z ≤ Σ_e arg46(e) z_e² ≤ max_e arg46(e), so
ρ(Q_G) = 2 + λ ≤ 2 + √(max_e arg46) = RHS46 (childB Lemma B1), and μ ≤ ρ(Q_G). ∎

### Conjecture D1 (the crown statement)
**For every connected graph G with δ(G) ≥ 2: K(G) ⪰ 0.**

Verified exhaustively: ALL connected δ≥2 graphs with 3 ≤ n ≤ 9
(507 + 7,442 + 197,772 at n = 7,8,9; smaller n included; min eigenvalue ≥ −1.6e-14,
i.e. zero up to float noise; `psd_check.py`, logs psd9_*.log) and 175,465 random
larger graphs (G(n,p), random-regular ± edges, K_{d,d} minus edges, BA graphs,
n up to 40; min eig −1.4e-13; `rand_psd.py`). Equality (min eig = 0) occurs
e.g. at bipartite regular graphs — as it must, since Bound 46 is tight there.

Remarks.
- K ⪰ 0 ⟺ ρ(diag(arg)^{-1/2} A_L² diag(arg)^{-1/2}) ≤ 1 (needs arg > 0; we verified
  min_e arg46 = 4 > 0 over all δ≥2 graphs n ≤ 8, attained at C₃-like data).
  Max of that spectral radius over all δ≥2 graphs n ≤ 8 is exactly 1.0000000000.
- D1 is strictly stronger than Bound 46 and even than the ρ(Q) strengthening,
  yet it survives n ≤ 9 exhaustively. It is FALSE for δ = 1 (39 failures at n = 8,
  worst min-eig −11.97 at G??F?{): leaves must be handled separately (§4).
- Via (†), D1 says: Σ_e(arg−4)x_e² + XᵀL_GX ≥ 2Σᵢ(dᵢ−2)Xᵢ². The Dirichlet term
  XᵀL_GX is ESSENTIAL: the relaxation dropping it (Q' := diag(arg−4) − B,
  B_{ef} = Σ_{i∈e∩f} 2(dᵢ−2)) is NOT PSD in general (min eig −7.65 at G??F~{;
  `qprime.py`).

## 2. New rigorous sufficient conditions (proofs complete, sympy-checked)

### Theorem D2 (per-edge criterion)
Let G be connected with δ(G) ≥ 2. If every edge ij satisfies

  (dᵢ+dⱼ)(mᵢ+mⱼ) ≥ 4 dᵢdⱼ                                     (C-D2)

then K(G) ⪰ 0, hence Bound 46 holds for G.
*Proof.* In (†), drop XᵀL_GX ≥ 0 and apply Cauchy–Schwarz Xᵢ² ≤ dᵢ Σ_{e∋i} x_e²
(coefficients dᵢ−2 ≥ 0 by δ≥2):
2Σᵢ(dᵢ−2)Xᵢ² ≤ Σ_{e=ij} [2dᵢ(dᵢ−2)+2dⱼ(dⱼ−2)] x_e². The sympy-verified identity
arg46 − 4 − 2dᵢ(dᵢ−2) − 2dⱼ(dⱼ−2) = 4s − 16p/(mᵢ+mⱼ) shows the remaining per-edge
coefficient is ≥ 0 iff (C-D2). ∎

(C-D2) holds with equality for regular graphs and covers all (r,s)-semiregular
bipartite graphs ((r+s)² − 4rs = (r−s)² ≥ 0) — so D2 subsumes childB Prop B6 for
Bound 46 and covers the entire equality manifold. It strengthens the parent-run
criterion (NOTES.md §3 item 1) from "at a max-degree-sum edge" to a full PSD
certificate. Coverage beyond that is small (42 / 8,025 δ≥2 graphs n ≤ 8;
`coverage.py`): the interesting graphs have "deficient" edges with s(mᵢ+mⱼ) < 4p
(high-degree adjacent vertices whose neighbors have low degree).

### Theorem D3 (power-weighted criterion)
Let δ(G) ≥ 2, a ∈ [0,1]. If every edge ij satisfies
  2(dᵢ−2) dᵢ mᵢᵃ dⱼ^{−a} + 2(dⱼ−2) dⱼ mⱼᵃ dᵢ^{−a} ≤ arg46(e) − 4,
then Bound 46 holds for G.
*Proof.* Weighted Cauchy–Schwarz with weights w_{i,ik} = d_k^{−a}:
Xᵢ² ≤ (Σ_{k∼i} d_kᵃ)(Σ_{k∼i} d_k^{−a} x_{ik}²) and Jensen (xᵃ concave) gives
Σ_{k∼i} d_kᵃ ≤ dᵢmᵢᵃ; substitute into (†) as in D2. ∎
(Coverage 56 / 8,025 at n ≤ 8 with a-grid — only marginally more than D2; no choice
of per-vertex-edge weights can cover graphs where Q' itself is non-PSD, e.g. G??F~{.
This shows ALL pure Cauchy–Schwarz/certificate localizations of D1 that discard the
Dirichlet term must fail; the coupling term is where the remaining difficulty lives.)

## 3. Negative findings for the childB proof program (rule G ↦ φ_G)

1. **λ-normalized DHS-style φ fails.** The natural enrichment of childB's edge-CW
   Lemma B2 following DHS's proofs of Bounds 10/23/43 (φ evaluated at dᵢ/λ, mᵢ/λ with
   λ = RHS46, so a two-piece φ "knows" the graph via λ) does NOT admit a universal φ:
   identity, all two-piece linear φ (breakpoint c ∈ [0.3,0.8], slope t ∈ [0,0.8]),
   and x(1−x)^b all fail on thousands of n ≤ 8 graphs (`scan_lamnorm.py`; worst
   deficits ≈ −25 at GTm|~{). Note powers x^a are λ-invariant, so normalization adds
   nothing there.
2. **No simple rule a(G) for the power family.** The per-graph sets
   {a : max_e CW_a ≤ RHS46} are nonempty intervals for ALL δ≥2 graphs n ≤ 8
   (`aintervals.py`, aint8_d2.tsv) — but no function of Δ/δ alone can select from
   them (bucket [1.5,2): required max-alo 0.585 > available min-ahi 0.575), nor of
   RHS46/Δ (5 overlapping buckets fail), so any valid rule a(G) must use finer
   structure than these invariants. (The intervals being nonempty at n = 9 too is
   childB's finding 3.)
3. **Pointwise second-order certificates fail.** No fixed edge- or vertex-form test
   vector y (13 natural candidates incl. y = 1, s, √arg, arg, Rᵀd, Rᵀ(d+m), …)
   satisfies (A_L²y)_e ≤ arg46(e) y_e on all δ≥2 graphs (`certs.py`) — forced,
   because equality graphs make ρ(...) = 1 exactly, so any pointwise certificate
   must coincide with the Perron vector there. All proofs must exploit slack
   globally (max-vs-max), consistent with childB finding 4.

## 4. The leaf (δ = 1) case: what holds and what breaks

- K ⪰ 0 fails for some δ=1 graphs (§1), and arg46 can be ≤ 0 (P₄ middle edge), so
  D1-type machinery cannot apply verbatim.
- **L4 (empirical, promising)**: for every connected graph with a leaf, n ≤ 8:
    μ(G) ≤ max( max_{leaf edges e} t46(e), RHS46(G−v) )   for v the/a leaf,
  with min slack +0.0112 (at G?`@f?; `leaves.py`). Also verified for all 63,308
  connected n = 9 graphs with a leaf (min slack 0.083; `leaves9.py`, l9_*.log).
  If L4 were proved, induction on n would reduce Bound 46 to the δ≥2
  case PROVIDED deletion never increases RHS46 — but:
- **Monotonicity fails**: there are graphs (FCOf?, GCOcfc — exactly the known
  power-family exception family) where deleting EVERY leaf increases RHS46
  (`leaves2.py`). So leaf-deletion induction cannot close as-is; the induction
  would have to carry a stronger hypothesis than Bound 46 itself.
- **The ρ(Q) version of L4 is FALSE** (min slack −0.179 at GTm|~{), so unlike the
  δ≥2 case the leaf case genuinely needs μ, not ρ(Q) — interlacing arguments on Q
  alone cannot prove it.

## 5. Exactly which case resists (map for future sessions)

1. δ≥2, proving Conjecture D1. Obstruction: at edges with s(mᵢ+mⱼ) < 4p the
   diagonal of (†) is negative after any Cauchy–Schwarz localization; positivity is
   restored only by the Dirichlet coupling XᵀL_GX across the whole graph, and every
   certificate-style bound collapses to equality on bipartite regular graphs (so
   certificates must equal Perron vectors exactly there). A proof likely needs
   either (a) an SOS decomposition of (†) mixing the three terms non-locally, or
   (b) spectral: K ⪰ 0 ⟺ λ_max(H^{1/2}(Q_G−4I)H^{1/2}) ≤ 1 with
   H := R diag(1/(arg46−4)) Rᵀ (an n×n weighted signless Laplacian; when arg > 4);
   on bipartite regular this reads q(q−4)/(4d(d−2)) ≤ 1 with equality at q = 2d —
   a promising finite-dimensional target for interlacing/majorization arguments.
2. δ=1. Obstruction: RHS46 is not monotone under leaf deletion on the FCOf? family;
   need either a strengthened induction hypothesis or a direct argument for graphs
   whose deficient structure is leaf-driven.

## 6. Files

- `psd_check.py` — K ⪰ 0 exhaustive check (+ identity (†) self-test); psd9_*.log
- `rand_psd.py` — random large-graph D1 stress test (175k graphs)
- `qprime.py` — non-PSD-ness of the Dirichlet-free relaxation Q'
- `certs.py` — pointwise second-order certificate candidates (all fail)
- `sq_pointwise.py` — ρ(D^{-1/2}A_L²D^{-1/2}) ≤ 1 formulation check, min arg46 > 0
- `coverage.py` — D2/D3 coverage; sympy identity checks inline in session log
- `scan_lamnorm.py` — λ-normalized two-piece/DHS-style φ scan (negative)
- `aintervals.py`, aint8_d2.tsv — per-graph working-exponent intervals + rule mining
- `leaves.py`, `leaves2.py`, `leaves9.py`, l9_*.log — leaf-case claims L1–L5, M

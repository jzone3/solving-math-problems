# P16 childF — Conjecture D1 (K ⪰ 0): a rigorous reduction to a vertex-space Z-matrix conjecture (F2)

Child session of runs/P16-v2 (builds on childD). Task: prove **Conjecture D1**:
for every connected graph G with δ(G) ≥ 2,

  K := diag(arg46(e)) − A_L² ⪰ 0,   arg46(ij) = 2(dᵢ²+dⱼ²) − 16dᵢdⱼ/(mᵢ+mⱼ) + 4.

Notation as in childD: R = unoriented incidence matrix (n×E), Q = D+A, A_L = A(L(G)),
σᵢ := dᵢ + mᵢ − 4. All numerics float64, tol 1e-8/1e-9, nauty-geng exhaustive.

**OUTCOME: no complete proof of D1 (and no counterexample). Main advance: a fully
rigorous, machine-verified REDUCTION of D1 to a new n-dimensional vertex-space
conjecture F2 about an explicit symmetric Z-matrix M(G), plus exhaustive
verification of F2 for all 9,808,209+197,772 connected δ≥2 graphs at n = 10, 9
(and all n ≤ 8), plus 4,000 random graphs to n ≈ 120. F2 ⇒ D1 is proved
unconditionally (Theorem F3 below), so the open core of Bound 46 (δ≥2 case) is
now the single n×n PSD statement F2.**

Everything in §§1–3 is proved; §4 is the new conjecture + verification; §5 is
what we tried against F2 and why it resists; §6 negative results; §7 files.

## 1. Lemma F1 (min arg46 ≥ 4 for δ ≥ 2; equality characterization)

For every edge ij of a connected graph with δ ≥ 2:  arg46(ij) ≥ 4, with equality
iff dᵢ = dⱼ = 2 and mᵢ = mⱼ = 2 (i.e. both endpoints and all their neighbors have
degree exactly 2).

*Proof.* Since δ ≥ 2, every neighbor of any vertex has degree ≥ 2, so mᵢ, mⱼ ≥ 2,
hence mᵢ+mⱼ ≥ 4. Sympy-verified identities (`verify_f2_reduction.py`, step 1):

  arg46 − 4 = (2/(mᵢ+mⱼ)) [ (dᵢ²+dⱼ²)(mᵢ+mⱼ) − 8dᵢdⱼ ], and
  (d²+e²)(x+y) − 8de = (x+y)(d−e)² + 2de(x+y−4).

With x, y ≥ 2 and de > 0 both summands are ≥ 0; both vanish iff d = e and
x + y = 4, i.e. x = y = 2. Finally mᵢ = 2 with δ ≥ 2 forces every neighbor of i to
have degree exactly 2; since j ∼ i this gives dⱼ = 2, and symmetrically dᵢ = 2. ∎

**Corollary F1′ (degenerate edges).** On every edge with arg46 = 4 we have
σᵢ = σⱼ = 0 (σ = d+m−4). Verified exhaustively for all 8,025 δ≥2 graphs n ≤ 8
(50 degenerate edges occur, all with d=m=2 at both ends; step 5 of the verifier).

## 2. The reduction machinery (all proved)

Fix any diagonal matrix D = diag(σ) (any real σ; we use σ = d+m−4) and ε ≥ 0.
Let a_e := arg46(e) − 4 + ε, and for a_e > 0 put w_e := 1/a_e; define

  H := R diag(w) Rᵀ  (n×n weighted signless Laplacian; on ε = 0 degenerate
  edges set w_e := 0 — legitimate because σ = 0 there kills every occurrence,
  see Corollary F1′),
  M(G) := 2D + 4I − Q − D H D.

### Theorem F3 (per-edge Young / completion-of-square): M ⪰ 0 ⇒ K ⪰ 0.
*Proof.* For any x ∈ R^E let X := Rx and b := Rᵀ(DX). Per-edge Young inequality
(a_e x_e² − 2x_e b_e + b_e²/a_e = a_e(x_e − w_e b_e)² ≥ 0) summed over edges gives

  Σ_e a_e x_e² ≥ 2 XᵀDX − XᵀD H D X            (identity + inequality machine-
                                                 verified, step 3 of verifier)
so with K_ε := diag(arg46+ε) − A_L² and the childD Lemma D0 factorization
K_ε = diag(a) − Rᵀ(Q−4I)R:

  xᵀK_ε x = Σ_e a_e x_e² − Xᵀ(Q−4I)X ≥ Xᵀ[2D + 4I − Q − D H_ε D]X = XᵀM_ε X.

Since w_ε(e) = 1/(arg−4+ε) ≤ w_0(e) edgewise and each edge contributes the PSD
rank-1 term w_e (σᵢXᵢ+σⱼXⱼ)(…)ᵀ to DHD, we get M_ε ⪰ M_0 =: M (step 4 of the
verifier; degenerate edges contribute exactly 0 for every ε by F1′). Hence
M ⪰ 0 ⇒ xᵀK_ε x ≥ 0 for all x and all ε > 0 ⇒ K = lim_{ε→0} K_ε ⪰ 0. ∎

Remarks.
- No pseudo-inverses, no range conditions, no irreducibility: the proof is a sum
  of per-edge scalar inequalities plus one PSD comparison. Every algebraic step
  is machine-verified (`verify_f2_reduction.py`: sympy step 1 exact; steps 2–4
  numeric on 300 random graphs; steps 5–6 exhaustive n ≤ 8).
- The identity Q d = d ∘ (d+m) (i.e. (Qd)ᵢ = dᵢ(dᵢ+mᵢ)) is what makes σ = d+m−4
  natural: on d-regular graphs D = 2(d−2)I, H = Q/(4d(d−2)) and
  M = (2d−2)(2I − Q/d) ⪰ 0 ⟺ ρ(Q) ≤ 2d, with equality exactly on bipartite
  regular graphs — so the reduction is TIGHT on the entire equality manifold of
  Bound 46 (it loses nothing there).

## 3. Structure of M: a symmetric Z-matrix with the sparsity of G

With σ = d+m−4 ≥ 0 (δ≥2):
  M_ij = −(1 + σᵢσⱼ w_ij) for ij ∈ E,  M_ii = 2σᵢ + 4 − dᵢ − σᵢ² Σ_{e∋i} w_e,
i.e. M is an n×n symmetric Z-matrix supported on G. Consequently (standard
M-matrix theory, for connected G): **M ⪰ 0 ⟺ ∃ h > 0 with Mh ≥ 0** — i.e. F2 is
equivalent to the existence of a positive "ground-state super-harmonic" vertex
vector h. Writing B := Q + DHD (entrywise nonnegative!) and T := 2σ + 4, the
certificate condition reads Bh ≤ T∘h, so F2 ⟺ ρ(diag(T)^{-1}B) ≤ 1 — a
Collatz–Wielandt problem for an explicit nonnegative matrix in VERTEX space.
This replaces childD's E-dimensional edge-space certificate problem (where all
13 natural candidates failed) by an n-dimensional one with explicit weights.

## 4. Conjecture F2 (the new crown statement) + verification

**Conjecture F2.** For every connected graph G with δ(G) ≥ 2:  M(G) ⪰ 0.

By Theorem F3, F2 ⇒ D1 ⇒ (childD Thm D1⇒46) ρ(Q) ≤ RHS46 ⇒ Bound 46 (δ≥2 case).

Verified exhaustively (`f2_check.py`, logs f2_9_*.log, f2_10_*.log):
- ALL 8,025 connected δ≥2 graphs 3 ≤ n ≤ 8: 0 failures;
- ALL 197,772 connected δ≥2 graphs n = 9: 0 failures;
- ALL 9,808,209 connected δ≥2 graphs n = 10: 0 failures (16-way geng split;
  worst min-eig ≈ −8e−15, i.e. zero to float noise — equality manifold);
- 4,000 random graphs (G(n,p), random-regular ± edge deletions, K_{a,b} minus
  edges, BA), pruned to δ≥2 cores, n up to ~120: 0 failures (`f2_rand.py`).

So F2 holds everywhere D1 has ever been tested, and D1's exhaustive range
(childD n ≤ 9, parent n = 10) is exactly reproduced THROUGH the reduction.

## 5. What resists in F2 (map for the next session)

The certificate h = d is remarkably good but not universal:
- With h = d the condition Bh ≤ T∘h reduces (via Qd = d∘(σ+4)) to the per-vertex
  inequality  σᵢ Σ_{j∼i} w_ij (σᵢdᵢ + σⱼdⱼ) ≤ σᵢ dᵢ,  which holds with EQUALITY
  on regular graphs and fails on only 627/8,025 graphs at n ≤ 8 (`f2 cw scans`).
  Failing vertices are exactly those with tᵢ := Σ_{j∼i}(σᵢ+σⱼ)w_ij > 1
  (max observed excess 13.5% at n ≤ 8) — high-σ vertices adjacent to low-σ ones,
  same "deficient" family childD identified.
- Power-iteration smoothing h = (diag(1/T)B)^K d certifies 8025−{627,72,15,5,2,2,1,1}
  graphs for K = 0..7 and ALL n ≤ 8 graphs at K = 8, so the ground state is
  reachable by finitely many local averaging steps — but no FIXED K can work for
  all n (equality graphs pin ρ = 1), and no closed form matched: h ∈ {1, m, σ,
  d^a m^b, d+c(m−2), d·f(t), Q-Perron u, u², u∘d, Perron(B), …} all fail on
  thousands of graphs (scan logs in session). As with childD finding 3, any
  closed-form h must coincide with the exact ground state on the equality
  manifold; h = d does (that is why it is the best local candidate).
- Local per-edge/per-vertex splits of M provably fail: allocating the diagonal
  of M over edges and demanding 2×2 PSD blocks fails already on regular graphs
  (slack must be routed globally); the Cauchy–Schwarz localization
  (σᵢxᵢ+σⱼxⱼ)² ≤ (σᵢ+σⱼ)(σᵢxᵢ²+σⱼxⱼ²), which would reduce F2 to t ≤ 1, is
  false on 7,512/8,025 graphs. The Dirichlet/global character of D1 survives
  in F2 — but now in n dimensions with all-explicit rational weights.
- Suggested attacks: (i) prove existence of h > 0 with Bh ≤ T∘h by a discrete
  maximum-principle / Allegretto–Piepenbrink argument on the weighted graph
  (B, T) exploiting σᵢ+4 = dᵢ+mᵢ and Qd = d∘(d+m); (ii) exploit the freedom in
  D: the feasible set {D diagonal : M(D) ⪰ 0} is convex and SDP-representable
  (Schur: [[2D+4I−Q, DR diag(√w)],[diag(√w)RᵀD, I_E]] ⪰ 0 is LINEAR in D), so
  one can OPTIMIZE the choice of σ per graph and learn a better closed form
  than d+m−4; (iii) interlacing on the ε-family M_ε, which is monotone in ε.

## 6. Negative results (routes killed this session)

1. **Diagonal splitting fails.** H ⪯ D̃ together with Q−4I ⪯ D̃^{-1} (D̃ diagonal)
   would give D1, and is tight on bipartite regular (D̃ = 2(d−2)I), but is
   INFEASIBLE for 5 graphs already at n ≤ 7 (min-max ≈ 1.0117 > 1 at FQjVO;
   `diag_split.py`). The two spectral factors cannot be decoupled by a diagonal.
2. **Dropping the helpful part of Q's spectrum almost works but fails.** The
   sufficient condition λ_max(Σ_{q_k>4}(q_k−4) v_k v_kᵀ) ≤ 1 (v_k =
   diag(1/√(arg−4))Rᵀu_k, Qu_k = q_k u_k) fails on exactly 3/8,025 graphs at
   n ≤ 8 (worst 1.0384 at G?r@d_): the eigenvalues q < 4 of Q contribute
   essential negative (helping) terms on the deficient family.
3. **Crude ρ(Q)-substitution fails badly**: (ρ(Q)−4)·λ_max(H) ≤ 1 fails on
   4,012/8,025 graphs (up to 4.5): the Perron alignment of Q vs H matters.
4. **Certificate ansatz y = diag(1/(arg−4+c)) RᵀZ** (edge certificate from a
   vertex vector) is LP-feasible for ALL n ≤ 8 graphs for c ∈ {0.5, 2}, but no
   closed-form Z was found (12+ candidates including Q-Perron all fail on
   1,343+ graphs). Superseded by the sharper F2 formulation.

## 7. Files

- `verify_f2_reduction.py` — machine verification of §§1–2 (sympy exact +
  numeric + exhaustive n ≤ 8); run output: ALL REDUCTION STEPS VERIFIED.
- `f2_check.py` — exhaustive F2 verifier; logs f2_9_*.log (197,772 graphs,
  0 failures), f2_10_*.log (9,808,209 graphs, 0 failures).
- `f2_rand.py`, f2_rand.log — random large-graph F2 stress test (4,000 graphs,
  0 failures).
- `diag_split.py` — negative result 1.
- `vertex_cert.py`, `ansatz_scan.py`, `shifted_scan.py` — certificate-ansatz
  scans (§6.4 and helpers used by the other scripts).

**Bottom line.** D1 (hence Bound 46, δ≥2 case) is now reduced, with a complete
machine-verified proof of the reduction, to Conjecture F2: an explicit n×n
symmetric Z-matrix M(G) = 2diag(d+m−4) + 4I − Q − diag(d+m−4)·H·diag(d+m−4) is
PSD for every connected δ≥2 graph — equivalently ρ(diag(2d+2m−4)^{-1}(Q+DHD)) ≤ 1,
a Collatz–Wielandt statement in vertex space, tight exactly on regular graphs
(bipartite regular for the full chain). F2 is verified for all ~10⁷ graphs
n ≤ 10 and random graphs to n ≈ 120. No counterexample to anything was found.

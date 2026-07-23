# P16 v2 — BHS Bounds 44 & 46 (literature-first / proof attempt + structured search)

Session: runs/P16-v2 branch. Variant V5-style (literature-first), per dispatch:
read arXiv:2606.14550 (Damnjanović–Ha–Stevanović, "Upper bounds for the Laplacian
spectral radius: Proofs and counterexamples", 12 Jun 2026 = DHS) and attempt a proof
via their Collatz–Wielandt technique; fall back to structured search.

## 1. Statement fidelity (verified against primary source)

Downloaded arXiv:2606.14550v1 PDF and extracted Table 2 verbatim. The **catalog file
`problems/P16-bhs-44-46.md` paraphrases both formulas INCORRECTLY** (it puts the
leading "2 +" inside the square root). The correct statements (DHS Table 2; original
numbering from Ghebleh–Al-Yakoob–Kanso–Stevanović, Discrete Appl. Math. 380 (2026),
bounds proposed by Brankov–Hansen–Stevanović, LAA 414 (2006)):

- **Bound 44**: μ(G) ≤ max_{ij∈E} [ 2 + √( 2((dᵢ−1)² + (dⱼ−1)² + mᵢmⱼ − dᵢdⱼ) ) ]
- **Bound 46**: μ(G) ≤ max_{ij∈E} [ 2 + √( 2(dᵢ² + dⱼ²) − 16dᵢdⱼ/(mᵢ+mⱼ) + 4 ) ]

Conventions (DHS Sec. 2): finite simple graphs without isolated vertices
(disconnected allowed; a violating component yields a connected witness); if a square
root argument is negative that edge term is −∞ (excluded from the max). dᵢ = degree,
mᵢ = average degree of neighbors.

Cross-check: our implementation of both RHS formulas agrees with the independent
implementation in Taewoo Ha's artifact repo (github.com/txh2120/bhs-counterexamples,
`src/exhaustive_bound_search.py`, lines for bounds 44/46) and with DHS Table 2.

Status per DHS Theorem 1.1: of the 68 BHS bounds, all are now settled EXCEPT 44
and 46 (22 proved + 12 refuted by DHS; 30 refuted by GAKS 2024; 2 refuted by
Taieb–Roucairol–Cazenave–Harutyunyan, LION 2025).

## 2. Priority check (mandatory scope, incl. artifact repos)

Searches performed 2026-07-23:
- arXiv API: "Laplacian spectral radius" + "upper bounds" recent; citations of
  2606.14550 via Semantic Scholar (0 citing papers found).
- GitHub: repo search "laplacian spectral radius bound" → only
  `Ivan-Damnjanovic/bhs-bounds` (DHS supplementary, last push 2026-06-28: README
  update only; scripts unchanged since 2026-06-05 — no post-paper resolution of
  44/46) and `txh2120/bhs-counterexamples` (Ha, 2026-03/04: refuted bounds
  11,13,40,45,48 — subsumed by DHS; 44/46 not refuted there).
- Zenodo API ("Laplacian spectral radius bound", most recent): nothing relevant.
- OpenReview search: nothing relevant.
- Exa web search ("BHS bounds 44 46 refuted/proved", June–July 2026): nothing
  beyond DHS itself.

Conclusion: Bounds 44 and 46 appear still open as of 2026-07-23. Residual risk:
private/unindexed work by the DHS authors themselves (their README edit of
2026-06-28 suggests ongoing attention).

## 3. Why these two are hard (proof-gap analysis)

Both bounds are **tight with equality exactly on bipartite regular graphs**:
for d-regular G, RHS(44) = RHS(46) = 2 + 2(d−1) = 2d = μ(G) when G is bipartite
regular. So no proof can lose anything on that manifold, and any counterexample
must beat the bound near it.

DHS proof techniques and why they fail here:
1. Max-degree-sum edge reduction (their Prop 3.4): at an edge maximizing dᵢ+dⱼ we
   have mᵢ ≤ dⱼ and mⱼ ≤ dᵢ. For Bound 44 this gives mᵢmⱼ ≤ dᵢdⱼ, i.e. the term at
   that edge can be BELOW dᵢ+dⱼ — reduction to Anderson–Morley fails. For Bound 46
   the term at that edge is ≥ dᵢ+dⱼ iff mᵢ+mⱼ ≥ 4dᵢdⱼ/(dᵢ+dⱼ); the a-priori lower
   bound mᵢ+mⱼ ≥ (s−1)s/p (s=dᵢ+dⱼ, p=dᵢdⱼ) is insufficient (fails already for
   dᵢ=dⱼ=d: deficit −8d(d−1)²/(2d−1) < 0). [We did verify the clean identity
   arg46−(s−2)² = (dᵢ−dⱼ)² + 4(s − 4p/(mᵢ+mⱼ)), which yields: **Bound 46 holds for
   any graph having a max-degree-sum edge with mᵢ+mⱼ ≥ 4dᵢdⱼ/(dᵢ+dⱼ)**.]
2. Perron two-vertex argument (their Prop 3.5): at the Perron-critical edge one
   gets ρ ≤ (dᵢ+dⱼ+√((dᵢ−dⱼ)²+4mᵢmⱼ))/2 and ρ ≤ dᵢ+mᵢ. Pointwise comparison with
   RHS(44)/RHS(46) FAILS on feasible local data (e.g. dᵢ=dⱼ=2, mᵢ=mⱼ=3/2: P4-like
   local data where the Perron bound is 3.5 but the 44-term is 2+√0.5 ≈ 2.71; P4
   itself is saved by its leaf edges whose term is 4). The obstruction is global:
   the max over edges is rescued by OTHER edges, which the local argument cannot see.
3. Collatz–Wielandt with concave φ (their Lemma 3.6) is inherently vertex-type;
   both open bounds are edge-type and not ≥ any of the proved vertex bounds
   pointwise. No natural φ found; the equality manifold (bipartite regular, where
   Qv = 2d·v needs v constant on sides) forces φ to be constant-like there, and
   first- AND second-order expansions of gap around regular data vanish (computed:
   for both bounds, homogenized leading term and the O(1) correction cancel exactly
   at dᵢ=dⱼ=mᵢ=mⱼ=d), so any proof must control third-order behavior. We did not
   find such a proof.

## 4. Structured search for counterexamples (all negative so far)

All search code in this directory; floats for screening only, tolerance 1e-9;
any candidate would go through `verify_p16.py` (exact rationals + Sturm; no floats
on the accept path; self-tested).

1. **Exhaustive**: all connected graphs n ≤ 10 via nauty-geng (1 + 2 + ... =
   12,293,443 graphs total: 273,192 for n≤9 plus 11,716,571 for n=10), both bounds:
   **no violation**. Minimum gap 0 (equality) attained exactly at bipartite regular
   graphs (e.g. g6 `EFz_` = K_{3,3}); smallest nonzero gaps ~0.02.
2. **Trees**: all trees n ≤ 17 via nauty-gentreeg: no violation (see trees.log).
3. **Equitable-partition quotient search** (the family from which ALL DHS
   refutations came): random restarts + hill-climbing + simulated annealing over
   k×k nonnegative-integer quotient matrices, k ∈ {2,...,5}, entries ≤ 400–500,
   symmetrizability + Lemma 2.3 realizability enforced, score = λ_max(L_B) − RHS
   computed from cell data (Lemma 2.2 certificate). Runs: quotient_search.py,
   anneal_quotient.py, seeded_anneal.py (seeded at the tightest DHS Table-3
   counterexample quotients and K_{d,d}−e quotients). **No violation**; best
   reachable gap → 0 only along regular-bipartite equality configurations.
4. **Targeted families near the equality manifold**:
   - K_{d,d} − e, d up to 320 (4-cell quotient): gap ↓ 0⁺ like Θ(1/d) but positive
     (d=320: gap44 ≈ 0.0031, gap46 ≈ 0.0062). Tightest known non-equality family.
   - K_{d,d} minus an (r,s)-biregular graph between p+q chosen vertices (4-cell
     quotient), full sweep p,q ≤ 30, d ∈ {10,...,320}: minimum gap is always the
     p=q=r=s=1 case (K_{d,d}−e). No violation.
   - Sparse random bipartite d-regular ± edge/pendant (n up to 96): no violation;
     minus-edge gap ↓ 0⁺ with n.
   - All 10 DHS Table-3 counterexample quotients (which refute OTHER bounds)
     satisfy 44 and 46 (smallest gap: 0.131 for their bound-24 graph, cells
     (69,19,76)).

## 5. Encodings / compute log

- RHS/eigen screening: numpy eigvalsh on L (float64); quotient spectra via
  eigenvalues of L_B (real by symmetrizability).
- Realizability: Lemma 2.3 (DHS) — cell sizes from symmetrizing ratios, parity fix
  by even scaling; implemented in search_common.quotient_ok.
- Exhaustive n=10 parallelized 16-way via geng res/mod (~30 min wall on 8 cores).
- Annealing/hill-climb: ~10⁶–10⁷ quotient evaluations per bound across runs
  (see qs44.log, an44.log, an46.log, sa44.log, sa46.log).
- Exact verifier: sympy charpoly + count_roots (Sturm) over Q; edge-term
  comparison via (λ_lo−2)² > arg with rational arg.

## 6. Outcome

**Negative result (no resolution).** No counterexample to Bound 44 or Bound 46
found in: all connected graphs n ≤ 10, all trees n ≤ 17, extensive equitable-
partition quotient search (k ≤ 5) including annealing seeded at every known tight
configuration, and targeted near-bipartite-regular families up to degree 320.
No proof found either; the precise obstruction to each DHS technique is documented
in §3, including one new conditional positive result (§3.1 criterion for Bound 46)
and the observation that both bounds are exactly tight on bipartite regular graphs
with the gap vanishing to second order around regular local data — which explains
why both MC search (Taieb et al.) and DHS's methods left exactly these two open.

Suggested next steps for future runs: (a) third-order perturbation analysis around
the bipartite-regular manifold in quotient space to either extract a violating
direction or prove local validity; (b) Lean-style case analysis combining Merris +
Perron edge constraints with global counting (Σᵢ dᵢmᵢ = Σ_{ij∈E}(dᵢ+dⱼ)) to bound
how many edges can simultaneously have depressed terms; (c) larger-k quotient SAT/
ILP encoding with λ_max as an eigenvector-certificate variable.

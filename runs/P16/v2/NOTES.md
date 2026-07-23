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
Note the canonical numbering of the 68 bounds comes from Ghebleh–Al-Yakoob–Kanso–
Stevanović (DAM 380, 2026; paywalled — residual risk); DHS Table 2 and Ha's repo are
two independent sources agreeing on the formulas for #44/#46, which we treat as the
authoritative statement.

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

## 4. Structured search for counterexamples (all negative)

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
   computed from cell data (Lemma 2.2 certificate). Runs: quotient_search.py
   (61,448 hill-climb restarts, bound 44), anneal_quotient.py (30 min each bound;
   9,056 / 9,207 annealing restarts), seeded_anneal.py (30 min each bound; 4,960 /
   5,215 chains seeded at the tightest DHS Table-3 counterexample quotients and
   K_{d,d}−e quotients). **No violation**; minimum gap found ~ −6e-13 = float noise
   exactly on regular-bipartite equality configurations (e.g. 4-cell bipartite
   205-regular quotient), never genuinely below.
3b. **Continuous relaxation over quotient space** (continuous_opt2.py): minimize
   gap over CONTINUOUS B = diag(n)^{-1}S (S symmetric, n > 0) with the
   realizability-faithful constraint that every present entry of B is ≥ 1, per
   support pattern, Nelder-Mead multistart. Integer quotients are a subset, so a
   nonnegative infimum rules out ALL certificates with that cell count regardless
   of entry size. Result for k = 2 (both bounds): min gap −5.7e-14 ≈ 0, attained
   only at regular bipartite ⇒ numerically, **no 2-cell equitable-partition
   certificate can refute either bound**. k = 3: minima also ≈ 0 (−6e-5 outlier for
   bound 44 occurred at entries ~1e10 where float eigensolves have ~1e-15 relative
   error — noise, not a candidate; a first, buggy relaxation without the ≥ 1
   constraint produced spurious "negative" points with fractional edges — recorded
   as a warning for future runs).
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

Additional small observation (Bound 46 −∞ convention cannot bite globally): an
edge term of Bound 46 is undefined (arg < 0) only if mᵢ+mⱼ < 4−O(1/d²) at
degrees ~d, which forces a degree-1 neighbor; but any leaf edge (dⱼ = 1) has
arg = 2dᵢ²+6−16dᵢ/(mᵢ+dᵢ) > 0 for dᵢ ≥ 2. So every graph with an edge has at
least one well-defined Bound-46 edge term; the −∞ convention never yields a
trivial counterexample.

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
found in: all connected graphs n ≤ 10 (12,293,443 graphs, incl. 11,716,571 at
n = 10), all trees n ≤ 17, ~2×10⁴ annealing chains / 6×10⁴ hill-climb restarts
over equitable-partition quotients (k ≤ 5, entries ≤ 500) seeded at every known
tight configuration, targeted near-bipartite-regular families up to degree 320,
and a continuous relaxation showing (numerically) that no 2-cell quotient
certificate exists at all.
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

## 7. Escalation round (same session, continued; + three child sessions)

All three suggested next steps above were executed (this session + children).
Everything remained NEGATIVE for a counterexample; substantial new partial results
toward a PROOF were obtained (both bounds increasingly look TRUE).

Local (this branch):
- k ≤ 8 quotient annealing, entries ≤ 3000, 45 min/bound (`anneal_quotient8.py`,
  an44_big.log/an46_big.log): min gap −3.1e-13 (float noise at 101-regular bipartite
  equality configs). 12k restarts per bound.
- Realization search (`realization_search.py`, real44/46.log): 2.1M random
  near-regular bipartite graphs (configuration model + up to 8 edge flips,
  d ≤ 30, n ≤ 90) — rationale: μ(G) of a realization can exceed the quotient
  eigenvalue used by all prior lower bounds. Best gap −8.9e-15 (noise). Negative.
- k = 4 continuous relaxation (cont2_44_4.log/cont2_46_4.log): only ill-conditioned
  float artifacts (entry ~1.2e9, relative error 1e-15 scale); no valid negative.
- **Stronger statement verified at n = 10**: ρ(Q) ≤ RHS44 and ρ(Q) ≤ RHS46 for ALL
  11,716,571 connected graphs on 10 vertices (`rho_n10.py`, rho10_*.log). Combined
  with childB's n ≤ 9 check, the signless-Laplacian strengthening holds for all
  connected graphs n ≤ 10.
- One-breakpoint piecewise-linear φ (min(x, c+t(x−c))) in childB's edge-CW lemma is
  NOT sufficient: 1420 (B44) / 1740 (B46) failures on n ≤ 8 — the φ-rule needs to be
  richer than a single breakpoint family.

Child sessions (branches merged here):
- `runs/P16/v2/childA/` (branch runs/P16-v2-childA): exact symbolic perturbation
  analysis around the equality manifold. Closed forms: (d,d+c)-biregular has
  arg44−(μ−2)² = c² and arg46−(μ−2)² = c²(c+2d+4)/(c+2d) → positivity proved for the
  whole family. K_{d,d} minus matching: gap t/d − 5t/d² + … > 0. Near-perfect
  matching: a genuinely NEGATIVE edge-term series exists (−u/d for B44) but other
  edges rescue at O(1) — pinpoints exactly what a counterexample would need.
  219,204 exact instance evaluations of 4/6-cell perturbed quotients at d ∈
  {50,200,1000}: none negative.
- `runs/P16/v2/childB/` (branch runs/P16-v2-childB): NEW edge-type Collatz–Wielandt
  lemma on the line graph (μ ≤ ρ(Q) ≤ max_{ij∈E}[dᵢφ(mᵢ)/φ(dⱼ)+dⱼφ(mⱼ)/φ(dᵢ)] for
  concave φ>0), a new valid one-parameter bound family sharp on bipartite regular,
  checkable sufficient conditions C44/C46 via second-order Perron localization on
  the line graph, proof of both bounds for all (r,s)-semiregular bipartite graphs,
  and the key empirical facts: a per-graph concave φ certifies BOTH bounds on every
  connected n ≤ 8 graph (0/12,112 failures), and a power φ certifies Bound 46 on
  every δ ≥ 2 graph n ≤ 9. No universal φ exists (pointwise proofs impossible; the
  max-vs-max slack is essential). Full writeup in childB/NOTES.md.
- `runs/P16/v2/childC/` (branch runs/P16-v2-childC): large-scale search in new
  regimes — ~86M graphs at n = 11 (all bipartite; degree windows [1,5], [2,5],
  [3,6]) with min gap44 = 0.046; CP-SAT eigenvector-certificate (Collatz–Wielandt)
  quotient search k = 4..10, entries ≤ 150, ~2h solver time, 0 feasible; bipartite
  overlays n ≤ 120; continuous relaxation k = 4..8 with all 18 float-negative
  points refuted at 60-digit precision (all cancellation noise at entry scales
  1e9–5e16). No violation anywhere. See childC/NOTES.md.

Bottom line after escalation: still **no counterexample and no complete proof**; the
strengthened conjecture ρ(Q) ≤ RHS holds exhaustively to n = 10, positivity is proved
exactly for every structured family analyzed, and the most promising proof program
(childB §3: rule G ↦ φ_G in the edge-CW lemma + leaf case analysis) is documented.

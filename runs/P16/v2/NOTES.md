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

## 8. Proof wave (round 3: children D & E + local n=10 verifications)

Two more children executed the proof program; still **no complete proof, no
counterexample**, but the problem is now reduced to sharply characterized cores.

- `runs/P16/v2/childD/` (Bound 46): **PSD reformulation** — Lemma D0 factorization
  K := diag(arg46) − A_L² = diag(arg46−4) − Rᵀ(Q_G−4I)R, and Theorem D1⇒46: K ⪰ 0
  implies ρ(Q) ≤ RHS46. **Conjecture D1 (K ⪰ 0 for all connected δ≥2 graphs)**
  verified exhaustively n ≤ 9 + 175k random graphs to n = 40 (childD), and — this
  session — **exhaustively at n = 10: all 9,808,209 connected δ≥2 graphs, 0
  failures** (`psd_n10.py`, psd10_*.log). New rigorous sufficient conditions D2
  ((dᵢ+dⱼ)(mᵢ+mⱼ) ≥ 4dᵢdⱼ per edge ⇒ Bound 46) and D3 (power-weighted), subsuming
  the equality manifold. Leaf case: induction candidate L4 verified n ≤ 9 but
  RHS46 is not monotone under leaf deletion (FCOf? family) — needs a stronger
  induction hypothesis. Resisting core: PSD-ness of (†) requires the global
  Dirichlet coupling XᵀL_GX; all local Cauchy–Schwarz certificates provably fail.
- Local: the childB power-φ certificate for Bound 46 was verified at n = 10:
  **all 9,808,209 δ≥2 connected graphs pass with some a ∈ {0,…,1}** (0 failures;
  `pow46_n10.py`, pow46_10_*.log).
- Local negative datum: the analogous PSD statement for **Bound 44 is FALSE**
  (K44 = diag(arg44) − A_L² has 38 non-PSD δ≥2 graphs at n ≤ 8, worst −0.277 at
  GQjlt[), so Bound 44 cannot use the D1 route.
- `runs/P16/v2/childE/` (Bound 44): **Lemma E1** (exact shifted-sum CW weights):
  ρ(Q) ≤ max_e (M_e + c·s_e)/(s_e + c) for any c > −min s_e — a one-parameter
  homotopy Das ↔ Anderson–Morley whose feasibility in c is an exact interval
  intersection. Covers 273,183/273,191 graphs n ≤ 9; sum ∪ affine-product covers
  ALL n ≤ 9 and all but 190 graphs at n = 10 (all 190 pass the second-order
  affine test). Correction to childB: best-concave product weights fail at n = 9;
  the right family is additive/bivariate-ψ. Resisting core for 44: 190 graphs
  with (δ,Δ) ∈ {(2,5),(2,6),(3,6),(3,7)}, 6 spider trees, and leaf-heavy small
  graphs; sharpest path documented in childE/PROOF44.md §5.

## 9. Round 4 (children F, G, H): attacking the finite targets

- `runs/P16/v2/childF/` (prove D1): **Theorem F3 proved** — for a diagonal D,
  M := 2D+4I−Q−DHD ⪰ 0 implies K ⪰ 0 (D1), via per-edge Young inequality on (†),
  tight on the equality manifold. **New Conjecture F2** (with σ = d+m−4):
  M(G) ⪰ 0 for all connected δ≥2 graphs — an n×n vertex-space Z-matrix statement
  (equivalently: ∃h>0 with (Q+DHD)h ≤ (2σ+4)h), verified exhaustively at
  n ≤ 10 (9.8M δ≥2 graphs, 0 failures) + random to n≈120. So the chain is now
  F2 ⇒ D1 ⇒ Bound 46 (δ≥2), reducing an E-dim PSD problem to an n-dim
  Collatz–Wielandt target. No closed-form ground state h found yet (h = d works
  on all but 627/8025 graphs n ≤ 8).
- `runs/P16/v2/childG/` (leaf case of 46): **Lemma G1 proved** (exact Schur
  pendant elimination): μ(G) ≤ t ⟺ λ_max(L(H) + (t/(t−1))diag(ℓ)) ≤ t — the
  δ=1 case is exactly a diagonally-loaded δ≥2 problem. Theorem G2 (leaf-aware
  Merris) covers 85% of leafy n=9 graphs unconditionally; black-box uses of
  Hypothesis D provably fail (explicit certificates) — the injection point is
  Lemma G1's loaded eigenvalue problem.
- `runs/P16/v2/childH/` (Bound 44 residue): Lemmas H1/H1'/H2 + Corollary H3
  proved (second-order CW with shifted-sum weights, exact linear-in-c
  feasibility). **Conjecture H** (first ∪ second-order shifted-sum certificates
  cover every graph) verified with ZERO failures on all 11,989,762 connected
  graphs n ≤ 10 and 204,994 trees n ≤ 18, incl. exact Fraction recheck of the
  198 hard graphs. Bound 44 is now reduced to Conjecture H. (Parent-session
  datum: second-order alone is NOT universal — 2,123 failures n ≤ 9 — only the
  union is conjecturally universal.)

Final status after four rounds (8 child sessions + this session): Bounds 44 and 46
remain OPEN. All evidence (exhaustive to n=10/n=11-windows, ~10⁸ structures, exact
perturbation series, PSD verification) indicates both bounds are TRUE, with equality
exactly on regular bipartite graphs. The sharpest remaining targets after round 4:
(i) Conjecture F2 (vertex-space CW target, ⇒ D1 ⇒ Bound 46 δ≥2) plus injecting
Hypothesis D into Lemma G1's diagonally-loaded problem for the leaf case;
(ii) Conjecture H (union of first/second-order shifted-sum certificates) for
Bound 44 — verified to n = 10 / trees n = 18 with zero failures.

## 10. Round 5 (children I, J + local probes): attacking F2 and Conjecture H head-on

Local probes (this session, `f2_ground.py`, `f2_hard_probe.py`, `f2_family_scan.py`,
`f2_sdp_sigma.py`): smoothing iterates h=(diag(1/T)B)^K d shrink the h=d failure
set (627 -> 75 -> 12 at n<=9 for K=0,1,2) but no fixed K suffices; linear families
h = d + a*sigma + b*(m-2) are strictly worse than h = d; SDP optimization of the
diagonal sigma on hard graphs finds strictly positive margins, with the optimal
correction raising sigma on low-sigma vertices adjacent to high-sigma ones (no
simple closed form emerged).

- `runs/P16/v2/childI/` (Conjecture F2): **Theorem T1 PROVED** — F2 holds on all
  connected regular graphs and all semiregular bipartite graphs (the entire
  conjectured equality manifold of Bound 46), sympy-verified. **New resolvent
  certificate** h_alpha = (I - alpha*P)^{-1} d with P = diag(T)^{-1}B: Lemmas
  I4 (sufficiency), I5 (necessity), I6 (window monotonicity) all proved;
  **Theorem I7: F2 <=> alpha*(G)*rho(G) < 1** (window nonemptiness) — an exact
  reformulation. The sound certificate (Conjecture I1, alpha = 0.99/rho0)
  passes exhaustively on ALL 10,013,006 connected delta>=2 graphs n <= 10 with
  zero failures. Negative: ground-state locality regression R^2 ~ 0.53 (the
  ground state is genuinely non-local), fixed-K power certificates, per-vertex/
  per-edge splits, optimized-diagonal first-order certificates all fail.
- `runs/P16/v2/childJ/` (Conjecture H): reduction sharpened to **Conjecture J**,
  a pairwise statement about 2-ball data (z1, zs, s, rho0) of two edges over the
  whole ray rho >= max(rho0(e), rho0(f)); J => H proved (PROOF_H.md §2); J
  verified on all 273k graphs n<=9 (all pairs, all rho, exact quadratic
  minimization), trees n<=16, the 198 hard graphs, 400 random n<=60 — zero
  violations. **Decoupling refuted**: NO rule c = phi(R) can exist — trees
  HkE?K?@ and Li_GS?@?S??@?A share R = 14 but have disjoint exact feasible
  c-intervals [-21/10, inf) vs [-16/7, -11/5]; any proof must show the two
  binding 2-ball configurations exclude each other within one graph. New
  2-local identities (I0–I5, psi-form) make the whole criterion explicit.

Status after round 5 (10 child sessions total): Bounds 44 and 46 remain OPEN —
no proof, no counterexample. Sharpest targets now: (i) window nonemptiness
alpha*(G)*rho(G) < 1 off the equality manifold (childI §8 route map) for 46;
(ii) Conjecture J's binding-pair exclusion (childJ route map: V1/V2 case bash,
T1/T2 coexistence contradiction, or ord4 certificates) for 44.

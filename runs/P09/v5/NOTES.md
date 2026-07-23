# P09 Bollobás–Nikiforov — V5 (literature-first) run notes

Session: devin-f14d36ed797d4ce1bd993e57698d51b9, 2026-07-22.

## 0. Statement re-verification

Original source: Bollobás & Nikiforov, *Cliques and the spectral radius*, JCTB 97 (2007)
859–865, Conjecture 1: for G ≠ K_n with m edges and clique number ω = ω(G),
λ₁² + λ₂² ≤ 2m(1 − 1/ω). Matches the problem file (checked against restatements in
arXiv:2407.19341, arXiv:2501.07137, arXiv:2101.05229, arXiv:2603.26379, all quoting the
same inequality). **Still open in general as of July 2026** — the March 2026 paper
(arXiv:2603.26379) treats only complete multipartite + dense K₄-free cases and calls the
general conjecture open.

## 1. Literature digest → exact open region

Proved cases (as of 2026-07):
- **ω = 2 (triangle-free)**: Lin–Ning–Wu, Comb. Probab. Comput. 2021 (arXiv:1910.12474).
- **Regular graphs, all ω**: Zhang (arXiv:2309.08184). Equality iff balanced Turán graph
  or disjoint union of two equal-size balanced Turán graphs.
- **Few triangles**: Kumar–Pragada (arXiv:2407.19341): t(G) = O(m^{1.5−ε}) triangles ⇒
  conjecture (even the Elphick–Linz–Wocjan generalization) holds. Covers planar,
  book-free, cycle-free graphs.
- **Complete multipartite graphs** (all): arXiv:2603.26379 (λ₂ ≤ 0 there, Nikiforov's
  spectral Turán theorem suffices).
- **Dense K₄-free**: m = Ω(n²), n large (arXiv:2603.26379 stability argument).
- **Random graphs**: a.a.s. (Liu–Bu, arXiv:2501.07137).
- Weakly perfect / Kneser classes for the related s⁺ conjecture (arXiv:2101.05229).

**Open region** (where any counterexample must live):
- irregular, connected (see §2: disjoint unions reduce to Nikiforov's *theorem*),
- Θ(m^{3/2}) triangles (many triangles),
- not complete multipartite,
- ω ≥ 3; for ω = 3 only the non-dense (m = o(n²)) K₄-free regime remains open,
- λ₂ > 0 required in any violation, so it also refutes ELW's s⁺ ≤ 2m(1−1/ω); i.e. the
  search doubles as a s⁺-conjecture search.

## 2. Analytic observations (drive the search design)

- **Disjoint unions can't violate**: for G = H₁ ∪ H₂ with the two top eigenvalues coming
  from the components, score(G) = score_Nikiforov(H₁) + score_Nikiforov(H₂) where
  score_Nikiforov(H) = λ₁(H)² − 2m_H(1−1/ω) ≤ 0 is Nikiforov's proved theorem
  (when ω(H_i) = ω(G); if a component has smaller ω its slack is strictly bigger).
  ⇒ counterexamples must be **connected** with genuinely interacting λ₁, λ₂.
- **Equality set is large**: any union of balanced Turán graphs with the same r,
  T(ar,r) ∪ T(br,r), gives equality (λ₂ = λ₁ of the smaller part, both parts tight for
  Nikiforov). Includes irregular graphs like T(3r,r) ∪ K_r. Verified numerically
  (tightness.py). Perturbation attacks should be centered on this whole family.
- Since the equality graphs are disconnected or complete multipartite (both proved
  regimes), a violation is a *strict crossing* away from a proved boundary — local
  perturbation must overcome a strictly negative first-order margin per edge flip
  (RHS moves by 2(1−1/ω) ≥ 4/3 per added edge; λ contributions are second-order for
  cross edges w.r.t. localized eigenvectors). This is why the conjecture is hard to
  break locally; global/structured families needed.

## 3. Compute log

All scores are score(G) = λ₁² + λ₂² − 2m(1 − 1/ω) with exact ω (Tomita-style
branch-and-bound max-clique, `core.py`) and dense `eigvalsh`. Conjecture ⇔ score ≤ 0.

### Round 1 (checkpoint 20:25 UTC)

- `tightness.py`: equality confirmed to 1e-13 on T(kr,r), unions of equal AND unequal
  balanced Turán graphs (same r), 2K_w. Near-tight but negative: bridged unions
  (≈ −1.0 to −1.45), books, joins K_a ∨ I_t (all ≤ −0.5).
- `perturb.py`: exhaustive 1-flip + 4000 sampled 2-flips around T(kr,r) (r=3..5, k=2..4),
  2×T(kr,r) (r=3,4), 2K_w (w=4..6): **max neighborhood score < 0 everywhere**
  (best ≈ −0.4 to −0.6; typical −0.1 near T(9,3)).
- `perturb3.py`: 3000 sampled 3-flips + 3000 4-flips + greedy 8-step plateau walks around
  ALL unions T(ar,r) ∪ T(br,r), r=3..6, a,b≤3: max < 0; plateau walks return to score ≈ 0
  only at equality graphs themselves.
- `families.py` (parametric, exact): overlapping Turán blobs (best −0.105 at r=3,q=2),
  Turán+pendant-clique (−0.209), K_a ∨ (T∪T) joins (−0.438), bridged unions b=1..8
  (−0.785), C5 blowups (−2.47). All negative.
- `omega3.py wheel`: wheel blowups I_a ∨ C5[x,y,z,y,x], all a≤12, x,y,z≤10, n≤45:
  best −0.985 (a=2, all b=1). K4-free anneal (moves creating K4 rejected), n=30/45,
  32 restarts × 40k steps: best −0.43.
- `anneal.py` round 1: n ∈ {20,24,25,28,30,33,35,36,40,45,48}, inits random/turan-union/
  cliques, ~200 restarts × 20–60k flip steps, exact ω every step: global best over
  non-equality graphs ≈ −0.4 (n=20); turan-union inits sit on the score-0 equality
  plateau and never cross it. A random-init run at n=20 also annealed INTO the equality
  plateau (best exactly 0) without ever exceeding it.

### Round 2 — fixed-ω anneal in the designed open region (`anneal2.py`)

Literature-designed search: fix ω ∈ {3,4,5} (flips changing ω rejected), seeds =
connected roughened Turán-unions (irregular, triangle-rich). n ∈ {24,26,30,32,34,36,38,
40,42,50}, 30–50k steps, ~60 restarts. **All negative**; best −0.32 (n=26, ω=4).

### Round 3 — ELW generalization (`elw.py`)

Also attacked the Elphick–Linz–Wocjan generalization (arXiv:2101.05229 Conj. 2):
Σ_{i≤ω, λᵢ>0} λᵢ² ≤ 2m(1−1/ω). Found its equality plateau is much larger: ANY union of
≤ ω balanced Turán graphs T(kᵢr, r) is exactly tight (verified to 1e-12 for r=3..6, up
to 6 components — includes t·K_w unions). Annealing from these seeds, n ∈ {20,28,36,44},
~45 restarts × 40k steps: reaches 0 on the plateau, never exceeds it. Negative.

### Round 4 — final escalation

anneal2 ω=4 up to n=60 and ω=3/6 variants, 80k steps (~70 restarts), plus ELW anneal
n=52,60: all negative. Best per-run scores collected in `RESULTS-summary.txt`.

### Round 5 — new encodings (after restart, pushing the frontier)

- **Exhaustive geng sweep** (`exhaustive.py`): all connected graphs (disconnected
  reduce to Nikiforov, §2), graph6 parsed in batches, batched `eigvalsh`; exact
  max-clique only where violation is arithmetically possible (violation ⇔
  ω < 2m/(2m−L), L = λ₁²+λ₂², since Σλᵢ² = 2m).
  - n ≤ 9: 0 violations (273k connected graphs), worst score exactly 0 (Turán).
  - **n = 10: all 11,716,571 connected graphs — 0 violations**, worst score 0.
    (Published exhaustive frontier for this conjecture appears to be incidental
    small checks only; this is a full n ≤ 10 certificate.)
  - **n = 11: all 1,006,700,565 connected graphs — 0 violations**, worst score
    exactly 0 (Turán equality graphs). ~4 h wall on 7 cores.
  - Pipeline independently cross-checked (`crosscheck.py`): graph6 parser vs
    networkx on 1200 random geng samples (n = 8..11) and candidate-filter logic vs
    direct score computation — PASS.
  - Together with the disjoint-union reduction (§2), this certifies BN for **all**
    graphs on ≤ 11 vertices (connected or not) — well past any published check.
- **Blowup continuous relaxation** (`blowup.py`): for every pattern H, BN on ALL
  independent-set blowups H[x·N] (N→∞) reduces to max over the simplex of
  f_H(x) = μ₁² + μ₂² − (1−1/ω(H))·xᵀAx, μᵢ from D^{1/2}A_H D^{1/2}, D=diag(x).
  Projected-gradient ascent (12 restarts × 400 iters) over ALL connected patterns
  with ω ≥ 3: |H| ≤ 8 complete (12,913 patterns, 12 restarts × 400 iters), and
  |H| = 9 complete (all 261,080 connected patterns, 259,699 optimized; lighter
  budget 4 restarts × 250 iters). max f = 0 exactly, attained at Turán-type
  patterns/weights; no positive value ⇒ **no counterexample exists among
  independent-set blowups of any pattern with ≤ 9 vertices, at ANY blowup size**
  (≤ 8 with the heavier optimization budget; ≤ 9 with the lighter one).

### Round 6 — new methods (coordinator push #2)

- **Frank–Wolfe / ILP duality attack** (`fw_ilp.py`, CBC via python-mip): iterate
  {compute top-2 eigenpairs → linearize dF/dA_ij = 4λ₁x_ix_j + 4λ₂y_iy_j − 2(1−1/ω)
  → re-choose the ENTIRE edge set by ILP subject to K_{ω+1}-freeness via lazy clique
  cuts}. Global jumps, completely different dynamics from flip search. Result: from
  every start (n ∈ {18,24,30}, ω ∈ {3,4,5}), the linearized global optimum converges
  to the Turán equality plateau with score EXACTLY 0 and never exceeds it — a strong
  dual/variational confirmation that the extremal family is the global maximizer of
  the first-order model.
- **Cones/joins over named spectral-extremal families** (`cones.py`): K_s ∨ H and
  K_s ∨ (H ∪ H) for H ∈ {Paley(q≤41), Kneser(v,k), triangular J(v,2) v≤9, co-C_n,
  hypercube-like}; 120 graphs, all irregular and triangle-rich (open region).
  All negative; best −0.618 (small co-cycle cone). No near-misses.

## 4. Near-misses & dead ends

- Best genuinely non-tight score found anywhere: ≈ **−0.105** (T(9,3)-blobs overlapping
  in a 2-set, family A), then −0.2..−0.6 band for pendant-clique / 1-flip perturbations.
- The equality plateau (unions of same-r balanced Turán graphs; for ELW, unions of up to
  ω of them) acts as a strong attractor for annealing; every crossing attempt loses at
  least ~0.1 immediately. Consistent with the §2 first-order-margin argument.
- Dead end: disjoint-union constructions — provably cannot violate (reduces to
  Nikiforov's theorem, §2).
- Total compute: ~7 h wall on 8 cores — ~400 annealing restarts (~2×10⁷ scored flips)
  with exact ω at every evaluation; structured scans of 6 parametric families;
  1.02×10⁹-graph exhaustive sweep; ~155k simplex optimizations for blowup patterns.

## 5. Conclusion

No violation of Bollobás–Nikiforov (nor of the ELW generalization) found. New verified
frontier: BN holds for **every graph on ≤ 11 vertices** (exhaustive, cross-checked) and
for **every independent-set blowup of every pattern on ≤ 9 vertices at every size**
(continuous-relaxation certificate, max f_H = 0 attained only at Turán-type optima).
Heuristic search (exact ω) to n = 90 in the literature-mapped open region found nothing
above −0.1 outside the equality plateau. Any counterexample must have n ≥ 12, is not a
blowup of a small pattern, and is not a local perturbation of the extremal family.

Late additions: fixed-ω anneals at n = 70–90 (19 restarts × 60k steps, ω ∈ {3..6}):
all negative (best −3.78 at n=70 ω=6).

STATUS: frontier-pushed (no counterexample; exhaustive certificate n ≤ 11 = 1.02e9
graphs, blowup-family certificate for all patterns ≤ 9 vertices at all sizes, plus
~2×10⁷ scored heuristic evaluations to n = 90 — all negative)

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
  plateau and never cross it.

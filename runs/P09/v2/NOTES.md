# P09 — Bollobás–Nikiforov — Variant V2 (structured two-eigenvalue design)

Session: https://app.devin.ai/sessions/00bbfc32f7bf4cc68f8ae50996b738a4
Branch: runs/P09-v2 (off devin/1784749757-context-plan)

## Statement re-verification (against original source)

Conjecture 1, Bollobás & Nikiforov, "Cliques and the spectral radius", JCTB 97 (2007):
for every graph G ≠ K_n with m edges and clique number ω,
λ₁² + λ₂² ≤ 2m(1 − 1/ω).
Cross-checked verbatim against arXiv:2407.19341 (Kumar–Pragada 2024) and
arXiv:2603.26379 (Giacomelli 2026), both quoting the same inequality. Confirmed
**still open in general as of July 2026**: partial results only — triangle-free
(Lin–Ning–Wu 2021), line graphs / not-too-many-triangles (2024), a.a.s. random
graphs (arXiv:2501.07137, 2025), complete multipartite + dense K₄-free
(arXiv:2603.26379, 2026), weighted spectral Turán consequences (arXiv:2510.26410).

score(G) := λ₁² + λ₂² − 2m(1 − 1/ω); violation ⇔ score > 0.

## V2 approach

Violations need TWO large eigenvalues ⇒ two-near-clique structure. We search
structured families whose spectra reduce to small quotient matrices (exact) or
tiny dense eigenproblems:

1. **Blow-up sweep** (`search_blowup.py`): every pattern graph F on ≤ 6 (then 7)
   vertices (networkx atlas, all iso classes), every type assignment
   {clique, independent-set}^k, integer weights hill-climbed (multi-restart) up
   to n = 240. λ₁, λ₂ exact from the k×k equitable-partition quotient (remaining
   eigenvalues are −1/0); ω exact from max weighted clique of F. This class
   contains: unions of cliques, joins, books K_p ∨ qK₁, complete split graphs,
   complete multipartite, kites, C₅-blowups, double-clique + apex cones, etc.
2. **Bridged cliques** (`search_bridge.py`): K_a ∪ K_b (a,b ≤ 30) plus bridge
   patterns not expressible as blow-ups: matchings (all t), stars, random
   bipartite bridges, double kites (cliques joined by paths, L ≤ 7), overlapping
   cliques (sunflowers). Exact ω via branch-and-bound; numpy eigvalsh.
   17,106 graphs.
3. **Structure-seeded annealing** (`search_localseed.py`): single-edge-flip
   annealing seeded AT the equality manifold (K_a ∪ K_a and +bridge variants,
   a ∈ {5,8,10,12,15,18}), exact ω each step — probes whether equality can be
   crossed by irregular perturbation.
4. **Named families** (`search_families.py`): Kneser graphs (closed-form spectra,
   ω = ⌊n/k⌋) up to 500k vertices; complete multipartite ± edge; apex over two
   cliques with partial attachment.

## Results so far (checkpoint 1)

- **Bridged cliques**: 17,106 graphs, ZERO violations. Max score = 0 exactly, at
  K_a ∪ K_a (t = 0). Any bridging edge strictly decreases score (λ₂ drops faster
  than the m-term grows). Two earlier "+1.0" hits were K_n itself (bridge filled
  the graph) — excluded case; script now skips complete graphs.
- **Seeded annealing** (1h, seeds up to a=18): never exceeds 0; runs converge back
  onto the equality manifold (score → 0⁻) — the conjecture looks locally tight
  but not crossable near K_a ∪ K_a.
- **Kneser**: hopeless (regular sparse; best score −5 at K(5,2) = Petersen).
- **Multipartite ± e**: equality for complete multipartite (matches the proved
  2026 result). NOTABLE: K_{b,b} − e is ALSO exactly extremal (score = 0):
  bipartite ⇒ Σλᵢ² = 2m and the spectrum is ±λ₁, ±λ₂, 0,… with exactly two
  positive eigenvalues, so λ₁²+λ₂² = m·2·(1−1/2) exactly. Equality family:
  **bipartite graphs with exactly 2 positive eigenvalues** (e.g. complete
  bipartite minus a complete bipartite corner). New-to-us equality manifold to
  perturb around.
- **Blow-up sweep k ≤ 6**: running.

## Results (checkpoint 2)

- **Blow-up sweep k ≤ 6** (`blowup_k6.log`): 11,283 (pattern,type) combos, integer
  weights hill-climbed (6 restarts × 400 iters) up to n = 240. ZERO violations.
  Max score exactly 0, attained by a rich equality manifold: complete split
  graphs / any blow-up with λ₂ = 0 and λ₁² = 2m(1−1/ω) (Nikiforov-extremal),
  balanced multipartite, unions of two Nikiforov-extremal graphs with equal λ₁.
- **Blow-up sweep k = 7** (`blowup_k7.log`): 133,631 combos (all 1044 atlas
  patterns × 128 type maps), n ≤ 300, 4×300 hill-climb. ZERO violations; top
  scores again exactly 0 (same equality classes).
- **Double Turán unions** (`doubleturan.log`): T(n,ω) ⊔ T(n′,ω) is exactly
  extremal for ALL part sizes (even unbalanced pairs) — every cross edge
  strictly decreases the score. 315 graphs, no violation.
- **Continuous weight relaxation** (`opt_continuous.py`, cont_k5b.log): reported
  "positives" (up to +2.33) all sit at FRACTIONAL weights in [1,2.5] near K_n;
  the spectra-floor clamps (λ₂ ≥ −1/0) are invalid at fractional weights.
  Spot-checks of every such point rounded to integers give strictly negative
  scores (e.g. triangle-pattern (2,2,2) IKI → −0.383). Artifact, not a lead.
- **Structural observation** (why unions can't win): by Nikiforov's spectral
  Turán theorem λ₁(H)² ≤ 2m(H)(1−1/ω(H)) for every H. For a disjoint union
  G = G₁ ⊔ G₂, {λ₁(G),λ₂(G)} ⊆ {λ₁(G₁),λ₁(G₂),λ₂(G₁),λ₂(G₂)} and the best case
  λ₁(G₁),λ₁(G₂) gives score(G) ≤ 0 with equality iff both components are
  Nikiforov-extremal with ω(G₁)=ω(G₂). So any counterexample must be CONNECTED,
  and our bridging experiments show sparse connections strictly destroy λ₂
  faster than they credit m. The open window for V2-type constructions is
  therefore dense connected two-cluster graphs — exactly the blow-up class we
  swept exhaustively for k ≤ 7.

## Results (checkpoint 3, final)

- **Random blow-up sampler k = 8–10** (`search_blowup_rand.py`, blowup_rand.log):
  191,568 additional (pattern,type) combos, random patterns at densities
  0.2–0.8, integer weights hill-climbed, n ≤ 400, 90 CPU-min × 8 cores.
  ZERO violations; max score exactly 0 (same equality classes: λ₂ = 0
  Nikiforov-extremal blow-ups, bipartite with two positive eigenvalues,
  unions of matched-λ₁ extremal graphs).
- **Annealing wave 2** (`search_localseed2.py`, localseed2.log): edge-flip
  annealing seeded at double-Turán unions (ω=3..6) and complete split graphs,
  80 min × 4 workers, exact ω per step. Never exceeded 0; best runs converge
  back onto the equality manifold.

## Compute summary

≈ 6 CPU-hours total. Graphs/configurations scored:
- 144,914 exhaustive blow-up (pattern ≤ 7 vertices) weight-optimized configs (n ≤ 300);
- 191,568 random blow-up configs on 8–10-vertex patterns (n ≤ 400);
- 17,106 bridged-clique graphs; 315 double-Turán graphs; ~2h edge-flip
  annealing at/near equality manifolds; Kneser family; multipartite ± e; apex cones.

## Dead ends / lessons

- Regular/vertex-transitive families (Kneser, Paley) are hopeless for this
  conjecture: violations need λ₁ ≈ λ₂ ≈ Θ(n), i.e. two dense near-cliques.
- The equality manifold is much richer than K_a ⊔ K_a: any union of two
  Nikiforov-extremal graphs with equal λ₁ and equal ω, all complete split
  graphs, all complete multipartite graphs, bipartite graphs with exactly two
  positive eigenvalues. Every direction we probed off this manifold moves
  strictly negative — the inequality behaves locally tight but uncrossable.
- Continuous weight relaxations of blow-ups produce spurious positives at
  fractional weights near K_n; do not trust them without integer rounding.
- No witness found ⇒ no solutions/P09/verify.py (per methodology, verifier is
  only required for a claimed result).

## STATUS: negative — no counterexample in the structured (V2) two-eigenvalue
design class: exhaustive blow-ups (≤7-vertex patterns, n ≤ 300), sampled
blow-ups (8–10-vertex patterns, n ≤ 400), bridged/overlapping clique pairs,
double-Turán unions, seeded annealing. Conjecture holds with equality on a
large manifold; all perturbations strictly negative.

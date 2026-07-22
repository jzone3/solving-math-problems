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

## STATUS: (interim) negative — see final line at end of file.

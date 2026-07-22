# Open math problems we could attack together (counterexample-search style)

The Rybin result (disproving Dinitz–Garg–Goemans) worked because the conjecture has a **finite, checkable witness**: a single graph + demands where an LP bound and an exhaustive/ILP search over unsplittable routings disagree. Below are open problems with the same shape — a counterexample (or verification) is a concrete finite object we can hunt for with LP/ILP, SAT solvers, or RL/LLM-guided search.

## Tier 1 — directly adjacent to the DGG result (flow conjectures, still open)

1. **Goemans' unsplittable min-cost flow conjecture.** DGG (the ~"violation ≤ d_max, ignore cost" version with the specific constant) is now false, but the main Goemans conjecture — *any fractional flow can be turned unsplittable with no higher cost and load increase ≤ d_max on every arc* — is still open (proved only for unweighted/error-bounded variants, arXiv:2510.21287, Morell–Skutella 2021). A counterexample would be found exactly the way Rybin did it: small DAG, LP for fractional cost, ILP over unsplittable routings. We could even start from his 58-vs-60 graph and probe cost-preserving variants.
2. **Related discrepancy variants** (arc-wise lower+upper bound versions, "flow discrepancy" bounds — see emergentmind.com/open-problems/single-source-unsplittable-flow-max-demand-discrepancy). Same harness, different constraints.

## Tier 2 — graph theory conjectures with strong counterexample-search track records

3. **Seymour's Second Neighborhood Conjecture** (every oriented digraph has a vertex with |N⁺⁺| ≥ |N⁺|). Finite counterexample = one digraph. SAT/SMS-friendly; verified only for small orders and special classes.
4. **Tuza's conjecture** (τ ≤ 2ν for triangle packing/covering). A counterexample is a single graph where min triangle edge-cover > 2× max edge-disjoint triangle packing — both are small ILPs. Believed tight examples are near K₄/K₅ blowups; guided search is plausible.
5. **Barnette's conjecture** (3-connected cubic planar bipartite ⇒ Hamiltonian). Verified to ~90 vertices; counterexample search = plantri generation + Hamiltonicity SAT. Long-shot but cheap to run.
6. **Erdős–Gyárfás conjecture** (min degree 3 ⇒ cycle of length 2^k). SAT-modulo-symmetries has verified up to 30 vertices (Zenodo 2025); we could push the frontier or hunt in structured families.
7. **Spectral graph theory conjectures** (Graffiti/AutoGraphiX-style, e.g., bounds on λ_max, energy, eccentricity). Wagner (2021) and ECAI-2025 Monte-Carlo search papers refuted several; dozens remain open and are ideal for RL/MCTS/LLM-guided graph search — highest hit rate per compute of anything on this list.

## Tier 3 — famous, harder, but finite-witness

8. **Union-closed sets (Frankl) conjecture** — counterexample is a finite family; Gilmer-style progress got to 38%, gap to 50% open. Counterexample unlikely, but improving the constant is a real target.
9. **Hadwiger–Nelson gap** (chromatic number of the plane is 5, 6, or 7 — de Grey's 5-chromatic graph came from SAT). Finding a 6-chromatic unit-distance graph is a pure SAT+geometry search.
10. **Reconstruction conjecture** — verified for n ≤ 13; pushing to n = 14, or searching structured families, is a canonical nauty/canonical-form computation.

## Suggested first project

Start with **#1 (Goemans cost conjecture)**: reuse the exact methodology from the tweet (LP relaxation vs. ILP over unsplittable routings, small DAGs, randomized + LLM-guided instance generation), seeded from Rybin's counterexample graph. If nothing falls out in a few days of compute, pivot the same harness to #4 (Tuza) or #7 (spectral conjectures), which share the "generate graph → evaluate two ILP/LP quantities → score gap" loop.

Useful problem catalogs to mine for more: erdosproblems.com, Open Problem Garden, epoch.ai/frontiermath/open-problems, the Duke "AI-powered Discovery of Counterexamples in Combinatorics" report.

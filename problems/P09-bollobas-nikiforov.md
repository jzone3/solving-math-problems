# P09 — Bollobás–Nikiforov Conjecture

**Statement.** For every non-complete graph G with m edges and clique number ω:
λ₁(G)² + λ₂(G)² ≤ 2m(1 − 1/ω). (Bollobás–Nikiforov, JCTB 97 (2007), Conjecture 1.)

**Why it matters.** The central open "spectral Turán" strengthening; very active community
(triangle-free case proved Lin–Ning–Wu 2021; dense K₄-free and complete-multipartite cases 2026;
a.a.s. for random graphs 2025).

**Status.** Open in general as of July 2026. **No published large-scale numerical counterexample
search** — all compute has been incidental to proofs. Highest-prestige target with a dirt-cheap
evaluation loop.

**Witness & verifier.** One graph violating the inequality; two eigenvalues + exact clique
number (ILP/branch-and-bound, fine to n ≈ 100).

**Prompt variants:**
1. **V1 annealed dense search**: edge-flip annealing at n = 15–80, score = λ₁²+λ₂² − 2m(1−1/ω)
   with exact ω via a MaxClique solver; multiple restarts across densities and ω values.
2. **V2 two-eigenvalue design**: violations need two large eigenvalues — search
   two-near-clique constructions (joins, books, double kites, Kneser/quasi-random families) with
   closed-form spectra; optimize parameters exactly.
3. **V3 fixed-ω sweeps**: for each ω ∈ {3,…,8}, search only ω-clique-saturated graphs (avoids
   clique-number drift during search); compare against the known proved classes to stay in
   genuinely open territory (e.g. K₄-free sparse regime).
4. **V4 exhaustive small-n**: geng-exhaust all graphs n ≤ 12 (beyond any published check);
   then vertex-transitive/circulant graphs to n ≈ 50 via orbit enumeration.
5. **V5 literature-first**: digest Lin–Ning–Wu and 2024–2026 partial results to map the exact
   open region (ω ≥ 4, non-dense, "many triangles" regime); design the search to live there;
   also test the tightness sequence of known extremal graphs for perturbation attacks.

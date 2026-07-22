# P10 — Brouwer's Conjecture (Laplacian partial sums)

**Statement.** For every graph G with m edges and Laplacian eigenvalues μ₁ ≥ … ≥ μₙ:
for all 1 ≤ t ≤ n, Σ_{i=1}^t μᵢ ≤ m + t(t+1)/2. (Brouwer–Haemers, *Spectra of Graphs*, §3.2.)

**Why it matters.** The standing analogue of Grone–Merris (proved by Bai 2011); very active
2025–2026 literature wave; proved for t ∈ {1,2,n−1,n}, trees, split graphs, cographs.

**Status.** Open in general (July 2026). Exhaustive n ≤ 10 (Brouwer). The tight regime is
t ≈ n/2 on dense graphs near split-graph structure — no reported metaheuristic attack there.

**Witness & verifier.** A graph + index t violating the sum bound; one eigensolve.

**Prompt variants:**
1. **V1 annealed search**: score = max_t (Σ_{i≤t} μᵢ − m − t(t+1)/2); edge-flip annealing at
   n = 12–60 across all densities; exact-verify near-misses with high-precision arithmetic.
2. **V2 equality perturbation**: split graphs achieve equality — enumerate split and
   near-split/threshold graphs and perturb (single edge moves) hunting sign flips; closed-form
   Laplacian spectra of threshold graphs make this exact and fast.
3. **V3 exhaustive n = 11–12**: push Brouwer's exhaustive verification frontier with geng +
   optimized eigensolve pipeline; publishable frontier either way.
4. **V4 structured families**: joins, complements, Kneser graphs, incidence graphs — families
   with computable Laplacian spectra; symbolic scan of the middle-t inequality.
5. **V5 literature-first**: digest the 2025–26 wave (arXiv:2503.11165, 2606.12197, 2607.03388,
   2607.08452, 2607.17293) — verify none closes the conjecture; identify the residual open class
   and the loosest step in current proofs; target the search there.

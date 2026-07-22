# P09 Bollobás–Nikiforov — Variant V4 (exhaustive small-n + circulants)

Session: https://app.devin.ai/sessions/3bec412feb19407cbf683132877f8929
Branch: `runs/P09-v4` (based off `devin/1784749757-context-plan`)

## Problem statement re-verification (done first)

Checked against arXiv sources quoting the original (Bollobás–Nikiforov, "Cliques and the
spectral radius", JCTB 97 (2007), Conjecture 1): for any graph G ≠ K_n with m edges,
clique number ω, and adjacency eigenvalues λ₁ ≥ λ₂ ≥ …:

    λ₁² + λ₂² ≤ 2m(1 − 1/ω).

Matches the problem file exactly (sources checked: arXiv 2407.19341 Kumar–Pragada,
arXiv 2501.07137 Liu–Bu, arXiv 2603.26379 Giacomelli). Openness as of July 2026
confirmed: only partial cases proved (triangle-free = Lin–Ning–Wu 2021; complete
multipartite + dense K₄-free 2026; a.a.s. random graphs 2025; regular-graph partial
results Zhang 2023). General case open. No published exhaustive small-n check found.

## Encoding / tooling

- `checker.c`: reads graph6 on stdin. Full Jacobi eigendecomposition (doubles),
  exact clique number via bitmask branch-and-bound. Skips complete/empty graphs.
  **Prune**: since ω ≥ 2 ⇒ RHS ≥ m, a violation needs s = λ₁²+λ₂² > m; clique number
  computed only for graphs with s > m − 1e-6. Violation threshold gap > 1e-7
  (near-boundary graphs tracked via best_gap).
- `checker2.c`: ~2× faster path (Householder tridiagonalization + Sturm bisection for
  top-2 eigenvalues only); any candidate violation is re-confirmed with an
  independently coded full Jacobi before being reported. Counts cross-validated
  against `checker.c` on n = 8 and n = 10 (identical totals/evaluated/violations).
- `circulant.c`: enumerates ALL circulant graphs C_n(S), S ⊆ {1..⌊n/2⌋}, via Gray-code
  incremental eigenvalue updates (λ_j closed form); same prune + exact clique
  (64-bit bitmask B&B).
- Generation by `nauty-geng` (nauty 2.7r3), parallelized with res/mod splitting.

## Results so far

### Exhaustive: ALL graphs n ≤ 11 — ZERO violations

| n | graphs checked | clique-evaluated (s > m) | violations | max gap seen |
|---|---|---|---|---|
| ≤ 9 | 288,092 (cum: 5,6,7,8,9) | — | 0 | ~1e-13 (equality cases) |
| 10 | 12,005,168 | 11,587,234 | 0 | 2.3e-13 |
| 11 | 1,018,997,864 | 990,183,185 | 0 | 2.3e-13 |

n = 11 total matches OEIS A000088(11) = 1,018,997,864 exactly (generation sanity check).
All "best gap" graphs are equality cases (complete bipartite / complete multipartite /
2K_k-type unions), gap ~1e-13 = float noise around exact equality — consistent with
the known extremal families. **No near-misses**: nothing strictly between equality
and violation was observed.

Compute: n ≤ 10 ≈ 2 CPU-min; n = 11 ≈ 4 CPU-hours (8-way res/mod parallel, ~30 min wall).

### Reduction for n = 12: connected graphs suffice

Given the n ≤ 11 exhaustive result, any 12-vertex counterexample must be connected.
Let G be a disconnected 12-vertex graph; every component has ≤ 11 vertices. Two cases:

1. λ₁, λ₂ of G come from different components G₁, G₂. Nikiforov's proved theorem
   (λ₁(H)² ≤ 2m(H)(1 − 1/ω(H)) for every H) applied to each gives
   λ₁² + λ₂² ≤ 2m₁(1−1/ω₁) + 2m₂(1−1/ω₂) ≤ 2m(G)(1−1/ω(G)), since ωᵢ ≤ ω(G) and
   m₁ + m₂ ≤ m(G). No violation.
2. λ₁, λ₂ both come from a single component H (≤ 11 vertices). Then
   LHS(G) = LHS(H) ≤ RHS(H) = 2m(H)(1−1/ω(H)) by the n ≤ 11 exhaust, and
   RHS(H) ≤ 2m(G)(1−1/ω(G)) since m(H) ≤ m(G) and ω(H) ≤ ω(G). No violation.

Hence sweeping connected graphs (`geng -c`) is complete at n = 12.

### In progress

- n = 12 connected sweep (`geng -c`, 141,100,986,679 graphs*, 120 res/mod slices,
  checker2, 6 workers). *count = A001349(12).
- Circulants n = 21…46 exhaustive over connection sets (n ≤ 20 done above: zero
  violations, equalities at complete-multipartite circulants only).

## STATUS (checkpoint, to be finalized)

STATUS: negative (so far) — conjecture verified for ALL graphs on ≤ 11 vertices and
all circulants n ≤ 20; larger sweeps in progress.

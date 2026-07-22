# P09 — Bollobás–Nikiforov, Variant V1 (annealed dense search)

Session: https://app.devin.ai/sessions/1d89a8862d154f23b76d15b47022bd01

## Statement verification

Conjecture 1 of B. Bollobás, V. Nikiforov, *Cliques and the spectral radius*, JCTB 97 (2007)
859–865: for every G ≠ K_n with m edges and clique number ω,
λ₁² + λ₂² ≤ 2m(1 − 1/ω), where λ₁ ≥ λ₂ are the two largest adjacency eigenvalues.
Cross-checked against arXiv:2603.26379 (Mar 2026), arXiv:2501.07137, arXiv:2407.19341 — the
statement in `problems/P09-bollobas-nikiforov.md` matches, and the general conjecture is still
**open as of July 2026** (the 2026 papers prove only complete-multipartite and dense K₄-free
cases).

## Encoding & tooling

- `bn_core.py`: graphs as bitmask adjacency lists; λ₁, λ₂ via `numpy.linalg.eigvalsh`; exact ω
  via a Tomita-style branch-and-bound MaxClique with greedy-coloring bound (cross-validated
  against `networkx.find_cliques` on 50 random graphs). graph6 encode/decode for logging.
- Score = λ₁² + λ₂² − 2m(1 − 1/ω); ratio = (λ₁²+λ₂²)/(2m(1−1/ω)). Counterexample ⟺ score > 0.
- Sanity checks passed: K_{5,5} and Turán T(9,3) give ratio exactly 1 (known equality cases);
  C₅ 0.876; Petersen 0.667; K₁₀−e 0.9934.
- Float-noise guard: a "found" requires score > 1e−6 (an early run flagged T(18,6) itself at
  score ≈ 1.1e−13 — pure eigensolver noise on an equality case; fixed with EPS).

- `anneal.py`: simulated annealing on edge flips (80% single flip, 20% double), geometric
  temperature 0.02 → 0.0005, objective = ratio, plus an `l2bias` mode
  (ratio + 0.03·λ₂/λ₁) to push away from the complete-multipartite attractor (λ₂ = 0 equality
  class, proved safe in arXiv:2603.26379). 8 worker processes, random restarts across
  n ∈ [nmin, nmax], p ∈ [0.15, 0.9], steps ∈ {3k, 8k, 20k}.
- `analyze.py`: summarizes results, detects complete-multipartite graphs (complement = disjoint
  cliques), reports best per ω and best non-multipartite near-misses.

## Runs

### Phase 1: n = 15–60, 2 h × 8 cores (seed 42)

(in progress — see results below)

## STATUS: (pending)

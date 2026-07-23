# P09 — Bollobás–Nikiforov, Variant V1 (annealed dense search)

Session: https://app.devin.ai/sessions/1d89a8862d154f23b76d15b47022bd01

## Statement verification

Conjecture 1 of B. Bollobás, V. Nikiforov, *Cliques and the spectral radius*, JCTB 97 (2007)
859–865: for every G ≠ K_n with m edges and clique number ω,
λ₁² + λ₂² ≤ 2m(1 − 1/ω), where λ₁ ≥ λ₂ are the two largest adjacency eigenvalues.
Cross-checked against arXiv:2603.26379 (Mar 2026), arXiv:2501.07137, arXiv:2407.19341 — the
statement in `problems/P09-bollobas-nikiforov.md` matches, and the general conjecture is still
**open as of July 2026** (the 2026 papers prove only complete-multipartite and dense K₄-free
cases; triangle-free case was Lin–Ning–Wu 2021).

## Encoding & tooling

- `bn_core.py`: graphs as bitmask adjacency lists; λ₁, λ₂ via `numpy.linalg.eigvalsh`; exact ω
  via a Tomita-style branch-and-bound MaxClique with greedy-coloring bound (cross-validated
  against `networkx.find_cliques` on 50 random graphs). graph6 encode/decode for logging.
- Score = λ₁² + λ₂² − 2m(1 − 1/ω); ratio = (λ₁²+λ₂²)/(2m(1−1/ω)). Counterexample ⟺ score > 0.
- Sanity checks passed: K_{5,5} and Turán T(9,3) give ratio exactly 1 (known equality cases);
  C₅ 0.876; Petersen 0.667; K₁₀−e 0.9934.
- Float-noise guard: a "found" requires score > 1e−6 (an early run flagged T(18,6) itself at
  score ≈ 1.1e−13 — pure eigensolver noise on an equality case; fixed with EPS=1e-6; any hit
  would then be re-verified exactly before being claimed).
- `anneal.py`: simulated annealing on edge flips (80% single flip, 20% double), geometric
  temperature 0.02 → 0.0005, objective = ratio, plus an `l2bias` mode
  (ratio + 0.03·λ₂/λ₁, chosen 2/3 of restarts) to push away from the complete-multipartite
  attractor (λ₂ = 0 equality class, proved safe in arXiv:2603.26379). 8 worker processes,
  random restarts across n ∈ [nmin, nmax], p ∈ [0.15, 0.9].
- `analyze.py`: summarizes results, detects complete-multipartite graphs (complement = disjoint
  cliques), reports best per ω and best non-multipartite near-misses.
- `perturb.py`: deterministic scan of ALL single edge flips (and all double flips for n ≤ 18)
  around the equality cases: Turán T(n,ω) for n ∈ {12,…,40}, ω ∈ {2,…,8}, and disjoint unions
  K_{a,b} ∪ K_{c,d} (which achieve equality with λ₂ > 0).

## Runs (all on 8 cores; ~49 core-hours total; zero counterexamples in 1951 restarts)

### Phase 1: n = 15–60, steps ∈ {3k, 8k, 20k}, seed 42 — 1362 restarts, 16.1 core-h
- Best ratio = 1.00000000 (to machine precision), attained ONLY at known equality cases:
  Turán graphs T(15,5), T(18,6), T(19,6)+isolated vertex, T(15,5)+isolated vertex, and a
  disjoint union of two complete bipartite graphs (n=18, m=46, ω=2, λ₂=2.876 — equality via
  λ₁²+λ₂² = ab+cd = m). The annealer reliably *finds* the equality surface but never crosses it.
- Best genuinely non-equality near-miss: ratio 0.99864 (n=24, m=220, ω=6).
- Best with substantial λ₂: ratio 0.98627 (n=23, m=213, ω=6, λ₂=2.11).
- ω=3 (K₄-free, most open regime): best ratio only 0.9835 — the conjecture looks slack there.
- Full log: `results_phase1.jsonl`, summary `phase1_summary.txt`.

### Phase 2: n = 55–80 (larger graphs), seed 777 — 204 restarts, 16.3 core-h
- Best ratio 0.931 (n=55, m=1321, ω=22). At these sizes 20k steps is far from converged;
  ratios trend well below 1. No violation. Log: `results_phase2.jsonl`.

### Phase 3: deep anneals, n = 20–45, fixed 60k steps, seed 2026 — 385 restarts, 16.3 core-h
- Best ratio again exactly 1.0 only at equality cases (T(20,6)-type ± isolated vertices,
  T(24,8)); best non-equality 0.99863 (n=23, m=207, ω=7). No violation.
  Log: `results_phase3.jsonl`, summary `phase3_summary.txt`.

### Perturbation scan (deterministic, `perturb.log`)
- All 1-flip neighbors of T(n,ω), n ≤ 40, ω ≤ 8, and of K_{a,b} ∪ K_{c,d} up to n=28:
  max score strictly < 0 (typically ≤ −0.3), except flips that land on another equality case
  (score exactly 0, e.g. K_{a,b} edge deletions creating another extremal configuration).
- All 2-flip neighbors for n ≤ 18: same conclusion. **The equality surface is locally strictly
  optimal** — no ascent direction out of the known extremal families.

## Near-misses & structure observed

- The ratio landscape has a single dominant attractor: complete multipartite (Turán) graphs and
  their unions/isolated-vertex paddings, all with ratio exactly 1 — precisely the classes
  proved safe in 2021/2026. Every high-ratio anneal endpoint is a slightly-perturbed Turán
  graph with ratio strictly < 1.
- Graphs engineered by the l2bias mode toward two large eigenvalues top out around
  ratio ≈ 0.986 (e.g. n=23, m=213, ω=6, λ₂=2.11) — the λ₂² term costs more in m than it gains.
- The most-open regimes (ω = 3 sparse; ω ≥ 4 non-dense) never exceeded ratio 0.984 in ~2000
  converged anneals; the inequality appears to have real slack away from the Turán surface.

## Dead ends

- Pure `ratio` objective wastes most restarts converging onto Turán graphs; `l2bias` explores
  better but still ends below the multipartite attractor.
- n ≥ 60 dense anneals are compute-bound by MaxClique (ω ≈ 20 at p = 0.8, ~0.4 s/eval) and
  would need incremental eigen/clique updates to converge; not pursued further under V1.

## STATUS: negative

No counterexample found. ~1951 annealed restarts (~49 core-hours) over n = 15–80 across
densities 0.15–0.9 and ω = 2–22, plus exhaustive 1-/2-edge perturbation scans of the known
equality families. Maximum ratio ever observed: exactly 1 (known equality cases only);
maximum strictly-inside ratio 0.99864. Consistent with the conjecture being TRUE, with the
extremal surface exactly the complete-multipartite class already proved safe.

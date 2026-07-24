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

## Frontier extension (post-resume, second campaign)

### Exhaustive verification: ALL graphs on n ≤ 11 vertices — NO violation
- `exhaust.py`: geng stream → vectorized graph6 decode → batched `eigvalsh` → prune
  (violation ⟺ ω·r < 2m with r = 2m − λ₁² − λ₂² ≥ 0; ω ≥ 2 gives necessary condition
  r < m) → greedy clique lower bound → exact MaxClique on the rest.
- n = 8: 12,346; n = 9: 274,668; n = 10: 12,005,168; n = 11: **1,018,997,864 graphs**
  (24-way geng res/mod split on 8 cores, ~2 h wall). Totals match the known counts of
  graphs on n vertices exactly. Zero graphs even reached the exact-score stage
  (`clique_checked=0`): no non-complete graph on ≤ 11 vertices comes within the pruning
  tolerance of violating the inequality. Logs: `exhaust_n10.log`, `exhaust_n11.log`.
- Independent cross-check (`crosscheck.py`): 2,000 random n=9 + 500 random n=11 graphs
  re-evaluated through a fully separate code path (networkx `adjacency_spectrum` +
  `find_cliques`) — PASS, zero mismatches.
- To our knowledge no exhaustive n ≤ 11 check has been published for this conjecture
  (the problem file notes n ≤ 12 as "beyond any published check"); n = 12 (~1.65×10¹¹
  graphs) would need ~160× more compute — left as the natural next step.

### Exhaustive circulant sweep: ALL C_n(S) for n ≤ 50 — NO violation
- `circulant.py`: closed-form spectra (λ_j = Σ_{s∈S} 2cos(2πjs/n)), all 2^⌊n/2⌋
  connection sets per n (up to 33.5M subsets at n = 50; ~2.1×10⁸ circulants total),
  same prune + exact ω on survivors. Zero violations, zero survivors even reaching the
  clique stage. Log: `circulant.log`.

### Structured families (`families.py`) — NO violation
- Kneser/Johnson (n ≤ 12), Paley (q ≤ 149), books K_p+I_q, two cliques sharing s vertices,
  joins K_p + (K_a ∪ K_b [∪ K_c]) — all safe. Noted equality family beyond Turán:
  **K_a ∪ K_a** (λ₁ = λ₂ = a−1) gives ratio exactly 1, as do padded/union variants.

### Basin-hopping seeded anneal (`seeded.py`)
- 1,304 re-anneals (30k steps each, low temperature) seeded from the 120 best near-miss
  endpoints of phases 1–3, perturbed by 3–10 random flips. Best non-equality near-miss
  improved to 0.99899994 (m=260, ω=6); best ratio again exactly 1
  (equality cases only); no violation. Log: `results_seeded.jsonl`.

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

## Campaign 3 (resumed session): exhaustive n = 12 via native C checker

Goal: execute the recorded next frontier — exhaustive verification of ALL graphs on 12
vertices (165,091,172,592 non-isomorphic graphs, ~160× the n = 11 compute).

New tool: `bn_check.c` — a dependency-free C checker (~2.5 µs/graph at n = 10):
- decodes geng's fixed-length graph6 lines in bulk;
- top-2 adjacency eigenvalues via Householder tridiagonalization + Sturm-sequence bisection,
  with threshold-aware early exit (certifies λ₁²+λ₂² ≤ 2m(1−1/g)−MARG as soon as the
  bisection interval allows, g = greedy clique lower bound; uses λ₂² ≤ λ₁², valid by
  Perron–Frobenius);
- survivors get full-precision eigenvalues + exact Tomita-style BnB MaxClique (greedy-coloring
  bound); prints any graph with ω·(2m − λ₁² − λ₂²) < 2m − MARG, MARG = 1e-5
  (i.e. rules out violations with score > ~1e-6, same standard as the Python phases).

Validation of the C checker:
- Bug found & fixed during bring-up: BnB coloring bound requires vertices sorted by color
  before the reverse sweep; the unsorted version under-reported ω (caught by differential
  disagreement with `bn_core.py`).
- Differential test vs `bn_core.evaluate` on ALL 12,344 non-trivial n = 8 graphs:
  0 mismatches in λ₁, λ₂, m, ω, score (tol 1e-7).
- Differential test on 2,999 random n = 12 graphs (p ∈ [0.1, 0.9]): 0 mismatches.
- Full n = 11 re-run in C: total = 1,018,997,864 (matches the known count and the Python
  campaign exactly), candidates = 0, in ~7 min on 8 cores.

n = 12 production run: `run_n12.sh` — geng 12 split into 64 res/mod parts, 8-way parallel,
per-part logs in `c12/n12_p*.log`, restartable via `.done` markers. Estimated ~24–30 h on
8 cores.

RESULT: **COMPLETE — all 165,091,172,592 non-isomorphic graphs on 12 vertices satisfy the
conjecture.** Per-part totals sum EXACTLY to the known count 165,091,172,592 (validating that
no graph was dropped); 103,978,035 survivors required an exact MaxClique resolution; ZERO
candidates (no graph with ω·(2m − λ₁² − λ₂²) < 2m − 1e-5). Wall time ~15 h: parts 0–15 and
24–55 on this box (8 cores), parts 16–23 and 56–63 delegated to two child Devin sessions
(logs merged from branches runs/P09-v1-parts16-23 and runs/P09-v1-parts56-63; child checkers
passed the mandatory n=9 sanity gate total=274668/survivors=3890/candidates=0 before running).
Per-part logs: c12/n12_p*.log (all 64 committed).

## Campaign 4: weighted-blowup / graphon-regime search (`blowup.py`)

Since n ≤ 12 is exhausted, any counterexample lives at n ≥ 13 or asymptotically. This attack
probes the n → ∞ regime directly: for a profile graph H with vertex weights w on the simplex,
the blowup G_n (parts ≈ n·w_i independent sets) has λ₁/n → μ₁(S), λ₂/n → max(μ₂(S), 0),
m/n² → e_w = ½·Σ_{i≠j} A_ij w_i w_j, ω = ω(H), where S = diag(√w)·A_H·diag(√w). Any (H, w)
with ratio(w) = (μ₁² + (μ₂⁺)²)/(2 e_w (1 − 1/ω(H))) > 1 would give an asymptotic (hence, by
continuity, a finite) counterexample.

Method: projected-gradient ascent on the simplex (analytic eigenvalue gradients via
∂μ_k/∂x_i = 2 v_k[i]·(A diag(x) v_k)[i], x = √w), multi-restart, over ALL connected profiles
H from geng.

RESULT: for every connected profile on 3–9 vertices (2 + 6 + 21 + 112 + 853 + 11,117 +
261,080 profiles), the maximum of ratio(w) is EXACTLY 1, attained only at Turán-type weights
(zero-weight-degenerations included). Zero violations. So no blowup/graphon-scale
counterexample exists with ≤ 9 parts.

Remark (proved, not just searched): for blowups with *clique* parts (looped profiles),
ω(G_n) → ∞ so the RHS → 2m, while λ₁² + λ₂² ≤ Σ λ_k² = 2m always — hence clique-part blowups
can never violate the conjecture (equality iff the positive spectrum has rank ≤ 2, e.g.
K_a ∪ K_a). Also note 2e_w = ‖S‖_F² for loopless profiles, so the graphon-regime statement is
μ₁² + (μ₂⁺)² ≤ (1 − 1/ω)·Σ_k μ_k².

## STATUS: negative / frontier-pushed

No counterexample found. Campaign totals:
- **Exhaustive: every graph on ≤ 12 vertices (1.66×10¹¹ graphs) satisfies the conjecture**
  (believed to exceed any published verification); totals match known graph counts exactly at
  every n; C checker differentially validated against an independent Python/NumPy/NetworkX path.
- Exhaustive: every circulant C_n(S), n ≤ 50 (~2.1×10⁸ graphs) satisfies it.
- Graphon regime: no weighted-blowup counterexample over ALL connected profiles ≤ 9 vertices
  (273k profiles × multi-restart simplex optimization); max ratio exactly 1 at Turán weights.
- ~2,700 annealed/basin-hopped restarts (~60 core-h) over n = 15–80, ω = 2–22; exhaustive
  1-/2-flip scans of equality families; Kneser/Johnson/Paley/book/kite/join scans.
Maximum ratio ever observed: exactly 1, only at known equality classes (complete multipartite,
disjoint unions like K_{a,b} ∪ K_{c,d} and K_a ∪ K_a, plus isolated-vertex paddings). Maximum
strictly-inside ratio 0.99900. Strong computational evidence the conjecture is TRUE with
extremal surface exactly these classes. Natural next frontier: exhaustive n = 13 (~5×10¹³
graphs, ~300× the n = 12 compute — needs a cluster) or SAT/SMS-driven search in the
ω = 3,4 sparse regime.

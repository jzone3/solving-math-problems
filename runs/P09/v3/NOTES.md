# P09 Bollobás–Nikiforov — V3 run notes (fixed-ω sweeps)

Session: https://app.devin.ai/sessions/39f7938d82d744ec91d21ac1ee636804
Variant: V3 — for each ω ∈ {3,…,8}, search only within graphs of exactly that
clique number ("ω-clique-saturated" search: clique number never drifts).

## 0. Statement re-verification (before deep work)

Checked the statement against the original source and recent literature
(2026-07-22, via Exa search of arXiv):

- Original: Bollobás & Nikiforov, *Cliques and the spectral radius*, JCTB 97
  (2007) 859–865, Conjecture 1: for G ≠ K_n with m edges, clique number ω,
  λ₁² + λ₂² ≤ 2m(1 − 1/ω). Matches problem file exactly (confirmed against
  the restatements in arXiv:2407.19341, arXiv:2101.05229, arXiv:2603.26379,
  which all quote Conjecture 1 in this exact form).
- Still open as of July 2026: arXiv:2603.26379 (Mar 2026) proves only special
  cases (complete multipartite; dense K₄-free) and explicitly calls the
  general conjecture open. Proved cases to avoid wasting compute on:
  triangle-free / ω=2 (Lin–Ning–Wu 2021), ω-regular-ish dense K₄-free
  (m = Ω(n²), n large), complete multipartite, random graphs a.a.s.
  (arXiv:2501.07137), graphs with few triangles (arXiv:2407.19341).

## 1. Encoding / search design

`search.py`: simulated annealing over edge flips with ω held EXACTLY fixed:

- Plant a K_ω on vertices 0..ω−1; its edges are immutable → ω ≥ target always.
- Any edge addition is first checked with a bitset branch-and-bound
  `has_clique(N(u)∩N(v), ω−1)`; additions creating K_{ω+1} are rejected →
  ω ≤ target always. So every visited graph has clique number exactly ω
  (independently re-verified per restart with `verify_omega`).
- Score = (λ₁²+λ₂²) / (2m(1−1/ω)); ratio > 1 ⇔ counterexample.
- Eigenvalues: numpy `eigvalsh` (dense, exact symmetric solver); candidate
  verification is delegated to `solutions/P09/verify.py`-style exact check if
  anything exceeds 1.
- Clique check correctness: cross-validated against networkx `find_cliques`
  on 200 random G(n,p) graphs, all sizes k — PASS.

## 2. Runs

### Phase 1 (done, ~2 min/ω, 6 parallel procs)
ω ∈ {3..8}, n ∈ [12,45], 60 restarts × 12000 annealing iters each,
random initial densities p ∈ [0.2,0.8].

Result: annealer converges onto the EQUALITY surface, ratio = 1.0 exactly
(float 1.0 + ~1e-15). All ratio-1 graphs found are balanced complete
multipartite Turán graphs (+ isolated vertices): T(9,3), T(16,4), T(15,5),
K_{2×6}, K_{2×7}; ω=8 best was 0.99765 (near-balanced multipartite). These
have λ₂ = 0, so equality is just Nikiforov's spectral Turán theorem — the
known (proved) equality class, NOT counterexamples. Lesson: the hard tension
is getting λ₂ > 0 while keeping λ₁² close to 2m(1−1/ω); the annealer's local
optimum is always λ₂→0.

Bug fixed after phase 1: early-exit threshold was `ratio > 1.0`, which float
noise (1+1e-15) triggered; now requires ratio > 1 + 1e-8 and any candidate
would be re-verified exactly.

### Phase 2 (running)
Two attack refinements per the "perturbation near the extremal class" idea:
- `--init turan`: start at Turán graph T(n,ω) plus up to n²/20 random flips,
  ω ∈ {3..8}, n ∈ [15,60], 80 restarts × 20000 iters.
- `--lam2min 1.5`: penalized objective forcing λ₂ ≥ 1.5, ω ∈ {3,4,5},
  n ∈ [15,50], 60 restarts × 20000 iters (searches the λ₂>0 stratum, where
  the conjecture is genuinely untested).

## STATUS: (pending)

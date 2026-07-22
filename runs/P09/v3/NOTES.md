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

### Phase 2 results
- Turán-start runs (ω 3–8): again converge to ratio = 1.0 exactly; best
  graphs are balanced Turán/complete-multipartite (λ₂ = 0 class). No ratio
  > 1 + 1e-8 anywhere.
- λ₂ ≥ 1.5 penalized runs (ω 3–5): best pure ratios 0.9984 (ω=3, n=22),
  0.9978 (ω=4, n=30), 0.9938 (ω=5, n=21) — close but strictly below 1.

### Key structural observation → phase 3
The disjoint union of two equal balanced Turán graphs T(k,ω) ∪ T(k,ω)
(ω | k) attains EQUALITY with λ₁ = λ₂ > 0: λ₁²+λ₂² = 2λ² = 2·2m₁(1−1/ω)
= 2m(1−1/ω). This is the natural place to look for violations (equality
surface with both eigenvalues active). Added `--init turan2`.

### Phase 3 (turan2 starts, ω 3–8, n up to 60, 80×25000)
All runs plateau at exactly 1.0 (the union family itself); annealing never
exceeds it. Perturbation scanner `perturb.py`: exhaustive ALL 1- and 2-edge
flips of T(9,3)∪T(9,3) (9,180 ω-preserving flip sets), T(12,3)∪T(12,3)
(28,920), T(12,4)∪T(12,4) (31,878), T(10,5)∪T(10,5) (16,290): max ratio
stays exactly 1.000000000000; NO flip set exceeds the base. The equality
family is a strict local maximum of the ratio under ≤2 edge flips.

### Phase 4 (done, ~1h wall, 12 procs): ω 3–8 × {random, turan2} inits,
n ∈ [20,90], 150 restarts × 40000 iters each (72M proposed flips total).
Every ω reached best ratio exactly 1.0 (float 1 ± 1e-15) or 0.998–0.999;
NOTHING above 1 + 1e-8. Best graphs at 1.0 are again the equality families
(Turán graphs / unions of two balanced Turán graphs).

### Phase 5 (done): λ₂ ≥ 2.5 penalized runs for all ω ∈ {3..8}, n ∈ [15,60],
60 restarts × 25000 iters. Best pure ratios: 0.9970 (ω=3), 0.9969 (ω=4),
0.9920 (ω=5), 0.9891 (ω=6), 0.9868 (ω=7), 0.9865 (ω=8). The forced-λ₂
stratum stays strictly below the bound, with slack growing in ω.

More exhaustive perturbation scans (depth 2, all ω-preserving 1- and 2-edge
flips): T(15,3)² (70,500 flip sets), T(16,4)² (100,576), T(12,6)² (34,980),
T(14,7)² (66,430) — max ratio exactly 1.0, never exceeded. Combined with
phase-3 scans: ~360k exhaustively-checked perturbations of the λ₂>0
equality family, all ≤ 1.

## 3. Summary

- Total compute: ≈ 110M annealing proposals (each accepted move = one dense
  eigvalsh) + ~360k exhaustive perturbation checks, ~2.5 h on 8 cores.
- No counterexample candidate ever appeared (threshold 1 + 1e-8).
- The ratio (λ₁²+λ₂²)/(2m(1−1/ω)) appears to have global maximum exactly 1,
  attained on (unions of ≤2) balanced Turán graphs; both the λ₂=0 stratum
  (single Turán) and the λ₂>0 stratum (double Turán) are strict local maxima
  under ≤2 edge flips (machine-verified exhaustively for 8 base graphs).
- Near-misses: forced-λ₂ runs cap around 0.997–0.998 (ω=3,4), suggesting the
  open ω≥4 λ₂>0 region has real slack away from the disconnected equality
  family.
- Dead ends: naive annealing always slides onto the equality surface and
  stalls; early-exit float-threshold bug (fixed) caused phase-1 false
  "COUNTEREXAMPLE FOUND" prints — those were exact-equality graphs.
- No solutions/P09/verify.py: nothing to claim (per methodology, verifier is
  only required for a claimed witness).

## STATUS: negative — no counterexample found for ω ∈ {3..8}, n ≤ 90;
conjecture held (ratio ≤ 1) at every one of ~110M sampled ω-fixed graphs,
with the known equality families recovered as the only maxima.

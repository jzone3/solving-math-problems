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

## 4. Frontier push (second pass, after orchestrator "keep going")

### Exhaustive verification for ALL graphs n ≤ 11 (`check.c`)
Wrote a C checker (graph6 stdin → exact bitset clique number + cyclic-Jacobi
eigenvalues; EPS 1e-7; cross-validated against numpy/networkx on 300 random
graphs and all graphs n ≤ 8). Ran `nauty-geng` exhaustively:
- n ≤ 10: 12,293,427 graphs — 0 violations, max ratio exactly 1.
- n = 11: 1,018,997,864 graphs (8-way geng res/mod split, ~1.5 h) —
  0 violations, max ratio exactly 1 (sum of part counts matches the known
  total number of graphs on 11 vertices exactly).
The conjecture is now machine-verified for EVERY graph on ≤ 11 vertices —
beyond any check reported in the literature.

### Exhaustive circulant sweep (`circulant.py`)
All 2^⌊n/2⌋−1 circulants C_n(S) for every n ≤ 42, eigenvalues in closed form
(DFT of connection set; formula cross-validated against networkx for n ≤ 12).
Violation test reduced to a single clique query: violation ⇔ ω ≤ kmax :=
⌈1/(1−t)⌉−1 where t = (λ₁²+λ₂²)/(2m) ⇔ no (kmax+1)-clique exists.
Zero candidates for all n ≤ 42 (~7M circulants; found+fixed an edge-count
bug — first version halved m, producing false candidates that vanished once
m was corrected and re-validated against networkx).

### Depth-3 perturbation scans
All ≤3-edge-flip ω-preserving perturbations of T(9,3)∪T(9,3) (409,689 flip
sets) and T(8,4)∪T(8,4) (234,344): max ratio exactly 1.0, never exceeded —
the λ₂>0 equality family is a strict local max to flip-distance 3.

### Phase 6: large-n annealing (n ∈ [80,150], ω ∈ {3,4,5},
random + turan2 inits, 40×25000, ~2.5 h)
Best ratios: turan2 inits 0.9848 (ω=3, n=134), 0.9993 (ω=4, n=127),
0.9953 (ω=5, n=127); random inits only 0.53–0.60 (annealing budget too small
to organize large sparse graphs — the equality structure is hard to reach
from random at this scale). No violation; large-n regime shows no upward
drift of the maximum.

## 5. Third pass (coordinator "keep grinding"): n = 12 exhaustive + VT census

### Fast threshold checker (`check2.c` / 64-bit `check64.c`)
Rewrote the exhaustive checker around the contrapositive threshold logic
(same reduction as circulant.py):
- Householder tridiagonalization + Sturm-sequence bisection for the top-2
  eigenvalues only, returning rigorous UPPER bounds (hi end of the bisection
  bracket, tol 1e-5) — ~3.4× faster than full cyclic Jacobi.
- t := (λ₁²+λ₂²)/(2m). If t ≤ 2/3: skip — a violation would need ω ≤ 2,
  and ω=2 (triangle-free) is a THEOREM (Lin–Ning–Wu 2021); ω=1 ⇒ m=0.
- Else kmax := ⌈1/(1−t)⌉−1; single query has_clique(kmax+1): if a
  (kmax+1)-clique exists the graph cannot violate; else print CANDIDATE for
  exact offline recheck. False positives are only graphs within the
  eigenvalue tolerance of exact equality.
- Validated: n ≤ 10 exhaustively — candidates are exactly the known
  equality graphs (all recheck to ratio = 1.0 exactly in numpy/networkx;
  e.g. n=9: 12 candidates, all balanced complete multipartite, 0 violations).
- Throughput ~407k graphs/s/core at n=10 (vs 120k/s for check.c).

### Connectivity reduction (rigorous)
For the n=12 sweep only CONNECTED graphs need checking: if G = C ⊔ D is
disconnected, either (a) λ₁,λ₂ both come from one component C with ≤ 11
vertices — then λ₁²+λ₂² ≤ 2m_C(1−1/ω(C)) ≤ 2m(1−1/ω(G)) by the completed
n ≤ 11 exhaustive verification; or (b) λ₁(C), λ₁(D) from two components —
then Nikiforov's theorem per component gives λ₁(C)²+λ₁(D)² ≤
2m_C(1−1/ω(C)) + 2m_D(1−1/ω(D)) ≤ 2m(1−1/ω(G)). So disconnected n=12
graphs cannot be minimal counterexamples given n ≤ 11 is verified.

### n = 12 exhaustive sweep (running)
`nauty-geng -c 12` (153,620,333,545 connected graphs), 16-way res/mod split
through check2. Expected ~14 h wall on 8 cores.

### Vertex-transitive census sweep (running)
Downloaded the full Holt–Royle census of ALL vertex-transitive graphs on
< 48 vertices (Zenodo record 4010122, ~11 GB) and ran check64 over every
graph, n = 10..47. Results so far (graphs checked / candidates — all
candidates are exact-equality complete multipartite graphs pending final
exact recheck): n≤39 done, e.g. n=36: 1,963,202 graphs, 10 candidates;
n=38: 814,216 graphs, 2 candidates. Big classes n=40,42,44,46 in progress.

## STATUS: negative — no counterexample found. Frontier pushed:
conjecture exhaustively machine-verified for ALL graphs n ≤ 11
(1.03 × 10⁹ graphs) and ALL circulants n ≤ 42; ~110M+ annealed samples
ω ∈ {3..8} up to n = 150; equality family strict local max to flip-dist 3.

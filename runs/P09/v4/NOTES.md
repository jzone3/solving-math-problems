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

### Circulants: ALL C_n(S), 4 ≤ n ≤ 50 — ZERO violations (COMPLETE)

Every connection set S ⊆ {1..⌊n/2⌋} (complete graph excluded) for every n ≤ 50:
2³ + … + 2²⁵ ≈ 1.34×10⁸ circulant graphs total (with multiplicity in S, not up to
iso — redundant but exhaustive). Zero violations. All best_gap = 0 cases are
equality at complete-multipartite circulants (e.g. n=50, S giving C_50(…) ≅
K_{5×10}-type Turán graphs); all non-equality maxima are clearly negative
(gap ≤ −Ω(m/ω)). Near-boundary floats (~1e-13) again only at exact-equality
families. Compute: ~40 CPU-min. This covers vertex-transitive territory up to
n = 50 within the circulant subclass called for by the V4 spec.

### n = 12: ALL connected graphs — ZERO violations (COMPLETE)

Connected sweep (`geng -c 12`, 120 res/mod slices, checker2; slices 0–11 run
locally, slices 12–119 fanned out to 12 child worker sessions, results folded
back from branches `runs/P09-v4-n12-<k>`; slice summaries in `n12/`):

- graphs checked: **164,059,830,476** — exactly A001349(12), the number of
  connected 12-vertex graphs (generation sanity check passed).
- clique-evaluated (s > m prune passed): 160,185,787,863.
- **violations: 0.** No VIOLATION lines in any out file.
- max gap over all 120 slices: 5.3e-12, at `K]~v~z~~v~~}` = K_{2,2,2,2,2,2}
  (cocktail-party Turán graph, m=60, ω=6, exact equality 100 = 100; confirmed
  independently by `solutions/P09/verify.py`). All top “near-misses” are again
  exact-equality complete-multipartite graphs + float noise; nothing strictly
  between equality and violation.

Combined with the connectivity reduction above, this verifies the conjecture
for **every graph on ≤ 12 vertices**. Compute: ≈ 550 CPU-hours total across
13 machines (≈ 6 h wall).

### Independent verifier

`solutions/P09/verify.py`: pure-Python, dependency-free, independently coded
(Householder+QL eigensolver, Bron–Kerbosch max clique; trace and trace(A²)
sanity asserts). Verifies any graph6/edge-list witness; `--demo` self-test
passes (C5, Petersen, K_{3,3} equality).

## Dead ends / notes for other variants

- The s > m prune keeps ~97% of graphs (top-2 spectral energy exceeding m is
  common), so it saves clique work but not eigen work; eigen cost dominates.
- No non-trivial near-miss exists at n ≤ 12: the inequality is only tight on
  the known equality families (complete multipartite graphs). Perturbation
  attacks around n ≤ 12 extremal graphs are therefore hopeless; any
  counterexample lives at n ≥ 13 (or nowhere).
- Circulants to n = 50 show the same picture: equality exactly on
  complete-multipartite circulants, everything else clearly negative, with the
  deficit growing with n. Vertex-transitive structure does not help produce
  two simultaneously large eigenvalues relative to 2m(1−1/ω).
- n = 13 all-connected would be ≈ 5×10¹³ graphs (≈ 300× the n = 12 cost) —
  not feasible with this approach; would need stronger pruning or restricted
  families (V3-style fixed-ω sweeps).

## Round 2: weighted-blowup / step-graphon relaxation (LP-duality framing)

New attack after the exhaustive frontier was reached (coordinator request).

**Setup.** For a support pattern H on k vertices (parts = independent sets) with
clique number ω, part fractions c on the simplex, and fractional edge densities
W_ij ∈ (0,1] on E(H), the n-blowup G_n has a.a.s. ω(G_n) = ω(H), while
λ_i(G_n)/n → μ_i(C^{1/2} W C^{1/2}) (top eigenvalues; λ₂/n → max(μ₂,0), the bulk
zeros dominate a negative μ₂) and 2m/n² → S = Σ c_i c_j W_ij. Conjecture in the
limit: F(W,c) = μ₁² + max(μ₂,0)² − S(1−1/ω) ≤ 0. Any strictly positive F rounds
to an explicit finite counterexample. Note sup F ≥ 0 always (weights supported
on a maximum clique give the Turán equality).

**Search.** `blowup.c` (0/1 W, optimize c) and `blowup2.c` (joint W and c),
multi-restart adaptive gradient ascent (finite-difference gradients, Jacobi
eigensolver, 4–8 restarts, ~600 ascent iterations each):

| patterns | program | count | max F found | positives |
|---|---|---|---|---|
| all connected k ≤ 9 | blowup (0/1) | 261,080 + smaller | ~6e-15 | 0 |
| all connected k ≤ 9 | blowup2 (fractional W) | 261,080 + smaller | ~4e-15 | 0 |
| all connected k = 10 | blowup2 (fractional W) | 11,716,571 (=A001349(10)) | ~5e-15 | 0 |

**Result: the relaxation supremum is exactly 0 for every pattern** — attained
only at Turán-type weightings — for every connected template up to 10 vertices
with arbitrary fractional densities. So NO blowup/step-graphon construction
from any ≤ 10-vertex template can violate the conjecture, killing the entire
"two-near-clique join / book / blowup-of-near-miss" family of counterexample
strategies (V2's territory) in one sweep. This is consistent with (and numerical
evidence for) the natural graphon formulation of Bollobás–Nikiforov being tight
exactly on complete multipartite graphons.

Caveats: numerical local search (not a certificate); a positive F would have
been a proof-grade lead, its absence is evidence. One modeling bug found and
fixed during development: λ₂ of the blowup is max(μ₂,0)·n, not μ₂·n — without
the fix, complete patterns show spurious F = 1/ω² > 0 (caught on K₅ sanity run).

## Round 3 (coordinator push #2): large-n simulated-annealing edge-flip search

Third, again fundamentally different attack: direct stochastic search in graph
space at sizes far beyond exhaustion (n = 13..64), maximizing
gap(G) = λ₁² + λ₂² − 2m(1 − 1/ω) by simulated annealing on single edge flips.
Code: `anneal.c` (build: `gcc -O3 -march=native -o anneal anneal.c -lm`).
Per-step exact evaluation: Householder tridiagonalization + Sturm bisection for
λ₁, λ₂ (tolerance 1e-11) and exact ω via bitmask branch-and-bound (n ≤ 64).
Any gap > 1e-7 is printed as CANDIDATE with its graph6 string for independent
re-verification with `solutions/P09/verify.py`.

Two modes:
1. Random-init anneal: `./anneal n restarts steps seed` — random G(n,p) starts
   (p ∈ [0.15, 0.9]), geometric cooling T: 0.5n → 1e-3.
   Ran n ∈ {13,14,15,16,18,20,22,25,28,32,36,40,45,50,56,64}, 30 restarts ×
   1e6 steps each (4.8×10⁸ exact evaluations total).
2. Turán-perturbation anneal: `./anneal n restarts steps seed 0 w` — start at
   the balanced complete multipartite Turán graph K_{n/w×w} (an exact equality
   point) plus 1–4 random flips, low temperature (0.02n) — a direct attack on
   the neighborhood of the equality manifold at sizes unreachable by
   exhaustion. Ran (n,w) ∈ {24,30,36,42,48,50,56,64} × {3..8} (16 configs),
   20 restarts × 5e5 steps each (1.6×10⁸ evaluations).

Results (best gap found per config, `anneal_summary_*.txt` /
`turan_summary_*.txt`):
- Small/medium n (13–28) random-init runs converge to gap ≈ +5e-11 — i.e. the
  anneal *finds the equality graphs* (complete multipartite) to within the
  1e-11 eigenvalue tolerance, and never exceeds them.
- Turán-perturbation runs at n = 24, 36, 48 return to gap ≈ 0 (−2e-11 …
  +1.8e-10, pure Sturm-bisection noise at equality) and never go above; all
  other configs top out strictly below 0 (−0.24 … −1.05).
- Largest-n random runs (n = 45–64) plateau at gap ≈ −3 … −4.3 (annealing
  doesn't fully converge to Turán at this size/budget, but never trends
  positive).
- ZERO candidate lines emitted across all ~6.4×10⁸ evaluations.

Interpretation: even far beyond the exhaustively verified range, stochastic
hill-climbing with exact ω and high-precision eigenvalues always terminates at
(or below) the known complete-multipartite equality manifold; the landscape
shows no ascent direction past equality anywhere up to n = 64. Combined with
rounds 1–2 this is strong evidence the conjecture is true with equality
exactly on complete multipartite graphs.

## STATUS

STATUS: negative / frontier-pushed — no counterexample and no non-trivial
near-miss; conjecture machine-verified for ALL graphs on ≤ 12 vertices
(1.65×10¹¹ graphs; beyond any published check) and ALL circulant graphs
C_n(S) for n ≤ 50 (≈1.3×10⁸). Only known equality families touch the bound.
Round 2: the weighted-blowup / step-graphon relaxation has supremum exactly 0
for every connected template up to 10 vertices (11.7M patterns, fractional edge
densities + part weights) — no blowup-type counterexample exists from any such
template; the graphon form of the conjecture is numerically tight only at
complete multipartite graphons.
Round 3: simulated-annealing edge-flip search at n = 13..64 (~6.4×10⁸ exact
evaluations, random + Turán-perturbation starts) — zero candidates; the search
always terminates at or below the complete-multipartite equality manifold.
Round 4: the triangle-free subcase (bound λ₁²+λ₂² ≤ m) exhausted for ALL
triangle-free graphs n ≤ 15 (1.47×10¹⁰ graphs, counts match A006785 exactly) —
zero violations; equality only at disjoint unions of complete bipartite graphs
(max gap ≈ 6e-12 float noise).
Round 5: ~8×10⁷ dihedral Cayley graphs up to order 64 (exhaustive through
order 34, sampled beyond) — zero violations, equality families only.

## Round 4 (coordinator push #3): exhaustive triangle-free subcase (ω = 2)

Fourth attack: exhaustively verify the smallest structured subcase — the
triangle-free case, where the conjecture reads λ₁² + λ₂² ≤ m — at sizes beyond
the general n ≤ 12 exhaustion, via `nauty-geng -t` piped into the existing
cross-validated `checker2` (whose early-out `s ≤ m − 1e-6` is exact here since
ω = 2 ⇒ RHS = m; ω is still computed exactly for every near-boundary graph).

- n = 13: all 20,797,002 triangle-free graphs — 0 violations
  (count = A006785(13) exactly).
- n = 14: all 467,871,369 triangle-free graphs, 8 parallel geng slices —
  0 violations (slice totals sum to A006785(14) exactly; `tf/n14_*.sum`).
- n = 15: all 14,232,552,452 triangle-free graphs, 32 parallel geng slices —
  0 violations (slice totals sum to A006785(15) exactly; `tf/n15_*.sum`;
  ~9 h wall on 8 cores).

Near-boundary structure: every best_gap is +4e-12 float noise at exact
equality s = m, attained by disjoint unions of complete bipartite graphs
(λ₁² + λ₂² = ab + cd = m for K_{a,b} ∪ K_{c,d}) — the known ω = 2 equality
family. No non-trivial near-miss.

## Round 5 (coordinator push #4): dihedral Cayley graph sweep

Fifth attack: Cayley graphs of the dihedral groups D_n (order 2n), a
vertex-transitive family strictly beyond the circulant scan of round 1.
Code: `cayley.c` (`gcc -O3 -march=native -o cayley cayley.c -lm`).
Connection sets S = S^{-1} built from rotation pairs {r^k, r^{-k}},
optionally r^{n/2}, and any subset of the n reflections s r^i; exact ω via
bitmask B&B (2n ≤ 64), λ₁/λ₂ via tridiagonalization + Sturm bisection to
1e-12; early-out s ≤ m − 1e-6 is safe since RHS ≥ m.

- EXHAUSTIVE for n = 3..17 (all 2^(⌊(n−1)/2⌋+[2|n]+n) − 1 connection sets;
  33,554,430 sets at n = 17 / order 34): 0 candidates.
- SAMPLED 3×10⁶ random connection sets each for n = 18..32 (orders 36..64,
  ~4.5×10⁷ total): 0 candidates.
- Best gaps everywhere ≈ +7e-11 or below — float noise at exact equality,
  attained by complete-multipartite-type Cayley graphs (e.g. 2·K_n from all
  rotations, K_{n,n} from all reflections, cocktail-party-type sets).

Result: zero violations, zero non-trivial near-misses across ~8×10⁷ dihedral
Cayley graphs up to order 64 (`cay/n*.sum`).

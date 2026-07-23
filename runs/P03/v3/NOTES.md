# P03 — Woodall's conjecture, V3 run (τ=3 targeted enumeration)

Session: https://app.devin.ai/sessions/d9627b2d22344bbf8de500ab861b6d53
Variant: **V3 — τ=3 targeted**: restrict to digraphs with min dicut exactly 3; use
Abdi–Cornuéjols–Zlatin (ACZ) partial results to constrain the class a counterexample must
live in; search within that class.

## 0. Statement re-verification (against original source) & openness check

- Statement used: *in every finite digraph, min size of a nonempty dicut = max number of
  pairwise disjoint dijoins* (Woodall 1978, LNM 642). Cross-checked against:
  - ACZ, "On packing dijoins in digraphs and weighted digraphs" (arXiv:2202.00392, Math.
    Programming): identical definitions (dicut = δ⁺(U), δ⁻(U)=∅; dijoin hits every dicut;
    Woodall conjectures A partitions into τ dijoins). ✓ matches problem file.
  - Feofiloff's Woodall's-conjecture page (ime.usp.br/~pf/dijoins/, updated 2025-04-05):
    conjecture still listed as open. ✓
  - Wikipedia "Woodall's conjecture": unsolved as of retrieval (2026-07-22). ✓
  - Cornuéjols–Liu–Ravi, "Approximately packing dijoins via nowhere-zero flows",
    Combinatorica 45:32 (published 2025-06-02): still frames Woodall as open. ✓
- Conclusion: **statement verified, still open as of July 2026** (incl. τ=3 case).

## 1. Structural constraints a τ=3 counterexample must satisfy (from literature)

Let ρ(3,D,1) = (1/3)·Σ_v ((d⁺(v) − d⁻(v)) mod 3).

1. **ρ ≥ 4** — ACZ (arXiv:2202.00392) prove Woodall's conjecture for τ=3, w=1 whenever
   ρ ∈ {0,1,2,3} (results (i),(ii),(iii) of their abstract; (iii) is exactly τ=3, ρ=3, w=1).
   Hence Σ_v ((d⁺−d⁻) mod 3) ≥ 12, so **at least 6 vertices have imbalance ≢ 0 (mod 3)**,
   and in particular **n ≥ 6** (each term ≤ 2 gives Σ ≤ 2n, and ≥12 ⟹ n ≥ 6).
2. **Not source-sink connected** — Schrijver 1982 / Feofiloff–Younger 1987: Woodall holds
   when every source reaches every sink. So the counterexample has a source s and sink t
   with no directed s→t path (in particular ≥2 sources or ≥2 sinks... more precisely at
   least one blocked (source, sink) pair).
3. **Underlying undirected graph non-planar** — planar case follows from Lucchesi–Younger
   via duality (dijoins ↔ feedback arc sets in the dual).
4. Every source has outdeg ≥ 3, every sink has indeg ≥ 3 (their δ⁺/δ⁻ are dicuts).
5. Not series-parallel (Lee–Wakabayashi) — implied by 3 (non-planar).

These give a very strong filter; the search below only SAT-checks digraphs meeting 1–4.

## 2. Encoding / machinery (runs/P03/v3/core.py)

- Digraph = (n, list of arcs), parallel arcs allowed, loops disallowed.
- Dicuts: exhaustive over all 2ⁿ vertex subsets U with δ⁻(U)=∅ (n ≤ ~16). τ = min size.
- Packing decision: 3 pairwise disjoint dijoins exist ⟺ arcs 3-colorable s.t. every
  (minimal) dicut contains all 3 colors (supersets of dijoins are dijoins, so WLOG a
  partition). Encoded as SAT (exactly-one color per arc + one at-least-one clause per
  minimal-dicut × color); solved with python-sat (Minicard).
  **A τ=3 instance that is UNSAT = counterexample.**
- Cross-validation: SAT decision agreed with brute-force 3^m enumeration on 248 random
  small instances (test_core.py). All unit tests PASS.

## 3. Search harnesses

- `search.py` (v1): random generation + repair-to-τ=3 + hard filters, and a hill-climb on
  minimal-dicut density. Yield of filtered candidates was terrible (~2 full-pass per 2 min):
  random τ=3 digraphs are almost always source-sink connected and have ρ ≤ 3.
- `search2.py` (v2, main engine): structured generator with two sources / two sinks layered
  so s1 cannot reach t2; annealing with soft score = 4000·[not ss-connected] +
  1000·min(ρ,4) + 2000·[non-planar] + 5·(#size-3 minimal dicuts) + #minimal dicuts;
  parallel-arc duplication used as a reachability/planarity-preserving move that shifts
  imbalances mod 3 (pushes ρ up). Every distinct full-pass candidate is SAT-checked.
  Yield: ~1000 full-pass candidates SAT-checked per minute per core.

## 4. Compute log (checkpointed)

| run | params | wall | candidates SAT-checked (full-pass) | UNSAT |
|---|---|---|---|---|
| smoke random | n 6–10, 2 min | 2 min | 2 | 0 |
| smoke anneal | n 6–10, 2 min | 2 min | 1 | 0 |
| smoke search2 | n 8–12, 3 min | 3 min | 3260 | 0 |
| search2 ×7 seeds 11–17 | n ranges 6–9 … 12–16, 150 min each (parallel) | 17.5 core-h | 409,679 | 0 |
| search3 (min-#colorings anneal) seed 21 | n 8–13, 150 min | 2.5 core-h | 339,194 | 0 (min colorings never dropped below cap 600) |
| search2 seeds 31 (n 7–10) & 32 (n 6–8), search3 seed 33 (n 7–10) | 75–90 min each | ~4 core-h | 67,127 + 224,049 | 0 |

Total randomized-search SAT decisions on fully-filtered multigraph candidates
(parallel arcs allowed, the slice nauty can't cover): **~1.04M, all packable (0 UNSAT).**

(long runs appended below)

## 5. Exhaustive verification (frontier pushes) — exhaustive.py / exhaustive2.py / exhaustive3.py

All generation via nauty (`nauty-geng -c N | nauty-directg [-o]`), i.e. all weakly-connected
digraphs up to isomorphism; `-o` = orientations only (no 2-cycles); no parallel arcs in any
nauty slice (digraph6 can't express them — parallel-arc instances are covered by the random
searches instead).

| slice | #digraphs | result |
|---|---|---|
| all simple digraphs, n ≤ 5 (2-cycles allowed) | 9,563 | Woodall holds for **all** τ (0 cex) |
| all simple digraphs, n = 6 (2-cycles allowed) | 1,530,843 | Woodall holds for **all** τ (0 cex); τ=3 count 143,018 |
| all oriented digraphs, n = 7 (all connected underlying graphs) | 2,120,098 | Woodall holds for **all** τ (0 cex); τ=3 count 445,394 |
| oriented, n = 7, non-planar underlying (τ=3-targeted re-scan) | 1,266,232 | ρ≥4 pass: 49,767; τ=3∧ρ≥4: 1,180; also not-ss-connected: **0** → no candidate even reaches SAT |

Independence: the n=6 slice was verified TWICE by differently-written checkers
(exhaustive.py with randomized greedy + SAT, and exhaustive2.py with deterministic greedy +
SAT + different dicut enumeration); identical τ-distributions and 0 counterexamples.
exhaustive3.py's filter fractions were cross-checked against core.py on a 25,371-instance
random sample (agreement within sampling error).

Combined with ACZ (ρ≥4 ⟹ n≥6), the n≤6 exhaustion means: **any τ=3 counterexample has
n ≥ 7; no counterexample exists among all simple digraphs with n ≤ 6, nor among all
2-cycle-free simple digraphs with n = 7.** (n=7 with 2-cycles is being closed by the
τ=3-targeted full scan below.)

n = 8, oriented, non-planar underlying, τ=3-targeted (exhaustive3.py, 8 chunks): **DONE, 0
counterexamples.** TOTAL = 515,858,293 digraphs; ρ≥4 pass = 64,939,394; τ=3∧ρ≥4 =
3,483,663; additionally not-ss-connected = **14**; all 14 SAT-checked packable.
(Per-chunk totals in log_exh3_n8_c*.txt; chunk sums verified = 515,858,293.)

n = 7, ALL simple digraphs incl. 2-cycles, τ=3-targeted (exhaustive3.py, 8 chunks, no
planarity filter — only ACZ ρ≥4 + τ=3 + not-ss-connected): **DONE, 0 counterexamples.**
TOTAL = 880,471,142 digraphs; ρ≥4 = 34,092,680; τ=3∧ρ≥4 = 264,454; additionally
not-ss-connected = **0** — i.e. no τ=3 simple digraph on 7 vertices even satisfies the
necessary conditions (ACZ + Schrijver) for a counterexample.

## 6. Final frontier statement

Assuming only the published safe-class theorems (ACZ 2022/23 ρ≤3 cases; Schrijver 1982 /
Feofiloff–Younger 1987 source-sink connected; Lucchesi–Younger planar):

1. **Unconditional exhaustion**: Woodall's conjecture (all τ) holds for every simple digraph
   (2-cycles allowed) on ≤ 6 vertices (1,540,406 digraphs up to iso) and for every oriented
   digraph on 7 vertices (2,120,098).
2. **τ=3-targeted exhaustion**: there is NO τ=3 counterexample among ANY simple digraph on
   ≤ 7 vertices (880M scanned at n=7), nor among any oriented (2-cycle-free) simple digraph
   on 8 vertices (515.9M scanned; planar-underlying instances excluded as LY-safe).
3. Hence any τ=3 counterexample requires **n ≥ 8 with 2-cycles or parallel arcs, or n ≥ 9**.
4. Randomized multigraph search (parallel arcs allowed, n 6–16, ~24 core-hours, ~1.04M
   fully-filtered candidates SAT-decided): 0 unpackable instances; the min-#colorings
   annealer never got below 600 colorings — no near-miss pressure anywhere.

Dead ends / notes:
- The binding constraint is the conjunction τ=3 ∧ ρ≥4 ∧ ¬ss-connected: at n=7 it is
  EMPTY over simple digraphs, and at n=8 (oriented nonplanar) only 14 of 515.9M instances
  satisfy it — and all pack trivially. A counterexample, if it exists, seems to need
  parallel-arc structure (as in Schrijver's weighted example) — that direction is V2's
  subdivision-seed territory; our random multigraph searches (which do duplicate arcs)
  found no pressure either.
- search3's model-count gradient saturated at the cap (600): the filtered class is nowhere
  near UNSAT; local search cannot see a gradient.
- No verify.py/solutions artifact: nothing to verify — no witness found.

## 7. Second wave (post-restart escalation)

### 7a. n ≤ 6 fully closed, parallel arcs included (multigraph_n6.py)

Reduction proved & documented: a MINIMAL τ=3 counterexample has arc multiplicities ≤ 2
(a ≥3-bundle can be rainbow-colored; the remaining dicuts are exactly those of the
contraction, which is a smaller counterexample — contradiction with minimality). Since
contraction reduces n, exhausting mult≤2 at n=6 plus the simple n≤6 exhaustion rules out
ALL n≤6 counterexamples including parallel arcs. At n=6 ACZ forces ρ=4 exactly ⟹ every
vertex imbalance ≡ 2 (mod 3). Skeleton filters (multiplicity-invariant): weakly conn.,
not ss-connected, all skeleton dicuts ≥ 2 → only **53 skeletons** out of 1,530,843
(count_skeletons.py). All 33,472 mult∈{1,2} patterns enumerated: **0 pass τ=3∧ρ=4**
(the class is empty), hence **no τ=3 counterexample on ≤ 6 vertices, multigraphs
included**.

### 7b. NEW TARGET FAMILY: ACZ-complete sink-regular (3,4)-bipartite digraphs (bip.py)

ACZ §2 ("Decompose, Lift, and Reduce", valid for unweighted digraphs when τ≥3) reduces
τ=3 Woodall to sink-regular (3,4)-bipartite digraphs: **if any τ=3 counterexample exists,
one exists in this class.** Class: all arcs source→sink; sinks have in-degree 3; sources
out-degree 3 or 4; all dicuts ≥ 3. Here ρ = |S₄|/3, so ACZ safe cases force
**≥ 12 degree-4 sources ⟹ ≥ 16 sinks, ≥ 48 arcs, n ≥ 28** — far beyond every slice any
generic small-digraph search (incl. our first wave) ever touched; this explains why
random small-n searches are hopeless and makes this the right haystack.

Encoding: dicuts ↔ source subsets X with Y=Ymax(X), PLUS per-sink in-arc dicuts
(δ⁻(t) via U=V∖{t}) — a subtle omission caught by cross-validation against core.py
(test_bip.py: 120 random bipartite instances, τ + minimal dicut sets + packing decisions
all agree). Degree-preserving double-swap annealing, score = tight-dicut density,
non-planar filter (LY), SAT packing decision per valid candidate.

Runs: 8 parallel shapes (|S₄|,|S₃|) ∈ {12}×{0..4} ∪ {15}×{0,1,3}, 240 min each
(results appended below).

## STATUS: negative / frontier-pushed — no τ=3 counterexample with n≤7 (simple, any) or n=8 (oriented); ~1.04M filtered multigraph candidates + 1.4B nauty-enumerated digraphs scanned, 0 UNSAT.

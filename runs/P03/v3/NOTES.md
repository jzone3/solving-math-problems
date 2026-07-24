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

Engines: bip.py (tight-dicut-density score, exact minimal dicuts every step),
bipfast.py (numpy-vectorized cut-size sweep, ~25x faster; exact minimal dicuts + SAT only
on accepted improvements; τ agreement with bip.py cross-checked on 60 instances),
bip3.py (min-#colorings gradient, cap 400).

### 7c. Results of the bipartite-class runs (~4h x 12 processes, 8 cores)

| engine  | shapes (|S₄|,|S₃|)            | iters | τ=3 nonplanar SAT decisions | UNSAT |
|---------|-------------------------------|-------|------------------------------|-------|
| bip.py  | (12,0),(12,1),(12,2),(12,3)   | 380k  | 4,630                        | 0     |
| bip.py (partial, replaced) | (12,4),(15,0),(15,1),(15,3) | ~5k | ~120         | 0     |
| bipfast | (12,4),(15,0),(15,1),(15,3),(18,0),(12,8) | 7.6M | 6,533            | 0     |
| bip3    | (12,0),(12,2)                 | 80k   | 79,938 min-coloring counts   | 0 (never < 400 cap) |

Every SAT decision here is a full check of a τ=3, ρ≥4, non-planar member of the
ACZ-complete class (n = 28–44, 48–72 arcs) — a regime NO previous slice of this run (or
any generic small-n scan) could reach. All packable; no near-misses (bip3's coloring-count
gradient again saturated at its cap).

Exhaustion of the class is impossible (nauty-genbg count of just the minimal shape
12+16, (4,3)-biregular, did not terminate in 120s → astronomically many), so annealing
coverage is the practical frontier here.

## 8. Third wave: orbit-reduction (Kramer–Mesner style) exhaustive closure (bipsym4.py)

Target: the MINIMAL shape of the ACZ-complete class — 12 degree-4 sources × 16 degree-3
sinks, 48 arcs (minimum possible size of a τ=3 counterexample within the class). Assume
an automorphism σ of order 4 acting freely on the sources; freeness on sources FORCES
freeness on all of V (a σ-fixed or 2-orbit sink would need in-degree divisible by 4 or
with pair-sum divisible by 4; in-degree is 3, pair-sum 6 — impossible), so the scan
covers ALL members of the minimal shape admitting an order-4 automorphism free on sources.

Orbit encoding: sources (a,i), a∈{0,1,2}; sinks (b,i), b∈{0..3}; i∈Z4; graph determined
by 3 representative neighborhoods. Sink-regularity ⟺ 3×4 contingency table c (rows sum
4, cols sum 3): 415 tables, 189,399,040 raw offset assignments. Exact dedup of the 4⁴
sink-rotation subgroup (rotation-minimal columns) + row-sort + hash dedup → 686,660
candidates (remaining group not deduped — harmless overcounting; exhaustiveness intact).

Result (8 shards, ~55 min each): 686,660 candidates, 685,334 with τ=3, 676,378
non-planar → full SAT 3-dijoin-packing decision: **0 UNSAT**. Combined with waves 1–2:
**no τ=3 counterexample exists in the minimal ACZ shape with any order-4 automorphism
acting freely on sources** — an exhaustive, citable closure of the symmetric subclass.

Not pursued (documented dead ends): Z2-free at minimal shape (6.3×10¹⁵ raw — hopeless);
Z3 (order-3, 1–7 fixed sinks: ~10⁸ candidates per case ≈ days); shape (12,4) under Z4
(3.9×10⁹ candidates).

## 9. Fourth wave: C engine — exhaustive order-3 symmetry closure (zscan.c)

zscan.c (bitmask dicut sweep + WalkSAT 3-coloring with full-verification CEGAR loop;
WalkSAT success is a rigorous positive certificate since the final coloring is verified
against ALL dicuts; unresolved candidates dumped for exact SAT in Python — zverify.py).
Cross-validated against the Python bip.py pipeline on 367 sampled candidates (τ flags and
packing certificates: 0 mismatches).

Scope: minimal ACZ shape (12×16, 48 arcs) with an order-3 automorphism free on sources
(4 orbits of 3). Sinks: k orbits of size 3 + f fixed sinks (3k+f=16, f∈{1,4,7,10,13,16});
a fixed sink's 3 in-arcs are exactly one full source orbit ("owner"). Owners canonical
non-decreasing (exact dedup of fixed-sink permutations); offset columns rotation-minimal
(exact dedup of the 3^k rotation subgroup).

Results (≈6 h wall, 8 cores, ~1.1k candidates/s/core):

| f  | candidates  | τ<3 rejected | packed (certified) | dumped/UNSAT |
|----|-------------|--------------|--------------------|--------------|
| 1  | 178,704,900 | 6,480        | 178,698,420        | 0            |
| 4  | 15,039,240  | 0            | 15,039,240         | 0            |
| 7  | 369,384     | 0            | 369,384            | 0            |
| 10 | 5,700       | 0            | 5,700              | 0            |
| 13 | 76          | 0            | 76                 | 0            |
| Σ  | 194,119,300 | 6,480        | 194,112,820        | **0**        |

f=16 (σ fixes every sink) forces disjoint unions of complete K_{3,4} components
(identical neighborhoods within each source orbit); K_{3,4} has τ=3 and packs (checked),
so the whole f=16 family packs componentwise — no scan needed.

Combined with wave 3: **no τ=3 counterexample exists in the minimal ACZ shape (the
smallest possible shape of any τ=3 counterexample after the ACZ reduction) admitting ANY
automorphism of order 3 or 4 acting freely on the sources** — 194.8M candidates
exhaustively decided, 0 unpackable.

## 10. Fifth wave: C annealed sampling of the FULL (asymmetric) ACZ region

The order-3/4 symmetric subclasses being exhausted, the remaining haystack is asymmetric
(or ≤order-2-symmetric) members of the ACZ-complete class. Ported the sampler to C
(`ascan.c`): random configuration-model start, degree-preserving double-swap mutations,
hill-climb on tight-dicut count (harder instances = more tight cuts), random restarts
after 400 stale steps. EVERY τ=3 candidate along every trajectory gets a CERTIFIED
packing decision (WalkSAT 3-coloring + full-verification CEGAR against ALL dicuts, as in
zscan.c); any unresolved candidate is dumped as an `ACAND` line and exact-SAT-checked by
`averify.py` (independent bip.py pipeline). Cross-validated on 400 debug samples
(τ flags + packing certificates vs exact Python SAT): 0 mismatches.

Shapes (all satisfy ρ≥4, i.e. n4≥12 with n4≡0 mod 3): (n4,n3) = (12,0) minimal n=28;
(12,3) n=34; (12,4) n=36; (15,0) ρ=5 n=35. 8 workers × 4 h wall:

| shape (n4,n3) | workers | restarts | τ=3 certified decisions | UNSAT/dumped |
|---------------|---------|----------|-------------------------|--------------|
| (12,0)        | 4       | 249,628  | 72,532,184              | 0            |
| (12,3)        | 2       | 16,685   | 5,545,274               | 0            |
| (12,4)        | 1       | 3,921    | 1,380,936               | 0            |
| (15,0)        | 1       | 6,561    | 1,939,851               | 0            |
| Σ             | 8       | 276,795  | **81,398,245**          | **0**        |

That is 81.4M certified 3-dijoin-packing decisions inside the full (unrestricted) ACZ
class — ~7,200× the wave-2 Python annealing coverage (11.3k) — with 0 unpackable
instances and 0 candidates even surviving the heuristic packer. Together with the
exhaustive symmetric closures, the empirical evidence within the ACZ-complete class is
now: every sampled/enumerated τ=3 member packs, across ~276M decided instances.

Second batch (5 h × 6 workers, new shapes (12,1) n=29, (12,2) n=30, (15,1) n=37 plus
more (12,0)): 296,437 restarts, **87,396,129 further certified τ=3 packing decisions,
0 UNSAT** — wave-5 sampling total 168.8M.

## 11. Sixth wave: exhaustive closure of NON-free order-3 automorphisms

Wave 4 closed order-3 automorphisms acting FREELY on the 12 sources. Wave 6 attacks the
non-free case (`z3nf.c`): σ of order 3 with q>0 fixed sources (source orbits p=3..0,
q=12−3p ∈ {3,6,9,12}); sinks k orbits + f fixed (f ∈ {1,4,7,10,13,16}). σ forces:
a fixed source's 4-neighborhood is σ-invariant (one full sink orbit + 1 fixed sink, or
4 fixed sinks); a fixed sink's in-neighborhood is one full source orbit XOR 3 fixed
sources; orbit sources use Z3-offset subsets per sink orbit and may "own" fixed sinks.
Enumeration is exhaustive up to isomorphism (overcounting allowed): owners and
fixed-source choices canonical non-decreasing, offset columns rotation-minimal.
Same certified engine as zscan/ascan (τ bitmask sweep; WalkSAT+CEGAR colorings verified
against ALL dicuts; unresolved → exact Python SAT). Cross-validated on 1,204 debug
samples spanning 5 (p,f) cases vs the exact bip.py pipeline: 0 mismatches.

Results — all 15 tractable (p,f) cases fully scanned:

| case | cand | τ<3 | certified packed |
|------|------|-----|------------------|
| Σ over (p,f): p=3 all f; p=2 all f; p∈{0,1}, f∈{1,4,7} | 17,602,772 | 4,864,087 | 12,738,685 |

(0 dumped, 0 UNSAT; f=1 with p≤2 and several other cases are structurally empty.)
Largest cases: (2,10) 4.99M, (1,7) 3.47M, (3,1) 2.90M, (0,7) 2.61M.

Residual gap within order-3: p∈{0,1} (q≥9 fixed sources) combined with f∈{10,13,16}
(≥10 fixed sinks) blows up combinatorially (the fixed–fixed part degenerates to a
near-unrestricted 12×16-ish bipartite enumeration; COUNT-ONLY mode for (1,10) did not
terminate in >4.5 h of dedicated runtime, i.e. ≳10¹⁰) — plus (0,16) which is the trivial σ (excluded by definition). So the
combined exhaustive statement is now: **no τ=3 counterexample in the minimal ACZ shape
admits any automorphism of order 4 free on sources, or ANY order-3 automorphism having
at least 2 source orbits or at most 7 fixed sinks** (~212M candidates decided overall,
0 unpackable).

## STATUS: negative / frontier-pushed — no τ=3 counterexample: n≤6 CLOSED incl. parallel arcs (mult≤2 reduction; viable class empty); n≤7 simple + n=8 oriented exhausted (1.4B digraphs); ~1.04M filtered multigraph candidates; ~11.3k annealing SAT decisions inside the ACZ-complete sink-regular (3,4)-bipartite class (ρ≥4, n=28–44) — 0 UNSAT; NEW: EXHAUSTIVE closure of the minimal ACZ shape (12×16, 48 arcs) under ANY automorphism of order 3 or 4 acting freely on sources — 194.8M candidates decided (676,378 SAT + 194.1M certified colorings), 0 UNSAT; NEW (wave 5): 81.4M certified packing decisions via C annealed sampling of the FULL asymmetric ACZ region (shapes (12,0),(12,3),(12,4),(15,0); ρ=4–5, n=28–36), 0 UNSAT — ~276M total decided instances in the ACZ-complete class, all pack; NEW (wave 6): non-free order-3 closure — all 15 tractable (p,f) cases exhausted (17.6M candidates, 12.7M certified packings, 0 UNSAT), upgrading the exhaustive statement to: no minimal-shape τ=3 counterexample admits an order-4 automorphism free on sources, or ANY order-3 automorphism with ≥2 source orbits or ≤7 fixed sinks; plus 87.4M more certified sampling decisions (wave 5 batch 2; shapes (12,0),(12,1),(12,2),(15,1)) — cumulative ~381M decided ACZ-class instances, every one packs.

# P03 Woodall's conjecture — V5 (literature-first) run notes

Session: https://app.devin.ai/sessions/7aa363207b174207af62780e6f2cc8fb
Variant: V5 — digest known partial results, map the "safe" digraph classes where the
conjecture is proven, design the search to live entirely outside them, then compute.

## 1. Statement re-verification (against original-source formulations)

- Woodall 1978 (via Schrijver's discussion notes, homepages.cwi.nl/~lex/files/woodall.pdf;
  Feofiloff's 2025 survey ime.usp.br/~pf/dijoins; Wikipedia rev. 2026-04-29):
  *In every digraph, the maximum number of pairwise disjoint dijoins equals the minimum
  size of a dicut.* Matches problems/P03-woodall-dijoins.md exactly.
- Equivalent form used here (Schrijver): for k >= 2, A can be partitioned into k
  "strengthening" sets iff every dicut has size >= k. Note: k disjoint dijoins exist iff
  the arc set partitions into k dijoins (supersets of dijoins are dijoins), so the SAT
  check below tests an exact partition.
- Still open as of July 2026: Wikipedia (edited 2026-04) lists it as an unsolved problem;
  the newest literature (Combinatorica 2025 "Approximately Packing Dijoins via
  Nowhere-Zero Flows"; JGT 2026 chordal-digraph min-max paper) all state it open.
  Cornuéjols's $5000 prize (Open Problem Garden) still listed.

## 2. Literature digest → map of safe classes

A counterexample D (min dicut tau = k, no k disjoint dijoins) must avoid ALL of:

| # | Safe class / condition | Source |
|---|---|---|
| 1 | tau <= 2 | Frank's observation (Schrijver's book Thm 56.3): k=2 always packs |
| 2 | non-DAG reducible | contract strong components: WLOG D is a DAG |
| 3 | source-sink connected digraphs (every source reaches every sink by a dipath) | Schrijver 1982 (Min-max relations for directed graphs), Feofiloff–Younger 1987 |
| 4 | rho(k, D) <= 2, where rho = (1/k) * sum_v ((outdeg-indeg) mod k); and for k=3, even rho = 3 | Abdi–Cornuéjols–Zlatin, SIDMA 2023 (arXiv:2202.00392): rho in {0,1} equitable packing, rho=2 packing; rho=3 & tau=3 & w=1 partitions into 3 dijoins. So a tau=3 counterexample needs rho(3,D) >= 4 |
| 5 | planar digraphs (per problem file; via LY-dual feedback-arc-set formulation) | problem file P03; Feofiloff survey |
| 6 | underlying graph chordal | Cornuéjols–Liu–Ravi 2025 (arXiv:2501.10918, IPCO/JGT 2026): weighted chordal digraphs pack |
| 7 | tau >= 6 with NZ 6-flow guarantee: every digraph has floor(tau/6) disjoint dijoins; 6p-edge-connected underlying gives floor(tau*p/(2p+1)) | Combinatorica 2025 (Chen–?, nowhere-zero flows). For tau=3 gives nothing binding, but underlying graphs with NZ 3-flows admit 1 dijoin trivially — not restrictive |
| 8 | Minimal-counterexample structure ("reduced"): acyclic, weakly 3-arc-connected, every dicut of size k determined by a single source or single sink, all sources/sinks have degree exactly k, all internal vertices have degree 3 with (in,out) in {(1,2),(2,1)} | Schrijver's discussion notes, Thm 3 |

Additional notes:
- ACZ 2023 also prove: A always partitions into a dijoin and a (tau-1)-dijoin.
- Dyadic packing (SIDMA 2024): a max *fractional* packing with dyadic values always
  exists — LP side is well-behaved; obstruction, if any, is purely integral.
- Known weighted (Edmonds–Giles) counterexamples: Schrijver 1980 (7 nodes, 14 arcs,
  0/1 weights), Cornuéjols–Guenin 2002 family, Williams. All have tau(w)=2.
  Their unweighted versions pack (weight-0 arcs are the whole obstruction).
- rho >= 4 with the reduced degree shape: sources/sinks (deg 3, k=3) contribute 0 to rho
  (excess ±3 ≡ 0 mod 3). An internal (in=1,out=2) vertex has excess +1 → contributes 1;
  an (in=2,out=1) vertex has excess −1 ≡ 2 mod 3 → contributes 2. rho >= 4 requires the
  internal contributions to sum to >= 12, so at least 6 internal vertices are needed
  (all type (2,1)), and generically more. This lower-bounds counterexample size:
  n >= 2 sources/sinks + 6 internal = 8 vertices, >= 12 arcs.

## 3. Search design (outside ALL safe classes)

Target region for candidates (k=3):
DAG, tau=3, NOT source-sink connected, rho(3,D) >= 4, underlying non-planar,
underlying non-chordal, with the Schrijver reduced degree shape as generation prior
(sources outdeg=3, sinks indeg=3, internal deg-3 (1,2)/(2,1)).

Code: `harness.py` (dicut enumeration by bitmask over closed sets; tau; minimal
dicuts; SAT partition-into-3-dijoins via Glucose4 with exactly-one color per arc and
"every color hits every minimal dicut" clauses; rho/planarity/chordality/ss-connectivity
filters). `search.py` phase A = random shape-constrained screening (SAT-checks *every*
tau=3 sample, so we also cover safe-class instances as sanity), phase B = simulated
annealing on arc rewires toward region-score 0, SAT-checking every region hit.

Sanity tests: `test_harness.py` — ALL PASS (path, K3,3 orientation tau=3 packs 3 not 4,
disconnected => tau 0, smoke DAG).

## 3b. Size lower bound for a minimal tau=3 counterexample (derived here)

Combining the safe classes gives a sharper bound than any single source states:
- Reversal symmetry: reversing all arcs preserves tau and nu, and maps rho to
  rho-bar. So a counterexample needs BOTH rho(3,D) >= 4 and rho(3,rev D) >= 4.
- In the reduced shape (Schrijver): internal type (in1,out2) contributes 1 to rho and
  2 to rho-bar; type (in2,out1) contributes 2 and 1. With a type-A and b type-B
  internals: a + 2b >= 12 and 2a + b >= 12 => a + b >= 8: at least 8 internal vertices.
- Stub balance forces a - b = 3(#sinks - #sources).
- A DAG with a single source is automatically source-sink connected (every vertex is
  reachable from the unique source), and dually for a single sink. So >= 2 sources and
  >= 2 sinks are needed to escape the Schrijver/Feofiloff-Younger safe class.
- Minimum: 2 sources + 2 sinks + 8 internals (a = b = 4), n = 12, 18 arcs.
  (Next shapes: (2,2,10) n=14 / 21 arcs; (3,2,9)+(2,3,9) n=14; etc.)
This focuses the targeted deep runs (`runA_min.log`, `runB_min.log`).

## 4. Run log

- 2026-07-22 ~20:40 UTC calibration: phase A, 60 s, seed 1, sizes up to n=16:
  17135 generated / tau distribution 0:84, 1:1256, 2:8745, 3:7050 / 7050 SAT-checked /
  290 in full target region / **0 non-packing**.

- 2026-07-22 20:22–22:22 UTC main wave (7 parallel 2h runs, shape-constrained DAGs
  n<=16):
  - phase A random screening, seeds 11–14: 8.2M DAGs generated, 3.376M with tau=3
    SAT-checked (every one), 147,791 of them in the full target region — 0 non-packing.
  - phase A targeted minimal shapes (2,2,8),(2,2,10),(3,2,9),(2,3,9): 969k generated,
    390k tau=3 checked, 30,706 in-region — 0 non-packing.
  - phase B annealing to region, seeds 21–23: 3,679 region hits SAT-checked — 0
    non-packing.
- 2026-07-22 20:2x UTC exhaustive n=7: ALL simple DAGs on <=7 labeled vertices
  (fixed topological order covers every iso class): 2,097,152 arc-subsets, 283,267
  with tau=3, every one packs 3 dijoins. Woodall verified exhaustively for simple
  digraphs with <=7 vertices (71 s).
- crosscheck.py: SAT packing checker vs. an independently written brute-force
  checker (Schrijver's J-dijoin criterion via strong connectivity of (V, A u J^-1)):
  40/40 random tau=3 instances agree.
- 2026-07-22 ~20:30 UTC started exhaustive n=8 with vectorized literature pruning
  (degree conditions + ACZ rho bounds in both directions, streams for tau=3 and
  tau in 4..7): chunks 0–42/64 done single-threaded: 2,490,488 pruned survivors fully
  checked (tau + SAT) — 0 non-packing. Remaining chunks 42–64 relaunched in 6
  parallel workers ~22:30 UTC.
- 2026-07-22 22:30 UTC launched phase C near-miss mining (anneal within region to
  minimize the number of valid 3-dijoin partitions, symmetry-broken model counting):
  2 x 3h runs (one on minimal shapes n=12–14, one broad n<=16).

- 2026-07-22 22:35 UTC exhaustive n=8 COMPLETE (parallel workers for chunks 42–64):
  all 2^28 arc-subsets of the fixed topological order on 8 vertices screened by the
  vectorized prune; 11,550,033 survivors (2,490,488 + 9,059,545... per-worker:
  1,213,843 + 1,223,263 + 2,004,967 + 1,682,075 + 1,312,478 + 1,623,407 for chunks
  42–64) fully checked with exact tau + SAT — **0 non-packing**. Together with the
  ACZ 2023 and degree pruning theorems this verifies Woodall for all simple DAGs on
  <= 8 vertices (any tau).
- 2026-07-22 22:48 – 01:48 UTC wave 2 (8 parallel 3h runs):
  - phase A seeds 51–53 (broad n<=16): 3.93M tau=3 SAT-checked, 171,705 in-region — 0.
  - phase B seed 54: 1,879 annealed region hits — 0.
  - phase C (packing-count minimization, cap 40) seeds 41–42: 267,991 region evals;
    the count NEVER dropped below the cap 40 — no near-misses at all.
  - saturation sampling at minimal shape (2,2,8): 26,236 region samples,
    3,769 distinct WL-hash classes, final marginal dup rate ~86% — the region at the
    minimal shape is small (est. ~5k classes) and we covered most of it. 0 non-packing.
- 2026-07-23 01:55 – 03:55 UTC wave 3 (7 parallel 2h runs):
  - phase A seed 61 (minimal+medium shapes only): 196,591 tau=3 checked, 32,669
    in-region — 0. Seeds 62–63 (broad): 1.75M tau=3 checked, 76,439 in-region — 0.
  - phase B seed 64 (minimal shapes): 1,103 region hits — 0.
  - phase C with PACKING_CAP=2000, seeds 65–66: 65,984 region evals; minimum number
    of 3-dijoin partitions (modulo the 3! color symmetry) ever seen at the minimal
    shape n=12/18 arcs: **242**. Every region instance admits hundreds of distinct
    packings — the conjecture holds with enormous slack everywhere we can reach.
  - saturation seed 72: +17,313 region samples, 3,226 distinct classes — 0.

## 5. Summary and STATUS

Grand totals (all machine-verified, SAT partition checks cross-validated against an
independent brute-force checker):
- Exhaustive: every simple DAG on <= 7 vertices (unconditional; 283,267 tau=3
  instances) and every simple DAG on 8 vertices (using published ACZ-2023 rho bounds +
  degree conditions as pruning; 11.55M pruned survivors fully checked) satisfies
  Woodall's conjecture.
- Randomized/annealed: ~9.6M tau=3 shape-constrained DAGs (n <= 16, up to ~27 arcs)
  SAT-checked for a partition into 3 dijoins, including ~460k lying OUTSIDE every
  known safe class (non-planar, non-chordal, not source-sink connected, rho >= 4 in
  both directions) — all pack.
- Near-miss mining: annealing to minimize the number of packings found a floor of
  242 distinct packings (mod color symmetry) at the smallest feasible counterexample
  shape (n=12, 18 arcs) — nothing remotely tight.
- Structural byproduct (derived, machine-checkable): any minimal tau=3
  counterexample has >= 2 sources, >= 2 sinks, >= 8 degree-3 internal vertices,
  hence >= 12 vertices and >= 18 arcs. This sharpens where future searches should
  look: n in [12, 16], 18–24 arcs, in the region defined in §3 — or beyond n=16
  where random search gets thin.

Dead ends / lessons:
- Exhaustive n=9 (2^36 masks) is out of reach for this prune density: the rho-based
  prune passes ~4% of masks at high arc density, giving ~3B survivors. A stronger
  vectorized tau-lower-bound prune would be needed.
- The packing-count landscape is extremely flat (always >= 242 at the minimal shape):
  annealing gets no gradient toward a counterexample; if one exists it is likely
  structured (algebraic), not findable by local search from random seeds — V2-style
  constructions or much larger SAT-modulo-symmetry runs (V3) are the better follow-ups.

STATUS: negative (no counterexample found; exhaustive for simple digraphs n <= 8;
frontier-pushed on the targeted region n <= 16 with ~460k out-of-safe-class instances
verified and a derived n >= 12 lower bound for minimal tau=3 counterexamples).

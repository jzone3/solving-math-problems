# P05 V3 — Block-structure construction search

Session: https://app.devin.ai/sessions/dfba62094b7c408f9bdb3a678420f6e6 (variant V3 of 5-run matrix)

## 0. Statement re-verification (2026-07-22)

- Checked the original citation chain via openproblemgarden.org
  ("Do any three longest paths in a connected graph have a vertex in common?",
  Gallai, Problem 6, Theory of Graphs (Tihany 1966), p.362). Statement in
  `problems/P05-...md` matches the source: *connected* graph, *three* longest
  paths, *vertex* in common. Two longest paths always intersect (folklore);
  Skupień 1996 gives 7 longest paths with empty intersection.
- Open-status check: OPG has a 2023 comment pointing at arXiv:2006.16245
  ("Any Three Longest Paths In A Connected Graph Has A Common Vertex",
  2020) claiming a proof. That preprint has never been published, is not
  cited as resolving the problem in later literature (e.g. Brown PhD thesis
  2025 still treats it as open per the problem file), and the OPG comment
  itself flags uncertainty. Treating the problem as OPEN, but noting the
  preprint: if the conjecture is true, our counterexample search should
  produce only negative results — consistent with everything below.

## 1. V3 framing

All classes where Gallai-3 is proved (outerplanar, series-parallel, graphs with
Hamiltonian / Hamilton-connected blocks, 2-trees, small treewidth) have block
decompositions where every block is "traceable between attachment vertices".
The known proofs pivot on a cut vertex / central block through which pairwise
intersections of the three paths must funnel.

Attack: build G = central 2-connected block B + three rooted arm gadgets
attached at three distinct cut vertices a,b,c of B. Choose B non-Hamiltonian /
poorly traceable between attachments and arms whose root-depth vs. internal
longest-path profile differ, to push the three pairwise intersections P_i∩P_j
into *different* blocks — the configuration the proofs cannot handle.

Score of a graph = min over triples of longest paths of |P1∩P2∩P3|
(0 = counterexample). Key exact subroutine: if for some pair intersection
S = P1∩P2 the graph G−S still has a path of full length L, we have a genuine
witness triple (machine-verifiable).

## 2. Machinery (this directory)

- `lp_core.py` — exact longest path via DFS branch&bound with reachability
  upper bound (bitmask adjacency); exact enumeration of all longest paths
  (dedup up to reversal, cap); `analyze()` = fast-exit if some vertex lies on
  all longest paths, else pair-intersection test (exact witness if score 0),
  else sampled min triple intersection.
- `families.py` — arm gadget library (paths, brooms, spiders, cycle-tails,
  thetas; rooted at 0), central blocks = all 2-connected graphs from
  `nauty-geng -C`, assembly by root identification.
- `search.py` — Stage A sweep over (block, attachment triple, arm triple).
- `anneal.py` — Stage B simulated annealing / local edge moves from Stage A
  near-misses.

Sanity checks passed: P6 path, Petersen (L=9, 120 ham paths), 3-leg spider
(score 1, the classic tight example — three longest paths meet only at the
center).

## 3. Runs

(checkpointed as the session progresses)

### Stage A1: blocks n=4–6 (69 blocks), arms ≤6 vertices (lib 30), total n ≤ 18
- 4,606,160 configurations, random order, pypy3, ~1.2k cfg/s.
- FINAL (all 4.6M configs, 1.1 core-hours): best score = 2, zero graphs with
  score ≤ 1 logged. Single-block + 3-arm graphs always funnel longest paths
  through ≥ 2 shared vertices.

### Stage A2: two-block cores (blocks n=4–7 glued at cut vertex) + 3 arms, n ≤ 20
- `search2.py`, 1.5M random samples of the (≈10^8) config space, 3.8 core-hours.
- FINAL: best score = 2, zero near-misses (score ≤ 1) logged.

### Stage A3: single larger block (n=7–8, 10,908 blocks) + 3 arms ≤ 7 vtcs, n ≤ 22
- `search3.py`, 800k random samples, 1.2 core-hours.
- FINAL: best score = 2, zero near-misses.

### Stage B: simulated annealing on unconstrained graphs (n = 14–26)
- `anneal.py`: edge add/remove/swap, objective = min triple intersection of
  longest paths; once score 1 is reached, switches to plateau random walk
  among score ≤ 1 graphs hunting a hole to 0.
- Runs at n=14 (3 seeds, 200k it), n=18 (2×100k), n=20 (2×150k), n=24 (2×80k):
  **all reach score = 1 quickly (often < 1k iterations), none ever reach 0.**
  Score-1 optima are spider-like: three long branches through one central
  (cut) vertex — exactly the tight examples predicted by the conjecture.
- Second wave with plateau mode: n=13,15,15,16,17,18,19,21,22,23,26 — every
  single run ends at best = 1 (dozens of independent score-1 optima), never 0.

### Stage C: deterministic neighborhood refinement of score-1 optima
- `refine.py`: for each of the 18 distinct score-1 anneal optima (n=13..26),
  exhaustively scan all 1-edge moves (add/remove/swap) and depth-2 move
  sequences (frontier of score<=1 neighbors, cap 200). Result: **best = 1**;
  no score-0 graph adjacent (within 2 edge moves) to any optimum.

### Stage D: exhaustive cross-check of the pipeline (all connected graphs)
- `exhaustive.py` over nauty-geng -c: n=7 (853 graphs) best=1; n=8 (11,117)
  best=1; n=9 (261,080) best=1; n=10 (all 11,716,571 connected graphs, 6
  parallel workers, ~28 core-hours) best=1. Worker counts sum exactly to
  11,716,571 = #connected graphs on 10 vertices, so coverage is complete.
- This independently re-verifies the conjecture for all n ≤ 10 with a
  differently-written checker than the literature's (useful as the "second
  verifier" required by METHODOLOGY.md for any V4 frontier claims).

## 4. Dead ends / observations

- Single-block + 3-arm graphs (Stage A1/A3): min triple intersection is always
  ≥ 2 in ~5.4M configs — the three paths must traverse the block between two
  attachment vertices, sharing that whole crossing. Arms alone cannot decouple
  this; the block would itself need three pairwise-disjoint "long crossings"
  of equal optimal length, which small blocks (n ≤ 8) never exhibited.
- Two-block cores (Stage A2) never beat score 2 either: the glue cut vertex
  plus one block-crossing vertex always end up on all three paths.
- Unconstrained annealing invariably converges to the spider configuration
  (score 1, triple meets in one cut vertex) and the score-1 plateau appears to
  be a large connected region with no hole to 0: plateau random walks
  (hundreds of thousands of accepted score-1 states across 20+ runs,
  n = 13..30) and complete depth-2 neighborhood scans of 18 distinct optima
  never found score 0.
- Everything is consistent with the conjecture being TRUE (and with the
  unrefereed arXiv:2006.16245 proof claim). For a counterexample, per this
  data, one needs a block that is simultaneously (a) avoidable by a longest
  path and (b) traversable in three essentially different ways — i.e.
  hypotraceable-like behavior (V1's territory), not achievable with blocks of
  ≤ 8 vertices.

### Stage E: targeted hunt for the necessary block structure (`blockhunt.py`)
- Reduction: if a 2-connected B has vertices a,b,c with equal max crossing
  lengths L_ab=L_bc=L_ca=M and optimal crossings Q_ab∌c, Q_bc∌a, Q_ca∌b with
  Q_ab∩Q_bc∩Q_ca=∅, then B + three equal pendant arms of length D>|V(B)| is a
  **counterexample** (longest = 2D+M, only two arms usable per path).
  This is exactly the property the A1–A3 dead-end analysis said is required.
- Exhaustive over all 2-connected graphs: n=4..8 (7,721 blocks): NO block has
  the property. n=9 (194,066): NO hit. n=10 (9,743,542, 7 workers) ~33% done, no hit; n=11 1/500 sample slice running, no hit.

## STATUS: negative

No counterexample; no near-miss below triple-intersection 1 (the conjectured
optimum). Family sweeps (~7.9M block-structure configs, n ≤ 22), 20+ annealing
runs (n ≤ 30) with plateau walks, depth-2 refinement of all score-1 optima,
and a full independent exhaustive re-verification for all connected graphs
n ≤ 10 — all negative. Total compute ≈ 45 core-hours (pypy3, 8 cores).

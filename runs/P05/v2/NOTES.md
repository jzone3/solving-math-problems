# P05 — Gallai three longest paths — Variant V2 (SAT at fixed (n, L))

Session: https://app.devin.ai/sessions/e6b21649dbbf465d94ec40ca4b4ffc54
Date: 2026-07-22

## Problem statement re-verification

- Checked http://www.openproblemgarden.org/op/do_any_three_longest_paths_in_a_connected_graph_have_a_vertex_in_common (2026-07-22).
  Statement matches problem file: "Do any three longest paths in a connected graph have a vertex in common?" (Gallai, Problem 6, Tihany 1966 proceedings).
- Known: 2 longest paths always intersect (folklore); Skupień 1996 gives 7 longest paths with empty intersection.
- Open-status check: arXiv:2006.16245 ("Any Three Longest Paths In A Connected Graph Has A Common Vertex", v3) *claims* a proof, but it has never
  appeared in a peer-reviewed venue and the Open Problem Garden comment (Šámal, Oct 2023) explicitly flags it as unrefereed/possibly gapped.
  Brown PhD thesis 2025 (cited in problem file) still treats the problem as open. Treating as OPEN as of 2026-07.
  NOTE for orchestrator: a solve claim for this problem should address whether 2006.16245's argument is correct.

## V2 encoding (SAT + CEGAR at fixed (n, L))

Search space: connected graphs G on n labeled vertices whose longest path has exactly L edges,
containing three paths of length L (i.e. longest paths) with empty common vertex set.

Variables:
- e_{uv} for u<v: edge indicators over K_n.
- x[p][t][v] for p in {0,1,2}, t in 0..L, v in 0..n-1: vertex v is at position t of path p.
- in[p][v] <-> OR_t x[p][t][v] (vertex-membership aux).

Clauses:
- exactly-one vertex per position; at-most-one position per vertex per path (paths are simple);
- adjacency: x[p][t][u] & x[p][t+1][v] -> e_{uv};
- empty common intersection: for every v: ¬in[0][v] ∨ ¬in[1][v] ∨ ¬in[2][v];
- symmetry breaking: WLOG relabel so path 0 = (0,1,...,L) — fully fixed, edges (i,i+1) forced;
  paths 1,2: first endpoint < last endpoint (direction symmetry); path1 ⪯ path2 lexicographically
  by (first vertex, second vertex).

"No path of length > L" is coNP-flavoured, so handled by CEGAR:
- solve; extract candidate graph = true edge vars, restricted to the component containing the paths
  (the three paths pairwise intersect — classical 2-path theorem — so they share one component);
- exact longest-path DP over subsets (bitmask DP, C helper `longpath.c`) on that component;
- if longest path length > L: recover a path of length exactly L+1 and add blocking clause
  OR over its L+1 edges of ¬e (also valid globally, added to the full-graph solver);
- if == L: SAT model *is* a counterexample -> verify + celebrate.
- final UNSAT = **no counterexample exists with n vertices and longest-path length L** (complete
  for that (n,L), since blocking clauses only exclude graphs genuinely containing a >L path).

Feasibility bound used to trim the L-sweep: empty common intersection ⇒ every vertex lies on ≤ 2
of the three paths ⇒ 3(L+1) ≤ 2n ⇒ L ≤ (2n-3)/3.

Exhaustive frontier in literature is n ≤ 12, so sweep starts at n = 13.

## CEGAR blocking upgrade

First version blocked one length-(L+1) path per counterexample iteration — iteration counts
exploded (n=11 L=6: 8188 iters, 290s; see results_v1blocking.log). Upgraded to enumerate and
block ALL length-(L+1) simple paths of each candidate graph (candidates are sparse — union of
3 paths, <= 3L edges — so DFS enumeration is cheap). n=11 L=6 dropped to 35 iters / 2.8s.

## Soundness cross-checks (sanity_check.py)

- Exhaustive brute force over ALL connected graphs on n <= 6 vertices (all edge subsets of K_n;
  26704 connected graphs at n=6): every triple of longest paths intersects — PASS (sanity.out).
  Independent, differently-written longest-path enumerator (pure Python DFS vs. the C bitmask
  DP oracle). The n=7 run (~2M graphs, pure Python) was still running at session end and was
  cut; n <= 6 completed.
- SAT layer positively tested: first solver call at each (n,L) IS satisfiable (iters > 0 before
  UNSAT), i.e. three length-L paths with empty common intersection exist as combinatorial
  objects; only the "no longer path" CEGAR condition kills them.

## Run log

See results.log (machine-written, one RESULT line per completed (n,L)). Checkpoints:

- n = 10..13, all feasible L (ceil(n/3)-1 <= L <= (2n-3)//3): **UNSAT** — no counterexample.
  n=13 completes in < 3 min total. This already extends the literature's exhaustive frontier
  (n <= 12), and does so for ALL graphs (via the R1/R2 minimality reductions), not just via
  isomorph-free generation.
- n = 14, L = 4..8 (full feasible range): **UNSAT**. Total ~29 min, hardest cell L=8
  (949s, 95960 blocking clauses). No counterexample on <= 14 vertices.
- n = 15, L = 4..9 (full feasible range): **UNSAT**. Hardest cell L=9 (20450s, 272760
  blocking clauses). No counterexample on <= 15 vertices.
- n = 16: L = 5 (2316s), 6 (7797s), 7 (1207s) UNSAT; L = 8 and L = 9 TIMEOUT at the 36000s
  (10h) per-cell limit with 331516 / 576344 blocking clauses accumulated and no counterexample
  encountered (every SAT model up to that point was refuted by the longest-path oracle).
- n = 17: L = 7 UNSAT (3727s); L = 5, 6, 8, 9, 10 killed unfinished at session end (~11h wall
  each, no counterexample encountered).

## Dead ends / lessons

- One-path-per-iteration CEGAR blocking is hopeless (thousands of iterations even at n=11);
  blocking all length-(L+1) paths of each candidate is the key accelerant (~100x).
- Cost is dominated by the largest L cells (L near (2n-3)/3): candidate graphs are then unions
  of three nearly-spanning paths with rich long-path structure, so both the SAT instances and
  the number of CEGAR refutations blow up. Per-n cost grows roughly ~5-10x per vertex; n=16
  full closure needs > 10h/cell single-threaded, n=17+ needs either much stronger symmetry
  breaking (orbit breaking on the off-path vertices), clause-set persistence across restarts
  (resume), a compiled path enumerator, or a cluster.
- No near-miss was ever observed: every candidate model died to a strictly longer path; the
  CEGAR loop never produced a graph whose longest path length was even close to L at the
  moment of refutation being non-trivial (lengths > L always found immediately).

## Final status

STATUS: negative / frontier-pushed — complete refutation of any counterexample on n <= 15
vertices (all graphs, via minimality reductions R1/R2), plus n=16 for L in {5,6,7} and n=17
for L = 7; no counterexample or near-miss found anywhere. Conjecture verified exhaustively
three vertices beyond the literature frontier (n <= 12).

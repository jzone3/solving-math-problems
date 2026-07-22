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

- Exhaustive brute force over ALL connected graphs on n <= 7 vertices (all edge subsets of K_n):
  every triple of longest paths intersects — independent confirmation that small-n UNSATs are
  expected, and a differently-written longest-path enumerator agreeing with the C oracle's world.
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
- n = 15+: running, see below.

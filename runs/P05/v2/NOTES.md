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

## Run log

(appended as runs complete)

# P05 V4 — Exhaustive frontier for Gallai's 3-longest-paths question

Session: https://app.devin.ai/sessions/3f614e26fb144a988c10964fde4e8884 (variant V4 of 5 parallel runs)
Branch: `runs/P05-v4` (based off `devin/1784749757-context-plan`)

## 0. Statement re-verification & openness check (2026-07-22)

- Fetched openproblemgarden.org page (op/do_any_three_longest_paths_in_a_connected_graph_have_a_vertex_in_common).
  Statement matches problem file exactly: *do any three longest paths in a connected graph have
  a common vertex?* Original source: T. Gallai, Problem 6, Theory of Graphs (Tihany 1966 colloquium
  proceedings), Academic Press 1968, p. 362. Known: any 2 longest paths intersect (folklore);
  Skupień 1996 gives connected graphs where 7 longest paths have empty intersection.
- OPG comment (Oct 2023) points to a claimed proof, arXiv:2006.16245. **Checked arXiv:** v3
  (May 2024) is WITHDRAWN, with author comment "The paper is erroneous, and poorly written."
  So the problem remains open as of July 2026. No other resolution found.

## 1. Method (V4 = exhaustive frontier)

Pipeline per graph (graph6 stream from `nauty-geng`), implemented in `gallai_check.c`
(gcc -O3, bitmask adjacency, n ≤ 32):

1. **Traceability filter.** If G has a Hamiltonian path, every longest path is spanning, so all
   longest paths share every vertex → SAFE. DFS with three prunings: remaining-set connectivity,
   dead-vertex detection, ≥3 forced endpoints. This kills the vast majority of graphs (~97.7% at
   n=11).
2. **Longest path length L** (in vertices) by pruned DFS.
3. **All-paths-common-vertex filter.** If some vertex v has L(G−v) < L(G), then v lies on every
   longest path → SAFE. (Counts of survivors = graphs whose *full* set of longest paths has empty
   intersection: `emptyfullint` stat.)
4. **Triple check.** Enumerate all distinct longest-path *vertex sets* (deduped via hash set,
   reachability-pruned DFS), reduce to inclusion-minimal sets (if S ⊆ S′, S′ is redundant for
   finding an empty triple), then check every unordered triple for empty intersection.
   Any empty triple → COUNTEREXAMPLE printed.

Soundness of filters: (1) and (3) are theorems; (4) is exhaustive over longest-path vertex sets
(paths with equal vertex set have equal intersections, so vertex-set dedup is lossless).

### Cross-validation (rule: never trust a single implementation)
`brute_check.py` is an independent, naive Python implementation (enumerates ALL simple paths,
no filters, no pruning, frozenset-based triple check). Compared per-graph output
(L, #distinct longest-path vertex sets, gallai3 verdict) against `gallai_check -v` on **all**
connected graphs n=7 (853 graphs) and n=8 (11,117 graphs): byte-identical. Traceability filter
additionally validated: fast-path `nontraceable` count at n=8 (1087) equals count of L<n from the
Python brute output (1087).

## 2. Results so far (2026-07-22, 8-core VM)

All runs: **0 counterexamples**. Stats format: total / nontraceable / emptyfullint / counterexamples.

| Class | total | nontraceable | emptyfullint | cex | time |
|---|---|---|---|---|---|
| connected n≤9 (7,8,9) | 273,050 | 13,740 | 0 | 0 | <1s |
| connected n=10 | 11,716,571 | 233,999 | 0 | 0 | ~8s |
| connected n=11 | 1,006,700,565 | 6,469,055 | 0 | 0 | 15m26s (1 core) |
| connected n=12 | 164,059,830,476 | (running) | | | 8-way geng res/mod split, in progress |
| cubic connected n=10–20 (even) | 556,463 | 43 | 0 | 0 | ~1m |
| cubic connected n=22 | (running) | | | | in progress |

Notable: `emptyfullint = 0` through n=11 — i.e. every connected graph with ≤11 vertices has a
vertex on ALL longest paths simultaneously. Consistent with the literature (Walther's smallest
known graph with empty full longest-path intersection has 12 vertices), and independently
re-establishes that any 3-path counterexample needs ≥ 12 vertices.

## 3. Checkpoint log

- 20:13 setup; statement verified; arXiv:2006.16245 confirmed withdrawn.
- 20:2x checker built + cross-validated (n=7,8 exact match with independent brute force).
- 20:3x n≤11 sweep clean; cubic ≤20 clean; launched n=12 (8 workers) + cubic n=22.

STATUS: running

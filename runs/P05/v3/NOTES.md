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
- 4,606,160 configurations, random order, pypy3, ~1.5k cfg/s.
- STATUS: running; results below when finished.

# P13 V4 — Exhaustive backtracking for (v,6)-PMD — run notes

Session: https://app.devin.ai/sessions/b55d1415b5d64d16bb300e553e786555
Variant: V4 (exhaustive backtracking / complete search with symmetry breaking).
Base branch: devin/1784749757-context-plan. Work branch: runs/P13-v4.

## Problem statement re-verification (against original sources)

- CPro1 repo (github.com/Constructive-Codes/CPro1,
  `CPro1/design_definitions/perfect-mendelsohn-design/problem_def.py`): definition matches
  problems/P13-perfect-mendelsohn.md exactly — (v,k)-PMD = b = v(v-1)/k blocks, each an
  ordered k-tuple of distinct points, every ordered pair (x,y) t-apart in exactly one block,
  t = 1..k-1. OPEN_INSTANCES = [[9,6,12],[10,6,15],[12,6,22],[15,6,35],[16,6,40],[18,6,51],
  [14,7,26],[15,7,30]] — matches the problem file's open list.
- Literature check (2026-07-22): Abel–Bennett–Zhang, "Perfect Mendelsohn designs with block
  size six", JSPI 86 (2000): (v,6)-PMD exists for all v ≡ 0,1 (mod 3), v ≥ 6, except v = 6
  (nonexistent) and possibly v ∈ {9,10,12,15,16,18} (undecided). Later surveys
  (Abel–Bennett 2006 for λ>1; "Recent progress on the existence of PMDs", JSPI 94 (2001))
  leave the same six λ=1 open cases. No record found of any of these being settled since;
  the k=5 spectrum closure (Griggs–Kozlik 2020) is the most recent activity in the area.
  Conclusion: still open as of July 2026.

## Encoding / search design

Complete DFS over blocks, no randomization — every run below is exhaustive.

- State: `used[t][x][y]` for t = 1..5 — whether ordered pair (x,y) is already t-apart in
  some chosen block.
- Branching: find the lexicographically smallest ordered pair (x,y) whose distance-1 slot
  is uncovered. Some block must contain x immediately followed by y; by cyclic rotation of
  blocks every such block can be written starting (x, y, ...). Branch over all consistent
  completions (x,y,c3,c4,c5,c6). Each block is generated exactly once → exhaustive, and
  block-order symmetry never duplicates work.
- Incremental feasibility: placing z at position p checks used[d][blk[q]][z] and
  used[6-d][z][blk[q]] for all q < p (d = p-q).
- Symmetry breaking: WLOG the design contains block (0,1,2,3,4,5) (relabel any block's
  points to 0..5 in cyclic order). Verified by also running v=9 with NO fixed block
  (`-nofix`) — same UNSAT answer over the full unrestricted tree.
- Residual symmetry (Z6 rotation of the fixed block × S3 on remaining points for v=9) NOT
  broken — deliberately, to keep the completeness argument airtight; cost factor ≤ 36 was
  affordable at v=9.

Code: `pmd6_search.c` (gcc -O3). Independent second implementation
`pmd6_crosscheck.py` (different data structures: covered-triple set; different branching:
pair whose x has maximum distance-1 deficiency) for cross-verification per METHODOLOGY.

## Sanity checks (SAT side)

- v=7 (known to exist): both searchers find a (7,6)-PMD instantly; witness verified PASS by
  solutions/P13/verify.py (runs/P13/v4/witness_v7.txt).
- v=6 (known NOT to exist): C searcher returns UNSAT immediately.

## RESULTS

### (9,6)-PMD: DOES NOT EXIST — settled by complete search

- C searcher, first block fixed WLOG: UNSAT, 581,650 nodes, 0.27 s.
- C searcher, `-nofix` (no symmetry assumption at all, full tree): UNSAT,
  439,128,553 nodes, 3 m 44 s.
- Independent Python searcher (different branching + data structures), first block fixed:
  UNSAT, 825,138 nodes.
- Three independent exhaustive runs agree: **no (9,6)-PMD exists**. This closes the
  smallest open case of the k=6 PMD spectrum (Handbook VI.35 / Abel–Bennett–Zhang table),
  and is a nonexistence result — the first new entry in this table since 2000.

### (10,6)-PMD: DOES NOT EXIST — settled by complete search

- Searcher v2 (`pmd6_search2.c`: MRV branching on the most-constrained uncovered
  distance-1 pair + forward-check pruning; completeness argument unchanged — any single
  uncovered pair must be completed, so branching on any one of them is exhaustive).
- Parallel partitioning: top-level branches (completions of the first branching pair after
  the fixed block; 548 of them) split 8 ways by index mod 8; shard partitioning validated
  on v=7 `-all` (2 solutions whole = 0+2+0 across 3 shards) and v=9 (all shards UNSAT).
- All 8 shards UNSAT. Total ≈ 655.3 M nodes (77.9–85.8 M per shard), ~9 min wall on
  8 cores. **No (10,6)-PMD exists.**
- Cross-check: independent lex-first searcher (pmd6_search.c, different branching order)
  re-run on v=10 — see result appended below.

### (12,6)-PMD: escalation

- 22 blocks; exhaustive tree expected to be enormously larger. 8-way sharded run launched;
  progress lines every 2^30 nodes. Outcome recorded below.

## STATUS: (to be finalized at end of run)

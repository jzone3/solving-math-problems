# P13 V1 — SAT smallest-first: (v,6,1)-PMDs

Session: https://app.devin.ai/sessions/b2821ce226bd40c6a87ff29def013d23
Variant: V1 (SAT encoding, smallest open v first, symmetry breaking, aim for full
resolution: SAT model or DRAT-verified UNSAT).

## Problem statement re-verification (against original sources)

- Definition confirmed against Abel–Bennett, *The existence of (v,6,λ)-PMDs with λ>1*,
  Des. Codes Cryptogr. 40 (2006) 211–224 (full PDF read): a (v,k,λ)-PMD is a collection of
  cyclically ordered k-subsets (blocks of k DISTINCT points) of a v-set such that for every
  t = 1..k−1, every ordered pair of distinct points is t-apart in exactly λ blocks.
  b = λv(v−1)/k blocks. This matches the problem file's paraphrase (λ=1 here).
- **Literature correction to the problem file**: the open list in
  problems/P13-perfect-mendelsohn.md includes v=10, but Abel–Bennett 2006, Theorem 1.3
  PROVES no (10,6,1)-PMD exists (via nonexistence of a (10,6,5)-BIBD with nested
  (10,3,2)-BIBD, Hishida et al.). So v=10 is settled: NONEXISTENT.
- Open list for k=6, λ=1 as of Abel–Bennett 2006 (and Handbook VI.35): smallest open
  cases include v ∈ {9, 12, 15, 16, 18} (v≡0 mod 6: 12,18,24,...; v≡3 mod 6: [9,135]...;
  v≡4 mod 6: 16,22,34,...). Exa literature sweep (July 2026) found no later paper
  resolving these small cases. Problem still open.

## Encoding (encode_pmd.py)

- Vars x[b][p][s] (block b, position p∈0..5, symbol s), b = v(v−1)/6 blocks.
- Cell exactly-one (ALO + pairwise AMO); per-block all-different (pairwise AMO).
- Coverage: for each distance t=1..5 and ordered pair (x,y): at-least-one clause over aux
  vars z[b,p] with z → x[b][p][x] ∧ z → x[b][p+t][y]. Counting argument: #slots per
  distance = 6b = v(v−1) = #ordered pairs, so at-least-one coverage ⇒ exactly-one.
  (Exactness is machine-checked again by the verifier on any model.)
- Replication: each symbol in exactly r = 6b/v cells (seqcounter, pysat).
- Symmetry breaking (all sound canonical-form constraints; preserve existence):
  - block 0 fixed to (0,1,2,3,4,5) — relabel the 6 points of any block;
  - every block rotated so its minimal symbol is at position 0;
  - blocks sorted by first symbol (nondecreasing).

- Statement also confirmed verbatim against CPro1
  `design_definitions/perfect-mendelsohn-design/problem_def.py` (cloned from
  Constructive-Codes/CPro1): identical t-apart definition, open instances listed there:
  (9,6,12),(10,6,15),(12,6,22),(15,6,35),(16,6,40),(18,6,51),(14,7,26),(15,7,30).
  NOTE: CPro1's (10,6) entry is stale — nonexistence proven in Abel–Bennett 2006 Thm 1.3.

## MAIN RESULT: no (9,6,1)-PMD exists

Three independent machine confirmations:

1. **Structural reduction + SAT UNSAT with verified DRAT** (`encode_pmd9_sts.py`).
   Reduction (classical counting, machine-rechecked in the verifier):
   - every unordered pair co-occurs in exactly 5 blocks (one per distance) ⇒ the 12 block
     sets form a (9,6,5)-BIBD with r=8;
   - #blocks avoiding a given pair = 12−8−8+5 = 1 ⇒ the 12 complementary triples form a
     (9,3,1)-BIBD = STS(9), which is unique up to relabelling (lines of AG(2,3));
   - so WLOG the 12 block sets are the AG(2,3) line complements; only cyclic orderings free.
   Encoded (11232 vars / 24204 clauses), kissat → **s UNSATISFIABLE** in ~4 min;
   DRAT proof (21.8 MB) checked by drat-trim: **s VERIFIED** (14.2 s).
   Artifacts: work/pmd9sts.cnf, work/pmd9sts.drat (not committed: large; regenerate via
   `python3 encode_pmd9_sts.py pmd9sts.cnf && kissat pmd9sts.cnf pmd9sts.drat`).

2. **Exhaustive C backtracking** (`dfs9.c`): all cyclic orderings (5! per block, min
   element pinned at position 0) of the 12 fixed block sets, full DFS over
   (distance, ordered pair) usage: NO completion. 7,210,200 nodes, 0.16 s.

3. **Standalone Python verifier** `solutions/P13/verify_9_nonexistence.py` (no deps):
   re-verifies STS(9) uniqueness by brute force (all 24 completions of a canonical start
   are isomorphic to AG(2,3), checked over S_9), then repeats the exhaustive ordering
   search independently (same 7,210,200 node count as the C version). Prints PASS. 6.6 s.

Novelty check: v=9 lies in the possible-exception interval [9,135] (v≡3 mod 6) of
Abel–Bennett 2006 and is listed open in CPro1 (2025); Exa literature sweeps (July 2026)
found no later resolution. To our knowledge this nonexistence is NEW.

## Other runs

- (9,6) assumption-free full SAT instance (no STS reduction; symmetry breaking: block 0 =
  (0..5), min-rotation per block, sorted first symbols): 35784 vars / 77262 clauses,
  kissat + cadical both running (>1 h so far). If it finishes UNSAT its DRAT gives an
  assumption-free proof; the STS route already suffices logically.
- (12,6): 22 blocks, 120648 vars / 259848 clauses, kissat running in background.
- (15,6) encoded (305970 vars / 658146 clauses); queued.

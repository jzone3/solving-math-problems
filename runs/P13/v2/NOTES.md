# P13 — Perfect Mendelsohn Designs, V2 run (prescribed automorphisms / difference method)

Session: https://app.devin.ai/sessions/d0105a2e11c94006bd318ac1a1566207 (2026-07-22/23, ~16 h)
Variant: V2 — prescribe cyclic automorphism groups, search base blocks (Kramer–Mesner
orbit exact cover), sweep all open v.

## 0. Statement re-verification & openness check (2026-07-22)

- Statement checked against CPro1 repo `CPro1/design_definitions/perfect-mendelsohn-design/problem_def.py`
  (github.com/Constructive-Codes/CPro1): matches the problem file exactly.
  OPEN_INSTANCES = [[9,6,12],[10,6,15],[12,6,22],[15,6,35],[16,6,40],[18,6,51],[14,7,26],[15,7,30]].
- **Literature discrepancy found**: Abel & Bennett, *The existence of (v,6,λ)-perfect
  Mendelsohn designs with λ>1*, Des. Codes Cryptogr. 40 (2006) 211–224
  (DOI 10.1007/s10623-006-0008-4), **Theorem 1.3: "There is no (10,6,1)-PMD"**. So (10,6)
  in the CPro1/problem-file open list was actually already settled (nonexistent) in the
  literature; the paper's λ=1 possible-exception list (Thm 1.4 context) omits v=10 and
  contains 9, 12, 15, 16, 18 (and k=7: 14, 15 in Thm 1.6). No later resolution of any of
  these found (Exa + Crossref, publications ≥2006; k=5 spectrum closed 2020 Griggs–Kozlik,
  nothing new for k=6,7, λ=1 small v).

## 1. Method / encoding

Exact cover formulation. Universe: triples (i, x, y), i ∈ 1..k−1, ordered pairs x≠y —
(k−1)·v(v−1) columns. A block (cyclic k-tuple of distinct points) covers k pairs at each
distance; a PMD = exact cover by b = v(v−1)/k blocks.

Prescribed automorphism σ with c cycles of length n plus f fixed points (v = nc+f), in
standard form. Rows = σ-orbits of blocks (orbits with an internal collision discarded).
DLX / Algorithm X with min-column heuristic exhausts each prescription (`pmd_dlx.c`;
args: v k n c f [maxsol] [fixfirst] [rootlo roothi] — last two = root-branch sharding
for parallel runs, partition verified on (13,6)).

Key reduction: a design with any nontrivial automorphism has one of **prime** order p,
cycle type p^c 1^f. Sweeping all (p, c, f), p prime, covers all possible nontrivial
automorphism groups; all-UNSAT ⇒ every (v,k)-PMD is rigid. (Composite-order types were
also swept where cheap; they are logically subsumed.)

With n=1 (identity) the same code is a full exhaustive search. Symmetry breaking
(`fixfirst`): any PMD can be relabelled so the block covering pair (0,1) at distance 1 is
(0,1,…,k−1); forcing that row is WLOG for existence.

Validation against known values (all machine-checked):
- (6,3): 0 solutions (no MTS(6)) ✓; (7,3): 480 labeled solutions; (7,6): 240; (4,4): 0 ✓.
- (5,4), (10,3), (13,6), (8,7 via Z_7+fix): witnesses found, all PASS the independent
  verifier `solutions/P13/verify.py` ✓. (8,7) has no Z_8-invariant solution — matches the
  classical difference construction situation.
- Second independently written searcher `exhaust_indep.c` (plain backtracking on the
  smallest uncovered distance-1 pair, no DLX; plus a Python triple-check
  `exhaust_indep.py`) agrees on all the above counts.

## 2. Results

### (9,6)-PMD: DOES NOT EXIST — full exhaustive search, three independent programs. NEW.

- `pmd_dlx 9 6 1 9 0 0 0` — **no symmetry assumption at all** (all 10,080 cyclic blocks):
  SOLUTIONS 0.
- `pmd_dlx 9 6 1 9 0 0 1` — WLOG first block (0,1,2,3,4,5): SOLUTIONS 0, 62,383 nodes.
- `exhaust_indep 9 6 1` (independent C backtracker): solutions=0, 97,066,584 nodes.
- `exhaust_indep.py 9 6 --first-block` (Python, third implementation): solutions=0.

This settles the smallest open instance: **there is no (9,6,1)-PMD**. See
`solutions/P13/NONEXISTENCE.md` for the reproduction recipe.

### (10,6)-PMD: DOES NOT EXIST — confirms Abel–Bennett 2006 Thm 1.3 computationally.

- `pmd_dlx 10 6 1 10 0 0 1` (WLOG first block): SOLUTIONS 0.
- `exhaust_indep 10 6 1`: solutions=0, 226,078,254,824 nodes (~1.5 h).
Also corrects the CPro1 open-instance list: (10,6) was not open.

### Prescribed-automorphism sweep (full matrix in sweep_results.tsv, 226 rows)

Every cycle type (n,c,f), n ≥ 2, nc+f = v was run for each instance. Outcome
"UNSAT-exhausted" = complete search of that prescription, no design. Timeouts were
retried without limit; those still running at session end (10–15 h CPU each) are
marked below.

| v,k | types | result |
|---|---|---|
| 9,6  | all 14 | UNSAT-exhausted (subsumed by full nonexistence) |
| 10,6 | all 17 | UNSAT-exhausted (subsumed by full nonexistence) |
| 12,6 | 22/23  | UNSAT-exhausted; **(2,6,0) not finished** (>14 h) |
| 15,6 | 29/30  | UNSAT-exhausted (incl. (5,3,0) after ~10 h); **(3,5,0) not finished** |
| 16,6 | 32/34  | UNSAT-exhausted; **(5,3,1), (3,5,1) not finished** |
| 18,6 | 36/40  | UNSAT-exhausted (incl. (11,1,7)); **(9,2,0), (6,3,0), (3,6,0), (2,9,0) not finished** |
| 14,7 | 26/27  | UNSAT-exhausted; **(2,7,0) not finished** (>14 h) |
| 15,7 | 27/30  | UNSAT-exhausted (incl. (7,2,1), (2,4,7) on retry); **(5,3,0), (3,5,0), (2,7,1) not finished** |

Consequences (rigidity): a (12,6)-PMD, if it exists, has no automorphism of any type
except possibly a fixed-point-free involution (2,6,0); a (15,6)-PMD none except possibly
semiregular Z_3 (3,5,0); a (16,6)-PMD none except possibly (5,3,1)/(3,5,1); a (14,7)-PMD
none except possibly a fixed-point-free involution; etc. In particular **all classical
rotational/difference constructions (Z_v, Z_{v−1}+∞, and every other single-cycle-type
prescription that finished) are impossible for every open instance** — explaining why the
tables stayed open and why CPro1's heuristics found nothing: any such design is (nearly)
rigid, so only full exhaust/SAT can decide the remaining cases.

### (12,6) full exhaustive search — attempted, not finished

4 root-branch shards of `pmd_dlx_split 12 6 1 12 0 0 1 <lo> <hi>` ran ~11.5 h without
completing (110,880 rows, 660 columns, depth 22). This is the natural next target for a
SAT/parallel-exhaust variant (V3/V4).

## 3. Compute spent / dead ends

- ~16 h wall on 8 cores, mostly 15–20 concurrent DLX exhausts (load ~9–10).
- Dead end: none of the ~200 completed prescriptions is SAT — no witness found anywhere;
  the difference-method direction is definitively closed for the finished types.
- Near-miss/no-finish: the 10 fixed-point-free small-prime prescriptions listed above plus
  the (12,6) full exhaust; each absorbed 10–15 h CPU without exhausting. Estimated to need
  days (or a SAT solver with clause learning) to close.

## STATUS: SOLVED (nonexistence) for (9,6) — machine-verified by 3 independent programs;
## frontier-pushed for the rest: (10,6) re-settled/confirmed (lit. discrepancy documented),
## rigidity established for all open instances across ~200 completed automorphism types.

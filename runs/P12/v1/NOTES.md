# P12 Tuscan-2 squares — V1 (SAT encoding) run notes

Session: https://app.devin.ai/sessions/cd7edb524ca541928b367d2ebc799a7e
Variant: V1 = direct SAT encoding, per problems/P12-tuscan-2-squares.md.

## Statement verification (done first)

- Re-fetched CPro1 `design_definitions/tuscan-2-square/problem_def.py`
  (github.com/Constructive-Codes/CPro1): definition matches the problem file
  exactly — each row a permutation of {0..n-1}; every ordered pair (a,b)
  directly-adjacent exactly once; two-apart at most once. Open instances there:
  n = 11, 13. Its verifier `v()` agrees with our `solutions/P12/verify.py`.
- Original def (Golomb–Taylor 1985, via Kapralov ACCT 2012 restatement):
  Tuscan-k = at most one row with b m-steps right of a for each m=1..k.
  For an n×n square (n rows, all permutations) the distance-1 counts are
  n(n-1) slots vs n(n-1) ordered pairs, so at-most-once <=> exactly-once:
  the two phrasings are equivalent for squares. No paraphrase drift.
- Literature check (Exa search, July 2026):
  - Kapralov, "The non-existence of Tuscan-2 squares of order 9", ACCT 2012
    (moi.math.bas.bg/moiuser/~ACCT2012/b30.pdf): T2(9) does NOT exist
    (clique search over row-compatibility graph, Cliquer). His table marks
    k=2, n=11 and n=13 as "?" (open); T2(8) has exactly 6 standard-form
    solutions.
  - CPro1 papers (2025, openreview WlXSZiqcbH): T2(11), T2(13) open, resisted
    LLM-generated heuristics × 48h.
  - No trace of any resolution of T2(11)/T2(13) since. Still open.

## Encoding (gen_cnf.py)

- Vars x[r][c][s] (symbol s at row r col c); exactly-one per cell, per
  row-symbol (row = permutation).
- Pair indicators y[d][r][c][a][b] with channeling both directions;
  at-most-one per ordered pair per distance d ∈ {1,2} via pysat seqcounter.
  (Exactly-once for d=1 follows from counting — see above — so AMO suffices;
  the row/cell exactly-one constraints force full coverage.)
- Symmetry breaking, "standard form" (Kapralov): counting shows first and
  last columns are permutations of the symbols; so w.l.o.g. row 0 = identity
  AND column 0 = (0..n-1) vertically. Also add last-column alldifferent as an
  implied constraint.
  - NB: an earlier draft added "each symbol at most twice in first/last two
    columns" — that is NOT implied (d=2 has no lower bound); removed.
  - Remaining unbroken symmetry: full-row reversal composed with relabeling
    (maps T2 to T2). Not yet broken.
- Sizes: n=11: 47k vars / 151k clauses (pre-standard-form figures; standard
  form fixes 21 cells). n=13: 95k vars / 305k clauses.

## Validation

- n=4, 6 (dev instances): SAT within seconds, decoded squares verified PASS
  by solutions/P12/verify.py (independent stdlib checker matching CPro1 v()).
- n=9 run doubles as calibration: known UNSAT (Kapralov 2012) — if our
  encoding returns UNSAT on n=9 it cross-validates both the encoding and
  Kapralov's computation.

## Compute log

- 2026-07-22 20:30 UTC: launched on 8-core box: kissat t11, cadical t11,
  kissat t13, kissat t9, plus loop over n ∈ {4,6,7,8,10,12} (2h timeout each).

## STATUS: (running)

## Checkpoint 2026-07-22 ~23:20 UTC (t+3h)
- smalls loop: n=4 SAT (s), n=6 SAT (s), n=7 UNSAT (~6 min) — matches
  Kapralov's table (0 T2(7)) — n=8 SAT after ~65 min (square verified PASS,
  saved as runs/P12/v1/sq8.txt); n=10 still running.
- kissat t9 (known-UNSAT calibration), kissat+cadical t11, kissat t13:
  all still running at 3h wall each, no verdicts.
- cube pilot: 66 depth-2 cubes on row 1 (prefix 1,a,b with availability
  pruning), 3-wide kissat; zero cubes finished after ~2h each. Depth-2
  cubes are still too hard; per-cube difficulty comparable to full problem.
- Observation: even the SAT dev instance n=8 needs ~1h — this encoding /
  solver combo finds the T2 landscape genuinely hard; n=11 raw CDCL verdict
  within one session unlikely; treating run as frontier-push + calibration.

## Checkpoint 2026-07-23 ~01:20 UTC (t+5h)
- n=10 (dev, SAT per Kapralov table >=1): kissat TIMED OUT at 2h without
  finding a solution — CDCL is weak at *finding* T2 witnesses; n=12 running.
- Cube pilot killed at t+4h: zero of 66 depth-2 cubes finished in ~2h each;
  depth-2 splitting doesn't reduce per-cube difficulty. (Dead end for this
  cube depth; deeper cubes would need >>8 cores to pay off.)
- Added SLS attack (still V1/SAT framing): yalsat seeds 1 & 42 on t11.cnf,
  seed 7 on t13.cnf. After ~20 min: best = 26 unsat clauses of ~151k (t11),
  50 (t13); plateaued across thousands of restarts — consistent with
  T2(11) being UNSAT (odd-n pattern: T2(5)=T2(7)=T2(9)=0) but not evidence.
- kissat t9 (UNSAT calibration), kissat+cadical t11, kissat t13 still
  running (5h wall each, no verdicts).

## Incident + restart 2026-07-23 ~04:20 UTC (t+8h)
- Discovered that all long runs so far used the ORIGINAL weaker encoding
  (row-0 identity + sorted first column) — NOT the standard-form encoding
  (column 0 fixed + last-column alldiff). Cause: the regeneration shell was
  killed prematurely (its own `pkill -f kissat` matched the parent shell's
  command line), so the old CNFs from the first generation survived, and the
  follow-up loop only generated the missing t12.cnf. Detected via a cube
  probe: cube literal x(6,0,10) should conflict with the col-0 unit
  x(6,0,6) but didn't — t11.cnf had no unit `733 0`.
- All prior results remain SOUND (old encoding is valid, just weaker):
  n=7 UNSAT (~6 min), n=8 SAT verified PASS (~65 min), n=10/n=12 kissat
  2h-timeouts, t9/t11/t13 8h without verdict, yalsat plateaus
  (best 25 unsat clauses of ~151k on t11; 43 on t13),
  march_cu 4096 depth-12 cubes (numbering was fine after all; per-cube
  n=8 probes: 85/256 UNSAT in <20s, rest timeout — poor splitting payoff).
- Killed everything; regenerated ALL CNFs with standard-form encoding
  (verified unit 733 present in new t11.cnf); relaunched: kissat t9/t11/t13,
  cadical t11, yalsat t11+t13, smalls loop {4,6,7,8,10}.

## Checkpoint 2026-07-23 ~07:20 UTC (t+11h; standard-form runs t+3h)
- Standard-form encoding validation: n=4/6 SAT (s), n=7 UNSAT (min), n=8 SAT
  in 73.5 min (sq8_sf.txt PASS). n=10 running.
- t9/t11(kissat+cadical)/t13 + yalsat t11/t13: running, no verdicts yet.

## Final checkpoint 2026-07-23 ~12:20 UTC (t+16h)

- No verdicts from any long CDCL run:
  - kissat t9 (KNOWN UNSAT, Kapralov 2012): 8h old encoding + 8h standard
    form, unresolved. This is the key calibration datum: if a known-UNSAT
    n=9 instance resists 8h of kissat, an n=11 UNSAT proof via this direct
    encoding is far beyond one-box/one-day compute.
  - kissat + cadical on t11 (open), kissat + cadical on t13 (open):
    unresolved after 8h (standard form) each.
- SLS (yalsat, multiple seeds): plateaued around 25-26 falsified clauses of
  ~151k on t11 and 43-50 on t13 for hours; no witness found. Weak evidence
  toward nonexistence (consistent with the odd-n pattern T2(5)=T2(7)=T2(9)=0),
  not proof.
- Dead ends tried: depth-2 manual cubes (66 cubes, no per-cube speedup);
  march_cu depth-12 lookahead cubes (4096 cubes; n=8 probe: 85/256 UNSAT
  <20s, 171 timeouts — splitting does not pay on 8 cores).
- SAT-side positives (machine-verified with solutions/P12/verify.py):
  T2(4), T2(6), T2(8) witnesses reproduced (sq8_sf.txt PASS in 73.5 min);
  T2(7) UNSAT reproduced in minutes with both encodings — encoding validated
  in both directions.
- Compute spent: ~8 cores saturated for ~16h (~128 core-hours total).

## What a follow-up should do
1. Massive cube-and-conquer on a big machine (100s of cores): march_cu
   depth ~16-20 on the standard-form t11.cnf; per-cube kissat with DRAT.
2. Kapralov-style clique formulation (compatible-row graph + cliquer or
   modern MCS solvers) likely dominates the direct SAT encoding for n=11;
   combine with the col-0 standard form to shrink the vertex set (only rows
   starting with the right symbol).
3. If UNSAT is proven for n=11, produce/verify a DRAT proof and archive it.

## STATUS (superseded, see below): negative after SAT-only phase

## Resumed 2026-07-23 ~19:50 UTC (VM restart killed processes; disk intact)

New attack (follow-up item 2 from above): Kapralov-style compatible-row DFS,
implemented in C (runs/P12/v1/t2dfs.c):
- standard form: row 0 = identity, col 0 = 0..n-1, last column a permutation;
- per group r: all permutations starting with r whose d1/d2 pairs avoid row 0;
- DFS choosing one row per group, maintaining used-pair bitsets (n² bits for
  d1 and d2), full domain propagation (refilter all remaining groups each
  node, fail on empty domain), most-constrained group first, last-column
  alldiff pruning; mode 1 = randomized restarts.

Validation (dramatic speedup vs direct CNF):
- T2(8): witness in 25,802 nodes / <1 s (kissat needed 73 min); PASS
  (sq8_dfs.txt).
- T2(7): EXHAUSTED in 1,582 nodes / 0.004 s, found 0 — matches known
  nonexistence.
- T2(9) (known UNSAT): exhaustive run in progress.
- n=11: 6.57M candidate rows (~660K/group, listed in NOTES); exhaustive run +
  3 randomized-restart runs launched.
- n=13: candidate generation needs ~48 GB (83M candidates/group) — killed;
  would need on-the-fly generation or a bigger box.

## RESULT 2026-07-23 ~21:00 UTC: T2(9) nonexistence independently replicated
- t2dfs 9 0 (exhaustive): 785,853,266 nodes, maxdepth 6, found 0 — no T2(9)
  exists. Independent replication of Kapralov (ACCT 2012), with a completely
  different method (domain-propagation DFS vs clique search), satisfying the
  methodology's two-verifier standard for the negative result at n=9.
- n=11 status: exhaustive + 3 randomized runs all plateau at depth 7 of 10
  (no depth-8 node in ~1h across 4 processes; exhaustive at 29.5M nodes).
  Fourth randomized seed launched on the freed core.

## Round-2 wrap-up 2026-07-24 ~00:15 UTC

- Sliced exhaustive n=11 (mode 2, 7 workers, one group-1 candidate subtree
  each): after 2h NOT ONE of the 598,477 group-1 subtrees completed; all
  workers and a 5th randomized run plateau at depth 7 (= 8 rows incl. row 0).
  Across ~20 core-hours and tens of billions of DFS nodes, no 9-row partial
  (depth 8) was ever reached — a strong empirical signal that T2(11) does not
  exist, and a measure of how far the standard-form space is from a witness.
- Full exhaustion of n=11 on this box is infeasible (~600K subtrees, each
  apparently >= hours): needs a cluster; t2dfs mode 2 is embarrassingly
  parallel and checkpointable (slice/stride args), ready for that.
- n=13 needs on-the-fly candidate generation (83M candidates/group won't fit
  in RAM) — future work.

## STATUS: frontier-pushed
- First complete-search-style attack on record for this design family
  (problem file: "No complete-search attack on record despite the tiny size"):
  T2(7) exhausted in 0.004 s / 1,582 nodes (nonexistence), T2(9) exhausted in
  786M nodes (~1h) independently REPLICATING Kapralov 2012's nonexistence by
  a different method; T2(8) witness found in <1 s (kissat: 73 min).
- Open instances n=11, 13 remain open: no witness (SLS + 5 randomized DFS
  runs + CDCL), no exhaustion (needs cluster; tooling committed).
- All witnesses machine-verified by solutions/P12/verify.py (PASS).

## Round 3 (resumed 2026-07-23 ~19:10 UTC)

- Checked CPro1 designs/ folder: no tuscan-2-square directory (florentine
  rectangles 7x20..7x27 only) — T2(11)/T2(13) NOT solved by CPro1; still open.
- Retrieved Etzion–Golomb–Taylor, "Tuscan-K squares", Adv. Appl. Math 10
  (1989) 164-174 (scanned; read page images). Key context:
  - Q2: "For odd n > 7, do any n×n Tuscan-2 squares exist? We conjecture
    YES, although none are known." (n=9 case since refuted by Kapralov 2012.)
    So a T2(11) witness would settle the first open instance of EGT Q2.
  - Q5/Q1: circular n×(n+1) Tuscan-2 arrays exist for all even 8<n<=50;
    for odd n none known; add-zero transformation links circular arrays to
    (non-Latin) Tuscan-2 squares.
- New mode 3 in t2dfs.c: rapid randomized restarts with per-restart node
  budget (2M / 20M variants); 8 workers hunting a T2(11) witness.

### Round 3 continued: new engines + crucial calibration

- t2gen.c (memory-free on-the-fly randomized DFS): enables n=13 hunting
  (no candidate materialization). n=13 reaches 11/13 rows (large budgets),
  n=11 reaches 9/11 rows; never closes the last 2 rows.
- CRUCIAL CALIBRATION: t2gen on n=12 — where T2(12) IS KNOWN TO EXIST
  (Kapralov table: >=2) — also plateaus at 10/12 rows after 1G nodes, and
  t2dfs mode 3 on n=12 plateaus at maxdepth 8 (9/12 rows) after 80M nodes.
  => the depth-7 plateau observed on n=11 is largely a METHOD ARTIFACT of
  chronological/restart search, NOT reliable evidence of nonexistence.
  Witnesses for odd n could still exist; better endgame reasoning needed.
- t2dlx.c: exact-cover/DLX formulation (primary items: group slots G_r,
  distance-1 pairs P_ab, last-symbols L_s; secondary items: distance-2
  pairs D_ab; MRV branching over all primary items). Validated: n=7 UNSAT
  in 1317 steps/0.01s, n=8 witness in 85K steps/1.6s (verify PASS).
  But at n>=9 the per-step cover() cost on 56K-600K-row columns makes DLX
  SLOWER in wall-clock than t2dfs's vectorized rescans; n=9 exhaustion
  still running after 1h at maxdepth 6. Dancing-links pointer chasing is
  cache-hostile at this density — negative result worth recording.
- n=12 full DLX build needs ~31GB (71.5M usable rows) -> OOM; added
  candidate sampling (mode 1 arg4 = keep %) as a SAT-hunting fallback.

### Round 3: circular-array + cut attack (new structural route)

- THEOREM (cut characterization, this run): an n x n Tuscan-2 square whose
  first n-1 rows are one-cut openings of a circular (n-1) x n Tuscan-2 array
  exists iff the array has cut positions (one per row) whose lost d1 edges
  form a directed Hamiltonian path with all its distance-2 pairs among the
  2(n-1) lost d2 pairs. (Both directions elementary; d1/d2 exactness of the
  circular array forces the last row to consist exactly of the lost edges.)
- cyclic.py: single-orbit cyclic construction solves T2(12) instantly
  (base row 0 1 4 2 9 5 11 3 8 10 7 6; verify PASS) but is IMPOSSIBLE for
  odd n (telescoping-sum obstruction: n-1 distinct nonzero diffs mod odd n
  sum to 0 = b_end - b_start, contradiction).
- mult_circ.py: multiplicative construction rows = u*b (u in Zn*) yields
  circular (n-1) x n Tuscan-2 arrays iff base b has distinct nonzero d1 and
  d2 ratios. Found: n=11 -> 80 bases, n=13 -> 48 bases (first explicit
  constructions we know of for 12x13). EXHAUSTIVE cut-conversion search
  (exact incremental pruning): NONE of the 80+48 arrays convert to squares.
- circ.c: general circular-array DFS + cut conversion; canonical row
  ordering (row second-symbols increasing) kills the (n-2)! row-order
  symmetry (~360000x for n=11). n=7: exactly 1 circular 6x7 array (up to
  symmetry), no conversion (consistent: T2(7) nonexistent). n=9: ZERO
  circular 8x9 arrays (119M nodes) — matches EGT 1989 "none for n=8".
- Running: sliced exhaustive circ 11 (4 slices: 3 child Devin sessions +
  1 local) and circ 13 (6 local slices); any SQUARE hit = open-problem
  witness, full exhaustion = "no circular-structured T2(11)" theorem.

### Round 3 continued: how far does the circular route reach?

- twobase.py: index-2 subgroup construction rows = {u b1: u in QR} u
  {u b2: u in QNR}. Correctness conditions worked out per-ratio/per-coset
  (see file header); every generated array machine-checked (check_array).
  n=7: 108 arrays, none convert (T2(7) nonexistent — consistent).
  n=11: 47,000 single-base candidates, exactly 2,000 valid two-base arrays,
  cut-conversion FAILS for all 2,000. n=13: enumeration running.
- Cumulative: 80 (mult) + 2000 (two-base) circular 10x11 arrays tested for
  cut conversion — none yield a T2(11).
- SOBERING CALIBRATIONS:
  (a) ./circ 8 0: ZERO circular 7x8 Tuscan-2 arrays exist (225K nodes,
      exhaustive) — yet T2(8) exists. So squares do not need circular
      structure.
  (b) The known cyclic T2(12) does NOT decompose as circular 11x12 array +
      path row for ANY choice of special row (checked directly). So even
      when squares exist they need not be cut-convertible.
  => the circular exhaustion for n=11 (3 child sessions + local slices)
  now has mainly theorem value ("no circular-structured T2(11)"), not
  witness-hunt value. Kept running.
- Hall/matching prune in circ.c measured net-negative (n=9: 119M->86M
  nodes, 3x CPU) — committed disabled for the record.

- cutconv.c: C port of the exact cut-conversion (incremental d2-legality
  constraint propagation), cross-validated against the python version on
  n=7 (108 arrays) and n=11 (2000 arrays).
- twobase n=13 result: 1,520,352 single-base candidates, 2,592 valid
  two-base circular 12x13 arrays; cut conversion fails for ALL of them
  (python and C converters agree).
- Cumulative cut-conversion negatives: n=11: 80 mult + 2000 two-base;
  n=13: 48 mult + 2592 two-base. No structured circular array converts.

### Round 3 final: affine-twisted family (largest structured family yet)

- affine.c: rows_u = u*b + v_u (u in Zn*), b any circular arrangement,
  v a twist vector. Exactly-once coverage <=> per-delta bijection
  conditions <=> binary difference-disequality CSP on v (constraints
  precomputed from b); trivial twists v_u = a + m*u normalized by fixing
  v_1 = v_2 = 0. Every emitted array independently re-checked. Validated
  on n=7 (arrays found, none convert — consistent with T2(7) nonexistence).
- n=11: >1,000,000 distinct affine circular 10x11 arrays generated and
  cut-converted (cutconv.c, exact search): ZERO convert to a T2(11).
  Also all twists around the 80 multiplicative bases (100K+ arrays): none.
- n=13: affine arrays much rarer over random bases (~4 per 30M bases);
  twist enumeration around the 48 multiplicative bases running.
- STATUS: frontier-pushed (no verdict on T2(11)/T2(13) existence).
  The circular/cut route is now heavily mapped: structured circular
  arrays exist in abundance for both open orders, but cut-conversion
  has failed on ~1M+ arrays; and squares provably do not require
  circular structure (n=8, n=12 calibrations). General sliced
  exhaustive circular searches continue (3 child sessions + local).

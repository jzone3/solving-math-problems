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

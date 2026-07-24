# P14 / V2 (SAT encoding) — run notes

Session: V2 of 5 parallel runs. Attack: direct SAT with cardinality networks, cube-and-conquer
for the hardest instance (per problem file prompt variant 2).

## Statement re-verification (2026-07-22)

- Fetched CPro1 repo `CPro1/design_definitions/balanced-ternary-design/problem_def.py`
  (github.com/Constructive-Codes/CPro1). Definition matches problems/P14 exactly:
  V×B matrix over {0,1,2}; row sums R; col sums K; per row exactly p1 ones and p2 twos;
  for every pair of distinct rows v,w: sum_b m_vb·m_wb = L.
- CPro1 OPEN_INSTANCES contains (14,18;7,1,9;7,4), (12,15;6,2,10;8,6), (12,20;4,3,10;6,4)
  — all attempted and unsolved there. (14,28;8,3,14;7,6) not in the list (Handbook-open,
  apparently unattempted).
- Necessary conditions machine-checked for all 4: R = p1+2p2; VR = BK;
  L(V−1) = RK − (p1+4p2). All pass, so no trivial nonexistence.
- Exa literature search (2026-07-22) for these parameter tuples: only the two Rosin/CPro1
  papers, Kaski's BTD enumeration page (small parameters only), Kunkle–Sarvate notes.
  No trace of these 4 cells being resolved. Treated as still open as of July 2026.

## Encoding (encode.py)

Per cell (v,b): x1 = [m≥1], x2 = [m=2], clause x2→x1, m = x1+x2.
- Row v: card(sum_b x1 = p1+p2), card(sum_b x2 = p2)  ⇒ row sum = R automatically.
- Col b: card(sum_v x1 + sum_v x2 = K).
- Pair v<w: m_v·m_w = x1v∧x1w + x1v∧x2w + x2v∧x1w + x2v∧x2w (each term a Tseitin AND var),
  so pair-Λ is a plain cardinality equality over 4B literals — no weighted PB needed.
- Cardinality: PySAT CardEnc.equals, cardnetwrk.
- Symmetry breaking (--nosym to disable):
  - row 0 fixed to canonical pattern (p2 twos, p1 ones, zeros);
  - column lex-decreasing (rows 1..V−1 as vector) within the three constant segments of row 0;
  - adjacent-row lex-decreasing for rows 1..V−1 (double-lex, sound for row/col perm group).

Sanity: dev instance BTD(4,8;2,3,8;4,6) → SAT in <1s, matrix verified PASS by verify.py.
Note: dense dev instances (15,15;6,3,12;12,9), (18,18;2,6,14;14,10) NOT solved in 120s
by kissat — dense K=V cells are hard for this encoding, but our 4 targets are sparser.

## Verifier

runs/P14/v2/verify.py — standalone stdlib-only; checks shape, entries∈{0,1,2}, row sums/
multiplicity counts, column sums, all pairwise inner products = L; prints PASS/FAIL.
(Will be copied to solutions/P14/verify.py if any witness is found.)

## Compute log

- 2026-07-22 20:3x: launched 8 × kissat (commit head, -q; nosym runs with --sat) on
  i14-18, i12-15, i12-20, i14-28 (sym + nosym), timeout 4h each, 8 cores.
  CNF sizes: 133k–414k vars, 203k–645k clauses.

(updated below as results come in)

- ~21:30–22:00 UTC: kissat (sym encodings) reports **s UNSATISFIABLE** for
  i12-15 (12,15;6,2,10;8,6), i12-20 (12,20;4,3,10;6,4), i14-18 (14,18;7,1,9;7,4)
  within ~1–1.5h each. i14-28 still running; nosym runs still running.
  CAUTION: UNSAT under symmetry breaking — before claiming nonexistence we must
  (a) confirm nosym runs also UNSAT, and/or (b) validate the sym encoding does not
  wrongly exclude solutions. Validation in flight:
  - sanity/: sym encoding on 4 CPro1-SOLVED instances (14,21;6,3,12;8,6),
    (16,22;9,1,11;8,5), (12,16;4,4,12;9,8), (12,21;4,5,14;8,8) — must come back SAT.
  - cpsat.py: independent OR-Tools CP-SAT model (integer vars, multiplication
    equalities; only row-0 fixing as symmetry) cross-checking (12,15) — running.
  Soundness argument for sym: fixing row 0 is WLOG (all rows share the same value
  multiset, columns freely permutable); remaining group = row perms of rows 1..V-1 ×
  column perms within row-0 segments; double-lex (Flener et al. 2002) has a
  representative in every orbit of such a product group.

## STATUS: running

- 00:40 UTC: 4h budget expired: nosym runs and i14-28 (sym) all TIMEOUT (no answer).
  All four sanity known-SAT instances returned SAT and their decoded matrices verify PASS
  → sym encoding does not wrongly exclude designs on any tested solvable sibling.
- 00:45 UTC relaunch (12h budgets): nosym × 3 UNSAT candidates; i14-28 sym; kissat with
  DRAT proof logging for i14-18/i12-15/i12-20 (to certify UNSAT with drat-trim);
  CP-SAT independent model on (12,15) (earlier CP-SAT run died silently, restarted).

- 02:04 UTC: drat-trim gotcha: our CNFs carry `c map ...` comment lines after the header;
  drat-trim misparses those and reports a bogus instant "c trivial UNSAT / s VERIFIED".
  Detected (fresh kissat couldn't reproduce an instant UNSAT), stripped comments
  (grep -v '^c'), re-ran real checks.
- 02:20–03:30 UTC: real DRAT verification: i12-15 **s VERIFIED** (2573s),
  i12-20 **s VERIFIED** (2570s); i14-18 still checking.
  Note: original kissat solve times were only ~1–10 min per instance (mtimes show
  i12-15.out done at 20:36, proofs at 00:44–00:48 within minutes of relaunch).
- 03:25 UTC: i14-18 DRAT also **s VERIFIED** (3274s; 5.48M/11.5M lemmas in core,
  650M resolution steps, 1372 RAT lemmas). All three UNSAT sym CNFs are now
  machine-certified: the CNFs themselves are unsatisfiable.
  Remaining links for a nonexistence claim: (a) encoding faithfulness (validated on 5
  known-SAT siblings, decoded+PASS), (b) symmetry-break soundness (row-0 WLOG +
  double-lex, Flener et al. 2002), (c) independent cross-checks: nosym kissat (12h)
  and OR-Tools CP-SAT integer model on (12,15) — both still running.

- 12:45 UTC: 12h budgets expired: nosym kissat runs (all 3) and monolithic i14-28 sym
  run TIMEOUT without verdicts; CP-SAT single-shot on (12,15) returned UNKNOWN at 12h.
  So the no-symmetry cross-checks are inconclusive by brute force — expected, the
  unbroken search space is enormous.
- Cross-check strategy replaced by cpsat_cubes.py: CP-SAT per row-1 cube, using ONLY
  elementary WLOG symmetry (row 0 fixed; row 1 canonical per segment given its
  per-segment counts) — no lex/double-lex assumptions. All cubes INFEASIBLE would
  independently confirm nonexistence. Launched on (12,15): 11 cubes, 4h/cube cap.
- Cube-and-conquer on (14,28) (13 row-1 cubes, kissat): cube0 UNSAT (~10 min);
  remaining cubes running (some >5h each).

- 19:55 UTC: literature-consistency test: sym encoding of (12,26;3,5,13;6,5) — the
  instance Greig PROVED nonexistent — returns s UNSATISFIABLE in <10 min. Encoding+
  symmetry-breaking now reproduces literature in both directions (5 known-existing
  siblings SAT with verified witnesses; 1 known-nonexistent instance UNSAT).
- Lex-free cross-check cubes (xcheck/, 23 CNFs: 11+7+5 for (12,15)/(12,20)/(14,18),
  row0+row1 fixed only, no lex) running since 17:11; none finished after ~2.7h —
  much harder without double-lex pruning, as expected.

## Final wrap-up (2026-07-24 00:45 UTC)

Lex-free cross-check cubes (xcheck/): none of the 23 finished after ~7.5h of 7-way
parallel kissat (no double-lex pruning ⇒ far harder). Left inconclusive; replication
of the three UNSATs by an independent encoding/solver remains the open follow-up
(recommend: orbit/Kramer–Mesner ILP from V3, or a fresh SAT encoding by another session).

### Results summary
- **(14,28;8,3,14;7,6): EXISTS — SOLVED.** Witness found by cube-and-conquer
  (13 row-1 cubes, kissat; SAT cube after ~10h). Verified PASS by
  solutions/P14/verify.py and by a second, independently-written numpy check.
  Witness: solutions/P14/witness-14-28-8-3-14-7-6.txt.
- **(12,15;6,2,10;8,6), (12,20;4,3,10;6,4), (14,18;7,1,9;7,4): UNSAT (nonexistence
  claimed).** kissat proves the symmetry-broken CNFs unsatisfiable (each in minutes);
  DRAT proofs (1.1–1.8 GB) checked by drat-trim: s VERIFIED (real backward check;
  beware drat-trim silently misparsing CNFs with mid-file comments — strip them).
  Claim rests on: (a) encoding faithfulness — validated by SAT+PASS on 5 known-existing
  siblings and UNSAT on Greig's proven-nonexistent (12,26;3,5,13;6,5);
  (b) symmetry-break soundness — row-0 fixing is elementary WLOG; double-lex on the
  remaining (V-1)×B submatrix with column group restricted to row-0 segments is sound
  by Flener et al. 2002. Independent replication still recommended before closing cells.

### Compute spent (approx)
~30h wall on 8 cores: 4h+12h monolithic runs (sym/nosym × 4 instances), 3 proof
reruns + 3 drat-trim verifications (~45 min each), 13-cube conquer on (14,28)
(~10h, 3–4-way), 5 sanity SAT runs, Greig UNSAT run, 23 lex-free cross-check cubes
(7-way, unfinished), 2 CP-SAT attempts (12h UNKNOWN; per-cube 4h UNKNOWN).

### Near-misses / dead ends
- Pure nosym kissat: no verdict in 12h on any instance.
- CP-SAT (OR-Tools): too slow both monolithic and per-cube at tested budgets.
- drat-trim "c trivial UNSAT / s VERIFIED" on comment-bearing CNFs is a false
  verification — a genuine tooling trap worth remembering.

## STATUS: SOLVED — (14,28;8,3,14;7,6) constructed & verified; plus frontier-pushed:
## DRAT-certified nonexistence claims for (12,15), (12,20), (14,18) pending
## independent replication.

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

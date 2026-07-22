# P14 — V4 (annealing++) run notes

Session: devin-59c4245d486b450cb78a3c35dbe3f0de (2026-07-22).
Variant V4: CPro1-style local search with multi-objective adaptively-weighted energy,
restarts from LP-relaxation roundings.

## 0. Statement re-verification & openness check

- Problem file statement matches `research/combinatorial-designs.md` §3.
- Checked against Kunkle–Sarvate's BPTD tables (https://kunklet.people.charleston.edu/section.pdf,
  the Handbook-adjacent survey table): all four cells present with **"known b2's: none"**:
  - `#15 (43): 14 18 7 1 9 7 4 — none known, open b2=14`
  - `#31 (76): 12 15 6 2 10 8 6 — none known, open b2=6..15`
  - `#33 (79): 12 20 4 3 10 6 4 — none known, open b2=12..20`
  - `#121 (234): 14 28 8 3 14 7 6 — none known, open b2=14..28`
  i.e. no BTD (any b2) is known for any of the four ⇒ still open as of that table. Quick Exa
  literature sweep (Kunkle/Sarvate BTD papers, Kaski–Östergård BTD enumeration page, AJC BTD
  papers) turned up no construction for these parameter sets.

## 1. Necessary-condition sanity (machine-checked, `sanity.py`)

All four instances pass: R = ρ1+2ρ2, VR = BK, and total pair coverage
(BK² − (Vρ1+4Vρ2))/2 == Λ·C(V,2). No cheap counting contradiction ⇒ search is warranted.

## 2. Encoding

Witness = V×B matrix over {0,1,2}. Constraints:
- row i: exactly ρ1 ones, ρ2 twos (⇒ row sum R);
- column j: sum = K;
- pair (i,k): Σ_j M[i,j]·M[k,j] = Λ.

Search state space: rows kept feasible by construction (each row a permutation of the
multiset {1^ρ1, 2^ρ2, 0^(B−ρ1−ρ2)}); move = swap two entries within a row. Column-sum and
pair violations are the (soft) energy.

## 3. Solver evolution

- `anneal.c` (v1): plain Metropolis SA, squared violations, two class weights (w_col, w_pair)
  adaptively bumped, geometric cooling + reheats. ~20M moves/s. On instance 1
  (14,18;7,1,9;7,4): 8×400M-iter seeds all plateau at total squared violation 14–15
  (e.g. col=0/pair=14 — 14 pairs off by ±1). Never reached 0.
- `anneal2.c` (v2): two-phase; phase 2 uses compound trades preserving BOTH row composition
  and column sums, per-pair dynamic weights, Metropolis. Worse (plateau ~16); the
  doubly-constrained neighborhood seems too rigid to tunnel between basins.
- `anneal3.c` (v3, main engine): breakout / dynamic-weight local search (Morris' breakout):
  L1 violations, per-column and per-pair integer weights, greedy + 50% sideways acceptance,
  at each local minimum increment weights of violated constraints; random restart after 4000
  weight bumps. LP-rounding start supported (see below).

### Engine validation on known-existing siblings
- BIBD smoke tests (7,7;3,0,3;3,1), (7,14;6,0;3,2), (9,12;4,0;3,1): SOLVED in <1s each.
- CPro1-solved sibling BTD(12,16;4,4,12;9,8): SOLVED by 4/6 seeds within 300s
  (fastest ~12s); witness re-verified by `solutions/P14/verify.py` → PASS.
  (v1/v2 could NOT solve this sibling — v3 is the validated engine.)

## 4. LP-relaxation roundings (`lp_starts.py`)

LP relaxation of the multiplicity-indicator ILP keeping the linear classes (row composition,
column sums, x1+x2≤1), random objective to sample vertices (scipy HiGHS), row-wise randomized
rounding proportional to fractional x1/x2. 8 starts generated per instance
(`starts_i1..i4/`). Pair constraints are quadratic in cell values and stay with the annealer.

## 5. Search log

- Round 1 (20:57–21:57 UTC): 2 workers/instance × 3600 s (one LP-rounded start + one
  random-restart worker per instance), engine v3. Best L1 violation reached
  (L1 = Σ|colsum−K| + Σ|P_ik−Λ|; 0 = solved):
  | instance | LP-start worker | random worker |
  |---|---|---|
  | (14,18;7,1,9;7,4)  | 12 | 10 |
  | (12,15;6,2,10;8,6) | 4  | 4  |
  | (12,20;4,3,10;6,4) | 6  | 6  |
  | (14,28;8,3,14;7,6) | 10 | 10 |
  Near-miss matrices saved in `round1/best_*.txt`. No solves.
- `anneal4.c` (WalkSAT-style targeted moves at violated constraints): validated WORSE on the
  known sibling (L1 16–18 in 120 s where v3 solves); the O(V²) violated-constraint scan per
  move kills throughput and targeting hurts diversification. Dead end; kept for the record.
- Basin hopping (`hop.sh` + `perturb.py`): keep best matrix, kick with 8 random in-row swaps,
  re-anneal 300 s legs. Smoke test on sibling (12,16;4,4,12;9,8) from its L1=14 near-miss:
  SOLVED in the first leg. Promising escape mechanism from the plateau.
- Round 2 (22:0x UTC, 3 h): 8 basin-hopping workers, 2 per instance, seeded from round-1
  near-misses, 300 s legs.

## STATUS: running

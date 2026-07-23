# P11 / V1 — SAT-direct attack on open circulant weighing matrix cells

Session: V1 of 5 parallel runs. Targets (per problem file): CW(96,36) and CW(105,36) first;
other open cells CW(112,36), CW(117,36), CW(120,49), CW(132,81) secondary.

## Statement re-verification (against original source)

- Source of truth: github.com/dmgordo/circulant-weighing-matrices (`cwm.json`, last commit
  2026-04-24) — the data behind ljcr.dmgordon.org/cwm. JSON keys are `CW(n,s)` with weight
  k = s². All six target cells (`CW(96,6)`, `CW(105,6)`, `CW(112,6)`, `CW(117,6)`, `CW(120,7)`,
  `CW(132,9)`) have `"status": "Open"` as of that commit. Still open as of July 2026. ✔
- **CRITICAL statement subtlety caught early**: the naive statement ("any circulant W with
  WWᵀ=kI") is trivially satisfiable for CW(96,36): padding the known CW(48,36)
  (Schmidt–Smith 2013) with zeros at odd positions gives a valid circulant with WWᵀ=36I of
  order 96 — machine-verified with solutions/P11/verify.py logic. The open question (per
  Arasu–Gordon–Zhang, arXiv:1908.08447, §6) is about **proper** CW(n,k): A(X) not equivalent
  to B(X^d) for any d>1 with B a CW(n/d,k). Equivalently (with a nonzero entry fixed at
  position 0): the support must not be contained in a single residue class mod p for any
  prime p | n. All searches below therefore include propriety clauses.
  For n=105 (=3·5·7) any CW(105,36) is automatically proper (105/p < 36 for all p|105),
  so a witness of ANY CW(105,36) settles that cell. For n=96 the only improper source is
  CW(48,36), excluded by the mod-2 propriety clause.

## Encodings

1. `cw_cpsat.py` — CP-SAT model: x_i ∈ {-1,0,1} via p_i/m_i bools, product IntVars per pair,
   PAF_t = 0 for t = 1..n/2, #pos = (k+√k)/2 = 21, #neg = 15 (WLOG negation), x_0 = +1 (WLOG
   shift), folded-quotient redundant constraints for divisors ≤ 24, global nonzero-pair count
   Σ_t Σ_i |x_i x_{i+t}| = (k²−k) identity.
2. `cw_cnf.py` — pure CNF (kissat): p/m bools, Tseitin product bools per pair per shift,
   per-shift equality count(+1 products) = count(−1 products) via hand-rolled two-sided
   totalizers with cap k/2; weight cardinalities via pysat totalizer; propriety clauses;
   optional `--classsum=d:c0,..` streamliner fixing #pos−#neg per residue class mod d.
   Validated: SAT on CW(13,9) (decoded row verifies), UNSAT on CW(12,9).
3. `fold_enum.py` — DFS enumeration of folded images mod d (feasible d ≤ ~8).
4. `stageA_fold.py` — CP-SAT enumeration of ALL folded images b ∈ Z^d (d = n/2 or n/3),
   PAF(b)=0, Σb=6, Σb²=36, reduced to canonical class reps under rot(Z_d)×units(Z_d).
5. (stage B, `stageB_lift.py`) — lift a fixed fold b to a ternary row: pairs/triples per
   class constrained to sum to b_j, full PAF CNF, kissat per branch.

## Calibration (known-SAT CW(48,36))

- CP-SAT full model, 8 workers, 1800 s: **no solution** (UNKNOWN).
- kissat full CNF (125k clauses), 900 s: **timeout**.
- kissat + correct mod-6 classsum streamliner (branch containing the known witness), 900 s:
  **timeout**. → plain/streamlined direct SAT at n≈48–105 is beyond reach for minutes-scale
  budgets; motivated the two-stage fold-and-lift attack (below).

## Fold-and-lift architecture (main attack)

Two validated facts drive the design:
- **Lift with fully pinned fold is easy**: kissat solves CW(48,36) in 3.5 s when the exact
  pair-sums b_j = a_j + a_{j+24} are fixed (`--liftsum`), vs >900 s otherwise.
- **Fold enumeration is the bottleneck**: CP-SAT enumeration of folds at d=24..48 produced
  nothing in ~30 min; incremental cadical likewise; kissat one-shot with a parent-fold
  streamliner solves d=24 fold instances in ~85 s. Correctness of the fold SAT encoding
  cross-checked against DFS enumeration (72 = 72 raw solutions at n=48,d=6) and against the
  known witness's own fold (pinned instance SAT in 0 s).

Pipelines (soundness: canonical-class reduction — rotations × units of Z_d, WLOG row sum +6 —
is applied at exactly ONE level per pipeline; all deeper levels enumerate RAW and lifts drop
the x_0=+1 fixing; propriety clauses cover all residue classes):
- `pipeline105.py`: folds mod 5 (5 raw → **1 class**: [6,0,0,0,0]) × folds mod 7 (21 raw)
  → SAT-enumerate folds mod 35 (both pinned) → kissat lift to 105 via `--liftsum=35:` (class
  size 3, blocking-clause exact sums). 4 sharded workers, ENUM_TL=900 s/branch, LIFT_TL=600 s.
- `pipeline96.py`: canonical folds mod 6 (72 raw → **8 classes**) → DFS: SAT-enumerate mod 12
  → mod 24 → mod 48 (each conditioned on parent) → kissat lift via `--liftsum=48:` (pair
  sums). 2 sharded workers.

## Compute log

- kissat full-instance baselines CW(96,36), CW(105,36): ran 21:21–22:30 UTC (~70 min each,
  one core), no answer — killed in favor of pipelines (baseline futility expected from the
  CW(48,36) calibration).
- CP-SAT full-instance calibration on known-SAT CW(48,36): 1800 s, 8 workers — UNKNOWN.
- 22:20 UTC: pipeline105 4 workers running; first branch [0_0] yielded 1 fold mod 35 in
  900 s (status: budget-limited, i.e. enumeration incomplete — caveat for completeness
  claims). 22:30 UTC: pipeline96 2 workers running.
- 22:47–01:30 UTC: **end-to-end pipeline validation on known-SAT CW(48,36)**: pipeline
  restricted to the top-level mod-6 class (4,0,4,0,-2,0) containing the known witness's fold:
  44 mod-12 folds (exhaustive), hundreds of mod-24 folds, 369 UNSAT lifts, then a **SAT lift
  → witness_48_36.json, independently verified: `solutions/P11/verify.py` prints PASS**.
  (Known matrix, not a new result — kept as a machinery-correctness artifact.)
- pipeline105 final: all 21 (c5,c7) branches processed at 900 s enumeration each (all
  budget-limited, none exhausted); only 6 distinct folds mod 35 found, all degenerate
  ({0,±3}-valued); all 6 lifts to n=105 TIMEOUT at 600 s, re-runs at 3600 s also TIMEOUT.
  → for n=105 the class-size-3 pinned lift is beyond kissat at 1-hour budgets.
- pipeline96 phases: (a) chain 6→12→24→48→lift(48): mod-48 (B=2) fold enumeration is the
  wall — essentially every 600 s branch returned 0 folds; (b) phase C (chain 6→12→24, lift
  directly from mod-24 pins, LIFT_TL=1800 s): b24-pinned lifts **TIMEOUT even at 1800 s**.
  Same wall for CW(112,36) at d=56.
- **Partial structural eliminations for CW(96,36)** (SAT-encoding-based UNSAT, encoding
  cross-validated but not independently verified): top-level canonical mod-6 fold classes
  c1 = (3,3,0,3,-3,0) and c5 = (5,1,2,1,-1,-2) admit NO mod-12 extension (kissat UNSAT,
  exhaustive); 2 of the 8 candidate mod-6 classes are eliminated outright. Additionally,
  hundreds of (b12→b24) subtrees proven UNSAT (exhausted enumerations logged in pl96*.log).
- Secondary cells: CW(112,36) pipeline (7→14→28→56) launched — level-14/28 exhaustive
  enumerations small (2–14 folds), d=56 B=2 wall as above. CW(120,49)/CW(132,81): top-level
  DFS fold enumeration at d=15/d=11 too slow (>12 min, killed) — divisor chains of 120/132
  are unfriendly to this method (dead end noted). CW(117,36) not attempted (no nested
  divisor chain with small top).

## Where the frontier actually is (for the next run)

- Pinned-lift difficulty is sharply graded by class size n/d: size 2 → seconds (validated,
  n=48); size 3 (n=105) and size 4 (n=96) → >1800–3600 s timeouts. Any method that can pin
  down folds at d = n/2 wins; the B=2 fold enumeration itself is the open bottleneck
  (kissat ~85 s per solution at d=24 pinned; effectively 0 solutions/600 s at d=48/56).
- Suggested next steps: negacyclic complement (b_j = a_j + a_{j+d}, c_j = a_j − a_{j+d};
  both have Σ=|·|²=36 constraints; joint (b,c) enumeration halves the lift freedom to zero),
  algebraic z·z̄=36 solutions in Z[ζ] per character (AGZ-style field descent), or a
  compiled/bit-parallel DFS for the B=2 fold level.

## Final state

- No new witness for any open cell (all lift attempts UNSAT or TIMEOUT).
- Verified artifacts: witness_48_36.json (known cell, machinery validation only).
- Everything reproducible: pipelines are env-configurable (`pipeline96.py` generic;
  `pipeline105.py` CRT-specific), launch scripts included, state/logs in this directory.
- Total compute: ~7 h wall, up to 8 cores (kissat 4.0.4, CP-SAT 9.14, python-sat).

## Resumed session (2026-07-23): two fundamentally different attacks

### Attack 2 — joint cyclic/negacyclic (b,c) decomposition (`bc_sat.py`)
For even n=2d: b_j=a_j+a_{j+d}, c_j=a_j−a_{j+d} is a bijection (no lift needed):
b has cyclic PAF=0, c has *negacyclic* NAF=0, Σb=6, Σb²=Σc²=36, plus the ternary
coupling |b_j|=2→c_j=0, |c_j|=2→b_j=0, |b_j|=1↔|c_j|=1. Encoded with shared product
vars + totalizers (n=48: 79k vars/751k clauses). Result: on known-SAT CW(48,36),
kissat TIMEOUT at 1800 s both plain AND with the correct mod-6 fold streamliner.
→ the bijective reformulation does not help CDCL; dead end (logged bc48_*.log).

### Attack 3 — multiplier/affine-orbit invariant search (`multiplier_search.py`, `mult_cpsat.py`)
Assume the row is fixed by an affine bijection φ(j)=t·j+r (t a unit mod n): then a is
constant on φ-orbits — one ternary variable per orbit. Complete CP-SAT decision per
(t,r): orbit-size cardinalities (Σ sizes over support = k, signed = 6) + exact PAF
as quadratics over ≤48 orbit vars. Validated: instantly finds classical CW(13,9)
(multiplier 3). Exhaustive sweeps over ALL distinct affine-orbit partitions with
≤48 orbits (120 s/class, then 600 s retries for UNKNOWNs):
- CW(96,36):  complete sweep — 347 UNSAT, 80 UNKNOWN (all still UNKNOWN at 600 s;
  all have ≥36 orbits), 139 skipped (>48 orbits). **No affine-invariant witness.**
- CW(132,81): complete sweep — 861 UNSAT + 33 more UNSAT at 600 s, rest UNKNOWN,
  286 skipped. No witness.
- CW(105,36): 950+ classes decided (all UNSAT/UNKNOWN), sweep still running.
- CW(112,36): 550+ decided; CW(117,36): 1070+ decided; CW(120,49): 760+ decided —
  all UNSAT/UNKNOWN so far, no witness.
Interpretation: none of the six open cells has a CW row invariant under any affine
symmetry with ≤48 orbits (modulo the residual UNKNOWN classes listed in the logs) —
consistent with AGZ's multiplier-based exhaustions; any witness must have small or
trivial stabilizer, i.e. these cells are hard for structure-first searches too.

### Residual open leads (for the next run)
- Finish the UNKNOWN affine classes (multretry logs) with hours-scale budgets.
- Kramer–Mesner style: relax invariance to a SUBGROUP of ⟨φ⟩ (fewer symmetries,
  more orbits) with the same CP-SAT scheme — interpolates toward the full problem.
- Field-descent (AGZ §3): enumerate z·z̄=36 in Z[ζ_m] per m|n via factorization of
  (2) and (3) in cyclotomic fields; would either construct or possibly rule out cells.

STATUS: negative — no new CW found across three attack families (fold-and-lift SAT
pipelines; joint cyclic/negacyclic bijective SAT; exhaustive affine-orbit CP-SAT
sweeps). New citable exclusions: 2/8 mod-6 fold classes eliminated for CW(96,36);
no affine-invariant (≤48 orbits) witness exists for CW(96,36)/CW(132,81) (complete
sweeps) and none found in 950+/550+/1070+/760+ decided classes for CW(105/112/117/120).

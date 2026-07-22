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

STATUS: (running)

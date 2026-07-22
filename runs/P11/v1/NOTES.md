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

## Compute log (running)

- kissat full-instance baselines on CW(96,36) and CW(105,36) (propriety clauses included),
  started 21:21 UTC, one core each — long-shot background runs.
- stage A fold enumerations: n=96 d=48 (b∈[-2,2]^48) and n=105 d=35 (b∈[-3,3]^35), started
  ~21:30 UTC.

STATUS: (running)

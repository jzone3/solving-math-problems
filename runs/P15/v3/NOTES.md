# P15 V3 — SAT layered attack on min-modulus covering systems

Session: https://app.devin.ai/sessions/0ad9a586fd2a4844851a6a7b4d2a20a6
Variant: V3 (SAT encoding, layered over prime factorization, incremental escalation)

## Statement re-verification (2026-07-22)
- Owens, "A Covering System with Minimum Modulus 42", BYU MSc thesis 2014
  (scholarsarchive.byu.edu/etd/4329) — confirmed: record 42, distinct moduli.
- Nielsen, "A covering system whose smallest modulus is 40" — confirmed; NOTE: Nielsen's
  min-mod-40 system has MORE THAN 10^50 congruences (recursive tree construction). The
  problem file's guess of 10^3–10^6 congruences for a 43-witness is almost certainly a
  large underestimate.
- Hough (Annals 2015): min modulus ≤ 10^16; BBMST 2022: ≤ 616,000. Literature search
  (Exa, 2026-07) found no construction beating 42. Problem confirmed open.

## Encoding
Fix a smooth lcm candidate N. Variables x[n][a] for each divisor n ≥ m of N (n > 1) and
residue a mod n. Constraints:
1. At-most-one residue per modulus (distinct moduli ⇒ each modulus used ≤ once).
2. Coverage: for every t in Z_N, OR over divisors n ≥ m of x[n][t mod n].
Symmetry breaking: translation symmetry of Z_N — smallest divisor d1 ≥ m, if used, is
forced to residue 0.
Necessary feasibility screen: Σ_{n|N, n≥m} 1/n ≥ 1 (each class covers density 1/n).

## Key literature calibration (found mid-session, crucial)
- Dalton–Trifonov, "Extreme Covering Systems", J. Integer Seq. 25 (2022): minimal lcm
  L(m=3)=120, L(m=4)=360 (proved optimal).
- Klein, arXiv:2508.18062 (Aug 2025): L(m=5)=1440, L(m=6)=5040 proved optimal
  (Krukenberg's constructions); L(m=7)=15120 conjectured optimal. Max modulus for m=5
  is ≥108. Historical m records: Swift 4/6, Churchhouse 9, Krukenberg 18, Choi 20,
  Morikawa 24, Gibson 25, Nielsen 40 (recursive, >10^50 congruences), Owens 42.
- Consequence: my early SAT targets m=5 with N ∈ {360, 720} were provably UNSAT
  (N < 1440 or wrong divisor structure) — explains hours of kissat grinding without
  answers. UNSAT proofs of these set-cover instances appear exponentially hard for CDCL.

## Tooling log
- cover_sat.py / cover_kissat.py: direct full-N encoding. pysat Glucose4/Cadical too weak;
  kissat 4.0.4 (built from source) solves m=4/N=2520 in 14 s (45 congruences, verified).
- GOTCHA: pysat's C-level solve holds the GIL — threading.Timer-based timeouts never fire.
  Replaced with conflict-budget chunks (cover_sat.py) / kissat --time (subprocess).
- AMO encoding bug caught by verifier: sequential-counter final clause used s[-2] instead
  of s[-1], silently allowing two residues on one modulus. Machine verification caught it
  (methodology rule 4 vindicated). Fixed; layered.py results before the fix discarded.
- layered.py: per-prime-power-layer MaxSAT (holes-only clauses) — works but pysat RC2 /
  anytime linear search too slow >~3k holes; greedy layer variant loses hole alignment
  (locally optimal hole counts pick unliftable hole sets — m=3 test failed at final layer).
- layered2.py: hybrid — interior layers MaxSAT (small) or greedy (large), FINAL WINDOW of
  ladder factors solved jointly and exactly with kissat over the lifted holes. Reproduces
  m=3 (lcm 120, 14 congr) and m=4 (lcm 2520, 45 congr) instantly; both verify PASS.

## BREAKTHROUGH: stochastic local search >> CDCL on these instances
- YalSAT (Biere) solves m=5/N=1440 (Krukenberg-minimal lcm) in <8 s where kissat 4.0.4
  made no visible progress in >1.5 h. m=6/N=5040 (proven-minimal lcm) in 302 s.
  Both witnesses verified by solutions/P15/verify.py (independent CRT-recursive check).
- ylocal.py: pairwise/sequential AMO encoding, no symmetry-break units, yalsat + decode
  + strict duplicate-modulus and coverage assertions before writing witness JSON.
- BreakID found 0 CNF-level symmetry generators (aux vars scramble the syntactic
  symmetry; translation orbit is there mathematically but not syntactically cheap).

## Witness-scale calibration for m=43 (min_lcm_bound.py)
Reciprocal necessary condition alone forces, for m=43: lcm N ≥ 183,783,600
(= 2^4·3^3·5^2·7·11·13·17, recip barely 1.005) and ≥926 congruences. True L(m) exceeds
the reciprocal bound by growing factors (L(5)=1440 vs 240; L(6)=5040 vs 720;
L(7)=15120 (conj) vs 1260), so a real m=43 cover likely needs lcm ≫ 10^10 and far more
congruences — direct full-N encodings are out of reach (CNF alone ≥10^11 literals);
only hole-layered approaches could ever scale, and their exact final windows blow up.

## Run log
- SAT+verified: m=3 N=120 (14 congr), m=4 N=2520 (45 congr, kissat 14s), layered2 m=4.
- TIMEOUT (≥900s, now known misguided): m=5 N∈{360,720,2520} direct; layered2 m=5
  final at N=2520 (provably requires lcm ≥1440 with different structure).
- kissat direct on literature-calibrated targets (m=5,N=1440)...(m=10,N=110880):
  NO ANSWERS after 1.5–4 h each — CDCL wall. Killed in favor of local search.
- YalSAT+verified: m=5 N=1440 (32 congr, 8 s), m=6 N=5040 (46 congr, 302 s).
- yalsat single-seed batch (m=7,15120) (m=8,30240) (m=9,55440) (m=10,110880)
  (m=12,166320) (m=12,332640): no hits in ~35 min each; killed for focused runs.
- yalsat -v diagnostics on m=7/N=15120: descends to ~13 unsatisfied clauses in seconds,
  then plateaus (classic SLS heavy tail). 8-thread palsat: no solution in ~1 h.
- greedy_sat.py (full-N greedy + kissat hole repair), m=7/N=15120, stop_ratio sweep
  {0.02, 0.05, 0.1, 0.2}: greedy either consumes too many moduli (residual UNSAT:
  126 holes/12 mods; 56 holes/1 mod) or stops too early (7848 holes/69 mods — kissat
  timeout). The alignment problem is global; local repair window is too narrow at m=7.
- palsat 4-thread on slacker targets (m=7,N=30240 recip 1.55) and (m=8,N=55440
  recip 1.59): no solution in ~1.5 h each. m=7 is the local-search wall on 8 cores.

## Verified witnesses (all pass solutions/P15/verify.py; see witnesses/)
| m | lcm    | #congruences | method            | time  |
|---|--------|--------------|-------------------|-------|
| 3 | 120    | 14           | layered2 + kissat | <1 s  |
| 4 | 2520   | 45           | layered2 + kissat | ~15 s |
| 5 | 1440   | 32           | yalsat direct     | 8 s   |
| 6 | 5040   | 46           | yalsat direct     | 302 s |

m=5 and m=6 witnesses hit the PROVEN-minimal lcms (Klein 2025), i.e. the SAT pipeline
reproduces the extremal known constructions fully automatically.

## Conclusions
1. Direct SAT on covering systems is CDCL-hostile (huge translation/unit symmetry,
   set-cover core); stochastic local search is the right engine, but stalls at m=7
   on this hardware within hours.
2. The gap to the target m=43 is astronomical: reciprocal bound alone needs
   lcm ≥ 1.8·10^8 / ≥926 congruences, and true structure pushes far beyond; explicit
   enumeration-based SAT cannot bridge 7 → 43. A 43-witness will need Nielsen/Owens-style
   recursive tree constructions (V4/V5 territory), likely with >>10^6 congruences.
3. Negative-but-calibrated result: V3 as specified (layer-by-layer SAT over the prime
   tower) is exhausted at the compute scale available; artifacts, encodings, and the
   local-search discovery are reusable for follow-up runs.

## SECOND PHASE (coordinator requested new methods after CNF-SAT exhaustion)

### Cube-and-conquer (negative)
cube_conquer.py: cubes = joint residue choices of scarce pure-prime-power moduli
(e.g. 8,16,9), translation-canonicalized, kissat per cube. On m=6/N=5040 every cube
timed out at 30 s — each cube retains the whole global alignment problem. Dead end.

### Native weighted min-conflicts (BREAKTHROUGH #2)
anneal.py → anneal2.py (numpy, greedy init, breakout hole-weighting, kissat endgame
repair) → anneal3.py (incremental hole tracking) → cover_mc.c (C engine, ~325k it/s,
~300x python). State = one residue per divisor ≥ m of N; energy = #holes; move =
min-conflicts reassignment of a random modulus; stagnation bumps hole weights
(breakout/PAWS style). Searching the combinatorial space directly beats CNF/SLS
(yalsat plateaued at m=7; native engine solves it in seconds–minutes).

KEY EMPIRICAL LAW: reciprocal slack drives feasibility. m=9 at N=55440 (recip 1.47)
stalled at ~800 holes; at N=332640 (recip 1.65) solved. Choose N with recip ≥ ~1.6.

### Verified witnesses, phase 2 (all PASS solutions/P15/verify.py)
| m | lcm     | #congr | engine  | time   |
|---|---------|--------|---------|--------|
| 7  | 15120    | 74     | anneal2  | 243 s  |
| 8  | 30240    | 89     | anneal2  | 341 s  |
| 9  | 332640   | 184    | anneal2  | 3541 s |
| 10 | 2162160  | 311    | cover_mc | 6373 s |
| 11 | 21621600 | 566    | cover_mc | greedy init alone |
| 12 | 21621600 | 565    | cover_mc | greedy init alone |

m=7 lcm 15120 matches Klein's conjectured-minimal L(7); found fully automatically.

### Engine evolution & lessons
- cover_mc.c: full-Z_N C engine, ~325k it/s at N=15120; per-move cost O(#holes+N/n).
- Stagnation kicks (restore best, reset weights, reshuffle ~8 random moduli) were
  essential for m=10: plateau at ~2-3k holes then staircase descent to 0 over ~90 min.
- Reciprocal slack law refined: greedy init ALONE covers when slack is high enough
  relative to m (m=11,12 at N=21621600, recip 1.84-1.93 → 0 holes at init).
  But slack needed grows with m: m=13 at recip 1.87 (N=73513440) still leaves
  ~273k holes after greedy; per-move cost at N~10^8 (holes ~10^5-10^6) drops to
  ~30 it/s — the explicit-enumeration wall for this engine is m≈13.
- layered_mc.py + holes_mc.c (Krukenberg-style layer-by-layer with hole-set C
  engine): validated mechanically but strictly worse than direct search at m=7
  (layers over-consume small moduli; final layer starved). Would need Krukenberg's
  hand-tuned modulus rationing to work — future direction.

Scaling summary: m=43 needs recip slack ≈1.8+ over divisors ≥43, i.e. lcm ~10^13+
and ~10^4-10^5 congruences — outside explicit-array methods entirely; a recursive/
symbolic construction (Nielsen/Owens style) is the only plausible route.

STATUS: frontier-pushed (verified covering systems built automatically for every
m ≤ 12 — previous automatic frontier here was m=4-6; no m≥43 witness — explicit
enumeration cannot reach it, see calibration)

# P01 Sheehan — V3 (SAT/CEGAR) run notes

Session: devin-93cec269c002482d9b6c7bf18aff8f4b (V3 of 5 parallel runs)
Branch: runs/P01-v3

## Source & openness re-verification (2026-07-22)

- Fetched openproblemgarden.org/op/uniquely_hamiltonian_graphs: statement matches
  problems/P01-sheehan.md — "no finite 4-regular (simple) graph is uniquely
  hamiltonian" (Sheehan 1975). OPG comments (2022) confirm the Jackson–Whitehead-style
  multigraph constructions are NOT counterexamples (parallel edges); conjecture open.
- arXiv search "uniquely hamiltonian" sorted by date (through 2026-06): no paper
  resolving the 4-regular case. Latest relevant: symmetry classes of HCs (2025),
  vertex-transitive unique-HC (2023). Treated as still OPEN as of July 2026.

## Encoding (the V3 idea)

Key symmetry breaking: WLOG relabel a counterexample so its unique HC is the base
cycle C_n = (0,1,...,n-1). Then the remaining edges form a set X of chords with
**exactly 2 chord-endpoints per vertex** (a 2-regular chord graph / 2-factor of
K_n − C_n). Search space = such X with C_n + X having no second HC.

CEGAR loop (runs/P01/v3/cegar.py, pysat + Cadical153):
- One boolean var per chord {i,j}, cyclic distance ≥ 2. Exactly-2 per vertex via
  sequential counter encoding.
- SAT model → candidate 4-regular graph → backtracking search (hc.py) for up to 4
  Hamiltonian cycles ≠ base cycle.
- Each second HC yields blocking clause "some used chord absent", plus its 2n
  dihedral images (rotations/reflections stabilize C_n, so images are valid
  learned clauses). This symmetry-amplified clause learning is the workhorse.
- Loop exhausted (UNSAT) ⇒ no counterexample of that order. Model with no second
  HC ⇒ counterexample (would be verified independently by solutions/P01/verify.py).
- Near-miss tracking: exact HC count (early cutoff) per candidate; log minima.

## Validation

n = 8..16 all exhausted UNSAT, consistent with Goedgebeur–Meersman–Zamfirescu
(no counterexample for n ≤ 21):

| n | models enumerated | learned clauses | time |
|---|---|---|---|
| 8 | 3 | 116 | <0.1s |
| 9 | 5 | 225 | <0.1s |
| 10 | 7 | 365 | <0.1s |
| 11 | 6 | 440 | <0.1s |
| 12 | 17 | 1452 | 0.1s |
| 13 | 30 | 2795 | 0.3s |
| 14 | 54 | 5663 | 1.8s |
| 15 | 95 | 10785 | 15.5s |
| 16 | 190 | 23408 | 137s |

Time grows ~9x per vertex (SAT solve time after clause accumulation dominates),
models only ~2x — the dihedral clause amplification is effective but the final
UNSAT proof gets hard.

## Long runs (in progress; see n17.log / n18.log / n22.log)

- n=17, n=18: attempt full exhaustion (4h budget each).
- n=22: first open order, 6h budget — CEGAR acts as a guided sampler over
  hard candidates; logging near-miss minima (min #HC over sampled 2-factors).

(checkpoints appended below)

## Checkpoint 2026-07-22 ~21:00 UTC

- Fixed near-miss counting bug (early-cap was corrupting counts; first n17 run's
  "hc_count=1..32 near-misses" were spurious cap artifacts — disregarded).
- Rewrote HC search as bitmask DFS with degree pruning (any unvisited vertex
  needs >= 2 usable neighbors) — hard instances now milliseconds.
- Diagnosed apparent n=17 "stall": SAT solve times explode in the endgame
  (~0.1ms early, ~2s by model 350, then minutes+) as learned clause set nears
  UNSAT. n=16 UNSAT proof took 140s / 195 models; n=17 substantially harder.
  Logging is per-model so long solves look like stalls.
- 6 parallel runs live: n=17 (exhaust attempt), n=18 (exhaust attempt),
  n=22 (6h sampler), n=22 min-chord-dist>=3 subfamily, n=23, n=24 samplers.

## Checkpoint ~22:20 UTC — symmetry breaking pays off

- Added min-distance-chord dihedral symmetry breaking to base encoding:
  OR_d z_d with z_d -> x_{(0,d)} and z_d -> "no chord of distance < d".
  Sound (every 2-factor has a dihedral image with a min-distance chord at
  vertex 0); completeness unaffected (blocking clauses already dihedral-closed).
- Added budgeted solves (2M conflicts) + fresh-solver rebuild on stall:
  re-preprocessing the accumulated clause DB beats grinding a stale solver.
- Effect: n=17 exhaustion 1450s -> 71s (~20x). n=18 exhausted UNSAT in 1244s
  (709 models, 100k learned clauses).
- **Independent re-verification of known results so far: no 4-regular uniquely
  hamiltonian graph exists for n <= 18** (via this SAT encoding — an
  independent method from Goedgebeur et al.'s generation approach).
- In flight: n=19 (endgame, likely exhaustible), n=20 (12h budget), samplers
  n=22, n=22 (chord-dist>=3), n=23, n=24, n=26, n=28.

## Sampler results (6h/5h budgets each, 2026-07-23 ~04:00 UTC)

All timed out without finding a witness; no near-miss (candidate with < 4
Hamiltonian cycles besides the base cycle) was ever encountered:

| run | models blocked | learned clauses | wall time |
|---|---|---|---|
| n=22 | 6,517 | 1,142,229 | 6h |
| n=22 chord-dist>=3 | 2,635 | 459,448 | 6h |
| n=23 | 7,941 | 1,455,739 | 6h |
| n=24 | 11,638 | 2,227,412 | 6h |
| n=26 | 21,302 | 4,421,547 | 5h |
| n=28 | 39,076 | 8,740,620 | 5h |

Each "model" is a full 2-factor candidate; each blocking clause kills all
supersets of a second-HC chord support and all its 2n dihedral images, so the
excluded region is vastly larger than the model count. Still nowhere near
exhaustion at n>=19: the candidate space grows superexponentially and the
learned-clause DB makes late SAT calls minutes-long.

## Exhaustion frontier for this encoding

- n <= 18 fully exhausted (UNSAT) — independently re-confirms
  Goedgebeur–Meersman–Zamfirescu for those orders with a different method.
- n = 19: all but the endgame done (1,427 models blocked, then a single
  residual SAT instance resisting >3h of escalating-budget Cadical restarts).
- n = 20: same shape (2,777 models, endgame grinding).

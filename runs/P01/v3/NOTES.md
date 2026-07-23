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

## n=19 EXHAUSTED (2026-07-23 07:36 UTC)

Hybrid pipeline: incremental Cadical CEGAR to the frontier (1,433 models,
215,517 dihedral-closed blocking clauses, ~40 min), dump blocking set, then
native kissat 4.0.4 on the full DIMACS per iteration (endgame.py). Kissat
found 4 more models (up to 731s each — where incremental Cadical stalled for
hours) and then proved the residual formula **UNSATISFIABLE** in ~4,400s.

=> No 4-regular uniquely Hamiltonian graph on n=19 vertices (already known
from GMZ n<=21, but independently re-derived with a completely different
method: SAT-CEGAR over canonical-HC chord 2-factors).

n=20 pipeline running the same way.

## Final results (2026-07-23 17:25 UTC)

### Exhaustion (this SAT/CEGAR encoding, independent of GMZ's generation method)

| n | outcome | models blocked | blocking clauses | notes |
|---|---|---|---|---|
| 8–16 | UNSAT (exhausted) | 3–196 | up to 24k | seconds–minutes |
| 17 | UNSAT (exhausted) | 379 | 50,337 | 71s with symmetry breaking |
| 18 | UNSAT (exhausted) | 709 | 100,053 | 1,244s |
| 19 | **UNSAT (exhausted)** | 1,437 | 215,973 | Cadical CEGAR to frontier + kissat endgame; final UNSAT proof ~4,400s |
| 20 | NOT exhausted | ~2,975 | 440,620 | kissat endgame timed out (8h); last residual call ran 3.5h undecided |

### Deep sampling at open orders (no witness, no near-miss)

n=22 (6h), n=22 chord-dist>=3 (6h), n=23 (6h), n=24 (6h), n=26 (5h), n=28 (5h):
~90,000 candidate 2-factors blocked in total, >18M dihedral-closed blocking
clauses. Every candidate examined had >= 4 Hamiltonian cycles besides the base
cycle (near-miss tracker with exact counting below 64 HCs never fired).

### Artifacts

- cegar.py — incremental Cadical CEGAR (canonical-HC chord-2-factor encoding,
  dihedral-closed clause learning, min-distance symmetry breaking, budgeted
  solves with shuffled rebuilds, blocking-set dump).
- endgame.py — kissat-based endgame driver (warm-startable from dump).
- hc.py — pruned bitmask Hamiltonian-cycle enumerator/counter.
- n19_blocking.json.gz / n20_blocking.json.gz — frontier blocking sets
  (resume points; n20 can be resumed with endgame.py --blocking).
- solutions/P01/verify.py — independent witness verifier (DP-based exact HC
  count; would print PASS on any claimed counterexample). Cross-validated
  against hc.py on K5 (12 HCs) and C9(1,2) (41 HCs).

### Dead ends / lessons

- Naive per-model exact HC counting with an early cap silently corrupted
  near-miss statistics (fixed: exactness flag).
- Unbudgeted incremental solves stall for hours in the endgame; fresh-solver
  rebuilds + escalating budgets + native kissat on the full formula are far
  more effective there.
- Exhaustion cost grows ~9x per vertex; n=21 (the GMZ frontier) would need
  ~1 CPU-week with this encoding, n=22 several CPU-months — pure SAT-CEGAR
  will not push past the known frontier without stronger structural pruning
  (V4's genreg-style approach is better positioned for that).

STATUS: negative — no counterexample found; n <= 19 exhausted (independent
re-verification of known results), n=20 partially exhausted, deep sampling at
n=22–28 found no uniquely Hamiltonian 4-regular graph and no near-miss.

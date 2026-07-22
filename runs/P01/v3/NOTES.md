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

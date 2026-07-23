# P13 — Perfect Mendelsohn Designs, k=6 — Variant V3 (CP + LNS)

Session: https://app.devin.ai/sessions/b812022361e74034814c567e327a58cb
Machine: 8 cores, 31 GB RAM. Solvers: OR-Tools CP-SAT 9.15.6755, kissat (master, built from source), drat-trim.

## 0. Statement re-verification (against original source)

Fetched Abel & Bennett, "The existence of (v,6,λ)-perfect Mendelsohn designs with λ>1",
Des. Codes Cryptogr. 40 (2006) 211–224 (full text). Definition confirmed: blocks are
cyclically ordered 6-tuples; ordered pair t-apart in exactly λ blocks for every t=1..5;
b = λv(v−1)/6. Matches problem file / verify.py semantics.

**Discrepancy found in the problem file**: Theorem 1.4 of Abel–Bennett 2006 states the
necessary conditions for a (v,6,1)-PMD are sufficient **except for v = 6, 10** (both proven
nonexistent), with the possible exceptions including v ≡ 0 (mod 6): {12, 18, ...},
v ≡ 3 (mod 6): interval [9,135]..., v ≡ 4 (mod 6): {16, 22, 34} ∪ [52,148].
So **v = 10 was already known NOT to exist** (nonexistence result cited there), and the
genuinely open small cases per that source are v ∈ {9, 12, 15, 16, 18, ...} (the problem
file's list minus 10). A 2015–2026 literature sweep (Exa) found no later paper resolving
the k=6, λ=1 small cases; the 2020 Griggs–Kozlik paper closed k=5 only. Treated as still
open as of July 2026.

## 1. Encodings

Two independently written encodings (deliberately different structure):

(a) `pmd_cpsat.py` — OR-Tools CP-SAT. Booleans x[b][p][s] + integer channel views.
    Exactly-one per cell, all-different per block, global count v−1 per symbol,
    pair-coverage via Tseitin product vars, ExactlyOne per (ordered pair, distance).
    Symmetry breaking: block0=(0..5); per-block rotation so position 0 = block min;
    blocks strictly ordered by key = c[b][0]*v + c[b][1] (sound: distance-1 pairs are
    unique across blocks, so keys are distinct); optional first-occurrence ordering of
    symbols ≥ 6 (POTENTIALLY UNSOUND in combination with key ordering — all UNSAT claims
    below were re-run with it OFF).

(b) `gen_cnf.py` — pure DIMACS CNF for kissat, written from scratch. Same core
    constraints (pairwise AMO instead of global counts), different symmetry breaking:
    block0=(0..5); rotation-min; first v−1 blocks are exactly the blocks containing
    symbol 0 (at position 0), strictly ordered by their position-1 symbol; remaining
    blocks ordered non-strictly by position-0 symbol. `--weak` flag drops everything
    except block0=(0..5) for soundness cross-checks.

Sanity checks of the pipeline:
- v=7 (known to exist): CP-SAT SAT in 0.1 s; kissat SAT; both witnesses verified PASS by
  `solutions/P13/verify.py` (independent stdlib-only verifier).
- v=6 (known nonexistent): both encodings UNSAT instantly.

## 2. MAIN RESULT: (9,6,1)-PMD does NOT exist

- CP-SAT (encoding a, first-occ OFF): **UNSAT in 5.7 s** (also UNSAT in 2.9 s with
  first-occ on).
- kissat (encoding b, full symmetry breaking): **UNSAT in 7.3 s**, DRAT proof emitted
  (22 MB) and **verified by drat-trim: `s VERIFIED`** (27 s, 15211 RAT lemmas in core).
- kissat (encoding b, `--weak`, only block0 fixed — which is sound by relabeling alone):
  run in progress at checkpoint time; see §4 for outcome.

Fixing block 0 = (0,1,2,3,4,5) is sound WLOG (any putative design has a block, relabel its
points in cyclic order). Rotation-min per block is sound (rotations of a cyclic tuple are
the same block). Block reordering constraints are sound (a design is a set of blocks).
Hence UNSAT of the constrained instance ⇒ nonexistence of any (9,6,1)-PMD.

This settles the smallest open case **negatively**. Consistent with (and explains) CPro1's
heuristics failing to find one.

## 3. v=10 reproduction (known nonexistent — benchmark for our method)

kissat on encoding (b): run in progress at checkpoint; result recorded in §4.
CP-SAT hit UNKNOWN at 250 s — CP-SAT is much weaker than kissat on the UNSAT side here.

## 4. Runs log (updated as they complete)

| v | encoding/solver | symmetry | result | time |
|---|---|---|---|---|
| 6 | CP-SAT | full (no first-occ) | UNSAT | 0.0 s |
| 6 | kissat | full | UNSAT | <1 s |
| 7 | CP-SAT | full | SAT, verified PASS | 0.1 s |
| 7 | kissat | full | SAT, verified PASS | ~1 s |
| 9 | CP-SAT | full+first-occ | UNSAT | 2.9 s |
| 9 | CP-SAT | full, no first-occ | UNSAT | 5.7 s |
| 9 | kissat | full | UNSAT + DRAT VERIFIED | 7.3 s solve + 27 s check |
| 13 | CP-SAT | full | UNKNOWN (SAT-side hard) | 180 s limit |
| 10 | CP-SAT | full, no first-occ | UNKNOWN | 250 s limit |
| 12 | CP-SAT | full, no first-occ | UNKNOWN (no design, no refutation) | 7200 s limit |

(Additional rows appended below as longer runs finish.)

## 5. Incidents / operational notes

- First long kissat runs on v=9-weak and v=10 (with DRAT emission) died silently after
  ~65 min: /tmp is a 16 GB tmpfs and the two proofs grew to 12.9 GB + 3.8 GB and filled
  it. Relaunched both WITHOUT proof output (the DRAT-verified refutation of v=9 with
  full symmetry breaking is already archived; the weak run is a soundness cross-check
  where only the s-line verdict matters).
- Verified v=9 artifacts archived: `pmd9.cnf` + `pmd9.drat` (drat-trim `s VERIFIED`),
  gzipped copies committed under `solutions/P13/`.

## 6. LNS phase (v = 12, 15, 16, 18)

`pmd_lns.py`: phase 1 solves the packing relaxation, phase 2 hints the exact model with
the best packing. First attempt used HARD at-most-one coverage + maximize covered — CP-SAT
found no feasible solution at all in 3600 s for v=12 (feasibility itself is hard); the
script then degenerates to a plain exact run (also UNKNOWN at 3600 s, seed 1). Rewrote
phase 1 as a SOFT model: coverage counts free, minimize sum |count(pair,t) − 1| (always
feasible; deviation 0 = PMD); sanity check v=7 reaches deviation 0 in <60 s.

Soft-LNS sweep (5 workers, pack 3000 s + exact-with-hint 1500 s, seed 2):

| v | best soft-packing deviation (of 5·v·(v−1) slots) | exact-with-hint |
|---|---|---|
| 12 | 160 / 660 after 3000 s | (below) |

Rows appended as the sweep progresses.

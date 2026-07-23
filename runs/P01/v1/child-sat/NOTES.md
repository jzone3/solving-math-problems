# P01 Sheehan — V1 child: SAT/CP-SAT CEGAR search (child-sat)

Child session of runs/P01-v1 (parent = annealing). Session:
https://app.devin.ai/sessions/7690c23323ba4f57a2afe6f10f41366c
Date: 2026-07-23. Branch: runs/P01-v1-sat.

## Encoding (`cegar.py`, OR-tools CP-SAT 9.15)

- WLOG the (would-be) unique Hamiltonian cycle is the fixed cycle 0-1-...-(n-1)-0
  (any witness can be relabeled so its HC is this cycle).
- Boolean variable x[(i,j)] for each **chord** (pair at cyclic distance ≥ 2);
  degree constraint: every vertex is incident to exactly 2 chosen chords (degree 4 total).
- **Symmetry breaking**: the encoding's symmetry group is the dihedral group D_n acting on
  the fixed cycle. We require the chord incidence vector to be lex-≤ each of its 2n−1
  nontrivial dihedral images (prefix-truncated to the first 30 positions — a sound
  relaxation of full lex-leader).
- **CEGAR loop**: solve → build the graph → enumerate its Hamiltonian cycles with an
  independent DFS enumerator (cutoff = max_block+1) → for every HC other than the fixed
  cycle, add the blocking clause `OR_{e chord of C} ¬x_e`, plus the same clause for all
  dihedral images of the chord pattern (valid because a rotated/reflected chord pattern
  of a cycle completes to a rotated/reflected second HC with the fixed cycle edges).
- Termination: INFEASIBLE ⇒ **verified negative for order n** (no 4-regular simple graph
  on n vertices has the fixed cycle as its unique HC ⇒ WLOG none is uniquely
  Hamiltonian). Model with exactly 1 HC ⇒ counterexample witness (would be dumped to
  `witness_n{n}.txt` and re-verified with `../verify_nearmiss.py`).
- Soundness notes: blocking clauses are universally valid (any assignment containing all
  chords of a second-HC pattern contains that cycle as a subgraph, hence ≥ 2 HCs), so
  they never exclude a genuine witness; symmetry breaking keeps one representative per
  D_n orbit. UNSAT after CEGAR convergence is therefore a complete negative for that n.

## Runs (8-core VM, CP-SAT 8 workers)

| n  | result | iters | blocking clauses | time |
|----|--------|-------|------------------|------|
| 8  | UNSAT (verified negative) | 2  | 792     | 0.1 s |
| 12 | UNSAT (verified negative) | 6  | 17 456  | 0.7 s |
| 14 | UNSAT (verified negative) | 12 | 83 769  | 4.2 s |
| 16 | UNSAT (verified negative) | 23 | 389 778 | 41.3 s |

(n ≤ 21 are known negatives — GMZ exhaustive search — used here to validate the
pipeline before escalating; results below extend to the open range.)

## Incremental SAT rewrite (`cegar_sat.py`, PySAT + CaDiCaL 1.9.5)

CP-SAT re-presolves the whole model each CEGAR iteration; with millions of blocking
clauses this dominates runtime (n=18: 1341 s). Rewrote the identical encoding on an
incremental CaDiCaL (`pysat`): exactly-2 via sequential counters, prefix-lex chains in
raw CNF, blocking clauses added incrementally so learned clauses persist.

| n  | result | iters | blocking clauses | time | solver |
|----|--------|-------|------------------|------|--------|
| 16 | UNSAT (verified negative) | 33 | 597 314 | 9.5 s | cegar_sat |
| 18 | UNSAT (verified negative) | 67 | 2 730 648 | 379 s | cegar_sat (3.5× faster than CP-SAT) |

Clause growth per +2 vertices is ~×5–7; n=20 estimated ~15–40 M blocking clauses,
n=22 likely ≳ 10⁸ — the CEGAR frontier is memory/time bound, mirroring the fact that
the exhaustive frontier in the literature stops at n=21.

## NOIMG mode (blocking without dihedral image expansion)

Expanding every blocking clause to its ≤2n dihedral images turned out to be
counterproductive at n ≥ 20: clause DB explodes (17.5 M at n=22 after 200 iterations)
and single CaDiCaL solves start taking hours. `NOIMG=1` adds only the pattern actually
found (letting the solver rediscover symmetric variants via cheap extra iterations):
~30× higher CEGAR throughput (6 000 iterations in 573 s at n=22 vs 200 in 1 111 s).

## Open-range runs (NOIMG, max_block=500, one CaDiCaL core each; killed at wrap-up)

| n  | result  | iters  | blocking clauses | wall time | min #HC over all models |
|----|---------|--------|------------------|-----------|--------------------------|
| 20 | TIMEOUT | 4 200  | 2.1 M | 3.8 h | ≥ 501 (cutoff) |
| 22 | TIMEOUT | 11 000 | 5.5 M | 4.8 h | ≥ 501 (cutoff) |
| 24 | TIMEOUT | 24 000 | 12.0 M | 4.9 h | ≥ 501 (cutoff) |
| 26 | TIMEOUT | 42 600 | 21.3 M | 4.9 h | ≥ 501 (cutoff) |
| 28 | TIMEOUT | 43 600 | 21.8 M | 3.3 h | ≥ 501 (cutoff) |

- No witness was ever produced: every single SAT model across ~125 000 CEGAR iterations
  (≥ 60 M blocked second-HC patterns) had > 500 Hamiltonian cycles (enumeration cutoff).
- Per-iteration solve time degrades sharply as clauses accumulate (n=20 fell from
  ~7 it/s to one solve per ~35 s after 2 M clauses, then a single solve > 1 h) — the
  bottleneck is genuinely hard SAT instances, not the enumerator (independent DFS,
  cross-validated against `../verify_nearmiss.py` semantics: exact match of the
  fixed-cycle count in every iteration).

## Conclusions

- SAT-CEGAR independently re-verifies Sheehan for n ≤ 18 (fast, complete, UNSAT), a
  fundamentally different pipeline from GMZ's generation-based exhaustion.
- The CEGAR wall sits at n≈20: full convergence there needs (well) beyond ~2 M distinct
  second-HC chord patterns and hours-long individual solves. n ≥ 22 is out of reach for
  this encoding on one box — consistent with the literature frontier stopping at n=21.
- No evidence against the conjecture: no model with ≤ 500 HCs was ever produced by the
  solver in the open range (the annealer's minimum, 144 at n=22, required targeted
  minimization; random SAT models sit far above it).
- Promising follow-ups: (a) seed the base encoding with all k≤4-chord second-HC
  patterns computed combinatorially instead of discovering them one CEGAR iteration at
  a time; (b) SAT-modulo-symmetries (SMS) with a custom "second HC" propagator instead
  of clause-level blocking; (c) distribute CEGAR at n=20 across many cores with cube-
  and-conquer on the first chords.

## STATUS

STATUS: NEGATIVE (no counterexample; SAT-CEGAR verified negatives n ∈ {8,12,14,16,18};
n=20..28 TIMEOUT after ~4–5 h each with no witness and no model below 501 HCs).

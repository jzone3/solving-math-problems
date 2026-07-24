# Woodall P03 — fusion1

## Environment

- Branch: `runs/P03-fusion1`
- Python: Python 3.10.12
- PySAT: `python-sat 1.9.dev7` (Glucose3 smoke test passed)
- NetworkX: `3.4.2`
- PyPy: PyPy 7.3.9 / Python 3.8.13
- nauty: 2.7r3; binaries are `/usr/bin/nauty-geng` and
  `/usr/bin/nauty-directg` (the unprefixed `geng`/`directg` names are absent)

## Port

The v5 phase-2 scripts were copied from `origin/runs/P03-v5`:
`orient_exhaust.py`, `prep_graphs.py`, `enum_pypy.py`, `harness.py`,
`crosscheck.py`, `sat_check.py`, and the supporting search/exhaustion and test
scripts.

## Checker validations

All validations below passed on 2026-07-24:

- `test_harness.py`: all sanity tests passed.
- `crosscheck.py`: independent brute-force checker agreed with the PySAT
  harness on 40/40 random tau=3 instances.
- `test_exact_pack.py`: pure-Python exact packer agreed with PySAT on 300
  n=14 candidates; random-DAG cross-check agreed on 21 instances (0
  non-packing instances in that sample).
- `test_cegar.py`: CEGAR packer agreed with pure exact backtracking on 400/400
  n=14 candidates and with PySAT on 60/60 random tau>=3 DAGs.
- `test_dicut_filter.py`: reduced-dicut filter agreed with brute force on
  500/500 candidates.

The fixture files used by the v5 tests were regenerated in `/tmp` from the
tracked v5 `kept14.jsonl`; they are not part of the repository.

## n=16 exhaustion

The fresh nauty generation produced 4,060 connected cubic graphs on 16
vertices. `prep_graphs.py` retained 2,595 non-planar, 3-edge-connected
graphs, dropping 681 planar and 784 not-3-edge-connected graphs. Eight PyPy
shards were initially run over these 2,595 retained graphs:

```
0:325  325:650  650:975  975:1300
1300:1625  1625:1950  1950:2273  2273:2595
```

Each shard uses `enum_pypy.py` with profile, DAG, source-sink, CEGAR exact
packing, reduced-dicut, and exact backtracking filters. Candidate output is
written to a separate `.cand.jsonl` file and stderr progress to a `.log`
file. At the latest checkpoint (about 12 minutes wall time), seven shards had
completed their first graph and one shard had completed two. Per-graph totals
ranged from 5.10M to 8.23M DAG leaves, 4.48M to 6.72M profile leaves, and
1.12M to 2.60M CEGAR packing checks; all reported zero candidates. One shard
was still processing its first graph. All eight candidate files remained
empty. This full-cell run was intentionally stopped after partial coverage:
approximately one graph per shard (two in one shard), all completed graphs
packed every checked orientation, and no candidate was emitted. The estimated
runtime for the full cell was about 38 hours per shard, so this is not a full
n=16 closure.

## Strategy pivot

The all-cubic n=16 run was stopped in favor of structurally distinct families.
Family B below is an exhaustive high-girth (girth at least 5) subfamily, not
the full cubic cell. Any negative result is scoped only to that high-girth
subfamily.

## Family B: high-girth cubic subfamily

The required `nauty-geng -c -t -f -d3 -D3 n` command generated 49 graphs at
n=16 and 455 graphs at n=18. The preparation filter retained all of them:
none were planar or below 3-edge-connectivity. Eight n=16 PyPy shards were
launched over ranges `0:7, 7:13, 13:19, 19:25, 25:31, 31:37, 37:43,
43:49`. Their candidate files are empty at launch/checkpoint; the exhaustive
orientation and exact CEGAR checks were then running. The n=16 high-girth
run is now **COMPLETE**. Across all 49 graphs and all orientation profiles,
the machine totals were 389,188,756 DAG leaves, 320,659,024
profile-matching leaves, 256,410,440 source-sink skips, and 64,248,584 exact
CEGAR packing checks. Every CEGAR check packed; there were **zero
candidates**, and all eight candidate files are empty. The longest shard
wall time was 2,487 seconds. This is an exhaustive closure of the
girth-at-least-5 n=16 subfamily only.

The n=18 input was generated and prepared (455 graphs retained), but was not
launched after n=16 completion because its expected runtime exceeded the
remaining session budget. It is now running in eight background shards over
the 455 prepared graphs; logs and candidate files are checkpointed by range.

## Tau=4 n=10 reduced-cell exhaustion

`nauty-geng -c -d3 -D4 10` generated 4,414 connected graphs. Filtering to
exact degree sequence `[3,3,3,3,3,3,4,4,4,4]` gave 1,404 graphs, of which
426 were planar and 978 non-planar. The corrected exhaustive run over all
978 non-planar graphs enumerated 25,345,994 acyclic orientations and 6,092
profile-matching orientations. Of those, 6,076 were source-sink-connected
and 16 had tau=3; **zero had tau=4**, so zero exact k=4 packing instances
were required and zero candidates were emitted. This is an exhaustive
closure of the reduced profile cell at n=10, with the stronger conclusion
that no orientation in the generated non-planar graph family reaches tau=4.

An initial implementation omitted the explicit tau=4 check before emitting
diagnostics; it emitted 16 false candidates that all independently verified
with the PySAT harness as tau=3 and non-packing for k=4. Those outputs are
retained as debugging artifacts; they are not counterexamples. The corrected
rerun has empty candidate files. The new size-4 reduced-dicut filter was
cross-validated against direct closed-set enumeration on 300/300 instances.

## Standalone verifier

Added `solutions/P03/verify.py`, which has no third-party dependencies. It
passed 80 exact-vs-brute checks for k=3, 80 for k=4, and independently
reconstructed two representative n=16 high-girth orientations, confirming
tau=3 and exact 3-dijoin packing. It prints `PASS` only after all checks.

This experiment is explicitly scoped to connected cubic graphs of girth at
least 5, after the non-planar and 3-edge-connected filters. It is not a
closure of the full n=16 cubic cell.

## Family A: tau=4 reduced shape

For sources `s`, sinks `t`, type-A internal vertices `(in,out)=(1,2)` and
type-B vertices `(2,1)`, stub balance gives `a-b=4(t-s)`. The two
rho(4) bounds give `a+3b >= 12` and `3a+b >= 12`. With at least two sources
and sinks, the smallest profile is `(s,t,a,b)=(2,2,3,3)`, hence n=10 and
17 arcs. The next profiles can be derived by `family_a.role_profiles`.

The derivation was computationally checked: 30 generated instances of the
claimed `(2,2,3,3)` shape with `tau=4` all had `rho(4,D)>=3` and
`rho(4,reverse(D))>=3`. The k=4 exact partition checker was independently
validated by `test_k4.py`: **300/300** small random DAG instances agreed
between `harness.has_k_disjoint_dijoins(...,4)` and brute-force 4-coloring.

## Family C: weighted search

The v4 weighted machinery (`weighted.py` plus its self-contained
`woodall.py`) has been ported. It uses PuLP/CBC lazy separation for weighted
packing. The v4 tau_w=2 smoke search ran 58,462 trials with no gap. A
tau_w=3 search ran 23,630 trials, encountered 3,154 instances with
tau_w=3, and found no `nu_w < 3` gap; every failed 3-packing check was also
required to pass the exact 2-packing feasibility check before it could be
reported.

Family A targeted runs have now covered:

- profile `(2,2,4,4)`, n=12: 10 out-of-safe-class instances, all packed;
- profile `(3,3,3,3)`, n=12: 889 out-of-safe-class instances, all packed.

The exact k=4 checker was used on every listed instance. The smallest
profile `(2,2,3,3)` was computationally tested separately: 4,746/5,000
generated instances had tau=4, all 4,746 were source-sink-connected (so no
out-of-safe-class instances occurred), and all satisfied both rho bounds.

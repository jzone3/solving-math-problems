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

The n=18 input was generated and prepared (455 graphs retained). It is now
running in eight background shards over the 455 prepared graphs; logs and
candidate files are checkpointed by range.

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
with the PySAT harness as tau=3 and non-packing for k=4. They are recorded in
`tau4_n10_prefix_false_positives.jsonl` with `tau=3` and
`real_counterexample=false`; they are not counterexamples. The corrected
rerun has empty candidate files. The new size-4 reduced-dicut filter was
cross-validated against direct closed-set enumeration on 300/300 instances.

## Standalone verifier

Added `solutions/P03/verify.py`, which has no third-party dependencies. It
passed 80 exact-vs-brute checks for k=3, 80 for k=4, and independently
reconstructed two representative n=16 high-girth orientations, confirming
tau=3 and exact 3-dijoin packing. It prints `PASS` only after all checks.

The structured broader search used four 900-second workers with layered
generators, degree-preserving rewires, and four-step annealing. It generated
2,810 instances, certified 845 out-of-safe-class tau=4 instances, and exact
checked all 845 as packed (slowest exact check 0.386 seconds). No near-miss
or non-packing instance occurred. A second throughput batch was stopped
before producing a completed aggregate log and is not counted.

The n=18 high-girth search was launched across all eight prepared ranges.
After approximately 36 minutes, no shard had completed its first graph and
all candidate files remained empty; the shards were stopped to avoid
unbounded resource use. Thus the recorded n=18 coverage is **0/455
completed**, not an exhaustion result.

## Validated C engine and n=12 tau=4 cells

`engine.c` is a standalone C orientation/dicut/partition engine. It reads
underlying graph edge-list records, enumerates acyclic orientations with
role-profile pruning, sweeps all vertex masks for dicuts and tau, applies
the source-sink, rho, and reduced size-k-dicut filters, and solves the
rainbow partition problem by exact backtracking.

Before using it for enumeration, its `check3` and `check4` modes were
compared against the Python/PySAT harness on 300 random DAGs for each k.
For every one of the 600 instances, tau, minimal-dicut count, and
pack/no-pack agreed exactly:

```text
PASS C validation k 3: 300/300
PASS C validation k 4: 300/300
```

For the n=12 profile `(2,2,4,4)`, nauty generated 327,041 connected
degree-3/4 graphs; 39,071 had the required degree sequence, 7,490 of
those were planar, and 31,581 non-planar graphs were exhausted. The C
engine enumerated 6,642,846,058 orientations and 744,680 profile
orientations. Of these, 737,962 were source-sink-connected, 5,572 had
tau different from 4, and the remaining 1,146 failed one of the two
rho>=3 filters. Thus **0 out-of-safe-class tau=4 orientations** reached
the exact packing check; candidate count was zero.

For the n=12 profile `(3,3,3,3)`, the correct underlying degree sequence
has six degree-4 and six degree-3 vertices (not four degree-4 vertices).
Among the same nauty output, 122,406 graphs had this degree sequence,
12,190 were planar, and 110,216 non-planar graphs were exhausted. The C
engine enumerated 32,849,953,100 orientations and 144,496 profile
orientations. Of these, 114,112 were source-sink-connected, 1,404 had
tau different from 4, and 9,416 failed the rho filters. The remaining
19,564 out-of-safe-class tau=4 orientations were all exactly packed:
**19,564/19,564 packed, 0 candidates**. This is exhaustive for the
retained non-planar graph list and profile.

The n=18 C rerun was launched after correcting the cubic role-profile
test. It was stopped after approximately eight minutes per shard while
the first graph in each range was still running; no graph completed and
all candidate files were empty. Recorded coverage is therefore **0/455**.

This experiment is explicitly scoped to connected cubic graphs of girth at
least 5, after the non-planar and 3-edge-connected filters. It is not a
closure of the full n=16 cubic cell.

## Fast closed-set dicut engine

The original C engine tested every nonempty proper vertex subset when
enumerating dicuts. `engine.c` now defaults to predecessor-closed
order-ideal recursion over a topological order of the DAG. An inclusion
branch is taken only when every in-neighbour of the vertex is already in
the current set; each nonempty proper ideal contributes its out-cut. The
previous `2^n` sweep remains available with the extra `old` command-line
argument for regression testing.

The implementation has a hard safety cap of 1,000,000 ideals and
`MAXCUT` collected cuts. If either cap is reached, the orientation is
marked deferred and is not classified as packed or non-packed; production
logs report the deferred count for exact PySAT follow-up. No truncated
minimal-dicut set is used for a packing decision.

Cross-validation results before production use:

```text
PASS C fast-vs-old 20,000/20,000 exact tau/minimal-dicut-set/pack
PASS C fast-vs-PySAT/reference k=3 1,000/1,000
PASS C fast-vs-PySAT/reference k=4 1,000/1,000
```

The cross-validation compared the full minimal-dicut mask set, not only
its cardinality. On a representative n=16 high-girth graph orientation,
1,000 repeated check-mode records took 0.132 seconds with closed-set
enumeration versus 0.467 seconds with the old subset sweep, a measured
3.54x per-record speedup after amortizing process startup. The earlier
measurement included a redundant second cut enumeration, which has also
been removed from the production leaf path. The exact speedup depends on
the orientation's ideal count.

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

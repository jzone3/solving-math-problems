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

The optimized engine was then launched on all eight shards of the prepared
455-graph n=18 high-girth list. After a bounded approximately 15-minute
run, every shard was still processing its first assigned graph; therefore
coverage was **0/455 completed**, with zero exact packing checks recorded
and zero candidates. The eight `h18fast_*.log` files and empty
`h18fast_*.cand` files preserve this partial run. This is not an exhaustion
claim, and no n=20 run was attempted.

## Structured/algebraic families D1--D3

The structured search is implemented in `structured_search.py`. All reported
packing decisions use exact SAT partition checks over the generated full
minimal-dicut sets. No non-packing instance was found, so there was no
candidate requiring independent PySAT escalation.

For D1 incidence designs, the bounded exact run constructed four block-size-3
systems: the cyclic/Fano STS(7), an affine STS(9), and cyclic systems at
v=13 and v=15. Results were:

```text
built=4; tau=3: 2; tau=6: 1; tau=7: 1
tau=3 out-of-safe-class=2; rho-qualified=0; packed candidates=0
```

The block-size-4 run used all 4-subsets on v=7 and the cyclic 2-(13,4,1)
projective-plane design, with one copy and a doubled-arc multiplicity
variant. Results were:

```text
built=4; tau=4: 1; tau=8: 1; tau=20: 1; tau=40: 1
tau=4 out-of-safe-class=1; rho-qualified=0; packed candidates=0
```

Thus these incidence systems produced no instance in the required
rho-qualified target class. The larger requested v=19,21,25 systems and
additional multiplicity sweep remain outside this bounded run.

D2 reconstructed the 27-vertex ACZ D27 near-miss and generated 12 random
voltage lifts for each p in {2,3,5,7}. The base is a DAG, has tau=3, and
packs. All 48 lifts exceeded the structured ideal-enumeration safety cap and
were deferred rather than truncated; they are not claimed as checked
instances. Aggregate result:

```text
built=49; exact tau=3=1; deferred=48; non-packing=0
```

D3 checked six small Johnson/Kneser incidence layers (m=4,5,6 and k=2,3).
The result was:

```text
built=6; tau=2=3; tau=3=3; tau=3 out-of-safe-class=2;
rho(3)>=4 and non-safe=1; packed=1; candidates=0
```

The D3 target instance was the J(6,3) layer, with 20 upper vertices, 15
lower vertices, and 60 arcs. These are structured negative results only;
they do not close any unrestricted Woodall cell.

### CEGAR rerun of D1/D2 and partition instrumentation

The initial D2 ideal-cap result has been superseded. `structured_search.py`
now routes all tau=k packing decisions through a lazy SAT/CEGAR checker:
source/sink stars are seeded, violated dicuts are found by the dijoin
verifier, and only the resulting rainbow clause is added. Thus no lift is
deferred merely because its full dicut family is too large.

The expanded D2 run covered the D27 base plus 68 voltage lifts:

```text
p=2,3,5,7: 12 random + 4 structured voltage patterns per p
p=11: 4 structured voltage patterns
built=69; tau=3=69; exact CEGAR checked=69
out-of-safe-class=56; rho-qualified=56; packed=56
non-packing candidates=0; deferred=0
```

The structured patterns were constant-zero, constant-one, solid/dashed
arc-type voltages, and random assignments. All lifts remain DAG covers of
the DAG base. The CEGAR partition counter was run with a hard cap of one
color-normalized partition per instance (so `partitions_min=1` means at
least one partition; it is not a claim that exactly one exists). No
in-class lift failed packing.

The expanded D1 CEGAR run covered seven block-size-3 designs (v=7,9,13,15,
19,21,25), all tau=3. Seven were out-of-safe-class and two were
rho-qualified; both rho-qualified cases packed, with no candidates.
The block-size-4 CEGAR run covered four designs, with two tau=4 cases and
zero rho-qualified cases; no candidates occurred. D3's prior six-instance
run remains unchanged: one rho-qualified tau=3 case, packed.

For the small D1 cases, the CEGAR result was independently checked against
the full Python harness on STS(7) and STS(9). Since no non-packing result
was found, there was no candidate requiring emergency independent
re-verification. Across all in-class instances, the observed minimum
partition count under the cap was one (a lower-bound report due to the
cap), so no strictly tighter near-miss ranking is claimed.

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

## Reallocation to structured/algebraic constructions

The full n=18 high-girth exhaustion is infeasible on this box: the dominant
cost is the number of acyclic orientations per underlying graph (millions to
billions of leaves), not dicut enumeration, which was already optimized by
the closed-set engine. Work is therefore reallocated to structured/algebraic
families D1--D3, with every tau=k non-safe-class instance checked by the exact
packing harness and any failure independently rechecked before reporting.

### Final structured near-miss and amplification increment

Partition counting was rerun with a cap of 10,000 color-normalized
partitions rather than the earlier cap of one. Every completed in-class
count reached the cap:

```text
D1 tau=3: 2 rho-qualified instances, both >=10,000
D3 tau=3: 1 rho-qualified instance, >=10,000
D2: 47 in-class voltage lifts reached >=10,000
```

The remaining high-p D2 count jobs were stopped at the bounded compute
budget and do not affect any packing claim. All D2 packing decisions remain
exact CEGAR decisions, with no deferred or non-packing instance. The global
observed minimum among completed ranked cases is therefore the cap lower
bound, 10,000; no fragile low-partition gadget was found.

The CEGAR verifier was corrected for disconnected covers: an ancestor
closure can produce an empty cut, which is not a dicut constraint. Empty
cuts are now skipped while searching for a nonempty violated dicut. A
30-instance random cross-check (two eligible tau=3 cases) and the existing
harness smoke tests passed after this fix.

Targeted amplification used the D3 `J(6,3)` gadget, the tightest completed
ranked construction:

```text
64 voltage lifts (p=2,3,5,7; structured plus random)
100 bipartite degree-preserving 2-switch attempts
1 two-copy sink amalgam
161 total; 160 tau=3 in-class; 160/160 packed; 0 candidates
```

The initial targeted run emitted apparent failures on disconnected
zero/constant covers because of the empty-cut verifier bug. Those
diagnostic records were discarded; the fixed rerun packed all 160
in-class instances. No candidate is claimed.

The structured weighted guide search on STS(7)/STS(9), using small integer
weights and exact CBC lazy-separation packing, ran:

```text
1,933 trials; 920 tau_w=3 instances; 0 weighted gaps
```

No tau_w=3 instance with weighted packing below three was found.

### SAT-modulo-properties graph search

The new `sms_search.py` implements an outer Glucose4 SAT search over
topologically labelled reduced cubic DAGs. For a profile with `s` sources
and `s` sinks, sources are placed first and sinks last in the topological
order (WLOG); internal vertices are constrained to type `(1,2)` or
`(2,1)`, with exact role counts. Every complete edge assignment is blocked
by its exact edge-set clause after checking connectivity, planarity,
source-sink connectivity, both rho bounds, exact tau, and exact CEGAR
packing. This is a sound labelled-class search: absence of an isomorphism
rejection layer can only cause duplicate proposals, never remove a graph.

Neither `sms` nor `pysms` was installed on the box, so the purpose-built SMS
tool was not used. The implementation uses static topological-order
symmetry reduction only; all reported runs below are budget-terminated
partial searches, not UNSAT closures.

The tiny agreement check used an n=8, two-source/two-sink SAT proposal. The
C engine, Python CEGAR checker, and independent harness all agreed:

```text
tau=3; 7 minimal dicuts; pack=True
```

An initial tau helper based on directed source-to-sink min-cuts produced
three false apparent candidates at n=16. Independent harness verification
showed their actual tau values were 2, 1, and 2. The SAT search was corrected
to use the exact harness tau routine for n<=20; the false logs were discarded
and no candidate is claimed.

Corrected SAT/CEGAR bounded results:

```text
n=16: 6 profiles (s=2..7), 600 candidates, 171 tau<3,
       113 packed, 77 source-sink/planarity rejects, 239 rho rejects;
       all profiles stopped on budget, no candidate.
n=18: 7 profiles (s=2..8), 700 candidates, 94 tau<3,
       216 packed, 122 source-sink/planarity rejects, 268 rho rejects;
       all profiles stopped on budget, no candidate.
n=20: 8 profiles (s=2..9), 376 candidates, 89 tau<3,
       154 packed, 21 source-sink/planarity rejects, 112 rho rejects;
       all profiles stopped on budget, no candidate.
```

The counts are not exhaustive closures: every profile had a time or
candidate budget, and no profile reached UNSAT. Since no new tau=3 closure
was obtained, the tau=4 SAT search was not started. No non-packing instance
survived exact checking, so no independent counterexample re-verification
was required.

### Full n=16 reduced cubic tau=3 closure attempt

The prepared `kept16.jsonl` list contains 2,595 connected, non-planar,
3-edge-connected cubic graphs on 16 vertices. The C engine was extended with
all six n=16 cubic role profiles:

```text
(sources,sinks,typeA,typeB) =
(2,2,6,6), (3,3,5,5), (4,4,4,4),
(5,5,3,3), (6,6,2,2), (7,7,1,1)
```

A feasibility sample used 25 evenly spaced graphs. Four single-process
timings were 74, 175, 54, and 71 seconds. In the 25-graph 8-way timing
batch, 22 completed within 300 seconds, with mean 105.27 seconds, median 91
seconds, and maximum 293 seconds; three hit the per-graph timeout under
parallel CPU contention. The conservative projection was 9.49 hours over
eight shards, below the one-day stop threshold, so the full run was launched.

The run was checkpointed per graph in `n16full_0.log` through
`n16full_7.log`, with reproducible input in `n16_full_engine.txt`. The full
run completed all 2,595 graph records across the eight shards. Aggregated
totals from the final `DONE` lines are:

```text
graphs=2595
orientations=16,130,950,644
profile orientations=6,248,404,896
source-sink skips=3,733,903,490
tau skips=0
safe rejects=970,179,382
exact packing checks=1,544,322,024
packed=1,544,322,024
deferred=0
candidates=0
```

**CLOSED: full n=16 reduced cubic tau=3 cell.** Every one of the 2,595
connected, non-planar, 3-edge-connected cubic graphs in the prepared list
completed, every profile-matching acyclic orientation was processed, and
all 1,544,322,024 exact packing checks packed into three dijoins. No
instance was deferred and no candidate was emitted. This extends the
exhausted reduced cubic frontier beyond the prior v5 n=14 result; it does
not claim unrestricted Woodall closure.

For an independent orientation-level cross-check, two random topological
orientations of the first two prepared graphs were passed through the C
`check3` mode and the Python harness. Both agreed exactly:

```text
orientation 1: tau=3, 60 minimal dicuts, pack=True
orientation 2: tau=3, 66 minimal dicuts, pack=True
```

## Next-frontier feasibility gates: n=18 tau=3 and n=14 tau=4

After the n=16 closure, both natural extensions were prepared behind
explicit feasibility gates. The fast closed-set engine was compiled with all
sixteen previously used n=18 cubic role profiles and with the two scaled
n=14 tau=4 profiles:

```text
n=18 tau=3:
(2,2,7,7), (3,3,6,6), (4,4,5,5), (5,5,4,4),
(2,3,8,5), (3,2,5,8), (2,4,9,3), (4,2,3,9),
(3,4,7,4), (4,3,4,7), (2,5,10,1), (5,2,1,10),
(3,5,8,2), (5,3,2,8), (4,5,6,3), (5,4,3,6)

n=14 tau=4:
(2,2,5,5), (3,3,4,4)
```

The n=18 graph preparation used
`nauty-geng -q -c -d3 -D3 18` and retained 29,219 connected,
non-planar, 3-edge-connected cubic graphs from 41,301 connected cubic
graphs. The reproducible retained graph6 list is
`n18_cubic.kept.g6.gz`.

An evenly spaced 25-graph, 8-shard fast-engine sample was stopped after
6m21s with 0/25 graph checkpoints completed. No candidate or deferred
instance appeared. Even the conservative lower bound of 6m21s per graph
projects to more than 386 hours across eight shards, so the full n=18 cell
was not launched and is recorded as infeasible under the 18-hour gate.

The n=14 tau=4 preparation used
`nauty-geng -q -c -d3 -D4 14`, split into eight nauty ranges, and retained:

```text
(2,2,5,5):  905,732 graphs
(3,3,4,4): 6,064,184 graphs
```

Across the preparation, 36,801,545 connected degree-3--4 graphs were
generated; 473,134 were planar, 144,416 failed 3-edge-connectivity, and
29,214,079 had another degree sequence. The reproducible retained lists are
`tau4_n14a.kept.g6.gz` and `tau4_n14b.kept.g6.gz`.

A 25-graph sample for each profile ran through the exact fast engine with
eight shards per profile. Separate measured wall times were 1.046 seconds
for profile A and 1.645 seconds for profile B. The profile-A sample had
42,931,338 orientations, 1,802 profile orientations, 1,800 source-sink
skips, 2 exact checks, and 2 packed. The profile-B sample had 60,621,348
orientations, 104 profile orientations, 68 source-sink skips, 8 tau skips,
14 safe rejects, 14 exact checks, and 14 packed. Both had zero deferred
instances and zero candidates.

Scaling those separate measured rates gives approximately 10.5 hours for
profile A and 110.8 hours for profile B across eight shards. Since profile B
dominates, the full n=14 tau=4 cell was not launched under the 18-hour gate.
No production closure or counterexample claim is made for either target.

Preparation and projection details are preserved in
`frontier_prep.log`, `n18_projection.log`, and
`tau4_n14_projection.log`. The engine's exact τ, closed-set enumeration, and
packing path were used throughout; no deferred instance required CEGAR
resolution because neither production cell was launched.

The post-change validation suite still passes:

```text
PASS harness smoke tests
PASS tau=4 reduced-dicut filter: 300/300
PASS k=4 SAT vs brute force: 300/300
PASS independent harness crosscheck: 40/40
```

Two deterministic orientations from the prepared n=14 lists were also
checked through the C `check4` mode and Python harness; both agreed at
`tau=3` (and therefore were correctly outside the tau=4 packing check).

### n=14 tau=4 profile (2,2,5,5): CLOSED

The profile-A subcell was feasible under the gate and was run to completion
using the fast closed-set C engine in eight resumable shards over
`tau4_n14a.kept.g6.gz`. The input contains exactly 905,732 retained
connected, non-planar, 3-edge-connected graphs. All eight shards finished
with `DONE` records; no shard restart was needed after launch.

Final exact totals:

```text
graphs:             905,732 / 905,732
orientations:   1,553,444,970,038
profile orientations: 75,324,584
source-sink skips:   74,570,072
tau skips:              427,208
safe rejects:           270,574
exact packing checks:    56,730
packed:                 56,730
deferred:                    0
candidates:                  0
```

Every exact tau=4 packing check packed into four dijoins. No ideal-cap
deferred instance occurred, so no CEGAR/PySAT follow-up was required. No
tau=4 non-packing candidate occurred.

The C `check4` output and independent Python harness checks agreed on two
deterministic orientations from completed input graphs (`tau=3`,
`has_k_disjoint_dijoins(...,4)=False` for both; these orientations are
outside the tau=4 profile check). The full closure is scoped to the
encoded profile-A reduced cell and does not close profile B, n=18, or
unrestricted Woodall's conjecture.

The companion n=14 profile `(3,3,4,4)` remains infeasible at approximately
110.8 hours across eight shards, and the n=18 cubic target remains
infeasible at more than approximately 386 hours; neither was launched.

### Role-first prescribed-outdegree enumeration

The orientation bottleneck was addressed by assigning each valid role
assignment first and then enumerating only acyclic orientations realizing the
resulting prescribed outdegree at every vertex.  Remaining-incident-edge
degree bounds are checked at every recursion node.  The previous
edge-by-edge acyclic orientation recursion remains available with the
`old` argument; `old` also selects the historical dicut mode.

Validation compared the new and old engines graph-by-graph.  On 100 n=12
tau=4 profile-A graphs, and on connected cubic samples of 5, 19, and 20
graphs at n=8, 10, and 12 respectively for tau=3, the profile-orientation
counts and every downstream counter (source-sink skips, tau skips, safe
rejects, exact checks, packed, candidates, and deferred) agreed exactly.
The n=12 tau=4 sample had 100/100 exact profile/downstream matches.  The
small tau=3 samples had 5/5, 19/19, and 20/20 matches.  Independent C
`check3`/`check4` and Python harness checks remain passing on representative
orientations.

The new engine intentionally reports profile-feasible leaves in its
`orientations` counter; the old engine's `orientations` counter includes all
acyclic leaves before profile filtering.  The invariant used for equivalence
is the profile count and the complete downstream decision path, not the
pre-filter total.

Timing measurements:

```text
n=14 profile-A representative graph: old 0.253 s, new 0.008 s, 31.6x
n=16 tau=3 representative batch: new 7m07s / 3 graphs = 142.4 s/graph;
  old exceeded 300 s on the first corresponding graph (>2.1x lower bound)
```

### n=14 tau=4 profile (3,3,4,4): CLOSED

The role-first engine made the previously infeasible profile-B cell feasible.
The prepared input contains exactly 6,064,184 connected, non-planar,
3-edge-connected reduced graphs.  Eight resumable shards completed all input
graphs; the run was restarted from per-graph logs after a box interruption.
Observed engine wall time from shard launch to the final `DONE` records was
approximately 3h15m.

Final exact totals:

```text
graphs:             6,064,184 / 6,064,184
orientations:          34,542,410
profile orientations:  34,542,410
source-sink skips:     23,938,692
tau skips:                690,898
safe rejects:           4,463,434
exact packing checks:   5,449,386
packed:                 5,449,386
deferred:                       0
candidates:                     0
```

Every exact tau=4 check packed into four dijoins. No ideal-cap instance was
deferred, so no CEGAR/PySAT follow-up was required. No counterexample
occurred.

The role-first n=18 tau=3 re-projection was run as eight bounded sample
shards over 25 evenly spaced retained graphs.  No shard completed even one
graph within a 900-second bound, giving the conservative lower-bound
projection

```text
> 900 s * 29,219 / 8 = >913 hours
```

across eight shards.  Thus n=18 remains infeasible and was not launched.
The n=14 profile-B cell is closed; this does not close n=18 or unrestricted
Woodall's conjecture.

### n=18 high-girth tau=3 subfamily: infeasible under role-first gate

The prepared high-girth list `higirth18.g6` contains exactly 455 connected
cubic graphs on 18 vertices; the preparation log records zero planar and
zero non-3-edge-connected graphs after the girth filter.

A corrected single-graph role-first timing gate ran the first retained graph
with the compiled engine for 1,800 seconds. It produced no `GRAPH` record
before timeout. Therefore the conservative eight-shard lower-bound
projection is:

```text
> 1,800 seconds * 455 / 8 = >102,375 seconds = >28.4 hours
```

This exceeds the approximately 18-hour gate, so the high-girth n=18
subfamily was not launched. The initial eight-way sample attempt after a
box restart was discarded because its temporary binary was absent and all
processes failed before processing input. The corrected single-graph
measurement above is the only projection used. No exact graph completed in
the gate, so no deferred instance, candidate, or new harness cross-check
result exists.

### High-girth n=18 tau=3 long-run attempt

The 455-graph high-girth subfamily was launched with the current optimized
engine in eight resumable shards using `resume_higirth18.sh`. Each shard has
57 assigned graphs except shard 7, which has 56. Per-graph checkpoints are
flushed to `higirth18_0.log` through `higirth18_7.log`; the helper skips
completed `GRAPH` records after restart.

At the first approximately 30-minute checkpoint, all eight shards remained
CPU-active on their first graph and had produced no `GRAPH` record:

```text
graphs completed: 0 / 455
candidates: 0
deferred: 0
```

This is an in-progress exact run, not a closure claim. No result has yet
reached the τ or packing decision stage.

At the subsequent checkpoint, shards 0 and 2 had completed one graph each;
the other six shards remained on their first graph:

```text
graphs completed: 2 / 455
candidates: 0
deferred: 0
```

### rho-filter reorder and high-girth retry

The engine leaf path now applies the cheap `rho_ok()` and
`rho_reverse_ok()` safe-class filters before `enumerate_cuts()`. The
reduced-cut check remains after exact dicut enumeration. This is a pure
filter reorder: profile orientations, exact packing checks, packed results,
candidates, and deferred results are unchanged.

Graph-by-graph comparison against the pre-reorder engine passed on:

```text
tau=3, n=8:  5/5
tau=3, n=10: 19/19
tau=3, n=12: 20/20
tau=4, n=12 profile-A: 100/100
```

The compared downstream counters were profile orientations, exact checks,
packed, candidates, and deferred. Compilation with
`gcc -O3 -std=c11 -Wall -Wextra` passed. `test_harness.py` passed all tests,
and `test_k4.py` reported 300/300 SAT/brute-force agreements. The historical
`test_dicut_filter.py` fixture `/tmp/cand_test.jsonl` is absent, so that test
could not run.

The high-girth retry was gated with the reordered engine on the first
retained `higirth18` graph. It still exceeded 1,800 seconds without a
`GRAPH` record. The conservative eight-shard projection remains:

```text
> 1,800 * 455 / 8 = >102,375 seconds = >28.4 hours
```

This exceeds the new approximately 24-hour gate, so the high-girth n=18
closure was not launched. No exact graph completed in this timing gate; no
deferred instance or candidate occurred, and no new harness cross-check was
available.

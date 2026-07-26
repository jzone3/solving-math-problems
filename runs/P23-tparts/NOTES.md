# P23 translated-Parts universes — stage 1

Branch: `runs/P23-tparts`.  This stage reconstructs the finite two-half
universes only; it does not perform a constructive SAT search or minimisation.

## What was built

`univ.py` rebuilds

```
A(rA) ∪ (T + ω·A(rB)),    ω = (7 + i√15)/8
```

in exact arithmetic.  The lattice pool is generated from scratch as the
orbit-closed legacy fusion1 pool `⊕^3 H²` (2839 integer lattice points at
radius 2), then each half is clipped in the positive physical embedding and
unioned with the recovered `L374` half from `decomp509.pkl`.  This is the pool
that fed fusion1's E43–E45 radius ladder; the `--pool-layers 4` option also
reconstructs the corrected Parts pool (9259 points at radius 2).

Coordinates in the two rotated/translated halves use `MField((3,5,11))`.
Every edge is found with a floating-point spatial prefilter and confirmed by
the exact field equation `dx² + dy² = 1`.  Pickles contain points, exact edge
indices, exclusive `AA`/`BB`/`cross` edge labels, and build metadata.

Translations are encoded from the published lattice decompositions:

```
T63: 12a=(-5,1,7,-1), 12b=(2,0,0,-2)
T65: 12a=(0,0,4,0),   12b=(6,0,-6,0)
T = a + ω b
```

Copied support files have one-line provenance comments:
`lattice.py`, `pools.py`, and `mfield.py` come from
`origin/runs/P23-parts-gadgets`; `decomp509.pkl` comes from
`origin/runs/P23-parts-method`.

## Reproduction and results

Command form:

```bash
python3 univ.py --translation 65 --rA 1.6 --rB 1.3 \
  --cache cache_t65_16_13.pkl
```

The reconstructed legacy-pool counts were:

| translation | radii | vertices | exact edges | AA / BB / cross | build |
|---|---:|---:|---:|---:|---:|
| T=0 | 2.0 / 2.0 | 4043 | 28506 | 14220 / 14220 / 66 | 19.7 s |
| T63 | 2.0 / 2.0 | 4043 | 28457 | 14220 / 14220 / 77 | 20.5 s |
| T65 | 2.0 / 2.0 | 4043 | 28506 | 14220 / 14220 / 66 | 19.7 s |
| T63 | 1.6 / 1.6 | 3069 | 19319 | 9654 / 9654 / 65 | 12.4 s |
| T65 | 1.6 / 1.6 | 3069 | 19326 | 9654 / 9654 / 71 | 12.7 s |
| T65 | 1.5 / 1.5 | 2829 | 17160 | 8572 / 8572 / 66 | 10.5 s |
| T65 | 1.6 / 1.3 | 2788 | 16837 | 9654 / 7168 / 64 | 10.2 s |
| T65 | 1.3 / 1.3 | 2507 | 14346 | 7168 / 7168 / 53 | 8.3 s |

The expected E43–E45 published counts were 4033/28422 for T=0,
2917/17740 for T65 at 1.6/1.6, and 2581/14796 for T65 at 1.6/1.3.
The reconstruction is therefore close in the control but does **not** match
the published universe: it has +10, +152, and +207 vertices respectively.
The corresponding edge counts are also higher by 84, 1586, and 2041.

This is not hidden by SAT: the three reconstructed cases were independently
encoded as ordinary 4-colouring CNFs and kissat returned UNSAT:

* T=0, 4043 vertices / 28506 edges: 69.6 s
* T65, 3069 vertices / 19326 edges: 52.6 s
* T65, 2788 vertices / 16837 edges: 73.2 s

No DRAT proof was requested for this stage.  The discrepancy is recorded
rather than repaired by changing a clip radius or deleting points.  The
likely remaining historical difference is the exact legacy `w4d.pkl` point
set used by fusion1: that artifact and the lost `w4d.pkl`/`tscan2.pkl` inputs
are not present on this branch.  The source reconstruction does reproduce
the published 2839-point legacy pool and the corrected 9259-point
`⊕^4 H²` pool.

## Compute spent

Pool regeneration is sub-second.  Exact edge reconstruction takes roughly
8–21 seconds per case on this machine, depending on the clipped half sizes.
The three sanity UNSAT checks above consumed approximately 195 CPU seconds
in total.  No branch changes, PR, or external deployment was made.

## Stage 2: interface patterns and constructive forcing

The stage-2 definitions used by `patterns.py` and `force.py` are:

* For a placement and chosen B-side set `S`, the interface `I` is the set of
  A-side vertices incident to an exact cross edge into `S`.
* A pattern is a partial coloring of a few vertices of `I`.
  `S + cross + pattern` forbids it when that SAT instance is UNSAT.
* Patterns are represented only by their equality type, using canonical
  color labels (`00`, `01` for pairs and the five canonical types for
  triples).  This is sound because the S-side theory has full color
  permutation symmetry.
* Pair patterns are tested first.  A triple is tested only when none of its
  two-vertex restrictions is already a forbidden pair, so the result reports
  minimal patterns through size three.
* A candidate A-side set `L` has the forcing property when
  `4-col(L)` together with one avoidance clause for every forbidden pattern is
  UNSAT.  `force.py` has a growth/CEGAR engine and a DRAT-core plus greedy
  shrink engine.  Interface endpoints of surviving patterns are preserved.

Calibration on the reconstructed full rotated half:

| placement/radius | A-interface | B-interface | cross edges | forbidden pairs | forbidden triples |
|---|---:|---:|---:|---:|---:|
| T=0, 1.6/1.6 | 18 | 18 | 18 | 0 | 0 |
| T=0, 2.0/2.0 | 66 | 66 | 66 | 0 | 0 |
| T65, 1.6/1.6 | 34 | 57 | 71 | 15 | 0 |

Thus, at T=0 in this self-certified reconstruction, mono-pairs do not
suffice; in fact no interface pattern of size at most three was found.  The
forcing engine therefore correctly reports `NO_PATTERNS` and no forcing-L
size at both T=0 radii.  This is consistent with the measurement that the
minimised Parts split does not expose a mono-pair obstruction on its
19-vertex lattice interface.

As a secondary engine calibration, T65 at 1.6/1.6 has 15 forbidden patterns
(all mono-pairs, no triples).  Interface-seeded growth added model-conflicting
or frontier vertices until the full 1535-vertex A half was reached; the
result remained SAT after 53.52 seconds.  The full-half shrink engine also
returned SAT in 0.10 seconds, so no forcing L was claimed.  This is an
important negative result: the pair pattern set at this placement is too weak
to force a subgraph under the current universe.

The pattern analyzer uses PySAT/CaDiCaL for repeated assumptions, including
the usual exactly-one color clauses for every B/interface variable.  Exact
graph edges still come from `univ.py`; no floating-point edge is admitted
without the field check.  Stage-2 pattern analysis timings were 7.70 seconds
for T=0 at 1.6, 236.02 seconds for the 66-interface T=0 radius-2 triple
sweep, and 1.48 seconds for T65 at 1.6 (pairs plus uncovered triples).

## Stage 3: lazy CEGAR interface oracle

Bounded pattern enumeration was replaced by `cegar.py`.  Given a coloring of
the current A set, it asks a persistent SAT instance for B plus all selected
cross edges to extend the complete interface assignment.  If extension is
impossible, deletion-based MUS reduction removes interface literals until the
remaining partial assignment is inclusion-minimal, and its blocking clause is
added to the A-side solver.  If extension succeeds, the A side grows by
model-conflicting or high-constraint frontier pool vertices.  The loop stops
when A is UNSAT under the accumulated lazy pattern clauses.  Pattern orders
are therefore discovered rather than bounded in advance.

`cegar.py` also contains alternating-side minimisation: cached A tests are
used for candidate L deletions, while B deletions first check that all cached
patterns remain forbidden and otherwise re-enter CEGAR.  A DRAT-core pass is
run before greedy deletion.  `verify.py` independently rebuilds the exact
edge set from cached field coordinates and can run kissat plus drat-trim.

### Calibration results

1. **T=0, Parts S135.**  The exact record split is L=374, S=135, with the
   shared origin placed on A.  The corrected CEGAR cross set has 96 edges
   because origin--B edges are correctly treated as cross edges.  Starting
   from L374, CEGAR reaches UNSAT with 227 minimal lazy patterns.  Their
   order distribution is:

   ```
   order 8: 8, 9: 16, 10: 11, 12: 24, 13: 24,
   14: 48, 15: 48, 16: 48
   ```

   Runtime was 175.03 seconds.  This directly confirms the high-order
   interface obstruction: the earlier size-3 enumeration missed all of these
   patterns.  The resulting 509-vertex graph was independently verified:
   509 exact vertices, 2442 recomputed exact edges, kissat UNSAT, and
   drat-trim `s VERIFIED`.

2. **T=0, full rotated half.**  The full reconstructed universe has
   A=2022 and B=2021 unique points.  Lazy CEGAR reached UNSAT with 37
   patterns, distributed as 16 order-3 and 21 order-4 patterns, in
   121.06 seconds.  A DRAT-core reduction of the A side produced
   `|L|=1529`, for a certified total of 3550 vertices.  Independent
   verification recomputed 25052 exact edges and returned kissat UNSAT plus
   drat-trim `s VERIFIED`.

3. **T65, rA=1.6, rB=1.3.**  The full reconstructed universe has
   A=1535 and B=1253 points.  CEGAR reached UNSAT with 28 patterns (18 of
   order 3 and 10 of order 4) in 89.13 seconds.  DRAT-core reduction gave
   `|L|=1123`, hence a certified total of 2376 vertices.  Independent
   verification recomputed 14362 exact edges and returned kissat UNSAT plus
   drat-trim `s VERIFIED`.

4. **T63, rA=1.6, rB=1.3.**  The full reconstructed universe (A=1535,
   B=1253) remained extendible after two discovered order-3 patterns:
   CEGAR reached the full A side and reported `EXTENDS_FULL_A` in 9.50
   seconds.  No non-4-colourable claim or certificate was made for this
   placement.

The T0 full-half and T65 totals above are the best certified totals reached
in this run.  The record calibration starts at the target 374+135 and
provides the expected high-order pattern certificate; the full-half and
translated cases were core-reduced but not yet exhaustive alternating-side
fixpoints.

## Stage 4: fixed-pattern trade-off and symmetric growth

`stage4.py` adds the next search layer.  A discovered pattern set `P` is
held fixed while the A side is tested against the single forcing property
`4-col(A) + avoid(P)`, and the B side is tested by one UNSAT query per
pattern.  The module includes DRAT-core reduction and greedy deletion for
both sides, followed by alternating passes.  For the constructive search,
`a_orbits` reconstructs each A lattice point and groups it under the
order-24 symmetry orbit from `lattice.py`; `grow_orbits` adds whole orbits
chosen from the currently escaping coloring before the deletion post-pass.

The first calibration used the lazy P sets from Stage 3.  The complete
fixed-P minimizer was intentionally not run to a claimed fixpoint on the
large 28/37-pattern cases: per-pattern B DRAT-core extraction is expensive.
The reported curve below is the fast constructive pass (symmetric growth
plus an A-side DRAT-core reduction, with B held at the selected radius).
Every resulting graph was nevertheless independently hard-certified from
coordinates.

### T=0 full-half P curve

The full B half has 2021 points and the lazy set has 37 patterns
(16 order-3, 21 order-4).  Pattern subsets that did not force the A pool
remained `EXTENDS_FULL_A`; the complete set produced:

| patterns retained | A after orbit growth/core | B | total | exact edges |
|---:|---:|---:|---:|---:|
| 10 | 2022 (EXTENDS_FULL_A) | 2021 | 4043 | — |
| 20 | 2022 (EXTENDS_FULL_A) | 2021 | 4043 | — |
| 37 | 718 | 2021 | **2739** | 18462 |

The 2739-vertex candidate passed exact coordinate/edge verification,
kissat UNSAT, and drat-trim `s VERIFIED`.

### T65 B-radius trade-off

All cases use `rA=1.6`.  The reconstructed B sizes and lazy pattern sets
were:

| `rB` | B size | patterns | orders |
|---:|---:|---:|---|
| 1.3 | 1253 | 28 | 18 order-3, 10 order-4 |
| 1.4 | 1304 | 28 | 18 order-3, 10 order-4 |
| 1.5 | 1414 | 33 | 18 order-3, 15 order-4 |

Symmetric A growth plus A-core reduction gave the following certified
trade-off:

| `rB` | A | B | total | exact edges |
|---:|---:|---:|---:|---:|
| 1.3 | 876 | 1253 | 2129 | 12657 |
| 1.4 | 876 | 1304 | 2180 | 13119 |
| 1.5 | 815 | 1414 | 2229 | 13578 |

The non-monotonic A sizes reflect the different lazy pattern sets and
orbit-growth paths, not a count error.  All three canonical rows
independently returned exact distinct coordinates, exact recomputed unit
edges, kissat UNSAT, and drat-trim `s VERIFIED`.

An earlier cache made before `univ.py`'s exclusive edge-label cleanup
produced an additional 2013-vertex candidate at `rB=1.3` (`A=760`,
`B=1253`, 11826 exact edges); its standalone exact verifier also returned
`s VERIFIED`.  The canonical rerun with the current labels is the 2129-row
above, and the stale-cache result is retained as a valid independently
certified graph but not as the reproducibility baseline.

The stale-cache T65 1.3 result, 2013 vertices, is the best Stage-4
certified total so far; the canonical current-label result is 2129.  Both
are still far above 509, but materially below the Stage-3 full-half
deletion result of 2376.  T63 remains a negative control: its Stage-3
full-half lazy set did not force the A pool, so no Stage-4
non-4-colourable candidate was claimed there.

## Stage 5: proof-guided B minimisation

Stage 5 adds the missing B-side reduction machinery.  `stage5.py` uses
three devices:

1. It parses the A-side drat-trim core and retains only pattern clauses
   appearing in that proof.
2. It takes the union of per-pattern B-side DRAT cores before deletion.
3. It provides a gated incremental B SAT instance for destroy-and-repair
   deletion batches, so a batch is tested in one persistent solver rather
   than rebuilding a solver for every pattern.

The full one-at-a-time repair pass remains available, but was not used for
the headline runs: even after the core reduction, thousands of incremental
queries over 28 patterns were too expensive on this box.  Batch-only
destroy-and-repair was used for the reported additional reductions, and
the lazy CEGAR refresh was rerun after each resulting B shrink.

### T65, `rA=1.6`, `rB=1.3`

Starting from the certified Stage-4 witness `(A,B)=(760,1253)`, one
proof-guided round gave:

| step | A | B | total | patterns | orders | time |
|---|---:|---:|---:|---:|---|---:|
| Stage-4 start | 760 | 1253 | 2013 | 28 | 18×3, 10×4 | — |
| A proof prune + B core union | 760 | 1067 | **1827** | 28 | 18×3, 10×4 | 730.73 s |
| batch-only B destroy/repair | 760 | 1003 | **1763** | 28 | 18×3, 10×4 | 237.42 s |

Refreshing the lazy CEGAR oracle after the B shrink returned `UNSAT` with
the same 28-pattern order distribution in 68.06 s.  The 1763-vertex
candidate was independently certified:

- 1763 exact distinct coordinates,
- 10230 exact recomputed unit edges,
- kissat UNSAT,
- drat-trim `s VERIFIED`,
- standalone `verify.py`: `OVERALL: PASS`.

No further batch deletion was possible in a second batch-only pass
(1003 B vertices remained).  The individual repair-enabled greedy pass
was attempted with batch size 64 but was stopped after approximately
20 minutes without producing a result; this is now the next optimization
target rather than an unverified claim.

### T=0 calibration

Starting from the Stage-4 full-half witness `(A,B)=(718,2021)` and its
37 lazy patterns (16 order-3, 21 order-4):

| step | A | B | total | patterns | orders | time |
|---|---:|---:|---:|---:|---|---:|
| Stage-4 start | 718 | 2021 | 2739 | 37 | 16×3, 21×4 | — |
| A proof prune + B core union | 718 | 1836 | **2554** | 37 | 16×3, 21×4 | 839.79 s |
| batch-only B destroy/repair | 718 | 1452 | **2170** | 37 | 16×3, 21×4 | 968.03 s |

Refreshing CEGAR after the B shrink returned `UNSAT` with all 37 patterns
still valid in 127.95 s.  The 2170-vertex candidate was independently
certified:

- 2170 exact distinct coordinates,
- 12357 exact recomputed unit edges,
- kissat UNSAT,
- drat-trim `s VERIFIED`,
- standalone `verify.py`: `OVERALL: PASS`.

Thus B-side core reduction and batch deletion materially improve both
calibrations, but T=0 is still not near 509.  The remaining one-at-a-time
greedy repair and more aggressive pattern-core extraction are unresolved.

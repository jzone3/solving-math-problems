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

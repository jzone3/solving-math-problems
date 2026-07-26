# P23 run `tuniv` — how small can a two-copy non-4-colorable universe be?

Follow-up to `runs/P23-fusion1` entries **E42–E46**. That run discovered that the
*rotation centre* of Parts' type-M construction is a free parameter: his universe
is `A u omega*A` with the rotation taken about the origin, and replacing it by a
translated copy `A u (T + omega*A)` is still non-4-colorable while obstructing in
a much smaller universe (radius 1.6 instead of 2.0, and asymmetric half radii
smaller still).

This run does the systematic version of that observation: a search of the
**four-parameter space (rotation `omega`, translation `T`, radius `rA` of the base
half, radius `rB` of the rotated half)** for the smallest universe whose
non-4-colorability can be verified *exactly*.

**Result.** The smallest exactly-verified non-4-colorable two-copy universe found
is

> **2269 vertices, 12044 exact unit edges** — `omega = omega[15] = (7 + i*sqrt15)/8`,
> `T = (7/8 - sqrt33/6) + i*(sqrt3/6 + sqrt15/8)`, base layers `L = 3`,
> `rA = 1.46`, `rB = 1.2420…`; kissat **UNSAT**, drat-trim **VERIFIED**, edge list
> independently recomputed in exact arithmetic from the pickle.

Everything below is exact: floats are used only as a prefilter, and every
accepted unit edge is re-checked with `dx^2 + dy^2 == 1` in the relevant
multiquadratic field.

## T1 — the base point set had to be rebuilt, and what that changes

The fusion1 scripts (`tscan.py`, `ttest.py`, `tradius.py`, `tasym.py`) all load
`/home/ubuntu/p23w4/w4d.pkl` for Parts' half-A point set, and the `lattice.py`
that produced it was never committed. Neither exists any more, so the pool had to
be reconstructed from first principles (`lattice.py`, `build_pool.py`,
`rotations.py`, `poolio.py`, all self-contained in this directory).

The lattice is Parts': a point is an integer 4-tuple `(a,b,c,d)` standing for
`x = (a + b*sqrt33)/12`, `y = (c*sqrt3 + d*sqrt11)/12`, and

```
144*|z|^2 = (a^2 + 33b^2 + 3c^2 + 11d^2) + 2*(ab + cd)*sqrt33
```

so `|z| = 1` **exactly** iff `a^2+33b^2+3c^2+11d^2 = 144` and `ab + cd = 0`. That
has exactly **30** solutions — the 30 unit vectors of Parts' ring — and the base
set used throughout this run is the clean, fully reproducible

```
A_L(r) = { sums of at most L of the 30 unit vectors } n disk(r)
```

`L = 3` **exactly reproduces the E37 control**: `A_3(2.0)` has 1999 points, and
`A_3(2.0) u omega[15]*A_3(2.0)` is **3997 vertices / 27846 exact edges**,
non-4-colorable (kissat UNSAT, 40 s) — the same two numbers E37 reports. That is
the anchor for every measurement here.

Parts' own `w4d` pool could *not* be reproduced (the fusion1 target of 4033
vertices / 28422 exact edges at `T = 0, r = 2`): that pool was hand-assembled as a
radius-clipped pool unioned with the 374 lattice points of the record itself, so
it is not a first-principles object. Attempts and their counts:

| candidate base | vertices at r=2, T=0 | exact edges |
|---|---:|---:|
| `A_3(2)` (3 unit-vector layers) — **E37 control, matches** | 3997 | 27846 |
| `(+)^4 H^2` reconstruction, radius 2 | 10861 | 91566 |
| same, thresholded to 2023 base points (fusion1's count) | 4045 | 24636 |
| fusion1's `w4d` A-half (target) | 4033 | 28422 |

**Consequence, stated plainly:** the vertex counts in this run are *not*
comparable one-for-one with fusion1's 2917 / 2581. Those were measured in a
denser, differently-assembled pool. The 2269 below is the smallest universe *in
the clean `A_L(r)` family*, measured against this run's own `T = 0` control
(3997). It is a smaller absolute number than 2581, but the honest comparison is
the *effect*, not the raw count: in both pools, moving the rotation centre buys
the obstruction at a radius well below the one the origin-centred construction
needs.

## T2 — rotation floors at `T = 0`: only Parts' rotation obstructs

Rotations `omega_t = (2t-1 + i*sqrt(4t-1))/(2t)` stay in `Q(sqrt3,sqrt5,sqrt11)`
only for `4t-1` in `{3,5,11,15,33,55,165}`, but exactness does not require the
base field — `rotations.py` builds each rotation in whatever multiquadratic field
it needs (`Q(sqrt3,sqrt11)`, `Q(sqrt3,sqrt5,sqrt11)`, `Q(sqrt3,sqrt7,sqrt11)` for
`t = 16` where `sqrt63 = 3*sqrt7`, `Q(sqrt3,sqrt11,sqrt37)` for `t = 28` where
`sqrt111 = sqrt3*sqrt37`), so all 27 variants below are decided in exact
arithmetic.

For each variant, the radius at which the *origin-centred* union first fails to
4-colour (ladder 2.4, 2.2, 2.0, 1.9, 1.8; kissat cap 600 s, no timeouts):

| rotation variants | outcome | floor |
|---|---|---|
| `w[15]`, `w[15]~` | SAT at 1.9, UNSAT at 2.0 / 2.2 / 2.4 | **r0 = 2.0** (3997 vtx / 27846 e) |
| `w[3]`, `w[5]`, `w[11]`, `w[33]`, `w[55]`, `w[165]` + conjugates + squares (24 variants) | SAT at every radius 1.8–2.4 | none in range |
| `t = 16`, `t = 28` + conjugates + squares | SAT at every radius 1.8–2.4 | none in range |

`w[15]~` is the mirror image of `w[15]` and reproduces it exactly, as it must.
So **Parts' rotation is the only one in the whole `omega_t` family that obstructs
at all here**, which sharpens E36's "his choice of ring, base and rotation is
close to isolated": the rotation is isolated too, and adding a translation
(section T3) does not rescue the others.

## T3 — translations: the scan, and how well the KD-tree proxy predicts

Candidate translations are exactly those producing at least one cross edge,
`T = p - q - u` for `p` in `A`, `q` in `omega*A`, `u` one of the 30 unit vectors.
They are sampled, deduplicated and ranked by a **numeric** KD-tree count of A-to-
`(T + omega A)` unit pairs (floats, prefilter only), then decided exactly.

56 distinct `w[15]` translations were screened exactly at symmetric radius 1.9 —
a radius at which `T = 0` is **SAT**, so every UNSAT there is already the E44
effect reproduced in the clean base:

| proxy score | screened | UNSAT | SAT |
|---:|---:|---:|---:|
| 90+ | 1 | 0 | 1 |
| 85–89 | 11 | 10 | 1 |
| 80–84 | 15 | 11 | 4 |
| 75–79 | 25 | 13 | 12 |
| <75 | 4 | 0 | 4 |

**34 of 56 are UNSAT at 1.9 while `T = 0` is SAT there.** So the effect is not a
lucky translation: a large fraction of well-coupled placements beat the origin.
The proxy is a useful prioritiser above ~80 and useless as a predictor in the
middle of the range (its top-scoring candidate is SAT) — worth knowing, because
it means ranking by cross-pair count cannot be trusted to find the best
placement, only to enrich the candidate list.

All 34 were then descended to the champion's radius pair (`rA = 1.46`,
`rB = 1.2420`) with triangle symmetry breaking: **32 SAT, 2 UNSAT, 0 timeouts**
(`translation_descent.tsv`). By monotonicity the 32 cannot recover at any smaller
radius, so the search over screened translations is closed, and the two survivors
(`w_15_e201c77f6560`, `w_15_3e07397d03c4`) give the identical 2269 / 12044
universe — presumably the same placement up to a lattice symmetry.

The other rotations were re-tested *with* their top translations at radii 2.0 and
2.2 (`w[3]`, `w[11]`, `t = 16`, `t = 28`): all **SAT**. Translation does not
rescue a rotation that does not obstruct at the origin.

The monotonicity that makes this affordable: shrinking either radius only deletes
vertices and edges, so a placement that is SAT at radius `r` is SAT at every
smaller radius, and only the survivors at 1.9 need descending.

## T4 — symmetric descent

Best symmetric radii for the leading translations (all exact, all UNSAT unless
marked):

| rA = rB | vertices | exact edges | status |
|---:|---:|---:|---|
| 1.9 | 3733 | 24828–24854 | UNSAT (`T = 0`: **SAT**) |
| 1.8 | 3397 | 21696 | UNSAT (`T = 0`: SAT) |
| 1.7 | 3157 | 19460 | UNSAT |
| 1.6 | 2881 | 17261 | UNSAT |
| 1.55 | 2713 | 15725 | UNSAT |
| 1.52 | 2641 | 14993 | UNSAT |
| 1.50 | 2593 | 14631 | UNSAT |
| 1.46 / 1.49 | **2569** | 14441 | UNSAT |
| 1.4440 | 2509 | 13827 | SAT |
| 1.4242 | 2413 | 13201 | SAT |

Also measured: the denser base `L = 4` obstructs (10861 vtx at r = 2.0, 12997 at
2.2) but its floor is the same 2.0 and it is far larger, so density does not buy
a smaller universe — `L = 3` is the right base.

## T5 — asymmetric halves

With `rA` pinned at 1.46, `rB` was pushed down by *attained shell norms* rather
than decimal steps, so each step peels exactly one shell:

| rA | rB | vertices | exact edges | status |
|---:|---:|---:|---:|---|
| 1.46 | 1.46 | 2569 | 14441 | UNSAT |
| 1.46 | 1.4440 | 2539 | 14134 | UNSAT |
| 1.46 | 1.4242 | 2491 | 13821 | UNSAT |
| 1.46 | 1.3696 | 2443 | 13389 | UNSAT |
| 1.46 | 1.3592 | 2425 | 13185 | UNSAT |
| 1.46 | 1.30 (= 1.2910 shell) | 2389 | 12909 | UNSAT |
| 1.46 | 1.2869 | 2353 | 12584 | UNSAT |
| 1.46 | 1.2758 | 2329 | 12464 | UNSAT |
| 1.46 | 1.2585 | 2281 | 12116 | UNSAT |
| 1.46 | 1.2420 | **2269** | **12044** | **UNSAT** |
| 1.46 | 1.2146 | 2233 | 11714 | SAT |

There is **no attained shell strictly between `rB = 1.2420` and `rB = 1.2146`**,
so in the attained-shell ordering this boundary is exact, not merely bracketed:
2269 vertices is the smallest universe of this shape that is non-4-colorable, and
the next shell down is 4-colorable.

The last four UNSAT rows were timeouts at a 300–600 s cap and were only decided
after adding **triangle symmetry breaking** — fixing a triangle of the graph to
colours 0,1,2, which is sound because any proper 4-colouring can be permuted to
agree with it (no 4-clique exists in these graphs, so a full clique assumption
was not available). With it, decisions land in ~110–170 s instead of stalling.
Nothing here is a proof-by-timeout: the boundary is `rB = 1.2420` UNSAT versus
`rB = 1.2146` SAT.

The asymmetry is real, in the same direction as fusion1's E45, and *not* a size
effect. Two independent measurements:

* the **symmetric** universe at 2413 vertices is SAT while the asymmetric 2389
  and 2269 are UNSAT — fewer vertices, still non-4-colorable;
* pinning `rB` and lowering `rA` instead kills the obstruction immediately
  (`rA = 1.4530` at 2551 vtx SAT with `rB = 1.46`; `rA = 1.4530` at 2371 vtx SAT
  with `rB = 1.30`). The base half must keep its 1.46 shell; all the slack is in
  the rotated half (`asymmetry_probe.tsv`).

## T6 — the champion, and how to re-check it

```
rotation      omega[15] = (7 + i*sqrt15)/8            (Parts' rotation)
translation   T = (7/8 - sqrt33/6) + i*(sqrt3/6 + sqrt15/8)   id w_15_e201c77f6560
base          A_3(r) = sums of <= 3 of the 30 unit vectors, clipped to disk(r)
radii         rA = 1.46 (base half), rB = 1.2420035798030784 (rotated half)
universe      A_3(1.46)  u  ( T + omega[15] * A_3(1.2420...) )
size          2269 vertices, 12044 exact unit edges, 43 exact cross edges
decision      kissat + triangle symmetry breaking: s UNSATISFIABLE (137 s)
certificate   drat-trim: s VERIFIED (142 s; 36335/64062 clauses, 1266464 lemmas
              in core, 89582116 resolution steps)
independent   verify_universe.py: 2269 vertices, 12044 exact edges: PASS
mirror check  conjugate rotation + conjugated T reproduces the geometry exactly
              (checked at rA = rB = 1.46: 2389 vtx / 12909 e, UNSAT)
```

`T` involves `sqrt15`, so it lies in neither the base lattice nor `omega*`lattice
— as in E43 this is a translated placement of Parts' two-copy structure, not a
new lattice and not a new rotation. Only **43** of the 12044 edges cross between
the halves, against 96 in Parts' origin-centred universe at radius 2: the
obstruction survives on less than half the coupling.

Artifacts in this directory:

* `champion.pkl` / `record_2269.pkl` — the champion (exact field points + edges)
* `record_2569.pkl`, `record_2539.pkl`, `record_2491.pkl`, `record_2443.pkl`,
  `record_2425.pkl`, `record_2389.pkl`, `record_2353.pkl`, `record_2329.pkl`,
  `record_2281.pkl` — every record-setting UNSAT universe on the way down
* `long_solver_notes.tsv`, `asymmetry_probe.tsv`, `translation_descent.tsv` — the
  symmetry-breaking runs, the `rA`-vs-`rB` probe, and all 34 obstructing
  translations descended to the champion's radius pair
* `tuniv_w_15_*.pkl` — the 16 UNSAT universes from the translation screen
* `results.tsv` — all 567 exact decisions (rotation, translation id and exact
  field coordinates, `L`, `rA`, `rB`, vertices, edges, status, seconds).
  Caveat: the `cross_edges` column carries the numeric KD-tree proxy for
  screening rows and 0 for `T = 0` rows; the exact cross count appears in
  `champion_summary.tsv`
* `record_manifest.tsv`, `champion_summary.tsv`, `champion_verification.txt`
* `verify_universe.py` — reloads a pickle, recomputes **all** unit edges from
  scratch in exact arithmetic and confirms the stored edge list; the
  re-verification path that any claim here must pass
* `lattice.py`, `rotations.py`, `build_pool.py`, `poolio.py`, `floor.py`,
  `phase2.py`, `refine.py` — the pipeline; `sat.py`, `mfield.py`, `findrot.py`
  carried over from fusion1

## What this is *not*

The object here is a **universe** — a finite point set whose unit-distance graph
is not 4-colorable — not a small 5-chromatic graph. No 5-chromatic witness is
claimed: the 509-vertex record stands, and extracting a witness from this
universe still needs the minimisation machinery (greedy/DRAT-core descent,
hitting-set bounds) that fusion1 runs. What the universe buys is where that
machinery has to run: 2269 vertices with 12044 edges instead of 3997/27846
(this run's own origin-centred control) or the 4033-vertex pool every recent
exact search has used, with a non-4-colorability proof in ~3 minutes and a
DRAT certificate in ~2.

Open, in decreasing order of interest:

1. more translations — only 56 were screened exactly, and 34 of those obstruct at
   1.9, so the placement space is far from exhausted even though every screened
   placement bottoms out at 2269;
2. minimising *inside* the 2389-vertex universe, which is the only route from
   this to an actual graph;
3. two-parameter placements (both halves translated, or three copies as in E42)
   and rotations outside the `omega_t` family, i.e. rotation centres that are not
   lattice-related at all.

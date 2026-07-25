# P23 parts-method campaign report

## Headline outcome

No sub-509 5-chromatic unit-distance graph was found in this run.
The smallest exactly verified 5-chromatic unit-distance graph remains the
509-vertex witness `solutions/P23/v509e2442.{vtx,edges}`, independently
verified by Kissat and drat-trim.

## What this run contributed beyond the earlier work

This branch did the Parts-specific reimplementation that the earlier runs did
not have:

- exact coordinate arithmetic for Parts' ring model in `mring.py`
- exact orbit generation under the order-24 symmetry group `τ0..τ5`
- faithful recovery of the record as `L374 ∪ ρS136` with exactly one shared
  witness vertex
- orbit-table comparison against Parts' published tables `tl` and `ts`
- exact SAT encodings for the Parts-style working graphs and their companions
- the expansion screen with the corrected polarity
- expansion sweeps and hybrid minimization on the best corrected expansions

It also kept a clean campaign log of the results, including zero-score
expansions and truncated runs.

## Decomposition verdict

The decomposition gate passed:

- `L`: 374 vertices
- `S`: 136 vertices
- shared witness vertices: 1
- total physical record: 509 vertices
- exact induced-edge counts: `L1860`, `S564`

The orbit-table comparison is faithful:

- `S136` matches Table `ts`, column `M6A`, exactly.
- `L374` matches Table `tl` modulo the published `{M}` ranges; the four
  deviations are valid because the shipped witness is a different member of
  Parts' minimal set `{M}` than the paper's column-M representative.

## Methodology

The campaign uses the following exact machinery:

- within-subgraph distances: integer ring criterion only
- cross-subgraph distances: exact `mfield` arithmetic over
  `Q(√3,√5,√11)`
- SAT encoding: common edge/AMO clauses precomputed once, per-check positive
  clauses added only for the surviving active set
- symmetry-breaking: the L-clique units are emitted only while the clique
  vertices are active
- screen polarity: `SAT` after deleting an old vertex means the vertex is
  indispensable; `UNSAT` means the vertex is freed
- hybrid minimization: core jumps plus greedy destructive deletion

The screen score is therefore the SAT-deletion count, and the freed count is
`old_count - SAT_count`.

## Experiments

### Corrected expansion sweep

The single-orbit and multi-orbit sweep was rerun with the corrected polarity.
The useful expansions were the ones with the smallest SAT-deletion count / the
largest freed count.

Representative corrected scores:

- S `(6,2,4,0)`: 7 freed
- S `(6,2,4,0) + (6,0,4,6) + (12,0,2,6)`: 51 freed
- L `(6,2,4,0)`: 9 freed
- L `(6,2,4,0) + (1,1,3,5) + (6,2,8,0)`: 29 freed
- joint L∪S screen: strong redundancy, but no sub-509 graph

The best corrected expansion on the S side was the triple
`(6,2,4,0) + (6,0,4,6) + (12,0,2,6)`, which freed 51 of the 136 old S
vertices and expanded to 185 vertices.

### Hybrid core/greedy floors

The hybrid minimizer was then run from the best corrected expansion pools.
Its floors were:

- `pool_sbest` (S triple): 509 for seeds 0, 1, and 2
- `pool_lbest` (L triple): 519 and 520 for seeds 0 and 1
- `pool_joint` (joint expansion): 509 for seeds 0 and 1
- `pool_split_s181`: 554 for seed 0

`pool_split_s181` seed 1 returned `NOVERIFY` at the core step. That means the
Kissat proof was not certified by drat-trim for that seed, so no verified core
was produced and no minimization floor can be claimed from it.

### Deep phase-2 runs

The strongest greedy expansions were also sent through untruncated phase-2
reduction with degree cap 3:

- S triple `[(6,2,4,0), (6,0,4,6), (12,0,2,6)]`
- L triple `[(6,2,4,0), (1,1,3,5), (6,2,8,0)]`

Both were explicitly stopped after about 2h02m wall time and recorded as
`TRUNCATED` / `phase-2 incomplete`. As expected, a truncated exhaustive
enumeration does not prove anything, so these runs are logged only as
unfinished experiments.

### Final deeper greedy/hybrid push

The last exploratory push extended the corrected greedy screen beyond the
three-orbit S and L expansions.  Each next orbit was chosen by maximum freed
count, with exact SAT screens for every candidate.  The S curve was:

| selected orbits | freed old S vertices |
|---:|---:|
| 1 | 7 |
| 2 | 23 |
| 3 | 51 |
| 4 | 59 |
| 5 | 59 |
| 6 | 59 |

The six-orbit S pool had 627 vertices, 3012 edges, 254 variable S vertices,
and 373 fixed L vertices.  The score plateaued at 59, so the depth-7/8
continuation was stopped rather than spending the remaining budget on
zero-growth screens.

The corresponding L curve was:

| selected orbits | freed old L vertices |
|---:|---:|
| 1 | 9 |
| 2 | 19 |
| 3 | 29 |
| 4 | 51 |
| 5 | 55 |
| 6 | 55 |

The final six-orbit L pool had 625 vertices, 3212 edges, 490 variable L
vertices, and 135 fixed companion vertices.  It likewise plateaued after
five selected orbits.

The corrected joint rerun reached one greedy step.  Its best tested addition
was `(6,2,4,0)` on the L side, alongside the initial
`(4,0,4,4)`/`(12,2,2,0)` expansion, freeing 18 old union vertices.  The
joint continuation was stopped after this step when the S and L hybrid
minimizers had priority.  Earlier joint rows showing negative freed counts
are retained in the raw appendix as the output of the already-documented
buggy accounting; they are not used as results.

The hybrid minimizer was run with four independent seeds on each deeper
pool.  All completed with drat-trim-certified core jumps; no floor was below
the record:

| pool | seed floors (pool total) | corresponding working-side floors |
|---|---|---|
| deeper L, 625 total, 135 fixed | 524, 534, 533, 529 | L = 389, 399, 398, 394 |
| deeper S, 627 total, 373 fixed | 525, 518, 523, 521 | S = 152, 145, 150, 148 |
| deeper joint, 566 total, 156 fixed | 516, 513 | union total = 516, 513 |

Thus the deepest S expansion did not approach the 136-vertex target after
hybrid minimization, and the deeper L expansion remained well above 374.
The deeper joint pool also stayed above 509.
No candidate reached a below-record threshold, so no new exact
reconstruction/independent-verifier/`s VERIFIED` gate was triggered.

### Parallel branch: `runs/P23-parts-gadgets` (finished)

This branch followed the gadget/devirtualization route and produced a separate,
finished negative result:

- reproduced the lattice arithmetic
- minimized 8 gadget classes
- `√7` non-mono-triple: 188 vs Parts' 159
- mono-pair `8/3`: 548 vs Parts' 367
- exhaustive `k <= 4` chain enumeration over all 20 mono vectors showed no
  type-J/A cycle closure inside the lattice; the only rational closing distance
  was `64/9`
- off-lattice spindles share exactly one vertex by the field argument
  `√247 ∉ Q(√3,√11)`, giving a 733-vertex floor for type J even with Parts'
  best gadgets
- no distance in the 30-distance scan admitted both mono and non-mono
  properties
- clamping costed at `79 + 118·306` naively and collapsed to the already
  exhausted monolithic minimization under maximal overlap
- an explicit 1095-vertex 5-chromatic spindle over
  `Q(√3,√11,√13,√19)` passes exact verification and drat-trim `s VERIFIED`

Conclusion from that branch: gadget assembly cannot beat 509 with the known
menu; it would need a mono-pair gadget of at most 254 vertices or a new mono
distance with unit-closing lattice chains.

### Parallel branch: `runs/P23-parts-rho` (still running)

Placeholder for the type-M rotation scan over the other Loeschian `ω_t`
values that Parts explicitly left unexplored. Numbers will be filled in when
that branch reports.

## Interpretation

What the run now tells us is fairly clear:

- the record decomposition and coordinate machinery are faithful
- Parts-style expansion can free old vertices, so the screen is behaving as
  intended
- the best corrected expansions still do not drive the hybrid minimizer below
  509
- the deep phase-2 path is too expensive for these expansions within this
  budget
- the gadget route, separately, is also below the bar needed to beat 509

The remaining plausible directions are therefore:

1. a genuinely new expansion family that frees many more old vertices than the
   current reserve sweep
2. a new gadget menu, or a mono-pair gadget with 254 or fewer vertices
3. the still-running `runs/P23-parts-rho` rotation scan, which may uncover a
   better type-M geometry
4. a future split-curve exploration with a larger frozen companion if that run
   turns out to be structurally more favorable

## Files and reproduction

Key files in `runs/P23-parts-method/`:

- `mring.py` — exact Parts ring arithmetic and orbit generation
- `decompose509.py` — faithfulness gate for the 509 witness
- `decomp509.pkl` — cached decomposition
- `sat_parts.py` — exact SAT / exact graph helpers
- `finesearch.py` — Parts-style fine search and expansion reserve
- `screening.py` — corrected expansion screen
- `joint_screen.py` — joint L/S screen
- `greedy.py` — greedy destructive minimization on screened expansions
- `deep_search.py` — untruncated phase-2 driver
- `hybrid_core.py`, `hybrid_min.py`, `build_hybrid_pools.py` — corrected
  adapter around the legacy core/greedy minimizer

Solver paths come from the environment:

- `KISSAT=/home/ubuntu/tools/kissat/build/kissat`
- `DRATTRIM=/home/ubuntu/tools/drat-trim/drat-trim`

Useful reproduction commands:

```bash
KISSAT=/home/ubuntu/tools/kissat/build/kissat DRATTRIM=/home/ubuntu/tools/drat-trim/drat-trim python3 decompose509.py

KISSAT=/home/ubuntu/tools/kissat/build/kissat DRATTRIM=/home/ubuntu/tools/drat-trim/drat-trim python3 build_hybrid_pools.py

KISSAT=/home/ubuntu/tools/kissat/build/kissat DRATTRIM=/home/ubuntu/tools/drat-trim/drat-trim python3 screening.py --leg S --screen-only

KISSAT=/home/ubuntu/tools/kissat/build/kissat DRATTRIM=/home/ubuntu/tools/drat-trim/drat-trim python3 hybrid_min.py --pool pool_sbest.pkl --start start_sbest.pkl   --fixed fixed_sbest.pkl --seed 0 --timeout 300   --output hybrid_sbest_0.pkl
```

## Compute spent

The earlier campaign rows sum to **4.57 hours** of recorded wall time.  The
final deeper greedy/hybrid push added approximately **2 hours of wall-clock
work** across concurrent S, L, and joint screens and four-seed hybrid runs.
The total campaign expenditure was therefore approximately **6.6 wall-clock
hours** (with the screening and hybrid legs parallelized across the available
cores).  The largest earlier single chunks were the two deep phase-2 legs,
each running for about **2h02m** before being stopped as truncated.

## Appendix A: raw campaign log

The table rows below are preserved verbatim as the measurement appendix.
| date/time | leg | expansion | `|W|` | cap | hyperedges | phase-2 list | checks | minima | wall time | result |
| 2026-07-24T20:28:31 | L | Parts opener (0, 0, 2, 2) | 380 | 3 | 1:374,2:0,3:0 | 1 | 749 | - | 317.5s | UNSAT |
| 2026-07-24T21:13:10 | L | Parts opener (0, 0, 2, 2) | 380 | 3 | 1:374,2:0,3:0 | 1 | 714 | - | 141.8s | UNSAT |
| 2026-07-24T21:15:50 | L | Parts opener (4, 0, 10, 2) | 394 | 3 | 1:374,2:0,3:0 | 1 | 726 | - | 160.4s | UNSAT |
| 2026-07-24T21:21:11 | S | orbit (0, 0, 8, 0) | 139 | 4 | baseline only | - | - | - | 3.4s | UNSAT |
| 2026-07-24T21:21:11 | S | orbit (0, 4, 0, 0) | 138 | 4 | baseline only | - | - | - | 3.6s | UNSAT |
| 2026-07-24T21:21:11 | S | orbit (12, 2, 2, 0) | 157 | 4 | baseline only | - | - | - | 5.5s | UNSAT |
| 2026-07-24T21:21:11 | L | orbit (0, 0, 0, 4) | 377 | 3 | baseline only | - | - | - | 2.7s | UNSAT |
| 2026-07-24T21:21:11 | L | orbit (4, 0, 10, 2) | 394 | 3 | baseline only | - | - | - | 3.5s | UNSAT |
| 2026-07-24T21:33:42 | L | orbit (0, 0, 2, 2) | 380 | 3 | 1:374,2:0,3:0 | 1 | 713 | - | 138.8s | UNSAT |
| 2026-07-24T21:33:42 | S | orbit (12, 2, 2, 0) | 157 | 4 | 1:135,2:0,3:0,4:0 | 1 | 285 | - | 166.9s | UNSAT |
| 2026-07-24T21:33:51 | S | screen (12, 2, 2, 0) | 157 | - | 135 | 136 | 22.8s | UNSAT |
| 2026-07-24T21:33:59 | L | screen (4, 0, 4, 4) | 398 | - | 371 | 374 | 29.5s | UNSAT |
| 2026-07-24T21:51:02 | L | screen (1, 1, 3, 5) | 398 | - | 374 | 374 | 27.1s | UNSAT |
| 2026-07-24T22:08:18 | L | screen ((4, 0, 4, 4), (1, 1, 3, 5)) | 422 | - | 369 | 374 | 40.0s | UNSAT |
| 2026-07-24T22:40:46 | S | screen (12, 2, 2, 0) | 157 | - | 135 | 136 | 22.7s | UNSAT |
| 2026-07-24T22:40:48 | L | screen (4, 0, 4, 4) | 398 | - | 371 | 374 | 29.4s | UNSAT |
| 2026-07-24T22:44:36 | L | screen (1, 1, 3, 5) | 398 | - | 374 | 374 | 26.9s | UNSAT |
| 2026-07-24T23:01:22 | S | screen (6, 2, 4, 0) | 146 | - | 129 | 136 | 28.9s | UNSAT |
| 2026-07-24T23:14:45 | joint | L(4, 0, 4, 4)+S(12, 2, 2, 0) | 554 | - | 504 | 509 | 54.4s | UNSAT |
| 2026-07-24T23:16:14 | S | screen (1, 1, 3, 5) | 160 | - | 136 | 136 | 16.2s | UNSAT |
| 2026-07-24T23:41:56 | S | screen (12, 2, 2, 0) | 157 | - | 135 | 136 | 22.7s | UNSAT |
| 2026-07-24T23:42:13 | L | screen (4, 0, 4, 4) | 398 | - | 371 | 374 | 29.3s | UNSAT |
| 2026-07-24T23:42:25 | S | screen (6, 2, 4, 0) | 146 | - | 129 | 136 | 28.9s | UNSAT |
| 2026-07-24T23:42:39 | L | screen (1, 1, 3, 5) | 398 | - | 374 | 374 | 26.9s | UNSAT |
| 2026-07-24T23:42:42 | S | screen (1, 1, 3, 5) | 160 | - | 136 | 136 | 16.2s | UNSAT |
| 2026-07-24T23:42:58 | S | screen (4, 0, 2, 2) | 160 | - | 136 | 136 | 16.9s | UNSAT |
| 2026-07-24T23:43:14 | L | screen (2, 0, 2, 4) | 390 | - | 369 | 374 | 34.5s | UNSAT |
| 2026-07-24T23:43:20 | S | screen (6, 0, 4, 6) | 144 | - | 135 | 136 | 21.1s | UNSAT |
| 2026-07-24T23:43:36 | S | screen (2, 0, 4, 2) | 160 | - | 136 | 136 | 16.5s | UNSAT |
| 2026-07-24T23:43:38 | L | screen (10, 0, 8, 2) | 398 | - | 374 | 374 | 24.4s | UNSAT |
| 2026-07-24T23:43:52 | S | screen (12, 0, 2, 6) | 148 | - | 136 | 136 | 15.5s | UNSAT |
| 2026-07-24T23:43:59 | L | screen (6, 2, 4, 0) | 386 | - | 365 | 374 | 20.4s | UNSAT |
| 2026-07-24T23:44:07 | S | screen (0, 0, 6, 6) | 142 | - | 136 | 136 | 15.9s | UNSAT |
| 2026-07-24T23:44:30 | L | screen (6, 2, 8, 0) | 390 | - | 368 | 374 | 30.9s | UNSAT |
| 2026-07-24T23:47:05 | S | screen (12, 2, 2, 0) | 157 | - | 135 | 136 | 22.7s | UNSAT |
| 2026-07-24T23:47:34 | S | screen (6, 2, 4, 0) | 146 | - | 129 | 136 | 28.9s | UNSAT |
| 2026-07-24T23:47:50 | S | screen (1, 1, 3, 5) | 160 | - | 136 | 136 | 16.2s | UNSAT |
| 2026-07-24T23:48:26 | S | screen ((12, 2, 2, 0), (6, 2, 4, 0)) | 167 | - | 124 | 136 | 36.1s | UNSAT |
| 2026-07-24T23:48:46 | S | screen ((12, 2, 2, 0), (1, 1, 3, 5)) | 181 | - | 135 | 136 | 19.1s | UNSAT |
| 2026-07-24T23:49:11 | S | screen ((6, 2, 4, 0), (1, 1, 3, 5)) | 170 | - | 129 | 136 | 25.3s | UNSAT |
| 2026-07-24T23:49:46 | S | screen ((12, 2, 2, 0), (6, 2, 4, 0), (1, 1, 3, 5)) | 191 | - | 124 | 136 | 35.2s | UNSAT |
| 2026-07-25T00:37:43 | S | screen (12, 2, 2, 0) | 157 | indispensable=135;freed=1 | 135 | 136 | 22.7s | UNSAT |
| 2026-07-25T00:37:48 | L | screen (4, 0, 4, 4) | 398 | indispensable=371;freed=3 | 371 | 374 | 29.3s | UNSAT |
| 2026-07-25T00:38:12 | S | screen (6, 2, 4, 0) | 146 | indispensable=129;freed=7 | 129 | 136 | 28.9s | UNSAT |
| 2026-07-25T00:38:15 | L | screen (1, 1, 3, 5) | 398 | indispensable=374;freed=0 | 374 | 374 | 26.9s | UNSAT |
| 2026-07-25T00:38:28 | S | screen (1, 1, 3, 5) | 160 | indispensable=136;freed=0 | 136 | 136 | 16.2s | UNSAT |
| 2026-07-25T00:38:45 | S | screen (4, 0, 2, 2) | 160 | indispensable=136;freed=0 | 136 | 136 | 16.9s | UNSAT |
| 2026-07-25T00:38:49 | L | screen (2, 0, 2, 4) | 390 | indispensable=369;freed=5 | 369 | 374 | 34.5s | UNSAT |
| 2026-07-25T00:39:06 | S | screen (6, 0, 4, 6) | 144 | indispensable=135;freed=1 | 135 | 136 | 21.1s | UNSAT |
| 2026-07-25T00:39:14 | L | screen (10, 0, 8, 2) | 398 | indispensable=374;freed=0 | 374 | 374 | 24.4s | UNSAT |
| 2026-07-25T00:39:23 | S | screen (2, 0, 4, 2) | 160 | indispensable=136;freed=0 | 136 | 136 | 16.5s | UNSAT |
| 2026-07-25T00:39:34 | L | screen (6, 2, 4, 0) | 386 | indispensable=365;freed=9 | 365 | 374 | 20.4s | UNSAT |
| 2026-07-25T00:39:38 | S | screen (12, 0, 2, 6) | 148 | indispensable=136;freed=0 | 136 | 136 | 15.5s | UNSAT |
| 2026-07-25T00:39:54 | S | screen (0, 0, 6, 6) | 142 | indispensable=136;freed=0 | 136 | 136 | 15.9s | UNSAT |
| 2026-07-25T00:40:05 | L | screen (6, 2, 8, 0) | 390 | indispensable=368;freed=6 | 368 | 374 | 30.9s | UNSAT |
| 2026-07-25T00:40:47 | L | greedy1 ((6, 2, 4, 0), (4, 0, 4, 4)) | 410 | indispensable=359;freed=15 | 359 | 374 | 24.3s | UNSAT |
| 2026-07-25T00:40:58 | S | greedy1 ((6, 2, 4, 0), (12, 2, 2, 0)) | 167 | indispensable=124;freed=12 | 124 | 136 | 36.1s | UNSAT |
| 2026-07-25T00:41:13 | L | greedy1 ((6, 2, 4, 0), (1, 1, 3, 5)) | 410 | indispensable=355;freed=19 | 355 | 374 | 26.5s | UNSAT |
| 2026-07-25T00:41:24 | S | greedy1 ((6, 2, 4, 0), (1, 1, 3, 5)) | 170 | indispensable=129;freed=7 | 129 | 136 | 25.3s | UNSAT |
| 2026-07-25T00:41:36 | L | greedy1 ((6, 2, 4, 0), (2, 0, 2, 4)) | 402 | indispensable=363;freed=11 | 363 | 374 | 23.3s | UNSAT |
| 2026-07-25T00:41:52 | S | greedy1 ((6, 2, 4, 0), (4, 0, 2, 2)) | 170 | indispensable=129;freed=7 | 129 | 136 | 28.8s | UNSAT |
| 2026-07-25T00:41:54 | L | greedy1 ((6, 2, 4, 0), (10, 0, 8, 2)) | 410 | indispensable=365;freed=9 | 365 | 374 | 18.0s | UNSAT |
| 2026-07-25T00:42:16 | L | greedy1 ((6, 2, 4, 0), (6, 2, 8, 0)) | 402 | indispensable=359;freed=15 | 359 | 374 | 22.0s | UNSAT |
| 2026-07-25T00:42:29 | S | greedy1 ((6, 2, 4, 0), (6, 0, 4, 6)) | 161 | indispensable=113;freed=23 | 113 | 136 | 36.1s | UNSAT |
| 2026-07-25T00:42:49 | L | greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (4, 0, 4, 4)) | 434 | indispensable=347;freed=27 | 347 | 374 | 32.9s | UNSAT |
| 2026-07-25T00:42:55 | S | greedy1 ((6, 2, 4, 0), (2, 0, 4, 2)) | 170 | indispensable=129;freed=7 | 129 | 136 | 26.8s | UNSAT |
| 2026-07-25T00:43:22 | L | greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (2, 0, 2, 4)) | 426 | indispensable=349;freed=25 | 349 | 374 | 32.3s | UNSAT |
| 2026-07-25T00:43:25 | S | greedy1 ((6, 2, 4, 0), (12, 0, 2, 6)) | 170 | indispensable=122;freed=14 | 122 | 136 | 30.0s | UNSAT |
| 2026-07-25T00:43:48 | L | greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (10, 0, 8, 2)) | 434 | indispensable=355;freed=19 | 355 | 374 | 26.0s | UNSAT |
| 2026-07-25T00:43:56 | S | greedy1 ((6, 2, 4, 0), (0, 0, 6, 6)) | 158 | indispensable=124;freed=12 | 124 | 136 | 30.8s | UNSAT |
| 2026-07-25T00:44:17 | L | greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0)) | 426 | indispensable=345;freed=29 | 345 | 374 | 28.7s | UNSAT |
| 2026-07-25T00:44:42 | S | greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 2, 2, 0)) | 182 | indispensable=105;freed=31 | 105 | 136 | 45.6s | UNSAT |
| 2026-07-25T00:45:21 | S | greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (1, 1, 3, 5)) | 185 | indispensable=113;freed=23 | 113 | 136 | 38.8s | UNSAT |
| 2026-07-25T00:46:00 | S | greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (4, 0, 2, 2)) | 185 | indispensable=113;freed=23 | 113 | 136 | 39.3s | UNSAT |
| 2026-07-25T00:46:35 | S | greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (2, 0, 4, 2)) | 185 | indispensable=113;freed=23 | 113 | 136 | 34.6s | UNSAT |
| 2026-07-25T00:47:22 | S | greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6)) | 185 | indispensable=85;freed=51 | 85 | 136 | 47.5s | UNSAT |
| 2026-07-25T00:48:13 | S | greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (0, 0, 6, 6)) | 173 | indispensable=88;freed=48 | 88 | 136 | 50.4s | UNSAT |
| 2026-07-25T01:13:59 | S | deep-start [(6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6)] | 185 | 3 | untruncated | - | - | - | RUNNING |
| 2026-07-25T01:13:59 | L | deep-start [(6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0)] | 426 | 3 | untruncated | - | - | - | RUNNING |
| 2026-07-25T03:16:24 | S | deep-stop [(6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6)] | 185 | 3 | phase-2 incomplete | - | 2h02m | - | TRUNCATED |
| 2026-07-25T03:16:24 | L | deep-stop [(6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0)] | 426 | 3 | phase-2 incomplete | - | 2h02m | - | TRUNCATED |
| 2026-07-25T04:11:10 | L | deep-greedy1 ((6, 2, 4, 0), (4, 0, 4, 4)) | 410 | indispensable=359;freed=15 | 359 | 374 | 46.3s | UNSAT |
| 2026-07-25T04:11:29 | S | deep-greedy1 ((6, 2, 4, 0), (12, 2, 2, 0)) | 167 | indispensable=124;freed=12 | 124 | 136 | 65.6s | UNSAT |
| 2026-07-25T04:12:01 | L | deep-greedy1 ((6, 2, 4, 0), (1, 1, 3, 5)) | 410 | indispensable=355;freed=19 | 355 | 374 | 50.4s | UNSAT |
| 2026-07-25T04:12:14 | S | deep-greedy1 ((6, 2, 4, 0), (1, 1, 3, 5)) | 170 | indispensable=129;freed=7 | 129 | 136 | 45.0s | UNSAT |
| 2026-07-25T04:12:23 | joint | joint-deep1 L((4, 0, 4, 4), (1, 1, 3, 5)) S((12, 2, 2, 0),) | 578 | indispensable=502;freed=-77 | 502 | 509 | 115.3s | UNSAT |
| 2026-07-25T04:12:45 | L | deep-greedy1 ((6, 2, 4, 0), (2, 0, 2, 4)) | 402 | indispensable=363;freed=11 | 363 | 374 | 44.2s | UNSAT |
| 2026-07-25T04:13:06 | S | deep-greedy1 ((6, 2, 4, 0), (4, 0, 2, 2)) | 170 | indispensable=129;freed=7 | 129 | 136 | 51.3s | UNSAT |
| 2026-07-25T04:13:19 | L | deep-greedy1 ((6, 2, 4, 0), (10, 0, 8, 2)) | 410 | indispensable=365;freed=9 | 365 | 374 | 34.0s | UNSAT |
| 2026-07-25T04:13:59 | L | deep-greedy1 ((6, 2, 4, 0), (6, 2, 8, 0)) | 402 | indispensable=359;freed=15 | 359 | 374 | 40.5s | UNSAT |
| 2026-07-25T04:14:13 | S | deep-greedy1 ((6, 2, 4, 0), (6, 0, 4, 6)) | 161 | indispensable=113;freed=23 | 113 | 136 | 66.9s | UNSAT |
| 2026-07-25T04:14:27 | joint | joint-deep1 L((4, 0, 4, 4), (2, 0, 2, 4)) S((12, 2, 2, 0),) | 570 | indispensable=502;freed=-77 | 502 | 509 | 119.2s | UNSAT |
| 2026-07-25T04:15:01 | S | deep-greedy1 ((6, 2, 4, 0), (2, 0, 4, 2)) | 170 | indispensable=129;freed=7 | 129 | 136 | 48.0s | UNSAT |
| 2026-07-25T04:15:02 | L | deep-greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (4, 0, 4, 4)) | 434 | indispensable=347;freed=27 | 347 | 374 | 63.0s | UNSAT |
| 2026-07-25T04:15:55 | S | deep-greedy1 ((6, 2, 4, 0), (12, 0, 2, 6)) | 170 | indispensable=122;freed=14 | 122 | 136 | 54.2s | UNSAT |
| 2026-07-25T04:16:04 | L | deep-greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (2, 0, 2, 4)) | 426 | indispensable=349;freed=25 | 349 | 374 | 62.1s | UNSAT |
| 2026-07-25T04:16:22 | joint | joint-deep1 L((4, 0, 4, 4), (10, 0, 8, 2)) S((12, 2, 2, 0),) | 578 | indispensable=502;freed=-77 | 502 | 509 | 110.5s | UNSAT |
| 2026-07-25T04:16:51 | S | deep-greedy1 ((6, 2, 4, 0), (0, 0, 6, 6)) | 158 | indispensable=124;freed=12 | 124 | 136 | 55.9s | UNSAT |
| 2026-07-25T04:16:53 | L | deep-greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (10, 0, 8, 2)) | 434 | indispensable=355;freed=19 | 355 | 374 | 48.9s | UNSAT |
| 2026-07-25T04:17:45 | joint | joint-deep1 L((4, 0, 4, 4), (6, 2, 4, 0)) S((12, 2, 2, 0),) | 566 | indispensable=491;freed=-66 | 491 | 509 | 80.7s | UNSAT |
| 2026-07-25T04:17:47 | L | deep-greedy2 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0)) | 426 | indispensable=345;freed=29 | 345 | 374 | 54.1s | UNSAT |
| 2026-07-25T04:18:17 | S | deep-greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 2, 2, 0)) | 182 | indispensable=105;freed=31 | 105 | 136 | 86.5s | UNSAT |
| 2026-07-25T04:18:58 | L | deep-greedy3 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0), (4, 0, 4, 4)) | 450 | indispensable=329;freed=45 | 329 | 374 | 70.1s | UNSAT |
| 2026-07-25T04:19:28 | S | deep-greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (1, 1, 3, 5)) | 185 | indispensable=113;freed=23 | 113 | 136 | 71.0s | UNSAT |
| 2026-07-25T04:19:47 | joint | joint-deep1 L((4, 0, 4, 4), (6, 2, 8, 0)) S((12, 2, 2, 0),) | 570 | indispensable=493;freed=-68 | 493 | 509 | 117.6s | UNSAT |
| 2026-07-25T04:20:18 | L | deep-greedy3 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0), (2, 0, 2, 4)) | 442 | indispensable=323;freed=51 | 323 | 374 | 80.1s | UNSAT |
| 2026-07-25T04:20:42 | S | deep-greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (4, 0, 2, 2)) | 185 | indispensable=113;freed=23 | 113 | 136 | 73.9s | UNSAT |
| 2026-07-25T04:21:16 | L | deep-greedy3 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0), (10, 0, 8, 2)) | 450 | indispensable=345;freed=29 | 345 | 374 | 58.5s | UNSAT |
| 2026-07-25T04:21:47 | S | deep-greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (2, 0, 4, 2)) | 185 | indispensable=113;freed=23 | 113 | 136 | 64.3s | UNSAT |
| 2026-07-25T04:21:54 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (6, 2, 4, 0)) | 564 | indispensable=493;freed=-68 | 493 | 509 | 123.8s | UNSAT |
| 2026-07-25T04:22:46 | L | deep-greedy4 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0), (2, 0, 2, 4), (4, 0, 4, 4)) | 466 | indispensable=319;freed=55 | 319 | 374 | 89.7s | UNSAT |
| 2026-07-25T04:23:17 | S | deep-greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6)) | 185 | indispensable=85;freed=51 | 85 | 136 | 90.0s | UNSAT |
| 2026-07-25T04:23:42 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (1, 1, 3, 5)) | 578 | indispensable=504;freed=-79 | 504 | 509 | 102.9s | UNSAT |
| 2026-07-25T04:24:09 | L | deep-greedy4 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0), (2, 0, 2, 4), (10, 0, 8, 2)) | 466 | indispensable=323;freed=51 | 323 | 374 | 83.6s | UNSAT |
| 2026-07-25T04:24:53 | S | deep-greedy2 ((6, 2, 4, 0), (6, 0, 4, 6), (0, 0, 6, 6)) | 173 | indispensable=88;freed=48 | 88 | 136 | 96.4s | UNSAT |
| 2026-07-25T04:25:27 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (4, 0, 2, 2)) | 578 | indispensable=504;freed=-79 | 504 | 509 | 100.9s | UNSAT |
| 2026-07-25T04:25:37 | L | deep-greedy5 ((6, 2, 4, 0), (1, 1, 3, 5), (6, 2, 8, 0), (2, 0, 2, 4), (4, 0, 4, 4), (10, 0, 8, 2)) | 490 | indispensable=319;freed=55 | 319 | 374 | 87.7s | UNSAT |
| 2026-07-25T04:26:49 | S | deep-greedy3 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0)) | 206 | indispensable=77;freed=59 | 77 | 136 | 116.4s | UNSAT |
| 2026-07-25T04:28:22 | S | deep-greedy3 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (1, 1, 3, 5)) | 209 | indispensable=85;freed=51 | 85 | 136 | 92.1s | UNSAT |
| 2026-07-25T04:29:54 | S | deep-greedy3 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (4, 0, 2, 2)) | 209 | indispensable=85;freed=51 | 85 | 136 | 93.0s | UNSAT |
| 2026-07-25T04:30:04 | joint | joint-deep1 L((4, 0, 4, 4), (1, 1, 3, 5)) S((12, 2, 2, 0),) | 578 | indispensable=502;freed=7 | 502 | 509 | 115.5s | UNSAT |
| 2026-07-25T04:31:31 | S | deep-greedy3 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (2, 0, 4, 2)) | 209 | indispensable=85;freed=51 | 85 | 136 | 96.8s | UNSAT |
| 2026-07-25T04:32:08 | joint | joint-deep1 L((4, 0, 4, 4), (2, 0, 2, 4)) S((12, 2, 2, 0),) | 570 | indispensable=502;freed=7 | 502 | 509 | 119.3s | UNSAT |
| 2026-07-25T04:33:12 | S | deep-greedy3 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (0, 0, 6, 6)) | 197 | indispensable=85;freed=51 | 85 | 136 | 100.5s | UNSAT |
| 2026-07-25T04:34:03 | joint | joint-deep1 L((4, 0, 4, 4), (10, 0, 8, 2)) S((12, 2, 2, 0),) | 578 | indispensable=502;freed=7 | 502 | 509 | 110.5s | UNSAT |
| 2026-07-25T04:35:12 | S | deep-greedy4 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (1, 1, 3, 5)) | 230 | indispensable=77;freed=59 | 77 | 136 | 120.2s | UNSAT |
| 2026-07-25T04:35:26 | joint | joint-deep1 L((4, 0, 4, 4), (6, 2, 4, 0)) S((12, 2, 2, 0),) | 566 | indispensable=491;freed=18 | 491 | 509 | 80.8s | UNSAT |
| 2026-07-25T04:37:12 | S | deep-greedy4 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (4, 0, 2, 2)) | 230 | indispensable=77;freed=59 | 77 | 136 | 120.3s | UNSAT |
| 2026-07-25T04:37:28 | joint | joint-deep1 L((4, 0, 4, 4), (6, 2, 8, 0)) S((12, 2, 2, 0),) | 570 | indispensable=493;freed=16 | 493 | 509 | 117.5s | UNSAT |
| 2026-07-25T04:39:08 | S | deep-greedy4 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (2, 0, 4, 2)) | 230 | indispensable=77;freed=59 | 77 | 136 | 115.5s | UNSAT |
| 2026-07-25T04:39:35 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (6, 2, 4, 0)) | 564 | indispensable=493;freed=16 | 493 | 509 | 123.8s | UNSAT |
| 2026-07-25T04:41:01 | S | deep-greedy4 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (0, 0, 6, 6)) | 218 | indispensable=77;freed=59 | 77 | 136 | 112.8s | UNSAT |
| 2026-07-25T04:41:23 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (1, 1, 3, 5)) | 578 | indispensable=504;freed=5 | 504 | 509 | 102.9s | UNSAT |
| 2026-07-25T04:42:58 | S | deep-greedy5 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (4, 0, 2, 2), (1, 1, 3, 5)) | 254 | indispensable=77;freed=59 | 77 | 136 | 117.1s | UNSAT |
| 2026-07-25T04:43:08 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (4, 0, 2, 2)) | 578 | indispensable=504;freed=5 | 504 | 509 | 100.9s | UNSAT |
| 2026-07-25T04:44:56 | S | deep-greedy5 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (4, 0, 2, 2), (2, 0, 4, 2)) | 254 | indispensable=77;freed=59 | 77 | 136 | 118.5s | UNSAT |
| 2026-07-25T04:45:22 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (6, 0, 4, 6)) | 569 | indispensable=493;freed=16 | 493 | 509 | 130.1s | UNSAT |
| 2026-07-25T04:46:53 | S | deep-greedy5 ((6, 2, 4, 0), (6, 0, 4, 6), (12, 0, 2, 6), (12, 2, 2, 0), (4, 0, 2, 2), (0, 0, 6, 6)) | 242 | indispensable=77;freed=59 | 77 | 136 | 117.1s | UNSAT |
| 2026-07-25T04:47:13 | joint | joint-deep1 L((4, 0, 4, 4),) S((12, 2, 2, 0), (2, 0, 4, 2)) | 578 | indispensable=504;freed=5 | 504 | 509 | 106.7s | UNSAT |
| 2026-07-25T04:47:30 | S | deep-final six-orbit pool | 627 | indispensable=77;freed=59 | - | 136 | ~30m | UNSAT |
| 2026-07-25T04:47:30 | L | deep-final six-orbit pool | 625 | indispensable=319;freed=55 | - | 374 | ~25m | UNSAT |
| 2026-07-25T05:14:00 | L | hybrid deep-final, seeds 0/1/2/3 | 625 | core+greedy | - | - | ~32m concurrent | FINAL 524,534,533,529 |
| 2026-07-25T05:19:00 | S | hybrid deep-final, seeds 0/1/2/3 | 627 | core+greedy | - | - | ~32m concurrent | FINAL 525,518,523,521 |

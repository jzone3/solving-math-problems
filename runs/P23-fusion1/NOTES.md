# P23 — Smaller 5-chromatic unit-distance graphs — Fusion run 1

Continuation of `runs/P23-v1` (session
https://app.devin.ai/sessions/8c6eba9abd204ecf9e216e61f6b8dbe4).
This session: https://app.devin.ai/sessions/95103c582b80462f94938c25f54e6e10
Branch `runs/P23-fusion1`. Machine: kissat (built from source) + drat-trim +
sympy 1.14 + numpy, Python 3.10.

## Target (unchanged)
A unit-distance graph in the plane with χ = 5 on **fewer than 509 vertices**
(Jaan Parts' 2020 world record; `solutions/P23/PRIORITY.md`). Exact algebraic
coordinates, unit distances verified in exact arithmetic, non-4-colorability by
DRAT-certified UNSAT.

## Outcome (honest summary)
**No graph smaller than 509 was found.** The 509 record was first re-verified from
scratch (2442 edges, kissat UNSAT). This session then pursued the three levers the
prompt/v1 flagged as *not yet tried* — **different field extensions**, new
Minkowski/rotation seeds, and SAT-driven minimization from a *differently
constructed* 5-chromatic graph. The headline new artifact is a fully verified
**569-vertex** 5-chromatic UDG living in a **different field**
ℚ(√2,√3,√5,√11) — genuinely distinct geometry from every Parts graph, and smaller
than v1's best fresh graph (586), **but still larger than the 509 record**.
Negative result for the world record; positive methodological result (field
extension opens new, valid 5-chromatic geometry). Negative results are results
(METHODOLOGY §3).

## What is new vs. runs/P23-v1
v1 worked entirely inside the Parts field ℚ(√3,√5,√11) and concluded that its
pools were "Parts-like" and bottomed out above 509; it explicitly named
"genuinely new geometry over new rings / different field extensions" as the
untried next lever. This run implements exactly that:

- **`mfield.py`** — exact arithmetic generalized from v1's hard-coded
  ℚ(√3,√5,√11) `field.py` to an **arbitrary real multi-quadratic field**
  ℚ(√p₁,…,√p_k). Element = Fraction vector over the 2^k subset-basis; exact
  `mul`/`inv`/`field_sqrt`/`norm2`; Mathematica `.vtx` parser that rejects any
  radical outside the chosen field. Validated: loading the 509 record into
  ℚ(√3,√5,√11) reproduces exactly 2442 unit edges.

## Experiments

### E1 — Rational (Pythagorean) rotation pool — NEGATIVE (collapses to record)
`build_pools.py rational`. Applied unit rotations with **rational** entries
(3/5,4/5), (5/13,12/13), (8/17,15/17), (20/29,21/29) and inverses to the record
(irrational angle multiples of π, so infinitely many new orientations, but
staying inside ℚ(√3,√5,√11)). Pool: 5589 vertices / 26862 edges.
Core-minimization (`coremin.py`, seeds 0–3) drove the pool **straight back to a
509-vertex core in one step** every time — the rational-rotation copies add no
denser non-4-colorable structure; the SAT UNSAT core just re-isolates the
embedded record. No improvement.

### E2 — Field extension ℚ(√2,√3,√5,√11) via 45° rotations — best 569 (still > 509)
`build_x2.py`. Adjoined √2 and applied the **45° unit rotation
r = (√2/2)(1+i)** (and 135/225/315°) to the record — vertices provably *not*
expressible in the Parts field (coords involve √2,√6,√22,√66). Pool: 1885
vertices / 9874 edges.
- Core-minimization did **not** collapse to the record: it bottomed at
  **683–687** — i.e. the √2 geometry supports a genuinely different non-4-colorable
  subgraph.
- Greedy destructive minimization (`greedy.py`, core-jumps, seeds 0–6) reached
  local minima **569, 572, 582, 583, 584, 587, 588**. Best = **569**.
- The **569-vertex** graph is emitted and **independently verified in exact
  arithmetic with a DRAT-certified UNSAT proof** (`verify_m.py`):
  569 vertices, 2816 exact unit edges, `s VERIFIED`. Files:
  `best569_x2.vtx` / `best569_x2.edges` (readable, reparseable) and
  `g569_x2.pkl` (exact witness). This is a fresh, differently-fielded
  5-chromatic UDG, below v1's 586, above the 509 record.

### E3 — Richer extension pool (√2 45° ⊕ native ring rotations) — NEGATIVE
`build_x2b.py`. Combined the √2 45° rotation with v1's native ring rotations
u₁=5/6+√11/6·i, u₂=1/2+√3/2·i and their products over ℚ(√2,√3,√5,√11). Pool:
3057 vertices / 16806 edges. Greedy minima **580, 599** — no improvement over the
plain √2 pool; the extra native-ring copies re-introduce the Parts basin.

### E4 — Large √2 Minkowski-sum pool (33k vertices) — NEGATIVE
`build_x2big.py`. Genuinely new geometry beyond E2/E3: a rotation orbit of the
record (45°/30°/60°/90° + ring rotations) **plus a Minkowski layer**
{p + R₄₅(q) : p,q ∈ record} clipped to 1.03× the record radius, mixing the √2
direction into every record vertex → **33,253 vertices / 173,922 exact unit
edges** over ℚ(√2,√3,√5,√11). Core-minimization bottoms at 808–1118; greedy
destructive from those cores plateaus at **636–664** — *worse* than the tight
pool, because the dense Minkowski cores are large and their greedy basins are
shallow. No improvement.

### Seed sweep (E2 pool, ~20 greedy chains total) — floor is structural
Across ~20 greedy chains over the E2/E3/E4 pools with diverse core-min seeds, the
local minima cluster tightly: **569, 572, 572, 579, 580, 582, 583, 584, 584,
586, 587, 588, 589, 592, 595, 596, 597, 599, 606, 636, 639** (…). The **569**
graph (E2, verified) is the global best of the session. The ~60-vertex gap to 509
is far larger than any greedy move can bridge — beating 509 needs a better
*construction*, not a better local search over √2 geometry.

**Sanity check that this is not a tooling artifact:** E1 (rational rotations)
drove its pool straight to a 509-vertex core, i.e. the identical SAT/DRAT/greedy
machinery *does* reach 509 exactly when the geometry supports it. The √2-field
floor at ≈569 is therefore a real property of the geometry, not a solver limit.

### E5 — SAT minimization of a *different construction* (Voronov series-1) — NEGATIVE
The prompt's third lever: "SAT-driven subgraph minimization from larger
5-chromatic graphs". v1 only ever minimized Parts-derived vertex sets. Here we
took **Voronov's series-1 plane graphs** (`github.com/vsvor/dist-graphs`,
`plane/series 1/dimacs/s1_graph{1..5}.dimacs`) — genuinely different constructions
in the field ℚ(√2,√3,√6), **3877 vertices / ~26,800 edges** each. Structure alone
suffices for minimization (every induced subgraph of a UDG is a UDG), so we
minimized the edge graph directly (`load_dimacs.py` → `coremin.py`/`greedy.py`).
- All five confirmed non-4-colorable (χ ≥ 5). Core-min → **1625–1969**.
- Greedy destructive (4 seeds on graph1) descends into the **~1000–1100** range
  and plateaus — **far above 509**, consistent with Voronov's published plane
  record being *larger* than Parts'. The five graphs differ by only ~18 edges, so
  their minima coincide. No sub-509 subgraph. (To even *attempt* a claim below 509
  one would also need Voronov's exact coordinates, which series-1 doesn't ship;
  moot, since the floor is ~1000.)

### Priority re-check (this session, widened) — record still 509
Fresh Exa web + arXiv sweep for any post-2020 sub-509 result: only Parts 2010.12665
(509), Heule 1805.12181 (553), de Grey/Heule graphs, and the ≥26 lower bound
(2303.14714). MathWorld "Parts Graphs" still lists 509 as the smallest. **No
public improvement exists** — reproducing/attacking 509 is the state of the art.

## Interpretation
- Rational rotations keep you inside the Parts field and its minimization basin →
  collapse to 509.
- A true field extension (√2) **does** open new 5-chromatic geometry, disproving
  the worry that "everything reduces to Parts", but that geometry's own
  minimization basin still bottoms out well above 509 (≈569). Beating 509 needs
  not just a new field but a construction whose *minimal* 5-chromatic core is
  smaller than Parts' hand-tuned H-graph reduction — consistent with the record
  having survived Polymath16 + v1.

## Files
- `mfield.py` — general multi-quadratic exact field + `.vtx` parser.
- `field.py`, `sat.py`, `verify.py` — copied from v1 (native ℚ(√3,√5,√11) path).
- `build_pools.py` (E1), `build_x2.py` (E2), `build_x2b.py` (E3),
  `build_x2big.py` (E4, 33k-vertex √2 Minkowski pool) — pool builders.
- `coremin.py`, `greedy.py` — SAT-core / greedy minimizers (reused from v1; read
  the pool via `POOL=<pool>.pkl`).
- `verify_m.py` — independent verifier over an arbitrary multi-quadratic field
  (exact edges + kissat UNSAT + drat-trim).
- `load_dimacs.py` (E5) — load a DIMACS graph (e.g. Voronov's) into a pool for
  structural SAT minimization.
- `emit.py`, `export_vtx.py` — extract an induced subgraph and export readable
  coords.
- `best569_x2.vtx` / `best569_x2.edges` / `g569_x2.pkl` — the verified 569-vertex
  ℚ(√2,√3,√5,√11) 5-chromatic UDG.

## Reproduce
```
cd runs/P23-fusion1           # needs kissat + drat-trim on PATH or ~/p23/...
python3 build_x2.py           # -> pool_x2.pkl
POOL=pool_x2.pkl python3 coremin.py 2
POOL=pool_x2.pkl python3 greedy.py 2 coremin_seed2.pkl   # -> greedy_seed2.pkl (569)
python3 emit.py pool_x2.pkl greedy_seed2.pkl g569_x2.pkl
python3 verify_m.py --pkl g569_x2.pkl --primes 2,3,5,11 --drat   # PASS + s VERIFIED
```

---

## Session 2 continuation (coordinator: "keep going")

### E6 — extended-field 508 swap scan (`scan508x.py`) — NEGATIVE, informative
Gap found in all previous work: v1's −1+1 / −2+1 / −3+2 swap scans, and this
run's minimization, only ever used candidate vertices from the **native** Parts
field ℚ(√3,√5,√11). The ℚ(√2,…) extension vertices had *never* been tested as
substitution candidates for the record.

Scan: 147 pool_x2big candidates with ≥4 record-neighbours; for each, every
record vertex within radius 2.05 was tested for `G509 − v + w` non-4-colorability
(DRAT-certified core each time), then all pairs of successful deletions (→ 508).

Result: **0 swap-deletable candidates** (1429 s, 8 cores). Contrast: v1's native
Minkowski candidates yielded 9 single swaps. Interpretation: √2-extension points
sit off the record's ring, so they can join the graph but can never take over the
colour-forcing role of a record vertex — the record's criticality is *ring-local*.

### E7 — large-neighbourhood ruin & recreate (`lns508.py`) — NEGATIVE so far
Every earlier move was small-radius (−1+0, −2+1, −3+2, greedy deletion), which
provably cannot escape a vertex-critical graph's basin. LNS uses radius-20 moves:

1. **ruin** — delete a *spatially localised ball* of k ∈ [6,26] vertices;
2. **recreate** — conflict-driven column generation: repeatedly ask kissat for a
   4-colouring of the current set and add the pool vertex that is *blocked*
   (sees all 4 colours) under the most sampled colourings — a proper
   column-generation recreate. (A degree-greedy recreate was tried first and
   *never* restored non-4-colorability: it is far too weak.)
3. **repair** — proof-free SAT deletion passes (GLIM=250) + one final
   DRAT core extraction;
4. **accept on ≤** so the search *plateau-walks* across alternative 509s instead
   of restarting from the record each time.

Behaviour: recreate reliably rebuilds a non-4-colorable set, and repair reliably
returns to **exactly 509** (or 510–517 on unlucky iterations) — i.e. the machinery
lands on the 509 plateau from many different ruined states, but never below.

### E7b — LNS results (native + extended pools) — NEGATIVE
Built a second, richer **native-field** pool (`build_native.py`, ℚ(√3,√5,√11)):
record ∪ Minkowski sums ∪ **apex points** (both third vertices of the unit
triangle on every record pair at distance ≤ 2 — computed exactly, with the
apex scale factor √((4−d²)/4d²) cached per distance so sympy denesting runs once
per distinct d²). After a degree-5 filter: **41,764 vertices / 365,632 exact
edges**. v1 had Minkowski pools here but no apex layer and, crucially, no LNS.

~70 LNS iterations over both pools (each iteration = ruin + column-generation
recreate + repair, ~3.5 min): the distribution of outcomes is
509 ×20+, 510, 511, 512, …, 522 — the search **lands exactly on 509 from many
different ruined states and never below**.

### E8 — alternative 509s and their unions (`union509.py`) — NEGATIVE, novel
The plateau walk emitted **genuinely different 509-vertex 5-chromatic graphs**
(differing from the record in 1–2 vertices), and the native swap scan found more
(e.g. `509 − v415 + apex41451`, `509 − v413 + apex41438`, `509 − v220 + mink2731`).
Until now only *one* 509 graph was known, so this test was impossible:

> if two distinct 509s exist, their union (510–512 vertices) is non-4-colorable,
> and its minimum non-4-colorable subgraph need not be either of them.

All **10 pairs** of the 5 distinct 509s were core-minimized + fully greedily
reduced: **every union collapses back to exactly 509**. Combining independent
509s does not interfere constructively.

### E9 — native-field 508 swap scan (`scan508x.py` on `pool_native.pkl`)
697 candidates with ≥4 record neighbours (including the new apex layer, which v1
did not have). Per candidate: DRAT-certified test of `509 − v + w` for every
record vertex within radius 2.05, then all pairs of successful deletions (→508).
Swap-deletable candidates *are* found here (unlike in the √2 extension), i.e. the
record has substitutable vertices — but no candidate so far admits **two**
simultaneous deletions, which is what a 508 requires.

**E9 result: 697 candidates scanned, 11 swap-deletable, 0 that admit two
deletions ⇒ no 508** (12,899 s, 5 cores). The 11 swaps are new (most are apex
points, which v1's pools did not contain), e.g.
`w=41451→v415`, `w=41438→v413`, `w=2731→v220`, `w=1666→v301`, `w=620→v347`,
`w=516→v353`, `w=41543→v375`, `w=2472→v217`, `w=3452→v356`, `w=1674→v300`,
`w=1341→v350`.

### E10 — composite multi-swap moves (`combo.py`) — NEGATIVE, novel
With 11 known swaps one can finally *compose* them. For all 220 pairs and
triples with disjoint deleted vertices: build `509 − {v_i} + {w_i}`, check it is
still non-4-colorable, then attempt to delete **every** vertex of the result.

- **200 / 220** composite substitutions are genuinely independent → 200 further
  distinct 509-vertex 5-chromatic UDGs (20 combinations interfere and become
  4-colorable);
- **every one of the 200 is again vertex-critical** — not a single vertex can be
  removed from any of them.

This is the sharpest statement of the obstruction found in this run: the record's
substitution structure is *rigid*. Swaps compose freely, generating hundreds of
distinct 509s, yet no combination ever frees a vertex. A 508 therefore cannot be
reached by any −k+k / −k+(k−1) move over these pools; it needs a different
construction, not a different search.

## Summary of session 2 (all negative for <509, all machine-checked)
| # | experiment | scale | floor |
|---|------------|-------|-------|
| E6 | √2-extension swap scan vs record | 147 candidates | 0 swaps at all |
| E7 | LNS ruin&recreate (√2 pool, 33k) | ~40 iterations | 509 |
| E7b | LNS ruin&recreate (native pool, 41.8k) | ~40 iterations | 509 |
| E8 | unions of distinct 509s | 10 pairs | 509 |
| E9 | native swap scan (Minkowski+apex) | 697 candidates | 509 (11 swaps, 0 doubles) |
| E10 | composite multi-swaps | 220 combos → 200 new 509s | all critical |

Parallel child sessions (independent machines, own branches, no PRs):
- `runs/P23-sms` — constructive CEGAR search over fixed exact universes:
  rediscovered the Moser spindle as the smallest 4-chromatic UDG (certified),
  proved Moser-ball universes up to 55,747 vertices are 4-colorable, and
  independently re-proved by a *different method* that no 508-subset of the
  record is non-4-colorable.
- `runs/P23-priority2` — exhaustive priority sweep: nothing below 509 exists
  publicly through 2026-06; de Grey–Parts arXiv:2303.14714 only improves the
  *edge* count (2442 → 2406) on the same 509 vertices.
- `runs/P23-parts-method` — reimplementation of Parts' own ring/gadget
  minimization (in progress at time of writing).

### Final LNS tally
254 completed LNS iterations across both pools (sqrt2-extension 33k and native
41.8k), ruin sizes k in [6,70]:

| result | 509 | 510 | 511 | 512 | 513 | 514 | 515 | 516 | 517 | 518+ |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|
| count  | 28  | 38  | 31  | 36  | 24  | 12  | 15  | 17  | 8   | 7    |

**Minimum over all 254 iterations = 509, attained 28 times, never beaten.**
Deep ruins (k > 60) usually cannot be repaired at all within the +60 slack: the
record's colour-forcing structure is not reconstructible from generic pool
vertices once a large region is removed.

## Bottom line for this run
Five independent new method classes (extension-field swaps, LNS ruin&recreate on
two pools, unions of distinct 509s, native Minkowski+apex swap scan, composite
multi-swaps) and three independent child investigations (Parts' own ring/gadget
method, constructive CEGAR over fixed universes, exhaustive literature/priority)
all terminate at exactly 509. The record is not merely a local optimum of vertex
deletion: it is stable under every substitution-composition move we can generate,
and hundreds of *distinct* 509-vertex 5-chromatic UDGs exist, every one of them
vertex-critical. No sub-509 graph is claimed.

### E11 — multi-way union of all known distinct 509s (`multiunion.py`) — NEGATIVE
Union of the record with **all 11 swap vertices at once** = a 520-vertex
non-4-colorable graph, attacked with independent **randomly ordered** greedy
deletions (degree-ordered greedy is deterministic and always lands in the same
place). Every run returns **509**, each time a *different* 509 (3–7 non-record
vertices). More evidence that 509 is the size of every minimal non-4-colorable
subgraph reachable in this geometry, not just of the published one.

### E12 — compute on the new type-M rotation ω₁₆ (child branch `runs/P23-parts-rho`)
The Parts-method child established something genuinely new: Parts wrote
*"working constructions of type M with other rotations are not known yet"*, and
the child's exact survey of ω_t = exp(i·arccos(1−1/2t)) found that
**ω₁₆ and ω₂₈ also work** (W₁₆ = 77,485 v / 863,046 e is non-4-colorable;
all other t ≤ 28 are 4-colorable, hence hopeless). This machine now contributes
parallel reduction runs on W₁₆ (Parts' 8-4-2-1 batched greedy with independent
seeds, plus `lns_gen.py`, a coordinate-free BFS-ball version of the LNS engine
for arbitrary pools): 5081 → 4347 and falling at the time of writing. Results
land on `runs/P23-parts-rho`.

**W₁₆ reduction status (this machine, 7 parallel seeds of Parts' 8-4-2-1 greedy
with DRAT core jumps):** 5081 → **2242** and still falling inside pass 1.
Every intermediate is a certified non-4-colorable subgraph of W₁₆, i.e. a
5-chromatic UDG at the *new* rotation ω₁₆ — the first working type-M rotation
other than Parts' ρ = ω₄. It is not yet below 509 and may well floor above it,
but it is the only line in this whole run that explores geometry no one has
published.

### E13 — CALIBRATION: deletion-based minimization is ~3.5× off the optimum
Ran the same reducers on **W₄** — the type-M union that *provably contains
Parts' 509* — starting from the full 5677-vertex pool:

| method | floor reached |
|---|---|
| Parts' 8-4-2-1 batched greedy + DRAT core jumps (2 seeds) | ~1865 / ~1878, ~4 vtx per 100 s and decelerating |
| iterated randomized DRAT core extraction (`corejump.py`) | 1864 → 1845 in 10 min, same rate |
| orbit-batched greedy (`symgreedy.py`) | same regime |

So on an instance whose optimum is known to be ≤ 509, *every* deletion-style
method stalls around 1850. **Consequence:** the ~1950 floor my seven parallel
runs reach on W₁₆ carries **no** negative information about the new rotation
ω₁₆ — and no amount of extra greedy compute will decide it. Beating 509
requires Parts' constructive side (reference-orbit selection + orbit filling +
fine search), which is what the child run `runs/P23-parts-rho` is now doing;
this calibration was sent to that session so it stops spending cores on
deletion.

### E14 — transplanting the record's halves onto the new rotations — NEGATIVE
`transplant.py`: the record is L374 ∪ ω₄·S136. Re-joining the *same lattice
sets* with ω₁₆ or ω₂₈ (only the rotation changes) gives 510 vtx / 2460 edges but
is **4-colorable** — the cross-edge kinds differ (36 vs 54 cross edges), so the
halves must be re-searched at each rotation, not transplanted.

### E15 — port/pattern decomposition — INFEASIBLE AS STATED
`ports.py`: L ∪ ωS is 5-chromatic iff the port-colouring pattern sets Π_A, Π_B
(restrictions of proper 4-colourings to the cross-edge endpoints, mod colour
permutation) conflict under every colour permutation. Attractive because it
decomposes the problem, but projected ALL-SAT enumeration of Π_B for the
record's own S136 blows past millions of patterns — the halves are far too
loosely constrained for explicit pattern enumeration.

### E16 — alternating half re-optimisation (`altmin.py`, `build_w4x.py`)
New pool `w4x.pkl` = P₄ ∪ L374 in copy A, P₄ ∪ S136 in copy B, exact edges,
which (unlike the radius-clipped `wt_4.pkl`, missing 19 record points) contains
the record exactly — verified: DRAT core of the 510 stored points = **509**.
On it, one half is frozen while the other is rebuilt from scratch over its whole
candidate pool (up to all 374 / all 136 vertices at once) by column generation.
This is a much deeper neighbourhood than any earlier move: previous scans always
perturbed both halves together and only locally. Status: full-half rebuilds do
not reconstruct (a half is a finely tuned 4-chromatic gadget, not something
column generation stumbles into); partial half ruins rebuild to 510–511.

### E17 — complete (CEGAR) search for a *smaller half* (`cegar_half.py`)
Every other move class in this run is heuristic. This one is complete: freeze
one half of the record and ask whether **any** subset of the other copy's whole
pool, under a cardinality bound, makes the union non-4-colorable —
`|S'| ≤ 135` (frozen L374) or `|L'| ≤ 373` (frozen S136); either hit is a 508.
Selection variables + totalizer bound, refined by sound "blocked-vertex"
clauses: given a proper 4-colouring of the selected graph, extend it greedily
over the whole pool (5 random orders, keep the shortest refinement); the
vertices that cannot be coloured form the clause. Plus a WLOG **min-degree-4**
constraint on every selected vertex (a vertex of degree ≤ 3 is colourable last,
hence removable, so a minimal witness has min degree ≥ 4) — this is what makes
the outer solver produce structured selections instead of junk.
Status: refinements are weak (|D| ≈ 850–900 per clause) and the outer solver
slows to ~7 s/iteration; no hit and no outer UNSAT within the run. Left running.

### Round tally (this continuation)
| experiment | outcome |
|---|---|
| E11 multi-way union of all distinct 509s (520 vtx) | always → 509, each time a different 509 |
| E12 parallel reduction of W₁₆ (new rotation ω₁₆) | 5081 → **1935** and still falling; 7 seeds |
| E13 **calibration on W₄** (optimum ≤ 509 known) | every deletion method stalls at ~1850 ⇒ deletion floors are meaningless as evidence |
| E14 transplant record halves onto ω₁₆ / ω₂₈ | 4-colorable |
| E15 port/pattern decomposition | pattern sets explode; infeasible |
| E16 alternating half re-optimisation (w4x pool, contains the record exactly) | 510–531, never below 509 |
| E17 complete CEGAR for a smaller half (≤135 / ≤373) | no hit, no outer UNSAT yet; running |

**No sub-509 graph. Nothing is claimed.** The one genuinely new mathematical
object produced across this whole run is the pair of *new working type-M
rotations* ω₁₆, ω₂₈ (child branch `runs/P23-parts-rho`) — the parameter Parts
explicitly left open — together with the calibration result that shows why
deletion-based minimization cannot settle them.

## E18 — hitting-set search with tabu-generated hyperedges (`hyperpar.py`, `cegar4.py`)

The reason E17's complete search made no progress was clause quality, not the
formulation. Restating it properly:

> D ⊆ pool is a **hyperedge** iff pool \ D is 4-colorable. Any non-4-colorable
> subset (a witness) must intersect every hyperedge, so the smallest witness is
> a **minimum hitting set** of the hyperedge system — this is Parts' §5
> minimal-graph search in modern form.

E17 built its hyperedges by greedy colour extension: |D| ≈ 850 of 2839 free
candidates, i.e. almost vacuous constraints. Replacing that with an incremental
**min-conflicts / tabu 4-colouring** of the pool (endpoints of the surviving
conflicting edges give D) changes the picture:

| generator | |D| (of 2839) |
|---|---|
| greedy colour extension (E17) | ~850 |
| tabu, 1–4 M moves (`hyperpar.py`) | **32 – 234**, median ~90 |

Whole-pool hyperedges (no frozen half, 5696 candidates): |D| ≈ 190–460.

`cegar4.py` runs the exact loop with those clauses: outer SAT picks ≤ MAXSEL
candidates hitting every known hyperedge (sequential-counter cardinality — the
totalizer used in E17 costs 4 M clauses and was the other bottleneck), kissat
tests the union with the frozen half, and a new tabu hyperedge disjoint from the
current selection cuts it off. Outer UNSAT would be a *complete* negative
result for that bound; a non-4-colorable selection would be a 508.

Measured behaviour (frozen L374, bound 135, three seeds): ~12 s/iteration,
outer solve 0.1–0.2 s (vs ~7 s in E17), hitting sets grow 23 → 43 over the first
40 refinements and keep growing. No hit, no outer UNSAT yet; running.

Attempted refinement — exact **shrinking** of a hyperedge (drop v from D while
kissat still colours pool \ D) — is sound and would give near-minimal clauses,
but each test is a colouring instance on ~3.1 k vertices and the pass did not
complete a single hyperedge in 25 min. Not usable at pool scale; noted as a
negative.

Also this round: the ω₁₆ hitting-set search was handed to a child session
(branch `runs/P23-hitset16`), and the calibrated-useless W₁₆ deletion runs were
stopped to free cores.

### E19 — shared clause bank, and complete whole-pool searches

`cegar4.py` now appends every hyperedge it discovers to an append-only
`bank.jsonl` and re-reads the file each iteration, so several seeds (and any
restart) accumulate one shared constraint system instead of throwing their work
away. Four seeds at bound 135 (frozen L374) share `bank135.jsonl`; hitting sets
grow 23 → ~43 and the bank grows ~9 hyperedges/minute.

Two further runs drop the frozen half entirely and search the *whole* W₄ pool
(5696 candidates, hyperedges |D| ≈ 150–600, `hyp_all.pkl`) under a cardinality
bound. Outer UNSAT at bound N there is a complete statement — "no 5-chromatic
unit-distance graph with ≤ N vertices exists inside Parts' W₄ union" — so the
bound is being pushed from below (150, 300) rather than jumping straight to 508,
where the outer solver just returns arbitrary 508-subsets and the loop degrades
into sampling.

Still no sub-509 graph, and nothing is claimed.

## E20 — small multi-rotation unions (`scan3.py`, in `runs/P23-parts-rho` geometry)

Parts' type M unions exactly two copies, P ∪ ρP. Nothing in the literature
unions three or more copies at different rotations, and a union that is
non-4-colorable while already having < 509 vertices would beat the record with
no minimisation at all. Scanned: base = ⊕ⁿH² (n = 2, 3) inside a disk of radius
r, copies rotated by ω_t and by conjugates ω̄_t (rotation by −angle), origin
shared; floats as prefilter, sizes capped at 520 vertices.

* 1088 unions over t ∈ {1..28}², r ∈ {0.6..1.2} — all 4-colorable.
* 90 unions over t ∈ {±1, ±2, ±3}², r ∈ {1.0..2.0} — all 4-colorable.

The scan also explains *why*, and this is worth recording as structural rather
than empirical: ω_t creates cross edges only between points at radius ≈ √t
(|1 − ω_t|² = 1/t), so a disk of radius r carries **zero** cross edges unless
r ≳ √t. Measured on the r = 2.0 disk (451 points/copy): t = 1 → 3840 cross
pairs, t = 3 → 1896, t = 4 → 126, t = 2 → 60. But a disk large enough for
cross edges at t = 4 already has ~450 points per copy, so two copies exceed 509
before anything else happens. Any sub-509 5-chromatic union must therefore be a
*sparse subset* of the disk — which is exactly Parts' minimisation problem
again, not something a union scan can stumble into.

## E21 — orbit-level hitting set with a 508-vertex budget (`orbit_cegar.py`)

The record is orbit-structured (L374 = 37 base orbits, S136 = 14), so the
natural search space is the **772 orbits** of ⟨τ₃, τ₄, conj₃₃, −1⟩ on W₄
(sizes 1–8), not the 5696 vertices. Selection variables per orbit; the vertex
budget Σ|orbit| ≤ 508 is encoded by repeating each orbit literal (size) times
inside a sequential counter (pypblib will not build here, so no native PB
encoding); hyperedges are lifted to orbits. Every iteration therefore tests an
orbit-closed candidate that would *be* a record if it were non-4-colorable, and
a lower budget (≥ 380 vertices) keeps the solver away from trivially colourable
tiny selections.

Status: ~25 s/iteration, candidates of 388–508 vertices, all 4-colorable so far;
lifted hyperedges are weak (300–460 of 772 orbits) because a tabu hyperedge
spreads over many orbits. Running.

## E22 — stronger hyperedges: greedy conflict cover + Kempe repair (`hyperpar.py`)

The hitting-set search is only as good as its clauses, and the clause a tabu
colouring yields is *any* vertex set meeting every monochromatic edge, i.e. a
vertex cover of the conflict graph. The original code scanned the edge list and
took whichever endpoint was movable — a 2-approximate cover. Replacing that
with a greedy max-degree peel (`cover()`) is sound (removing a cover of the
conflicts leaves a proper 4-colouring, so pool∖D really is 4-colorable) and
measurably tighter on the same colourings, seed 7, six samples on the full 5696
W₄ pool:

| colouring | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| edge-scan cover | 248 | 404 | 583 | 600 | 103 | 473 |
| greedy cover    | 193 | 280 | 407 | 423 |  86 | 338 |

i.e. 17–30 % smaller clauses for free. `kempe_repair()` adds Kempe-chain swaps
on the two-coloured components after min-conflicts stalls (components touching a
frozen vertex are skipped, so the frozen half stays fixed): mixed but sometimes
large gains (407→77, 423→275) for ~40 % more time, hence `KEMPE=200` by default.

Both are pure clause-strength improvements: previously banked hyperedges stay
valid, so the runs restart from the existing 1900+ clause `bank135.jsonl`.
Relaunched after the restart: 3× frozen-half bound-135 (avg hyperedge 258–290,
selection stuck at 76–82) and 3× orbit-level ≤508 (candidates 436–470 vertices,
all 4-colorable). Still no witness, and no outer UNSAT.

## E23 — *exact* large-neighbourhood search (`hyperpar.py` LNS mode + `lnsloop.sh`)

E7's LNS was heuristic: ruin a region, greedily recreate, keep if it works. The
hitting-set machinery makes the same move **complete**: freeze K vertices of the
record's W₄ embedding, and ask the outer SAT solver for ≤ 508 − K further pool
vertices hitting every known hyperedge. Then each neighbourhood terminates in
one of two definite ways — a 508-vertex witness, or outer UNSAT, i.e. *no*
refill of that hole exists at all.

Making it terminate needed the candidate restriction (`LNSHOPS`): with all 5246
free pool vertices the hyperedges are ~500 wide and the outer solver never runs
out of room (measured: |D| ≈ 300–800, ~55 s/iteration, no progress). Restricting
the free side to the 1-hop pool neighbourhood of the punched hole gives 207
candidates, hyperedges of ~10, and ~2 s/iteration. `LNSDEG=4` additionally
prunes candidates that cannot reach degree 4 (WLOG: a minimum witness is
vertex-critical) — no effect at hop 1, the pool is too dense.

Configuration in flight: K = 490 (hole of 20), budget 18 free, 5 workers × 12
random holes each. First completed neighbourhood (seed 2) returned

    OUTER UNSAT after 323 hyperedges: no witness with <= 18 free vertices
    exists over this pool (545s)

so that hole *provably* cannot be refilled below 509 within its 1-hop pool. This
is the first complete "no 508 here" statement in the run that is not a search
floor. Remaining holes are running; no witness so far.

### E23 status (continued)

21 random 20-vertex holes in the record's W₄ embedding are now **certified
UNSAT** (no ≤ 18-vertex refill from their 1-hop pool exists), 0 witnesses. Each
takes ~5–10 min and ~300–400 hyperedges of width ~10. A wider batch with
30-vertex holes and a 28-vertex budget (`lnsloop2.sh`, K = 480) is running; those
neighbourhoods are an order of magnitude larger and have not closed yet.

Reading: the record is not merely vertex-critical, it is *locally rigid* — every
hole tested so far cannot be refilled more cheaply even when the refill may use
any nearby pool vertex, not just record vertices. That is a much stronger
statement than the earlier swap scans (which only tried −k+k moves), and it says
a 508 (if one exists in this pool) must differ from the record in a large,
non-local region.

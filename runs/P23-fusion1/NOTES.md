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

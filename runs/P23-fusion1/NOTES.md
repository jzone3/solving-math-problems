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

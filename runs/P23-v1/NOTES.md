# P23 — Smaller 5-chromatic unit-distance graphs — Run v1

Session: https://app.devin.ai/sessions/8c6eba9abd204ecf9e216e61f6b8dbe4
Machine: 8 cores, 31 GB RAM. Tools: kissat (built from source), drat-trim, sympy 1.14, Python 3.10.

## Target
A unit-distance graph in the plane with χ = 5 on **fewer than 509 vertices** (Parts' 2020
world record; see `solutions/P23/PRIORITY.md`). Any such graph, with exact algebraic
coordinates + verified unit distances + DRAT-certified non-4-colorability, would be a new
world record.

## Outcome (honest summary)
**No graph smaller than 509 was found.** The 509 record was *reproduced and independently
re-verified from scratch* in exact arithmetic with a DRAT-certified UNSAT proof (a clean
result in itself — the Geombinatorics paper is paywalled and this is a fully open,
machine-checkable reconstruction). A substantial minimization attack (core-based reduction,
greedy destructive deletion, plateau/swap search, and new exact-coordinate vertex generation)
did not beat 509. As of the priority sweep, the record has stood since 2020 and Polymath16
threw major effort at exactly this minimization, so a negative result over a single session
is the expected outcome. **Negative results are results** (METHODOLOGY §3).

## The exact-arithmetic field (`field.py`)
Parts' coordinates live in ℚ(√3, √5, √11) (the individual `.vtx` files use
√3, √5, √11, √15, √33, √55, √165, √(11/3), and nested radicals like √((5(7+√33))/2)).
`field.py` represents an element as an 8-tuple of `Fraction`s over the basis
(1, √3, √5, √15, √11, √33, √55, √165), indexed by a 3-bit mask over primes (3,5,11).
- `parse_expr` uses sympy's Mathematica parser + `sqrtdenest`/`radsimp` to denest nested
  radicals into this basis, then **cross-checks the reconstruction against the original
  sympy expression exactly** (`to_sympy(out) - e` simplifies to 0) before returning.
- `mul`, `inv` (8×8 exact linear solve), `field_sqrt` (denest + square-back check) are exact.
- No floating point anywhere in the *decision*; `to_float` is used only as a prefilter for
  the O(n²) edge scan (candidate pairs are then confirmed with exact `norm2 == 1`).

## Verification of the 509 record (STEP 1, done)
`solutions/P23/verify.py solutions/P23/v509e2442.vtx --edges solutions/P23/v509e2442.edges --drat`
- [1] 509 vertices parse to exact algebraic numbers, all distinct.
- [2/3] exact recomputation of the unit-distance edge set = 2442 edges, matches the claim.
- [4] kissat: the direct 4-coloring CNF (2036 vars, 13331 clauses) is **UNSAT** (107 s) ⇒ χ ≥ 5.
- [4b] **drat-trim independently VERIFIED** the UNSAT proof: `s VERIFIED`
  (11342/13331 clauses in core; transcript in `solutions/P23/drat509_verification.log`).
The gzipped CNF is stored (`solutions/P23/g509_4color.cnf.gz`, 48 KB); the DRAT proof is 170 MB
so it is regenerated on demand (`kissat -q g509_4color.cnf proof.drat && drat-trim g509_4color.cnf proof.drat`, ~4 min total).

We also confirmed the 509 graph is **vertex-critical**: deleting *any single* vertex yields a
4-colorable graph (509/509 single-deletions returned SAT; `scan_del1` in this run). This is
exactly why the record is hard to shrink and why a smaller graph must be a genuinely different
construction, not a subgraph.

## STEP 2 — the attack (all negative)

### Pool construction
- Loaded all 43 Parts graphs (509 + subgraphs + mono/non-mono families) and took the union of
  distinct vertices → **1577 vertices, 9417 unit edges** (`union.pkl`).
- Generated **new exact-coordinate candidate vertices** by intersecting unit circles: for
  every pool pair at distance d < 2, the two apex points completing a unit-unit isosceles
  triangle were computed *exactly* (`field_sqrt` of (4−d²)/(4d²), denested into the field),
  keeping the 4255 apex points hit by ≥ 3 pairs. 4248 survived exact construction (7 apexes
  needed a radical outside ℚ(√3,√5,√11) and were dropped). Enriched pool: **5825 vertices,
  46408 edges** (`pool2.pkl`).

### Minimizers (all verified by DRAT core extraction — `coremin.py`)
Every UNSAT certificate is produced by kissat and **checked by drat-trim** (`-c` core
extraction); the surviving core drives the next reduction, so every reported subgraph is a
genuinely non-4-colorable unit-distance graph.

1. **Core-based reduction** (`coremin.py`): iterate "solve → keep drat-trim UNSAT core" from
   the full pool. From the 1577-pool it stabilizes around 785–796 vertices; from the 5825-pool
   around 1048–1087 (larger because the pool is denser).
2. **Greedy destructive** (`greedy.py`): repeatedly try deleting each vertex; keep the drat-trim
   core when the remainder is still UNSAT. Best local minima reached:
   - from union-pool cores: **586** (seed 6), 604, 605, 607, 611 vertices.
   - from enriched-pool / augmented-509 seeds: 638, 654, 662, 678, 691.
   All are valid 5-chromatic UDGs (the 586 one is emitted + fully re-verified:
   `runs/P23-v1/best586.vtx`, `best586.edges` → `verify.py` prints **PASS**), but all > 509.
3. **Plateau / swap search** (`plateau.py`): fixed-size random walk seeded at the 509 record —
   delete one vertex, add a pool vertex with ≥ 3 neighbours, require still-UNSAT, and probe
   pure deletions to 508. Thousands of steps (6000+ per seed) never left size 509 and never
   found a valid deletion — consistent with vertex-criticality.
4. **Targeted 508 search** (`scan508.py`): for each enriched-pool vertex w (≥ 4 neighbours in
   the record), test swaps 509 − v + w for v near w; collect swap-deletable v's and test pair
   deletions 509 − v₁ − v₂ + w for a 508-vertex UNSAT graph. Ran over all 697 candidate w's:
   **zero swap-deletable vertices, no 508 graph.**

## Why 509 was not beaten
- The record is vertex-critical, so no subgraph of it works; a smaller graph needs a new
  Minkowski-sum / ring construction, not local surgery on the 509 graph.
- Parts' graph was itself the endpoint of ~1000 laptop-hours of a bespoke minimization method
  ("H-graphs", devirtualization of bichromatic virtual edges over the rings Rₙ = ℤ[ω_{t}]),
  refined by the whole Polymath16 community; matching it with generic SAT-core minimization in
  one session was not expected to suffice.
- Our enriched pool is built from Parts' own vertex families, so the reachable local minima are
  "Parts-like" and bottom out above 509; genuinely new geometry (new Loeschian ring generators,
  larger √t apex angles) would be the next lever.

## Files
- `field.py` exact ℚ(√3,√5,√11) arithmetic + Mathematica `.vtx` parser + exact edge finder.
- `sat.py` 4-colouring CNF encoding + kissat driver.
- `verify.py` standalone independent verifier (also copied to `solutions/P23/`).
- `coremin.py` / `greedy.py` / `plateau.py` / `scan508.py` the minimization attack.
- `best586.vtx` / `best586.edges` a fresh, fully re-verified 586-vertex 5-chromatic UDG
  (a distinct graph produced by our pipeline; demonstrates the toolchain end-to-end, > record).

## Reproduce
```
cd runs/P23-v1                      # (needs kissat + drat-trim on PATH or ~/p23/…)
python3 verify.py ../../solutions/P23/v509e2442.vtx \
        --edges ../../solutions/P23/v509e2442.edges --drat   # record, PASS + s VERIFIED
python3 verify.py best586.vtx --edges best586.edges          # our 586-graph, PASS
```

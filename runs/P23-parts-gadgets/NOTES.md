# P23 — Gadget / virtual-edge / devirtualization route — Run parts-gadgets

Session: https://app.devin.ai/sessions/3e96bdc990bf49cba80073f78851cd5f
Branch `runs/P23-parts-gadgets`. Machine: 8 cores, 31 GB RAM; kissat + drat-trim
built from source; Python 3.10, exact rational arithmetic only (`fractions.Fraction`).

## Scope

Complementary to `runs/P23-v1` (monolithic 509-graph minimization, exhausted) and
`runs/P23-fusion1` (field extensions): can a 5-chromatic UDG **below 509 vertices** be
ASSEMBLED from minimized gadgets — mono-pairs, non-mono-pairs, non-mono-triples
(Parts arXiv:2010.12665, types A/J vs the monolithic type M), via
spindling / clamping / devirtualization (Polymath16 wiki)?

## Outcome (honest summary)

**No. No sub-509 assembly exists within reach of the known gadget menu, and we prove
sharp structural obstructions.** Headline results:

1. **Exact lattice arithmetic reproduced** (`lattice.py`): vertex = integer 4-tuple
   (a,b,c,d), z = (a + b√33 + i(c√3 + d√11))/12, a−b+c+d ≡ 0 (mod 4); unit distance
   ⟺ a²+33b²+3c²+11d² = 144 ∧ ab+cd = 0 (pure integers; derived and machine-checked;
   H² = V31 comes out with exactly 31 vertices / 60 edges).
2. **Gadget minimization reproduced** from ⊕ⁿH^m pools with SAT (kissat) +
   drat-trim UNSAT-core + greedy core-jump deletion (`gadget.py`, `run_gadget.py`).
   Sizes reached (vs Parts' Table 1, obtained with his far stronger exhaustive
   hyperedge machinery):

   | gadget | Parts | this run | gap |
   |---|---|---|---|
   | non-mono-triple √7      | 159 | **188** | +18% |
   | non-mono-triple √3      | 221 | **343** | +55% |
   | non-mono-triple √(5/3)  | 250 | **263** | +5% |
   | non-mono-triple √5      | 265 | 516 (bad basin) | |
   | non-mono-triple 1/√3    | 265 | **319** | +20% |
   | non-mono-pair 3         | 214 | **324** | +51% |
   | non-mono-pair √(11/3)   | 308 | **516** | +68% |
   | mono-pair 8/3           | 367 | **548** | +49% |

   Gaps are expected: Parts used months of exhaustive local restructuring with
   isomorph rejection; our generic DRAT-core + greedy core-jump (a few CPU-hours)
   still lands the same order of magnitude and every graph is exactly verified.
   The comparison table uses PARTS' (smaller) sizes for all assembly floors, so
   the negative conclusions below are conservative.

   Every emitted gadget passes `verify_gadget.py`: distinct exact vertices, stored
   edges == exact strict-UDG recomputation, the bare graph is 4-colorable (property
   non-vacuous), property-refutation CNF UNSAT with **drat-trim `s VERIFIED`**.
3. **Sharp obstruction to in-lattice spindles (types J and A).** The lattice contains
   exactly 6 difference vectors of length 8/3 and 14 of length 8/√3 (the two known
   mono-pair distances; 20 vectors total). Exhaustive exact enumeration
   (`assembly.py` + chain scripts) of ALL chains of k = 2, 3, 4 mono-vectors shows:
   the chain endpoint-distance² is **never rational except 64/9 itself** — in
   particular never 1 (unit closing edge) and never any non-mono gadget distance
   (3, 7/3, 5/3, 1/3, √(11/3)). Hence **no type-J/A cycle closes inside the
   lattice**: any spindle must rotate one gadget copy by an off-field angle.
4. **Off-lattice spindles share exactly one vertex.** The 8/3 spindle rotation has
   cos θ = 119/128, sin θ = 3√247/128 with √247 ∉ ℚ(√3,√11): if p ≠ 0 and both p and
   rp lie in the field, then r = (rp)·p̄/|p|² would be in the field — contradiction.
   So the two copies overlap in exactly the pivot, and the type-J floor is
   **2·367 − 1 = 733 > 509** with Parts' own minimal mono-pair (2·421−1 = 841 for
   8/√3; mixed 367+421−1 = 787). To beat 509 this way one would need a mono-pair
   gadget of ≤ 254 vertices — 113 below Parts' record gadget.
5. **Explicit end-to-end assembly.** We built the spindle G = M ∪ rM from our
   minimized mono-pair gadget in exact arithmetic over ℚ(√3,√11,√13,√19)
   (`build_spindle.py`, `mfield.py`): overlap exactly 1, closing edge exactly unit,
   4-coloring CNF UNSAT with drat-trim `s VERIFIED` — a valid 5-chromatic UDG of
   **1095 = 2·548 − 1** vertices (`spindle_union.pkl`), our smallest assembled
   graph. Overlap of the two copies was computed exactly and equals 1, matching
   the field-theoretic prediction. With Parts' 367-vertex gadget the same route
   gives 733 — still 224 above the 509 record.
6. **Same-pair composition is empty.** A distance d admitting BOTH a mono-pair and a
   non-mono-pair gadget would give a 5-chromatic union with massive overlap. Scan of
   ~30 lattice-representable distances (`scan_property.py`, pools up to ⊕⁴H², 8251
   vertices, pool verified 4-colorable so the tests are non-vacuous): the ONLY mono
   distance found is 8/3 (and per Parts 8/√3 in larger pools); **no distance admits
   both properties** (nonmono at 8/3 explicitly fails even on the ⊕⁴H² pool).
7. **Clamping/devirtualization accounting** (`virtual_scan.py`): none of the natural
   small hosts (H¹, H², ⊕²H¹, ⊕²H²) has a virtual edge at any gadget distance, so the
   smallest known virtual-edge host remains Exoo–Ismailescu's G₄₀/G₇₉ (arXiv:1805.00157):
   G₇₉ forces a mono √(11/3) pair among its **118** √(11/3)-edges. Clamping Parts'
   308-vertex non-mono-√(11/3) gadget on all of them costs naively
   79 + 118·306 = 36,187 vertices; even 95% overlap between the in-lattice gadget
   copies leaves ≈ 1,900. The wiki's caveat ("clamping has no benefit unless
   nontrivial points overlap") cuts the other way here: maximal overlap means all
   copies collapse into one lattice patch — which is exactly the monolithic type-M
   minimization already exhausted at 509 by Parts and by runs/P23-v1.
8. **Multiplicative property is a size explosion.** Scaling gadget H₀ by d₁ turns
   every unit edge of H₀ into a d₁-edge that must itself be devirtualized by a
   d₁-gadget: |H₂| ≈ |H₀| + |E(H₀)|·(|H₁|−2) — thousands of vertices for any known
   gadget pair. Useful for existence proofs of new virtual-edge lengths, never for
   minimization below 509.

## Assessment

The gadget/devirtualization route cannot beat 509 with anything resembling the known
gadget menu:
- the two known mono distances live on only 20 lattice vectors whose chain-sums never
  return to any gadget-closable distance (exhaustive, exact, k ≤ 4);
- off-lattice closures provably share a single vertex, giving a 733 floor for type J;
- no distance admits mono+non-mono simultaneously in pools up to ⊕⁴H²;
- clamping multiplies, not divides, vertex counts unless the copies collapse into a
  single lattice patch — which reduces to the exhausted monolithic minimization.

A sub-509 gadget assembly would need a qualitatively new gadget: a mono-pair on ≤ 254
vertices, or a mono distance whose lattice vector class supports unit-closing chains.
Our scans (30 distances, both properties) found neither. The smallest exactly-verified
5-chromatic UDG remains Parts' 509 (`solutions/P23/`, re-verified by runs/P23-v1).

## Files

- `lattice.py` — exact integer/rational lattice arithmetic, H^m, Minkowski sums,
  τ-symmetries, exact unit-edge scan (float prefilter only).
- `pools.py` — ⊕ⁿH^m pool builder, exact clipping, placement search
  (`find_radius_points`, `equilateral_triples`).
- `gadget.py` — property CNFs (mono via WLOG two fixed colors; non-mono via WLOG one
  fixed color), kissat driver, drat-trim core reduction, greedy core-jump minimizer.
- `run_gadget.py` — per-gadget minimization runner (placement orbits tried in turn).
- `scan_property.py` — mono/non-mono existence scan over ~30 distances.
- `assembly.py` — in-lattice cycle enumeration (type J/A closings).
- `virtual_scan.py` — virtual-edge host scan and clamping cost accounting.
- `build_spindle.py`, `mfield.py` — exact off-lattice spindle assembly over
  ℚ(√3,√11,√13,√19) + full verification.
- `verify_gadget.py` — independent gadget verifier (exact edges + SAT/DRAT).
- `gadget_*.pkl` — minimized, verified gadget graphs. `spindle_union.pkl` — the
  assembled 5-chromatic spindle. `logs/` — full run logs.

## Reproduce

```
cd runs/P23-parts-gadgets            # needs kissat + drat-trim in ~/p23/
python3 lattice.py                   # arithmetic sanity (H^2 = 31 vtx / 60 edges)
N=3 M=2 R2=4 DEGMIN=4 SEED=2 python3 run_gadget.py triple 7/3   # 188-vertex sqrt7 triple
python3 verify_gadget.py gadget_triple_7_3_seed2.pkl            # PASS + s VERIFIED
python3 assembly.py                  # 0 in-lattice spindle closings
python3 build_spindle.py gadget_monopair_64_9_seed1.pkl        # explicit 5-chromatic spindle
```

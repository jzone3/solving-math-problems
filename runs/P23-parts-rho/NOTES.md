# P23 — Type-M rotation parameter survey (Parts' rho = omega_4 vs all other omega_t)

Session: https://app.devin.ai/sessions/fa0f7a443b49448aaa447cb110c27f94
Branch `runs/P23-parts-rho`. Machine: 8 cores, 30 GB RAM; kissat + drat-trim built
from source, Python 3.10 + numpy + sympy.

## Scope

Parts (arXiv:2010.12665, the 509-vertex record) writes about type M — the
construction that holds the record (G509 = L374 ∪ ρ·S136, one shared vertex):

> "In the original the rotation multiplier is ρ = exp(i arccos(7/8)) ...
>  Working constructions of type M with other rotations are not known yet."

This run enumerates the rotation parameter Parts did not: the Polymath16 family
ω_t = exp(i arccos(1 − 1/(2t))) = (2t−1 + i√(4t−1))/(2t), t ∈ ℕ.
ω_t turns a lattice pair at radius √t into a unit-distance pair
(|1 − ω_t|² = 1/t). Parts' ρ is exactly ω_4.

Prior runs (`runs/P23-v1`, `runs/P23-fusion1`) are honest negatives via vertex
surgery / field extensions / other constructions; none touched the type-M
rotation parameter. Their experiments are NOT repeated here.

## Exact arithmetic (`lattice.py`)

Every base-graph vertex is an integer 4-tuple (a,b,c,d) ≙
z = (a + b√33 + i(c√3 + d√11))/12, with a−b+c+d ≡ 0 (mod 4) (Parts' h=1
lattice). 144|z|² = N + M√33 with N = a²+33b²+3c²+11d², M = 2(ab+cd); a unit
distance is the pure-integer condition N(Δ) = 144 ∧ M(Δ) = 0.

Cross edges u — ω_t v: with w = u·conj(v) = ((P+Q√33) + i(R√3+S√11))/144 and
4t−1 = e·s² (e squarefree),

```
e generic: R=0 ∧ S=0 ∧ t(N1+N2)−(2t−1)P = 144t ∧ t(M1+M2) = (2t−1)Q
e = 3    : t(N1+N2)−(2t−1)P−3sR = 144t ∧ t(M1+M2)−(2t−1)Q−sS = 0
e = 11   : t(N1+N2)−(2t−1)P−11sS = 144t ∧ t(M1+M2)−(2t−1)Q−sR = 0
```

— pure integers, no floats in any decision (floats only as an O(n²) prefilter,
tolerance 1e-6, then exact confirmation).

**Native rotations.** ω_t stays inside ℚ(√3,√11) iff 4t−1 = 3s² (t = 1, 7, 19,
37, …) or 11s² (t = 3, 25, …); these map the lattice into itself (integer
matrices /2t, `omega_native_matrix`). For all other t the second copy lives in
a genuinely rotated lattice; the field of the union is ℚ(√3, √11, √(4t−1)) —
for t=4 that is ℚ(√3,√5,√11), matching the published witness. (4t−1 = 33s² is
impossible: 33s² ≡ 1 mod 4 for odd s, but 4t−1 ≡ 3.)

**Validation against the record** (`recover_LS.py`): parsed
`solutions/P23/v509e2442.vtx` with the v1 exact field parser, split it into the
native-lattice part and the ρ-rotated part by exact division by ρ:
recovered **L = 374**, **S = 136** integer tuples (origin shared), with exactly
**1860 / 564 / 18** L/S/cross edges = 2442 total, all via the integer tests
above. The 18 cross edges decompose into 12 reference edges
(|u|²=|v|²=4, orbit (0,4,4,0)) + 6 auxiliary edges of kind
144|u|² = 408 ± 24√33, i.e. sides √11/2 ± √3/6 — precisely Parts' description
of subtype M6A. This validates both the arithmetic and the survey machinery.

## Which t have radius-√t lattice points at all (`norm_rep.py`)

|u|² = t requires N = 144t ∧ M = 0. Exhaustive integer search, t ≤ 32:
points exist for t = 1, 3, 4, 5, 7, 9, 11, 12, 13, 15, 16, 19, 20, 21, 23, 25,
27, 28, 31 (counts 30–120); none for t = 2, 6, 8, 10, 14, 17, 18, 22, 24, 26,
29, 30, 32. (This is the norm form of ℤ[ω₁,η]; the plain Loeschian condition
is necessary but not sufficient here, e.g. t=25 has 90 points, t=10 has none.)

## Cross-edge survey (`survey2.py`, exact; pool = radius-√t disk)

Pool P_t = all base-lattice points with min conjugate radius ≤ √t
(orbit-closed under Parts' order-24 group; for t=4 this reproduces Parts'
"about 400 orbits" disk: 2839 points / 421 orbits at r=2 for ⊕⁴H²).
Counted all exact cross unit pairs (u, ω_t v), u,v ∈ P_t \ {0}; a **kind** is
the exact pair (144|u|², 144|v|²) ∈ ℚ(√33)² — the shape of the triangle
(0, u, ω_t v). Pairs with u=0 or v=0 are excluded (they are ordinary
within-copy edges through the shared vertex, one kind, always present).

| t  | field adjoin | pool | cross | reference | kinds | kind sizes |
|----|-------------|------|-------|-----------|-------|------------|
| 1  | native       | 253  | 1932  | 60  | 32  | rich (degenerate: ω₁ = 60°, pool closed under it) |
| 2  | √7           | 343  | 0     | 0   | 0   | — |
| 3  | native (=η²) | 403  | 1632  | 36  | 44  | rich |
| 4  | √15 (=ρ)     | 2839 | 66    | 30  | 2   | **30 ref + 36 aux** (the record's geometry) |
| 5  | √19          | 3151 | 48    | 48  | 1   | ref only |
| 6  | √23          | 3235 | 0     | 0   | 0   | — |
| 7  | native       | 3379 | 1896  | 60  | 74  | rich |
| 8  | √31          | 3385 | 0     | 0   | 0   | — |
| 9  | √35          | 13633| 66    | 54  | 2   | **54 ref + 12 aux** |
| 10 | √39          | 13945| 36    | 0   | 2   | 24 + 12, **no reference kind** |
| 11 | √43          | 14155| 18    | 18  | 1   | ref only |
| 12 | √47          | 14311| 30    | 30  | 1   | ref only |
| 13 | √51          | 14467| 60    | 60  | 1   | ref only |
| 14 | √55          | 14473| 0     | 0   | 0   | — |
| 15 | √59          | 14527| 48    | 36  | 2   | **36 ref + 12 aux** |
| 16 | √7 (s=3)     | 38743| 66    | 30  | 4   | **30 ref + 12+12+12 aux** |
| 17 | √67          | 39223| 0     | 0   | 0   | — |
| 18 | √71          | 39223| 0     | 0   | 0   | — |
| 19 | native       | 39697| 4860  | 60  | 281 | rich |
| 20 | √79          | 39781| 36    | 36  | 1   | ref only |
| 21 | √83          | 39865| 84    | 60  | 2   | **60 ref + 24 aux** |
| 22 | √87          | 39901| 0     | 0   | 0   | — |
| 23 | √91          | 39931| 12    | 12  | 1   | ref only |
| 24 | √95          | 39943| 12    | 0   | 1   | 12, no ref |
| 25 | native (=η⁴·…)| 86659| 10152 | 66  | 583 | rich |

Headline: among NON-native rotations, **only t = 4, 9, 15, 16, 21 exhibit two
or more cross-edge kinds** (Parts: the second kind is *essential* for type M);
t = 16 is the richest (4 kinds). t = 10 and 24 have kinds but no reference
edges. All remaining non-native t have at most the reference kind, or nothing.

## Type-M SAT experiments (`typem.py`)

For each candidate t: W_t = P_t ∪ ω_t P_t (shared origin), all edges exact,
4-colorability by kissat (UNSAT ⇒ 5-chromatic witness at that rotation; SAT ⇒
**no subgraph of W_t works**, i.e. type M fails for ω_t at radius √t).

Control t=4: W_4 = 5677 vertices / 42018 edges → **UNSAT** (contains G509's
geometry; machinery confirmed end-to-end).

| t  | W_t vertices / edges | 4-colorable? | verdict |
|----|----------------------|--------------|---------|
| 1  | 505 / 3924           | SAT  | fails (degenerate: pool closed under ω₁) |
| 3  | 805 / 5076           | SAT  | fails (native) |
| 4  | 5677 / 42018         | **UNSAT** | control — the record's rotation ✓ |
| 5  | 6301 / 46440         | SAT  | fails (ref-only) |
| 7  | 6757 / 51204         | SAT  | fails (native) |
| 9  | 27265 / 270966       | SAT  | fails (despite ref + 1 aux kind) |
| 10 | 27889 / 275808       | SAT  | fails (no ref kind) |
| 11 | 28309 / 279246       | SAT  | fails (ref-only) |
| 12 | 28621 / 281562       | SAT  | fails (ref-only) |
| 13 | 28933 / 284112       | SAT  | fails (ref-only) |
| 15 | 29053 / 284952       | SAT  | fails (despite ref + 1 aux kind) |
| 16 | 77485 / 863046       | **UNSAT** | **WORKS — new type-M rotation** |
| 19 | 79393 / 884376       | SAT  | fails (native, 281 kinds!) |
| 20 | 79561 / 880920       | SAT  | fails (ref-only) |
| 21 | 79729 / 882384       | SAT  | fails (despite ref + 1 aux kind) |
| 23 | 79813 / 882972       | SAT  | fails (ref-only) |
| 25 | 173317 / 2063928         | SAT  | fails (native, 583 kinds) |
| 28 | 175057 / 2069280     | **UNSAT** | **WORKS — new type-M rotation** |

Controls for the two new working rotations: the SINGLE (unrotated) copy is
4-colorable in both cases — `pool_alone.py`: r=4 pool (38743 vtx / 431490
edges) → SAT; r=√28 pool (87469 vtx / 1034100 edges) → SAT. So the
non-4-colorability genuinely comes from the ω_t cross edges, not from the
lattice disk itself.

**New working rotations found (Parts: "Working constructions of type M with
other rotations are not known yet"):**
- **ω₁₆ = (31 + 3i√7)/32** = exp(i arccos(31/32)); union lives in
  ℚ(√3,√7,√11); cross structure: 30 reference edges (radius-4 pairs) + three
  auxiliary kinds (12+12+12).
- **ω₂₈ = (55 + i√111)/56** = exp(i arccos(55/56)); union in ℚ(√3,√11,√37);
  60 reference + 24 + 12 auxiliary.

## Minimization of the two new witnesses

DRAT-core iteration (`coremin.py`, every core drat-trim `s VERIFIED`) followed
by 8-4-2-1 batched greedy destructive deletion with core jumps (`greedy8.py`):

- **t=16**: 77485 → cores 5081/5299/6056 (3 seeds) → greedy (3 chains, ~7 h)
  → best **2167 vertices / 11884 edges** (chains: 2167, 2197, 2336; first
  greedy pass not exhausted — rate had decayed to ~1-2 vertices per 10 min).
- **t=28**: 175057 → core 9048 (138 coremin iterations) → greedy reached
  **7295 vertices / 55831 edges** before the time box expired (still
  descending; also independently verified — `verify28_final.log`).

The minimized ω₁₆ witness (2167 vtx) was passed through the INDEPENDENT exact
verifier `verify_m.py` (field ℚ(√3,√7,√11) multiquadratic arithmetic from
fusion1's `mfield.py`, exact coordinates emitted by `emit_t.py` — a codepath
disjoint from `lattice.py`'s integer conditions): all edges exactly unit,
edge list complete, kissat UNSAT, drat-trim VERIFIED (`verify16_final.log`;
the same pipeline also PASSed on an earlier 3756-vertex snapshot,
`verify16_snapshot.log`).

These sizes are far above 509 — greedy from a bulk disk union plateaus around
2000+ here, consistent with v1's finding that Parts-level sizes need his full
orbit-filling/customization machinery. The contribution of this run is the
EXISTENCE of working type-M rotations other than ρ, not a record attempt size.

Not tested (too large / no candidate structure): t=27, 31 (ref-only kind at
radius √t — all six tested ref-only rotations came out SAT); t=2, 6, 8, 14,
17, 18, 22, 24, 26, 29, 30, 32 (no reference points at all; t=24 has a single
aux kind and no ref, analogous to the failed t=10).

## Files

- `lattice.py` — exact integer lattice/rotation arithmetic (module docstring
  has the full derivations); `norm_rep.py` — |u|²=t representability.
- `recover_LS.py` → `LS.pkl` — L374/S136 in lattice coordinates from witness.
- `build_pool.py` / `build_pool_r.py` — radius-r orbit-closed pools.
- `survey.py` (fixed radius-2 pool) / `survey2.py` (radius-√t pools) →
  `survey.pkl`, `survey2.pkl`.
- `typem.py` — W_t construction + SAT test → `wt_<t>.pkl`, `typem_<t>.log`;
  `pool_alone.py` — single-copy controls.
- `coremin.py` (patched: per-iteration snapshots + plateau stop), `greedy8.py`
  — minimization; `greedy_t16a.pkl` = final 2167-vertex witness (ids into
  `wt_16.pkl`), `greedy_t28a.pkl` = t=28 partial result.
- `emit_t.py` → `v16_final.pkl` (exact ℚ(√3,√7,√11) coordinates);
  `verify_m.py`/`mfield.py` (from fusion1) — independent verifier;
  `verify16_final.log`, `verify16_snapshot.log`.
- `sat.py`, `greedy.py`, `emit.py` from runs/P23-fusion1.

## Conclusion

- ω₁₆ and ω₂₈ are the first known working type-M rotations besides Parts'
  ρ = ω₄, answering his open remark. New fields: ℚ(√3,√7,√11), ℚ(√3,√11,√37).
- Smallest exactly-verified 5-chromatic UDG from this run: **2167 vertices**
  (ω₁₆, independent exact verification + drat-trim VERIFIED UNSAT).
- No sub-509 graph obtained; the record stands. Plausible follow-up: apply
  Parts' full orbit-filling minimization (his §5-6 machinery, weeks of
  compute in his account) to the ω₁₆ geometry, which now has MORE auxiliary
  edge kinds (3) than ρ's single auxiliary kind.

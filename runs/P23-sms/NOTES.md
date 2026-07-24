# P23 — Smaller 5-chromatic unit-distance graphs — run `sms` (constructive CEGAR)

Session: https://app.devin.ai/sessions/49a9799ae0f94a7c89fbe224d49392f2
Branch `runs/P23-sms`. Machine: 8 cores, 31 GB. Tools: kissat + drat-trim (built from
source), python-sat (pysat) 1.9, sympy 1.14, numpy, Python 3.10.

## Scope (assigned, distinct from `runs/P23-v1` and `runs/P23-fusion1`)
v1/fusion1 attacked the record by **local deletion / annealing** on vertex pools derived
from Parts' graph (best fresh graphs 586 in ℚ(√3,√5,√11), 569 in ℚ(√2,√3,√5,√11); the 509
record reproduced + DRAT-verified but never beaten). This run does something structurally
different: a **constructive SAT search over a FIXED exact geometric universe** using
selection variables and **counterexample-guided abstraction refinement (CEGAR)** — i.e. we
do not start from Parts' graph at all; we fix a finite point universe `U`, build its exact
unit-distance graph, and search for the *smallest* subset `S ⊆ U` whose induced subgraph is
non-`k`-colorable.

## Outcome (honest summary)
- **REQUIRED sanity check PASSED, fully certified.** Over the exact universe `U_2` in
  ℚ(√3,√11) (163 points), the CEGAR search rediscovers that the **smallest non-3-colorable
  (= 4-chromatic) subgraph has exactly 7 vertices — the Moser spindle** — and *proves*
  (outer UNSAT) that **no ≤6-vertex 4-chromatic subgraph exists**. The 7-vertex witness is
  independently re-verified: 7 vertices / 11 exact unit edges in ℚ(√3,√11), kissat 3-coloring
  **UNSAT + drat-trim `s VERIFIED`**, and 4-colorable (so χ = 4 exactly).
- **No 5-chromatic graph below 509 was found.** Consistent with v1/fusion1 and with the
  record having survived Polymath16. Instead we establish **certified negative / lower-bound
  results over a family of natural fixed universes** (below), which is the assigned fallback
  deliverable ("prove strong lower bounds for a restricted universe").
- **k=4 CEGAR validated end-to-end and used to constructively re-derive the record's
  criticality**: over the universe consisting of exactly Parts' 509 vertices, CEGAR proves
  (outer UNSAT at N=508, 375 refinement colorings) that **no 508-vertex subset is
  non-4-colorable** — i.e. the 509 graph is the minimum non-4-colorable subset of itself
  (vertex-critical). This reproduces v1's deletion-search finding by a completely different
  (selection-variable/CEGAR) method.

## Method

### 1. Fixed exact geometric universe (`universe.py`, `universe5.py`, `mfield.py`)
"Moser-spindle-generating" ball: `U_k` = all points reachable by ≤ `k` unit steps from the
origin, where a *unit step* is one of a finite set `D` of exact unit vectors closed under the
dihedral group D6 (rotation by ω = e^{iπ/3} and complex conjugation):

    D = { ω^j : j=0..5 }  ∪  { ρ·ω^j }  ∪  { ρ̄·ω^j },   ρ = 5/6 + (√11/6) i, |ρ| = 1.

ρ is the **Moser rotation** (cos = 5/6, the angle that closes the spindle: two √3-diagonal
rhombi rotated so their tips are unit distance apart). Everything is exact in the real
multi-quadratic field ℚ(√3,√11) via `mfield.MField`; **no floating point enters any
decision** (`to_float` is only a prefilter for the O(n²) edge scan, every candidate edge
confirmed by exact `norm2 == 1`). The Moser spindle
`{0, 1, ω, 1+ω, ρ, ρω, ρ(1+ω)}` is a subgraph of `U_2` by construction, so the sanity target
is guaranteed present. `universe5.py` augments `D` with a √5 unit rotation
σ = (1+2i)/√5 (∠ = arctan 2) over ℚ(√3,√5,√11) — the extra generator in Parts' field beyond
the Moser ball. The D6 automorphisms are recorded as index permutations for symmetry breaking.

### 2. Constructive CEGAR search (`cegar.py`)
Search `min |S|` over `S ⊆ U` with χ(U[S]) ≥ k+1 (k=3 → 4-chromatic; k=4 → 5-chromatic),
QBF-free:
- **Selection variables** `s_v` for every `v ∈ U`; **cardinality** `|S| ≤ N` via pysat
  `ITotalizer` (incremental — N is tightened by a single assumption literal).
- **CEGAR blocking constraints**: maintain a growing set `C` of k-colorings of `U`. A
  non-k-colorable `S` must, for *every* coloring `c`, contain a `c`-monochromatic edge; we
  encode, for each `c ∈ C`, "S contains a monochromatic edge of `c`" (`OR_{(u,v)∈mono(c)}
  (s_u ∧ s_v)`, Tseitin-ised). This is a necessary condition (over-approximation).
  - outer **UNSAT** ⟹ **no non-k-colorable S with |S| ≤ N exists** (a genuine lower bound).
  - outer **SAT** ⟹ candidate `S`; **verify with a plain k-coloring SAT call** on U[S]:
    - not k-colorable ⟹ **witness** (χ ≥ k+1); tighten N ← |S|−1 and continue for the min.
    - k-colorable ⟹ extend its proper coloring greedily to all of `U` (minimising
      monochromatic edges → strongest possible blocking clause) and add it to `C` (refine).
- **Symmetry breaking**: lex-leader constraints `s ⪯_lex g(s)` for each non-identity D6
  automorphism `g` (sound: every `g` is a graph automorphism of `U`, preserving unit
  distances, and "non-k-colorable" is symmetry-invariant).

Inner/outer solving uses pysat (fast, thousands of small calls); every **claimed witness** is
then re-checked with exact arithmetic + kissat + **drat-trim** by `verify_sms.py`, and every
**4-colorability (negative) claim** is certified by an independently-checked proper 4-coloring
(`certify_4col.py`).

## Experiments

### E0 — code validation
- **k=3, U_2 (Moser sanity, REQUIRED):** smallest non-3-colorable subset = **7 vertices**
  (Moser spindle); **N ≤ 6 outer UNSAT**. Witness certified (kissat UNSAT + drat `s VERIFIED`,
  χ = 4). `witness_spindle.pkl`, `spindle.vtx`, `spindle.edges`. ✅
- **k=4 on synthetic K5** (`U_k5test.pkl`, K₅ + 5 isolated vertices): CEGAR returns min
  non-4-colorable subset = **5** (= K₅), N ≤ 4 UNSAT. Validates the k=4 path. ✅

### E1 — Moser-ball universes ℚ(√3,√11): NO 5-chromatic subgraph up to 55,747 vertices
Direct 4-colorability of the whole `U_k` (a proper 4-coloring is a self-verifying certificate
that U — and hence *every* subgraph of U — is 4-colorable, so contains no 5-chromatic UDG).
All colorings independently verified edge-by-edge (`certify_4col.py`):

| universe | |U| | edges | χ(U) | result |
|---|---:|---:|---|---|
| U_2 | 163 | 594 | ≤ 4 (χ=4) | 4-colorable — **no 5-chromatic subgraph** |
| U_3 | 865 | 4,530 | ≤ 4 | 4-colorable — no 5-chromatic subgraph |
| U_4 | 3,313 | 21,900 | ≤ 4 | 4-colorable — no 5-chromatic subgraph |
| U_5 | 10,099 | 79,962 | ≤ 4 | 4-colorable — no 5-chromatic subgraph |
| U_6 | 25,765 | 239,736 | ≤ 4 | 4-colorable — no 5-chromatic subgraph |
| U_7 | 55,747 | 582,048 | ≤ 4 | 4-colorable — no 5-chromatic subgraph |

So the natural "spindle-generating" ball over the Moser field ℚ(√3,√11) is **4-colorable out
to radius 7 (55k vertices)** — it contains the 4-chromatic Moser spindle but no 5-chromatic
UDG. 5-chromaticity does not arise from Moser-rotation geometry alone at these radii.

### E2 — richer field ℚ(√3,√5,√11) (adds √5 rotation): still 4-colorable
`universe5.py` adds the √5 unit rotation σ = (1+2i)/√5 to `D`:

| universe | |U| | edges | result |
|---|---:|---:|---|
| U5_2 | 451 | 1,686 | 4-colorable — no 5-chromatic subgraph |
| U5_3 | 4,141 | 22,350 | 4-colorable — no 5-chromatic subgraph |
| U5_4 | 27,301 | 188,388 | 4-colorable — no 5-chromatic subgraph (certified) |

Adding √5 geometry does not make the ball non-4-colorable at these sizes either.

### E3 — the 509 record as a fixed universe: constructive vertex-criticality (k=4 CEGAR)
`build509univ.py` loads Parts' exact 509 vertices (ℚ(√3,√5,√11)) → `U_509.pkl` (509 vertices,
2442 edges, matches the record).
- Whole graph: kissat 4-coloring **UNSAT** (178 s) ⟹ χ ≥ 5 (record reconfirmed from scratch).
- CEGAR at N = 508: **outer UNSAT after 375 refinement colorings** (105 s) ⟹ **no 508-vertex
  subset is non-4-colorable** ⟹ the record is the minimum non-4-colorable subset of itself
  (vertex-critical). `cegar509.log`. This matches v1's deletion-search criticality result via
  a different (selection-variable / CEGAR) method — an independent cross-check of the record.

## Interpretation
- The constructive CEGAR pipeline is correct and cheaply rediscovers the classical fact that
  the Moser spindle (7 vertices) is the smallest 4-chromatic UDG, and proves the ≤6 lower
  bound — a strong end-to-end validation over exact algebraic coordinates with a DRAT
  certificate.
- For the 5-chromatic target, the tractable, honest outcome over a *fixed* universe is a
  **lower bound**: the Moser-ball universes (ℚ(√3,√11) up to 55k vertices; ℚ(√3,√5,√11) up to
  27k) are all 4-colorable, so they contain **no** 5-chromatic UDG at all. Any 5-chromatic UDG
  therefore requires either a much larger radius or genuinely different geometry than these
  "unit-steps-from-origin" balls provide — consistent with de Grey's/Parts' 5-chromatic graphs
  being carefully-selected Minkowski-sum subgraphs, not balls.
- Where a universe *is* non-4-colorable (the 509 record itself), CEGAR confirms 509 is the
  minimum non-4-colorable subset of that universe. Beating 509 needs a fixed universe that
  (a) contains a 5-chromatic UDG and (b) whose *minimal* such subgraph is < 509 — an open
  question this method could settle for any concrete candidate universe, but no such universe
  was found here.

## Files
- `mfield.py` exact multi-quadratic field + Mathematica `.vtx` parser (copied from fusion1).
- `field.py`, `sat.py`, `verify_m.py` copied from fusion1 (native-field helpers / verifier).
- `universe.py` Moser-ball universe over ℚ(√3,√11) + exact UDG + D6 symmetry perms.
- `universe5.py` richer ball over ℚ(√3,√5,√11) (adds √5 rotation).
- `cegar.py` the constructive CEGAR search (selection vars + ITotalizer cardinality +
  refinement colorings + lex-leader symmetry breaking).
- `chi.py` whole-universe k-colorability check (kissat).
- `certify_4col.py` independently-verified proper 4-coloring (negative-result certificate).
- `verify_sms.py` certified witness verifier (exact edges + kissat UNSAT + drat-trim + χ=k+1).
- `build509univ.py` builds the 509-record universe pkl.
- `witness_spindle.pkl` / `spindle.vtx` / `spindle.edges` the rediscovered Moser spindle.
- `cegar509.log` the N=508 vertex-criticality run.
- `.pkl` universe caches are regenerable (see below) and git-ignored to keep the branch light.

## Reproduce
```
cd runs/P23-sms                          # needs kissat + drat-trim at ~/p23/.../  (or on PATH)
pip install python-sat sympy numpy

# Moser sanity (REQUIRED): smallest 4-chromatic subgraph = 7, N<=6 UNSAT
python3 universe.py 2 U_k2.pkl
python3 cegar.py U_k2.pkl 3 12 witness_spindle.pkl
python3 verify_sms.py U_k2.pkl witness_spindle.pkl --k 3 --drat    # PASS + s VERIFIED

# negative result: Moser balls are 4-colorable (no 5-chromatic subgraph)
for k in 3 4 5 6 7; do python3 universe.py $k U_k$k.pkl; python3 certify_4col.py U_k$k.pkl; done

# richer field
for k in 2 3 4; do python3 universe5.py $k U5_k$k.pkl; python3 certify_4col.py U5_k$k.pkl; done

# 509 record as fixed universe: chi>=5, and vertex-critical via CEGAR
python3 build509univ.py
python3 chi.py U_509.pkl 4                 # UNSAT => chi>=5
python3 cegar.py U_509.pkl 4 508           # outer UNSAT => no 508-vertex non-4-colorable subset
```

# P06 Lean formalization run notes (WoW 698, adjacency reading)

**Date:** 2026-07-23 · **Deliverable:** `formalization/P06/` · **Branch:** `runs/P06-lean`

## Result

`P06.wow_conjecture_698` (in `formalization/P06/P06/Main.lean`) fully proves,
with **no `sorry`, no custom axioms, no `native_decide`**:

for every finite simple graph `G` (over any `Fintype` vertex type, with
`hA : (G.adjMatrix ℝ).IsHermitian`, which always holds by
`P06.adjMatrix_isHermitian`):

```
Real.sqrt (∑ i ∈ univ.filter (fun i => hA.eigenvalues i < 0), hA.eigenvalues i ^ 2)
  ≤ randicIndex G
```

* Eigenvalue population = `Matrix.IsHermitian.eigenvalues` (mathlib's spectral
  theorem), i.e. all `|V|` adjacency eigenvalues with multiplicity, filtered to
  the negative ones, squared and summed — the WoW "length" (Euclidean norm).
* `randicIndex G = ∑ e ∈ G.edgeFinset, Sym2.lift (1/√(dᵤdᵥ)) e` — the Randić
  index summed over the edges of `G`. Edge endpoints have degree ≥ 1, so no
  division-by-zero issue; isolated vertices contribute nothing; `m = 0` is
  handled (both sides `0`), so no `m ≥ 1` hypothesis is needed.

Equality analysis was **not** formalized (not required to settle WoW 698).

## Axiom check (from `lake build`, `#print axioms` in `Main.lean`)

```
info: P06/Main.lean:126:0: 'P06.wow_conjecture_698' depends on axioms: [propext, Classical.choice, Quot.sound]
```

`lake build` completes cleanly (8659 jobs, warnings only for the P08-inherited
lint options, no errors).

## Proof chain (matches `solutions/P06/PROOF-698.md`)

1. **Rayleigh** (`P06.exists_eigenvalue_mul_ge`, `Spectral.lean`): expand the
   quadratic form in the orthonormal eigenbasis; the max eigenvalue index gives
   `x ⬝ᵥ A *ᵥ x ≤ μ (x ⬝ᵥ x)`. At `x = (√dᵤ)ᵤ`, edge double counting
   (`sum_dart_edge`, `sum_dart_eq_sum_neighbors`) gives numerator `2S`,
   denominator `2m`, so `S ≤ μ·m`.
2. **Cauchy–Schwarz over the edges** (`P06.card_edgeFinset_sq_le`): applied via
   `Finset.sum_sq_le_sum_mul_sum_of_sq_le_mul` with `r = 1`, `f = √(dᵤdᵥ)`,
   `g = (dᵤdᵥ)^(-1/2)`, so `m² ≤ S·R` (per-edge `1 = f·g` uses degree
   positivity of edge endpoints).
3. `m ≤ μR`, then `μ² + R² ≥ 2μR ≥ 2m` (nlinarith with `sq_nonneg (μ − R)`).
4. **Trace** (`P06.sum_sq_eigenvalues_eq_trace_mul_self` +
   `P06.trace_adjMatrix_mul_self`): `∑ λᵢ² = trace(A·A) = ∑ᵥ dᵥ = 2m`;
   splitting the sum at `λ < 0` and dropping the positive part below `μ²`
   yields `s⁻² ≤ 2m − μ² ≤ R²`, hence `s⁻ ≤ R`.

## Implementation notes

* Mathlib `v4.32.0` (same rev/manifest as `formalization/P08`); spectral helper
  lemmas (`inner_eq_dotProduct`, eigenbasis expansion) adapted from
  `P08/Spectral.lean`.
* `∑ λᵢ² = trace(A²)` proved from `Matrix.IsHermitian.spectral_theorem`
  (`A = u D u*` with `u` unitary), `map_mul` of `Unitary.conjStarAlgAut`,
  `Matrix.trace_mul_cycle`, and `Unitary.coe_star_mul_self`.
* Edge sums use `Finset.sum_fiberwise_of_maps_to` over darts, with
  `SimpleGraph.dart_edge_fiber_card` (each edge has exactly 2 darts) and
  `SimpleGraph.dart_fst_fiber` (darts at `v` ↔ neighbors of `v`).

## Reproduce

```
cd formalization/P06 && lake exe cache get && lake build
```

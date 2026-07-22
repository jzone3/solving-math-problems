import Mathlib

/-!
# The 9-vertex witness graph `W`

`W` is the graph with graph6 code `H?q`qjo`, edges
`{04, 05, 08, 14, 17, 18, 25, 26, 28, 36, 37, 38, 46, 57}`
(the minimal counterexample found in `runs/P02/v4`; it is the Grötzsch graph
minus two non-adjacent branch vertices).

This file proves the finite, decidable hypotheses of West's statement for `W`:
* `W_cliqueFree` — `W` is triangle-free;
* `W_common_neighbor` — every non-adjacent pair of distinct vertices has a
  common neighbour (whence `W_maximal`: `W` is maximal triangle-free);
* `W_degree` — every vertex has degree `≥ 3 = 9/3` (in the exact form
  `9 ≤ 3 * degree`, avoiding division);
* `W_minDegree` — the minimum degree is exactly `3`.

All of these are established by plain `decide` (no `native_decide`).
-/

namespace P02

/-- Edge list of the witness (graph6 `H?q`qjo`). -/
def edgeList : List (Fin 9 × Fin 9) :=
  [(0, 4), (0, 5), (0, 8), (1, 4), (1, 7), (1, 8), (2, 5), (2, 6),
   (2, 8), (3, 6), (3, 7), (3, 8), (4, 6), (5, 7)]

/-- The 9-vertex witness graph `W`. -/
def W : SimpleGraph (Fin 9) where
  Adj a b := (a, b) ∈ edgeList ∨ (b, a) ∈ edgeList
  symm := ⟨fun _ _ h => Or.symm h⟩
  loopless := ⟨by decide⟩

instance : DecidableRel W.Adj := fun _ _ =>
  inferInstanceAs (Decidable (_ ∨ _))

instance : Decidable (W.CliqueFree 3) :=
  inferInstanceAs (Decidable (∀ t, ¬W.IsNClique 3 t))

set_option maxRecDepth 4000 in
/-- `W` is triangle-free. -/
theorem W_cliqueFree : W.CliqueFree 3 := by decide

/-- Every non-adjacent pair of distinct vertices of `W` has a common
neighbour (so adding any edge would create a triangle). -/
theorem W_common_neighbor :
    ∀ u v : Fin 9, u ≠ v → ¬W.Adj u v → ∃ w, W.Adj u w ∧ W.Adj v w := by
  decide

/-- `W` is maximal triangle-free: it is triangle-free, and no strictly larger
graph on the same vertices is. -/
theorem W_maximal : Maximal (fun H => H.CliqueFree 3) W := by
  refine ⟨W_cliqueFree, fun H hH hWH u v hHuv => ?_⟩
  by_contra hnW
  obtain ⟨w, huw, hvw⟩ := W_common_neighbor u v hHuv.ne hnW
  exact hH {u, w, v} (SimpleGraph.is3Clique_triple_iff.mpr
    ⟨hWH huw, hHuv, hWH hvw.symm⟩)

/-- Every vertex of `W` has degree at least `n/3 = 3`, stated exactly as
`n ≤ 3 · deg(v)` with `n = 9` (no rounding). -/
theorem W_degree : ∀ v : Fin 9, 9 ≤ 3 * W.degree v := by decide

/-- The minimum degree of `W` is exactly `3 = 9/3`. -/
theorem W_minDegree : W.minDegree = 3 := by decide

end P02

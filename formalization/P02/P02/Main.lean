import P02.Multiplication
import P02.Witness

/-!
# P02: refutation of the statement on West's open-problem list

West (dwest.web.illinois.edu/openp/regsup.html) records: *"If G is a maximal
triangle-free graph and has minimum degree at least n(G)/3, then G has a
regular supergraph obtainable by vertex multiplications."*

Main results:
* `W_no_regular_mult_supergraph` — for the 9-vertex witness `W`, NO choice of
  positive multiplicities `x` makes the multiplication graph regular (of any
  degree `d`).
* `west_statement_false` — the statement above, formalized as
  `WestStatement`, is false; `W` (with `n = 9`, `δ(W) = 3 = 9/3`) is a
  counterexample.

The infeasibility of the linear system `{x ≥ 1, A x = d·1}` is certified by
the explicit Farkas vector `y = (2, -1, -1, 2, -1, -1, -1, -1, 2)` (twice the
rational certificate `(1, -½, -½, 1, -½, -½, -½, -½, 1)` from
`solutions/P02/verify.py`): `∑ y = 0`, `A y = 2·e₈ ≥ 0`, `𝟙ᵀA y = 2 > 0`.
-/

open Finset

namespace P02

/-- The Farkas certificate: twice the rational vector from
`solutions/P02/verify.py`. -/
def y : Fin 9 → ℤ := ![2, -1, -1, 2, -1, -1, -1, -1, 2]

lemma y_sum : ∑ v, y v = 0 := by decide

lemma y_Ay_nonneg : ∀ u, 0 ≤ ∑ v ∈ W.neighborFinset u, y v := by decide

lemma y_Ay_sum_pos : 0 < ∑ u, ∑ v ∈ W.neighborFinset u, y v := by decide

/-- The linear system `∑_{u ∈ N(v)} x u = d` (for `x ≥ 1` and any `d`) has no
solution over `W`: the Farkas certificate `y` rules out every degree `d`
simultaneously. -/
theorem W_linear_system_infeasible (x : Fin 9 → ℕ) (hx : ∀ v, 1 ≤ x v) (d : ℕ) :
    ¬∀ v, ∑ u ∈ W.neighborFinset v, x u = d := fun h =>
  W.farkas_no_solution y y_sum y_Ay_nonneg y_Ay_sum_pos x hx d h

/-- **Main theorem.** No supergraph of `W` obtained by vertex multiplications
is regular: for every positive multiplicity vector `x` and every degree `d`,
the multiplication graph `W.mult x` is not `d`-regular. -/
theorem W_no_regular_mult_supergraph (x : Fin 9 → ℕ) (hx : ∀ v, 1 ≤ x v) (d : ℕ) :
    ¬(W.mult x).IsRegularOfDegree d := fun h =>
  W_linear_system_infeasible x hx d ((W.mult_isRegularOfDegree_iff x hx d).mp h)

/-- West's recorded statement, formalized: every maximal triangle-free graph
`G` on `n` vertices with minimum degree at least `n/3` (stated exactly as
`n ≤ 3·deg(v)` for all `v`) has a regular supergraph obtainable by vertex
multiplications (positive multiplicities `x`, some degree `d`). -/
def WestStatement : Prop :=
  ∀ (n : ℕ) (G : SimpleGraph (Fin n)) (_ : DecidableRel G.Adj),
    Maximal (fun H => H.CliqueFree 3) G →
    (∀ v, n ≤ 3 * G.degree v) →
    ∃ (x : Fin n → ℕ) (d : ℕ), (∀ v, 1 ≤ x v) ∧ (G.mult x).IsRegularOfDegree d

/-- **West's recorded statement is false**: `W` is a counterexample. -/
theorem west_statement_false : ¬WestStatement := by
  intro hwest
  obtain ⟨x, d, hx, hreg⟩ := hwest 9 W inferInstance W_maximal W_degree
  exact W_no_regular_mult_supergraph x hx d hreg

end P02

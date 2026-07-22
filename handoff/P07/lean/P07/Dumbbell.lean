/-
# The dumbbell D(20, 12, 7) — partial formalization for Graffiti conjecture 143

Original conjecture (Fajtlowicz, *Written on the Wall*, item 143):

> "variance of positive eigenvalues < size / average distance."

The refutation witness (see `solutions/P07/verify143.py`,
`runs/P07/v5/NOTES.md`) is the dumbbell `D(20, 12, 7)`: cliques `K₂₀` and
`K₇` joined by a path with 12 internal vertices (13 path edges), `n = 39`,
`m = 224`, ordered distance sum `S = 9952`.

This file proves, fully and honestly, all the *combinatorial* facts about
the witness (graph definition, closed-form distance with certificates,
connectivity, `m = 224`, `S = 9952`), and reduces the refutation of
conjecture 143 to a single remaining *spectral* inequality
`Var(positive eigenvalues) > 10647/311 (= m·n²/S)` — see
`conjecture143_false_iff` and the NOTES.  The spectral inequality involves
irrational algebraic eigenvalues and is NOT proven here; no `sorry` is
used — the unproven statement is simply not asserted.

Vertex layout on `Fin 39`:
* `0, …, 19`  — clique `K₂₀`, attachment vertex `19`;
* `20, …, 31` — the 12 internal path vertices;
* `32, …, 38` — clique `K₇`, attachment vertex `32`;
* chain `19 – 20 – ⋯ – 31 – 32` (13 path edges).
-/
import Mathlib

namespace P07

/-- Adjacency for the dumbbell `D(20,12,7)` on the underlying naturals. -/
def adjD (u v : ℕ) : Prop :=
  (u < 20 ∧ v < 20 ∧ u ≠ v) ∨
  (32 ≤ u ∧ u < 39 ∧ 32 ≤ v ∧ v < 39 ∧ u ≠ v) ∨
  (19 ≤ u ∧ u ≤ 32 ∧ 19 ≤ v ∧ v ≤ 32 ∧ (u + 1 = v ∨ v + 1 = u))

instance : DecidableRel adjD := fun _ _ => by unfold adjD; infer_instance

/-- Closed-form graph distance on the dumbbell `D(20,12,7)`. -/
def distD (u v : ℕ) : ℕ :=
  if u = v then 0
  else if u < 20 ∧ v < 20 then 1
  else if 32 ≤ u ∧ 32 ≤ v then 1
  else if u < 20 then
    (if v < 32 then (v - 19) + (if u = 19 then 0 else 1)
     else 13 + (if u = 19 then 0 else 1) + (if v = 32 then 0 else 1))
  else if v < 20 then
    (if u < 32 then (u - 19) + (if v = 19 then 0 else 1)
     else 13 + (if v = 19 then 0 else 1) + (if u = 32 then 0 else 1))
  else if 32 ≤ v then (32 - u) + (if v = 32 then 0 else 1)
  else if 32 ≤ u then (32 - v) + (if u = 32 then 0 else 1)
  else (u - v) + (v - u)

set_option maxHeartbeats 4000000

lemma distD_self (u : ℕ) : distD u u = 0 := by unfold distD; simp

lemma distD_comm (u v : ℕ) : distD u v = distD v u := by
  unfold distD; split_ifs <;> omega

lemma eq_of_distD_eq_zero {u v : ℕ} (h : distD u v = 0) : u = v := by
  unfold distD at h; split_ifs at h <;> omega

/-- 1-Lipschitz certificate along edges. -/
lemma distD_lipschitz {u v w : ℕ} (h : adjD v w) :
    distD u v ≤ distD u w + 1 := by
  unfold adjD at h
  unfold distD
  split_ifs <;> omega

/-- BFS parent certificate. -/
lemma existsD_parent {u v : ℕ} (hu : u < 39) (hv : v < 39)
    (h : distD u v ≠ 0) :
    ∃ w, w < 39 ∧ adjD w v ∧ distD u w + 1 = distD u v := by
  have huv : u ≠ v := fun he => h (he ▸ distD_self u)
  by_cases hv20 : v < 20
  · by_cases hu20 : u < 20
    · exact ⟨u, hu, Or.inl ⟨hu20, hv20, huv⟩, by unfold distD; split_ifs <;> omega⟩
    · by_cases hv19 : v = 19
      · exact ⟨20, by omega, Or.inr (Or.inr (by omega)),
          by unfold distD; split_ifs <;> omega⟩
      · exact ⟨19, by omega, Or.inl ⟨by omega, hv20, by omega⟩,
          by unfold distD; split_ifs <;> omega⟩
  · by_cases hvB : 32 ≤ v
    · by_cases huB : 32 ≤ u
      · exact ⟨u, hu, Or.inr (Or.inl ⟨huB, hu, hvB, hv, huv⟩),
          by unfold distD; split_ifs <;> omega⟩
      · by_cases hv32 : v = 32
        · exact ⟨31, by omega, Or.inr (Or.inr (by omega)),
            by unfold distD; split_ifs <;> omega⟩
        · exact ⟨32, by omega, Or.inr (Or.inl ⟨by omega, by omega, hvB, hv, by omega⟩),
            by unfold distD; split_ifs <;> omega⟩
    · -- 20 ≤ v ≤ 31: v is an internal path vertex
      by_cases hlt : u < v
      · exact ⟨v - 1, by omega, Or.inr (Or.inr (by omega)),
          by unfold distD; split_ifs <;> omega⟩
      · exact ⟨v + 1, by omega, Or.inr (Or.inr (by omega)),
          by unfold distD; split_ifs <;> omega⟩

/-- The dumbbell graph `D(20, 12, 7)` on `Fin 39`. -/
def dumbbell : SimpleGraph (Fin 39) where
  Adj u v := adjD u.val v.val
  symm := ⟨by intro u v h; unfold adjD at *; omega⟩
  loopless := ⟨by intro u h; unfold adjD at h; omega⟩

instance : DecidableRel dumbbell.Adj := fun u v =>
  inferInstanceAs (Decidable (adjD u.val v.val))

lemma adjD_iff {u v : Fin 39} : dumbbell.Adj u v ↔ adjD u.val v.val := Iff.rfl

lemma distD_le_walk_length {u v : Fin 39} (p : dumbbell.Walk u v) :
    distD u.val v.val ≤ p.length := by
  induction p with
  | nil => simp [distD_self]
  | @cons a b c hab q ih =>
      calc distD a.val c.val
          ≤ distD b.val c.val + 1 := by
            rw [distD_comm a.val c.val, distD_comm b.val c.val]
            exact distD_lipschitz (adjD_iff.mp hab)
        _ ≤ q.length + 1 := by omega
        _ = (SimpleGraph.Walk.cons hab q).length := by
            simp [SimpleGraph.Walk.length_cons]

lemma exists_walk_distD (u v : Fin 39) :
    ∃ p : dumbbell.Walk u v, p.length = distD u.val v.val := by
  generalize hd : distD u.val v.val = d
  induction d generalizing v with
  | zero =>
      have : u = v := Fin.ext (eq_of_distD_eq_zero hd)
      subst this
      exact ⟨SimpleGraph.Walk.nil, rfl⟩
  | succ k ih =>
      obtain ⟨w, hw39, hadj, hwk⟩ :=
        existsD_parent u.isLt v.isLt (by omega : distD u.val v.val ≠ 0)
      have hwk' : distD u.val (⟨w, hw39⟩ : Fin 39).val = k := by
        simpa [hd] using hwk
      obtain ⟨q, hq⟩ := ih ⟨w, hw39⟩ hwk'
      exact ⟨q.concat hadj, by simp [SimpleGraph.Walk.length_concat, hq]⟩

lemma dumbbell_reachable (u v : Fin 39) : dumbbell.Reachable u v :=
  (exists_walk_distD u v).elim fun p _ => ⟨p⟩

theorem dumbbell_connected : dumbbell.Connected :=
  SimpleGraph.Connected.mk dumbbell_reachable

/-- The graph distance of the dumbbell equals the closed form `distD`. -/
theorem dumbbell_dist_eq (u v : Fin 39) :
    dumbbell.dist u v = distD u.val v.val := by
  obtain ⟨p, hp⟩ := exists_walk_distD u v
  refine le_antisymm (hp ▸ SimpleGraph.dist_le p) ?_
  obtain ⟨q, hq⟩ := (dumbbell_reachable u v).exists_walk_length_eq_dist
  exact hq ▸ distD_le_walk_length q

set_option maxRecDepth 100000

/-- `m = 224` edges (`C(20,2) + C(7,2) + 13 = 190 + 21 + 13`).
Plain kernel `decide`. -/
theorem dumbbell_card_edges : dumbbell.edgeFinset.card = 224 := by decide

theorem distD_sum : (∑ u : Fin 39, ∑ v : Fin 39, distD u.val v.val) = 9952 := by
  decide

/-- The ordered distance sum (all `39² = 1521` ordered pairs, diagonal
included) of the dumbbell is `S = 9952`. -/
theorem dumbbell_distSum :
    (∑ u : Fin 39, ∑ v : Fin 39, dumbbell.dist u v) = 9952 := by
  simp only [dumbbell_dist_eq]
  exact distD_sum

/-! ## Reduction of the conjecture-143 refutation to a spectral inequality -/

/-- Average distance of the dumbbell, `rc` convention (mean of all `n²`
ordered entries, diagonal included). -/
noncomputable def dumbbellMu : ℝ :=
  (∑ u : Fin 39, ∑ v : Fin 39, (dumbbell.dist u v : ℝ)) / 39 ^ 2

lemma dumbbellMu_eq : dumbbellMu = 9952 / 1521 := by
  unfold dumbbellMu
  rw [show (∑ u : Fin 39, ∑ v : Fin 39, (dumbbell.dist u v : ℝ)) = 9952 by
    exact_mod_cast dumbbell_distSum]
  norm_num

lemma dumbbell_adjMatrix_isHermitian : ((dumbbell.adjMatrix ℝ)).IsHermitian :=
  Matrix.isHermitian_iff_isSymm.mpr (SimpleGraph.isSymm_adjMatrix dumbbell)

/-- Population variance of the positive adjacency eigenvalues of the
dumbbell (eigenvalues with multiplicity from mathlib's spectral theorem). -/
noncomputable def dumbbellVarPos : ℝ :=
  let eigs := dumbbell_adjMatrix_isHermitian.eigenvalues
  let P := Finset.univ.filter fun i => 0 < eigs i
  (∑ i ∈ P, (eigs i - (∑ j ∈ P, eigs j) / P.card) ^ 2) / P.card

/-- **Reduction lemma**: conjecture 143 fails for the dumbbell `D(20,12,7)`
iff the variance of its positive adjacency eigenvalues exceeds the exact
rational `m/μ(D) = 224·39²/9952 = 10647/311 ≈ 34.235`.

The right-hand side (the spectral inequality) is the one remaining unproven
step; numerically `dumbbellVarPos ≈ 34.31` (see `solutions/P07/verify143.py`,
certified to 40 significant digits with exact charpoly root isolation, but
not yet formalized). -/
theorem conjecture143_false_iff :
    ¬ (dumbbellVarPos < (dumbbell.edgeFinset.card : ℝ) / dumbbellMu) ↔
      (10647 / 311 : ℝ) ≤ dumbbellVarPos := by
  rw [dumbbell_card_edges, dumbbellMu_eq, not_lt]
  push_cast
  norm_num

end P07

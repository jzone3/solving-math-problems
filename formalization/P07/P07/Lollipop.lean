/-
# The lollipop graph L(K₅₀, P₇₀) and its exact distance function

Vertex set: `Fin 120`, laid out as
* `0, …, 49`  — the clique `K₅₀` (all pairs adjacent);
* `50, …, 119` — the path `P₇₀` (70 extra vertices, 70 path edges), attached
  to the clique at vertex `49` via the edge `{49, 50}`; consecutive path
  vertices `i, i+1` (`50 ≤ i ≤ 118`) are adjacent.

Edge count: `C(50,2) + 70 = 1225 + 70 = 1295`.

`distN u v` is the closed-form graph distance, proven below to coincide with
`SimpleGraph.dist` via two standard certificates:
* a 1-Lipschitz bound along edges (`distN_lipschitz`), giving the lower bound
  on any walk length, and
* a BFS "parent" certificate (`exists_parent`), giving a walk of length
  exactly `distN u v`.

All certificate lemmas are proven by linear-arithmetic case analysis
(`omega`), with no `decide` on large search spaces and no `native_decide`.
-/
import Mathlib

namespace P07

/-- Adjacency on the underlying naturals: clique pairs, path edges, and the
attachment edge `{49, 50}`. -/
def adjN (u v : ℕ) : Prop :=
  (u < 50 ∧ v < 50 ∧ u ≠ v) ∨
  (50 ≤ u ∧ 50 ≤ v ∧ v < 120 ∧ u < 120 ∧ (u + 1 = v ∨ v + 1 = u)) ∨
  (u = 49 ∧ v = 50) ∨ (u = 50 ∧ v = 49)

instance : DecidableRel adjN := fun _ _ => by unfold adjN; infer_instance

/-- Closed-form graph distance on the lollipop.
For two clique vertices the distance is `1`; for two path vertices it is
`|u - v|` (written `(u - v) + (v - u)` in truncated ℕ subtraction); a clique
vertex `u` and a path vertex `v` are at distance `(v - 49) + 1`, except that
the attachment vertex `49` saves the `+1`. -/
def distN (u v : ℕ) : ℕ :=
  if u = v then 0
  else if u < 50 ∧ v < 50 then 1
  else if u < 50 then (v - 49) + (if u = 49 then 0 else 1)
  else if v < 50 then (u - 49) + (if v = 49 then 0 else 1)
  else (u - v) + (v - u)

lemma distN_self (u : ℕ) : distN u u = 0 := by unfold distN; simp

lemma distN_comm (u v : ℕ) : distN u v = distN v u := by
  unfold distN; split_ifs <;> omega

lemma eq_of_distN_eq_zero {u v : ℕ} (h : distN u v = 0) : u = v := by
  unfold distN at h; split_ifs at h <;> omega

/-- 1-Lipschitz certificate: crossing one edge changes `distN u ·` by at
most one. -/
lemma distN_lipschitz {u v w : ℕ} (h : adjN v w) :
    distN u v ≤ distN u w + 1 := by
  unfold adjN at h
  unfold distN
  split_ifs <;> omega

/-- BFS parent certificate: if `distN u v ≠ 0` there is a neighbour `w` of
`v` one step closer to `u`. -/
lemma exists_parent {u v : ℕ} (hu : u < 120) (hv : v < 120)
    (h : distN u v ≠ 0) :
    ∃ w, w < 120 ∧ adjN w v ∧ distN u w + 1 = distN u v := by
  have huv : u ≠ v := fun he => h (he ▸ distN_self u)
  by_cases hv50 : v < 50
  · by_cases hu50 : u < 50
    · exact ⟨u, hu, Or.inl ⟨hu50, hv50, huv⟩, by unfold distN; split_ifs <;> omega⟩
    · by_cases hv49 : v = 49
      · exact ⟨50, by omega,
          Or.inr (Or.inr (Or.inr ⟨rfl, hv49⟩)),
          by unfold distN; split_ifs <;> omega⟩
      · exact ⟨49, by omega, Or.inl ⟨by omega, hv50, by omega⟩,
          by unfold distN; split_ifs <;> omega⟩
  · by_cases hu50 : u < 50
    · by_cases hv50' : v = 50
      · exact ⟨49, by omega,
          Or.inr (Or.inr (Or.inl ⟨rfl, hv50'⟩)),
          by unfold distN; split_ifs <;> omega⟩
      · exact ⟨v - 1, by omega,
          Or.inr (Or.inl ⟨by omega, by omega, hv, by omega, by omega⟩),
          by unfold distN; split_ifs <;> omega⟩
    · by_cases hlt : u < v
      · exact ⟨v - 1, by omega,
          Or.inr (Or.inl ⟨by omega, by omega, hv, by omega, by omega⟩),
          by unfold distN; split_ifs <;> omega⟩
      · exact ⟨v + 1, by omega,
          Or.inr (Or.inl ⟨by omega, by omega, hv, by omega, by omega⟩),
          by unfold distN; split_ifs <;> omega⟩

/-- The lollipop graph `L(K₅₀, P₇₀)` on `Fin 120`. -/
def lollipop : SimpleGraph (Fin 120) where
  Adj u v := adjN u.val v.val
  symm := ⟨by intro u v h; unfold adjN at *; omega⟩
  loopless := ⟨by intro u h; unfold adjN at h; omega⟩

instance : DecidableRel lollipop.Adj := fun u v =>
  inferInstanceAs (Decidable (adjN u.val v.val))

lemma adj_iff {u v : Fin 120} : lollipop.Adj u v ↔ adjN u.val v.val := Iff.rfl

/-- Lower bound: every walk from `u` to `v` has length at least `distN`. -/
lemma distN_le_walk_length {u v : Fin 120} (p : lollipop.Walk u v) :
    distN u.val v.val ≤ p.length := by
  induction p with
  | nil => simp [distN_self]
  | @cons a b c hab q ih =>
      have h1 : distN a.val b.val ≤ 1 := by
        have : adjN a.val b.val := hab
        unfold adjN at this; unfold distN; split_ifs <;> omega
      calc distN a.val c.val
          ≤ distN b.val c.val + 1 := by
            rw [distN_comm a.val c.val, distN_comm b.val c.val]
            exact distN_lipschitz (adj_iff.mp hab)
        _ ≤ q.length + 1 := by omega
        _ = (SimpleGraph.Walk.cons hab q).length := by
            simp [SimpleGraph.Walk.length_cons]

/-- Upper bound: an explicit walk of length exactly `distN u v`, built by
recursion on the BFS parent certificate. -/
lemma exists_walk_distN (u v : Fin 120) :
    ∃ p : lollipop.Walk u v, p.length = distN u.val v.val := by
  generalize hd : distN u.val v.val = d
  induction d generalizing v with
  | zero =>
      have : u = v := Fin.ext (eq_of_distN_eq_zero hd)
      subst this
      exact ⟨SimpleGraph.Walk.nil, rfl⟩
  | succ k ih =>
      obtain ⟨w, hw120, hadj, hwk⟩ :=
        exists_parent u.isLt v.isLt (by omega : distN u.val v.val ≠ 0)
      have hwk' : distN u.val (⟨w, hw120⟩ : Fin 120).val = k := by
        simpa [hd] using hwk
      obtain ⟨q, hq⟩ := ih ⟨w, hw120⟩ hwk'
      exact ⟨q.concat hadj, by simp [SimpleGraph.Walk.length_concat, hq]⟩

lemma lollipop_reachable (u v : Fin 120) : lollipop.Reachable u v :=
  (exists_walk_distN u v).elim fun p _ => ⟨p⟩

theorem lollipop_connected : lollipop.Connected :=
  SimpleGraph.Connected.mk lollipop_reachable

/-- The graph distance of the lollipop equals the closed form `distN`. -/
theorem lollipop_dist_eq (u v : Fin 120) :
    lollipop.dist u v = distN u.val v.val := by
  obtain ⟨p, hp⟩ := exists_walk_distN u v
  refine le_antisymm (hp ▸ SimpleGraph.dist_le p) ?_
  obtain ⟨q, hq⟩ := (lollipop_reachable u v).exists_walk_length_eq_dist
  exact hq ▸ distN_le_walk_length q

end P07

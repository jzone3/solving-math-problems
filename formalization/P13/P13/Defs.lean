/-
P13: (9,6,1)-perfect Mendelsohn designs — definitions.

A (v,k,λ)-perfect Mendelsohn design (Abel–Bennett, Des. Codes Cryptogr. 40 (2006);
Bennett–Zwicker–Chang, Discrete Math. 309 (2009)) is a collection of cyclically
ordered k-tuples ("blocks") of *distinct* points of a v-set such that for every
t = 1, …, k−1, every ordered pair of distinct points appears "t-apart" (i.e. at
cyclic distance t within a block) in exactly λ blocks.

Here λ = 1.  We model a design with b blocks as a family
`B : Fin b → Fin k → Fin v`; positions within a block live in `Fin k`, and the
cyclic distance-t successor of position p is `p + t` (addition in `Fin k` is
mod-k, which is exactly the cyclic structure of a Mendelsohn block).

Note that a family (rather than a set/multiset) of blocks is fully general: for
λ = 1 no block can repeat (a repeated block would cover its distance-1 pairs
twice), and the coverage conditions are invariant under reindexing blocks.
-/
import Mathlib

namespace P13

/-- `B : Fin b → Fin k → Fin v` is a (v,k,1)-perfect Mendelsohn design:
* the k points of each block are pairwise distinct, and
* for every cyclic distance `t ≠ 0` and every ordered pair `(u, w)` of distinct
  points there is exactly one slot (block `bl`, position `p`) with `u` at
  position `p` and `w` at position `p + t`. -/
def IsPMD1 {v k b : ℕ} (B : Fin b → Fin k → Fin v) : Prop :=
  (∀ bl : Fin b, Function.Injective (B bl)) ∧
  ∀ t : Fin k, t.val ≠ 0 → ∀ u w : Fin v, u ≠ w →
    ∃! s : Fin b × Fin k, B s.1 s.2 = u ∧ B s.1 (s.2 + t) = w

/-- A (v,k,1)-PMD exists (with some number `b` of blocks). -/
def PMD1Exists (v k : ℕ) : Prop :=
  ∃ (b : ℕ) (B : Fin b → Fin k → Fin v), IsPMD1 B

/-- Counting forced block count for (9,6,1): the slots (block, position) are
in bijection with the 72 ordered pairs of distinct points via the distance-1
pairs, so `b * 6 = 72`, i.e. `b = 12`. -/
theorem block_count₉ {b : ℕ} (B : Fin b → Fin 6 → Fin 9)
    (h : IsPMD1 B) : b = 12 := by
  obtain ⟨hinj, hcov⟩ := h
  have h1ne : (1 : Fin 6).val ≠ 0 := by decide
  have hpne : ∀ p : Fin 6, p ≠ p + 1 := by decide
  -- the map from slots to ordered pairs of distinct points at distance 1
  let f : Fin b × Fin 6 → {p : Fin 9 × Fin 9 // p.1 ≠ p.2} := fun s =>
    ⟨(B s.1 s.2, B s.1 (s.2 + 1)), fun hEq => hpne s.2 (hinj s.1 hEq)⟩
  have hbij : Function.Bijective f := by
    constructor
    · intro s1 s2 hEq
      have hval := congrArg Subtype.val hEq
      have hu : B s1.1 s1.2 = B s2.1 s2.2 := congrArg Prod.fst hval
      have hw : B s1.1 (s1.2 + 1) = B s2.1 (s2.2 + 1) := congrArg Prod.snd hval
      have hne : B s2.1 s2.2 ≠ B s2.1 (s2.2 + 1) := (f s2).2
      obtain ⟨sw, _, huniq⟩ := hcov 1 h1ne (B s2.1 s2.2) (B s2.1 (s2.2 + 1)) hne
      have e1 := huniq s1 ⟨hu, hw⟩
      have e2 := huniq s2 ⟨rfl, rfl⟩
      rw [e1, e2]
    · intro ⟨⟨u, w⟩, hne⟩
      obtain ⟨s, ⟨h1, h2⟩, _⟩ := hcov 1 h1ne u w hne
      exact ⟨s, by simp only [f]; exact Subtype.ext (by simp [h1, h2])⟩
  have hcard := Fintype.card_of_bijective hbij
  have hL : Fintype.card (Fin b × Fin 6) = b * 6 := by simp
  have hR : Fintype.card {p : Fin 9 × Fin 9 // p.1 ≠ p.2} = 72 := by
    rw [Fintype.card_subtype]
    decide
  omega

end P13

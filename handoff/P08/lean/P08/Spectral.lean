/-
Spectral counting lemma: if a real symmetric matrix `A` has an `m`-dimensional
subspace on which the quadratic form `x ⬝ᵥ A *ᵥ x` is positive definite, then
`A` has at least `m` positive eigenvalues (and symmetrically for negative).

This is the half of Cauchy interlacing / Sylvester inertia we need: it will be
applied to the subspace spanned by suitable vectors supported on an induced
path of `G`, giving `⌊(d+1)/2⌋ ≤ n⁺(G)` and `⌊(d+1)/2⌋ ≤ n⁻(G)`.
-/
import Mathlib

open Finset Matrix Module

namespace P08

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The quadratic form of a matrix, `x ⬝ᵥ A *ᵥ x`. -/
def quadForm (A : Matrix V V ℝ) (x : V → ℝ) : ℝ := x ⬝ᵥ (A *ᵥ x)

local notation "⟪" x ", " y "⟫" => inner ℝ x y

lemma inner_eq_dotProduct (x y : EuclideanSpace ℝ V) :
    ⟪x, y⟫ = (WithLp.ofLp x) ⬝ᵥ (WithLp.ofLp y) := by
  simp [PiLp.inner_apply, dotProduct, mul_comm]

lemma sum_smul_dotProduct_orthonormal {ι : Type*} [Fintype ι] [DecidableEq ι]
    (u : ι → V → ℝ) (horth : ∀ i j, u i ⬝ᵥ u j = if i = j then 1 else 0)
    (c d : ι → ℝ) :
    (∑ j, c j • u j) ⬝ᵥ (∑ i, d i • u i) = ∑ i, c i * d i := by
  simp only [sum_dotProduct, dotProduct_sum, smul_dotProduct,
    dotProduct_smul, horth, smul_eq_mul, mul_ite, mul_one, mul_zero,
    Finset.sum_ite_eq, Finset.sum_ite_eq', Finset.mem_univ, if_true]
  exact Finset.sum_congr rfl fun i _ => mul_comm _ _

variable {A : Matrix V V ℝ} (hA : A.IsHermitian)

/-- Eigen-expansion of the quadratic form: writing `x` in the orthonormal
eigenbasis of `A`, the quadratic form is `∑ μᵢ ⟪bᵢ, x⟫²`. -/
lemma quadForm_eq_sum_eigenvalues (x : EuclideanSpace ℝ V) :
    quadForm A (WithLp.ofLp x)
      = ∑ i, hA.eigenvalues i * ⟪hA.eigenvectorBasis i, x⟫ ^ 2 := by
  set b := hA.eigenvectorBasis with hb
  set μ := hA.eigenvalues with hμ
  have hx : x = ∑ i, ⟪b i, x⟫ • b i := (b.sum_repr' x).symm
  have hofLp : (WithLp.ofLp x : V → ℝ) = ∑ i, ⟪b i, x⟫ • (WithLp.ofLp (b i)) := by
    conv_lhs => rw [hx]
    rw [WithLp.ofLp_sum]
    simp
  have hmul : A *ᵥ (WithLp.ofLp x) = ∑ i, (⟪b i, x⟫ * μ i) • (WithLp.ofLp (b i)) := by
    rw [hofLp, mulVec_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [mulVec_smul, hA.mulVec_eigenvectorBasis, smul_smul]
  have horth : ∀ i j, (WithLp.ofLp (b i) : V → ℝ) ⬝ᵥ (WithLp.ofLp (b j))
      = if i = j then 1 else 0 := by
    intro i j
    rw [← inner_eq_dotProduct]
    exact orthonormal_iff_ite.mp b.orthonormal i j
  rw [quadForm, hmul, hofLp, sum_smul_dotProduct_orthonormal _ horth]
  exact Finset.sum_congr rfl fun i _ => by ring

open Classical in
/-- If the quadratic form of a real symmetric matrix is positive on a subspace
spanned by `m` linearly independent vectors, then `A` has at least `m`
positive eigenvalues. -/
theorem le_card_pos_eigenvalues {m : ℕ} (w : Fin m → EuclideanSpace ℝ V)
    (hw : LinearIndependent ℝ w)
    (hq : ∀ x : EuclideanSpace ℝ V,
      x ∈ Submodule.span ℝ (Set.range w) → x ≠ 0 → 0 < quadForm A (WithLp.ofLp x)) :
    m ≤ (Finset.univ.filter fun i => 0 < hA.eigenvalues i).card := by
  by_contra hlt
  push_neg at hlt
  set b := hA.eigenvectorBasis with hb
  set μ := hA.eigenvalues with hμ
  set S : Finset V := Finset.univ.filter (fun i => ¬ 0 < μ i) with hS
  set P : Submodule ℝ (EuclideanSpace ℝ V) :=
    Submodule.span ℝ (Set.range fun i : S => b i) with hP
  set W : Submodule ℝ (EuclideanSpace ℝ V) := Submodule.span ℝ (Set.range w) with hW
  have hsplit : (Finset.univ.filter fun i => 0 < μ i).card + S.card
      = Fintype.card V := by
    rw [hS, ← Finset.card_univ]
    exact Finset.card_filter_add_card_filter_not _
  have hfinW : finrank ℝ W = m := by
    rw [hW, finrank_span_eq_card hw, Fintype.card_fin]
  have hli : LinearIndependent ℝ (fun i : S => b (i : V)) :=
    b.orthonormal.linearIndependent.comp Subtype.val Subtype.val_injective
  have hfinP : finrank ℝ P = S.card := by
    rw [hP, finrank_span_eq_card hli, Fintype.card_coe]
  -- dimension count forces a nonzero vector in W ⊓ P
  have hn : finrank ℝ (EuclideanSpace ℝ V) = Fintype.card V := by
    simp [finrank_euclideanSpace]
  have hsum : finrank ℝ W + finrank ℝ P > finrank ℝ (EuclideanSpace ℝ V) := by
    rw [hfinW, hfinP, hn]
    omega
  have hint : 0 < finrank ℝ (W ⊓ P : Submodule ℝ (EuclideanSpace ℝ V)) := by
    have hle : finrank ℝ (W ⊔ P : Submodule ℝ (EuclideanSpace ℝ V))
        ≤ finrank ℝ (EuclideanSpace ℝ V) := Submodule.finrank_le _
    have heq := Submodule.finrank_sup_add_finrank_inf_eq W P
    omega
  have : Nontrivial (W ⊓ P : Submodule ℝ (EuclideanSpace ℝ V)) :=
    Module.finrank_pos_iff.mp hint
  obtain ⟨y, hy⟩ := exists_ne (0 : (W ⊓ P : Submodule ℝ (EuclideanSpace ℝ V)))
  have hyW : (y : EuclideanSpace ℝ V) ∈ W := (Submodule.mem_inf.mp y.2).1
  have hyP : (y : EuclideanSpace ℝ V) ∈ P := (Submodule.mem_inf.mp y.2).2
  have hyne : (y : EuclideanSpace ℝ V) ≠ 0 := fun h => hy (Subtype.ext h)
  -- positivity on W
  have hpos : 0 < quadForm A (WithLp.ofLp (y : EuclideanSpace ℝ V)) := hq _ hyW hyne
  -- nonpositivity on P: coordinates along positive eigenvectors vanish
  have hcoord : ∀ i : V, 0 < μ i → ⟪b i, (y : EuclideanSpace ℝ V)⟫ = 0 := by
    intro i hi
    refine Submodule.span_induction ?_ ?_ ?_ ?_ hyP
    · rintro x ⟨⟨j, hjS⟩, rfl⟩
      have hij : i ≠ j := by
        rintro rfl
        rw [hS] at hjS
        exact (Finset.mem_filter.mp hjS).2 hi
      have := orthonormal_iff_ite.mp b.orthonormal i j
      rwa [if_neg hij] at this
    · simp
    · intro u v _ _ hu hv
      rw [inner_add_right, hu, hv, add_zero]
    · intro c u _ hu
      rw [inner_smul_right, hu, mul_zero]
  have hnonpos : quadForm A (WithLp.ofLp (y : EuclideanSpace ℝ V)) ≤ 0 := by
    rw [quadForm_eq_sum_eigenvalues hA]
    refine Finset.sum_nonpos fun i _ => ?_
    by_cases hi : 0 < μ i
    · rw [hcoord i hi]
      simp
    · push_neg at hi
      exact mul_nonpos_of_nonpos_of_nonneg hi (sq_nonneg _)
  linarith

open Classical in
/-- Negative counterpart: an `m`-dimensional subspace on which the quadratic
form is negative definite forces at least `m` negative eigenvalues. -/
theorem le_card_neg_eigenvalues {m : ℕ} (w : Fin m → EuclideanSpace ℝ V)
    (hw : LinearIndependent ℝ w)
    (hq : ∀ x : EuclideanSpace ℝ V,
      x ∈ Submodule.span ℝ (Set.range w) → x ≠ 0 → quadForm A (WithLp.ofLp x) < 0) :
    m ≤ (Finset.univ.filter fun i => hA.eigenvalues i < 0).card := by
  by_contra hlt
  push_neg at hlt
  set b := hA.eigenvectorBasis with hb
  set μ := hA.eigenvalues with hμ
  set S : Finset V := Finset.univ.filter (fun i => ¬ μ i < 0) with hS
  set P : Submodule ℝ (EuclideanSpace ℝ V) :=
    Submodule.span ℝ (Set.range fun i : S => b i) with hP
  set W : Submodule ℝ (EuclideanSpace ℝ V) := Submodule.span ℝ (Set.range w) with hW
  have hsplit : (Finset.univ.filter fun i => μ i < 0).card + S.card
      = Fintype.card V := by
    rw [hS, ← Finset.card_univ]
    exact Finset.card_filter_add_card_filter_not _
  have hfinW : finrank ℝ W = m := by
    rw [hW, finrank_span_eq_card hw, Fintype.card_fin]
  have hli : LinearIndependent ℝ (fun i : S => b (i : V)) :=
    b.orthonormal.linearIndependent.comp Subtype.val Subtype.val_injective
  have hfinP : finrank ℝ P = S.card := by
    rw [hP, finrank_span_eq_card hli, Fintype.card_coe]
  have hn : finrank ℝ (EuclideanSpace ℝ V) = Fintype.card V := by
    simp [finrank_euclideanSpace]
  have hsum : finrank ℝ W + finrank ℝ P > finrank ℝ (EuclideanSpace ℝ V) := by
    rw [hfinW, hfinP, hn]
    omega
  have hint : 0 < finrank ℝ (W ⊓ P : Submodule ℝ (EuclideanSpace ℝ V)) := by
    have hle : finrank ℝ (W ⊔ P : Submodule ℝ (EuclideanSpace ℝ V))
        ≤ finrank ℝ (EuclideanSpace ℝ V) := Submodule.finrank_le _
    have heq := Submodule.finrank_sup_add_finrank_inf_eq W P
    omega
  have : Nontrivial (W ⊓ P : Submodule ℝ (EuclideanSpace ℝ V)) :=
    Module.finrank_pos_iff.mp hint
  obtain ⟨y, hy⟩ := exists_ne (0 : (W ⊓ P : Submodule ℝ (EuclideanSpace ℝ V)))
  have hyW : (y : EuclideanSpace ℝ V) ∈ W := (Submodule.mem_inf.mp y.2).1
  have hyP : (y : EuclideanSpace ℝ V) ∈ P := (Submodule.mem_inf.mp y.2).2
  have hyne : (y : EuclideanSpace ℝ V) ≠ 0 := fun h => hy (Subtype.ext h)
  have hneg : quadForm A (WithLp.ofLp (y : EuclideanSpace ℝ V)) < 0 := hq _ hyW hyne
  have hcoord : ∀ i : V, μ i < 0 → ⟪b i, (y : EuclideanSpace ℝ V)⟫ = 0 := by
    intro i hi
    refine Submodule.span_induction ?_ ?_ ?_ ?_ hyP
    · rintro x ⟨⟨j, hjS⟩, rfl⟩
      have hij : i ≠ j := by
        rintro rfl
        rw [hS] at hjS
        exact (Finset.mem_filter.mp hjS).2 hi
      have := orthonormal_iff_ite.mp b.orthonormal i j
      rwa [if_neg hij] at this
    · simp
    · intro u v _ _ hu hv
      rw [inner_add_right, hu, hv, add_zero]
    · intro c u _ hu
      rw [inner_smul_right, hu, mul_zero]
  have hnonneg : 0 ≤ quadForm A (WithLp.ofLp (y : EuclideanSpace ℝ V)) := by
    rw [quadForm_eq_sum_eigenvalues hA]
    refine Finset.sum_nonneg fun i _ => ?_
    by_cases hi : μ i < 0
    · rw [hcoord i hi]
      simp
    · push_neg at hi
      exact mul_nonneg hi (sq_nonneg _)
  linarith

end P08

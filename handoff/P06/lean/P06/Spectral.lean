/-
Spectral toolkit for WoW conjecture 698:

* `dotProduct_mulVec_eq_sum_eigenvalues` / `dotProduct_self_eq_sum`:
  eigen-expansion of the quadratic form `x ⬝ᵥ A *ᵥ x` and of `x ⬝ᵥ x`
  in the orthonormal eigenbasis of a real symmetric matrix;
* `exists_eigenvalue_mul_ge` (Rayleigh): some eigenvalue `μ` satisfies
  `x ⬝ᵥ A *ᵥ x ≤ μ * (x ⬝ᵥ x)`;
* `sum_sq_eigenvalues_eq_trace_mul_self`: `∑ μᵢ² = trace (A * A)`.
-/
import Mathlib

open Finset Matrix

set_option linter.unusedSectionVars false

namespace P06

variable {V : Type*} [Fintype V] [DecidableEq V]

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
    Finset.sum_ite_eq', Finset.mem_univ, if_true]
  exact Finset.sum_congr rfl fun i _ => mul_comm _ _

variable {A : Matrix V V ℝ} (hA : A.IsHermitian)

lemma ofLp_eq_sum_inner_smul (x : EuclideanSpace ℝ V) :
    (WithLp.ofLp x : V → ℝ)
      = ∑ i, ⟪hA.eigenvectorBasis i, x⟫ • (WithLp.ofLp (hA.eigenvectorBasis i)) := by
  set b := hA.eigenvectorBasis with hb
  have hx : x = ∑ i, ⟪b i, x⟫ • b i := (b.sum_repr' x).symm
  conv_lhs => rw [hx]
  rw [WithLp.ofLp_sum]
  simp

lemma eigenvectorBasis_dotProduct_orthonormal :
    ∀ i j, (WithLp.ofLp (hA.eigenvectorBasis i) : V → ℝ)
        ⬝ᵥ (WithLp.ofLp (hA.eigenvectorBasis j)) = if i = j then 1 else 0 := by
  intro i j
  rw [← inner_eq_dotProduct]
  exact orthonormal_iff_ite.mp hA.eigenvectorBasis.orthonormal i j

/-- Eigen-expansion of the quadratic form: writing `x` in the orthonormal
eigenbasis of `A`, the quadratic form is `∑ μᵢ ⟪bᵢ, x⟫²`. -/
lemma dotProduct_mulVec_eq_sum_eigenvalues (x : EuclideanSpace ℝ V) :
    (WithLp.ofLp x) ⬝ᵥ (A *ᵥ WithLp.ofLp x)
      = ∑ i, hA.eigenvalues i * ⟪hA.eigenvectorBasis i, x⟫ ^ 2 := by
  set b := hA.eigenvectorBasis with hb
  set μ := hA.eigenvalues with hμ
  have hofLp := ofLp_eq_sum_inner_smul hA x
  have hmul : A *ᵥ (WithLp.ofLp x) = ∑ i, (⟪b i, x⟫ * μ i) • (WithLp.ofLp (b i)) := by
    rw [hofLp, mulVec_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    rw [mulVec_smul, hA.mulVec_eigenvectorBasis, smul_smul]
  rw [hmul, hofLp, sum_smul_dotProduct_orthonormal _
    (eigenvectorBasis_dotProduct_orthonormal hA)]
  exact Finset.sum_congr rfl fun i _ => by ring

/-- Parseval: `x ⬝ᵥ x = ∑ ⟪bᵢ, x⟫²` in the orthonormal eigenbasis. -/
lemma dotProduct_self_eq_sum (x : EuclideanSpace ℝ V) :
    (WithLp.ofLp x) ⬝ᵥ (WithLp.ofLp x : V → ℝ)
      = ∑ i, ⟪hA.eigenvectorBasis i, x⟫ ^ 2 := by
  have hofLp := ofLp_eq_sum_inner_smul hA x
  rw [hofLp, sum_smul_dotProduct_orthonormal _
    (eigenvectorBasis_dotProduct_orthonormal hA)]
  exact Finset.sum_congr rfl fun i _ => (sq _).symm

/-- **Rayleigh quotient bound**: some eigenvalue `μ` of the real symmetric
matrix `A` satisfies `x ⬝ᵥ A *ᵥ x ≤ μ * (x ⬝ᵥ x)`. -/
theorem exists_eigenvalue_mul_ge [Nonempty V] (x : V → ℝ) :
    ∃ i, x ⬝ᵥ (A *ᵥ x) ≤ hA.eigenvalues i * (x ⬝ᵥ x) := by
  obtain ⟨i0, -, hmax⟩ :=
    Finset.exists_max_image Finset.univ hA.eigenvalues univ_nonempty
  refine ⟨i0, ?_⟩
  set y : EuclideanSpace ℝ V := (WithLp.linearEquiv 2 ℝ (V → ℝ)).symm x with hy
  have hxy : (WithLp.ofLp y : V → ℝ) = x := rfl
  have h1 := dotProduct_mulVec_eq_sum_eigenvalues hA y
  have h2 := dotProduct_self_eq_sum hA y
  rw [hxy] at h1 h2
  rw [h1, h2, Finset.mul_sum]
  exact Finset.sum_le_sum fun i _ =>
    mul_le_mul_of_nonneg_right (hmax i (Finset.mem_univ i)) (sq_nonneg _)

/-- The sum of the squared eigenvalues of a real symmetric matrix is the
trace of its square. -/
theorem sum_sq_eigenvalues_eq_trace_mul_self :
    ∑ i, hA.eigenvalues i ^ 2 = (A * A).trace := by
  conv_rhs => rw [hA.spectral_theorem, ← map_mul, Unitary.conjStarAlgAut_apply]
  rw [Matrix.trace_mul_cycle, ← Matrix.mul_assoc, Unitary.coe_star_mul_self,
    Matrix.one_mul, Matrix.diagonal_mul_diagonal, Matrix.trace_diagonal]
  simp [RCLike.ofReal_real_eq_id, sq]

end P06

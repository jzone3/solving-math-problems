/-
Popoviciu's inequality on variances, in the discrete population form used here:
for a finite family of reals all lying in `[a, b]`, the population variance is
at most `((b - a) / 2)^2`, hence the population standard deviation is at most
`(b - a) / 2`.
-/
import Mathlib

open Finset

namespace P08

variable {ι : Type*} [Fintype ι]

/-- Population mean of a finite family of reals. -/
noncomputable def popMean (f : ι → ℝ) : ℝ :=
  (∑ i, f i) / (Fintype.card ι)

/-- Population variance of a finite family of reals. -/
noncomputable def popVariance (f : ι → ℝ) : ℝ :=
  (∑ i, (f i - popMean f) ^ 2) / (Fintype.card ι)

/-- Population standard deviation of a finite family of reals. -/
noncomputable def popStdDev (f : ι → ℝ) : ℝ :=
  Real.sqrt (popVariance f)

lemma popVariance_nonneg (f : ι → ℝ) : 0 ≤ popVariance f :=
  div_nonneg (Finset.sum_nonneg fun i _ => sq_nonneg _) (Nat.cast_nonneg _)

/-- Popoviciu's inequality: if all values lie in `[a, b]` then the population
variance is at most `((b - a) / 2)^2`. -/
theorem popVariance_le_of_mem_Icc [Nonempty ι] {f : ι → ℝ} {a b : ℝ}
    (h : ∀ i, f i ∈ Set.Icc a b) : popVariance f ≤ ((b - a) / 2) ^ 2 := by
  set N : ℝ := (Fintype.card ι : ℝ) with hN
  have hNpos : 0 < N := by
    have h0 : 0 < Fintype.card ι := Fintype.card_pos
    rw [hN]
    exact_mod_cast h0
  set μ : ℝ := popMean f with hμ
  have hsum : ∑ i, f i = N * μ := by
    rw [hμ, popMean, ← hN]
    field_simp
  -- ∑ (b - f i) * (f i - a) ≥ 0
  have key : 0 ≤ ∑ i : ι, (b - f i) * (f i - a) :=
    Finset.sum_nonneg fun i _ =>
      mul_nonneg (by linarith [(h i).2]) (by linarith [(h i).1])
  -- expand: ∑ f i ^ 2 ≤ (a + b) * (N * μ) - N * (a * b)
  have expand : ∑ i : ι, (b - f i) * (f i - a)
      = (a + b) * (N * μ) - N * (a * b) - ∑ i, f i ^ 2 := by
    have : ∑ i : ι, (b - f i) * (f i - a)
        = (a + b) * (∑ i, f i) - (Fintype.card ι : ℝ) * (a * b) - ∑ i, f i ^ 2 := by
      rw [Finset.sum_congr rfl (fun i _ => show (b - f i) * (f i - a)
            = (a + b) * f i - a * b - f i ^ 2 by ring)]
      rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum,
        Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
    rw [this, hsum, ← hN]
  have hsq : ∑ i, f i ^ 2 ≤ (a + b) * (N * μ) - N * (a * b) := by
    have := key
    rw [expand] at this
    linarith
  -- variance = (∑ f²)/N - μ²
  have hvar : popVariance f = (∑ i, f i ^ 2) / N - μ ^ 2 := by
    rw [popVariance, ← hN, ← hμ]
    have : ∑ i, (f i - μ) ^ 2 = ∑ i, f i ^ 2 - 2 * μ * ∑ i, f i + N * μ ^ 2 := by
      rw [Finset.sum_congr rfl (fun i _ => show (f i - μ) ^ 2
            = f i ^ 2 - 2 * μ * f i + μ ^ 2 by ring)]
      rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, ← Finset.mul_sum,
        Finset.sum_const, Finset.card_univ, nsmul_eq_mul, ← hN]
    rw [this, hsum]
    field_simp
    ring
  -- Var ≤ (b - μ)(μ - a) ≤ ((b-a)/2)^2
  have step1 : popVariance f ≤ (b - μ) * (μ - a) := by
    rw [hvar]
    have h2 : (∑ i, f i ^ 2) / N ≤ (a + b) * μ - a * b := by
      rw [div_le_iff₀ hNpos]
      calc ∑ i, f i ^ 2 ≤ (a + b) * (N * μ) - N * (a * b) := hsq
        _ = ((a + b) * μ - a * b) * N := by ring
    nlinarith [h2]
  have step2 : (b - μ) * (μ - a) ≤ ((b - a) / 2) ^ 2 := by
    nlinarith [sq_nonneg (b + a - 2 * μ)]
  linarith

/-- Standard-deviation form of Popoviciu's inequality. -/
theorem popStdDev_le_of_mem_Icc [Nonempty ι] {f : ι → ℝ} {a b : ℝ}
    (h : ∀ i, f i ∈ Set.Icc a b) : popStdDev f ≤ (b - a) / 2 := by
  have hab : a ≤ b := by
    obtain ⟨i⟩ := ‹Nonempty ι›
    exact le_trans (h i).1 (h i).2
  have hba : 0 ≤ (b - a) / 2 := by linarith
  rw [popStdDev, show (b - a) / 2 = Real.sqrt (((b - a) / 2) ^ 2) by
    rw [Real.sqrt_sq hba]]
  exact Real.sqrt_le_sqrt (popVariance_le_of_mem_Icc h)

end P08

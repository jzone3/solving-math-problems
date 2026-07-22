/-
From an induced path `x 0, …, x d` in `G` (an induced geodesic), we build
`m = ⌊(d+1)/2⌋` linearly independent vectors on which the adjacency quadratic
form is positive definite (resp. negative definite): the `t`-th vector is
`e_{x(2t)} + e_{x(2t+1)}` (resp. `e_{x(2t)} - e_{x(2t+1)}`).

The value of the quadratic form on `∑ cₜ • wₜ` is
`±(2∑ cₜ² + 2∑ cₜcₜ₊₁) = ±(c₀² + c_{m-1}² + ∑ (cₜ + cₜ₊₁)²)`,
which is definite. Combined with `P08.le_card_pos_eigenvalues` /
`P08.le_card_neg_eigenvalues` this yields
`⌊(d+1)/2⌋ ≤ n⁺(G)` and `⌊(d+1)/2⌋ ≤ n⁻(G)`.
-/
import Mathlib
import P08.Spectral

open Finset Matrix SimpleGraph

namespace P08

/-- Positivity of the tridiagonal quadratic form
`2 ∑_{i<m} cᵢ² + 2 ∑_{i<m-1} cᵢ cᵢ₊₁`, via the sum-of-squares identity
`… = c₀² + c_{m-1}² + ∑_{i<m-1} (cᵢ + cᵢ₊₁)²`. -/
lemma tridiag_pos {m : ℕ} (hm : 0 < m) (c : ℕ → ℝ) (hc : ∃ i, i < m ∧ c i ≠ 0) :
    0 < 2 * ∑ i ∈ Finset.range m, c i ^ 2
      + 2 * ∑ i ∈ Finset.range (m - 1), c i * c (i + 1) := by
  obtain ⟨k, rfl⟩ : ∃ k, m = k + 1 := ⟨m - 1, by omega⟩
  simp only [Nat.add_sub_cancel]
  have h1 : ∑ i ∈ Finset.range (k + 1), c i ^ 2
      = ∑ i ∈ Finset.range k, c i ^ 2 + c k ^ 2 := Finset.sum_range_succ _ k
  have h2 : ∑ i ∈ Finset.range (k + 1), c i ^ 2
      = ∑ i ∈ Finset.range k, c (i + 1) ^ 2 + c 0 ^ 2 := Finset.sum_range_succ' _ k
  have hexp : ∑ i ∈ Finset.range k, (c i + c (i + 1)) ^ 2
      = ∑ i ∈ Finset.range k, c i ^ 2 + ∑ i ∈ Finset.range k, c (i + 1) ^ 2
        + 2 * ∑ i ∈ Finset.range k, c i * c (i + 1) := by
    rw [Finset.sum_congr rfl fun i _ => show (c i + c (i + 1)) ^ 2
          = c i ^ 2 + c (i + 1) ^ 2 + 2 * (c i * c (i + 1)) by ring]
    rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum]
  -- the identity
  have hid : 2 * ∑ i ∈ Finset.range (k + 1), c i ^ 2
      + 2 * ∑ i ∈ Finset.range k, c i * c (i + 1)
      = c 0 ^ 2 + c k ^ 2 + ∑ i ∈ Finset.range k, (c i + c (i + 1)) ^ 2 := by
    linarith [h1, h2, hexp]
  rw [hid]
  -- nonnegativity of every term
  have hS : 0 ≤ ∑ i ∈ Finset.range k, (c i + c (i + 1)) ^ 2 :=
    Finset.sum_nonneg fun i _ => sq_nonneg _
  by_cases h : 0 < c 0 ^ 2 + c k ^ 2 + ∑ i ∈ Finset.range k, (c i + c (i + 1)) ^ 2
  · exact h
  push_neg at h
  -- otherwise everything vanishes and c = 0 below m, contradiction
  exfalso
  have h0 : c 0 ^ 2 = 0 := by nlinarith [sq_nonneg (c 0), sq_nonneg (c k)]
  have hSz : ∑ i ∈ Finset.range k, (c i + c (i + 1)) ^ 2 = 0 := by
    nlinarith [sq_nonneg (c 0), sq_nonneg (c k)]
  have hterm : ∀ i ∈ Finset.range k, (c i + c (i + 1)) ^ 2 = 0 :=
    (Finset.sum_eq_zero_iff_of_nonneg fun i _ => sq_nonneg _).mp hSz
  have hall : ∀ i, i < k + 1 → c i = 0 := by
    intro i
    induction i with
    | zero => intro _; exact pow_eq_zero_iff (n := 2) (by omega) |>.mp h0
    | succ n ih =>
      intro hn
      have hcn : c n = 0 := ih (by omega)
      have := hterm n (Finset.mem_range.mpr (by omega))
      have hsum0 : c n + c (n + 1) = 0 := pow_eq_zero_iff (n := 2) (by omega) |>.mp this
      linarith
  obtain ⟨i, hi, hne⟩ := hc
  exact hne (hall i hi)

/-- Bilinear expansion of the quadratic form over a finite combination. -/
lemma quadForm_sum {V : Type*} [Fintype V] {ι : Type*} (A : Matrix V V ℝ)
    (s : Finset ι) (e : ι → ℝ) (f : ι → V → ℝ) :
    quadForm A (∑ i ∈ s, e i • f i)
      = ∑ i ∈ s, ∑ j ∈ s, e i * e j * (f i ⬝ᵥ (A *ᵥ f j)) := by
  simp only [quadForm, mulVec_sum, mulVec_smul, sum_dotProduct, dotProduct_sum,
    smul_dotProduct, dotProduct_smul, smul_eq_mul]
  conv_rhs => rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Finset.mul_sum]
  exact Finset.sum_congr rfl fun j _ => by ring

lemma single_quad {V : Type*} [Fintype V] [DecidableEq V] (A : Matrix V V ℝ)
    (a b : V) : Pi.single a (1 : ℝ) ⬝ᵥ (A *ᵥ Pi.single b 1) = A a b := by
  rw [mulVec_single_one, single_dotProduct, one_mul, col_apply]

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

section Construction

variable {x : ℕ → V} {d : ℕ}
variable (hinj : ∀ i j, i ≤ d → j ≤ d → x i = x j → i = j)
variable (hadj : ∀ i j, i ≤ d → j ≤ d →
  (G.Adj (x i) (x j) ↔ (i = j + 1 ∨ j = i + 1)))

/-- Paired path vectors `e_{x(2i)} + ε • e_{x(2i+1)}`. -/
noncomputable def pathVec (x : ℕ → V) (ε : ℝ) (i : ℕ) : V → ℝ :=
  Pi.single (x (2 * i)) 1 + ε • Pi.single (x (2 * i + 1)) 1

include hadj in
/-- Entries of the adjacency matrix along the induced path. -/
lemma adjMatrix_path {i j : ℕ} (hi : i ≤ d) (hj : j ≤ d) :
    G.adjMatrix ℝ (x i) (x j) = if (i = j + 1 ∨ j = i + 1) then (1 : ℝ) else 0 := by
  rw [adjMatrix_apply]
  by_cases h : i = j + 1 ∨ j = i + 1
  · rw [if_pos ((hadj i j hi hj).mpr h), if_pos h]
  · rw [if_neg (fun hA => h ((hadj i j hi hj).mp hA)), if_neg h]

include hadj in
/-- The Gram-like matrix of the paired path vectors w.r.t. the adjacency
quadratic form is `ε` times the tridiagonal path matrix. -/
lemma pathVec_quad {ε : ℝ} (hε : ε * ε = 1) {m : ℕ} (hm : 2 * m ≤ d + 1)
    {i j : ℕ} (hi : i < m) (hj : j < m) :
    pathVec x ε i ⬝ᵥ (G.adjMatrix ℝ *ᵥ pathVec x ε j)
      = ε * ((if i = j then 2 else 0) + (if i = j + 1 then 1 else 0)
          + (if j = i + 1 then 1 else 0)) := by
  have hb1 : 2 * i ≤ d := by omega
  have hb2 : 2 * i + 1 ≤ d := by omega
  have hb3 : 2 * j ≤ d := by omega
  have hb4 : 2 * j + 1 ≤ d := by omega
  rw [pathVec, pathVec]
  rw [mulVec_add, mulVec_smul, dotProduct_add, add_dotProduct, add_dotProduct,
    dotProduct_smul, smul_dotProduct, smul_dotProduct, dotProduct_smul]
  rw [single_quad, single_quad, single_quad, single_quad]
  rw [adjMatrix_path hadj hb1 hb3, adjMatrix_path hadj hb1 hb4,
    adjMatrix_path hadj hb2 hb3, adjMatrix_path hadj hb2 hb4]
  have c1 : (2 * i = 2 * j + 1 ∨ 2 * j = 2 * i + 1) ↔ False :=
    ⟨fun h => by omega, False.elim⟩
  have c2 : (2 * i = 2 * j + 1 + 1 ∨ 2 * j + 1 = 2 * i + 1) ↔ (i = j + 1 ∨ i = j) :=
    ⟨fun h => by omega, fun h => by omega⟩
  have c3 : (2 * i + 1 = 2 * j + 1 ∨ 2 * j = 2 * i + 1 + 1) ↔ (i = j ∨ j = i + 1) :=
    ⟨fun h => by omega, fun h => by omega⟩
  have c4 : (2 * i + 1 = 2 * j + 1 + 1 ∨ 2 * j + 1 = 2 * i + 1 + 1) ↔ False :=
    ⟨fun h => by omega, False.elim⟩
  simp only [c1, c2, c3, c4, if_false]
  by_cases h1 : i = j
  · subst h1
    simp only [or_true, true_or, if_pos rfl, if_true,
      if_neg (show ¬ (i = i + 1) by omega), if_neg (show ¬ (i = i + 1 + 1) by omega)]
    ring
  · by_cases h2 : i = j + 1
    · have h3 : ¬ (j = i + 1) := by omega
      simp only [if_neg h1, if_pos h2, if_neg h3,
        if_pos (Or.inl h2 : i = j + 1 ∨ i = j),
        if_neg (show ¬ (i = j ∨ j = i + 1) by omega)]
      ring
    · by_cases h3 : j = i + 1
      · simp only [if_neg h1, if_neg h2, if_pos h3,
          if_neg (show ¬ (i = j + 1 ∨ i = j) by omega),
          if_pos (Or.inr h3 : i = j ∨ j = i + 1)]
        ring
      · simp only [if_neg h1, if_neg h2, if_neg h3,
          if_neg (show ¬ (i = j + 1 ∨ i = j) by omega),
          if_neg (show ¬ (i = j ∨ j = i + 1) by omega)]
        ring

include hinj in
/-- Value of `pathVec x ε t` at a path vertex of even index. -/
lemma pathVec_apply_even {m : ℕ} (hm : 2 * m ≤ d + 1) (ε : ℝ)
    {t s : ℕ} (ht : t < m) (hs : s < m) :
    pathVec x ε t (x (2 * s)) = if s = t then 1 else 0 := by
  rw [pathVec, Pi.add_apply, Pi.smul_apply, Pi.single_apply, Pi.single_apply]
  have h1 : (x (2 * s) = x (2 * t)) ↔ (2 * s = 2 * t) :=
    ⟨fun h => hinj _ _ (by omega) (by omega) h, fun h => by rw [h]⟩
  have h2 : ¬ (x (2 * s) = x (2 * t + 1)) := fun h => by
    have := hinj _ _ (by omega) (by omega) h
    omega
  rw [if_neg h2, smul_zero, add_zero]
  by_cases h : s = t
  · rw [if_pos (h1.mpr (by omega)), if_pos h]
  · rw [if_neg (fun hh => h (by have := h1.mp hh; omega)), if_neg h]

include hinj in
/-- The paired path vectors are linearly independent. -/
lemma pathVec_linearIndependent {m : ℕ} (hm : 2 * m ≤ d + 1) (ε : ℝ) :
    LinearIndependent ℝ (fun t : Fin m => pathVec x ε (t : ℕ)) := by
  rw [Fintype.linearIndependent_iff]
  intro g hg t
  have := congrFun hg (x (2 * (t : ℕ)))
  rw [Finset.sum_apply, Pi.zero_apply] at this
  rw [Finset.sum_congr rfl (fun s _ => by
    rw [Pi.smul_apply, pathVec_apply_even hinj hm ε s.isLt t.isLt,
      smul_eq_mul])] at this
  rw [Finset.sum_congr rfl (fun s _ => show
      g s * (if (t : ℕ) = (s : ℕ) then (1 : ℝ) else 0)
        = if s = t then g s else 0 by
    by_cases h : s = t
    · subst h
      rw [if_pos rfl, if_pos rfl, mul_one]
    · rw [if_neg (fun hh => h (Fin.ext hh.symm)), if_neg h, mul_zero])] at this
  rwa [Finset.sum_ite_eq' Finset.univ t g, if_pos (Finset.mem_univ t)] at this

include hinj hadj in
/-- Value of the adjacency quadratic form on a combination of paired path
vectors: `ε` times the tridiagonal form. -/
lemma quadForm_pathVec_combination {ε : ℝ} (hε : ε * ε = 1)
    {m : ℕ} (hm : 2 * m ≤ d + 1) (e : ℕ → ℝ) :
    quadForm (G.adjMatrix ℝ) (∑ i ∈ Finset.range m, e i • pathVec x ε i)
      = ε * (2 * ∑ i ∈ Finset.range m, e i ^ 2
          + 2 * ∑ i ∈ Finset.range (m - 1), e i * e (i + 1)) := by
  rw [quadForm_sum]
  rw [Finset.sum_congr rfl fun i hi => Finset.sum_congr rfl fun j hj => by
    rw [pathVec_quad hadj hε hm (Finset.mem_range.mp hi) (Finset.mem_range.mp hj)]]
  -- expand into three double sums
  have hsplit : ∀ i j : ℕ,
      e i * e j * (ε * ((if i = j then (2 : ℝ) else 0) + (if i = j + 1 then 1 else 0)
          + (if j = i + 1 then 1 else 0)))
      = ε * ((if i = j then 2 * (e i * e j) else 0)
          + (if i = j + 1 then e i * e j else 0)
          + (if j = i + 1 then e i * e j else 0)) := by
    intro i j
    split_ifs <;> ring
  rw [Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => hsplit i j]
  simp only [← Finset.mul_sum, Finset.sum_add_distrib]
  congr 1
  -- diagonal part
  have hdiag : ∑ i ∈ Finset.range m, ∑ j ∈ Finset.range m,
      (if i = j then 2 * (e i * e j) else 0) = 2 * ∑ i ∈ Finset.range m, e i ^ 2 := by
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.sum_congr rfl (fun j _ => show (if i = j then 2 * (e i * e j) else 0)
          = if j = i then 2 * (e i * e j) else 0 by
        by_cases h : i = j
        · rw [if_pos h, if_pos h.symm]
        · rw [if_neg h, if_neg (fun hh => h hh.symm)]),
      Finset.sum_ite_eq' (Finset.range m) i, if_pos hi]
    ring
  -- superdiagonal part (i = j + 1)
  have hsup : ∑ i ∈ Finset.range m, ∑ j ∈ Finset.range m,
      (if i = j + 1 then e i * e j else 0)
      = ∑ j ∈ Finset.range (m - 1), e j * e (j + 1) := by
    rw [Finset.sum_comm]
    have hj : ∀ j ∈ Finset.range m, ∑ i ∈ Finset.range m,
        (if i = j + 1 then e i * e j else 0)
        = if j + 1 < m then e (j + 1) * e j else 0 := by
      intro j _
      rw [Finset.sum_ite_eq' (Finset.range m) (j + 1) (fun i => e i * e j)]
      by_cases h : j + 1 < m
      · rw [if_pos (Finset.mem_range.mpr h), if_pos h]
      · rw [if_neg (fun hh => h (Finset.mem_range.mp hh)), if_neg h]
    rw [Finset.sum_congr rfl hj]
    rw [show Finset.range (m - 1) = (Finset.range m).filter (fun j => j + 1 < m) by
      ext j; simp only [Finset.mem_range, Finset.mem_filter]; omega]
    rw [Finset.sum_filter]
    exact Finset.sum_congr rfl fun j _ => by
      by_cases h : j + 1 < m
      · rw [if_pos h, if_pos h, mul_comm]
      · rw [if_neg h, if_neg h]
  -- subdiagonal part (j = i + 1)
  have hsub : ∑ i ∈ Finset.range m, ∑ j ∈ Finset.range m,
      (if j = i + 1 then e i * e j else 0)
      = ∑ i ∈ Finset.range (m - 1), e i * e (i + 1) := by
    have hi : ∀ i ∈ Finset.range m, ∑ j ∈ Finset.range m,
        (if j = i + 1 then e i * e j else 0)
        = if i + 1 < m then e i * e (i + 1) else 0 := by
      intro i _
      rw [Finset.sum_ite_eq' (Finset.range m) (i + 1) (fun j => e i * e j)]
      by_cases h : i + 1 < m
      · rw [if_pos (Finset.mem_range.mpr h), if_pos h]
      · rw [if_neg (fun hh => h (Finset.mem_range.mp hh)), if_neg h]
    rw [Finset.sum_congr rfl hi]
    rw [show Finset.range (m - 1) = (Finset.range m).filter (fun i => i + 1 < m) by
      ext i; simp only [Finset.mem_range, Finset.mem_filter]; omega]
    rw [Finset.sum_filter]
  rw [hdiag, hsup, hsub]
  ring

end Construction

end P08

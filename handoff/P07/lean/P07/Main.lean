/-
# Graffiti (WoW) conjecture 154 is FALSE: the lollipop L(K₅₀, P₇₀) witness

Original conjecture (Fajtlowicz, *Written on the Wall*, item 154):

> "deviation of eigenvalues < n / average distance."

The original WoW wording may also be read with a non-strict inequality
(`deviation of eigenvalues ≤ n / average distance`).  Both readings are
refuted here: the witness satisfies the STRICT reverse inequality
`dev > n/μ` (`graffiti_conjecture_154_false_le`), which refutes the
non-strict reading `dev ≤ n/μ` and a fortiori the strict reading
`dev < n/μ` (`graffiti_conjecture_154_false`).

Encoding conventions (documented against `runs/P07/v5/NOTES.md` and
`solutions/P07/verify.py`):

* **graph**: `P07.lollipop`, the lollipop `L(K₅₀, P₇₀)` on `n = 120`
  vertices: a 50-clique with a 70-edge pendant path (equivalently the
  dumbbell `D(2, 68, 50)` of `verify.py`, `WITNESSES_154[0]`), with
  `m = 1295` edges.
* **deviation of eigenvalues**: population standard deviation
  `√(∑ (λᵢ - mean)² / n)` of all `n` eigenvalues (with multiplicity) of the
  real adjacency matrix, enumerated by mathlib's spectral theorem
  (`hA.eigenvalues`).  Since `trace A = 0` and `trace A² = 2m`, this equals
  `√(2m/n)` — proven below, not assumed (`dev_eigenvalues_eq`).
* **average distance μ(D)**: mean of ALL `n² = 14400` ordered entries of the
  distance matrix, diagonal included (the Roucairol–Cazenave `rc`
  convention): `μ = S / n²` where `S = ∑ᵤ∑ᵥ dist(u,v) = 372120` is the
  ordered distance sum (the unordered sum over the `C(120,2)` pairs is
  `S/2 = 186060`).  This is the HARDER convention to violate; the classical
  `pair` convention `μ' = S / (n(n-1))` is violated a fortiori
  (`conjecture154_false_pair_convention`).
* **real-number form**: `dev < n/μ` with `dev = √(2m/n)` is (for positive
  quantities) equivalent to `2·m·μ² ≤ n³` up to the strict/non-strict
  boundary; we refute the WEAKER inequality `2·m·μ² ≤ n³`
  (`conjecture154_false_real_form`), hence a fortiori `dev < n/μ` is false
  (`graffiti_conjecture_154_false`).

The distance sum `S = 372120` is PROVEN inside Lean: `lollipop_dist_eq`
(file `P07/Lollipop.lean`) shows `SimpleGraph.dist` coincides with the
closed-form `distN` via Lipschitz + BFS-parent certificates, and the finite
sum of `distN` is evaluated by `decide` (plain kernel `decide`, NOT
`native_decide`).  Likewise `m = 1295` is proven by `decide` on
`edgeFinset.card`.  The core violation is the pure integer inequality
`2·m·S² > n³·(n²)²` (`conjecture154_int_violation`), i.e.
`358645832496000 > 358318080000000`.

No `sorry`, no extra axioms, no `native_decide` anywhere in this project.
-/
import Mathlib
import P07.Lollipop

open Finset Matrix SimpleGraph

namespace P07

set_option maxRecDepth 100000

/-! ## Exact integer invariants of the witness graph -/

/-- The lollipop `L(K₅₀, P₇₀)` has `m = 1295` edges (`C(50,2) + 70`).
Proven by plain kernel `decide`. -/
theorem lollipop_card_edges : lollipop.edgeFinset.card = 1295 := by decide

/-- The ordered distance sum of the closed-form distance is `372120`.
Proven by plain kernel `decide` (14400 evaluations of `distN`). -/
theorem distN_sum : (∑ u : Fin 120, ∑ v : Fin 120, distN u.val v.val) = 372120 := by
  decide

/-- The ordered distance sum (all `120² = 14400` ordered pairs, diagonal
included) of the ACTUAL graph metric of the lollipop is `S = 372120`. -/
theorem lollipop_distSum :
    (∑ u : Fin 120, ∑ v : Fin 120, lollipop.dist u v) = 372120 := by
  simp only [lollipop_dist_eq]
  exact distN_sum

/-- Equivalently, the unordered distance sum over the `C(120,2)` pairs of
distinct vertices is `186060 = 372120 / 2`. -/
theorem lollipop_distSum_unordered :
    (∑ u : Fin 120, ∑ v : Fin 120, lollipop.dist u v) = 2 * 186060 :=
  lollipop_distSum

/-! ## The core integer violation

Conjecture 154 in the real form `2·m·μ² ≤ n³` with `μ = S/n²` clears
denominators to `2·m·S² ≤ n³·(n²)²`.  The witness violates it: -/

/-- `2·m·S² > n³·(n²)²` for `m = 1295`, `S = 372120`, `n = 120`:
`358645832496000 > 358318080000000`. -/
theorem conjecture154_int_violation :
    2 * 1295 * 372120 ^ 2 > 120 ^ 3 * (120 ^ 2) ^ 2 := by norm_num

/-- The same violation for the classical `pair` convention `μ' = S/(n(n-1))`:
`2·m·S² > n³·(n(n-1))²`. -/
theorem conjecture154_int_violation_pair :
    2 * 1295 * 372120 ^ 2 > 120 ^ 3 * (120 * 119) ^ 2 := by norm_num

/-! ## Real-number forms -/

/-- The average distance `μ(D)` of the lollipop: mean of all `n²` ordered
entries of the distance matrix (diagonal included). -/
noncomputable def lollipopMu : ℝ :=
  (∑ u : Fin 120, ∑ v : Fin 120, (lollipop.dist u v : ℝ)) / 120 ^ 2

lemma cast_distSum :
    (∑ u : Fin 120, ∑ v : Fin 120, (lollipop.dist u v : ℝ)) = 372120 := by
  exact_mod_cast lollipop_distSum

lemma lollipopMu_eq : lollipopMu = 372120 / 14400 := by
  unfold lollipopMu
  rw [cast_distSum]
  norm_num

/-- **Refutation of conjecture 154, real-number form**: the lollipop
`L(K₅₀, P₇₀)` violates `2·m·μ(D)² ≤ n³` (with the actual edge count `m` and
the actual average distance `μ` of the graph). -/
theorem conjecture154_false_real_form :
    ¬ (2 * (lollipop.edgeFinset.card : ℝ) * lollipopMu ^ 2 ≤ 120 ^ 3) := by
  rw [lollipop_card_edges, lollipopMu_eq]
  norm_num

/-- The same refutation under the classical `pair` convention
`μ' = S/(n(n-1))` (a fortiori, since `μ' > μ`). -/
theorem conjecture154_false_pair_convention :
    ¬ (2 * (lollipop.edgeFinset.card : ℝ) *
        ((∑ u : Fin 120, ∑ v : Fin 120, (lollipop.dist u v : ℝ)) / (120 * 119)) ^ 2
          ≤ 120 ^ 3) := by
  rw [lollipop_card_edges, cast_distSum]
  norm_num

/-! ## The original eigenvalue-deviation form

`dev(eigenvalues) = √(2m/n)` because the adjacency matrix has trace `0` and
`trace A² = 2m`.  We prove this and derive the original statement's
negation: `dev(eigenvalues) ≥ n/μ` (indeed `>`). -/

/-- Population standard deviation of a finite family of reals. -/
noncomputable def popStdDev {ι : Type*} [Fintype ι] (f : ι → ℝ) : ℝ :=
  Real.sqrt ((∑ i, (f i - (∑ j, f j) / Fintype.card ι) ^ 2) / Fintype.card ι)

lemma adjMatrix_isHermitian : ((lollipop.adjMatrix ℝ)).IsHermitian :=
  Matrix.isHermitian_iff_isSymm.mpr (SimpleGraph.isSymm_adjMatrix lollipop)

/-- Conjugation by a unitary preserves the trace. -/
lemma trace_conjStarAlgAut {n : Type*} [Fintype n] [DecidableEq n]
    (U : unitary (Matrix n n ℝ)) (X : Matrix n n ℝ) :
    (Unitary.conjStarAlgAut ℝ _ U X).trace = X.trace := by
  rw [Unitary.conjStarAlgAut_apply, Matrix.trace_mul_cycle,
    Unitary.coe_star_mul_self, Matrix.one_mul]

/-- Sum of the eigenvalues of a real symmetric matrix equals its trace. -/
lemma sum_eigenvalues {n : Type*} [Fintype n] [DecidableEq n]
    {A : Matrix n n ℝ} (hA : A.IsHermitian) :
    (∑ i, hA.eigenvalues i) = A.trace := by
  simpa using (hA.trace_eq_sum_eigenvalues (𝕜 := ℝ)).symm

/-- Sum of the squared eigenvalues of a real symmetric matrix equals the
trace of its square (via the spectral theorem). -/
lemma sum_sq_eigenvalues {n : Type*} [Fintype n] [DecidableEq n]
    {A : Matrix n n ℝ} (hA : A.IsHermitian) :
    (∑ i, hA.eigenvalues i ^ 2) = (A * A).trace := by
  conv_rhs => rw [hA.spectral_theorem]
  rw [← map_mul, trace_conjStarAlgAut, Matrix.diagonal_mul_diagonal,
    Matrix.trace_diagonal]
  simp [pow_two]

/-- `trace A² = 2m` for the adjacency matrix of the lollipop. -/
lemma trace_sq_adjMatrix :
    ((lollipop.adjMatrix ℝ) * (lollipop.adjMatrix ℝ)).trace = 2 * 1295 := by
  have h : ∀ i : Fin 120,
      ((lollipop.adjMatrix ℝ) * (lollipop.adjMatrix ℝ)) i i
        = (lollipop.degree i : ℝ) :=
    fun i => lollipop.adjMatrix_mul_self_apply_self i
  rw [Matrix.trace]
  simp only [Matrix.diag_apply, h]
  rw [← Nat.cast_sum, SimpleGraph.sum_degrees_eq_twice_card_edges,
    lollipop_card_edges]
  norm_num

/-- The deviation of the eigenvalues of the lollipop is exactly `√(2m/n)`:
mean `0` (trace zero) and second moment `2m/n`. -/
theorem dev_eigenvalues_eq :
    popStdDev (adjMatrix_isHermitian.eigenvalues) = Real.sqrt (2 * 1295 / 120) := by
  unfold popStdDev
  have hsum : (∑ i, adjMatrix_isHermitian.eigenvalues i) = 0 := by
    rw [sum_eigenvalues adjMatrix_isHermitian, SimpleGraph.trace_adjMatrix]
  have hsq : (∑ i, adjMatrix_isHermitian.eigenvalues i ^ 2) = 2 * 1295 := by
    rw [sum_sq_eigenvalues adjMatrix_isHermitian, trace_sq_adjMatrix]
  rw [show (Fintype.card (Fin 120)) = 120 from rfl]
  rw [hsum]
  norm_num [hsq]

/-- **Graffiti conjecture 154 is FALSE** (original wording): for the lollipop
`L(K₅₀, P₇₀)` the deviation of the adjacency eigenvalues is NOT less than
`n / μ(D)`; in fact it is strictly greater. -/
theorem graffiti_conjecture_154_false :
    ¬ (popStdDev (adjMatrix_isHermitian.eigenvalues) < 120 / lollipopMu) := by
  rw [dev_eigenvalues_eq, lollipopMu_eq, not_lt]
  rw [show (120 : ℝ) / (372120 / 14400) = 1728000 / 372120 by norm_num]
  rw [show (2 * 1295 / 120 : ℝ) = 2590 / 120 by norm_num]
  have h1 : (0 : ℝ) ≤ 1728000 / 372120 := by norm_num
  have h2 : (1728000 / 372120 : ℝ) ^ 2 ≤ 2590 / 120 := by
    rw [div_pow, div_le_div_iff₀ (by norm_num) (by norm_num)]
    norm_num
  calc (1728000 / 372120 : ℝ)
      = Real.sqrt ((1728000 / 372120) ^ 2) := by
        rw [Real.sqrt_sq h1]
    _ ≤ Real.sqrt (2590 / 120) := Real.sqrt_le_sqrt h2

/-- **Graffiti conjecture 154 is FALSE** (non-strict reading): the deviation
of the adjacency eigenvalues of the lollipop `L(K₅₀, P₇₀)` is NOT `≤ n/μ(D)`
either — it is strictly greater, since the integer violation
`358645832496000 > 358318080000000` is strict.  This refutes both possible
readings ('<' and '≤') of the original wording. -/
theorem graffiti_conjecture_154_false_le :
    ¬ (popStdDev (adjMatrix_isHermitian.eigenvalues) ≤ 120 / lollipopMu) := by
  rw [dev_eigenvalues_eq, lollipopMu_eq, not_le]
  rw [show (120 : ℝ) / (372120 / 14400) = 1728000 / 372120 by norm_num]
  rw [show (2 * 1295 / 120 : ℝ) = 2590 / 120 by norm_num]
  have h1 : (0 : ℝ) ≤ 1728000 / 372120 := by norm_num
  have h2 : (1728000 / 372120 : ℝ) ^ 2 < 2590 / 120 := by
    rw [div_pow, div_lt_div_iff₀ (by norm_num) (by norm_num)]
    norm_num
  calc (1728000 / 372120 : ℝ)
      = Real.sqrt ((1728000 / 372120) ^ 2) := by
        rw [Real.sqrt_sq h1]
    _ < Real.sqrt (2590 / 120) := Real.sqrt_lt_sqrt (by positivity) h2

end P07

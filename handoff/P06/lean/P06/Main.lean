/-
# WoW conjecture 698 (Fajtlowicz, "Written on the Wall"), adjacency reading

For every finite simple graph `G`:

  `s⁻(G) := √(∑_{λᵢ < 0} λᵢ²) ≤ R(G) := ∑_{uv ∈ E(G)} (dᵤ dᵥ)^(-1/2)`,

where `λ₁ ≥ … ≥ λₙ` are **all** the eigenvalues of the real adjacency matrix
of `G`, counted with multiplicity, the sum on the left ranges over the
negative ones only (so `s⁻` is the Euclidean norm — the WoW "length" — of the
vector of negative adjacency eigenvalues), and `R(G)` is the Randić index,
summed over the edges of `G`.

Encoding:

* the eigenvalue population is `hA.eigenvalues : V → ℝ` where
  `hA : (G.adjMatrix ℝ).IsHermitian` — mathlib's spectral-theorem enumeration
  of all `|V|` eigenvalues of a real symmetric matrix with (algebraic =
  geometric) multiplicity, so filtering the index set by `λᵢ < 0` and summing
  `λᵢ²` gives exactly the squared Euclidean norm of the negative eigenvalues
  with multiplicity.  `IsHermitian` for a real matrix is exactly symmetry, so
  `hA` always holds (`P06.adjMatrix_isHermitian`); since `IsHermitian` is a
  proposition the value does not depend on the chosen proof.
* `randicIndex G = ∑ e ∈ G.edgeFinset, randicTerm G e` sums the symmetric
  edge weight `(dᵤ dᵥ)^(-1/2) = 1 / √(dᵤ dᵥ)` over the edge set of `G`
  (`Sym2.lift` of the symmetric two-variable function).  Both endpoints of an
  edge have degree ≥ 1, so no division by zero occurs on any edge; isolated
  vertices contribute no terms.  The empty graph (`m = 0`) is included: both
  sides are then `0`.

Proof chain (as in `solutions/P06/PROOF-698.md`):
1. (Rayleigh, `P06.exists_eigenvalue_mul_ge` at `x = (√dᵤ)ᵤ`)
   some eigenvalue `μ` satisfies `2S ≤ μ · 2m`, i.e. `μ ≥ S/m`,
   where `S = ∑_{uv ∈ E} √(dᵤ dᵥ)`;
2. (Cauchy–Schwarz over the edges, `P06.card_edgeFinset_sq_le`)
   `m² ≤ S · R`;
3. hence `μ R ≥ m` and by AM–GM `μ² + R² ≥ 2 μ R ≥ 2m`;
4. `∑ᵢ λᵢ² = trace(A²) = 2m` (`P06.sum_sq_eigenvalues_eq_trace_mul_self`,
   `P06.trace_adjMatrix_mul_self`) and `∑_{λᵢ ≥ 0} λᵢ² ≥ μ²`, so
   `s⁻² = 2m − ∑_{λᵢ ≥ 0} λᵢ² ≤ 2m − μ² ≤ R²`.
-/
import Mathlib
import P06.Spectral
import P06.EdgeSums

open Finset Matrix SimpleGraph

set_option linter.unusedSectionVars false

namespace P06

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The real adjacency matrix of a simple graph is Hermitian (= symmetric). -/
theorem adjMatrix_isHermitian : (G.adjMatrix ℝ).IsHermitian :=
  Matrix.isHermitian_iff_isSymm.mpr (SimpleGraph.isSymm_adjMatrix G)

variable {G}

/-- **WoW conjecture 698** (adjacency reading): the Euclidean norm of the
negative adjacency eigenvalues (with multiplicity) is at most the Randić
index.  See the module docstring for the encoding of each notion. -/
theorem wow_conjecture_698 (hA : (G.adjMatrix ℝ).IsHermitian) :
    Real.sqrt (∑ i ∈ Finset.univ.filter (fun i => hA.eigenvalues i < 0),
        hA.eigenvalues i ^ 2)
      ≤ randicIndex G := by
  classical
  set μ : V → ℝ := hA.eigenvalues with hμdef
  set m : ℝ := (#G.edgeFinset : ℝ) with hmdef
  set R : ℝ := randicIndex G with hRdef
  have hR0 : 0 ≤ R := randicIndex_nonneg G
  -- trace identity: `∑ᵢ μᵢ² = 2m`
  have htrace : ∑ i, μ i ^ 2 = 2 * m := by
    rw [hμdef, sum_sq_eigenvalues_eq_trace_mul_self hA, trace_adjMatrix_mul_self]
  -- the key quadratic bound `s⁻² ≤ R²`
  have key : ∑ i ∈ Finset.univ.filter (fun i => μ i < 0), μ i ^ 2 ≤ R ^ 2 := by
    rcases Finset.eq_empty_or_nonempty G.edgeFinset with hE | hE
    · -- no edges: `2m = 0`, so all eigenvalues are zero and `s⁻² = 0 ≤ R²`
      have hm0 : m = 0 := by rw [hmdef, hE]; simp
      have hle : ∑ i ∈ Finset.univ.filter (fun i => μ i < 0), μ i ^ 2
          ≤ ∑ i, μ i ^ 2 :=
        Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _)
          (fun i _ _ => sq_nonneg _)
      rw [htrace, hm0] at hle
      have : (0 : ℝ) ≤ R ^ 2 := sq_nonneg R
      linarith
    · -- at least one edge
      obtain ⟨e, he⟩ := hE
      obtain ⟨u, v⟩ := e
      have hadj : G.Adj u v := mem_edgeFinset.mp he
      haveI : Nonempty V := ⟨u⟩
      have hm1 : (1 : ℝ) ≤ m := by
        rw [hmdef]
        exact_mod_cast Finset.card_pos.mpr ⟨_, he⟩
      have hmpos : (0 : ℝ) < m := by linarith
      set S : ℝ := sqrtDegSum G with hSdef
      -- step 1: Rayleigh at `x = (√dᵤ)ᵤ` gives an eigenvalue with `S ≤ μᵢ₀ m`
      obtain ⟨i0, hi0⟩ :=
        exists_eigenvalue_mul_ge hA (fun w => Real.sqrt (G.degree w : ℝ))
      rw [dotProduct_sqrtDeg_mulVec, dotProduct_sqrtDeg_self] at hi0
      have hRay : S ≤ μ i0 * m := by
        rw [hSdef, hμdef, hmdef]; nlinarith [hi0]
      -- step 2: Cauchy–Schwarz `m² ≤ S R`
      have hCS : m ^ 2 ≤ S * R := card_edgeFinset_sq_le G
      have hS0 : 0 ≤ S := sqrtDegSum_nonneg G
      -- step 3: `m ≤ μᵢ₀ R`, hence `μᵢ₀² + R² ≥ 2m`
      have hmR : m ≤ μ i0 * R := by
        have h1 : S * R ≤ (μ i0 * m) * R := mul_le_mul_of_nonneg_right hRay hR0
        have h2 : m * m ≤ m * (μ i0 * R) := by nlinarith
        exact le_of_mul_le_mul_left h2 hmpos
      have hμ0pos : 0 < μ i0 := by nlinarith
      -- step 4: split the trace and drop the nonnegative part below `μᵢ₀²`
      have hsplit : ∑ i ∈ Finset.univ.filter (fun i => μ i < 0), μ i ^ 2
            + ∑ i ∈ Finset.univ.filter (fun i => ¬ μ i < 0), μ i ^ 2
          = ∑ i, μ i ^ 2 :=
        Finset.sum_filter_add_sum_filter_not _ _ _
      have hi0mem : i0 ∈ Finset.univ.filter (fun i => ¬ μ i < 0) :=
        Finset.mem_filter.mpr ⟨Finset.mem_univ _, not_lt.mpr hμ0pos.le⟩
      have hple : μ i0 ^ 2 ≤ ∑ i ∈ Finset.univ.filter (fun i => ¬ μ i < 0), μ i ^ 2 :=
        Finset.single_le_sum (fun i _ => sq_nonneg (μ i)) hi0mem
      -- conclude: `s⁻² ≤ 2m − μᵢ₀² ≤ R²` via `μᵢ₀² + R² ≥ 2 μᵢ₀ R ≥ 2m`
      nlinarith [sq_nonneg (μ i0 - R), htrace, hsplit, hple, hmR, hμ0pos]
  calc Real.sqrt (∑ i ∈ Finset.univ.filter (fun i => μ i < 0), μ i ^ 2)
      ≤ Real.sqrt (R ^ 2) := Real.sqrt_le_sqrt key
    _ = R := Real.sqrt_sq hR0

#print axioms wow_conjecture_698

end P06

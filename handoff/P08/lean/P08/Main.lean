/-
# Graffiti conjectures 39 and 40 (Fajtlowicz, "Written on the Wall")

For every finite connected simple graph `G` on vertex set `V` (nonempty):

* conjecture 39: `dev(D) ≤ n⁺(G)`;
* conjecture 40: `dev(D) ≤ n⁻(G)`;

where

* `dev(D)` is the **population standard deviation of all `|V|²` ordered
  entries of the distance matrix `D`, diagonal included**.  It is encoded as
  `popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))`: the index type `V × V`
  has exactly `|V|²` elements (ordered pairs, including the diagonal pairs
  `(v, v)` whose distance is `0`), `popStdDev f = √(∑ (f i - mean)² / card)`
  is the population (not sample) standard deviation, and the entries are the
  graph distances `G.dist`, cast from `ℕ` into `ℝ`.  This matches the original
  conjecture exactly (standard deviation, not variance; over `ℝ`).
* `n⁺(G)` (resp. `n⁻(G)`) is the **number of positive (resp. negative)
  eigenvalues of the real adjacency matrix, counted with multiplicity**.
  It is encoded as `(Finset.univ.filter fun v => 0 < hA.eigenvalues v).card`
  where `hA : (G.adjMatrix ℝ).IsHermitian` and `hA.eigenvalues : V → ℝ` is
  mathlib's spectral-theorem enumeration of the eigenvalues of a real
  symmetric matrix: it lists all `|V|` eigenvalues with (algebraic =
  geometric) multiplicity, so filtering the index set counts eigenvalues
  with multiplicity, as in the original conjecture.  `IsHermitian` for a
  real matrix is exactly symmetry, so `hA` always holds for `G.adjMatrix ℝ`
  (see `adjMatrix_isHermitian` below); since `IsHermitian` is a proposition,
  the count does not depend on the chosen proof.

Proof chain (as in `solutions/P08/PROOF.md`):
1. every distance lies in `[0, diam]`, so `dev(D) ≤ diam / 2`
   (Popoviciu; `P08.popStdDev_le_of_mem_Icc`);
2. a geodesic realizing the diameter is an induced path on `diam + 1`
   vertices (`P08.exists_geodesic_seq`);
3./4. the vectors `e_{x(2t)} ± e_{x(2t+1)}` (`t < ⌊(diam+1)/2⌋`) span a
   subspace on which the adjacency quadratic form is positive (resp.
   negative) definite, so `⌊(diam+1)/2⌋ ≤ n⁺` and `⌊(diam+1)/2⌋ ≤ n⁻`
   (this packages "path inertia + Cauchy interlacing" directly;
   `P08.le_card_pos_eigenvalues` / `P08.le_card_neg_eigenvalues`);
5. `dev(D) ≤ diam/2 ≤ ⌊(diam+1)/2⌋ ≤ min(n⁺, n⁻)`.
-/
import Mathlib
import P08.Popoviciu
import P08.Spectral
import P08.Geodesic
import P08.PathSubspace

open Finset Matrix SimpleGraph

namespace P08

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The real adjacency matrix of a simple graph is Hermitian (= symmetric). -/
theorem adjMatrix_isHermitian : (G.adjMatrix ℝ).IsHermitian :=
  Matrix.isHermitian_iff_isSymm.mpr (SimpleGraph.isSymm_adjMatrix G)

variable {G}

/-- **Step 1**: the population standard deviation of the `|V|²` ordered
distance-matrix entries is at most `diam / 2`. -/
theorem popStdDev_dist_le_diam [Nonempty V] (hconn : G.Connected) :
    popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ)) ≤ (G.diam : ℝ) / 2 := by
  have hbound : ∀ p : V × V, (G.dist p.1 p.2 : ℝ) ∈ Set.Icc (0 : ℝ) (G.diam : ℝ) := by
    intro p
    constructor
    · exact_mod_cast Nat.zero_le _
    · exact_mod_cast G.dist_le_diam
        (G.connected_iff_ediam_ne_top.mp hconn)
  have h := popStdDev_le_of_mem_Icc hbound
  simpa using h

section EigenvalueCounts

variable (hA : (G.adjMatrix ℝ).IsHermitian)

/-- **Steps 2–4** (positive side): `⌊(diam+1)/2⌋ ≤ n⁺(G)`.  The proof takes
a diameter-realizing geodesic (an induced path, step 2) and exhibits the
`⌊(diam+1)/2⌋`-dimensional positive-definite subspace spanned by
`e_{x(2t)} + e_{x(2t+1)}`, which lower-bounds the positive eigenvalue count
(steps 3–4, packaged inertia/interlacing argument). -/
theorem floor_diam_le_card_pos [Nonempty V] (hconn : G.Connected) :
    (G.diam + 1) / 2 ≤ (Finset.univ.filter fun v => 0 < hA.eigenvalues v).card := by
  classical
  obtain ⟨u, v, huv⟩ := G.exists_dist_eq_diam
  obtain ⟨x, hdist, hinj, hadj⟩ := exists_geodesic_seq hconn u v
  set d := G.dist u v with hd
  rw [← huv]
  set m := (d + 1) / 2 with hmdef
  rcases Nat.eq_zero_or_pos m with hm0 | hmpos
  · omega
  have hm : 2 * m ≤ d + 1 := by omega
  set e := WithLp.linearEquiv 2 ℝ (V → ℝ) with he
  set w : Fin m → EuclideanSpace ℝ V := fun t => e.symm (pathVec x 1 (t : ℕ)) with hw
  have hli : LinearIndependent ℝ w := by
    have h0 : LinearIndependent ℝ (fun t : Fin m => pathVec x 1 (t : ℕ)) :=
      pathVec_linearIndependent hinj hm 1
    exact h0.map' e.symm.toLinearMap e.symm.ker
  refine le_card_pos_eigenvalues hA w hli ?_
  intro y hy hyne
  obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun ℝ).mp hy
  have hofLp : (WithLp.ofLp y : V → ℝ) = ∑ t : Fin m, c t • pathVec x 1 (t : ℕ) := by
    have := congrArg e hc
    rw [map_sum] at this
    simp only [map_smul, he] at this
    simpa [hw, he] using this.symm
  -- convert to a sum over `Finset.range m`
  set eN : ℕ → ℝ := fun i => if h : i < m then c ⟨i, h⟩ else 0 with heN
  have hsum : (WithLp.ofLp y : V → ℝ) = ∑ i ∈ Finset.range m, eN i • pathVec x 1 i := by
    rw [hofLp, ← Fin.sum_univ_eq_sum_range (fun i => eN i • pathVec x 1 i) m]
    refine Finset.sum_congr rfl fun t _ => ?_
    have ht : eN (t : ℕ) = c t := by
      simp only [heN]
      exact dif_pos t.isLt
    rw [ht]
  have hcne : ∃ t : Fin m, c t ≠ 0 := by
    by_contra hall
    push_neg at hall
    apply hyne
    rw [← hc]
    simp [hall]
  obtain ⟨t0, ht0⟩ := hcne
  have heNne : ∃ i, i < m ∧ eN i ≠ 0 :=
    ⟨(t0 : ℕ), t0.isLt, by rw [heN]; simpa [dif_pos t0.isLt] using ht0⟩
  have hq := quadForm_pathVec_combination hinj hadj (by norm_num : (1 : ℝ) * 1 = 1) hm eN
  rw [hsum, hq, one_mul]
  exact tridiag_pos hmpos eN heNne

/-- **Steps 2–4** (negative side): `⌊(diam+1)/2⌋ ≤ n⁻(G)`, via the
negative-definite subspace spanned by `e_{x(2t)} - e_{x(2t+1)}`. -/
theorem floor_diam_le_card_neg [Nonempty V] (hconn : G.Connected) :
    (G.diam + 1) / 2 ≤ (Finset.univ.filter fun v => hA.eigenvalues v < 0).card := by
  classical
  obtain ⟨u, v, huv⟩ := G.exists_dist_eq_diam
  obtain ⟨x, hdist, hinj, hadj⟩ := exists_geodesic_seq hconn u v
  set d := G.dist u v with hd
  rw [← huv]
  set m := (d + 1) / 2 with hmdef
  rcases Nat.eq_zero_or_pos m with hm0 | hmpos
  · omega
  have hm : 2 * m ≤ d + 1 := by omega
  set e := WithLp.linearEquiv 2 ℝ (V → ℝ) with he
  set w : Fin m → EuclideanSpace ℝ V := fun t => e.symm (pathVec x (-1) (t : ℕ)) with hw
  have hli : LinearIndependent ℝ w := by
    have h0 : LinearIndependent ℝ (fun t : Fin m => pathVec x (-1) (t : ℕ)) :=
      pathVec_linearIndependent hinj hm (-1)
    exact h0.map' e.symm.toLinearMap e.symm.ker
  refine le_card_neg_eigenvalues hA w hli ?_
  intro y hy hyne
  obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun ℝ).mp hy
  have hofLp : (WithLp.ofLp y : V → ℝ) = ∑ t : Fin m, c t • pathVec x (-1) (t : ℕ) := by
    have := congrArg e hc
    rw [map_sum] at this
    simp only [map_smul, he] at this
    simpa [hw, he] using this.symm
  set eN : ℕ → ℝ := fun i => if h : i < m then c ⟨i, h⟩ else 0 with heN
  have hsum : (WithLp.ofLp y : V → ℝ)
      = ∑ i ∈ Finset.range m, eN i • pathVec x (-1) i := by
    rw [hofLp, ← Fin.sum_univ_eq_sum_range (fun i => eN i • pathVec x (-1) i) m]
    refine Finset.sum_congr rfl fun t _ => ?_
    have ht : eN (t : ℕ) = c t := by
      simp only [heN]
      exact dif_pos t.isLt
    rw [ht]
  have hcne : ∃ t : Fin m, c t ≠ 0 := by
    by_contra hall
    push_neg at hall
    apply hyne
    rw [← hc]
    simp [hall]
  obtain ⟨t0, ht0⟩ := hcne
  have heNne : ∃ i, i < m ∧ eN i ≠ 0 :=
    ⟨(t0 : ℕ), t0.isLt, by rw [heN]; simpa [dif_pos t0.isLt] using ht0⟩
  have hq := quadForm_pathVec_combination hinj hadj
    (by norm_num : (-1 : ℝ) * (-1) = 1) hm eN
  rw [hsum, hq]
  have hpos := tridiag_pos hmpos eN heNne
  linarith

end EigenvalueCounts

/-- Numeric step 5 glue: `diam / 2 ≤ ⌊(diam + 1) / 2⌋` over `ℝ`. -/
lemma half_le_floor_succ_half (D : ℕ) : (D : ℝ) / 2 ≤ (((D + 1) / 2 : ℕ) : ℝ) := by
  have h : D ≤ 2 * ((D + 1) / 2) := by omega
  have h' : (D : ℝ) ≤ 2 * (((D + 1) / 2 : ℕ) : ℝ) := by exact_mod_cast h
  linarith

/-- **Graffiti conjecture 39**: for a finite connected simple graph, the
population standard deviation of the `|V|²` ordered entries of the distance
matrix (diagonal included) is at most the number of positive eigenvalues of
the real adjacency matrix (with multiplicity).  See the module docstring for
the encoding of each notion. -/
theorem graffiti_conjecture_39 [Nonempty V] (hconn : G.Connected)
    (hA : (G.adjMatrix ℝ).IsHermitian) :
    popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))
      ≤ ((Finset.univ.filter fun v => 0 < hA.eigenvalues v).card : ℝ) := by
  calc popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))
      ≤ (G.diam : ℝ) / 2 := popStdDev_dist_le_diam hconn
    _ ≤ (((G.diam + 1) / 2 : ℕ) : ℝ) := half_le_floor_succ_half _
    _ ≤ ((Finset.univ.filter fun v => 0 < hA.eigenvalues v).card : ℝ) := by
        exact_mod_cast floor_diam_le_card_pos hA hconn

/-- **Graffiti conjecture 40**: the same deviation is also at most the number
of negative adjacency eigenvalues (with multiplicity). -/
theorem graffiti_conjecture_40 [Nonempty V] (hconn : G.Connected)
    (hA : (G.adjMatrix ℝ).IsHermitian) :
    popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))
      ≤ ((Finset.univ.filter fun v => hA.eigenvalues v < 0).card : ℝ) := by
  calc popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))
      ≤ (G.diam : ℝ) / 2 := popStdDev_dist_le_diam hconn
    _ ≤ (((G.diam + 1) / 2 : ℕ) : ℝ) := half_le_floor_succ_half _
    _ ≤ ((Finset.univ.filter fun v => hA.eigenvalues v < 0).card : ℝ) := by
        exact_mod_cast floor_diam_le_card_neg hA hconn

#print axioms graffiti_conjecture_39
#print axioms graffiti_conjecture_40

end P08

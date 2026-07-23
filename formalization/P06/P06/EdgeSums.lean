/-
Edge-sum toolkit: converting sums over ordered adjacent pairs (darts) to sums
over the edge set of a simple graph, and the combinatorial identities

* `dotProduct_sqrtDeg_mulVec`: `x ⬝ᵥ A *ᵥ x = 2 S` for `x = (√dᵤ)ᵤ`,
  with `S = ∑_{uv ∈ E} √(dᵤ dᵥ)`;
* `dotProduct_sqrtDeg_self`: `x ⬝ᵥ x = 2 m`;
* `trace_adjMatrix_mul_self`: `trace (A * A) = 2 m`;
* `card_edgeFinset_sq_le`: Cauchy–Schwarz `m² ≤ S · R(G)`.
-/
import Mathlib

open Finset Matrix SimpleGraph

set_option linter.unusedSectionVars false

namespace P06

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

/-- The Randić weight of an unordered pair `{u, v}`: `(dᵤ dᵥ)^(-1/2)`. -/
noncomputable def randicTerm : Sym2 V → ℝ :=
  Sym2.lift ⟨fun u v => 1 / Real.sqrt ((G.degree u : ℝ) * (G.degree v : ℝ)),
    fun u v => by dsimp only; rw [mul_comm]⟩

/-- The **Randić index** `R(G) = ∑_{uv ∈ E(G)} (dᵤ dᵥ)^(-1/2)`, summed over the
edges of the graph. -/
noncomputable def randicIndex : ℝ := ∑ e ∈ G.edgeFinset, randicTerm G e

/-- `√(dᵤ dᵥ)` for an unordered pair `{u, v}`. -/
noncomputable def sqrtDegTerm : Sym2 V → ℝ :=
  Sym2.lift ⟨fun u v => Real.sqrt ((G.degree u : ℝ) * (G.degree v : ℝ)),
    fun u v => by dsimp only; rw [mul_comm]⟩

/-- `S(G) = ∑_{uv ∈ E(G)} √(dᵤ dᵥ)`. -/
noncomputable def sqrtDegSum : ℝ := ∑ e ∈ G.edgeFinset, sqrtDegTerm G e

@[simp] lemma randicTerm_mk (u v : V) :
    randicTerm G s(u, v) = 1 / Real.sqrt ((G.degree u : ℝ) * (G.degree v : ℝ)) := rfl

@[simp] lemma sqrtDegTerm_mk (u v : V) :
    sqrtDegTerm G s(u, v) = Real.sqrt ((G.degree u : ℝ) * (G.degree v : ℝ)) := rfl

lemma randicTerm_nonneg (e : Sym2 V) : 0 ≤ randicTerm G e := by
  induction e with
  | _ u v => simp only [randicTerm_mk]; positivity

lemma sqrtDegTerm_nonneg (e : Sym2 V) : 0 ≤ sqrtDegTerm G e := by
  induction e with
  | _ u v => simp only [sqrtDegTerm_mk]; positivity

lemma randicIndex_nonneg : 0 ≤ randicIndex G :=
  Finset.sum_nonneg fun e _ => randicTerm_nonneg G e

lemma sqrtDegSum_nonneg : 0 ≤ sqrtDegSum G :=
  Finset.sum_nonneg fun e _ => sqrtDegTerm_nonneg G e

/-- A sum over the darts of `G` of an edge function counts every edge twice. -/
lemma sum_dart_edge (f : Sym2 V → ℝ) :
    ∑ d : G.Dart, f d.edge = 2 * ∑ e ∈ G.edgeFinset, f e := by
  rw [← Finset.sum_fiberwise_of_maps_to
    (g := SimpleGraph.Dart.edge) (t := G.edgeFinset)
    (fun d _ => mem_edgeFinset.mpr d.edge_mem) (fun d => f d.edge),
    Finset.mul_sum]
  refine Finset.sum_congr rfl fun e he => ?_
  have hcard : #{d : G.Dart | d.edge = e} = 2 :=
    G.dart_edge_fiber_card e (mem_edgeFinset.mp he)
  calc ∑ d ∈ ({d : G.Dart | d.edge = e} : Finset _), f d.edge
      = ∑ _d ∈ ({d : G.Dart | d.edge = e} : Finset _), f e :=
        Finset.sum_congr rfl fun d hd => by rw [(Finset.mem_filter.mp hd).2]
    _ = 2 * f e := by rw [Finset.sum_const, hcard]; simp [two_mul]

/-- A sum over the darts of `G` equals the double sum over neighborhoods. -/
lemma sum_dart_eq_sum_neighbors (F : V → V → ℝ) :
    ∑ d : G.Dart, F d.fst d.snd = ∑ v, ∑ u ∈ G.neighborFinset v, F v u := by
  rw [← Finset.sum_fiberwise_of_maps_to
    (g := fun d : G.Dart => d.fst) (t := Finset.univ)
    (fun d _ => Finset.mem_univ _) (fun d => F d.fst d.snd)]
  refine Finset.sum_congr rfl fun v _ => ?_
  rw [SimpleGraph.dart_fst_fiber,
    Finset.sum_image (fun a _ b _ h => G.dartOfNeighborSet_injective v h),
    neighborFinset_def, ← Finset.sum_set_coe]
  rfl

/-- The quadratic form of the adjacency matrix at `x = (√dᵤ)ᵤ` is `2 S(G)`. -/
lemma dotProduct_sqrtDeg_mulVec :
    (fun v => Real.sqrt (G.degree v : ℝ)) ⬝ᵥ
        (G.adjMatrix ℝ *ᵥ fun v => Real.sqrt (G.degree v : ℝ))
      = 2 * sqrtDegSum G := by
  have h1 : (fun v => Real.sqrt (G.degree v : ℝ)) ⬝ᵥ
        (G.adjMatrix ℝ *ᵥ fun v => Real.sqrt (G.degree v : ℝ))
      = ∑ v, ∑ u ∈ G.neighborFinset v, sqrtDegTerm G s(v, u) := by
    simp only [dotProduct, adjMatrix_mulVec_apply, Finset.mul_sum]
    refine Finset.sum_congr rfl fun v _ => Finset.sum_congr rfl fun u _ => ?_
    rw [sqrtDegTerm_mk, Real.sqrt_mul (by positivity)]
  have h2 : ∑ d : G.Dart, sqrtDegTerm G d.edge
      = ∑ v, ∑ u ∈ G.neighborFinset v, sqrtDegTerm G s(v, u) :=
    sum_dart_eq_sum_neighbors G (fun v u => sqrtDegTerm G s(v, u))
  rw [h1, ← h2, sum_dart_edge]
  rfl

/-- `x ⬝ᵥ x = ∑ᵥ dᵥ = 2 m` for `x = (√dᵤ)ᵤ`. -/
lemma dotProduct_sqrtDeg_self :
    (fun v => Real.sqrt (G.degree v : ℝ)) ⬝ᵥ (fun v => Real.sqrt (G.degree v : ℝ))
      = 2 * #G.edgeFinset := by
  have h : ∀ v : V, Real.sqrt (G.degree v : ℝ) * Real.sqrt (G.degree v : ℝ)
      = (G.degree v : ℝ) := fun v => Real.mul_self_sqrt (by positivity)
  rw [dotProduct]
  simp only [h]
  rw [← Nat.cast_sum, G.sum_degrees_eq_twice_card_edges]
  push_cast
  ring

/-- `trace (A * A) = ∑ᵥ dᵥ = 2 m` for the real adjacency matrix. -/
lemma trace_adjMatrix_mul_self :
    (G.adjMatrix ℝ * G.adjMatrix ℝ).trace = 2 * #G.edgeFinset := by
  have h : ∀ i : V, (G.adjMatrix ℝ * G.adjMatrix ℝ) i i = (G.degree i : ℝ) :=
    fun i => G.adjMatrix_mul_self_apply_self i
  rw [Matrix.trace]
  simp only [Matrix.diag_apply, h]
  rw [← Nat.cast_sum, G.sum_degrees_eq_twice_card_edges]
  push_cast
  ring

/-- On an edge both endpoint degrees are positive, so the weights multiply to 1. -/
lemma sqrtDegTerm_mul_randicTerm {e : Sym2 V} (he : e ∈ G.edgeFinset) :
    sqrtDegTerm G e * randicTerm G e = 1 := by
  induction e with
  | _ u v =>
    have hadj : G.Adj u v := mem_edgeFinset.mp he
    have hdu : 0 < G.degree u := hadj.degree_pos_left
    have hdv : 0 < G.degree v := hadj.degree_pos_right
    have hpos : 0 < (G.degree u : ℝ) * (G.degree v : ℝ) := by positivity
    have hsqrt : Real.sqrt ((G.degree u : ℝ) * (G.degree v : ℝ)) ≠ 0 :=
      ne_of_gt (Real.sqrt_pos.mpr hpos)
    rw [sqrtDegTerm_mk, randicTerm_mk, mul_one_div, div_self hsqrt]

/-- **Cauchy–Schwarz over the edges**: `m² ≤ S(G) · R(G)`. -/
lemma card_edgeFinset_sq_le :
    (#G.edgeFinset : ℝ) ^ 2 ≤ sqrtDegSum G * randicIndex G := by
  have h := Finset.sum_sq_le_sum_mul_sum_of_sq_le_mul G.edgeFinset
    (f := sqrtDegTerm G) (g := randicTerm G) (r := fun _ => (1 : ℝ))
    (fun e _ => sqrtDegTerm_nonneg G e) (fun e _ => randicTerm_nonneg G e)
    (fun e he => by rw [one_pow, sqrtDegTerm_mul_randicTerm G he])
  simpa [sqrtDegSum, randicIndex] using h

end P06

import Mathlib

/-!
# Vertex multiplication and a Farkas-style infeasibility lemma

`SimpleGraph.mult G x` replaces each vertex `v` of `G` by an independent set of
`x v` twin copies; copies of `v` and `u` are adjacent iff `v` and `u` are
adjacent in `G`.  This is exactly the "vertex multiplication" operation from
Brandt's regular supergraph problem (West, regsup.html): when `x v ≥ 1` for
every `v`, the multiplication graph contains `G` as an (induced) subgraph
(`multEmbedding`), i.e. it is a supergraph of `G` obtained by vertex
multiplications.

The key degree computation is `mult_degree`: every copy of `v` has degree
`∑ u ∈ N(v), x u`, so the multiplication graph is `d`-regular iff
`∑ u ∈ N(v), x u = d` for all `v` (`mult_isRegularOfDegree_iff`).

`farkas` is the certificate-checking lemma: an integer vector `y` with
`∑ y = 0`, `(A y)_u ≥ 0` for all `u`, and `∑_u (A y)_u > 0` witnesses that the
linear system `{x ≥ 1, A x = d·1}` has no solution for ANY `d` — the proof is
the standard symmetry argument `0 = d·∑y = ∑_v y_v (Ax)_v = ∑_u (Ay)_u x_u ≥
∑_u (Ay)_u > 0`.
-/

open Finset

namespace SimpleGraph

variable {V : Type*} (G : SimpleGraph V)

/-- Vertex multiplication: replace each vertex `v` of `G` by an independent set
of `x v` twin copies, joining copies of distinct vertices iff the originals are
adjacent. -/
def mult (x : V → ℕ) : SimpleGraph (Σ v : V, Fin (x v)) where
  Adj a b := G.Adj a.1 b.1
  symm := ⟨fun _ _ h => G.adj_symm h⟩
  loopless := ⟨fun _ h => G.irrefl h⟩

@[simp]
lemma mult_adj (x : V → ℕ) (a b : Σ v : V, Fin (x v)) :
    (G.mult x).Adj a b ↔ G.Adj a.1 b.1 := Iff.rfl

instance (x : V → ℕ) [DecidableRel G.Adj] : DecidableRel (G.mult x).Adj :=
  fun a b => ‹DecidableRel G.Adj› a.1 b.1

/-- When every multiplicity is positive, the multiplication graph is a
supergraph of `G`: mapping `v` to its first copy is a graph embedding (it is
even induced: adjacency is preserved and reflected). -/
def multEmbedding (x : V → ℕ) (hx : ∀ v, 1 ≤ x v) : G ↪g G.mult x where
  toFun v := ⟨v, ⟨0, hx v⟩⟩
  inj' _ _ h := congrArg Sigma.fst h
  map_rel_iff' := Iff.rfl

section Degree

variable [Fintype V] [DecidableRel G.Adj]

/-- The neighbours of a copy of `v` are all copies of all neighbours of `v`. -/
lemma mult_neighborFinset (x : V → ℕ) (a : Σ v : V, Fin (x v)) :
    (G.mult x).neighborFinset a
      = (G.neighborFinset a.1).sigma (fun u => (Finset.univ : Finset (Fin (x u)))) := by
  ext b
  simp [Finset.mem_sigma]

/-- Every copy of `v` in the multiplication graph has degree
`∑ u ∈ N(v), x u`. -/
lemma mult_degree (x : V → ℕ) (a : Σ v : V, Fin (x v)) :
    (G.mult x).degree a = ∑ u ∈ G.neighborFinset a.1, x u := by
  rw [← card_neighborFinset_eq_degree, mult_neighborFinset, Finset.card_sigma]
  simp

/-- With all multiplicities positive, the multiplication graph is `d`-regular
iff the linear system `∑ u ∈ N(v), x u = d` holds at every vertex of `G`. -/
theorem mult_isRegularOfDegree_iff (x : V → ℕ) (hx : ∀ v, 1 ≤ x v) (d : ℕ) :
    (G.mult x).IsRegularOfDegree d ↔ ∀ v, ∑ u ∈ G.neighborFinset v, x u = d := by
  constructor
  · intro h v
    have := h ⟨v, ⟨0, hx v⟩⟩
    rwa [mult_degree] at this
  · intro h a
    rw [mult_degree]
    exact h a.1

end Degree

section Farkas

variable [Fintype V] [DecidableRel G.Adj]

/-- Double counting over the (symmetric) adjacency relation:
`∑_v ∑_{u ∈ N(v)} f v u = ∑_u ∑_{v ∈ N(u)} f v u`. -/
lemma sum_neighborFinset_comm {M : Type*} [AddCommMonoid M] (f : V → V → M) :
    ∑ v, ∑ u ∈ G.neighborFinset v, f v u = ∑ u, ∑ v ∈ G.neighborFinset u, f v u :=
  Finset.sum_comm' (by simp [adj_comm])

/-- Farkas-certificate refutation: if `y : V → ℤ` satisfies `∑ y = 0`,
`(A y)_u ≥ 0` for all `u`, and `∑_u (A y)_u > 0`, then there is no `x ≥ 1`
with `A x = d·1` — for ANY `d` simultaneously. -/
theorem farkas_no_solution (y : V → ℤ) (hsum : ∑ v, y v = 0)
    (hAy : ∀ u, 0 ≤ ∑ v ∈ G.neighborFinset u, y v)
    (hpos : 0 < ∑ u, ∑ v ∈ G.neighborFinset u, y v)
    (x : V → ℕ) (hx : ∀ v, 1 ≤ x v) (d : ℕ)
    (h : ∀ v, ∑ u ∈ G.neighborFinset v, x u = d) : False := by
  -- `0 = d·∑y = ∑_v y_v (Ax)_v = ∑_u (Ay)_u x_u ≥ ∑_u (Ay)_u > 0`
  have key : (0 : ℤ) = ∑ u, (∑ v ∈ G.neighborFinset u, y v) * (x u : ℤ) := by
    calc (0 : ℤ) = ∑ v, y v * d := by rw [← Finset.sum_mul, hsum, zero_mul]
      _ = ∑ v, y v * ∑ u ∈ G.neighborFinset v, (x u : ℤ) := by
          refine Finset.sum_congr rfl fun v _ => ?_
          rw [← Nat.cast_sum, h v]
      _ = ∑ v, ∑ u ∈ G.neighborFinset v, y v * (x u : ℤ) := by
          simp [Finset.mul_sum]
      _ = ∑ u, ∑ v ∈ G.neighborFinset u, y v * (x u : ℤ) :=
          G.sum_neighborFinset_comm _
      _ = ∑ u, (∑ v ∈ G.neighborFinset u, y v) * (x u : ℤ) := by
          simp [Finset.sum_mul]
  have lower : ∑ u, ∑ v ∈ G.neighborFinset u, y v
      ≤ ∑ u, (∑ v ∈ G.neighborFinset u, y v) * (x u : ℤ) := by
    refine Finset.sum_le_sum fun u _ => ?_
    have h1 : (1 : ℤ) ≤ (x u : ℤ) := by exact_mod_cast hx u
    calc ∑ v ∈ G.neighborFinset u, y v
        = (∑ v ∈ G.neighborFinset u, y v) * 1 := (mul_one _).symm
      _ ≤ (∑ v ∈ G.neighborFinset u, y v) * (x u : ℤ) :=
          mul_le_mul_of_nonneg_left h1 (hAy u)
  omega

end Farkas

end SimpleGraph

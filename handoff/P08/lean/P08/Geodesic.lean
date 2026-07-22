/-
Geodesics are induced paths: along a shortest `u,v`-walk, the `i`-th vertex is
at distance exactly `i` from `u`, the vertices are pairwise distinct, and two
of them are adjacent in `G` iff they are consecutive.
-/
import Mathlib

open SimpleGraph

namespace P08

variable {V : Type*} {G : SimpleGraph V}

lemma dist_getVert_le {u v : V} (p : G.Walk u v) (i : ℕ) :
    G.dist u (p.getVert i) ≤ i := by
  induction i with
  | zero => simp [p.getVert_zero, SimpleGraph.dist_self]
  | succ i ih =>
    by_cases hi : i < p.length
    · have hadj : G.Adj (p.getVert i) (p.getVert (i + 1)) := p.adj_getVert_succ hi
      have htri : G.dist u (p.getVert (i + 1))
          ≤ G.dist u (p.getVert i) + G.dist (p.getVert i) (p.getVert (i + 1)) :=
        hadj.reachable.dist_triangle_right u
      have h1 : G.dist (p.getVert i) (p.getVert (i + 1)) = 1 :=
        SimpleGraph.dist_eq_one_iff_adj.mpr hadj
      omega
    · have hle : p.length ≤ i := by omega
      rw [p.getVert_of_length_le (by omega : p.length ≤ i + 1),
        ← p.getVert_of_length_le hle]
      omega

lemma dist_getVert_right_le {u v : V} (p : G.Walk u v) {i : ℕ} (hi : i ≤ p.length) :
    G.dist (p.getVert i) v ≤ p.length - i := by
  have h := dist_getVert_le p.reverse (p.length - i)
  rw [p.getVert_reverse] at h
  have hii : p.length - (p.length - i) = i := by omega
  rw [hii] at h
  rwa [SimpleGraph.dist_comm]

/-- Along a shortest walk, the `i`-th vertex is at distance exactly `i`
from the start. -/
lemma dist_getVert_eq (hconn : G.Connected) {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i : ℕ} (hi : i ≤ p.length) :
    G.dist u (p.getVert i) = i := by
  refine le_antisymm (dist_getVert_le p i) ?_
  have htri : G.dist u v ≤ G.dist u (p.getVert i) + G.dist (p.getVert i) v :=
    hconn.dist_triangle
  have h2 : G.dist (p.getVert i) v ≤ p.length - i := dist_getVert_right_le p hi
  omega

/-- The vertex sequence of a geodesic: exact distances, and adjacency exactly
between consecutive vertices (i.e. the geodesic is an induced path). -/
theorem exists_geodesic_seq (hconn : G.Connected) (u v : V) :
    ∃ x : ℕ → V,
      (∀ i, i ≤ G.dist u v → G.dist u (x i) = i) ∧
      (∀ i j, i ≤ G.dist u v → j ≤ G.dist u v → x i = x j → i = j) ∧
      (∀ i j, i ≤ G.dist u v → j ≤ G.dist u v →
        (G.Adj (x i) (x j) ↔ (i = j + 1 ∨ j = i + 1))) := by
  obtain ⟨p, hp⟩ := hconn.exists_walk_length_eq_dist u v
  set d := G.dist u v with hd
  refine ⟨p.getVert, fun i hi => dist_getVert_eq hconn p hp (by omega), ?_, ?_⟩
  · intro i j hi hj hxy
    have h1 : G.dist u (p.getVert i) = i := dist_getVert_eq hconn p hp (by omega)
    have h2 : G.dist u (p.getVert j) = j := dist_getVert_eq hconn p hp (by omega)
    rw [hxy] at h1
    omega
  · intro i j hi hj
    constructor
    · intro hadj
      have h1 : G.dist u (p.getVert i) = i := dist_getVert_eq hconn p hp (by omega)
      have h2 : G.dist u (p.getVert j) = j := dist_getVert_eq hconn p hp (by omega)
      have hdist : G.dist (p.getVert i) (p.getVert j) = 1 :=
        SimpleGraph.dist_eq_one_iff_adj.mpr hadj
      have htri1 : G.dist u (p.getVert j)
          ≤ G.dist u (p.getVert i) + G.dist (p.getVert i) (p.getVert j) :=
        hadj.reachable.dist_triangle_right u
      have htri2 : G.dist u (p.getVert i)
          ≤ G.dist u (p.getVert j) + G.dist (p.getVert j) (p.getVert i) :=
        hadj.symm.reachable.dist_triangle_right u
      have hdist' : G.dist (p.getVert j) (p.getVert i) = 1 :=
        SimpleGraph.dist_eq_one_iff_adj.mpr hadj.symm
      have hne : i ≠ j := by
        rintro rfl
        exact G.irrefl hadj
      omega
    · rintro (rfl | rfl)
      · exact (p.adj_getVert_succ (by omega)).symm
      · exact p.adj_getVert_succ (by omega)

end P08

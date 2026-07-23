/-
P13: the reduction — any (9,6,1)-PMD yields a satisfying assignment of the CNF.

Together with UNSAT of `pmdCnf` (checked via the verified LRAT checker in
`Cert.lean`), this refutes the existence of a (9,6,1)-PMD.  Because `pmdCnf`
carries *no* symmetry breaking, no WLOG argument is needed: the assignment is
read off the design directly.
-/
import P13.Canon

namespace P13

set_option maxRecDepth 10000

open Std.Sat

/-- The assignment induced by a design `B`: `x bl p s` is true iff block `bl`
has symbol `s` at position `p`; the Tseitin variable `e t u j bl p` is true iff
block `bl` realizes the ordered pair `(u, wOf u j)` at distance `t + 1` from
position `p`. -/
def assignOf (B : Fin 12 → Fin 6 → Fin 9) : V → Bool
  | .x bl p s => decide (B bl p = s)
  | .e t u j bl p => decide (B bl p = u) && decide (B bl (p + dOf t) = wOf u j)

/-- Two-literal negative clauses are satisfied when not both variables hold. -/
private theorem clause2_eval {a : V → Bool} {v1 v2 : V}
    (h : ¬(a v1 = true ∧ a v2 = true)) :
    CNF.Clause.eval a [(v1, false), (v2, false)] = true := by
  cases h1 : a v1 <;> cases h2 : a v2 <;> simp_all [CNF.Clause.eval]

private theorem ltPairs_ne {α : Type _} {l : List α} (h : l.Nodup)
    {q : α × α} (hm : q ∈ ltPairs l) : q.1 ≠ q.2 := by
  induction l with
  | nil => simp [ltPairs] at hm
  | cons a l ih =>
      simp only [ltPairs, List.mem_append, List.mem_map] at hm
      rcases hm with ⟨b, hb, rfl⟩ | hm
      · intro hEq
        simp only at hEq
        subst hEq
        exact (List.nodup_cons.mp h).1 hb
      · exact ih (List.nodup_cons.mp h).2 hm

private theorem mem_slots (q : Fin 12 × Fin 6) : q ∈ slots :=
  List.mem_flatMap.mpr ⟨q.1, List.mem_finRange _,
    List.mem_map.mpr ⟨q.2, List.mem_finRange _, rfl⟩⟩

private theorem slots_nodup : slots.Nodup := by decide

private theorem dOf_val_ne (t : Fin 5) : (dOf t).val ≠ 0 := by
  simp [dOf]

private theorem wOf_ne (u : Fin 9) (j : Fin 8) : u ≠ wOf u j := by
  unfold wOf
  split <;> (intro h; have := congrArg Fin.val h; simp at this; omega)

/-- The key semantic fact behind the Tseitin coverage constraints: `B` covers
`(u, wOf u j)` at distance `t+1` from slot `q` iff the corresponding product
variable is true. -/
private theorem eAssign_iff (B : Fin 12 → Fin 6 → Fin 9) (t : Fin 5) (u : Fin 9)
    (j : Fin 8) (q : Fin 12 × Fin 6) :
    assignOf B (V.e t u j q.1 q.2) = true ↔
      (B q.1 q.2 = u ∧ B q.1 (q.2 + dOf t) = wOf u j) := by
  simp [assignOf]

theorem eval_pmdCnfV (B : Fin 12 → Fin 6 → Fin 9) (h : IsPMD1 B) :
    CNF.eval (assignOf B) pmdCnfV = true := by
  obtain ⟨hinj, hcov⟩ := h
  have hall : ∀ c ∈ cnfList, CNF.Clause.eval (assignOf B) c = true := by
    intro c hc
    simp only [cnfList, List.mem_append, List.mem_flatMap] at hc
    rcases hc with ⟨bl, _, hc⟩ | ⟨t, _, u, _, j, _, hc⟩
    · -- block clauses
      simp only [blockClauses, List.mem_append, List.mem_flatMap] at hc
      rcases hc with ⟨p, _, hc⟩ | ⟨s, _, hc⟩
      · -- cell clauses
        simp only [cellClauses, List.mem_cons, List.mem_map] at hc
        rcases hc with rfl | ⟨q, hq, rfl⟩
        · -- at least one symbol in the cell
          refine List.any_eq_true.mpr ⟨(V.x bl p (B bl p), true), ?_, by simp [assignOf]⟩
          exact List.mem_map.mpr ⟨B bl p, List.mem_finRange _, rfl⟩
        · -- at most one symbol in the cell
          have hne := ltPairs_ne (List.nodup_finRange 9) hq
          refine clause2_eval fun ⟨h1, h2⟩ => hne ?_
          simp only [assignOf, decide_eq_true_eq] at h1 h2
          rw [← h1, ← h2]
      · -- each symbol at most once per block
        obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hc
        have hne := ltPairs_ne (List.nodup_finRange 6) hq
        refine clause2_eval fun ⟨h1, h2⟩ => hne ?_
        simp only [assignOf, decide_eq_true_eq] at h1 h2
        exact hinj bl (h1.trans h2.symm)
    · -- coverage clauses for distance t+1, pair (u, wOf u j)
      have hune := wOf_ne u j
      simp only [coverClauses, List.mem_append, List.mem_cons, List.mem_map] at hc
      rcases hc with hc | hc | ⟨q, hq, rfl⟩
      · -- Tseitin definition clauses
        simp only [defClauses, List.mem_flatMap, List.mem_cons] at hc
        obtain ⟨q, _, hc⟩ := hc
        have hcases :
            c = [(V.e t u j q.1 q.2, false), (V.x q.1 q.2 u, true)] ∨
            c = [(V.e t u j q.1 q.2, false),
                 (V.x q.1 (q.2 + dOf t) (wOf u j), true)] ∨
            c = [(V.e t u j q.1 q.2, true), (V.x q.1 q.2 u, false),
                 (V.x q.1 (q.2 + dOf t) (wOf u j), false)] := by
          rcases hc with rfl | rfl | rfl | h
          · exact Or.inl rfl
          · exact Or.inr (Or.inl rfl)
          · exact Or.inr (Or.inr rfl)
          · simp at h
        rcases hcases with rfl | rfl | rfl <;>
          · simp only [CNF.Clause.eval, List.any_cons, List.any_nil, assignOf]
            by_cases h1 : B q.1 q.2 = u <;>
              by_cases h2 : B q.1 (q.2 + dOf t) = wOf u j <;>
                simp [h1, h2]
      · -- at least one covering slot
        subst hc
        obtain ⟨q, ⟨h1, h2⟩, _⟩ := hcov (dOf t) (dOf_val_ne t) u (wOf u j) hune
        refine List.any_eq_true.mpr ⟨(V.e t u j q.1 q.2, true), ?_, ?_⟩
        · exact List.mem_map.mpr ⟨q, mem_slots q, rfl⟩
        · simp [assignOf, h1, h2]
      · -- at most one covering slot
        have hne := ltPairs_ne slots_nodup hq
        refine clause2_eval fun ⟨h1, h2⟩ => hne ?_
        rw [eAssign_iff] at h1 h2
        obtain ⟨w, _, huniq⟩ := hcov (dOf t) (dOf_val_ne t) u (wOf u j) hune
        rw [huniq q.1 h1, huniq q.2 h2]
  simp only [CNF.eval, pmdCnfV, List.all_toArray, List.all_eq_true]
  exact fun c hc => hall c hc

/-- If the `Nat`-relabeled CNF is unsatisfiable, then no (9,6,1)-PMD with 12
blocks exists. -/
theorem no_design_of_unsat (h : CNF.Unsat pmdCnf) :
    ¬∃ B : Fin 12 → Fin 6 → Fin 9, IsPMD1 B := by
  rintro ⟨B, hB⟩
  have hsat : CNF.Sat ((assignOf B ∘ dec) ∘ enc) pmdCnfV := by
    have : (assignOf B ∘ dec) ∘ enc = assignOf B := by
      funext w
      simp [Function.comp, dec_enc]
    rw [this]
    exact eval_pmdCnfV B hB
  have hsat' : CNF.Sat (assignOf B ∘ dec) pmdCnf := CNF.sat_relabel hsat
  rw [CNF.sat_def] at hsat'
  rw [h (assignOf B ∘ dec)] at hsat'
  exact Bool.false_ne_true hsat'

/-! ### The full (symmetry-broken) CNF

A design in `Canonical` form (see `Canon.lean`) additionally satisfies the
symmetry-breaking clauses, so UNSAT of the full CNF also refutes existence. -/

theorem eval_symList (C : Fin 12 → Fin 6 → Fin 9) (hC : Canonical C) :
    ∀ c ∈ symList, CNF.Clause.eval (assignOf C) c = true := by
  intro c hc
  simp only [symList, List.mem_append] at hc
  rcases hc with (((hc | hc) | hc) | hc) | hc
  · -- block 0 is the identity block
    obtain ⟨p, _, rfl⟩ := List.mem_map.mp hc
    simp [CNF.Clause.eval, assignOf, hC.block0 p]
  · -- rotation canonicity
    simp only [rotClauses, List.mem_flatMap, List.mem_map, List.mem_filter] at hc
    obtain ⟨bl, _, p, hp, s, _, s2, hs2, rfl⟩ := hc
    refine clause2_eval fun ⟨h1, h2⟩ => ?_
    simp only [assignOf, decide_eq_true_eq] at h1 h2
    have hlt := hC.rotmin bl p (by
      intro hEq
      exact absurd (congrArg Fin.val hEq) (by simpa using hp.2))
    rw [h1, h2] at hlt
    have := hs2.2
    simp only [decide_eq_true_eq] at this
    exact absurd (Fin.lt_def.mp hlt) (by omega)
  · -- zero placement
    simp only [zeroClauses, List.mem_append, List.mem_map, List.mem_flatMap,
      List.mem_filter] at hc
    rcases hc with ⟨bl, hbl, rfl⟩ | ⟨bl, hbl, p, _, rfl⟩
    · have := hC.zeroFirst bl (by simpa using hbl.2)
      simp [CNF.Clause.eval, assignOf, this]
    · have := hC.noZero bl (by simpa using hbl.2) p
      simp [CNF.Clause.eval, assignOf, this]
  · -- strict order on blocks 0–6
    simp only [order1Clauses, List.mem_flatMap] at hc
    obtain ⟨bl, _, hc⟩ := hc
    by_cases hbl : bl.val < 7
    · rw [dif_pos hbl] at hc
      simp only [List.mem_flatMap, List.mem_map, List.mem_filter] at hc
      obtain ⟨s, _, s2, hs2, rfl⟩ := hc
      refine clause2_eval fun ⟨h1, h2⟩ => ?_
      simp only [assignOf, decide_eq_true_eq] at h1 h2
      have hlt := hC.order1 bl hbl (by omega)
      rw [h1, h2] at hlt
      have := hs2.2
      simp only [decide_eq_true_eq] at this
      exact absurd (Fin.lt_def.mp hlt) (by omega)
    · rw [dif_neg hbl] at hc
      simp at hc
  · -- non-strict order on blocks 8–11
    simp only [order2Clauses, List.mem_flatMap] at hc
    obtain ⟨bl, _, hc⟩ := hc
    by_cases hbl : 8 ≤ bl.val ∧ bl.val < 11
    · rw [dif_pos hbl] at hc
      simp only [List.mem_flatMap, List.mem_map, List.mem_filter] at hc
      obtain ⟨s, _, s2, hs2, rfl⟩ := hc
      refine clause2_eval fun ⟨h1, h2⟩ => ?_
      simp only [assignOf, decide_eq_true_eq] at h1 h2
      have hle := hC.order2 bl hbl.1 hbl.2 (by omega)
      rw [h1, h2] at hle
      have := hs2.2
      simp only [decide_eq_true_eq] at this
      exact absurd (Fin.le_def.mp hle) (by omega)
    · rw [dif_neg hbl] at hc
      simp at hc

theorem eval_pmdCnfVFull (C : Fin 12 → Fin 6 → Fin 9) (h : IsPMD1 C)
    (hC : Canonical C) : CNF.eval (assignOf C) pmdCnfVFull = true := by
  have hbase := eval_pmdCnfV C h
  simp only [CNF.eval, pmdCnfV, List.all_toArray, List.all_eq_true] at hbase
  simp only [CNF.eval, pmdCnfVFull, fullCnfList, List.all_toArray,
    List.all_eq_true]
  intro c hc
  rcases List.mem_append.mp hc with hc | hc
  · exact hbase c hc
  · exact eval_symList C hC c hc

/-- If the full (symmetry-broken) CNF — the instance actually refuted by
kissat — is unsatisfiable, then no (9,6,1)-PMD with 12 blocks exists: any
design could be brought into canonical form, whose induced assignment would
satisfy the CNF. -/
theorem no_design_of_unsat_full (h : CNF.Unsat pmdCnfFull) :
    ¬∃ B : Fin 12 → Fin 6 → Fin 9, IsPMD1 B := by
  rintro ⟨B, hB⟩
  obtain ⟨C, hC, hcanon⟩ := exists_canonical hB
  have hsat : CNF.Sat ((assignOf C ∘ dec) ∘ enc) pmdCnfVFull := by
    have : (assignOf C ∘ dec) ∘ enc = assignOf C := by
      funext w
      simp [Function.comp, dec_enc]
    rw [this]
    exact eval_pmdCnfVFull C hC hcanon
  have hsat' : CNF.Sat (assignOf C ∘ dec) pmdCnfFull := CNF.sat_relabel hsat
  rw [CNF.sat_def] at hsat'
  rw [h (assignOf C ∘ dec)] at hsat'
  exact Bool.false_ne_true hsat'

end P13

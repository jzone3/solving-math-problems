/-
P13: soundness of the symmetry breaking (the WLOG argument), machine-checked.

`gen_cnf.py`'s full encoding adds five clause families to the base encoding:
1. block 0 is the identity block `(0,1,2,3,4,5)`;
2. every block has its minimum at position 0 (rotation canonicity);
3. blocks 0–7 start with point 0, blocks 8–11 do not contain point 0;
4. blocks 0–7 are strictly increasing in their position-1 symbol;
5. blocks 8–11 are non-strictly increasing in their position-0 symbol.

This file proves the WLOG: every (9,6,1)-PMD can be relabeled (point
permutation), rotated (per-block cyclic shift) and reordered (block
permutation) into a design in `Canonical` form, all three operations
preserving `IsPMD1`.  Hence UNSAT of the *constrained* CNF still refutes
existence of any design.
-/
import P13.Encoding

namespace P13

set_option maxRecDepth 10000

/-- Canonical form: the semantic content of the symmetry-breaking clauses. -/
structure Canonical (C : Fin 12 → Fin 6 → Fin 9) : Prop where
  block0 : ∀ p : Fin 6, C 0 p = ⟨p.val, by omega⟩
  rotmin : ∀ (bl : Fin 12) (p : Fin 6), p ≠ 0 → C bl 0 < C bl p
  zeroFirst : ∀ bl : Fin 12, bl.val < 8 → C bl 0 = 0
  noZero : ∀ bl : Fin 12, 8 ≤ bl.val → ∀ p, C bl p ≠ 0
  order1 : ∀ bl : Fin 12, bl.val < 7 →
    ∀ h : bl.val + 1 < 12, C bl 1 < C ⟨bl.val + 1, h⟩ 1
  order2 : ∀ bl : Fin 12, 8 ≤ bl.val → bl.val < 11 →
    ∀ h : bl.val + 1 < 12, C bl 0 ≤ C ⟨bl.val + 1, h⟩ 0

/-! ### Transport of unique existence along an equivalence -/

private theorem existsUnique_comp_equiv {α β : Type _} (f : α ≃ β) {p : β → Prop}
    (h : ∃! y : β, p y) : ∃! x : α, p (f x) := by
  obtain ⟨y, hy, hu⟩ := h
  refine ⟨f.symm y, by simpa using hy, fun x hx => ?_⟩
  have hfx := hu (f x) hx
  rw [← hfx]
  simp

/-! ### The three `IsPMD1`-preserving operations -/

theorem isPMD1_relabel {B : Fin 12 → Fin 6 → Fin 9} (σ : Equiv.Perm (Fin 9))
    (h : IsPMD1 B) : IsPMD1 (fun bl p => σ (B bl p)) := by
  obtain ⟨hinj, hcov⟩ := h
  refine ⟨fun bl => σ.injective.comp (hinj bl), fun t ht u w huw => ?_⟩
  have huw' : σ.symm u ≠ σ.symm w := fun hEq => huw (by
    have := congrArg σ hEq; simpa using this)
  obtain ⟨s, ⟨h1, h2⟩, hu⟩ := hcov t ht (σ.symm u) (σ.symm w) huw'
  refine ⟨s, ⟨by simp [h1], by simp [h2]⟩, fun y ⟨g1, g2⟩ => ?_⟩
  exact hu y ⟨by simp [← g1], by simp [← g2]⟩

theorem isPMD1_permute {B : Fin 12 → Fin 6 → Fin 9} (π : Equiv.Perm (Fin 12))
    (h : IsPMD1 B) : IsPMD1 (fun bl p => B (π bl) p) := by
  obtain ⟨hinj, hcov⟩ := h
  refine ⟨fun bl => hinj (π bl), fun t ht u w huw => ?_⟩
  exact existsUnique_comp_equiv (π.prodCongr (Equiv.refl (Fin 6)))
    (hcov t ht u w huw)

theorem isPMD1_rotate {B : Fin 12 → Fin 6 → Fin 9} (r : Fin 12 → Fin 6)
    (h : IsPMD1 B) : IsPMD1 (fun bl p => B bl (p + r bl)) := by
  obtain ⟨hinj, hcov⟩ := h
  refine ⟨fun bl => (hinj bl).comp fun p q hEq => by simpa using hEq,
    fun t ht u w huw => ?_⟩
  -- slot bijection (bl, p) ↦ (bl, p + r bl)
  let f : (Fin 12 × Fin 6) ≃ (Fin 12 × Fin 6) :=
    { toFun := fun s => (s.1, s.2 + r s.1)
      invFun := fun s => (s.1, s.2 - r s.1)
      left_inv := fun s => by simp
      right_inv := fun s => by simp }
  have base := existsUnique_comp_equiv f (hcov t ht u w huw)
  refine (existsUnique_congr fun s => ?_).mpr base
  refine and_congr Iff.rfl ?_
  show B s.1 (s.2 + t + r s.1) = w ↔ B s.1 (s.2 + r s.1 + t) = w
  rw [add_right_comm]

/-! ### Step 1: relabel points so that block 0 is the identity block -/

/-- Any injection `Fin 6 → Fin 9` can be carried to any other by a permutation
of `Fin 9`. -/
theorem exists_perm_comp (g c : Fin 6 → Fin 9) (hg : Function.Injective g)
    (hc : Function.Injective c) :
    ∃ σ : Equiv.Perm (Fin 9), ∀ p, σ (g p) = c p := by
  classical
  let e₀ : (Set.range g : Set (Fin 9)) ≃ (Set.range c : Set (Fin 9)) :=
    (Equiv.ofInjective g hg).symm.trans (Equiv.ofInjective c hc)
  have hcards : Fintype.card ↥((Set.range g)ᶜ : Set (Fin 9)) =
      Fintype.card ↥((Set.range c)ᶜ : Set (Fin 9)) := by
    have h1 : Fintype.card (Set.range g) = 6 :=
      (Fintype.card_congr (Equiv.ofInjective g hg).symm).trans (by simp)
    have h2 : Fintype.card (Set.range c) = 6 :=
      (Fintype.card_congr (Equiv.ofInjective c hc).symm).trans (by simp)
    rw [Fintype.card_compl_set, Fintype.card_compl_set, h1, h2]
  let e₁ : ↥((Set.range g)ᶜ : Set (Fin 9)) ≃ ↥((Set.range c)ᶜ : Set (Fin 9)) :=
    Fintype.equivOfCardEq hcards
  obtain ⟨σ, hσ⟩ := (Equiv.Set.compl e₀).symm e₁
  refine ⟨σ, fun p => ?_⟩
  have := hσ ⟨g p, Set.mem_range_self p⟩
  rw [this]
  show ((Equiv.ofInjective c hc) ((Equiv.ofInjective g hg).symm ⟨g p, _⟩) : Fin 9) = c p
  rw [Equiv.ofInjective_symm_apply]
  simp

theorem exists_relabel {B : Fin 12 → Fin 6 → Fin 9} (h : IsPMD1 B) :
    ∃ C : Fin 12 → Fin 6 → Fin 9, IsPMD1 C ∧
      ∀ p : Fin 6, C 0 p = ⟨p.val, by omega⟩ := by
  obtain ⟨σ, hσ⟩ := exists_perm_comp (B 0) (fun p => ⟨p.val, by omega⟩)
    (h.1 0) (fun p q hpq => by
      have := congrArg Fin.val hpq
      exact Fin.ext (by simpa using this))
  exact ⟨fun bl p => σ (B bl p), isPMD1_relabel σ h, hσ⟩

/-! ### Step 2: rotate every block so that its minimum is at position 0 -/

theorem exists_rotate {C : Fin 12 → Fin 6 → Fin 9} (h : IsPMD1 C)
    (hb0 : ∀ p : Fin 6, C 0 p = ⟨p.val, by omega⟩) :
    ∃ D : Fin 12 → Fin 6 → Fin 9, IsPMD1 D ∧
      (∀ p : Fin 6, D 0 p = ⟨p.val, by omega⟩) ∧
      (∀ (bl : Fin 12) (p : Fin 6), p ≠ 0 → D bl 0 < D bl p) := by
  have hmin : ∀ bl : Fin 12, ∃ p₀ : Fin 6, ∀ p, C bl p₀ ≤ C bl p := fun bl =>
    Finite.exists_min (C bl)
  choose r hr using hmin
  refine ⟨fun bl p => C bl (p + r bl), isPMD1_rotate r h, ?_, ?_⟩
  · -- block 0 is rotated by 0 because its minimum is already at position 0
    have hr0 : r 0 = 0 := by
      have h1 := hr 0 0
      rw [hb0 (r 0), hb0 0] at h1
      have : (r 0).val ≤ 0 := by exact_mod_cast h1
      exact Fin.ext (by omega)
    intro p
    show C 0 (p + r 0) = _
    rw [hr0, add_zero, hb0 p]
  · intro bl p hp
    have hle := hr bl (p + r bl)
    have hne : C bl (r bl) ≠ C bl (p + r bl) := by
      intro hEq
      have hpr := h.1 bl hEq
      have : p + r bl = 0 + r bl := by rw [← hpr, zero_add]
      exact hp (add_right_cancel this)
    show C bl (0 + r bl) < C bl (p + r bl)
    rw [zero_add]
    exact lt_of_le_of_ne hle hne

/-! ### Step 3: the blocks containing point 0 -/

section Sorting

variable {D : Fin 12 → Fin 6 → Fin 9}

/-- With minima at position 0, point 0 can only sit at position 0. -/
theorem zero_at_pos0
    (hmin : ∀ (bl : Fin 12) (p : Fin 6), p ≠ 0 → D bl 0 < D bl p)
    {bl : Fin 12} {p : Fin 6} (hp : D bl p = 0) : p = 0 := by
  by_contra hne
  have := hmin bl p hne
  rw [hp] at this
  exact absurd this (by simp)

private theorem fin6_zero_add_one : (0 : Fin 6) + 1 = 1 := by decide

/-- Two zero-blocks with the same successor of 0 coincide (uniqueness of the
distance-1 coverage of the pair `(0, w)`). -/
theorem key1_inj (h : IsPMD1 D)
    (hmin : ∀ (bl : Fin 12) (p : Fin 6), p ≠ 0 → D bl 0 < D bl p)
    {b1 b2 : Fin 12} (h1 : D b1 0 = 0) (h2 : D b2 0 = 0)
    (hk : D b1 1 = D b2 1) : b1 = b2 := by
  have hne : (0 : Fin 9) ≠ D b1 1 := by
    intro hEq
    have : (1 : Fin 6) = 0 := zero_at_pos0 hmin hEq.symm
    exact absurd this (by decide)
  obtain ⟨s, _, hu⟩ := h.2 1 (by decide) 0 (D b1 1) hne
  have e1 := hu (b1, 0) ⟨h1, by rw [fin6_zero_add_one]⟩
  have e2 := hu (b2, 0) ⟨h2, by rw [fin6_zero_add_one, hk]⟩
  have := e1.trans e2.symm
  exact (Prod.mk.injEq .. ▸ this).1

/-- Exactly 8 of the 12 blocks contain point 0 (at position 0). -/
theorem card_zeroBlocks (h : IsPMD1 D)
    (hmin : ∀ (bl : Fin 12) (p : Fin 6), p ≠ 0 → D bl 0 < D bl p) :
    Fintype.card {bl : Fin 12 // D bl 0 = 0} = 8 := by
  classical
  have hzmapne : ∀ bl : {bl : Fin 12 // D bl 0 = 0}, D bl.1 1 ≠ 0 := by
    intro ⟨bl, hbl⟩ hEq
    exact absurd (zero_at_pos0 hmin hEq) (by decide)
  let zmap : {bl : Fin 12 // D bl 0 = 0} → {w : Fin 9 // w ≠ 0} := fun bl =>
    ⟨D bl.1 1, hzmapne bl⟩
  have hbij : Function.Bijective zmap := by
    constructor
    · intro b1 b2 hEq
      exact Subtype.ext (key1_inj h hmin b1.2 b2.2 (congrArg Subtype.val hEq))
    · intro ⟨w, hw⟩
      obtain ⟨⟨bl, p⟩, ⟨hs1, hs2⟩, _⟩ := h.2 1 (by decide) 0 w (Ne.symm hw)
      have hp0 : p = 0 := zero_at_pos0 hmin hs1
      subst hp0
      rw [fin6_zero_add_one] at hs2
      exact ⟨⟨bl, hs1⟩, Subtype.ext hs2⟩
  rw [Fintype.card_of_bijective hbij]
  simp [Fintype.card_subtype_compl]

/-! ### Step 4: reorder the blocks -/

theorem exists_sorted (h : IsPMD1 D)
    (hb0 : ∀ p : Fin 6, D 0 p = ⟨p.val, by omega⟩)
    (hmin : ∀ (bl : Fin 12) (p : Fin 6), p ≠ 0 → D bl 0 < D bl p) :
    ∃ E : Fin 12 → Fin 6 → Fin 9, IsPMD1 E ∧ Canonical E := by
  classical
  -- zero-blocks sorted by successor of 0, then the rest sorted by minimum
  let P : Fin 12 → Bool := fun bl => decide (D bl 0 = 0)
  let Lz := (List.finRange 12).filter P
  let Ln := (List.finRange 12).filter (fun bl => !P bl)
  let Lzs := Lz.mergeSort (fun a b => decide (D a 1 ≤ D b 1))
  let Lns := Ln.mergeSort (fun a b => decide (D a 0 ≤ D b 0))
  let L := Lzs ++ Lns
  have hperm : L.Perm (List.finRange 12) :=
    ((List.mergeSort_perm Lz _).append (List.mergeSort_perm Ln _)).trans
      (List.filter_append_perm P (List.finRange 12))
  have hnodup : L.Nodup := hperm.nodup_iff.mpr (List.nodup_finRange 12)
  have hmem : ∀ bl, bl ∈ L := fun bl => hperm.mem_iff.mpr (List.mem_finRange bl)
  have hlen : L.length = 12 := hperm.length_eq.trans (by simp)
  -- the block permutation
  let eL := List.Nodup.getEquivOfForallMemList L hnodup hmem
  let π : Equiv.Perm (Fin 12) := (finCongr hlen.symm).trans eL
  have hπ : ∀ (i : Fin 12) (hi : i.val < L.length), π i = L[i.val]'hi :=
    fun i hi => rfl
  -- length of the zero-block prefix
  have hLzs : Lzs.length = 8 := by
    have h1 : Lzs.length = Lz.length := List.length_mergeSort ..
    have h2 : Lz.Nodup := (List.nodup_finRange 12).filter P
    have h3 : Lz.toFinset = Finset.univ.filter fun bl => D bl 0 = 0 := by
      ext bl
      simp [Lz, P]
    have h4 : Lz.length = Lz.toFinset.card :=
      (List.toFinset_card_of_nodup h2).symm
    rw [h1, h4, h3, ← Fintype.card_subtype, card_zeroBlocks h hmin]
  have hLtot : Lzs.length + Lns.length = 12 := by
    have := hlen
    simpa [L, List.length_append] using this
  -- membership characterizations
  have hmemz : ∀ bl ∈ Lzs, D bl 0 = 0 := by
    intro bl hbl
    have : bl ∈ Lz := (List.mem_mergeSort).mp hbl
    have := (List.mem_filter.mp this).2
    simpa [P] using this
  have hmemn : ∀ bl ∈ Lns, D bl 0 ≠ 0 := by
    intro bl hbl
    have : bl ∈ Ln := (List.mem_mergeSort).mp hbl
    have := (List.mem_filter.mp this).2
    simpa [P] using this
  -- sortedness
  have hsortz : Lzs.Pairwise fun a b => D a 1 ≤ D b 1 := by
    have := List.pairwise_mergeSort
      (le := fun a b => decide (D a 1 ≤ D b 1))
      (fun a b c hab hbc => by
        simp only [decide_eq_true_eq] at *
        exact le_trans hab hbc)
      (fun a b => by
        simp only [Bool.or_eq_true, decide_eq_true_eq]
        exact le_total (D a 1) (D b 1))
      Lz
    exact this.imp fun hab => by simpa using hab
  have hsortn : Lns.Pairwise fun a b => D a 0 ≤ D b 0 := by
    have := List.pairwise_mergeSort
      (le := fun a b => decide (D a 0 ≤ D b 0))
      (fun a b c hab hbc => by
        simp only [decide_eq_true_eq] at *
        exact le_trans hab hbc)
      (fun a b => by
        simp only [Bool.or_eq_true, decide_eq_true_eq]
        exact le_total (D a 0) (D b 0))
      Ln
    exact this.imp fun hab => by simpa using hab
  -- getElem facts for the two halves
  have hgetz : ∀ (i : ℕ) (hi : i < 8), ∀ hL : i < L.length,
      L[i]'hL = Lzs[i]'(by omega) := by
    intro i hi hL
    exact List.getElem_append_left (by omega)
  have hgetn : ∀ (i : ℕ) (hi : 8 ≤ i) (hi2 : i < 12), ∀ hL : i < L.length,
      L[i]'hL = Lns[i - 8]'(by omega) := by
    intro i hi hi2 hL
    have : L[i]'hL = Lns[i - Lzs.length]'(by omega) :=
      List.getElem_append_right (by omega)
    simpa [hLzs] using this
  -- the reordered design
  refine ⟨fun i p => D (π i) p, isPMD1_permute π h, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · -- block 0 is still the identity block
    intro p
    have h12 : (0 : ℕ) < L.length := by omega
    have hL0 : π 0 = Lzs[0]'(by omega) := by
      rw [hπ 0 h12]
      exact hgetz 0 (by omega) h12
    -- the identity block is the unique zero-block with successor 1
    have hb0z : L[0]'h12 ∈ Lzs := by
      rw [hgetz 0 (by omega) h12]
      exact List.getElem_mem _
    have hfirstzero : D (Lzs[0]'(by omega)) 0 = 0 :=
      hmemz _ (List.getElem_mem _)
    have hzeromem : (0 : Fin 12) ∈ Lzs := by
      have : (0 : Fin 12) ∈ Lz := by
        simp only [Lz, List.mem_filter, P]
        refine ⟨List.mem_finRange _, ?_⟩
        simp [hb0 0]
      exact (List.mem_mergeSort).mpr this
    obtain ⟨j, hj, hjeq⟩ := List.getElem_of_mem hzeromem
    have hfirst : Lzs[0]'(by omega) = 0 := by
      rcases Nat.eq_zero_or_pos j with hj0 | hjpos
      · subst hj0; exact hjeq
      · -- key of the first zero-block is ≤ key of the identity block = 1
        have hle : D (Lzs[0]'(by omega)) 1 ≤ D (Lzs[j]'hj) 1 :=
          List.pairwise_iff_getElem.mp hsortz 0 j (by omega) hj hjpos
        rw [hjeq] at hle
        have hD01 : D 0 1 = ⟨1, by omega⟩ := hb0 1
        rw [hD01] at hle
        have hne0 : D (Lzs[0]'(by omega)) 1 ≠ 0 := by
          intro hEq
          exact absurd (zero_at_pos0 hmin hEq) (by decide)
        have hge : (1 : ℕ) ≤ (D (Lzs[0]'(by omega)) 1).val := by
          rcases Nat.eq_zero_or_pos (D (Lzs[0]'(by omega)) 1).val with hv | hv
          · exact absurd (Fin.ext hv) hne0
          · omega
        have hkey : D (Lzs[0]'(by omega)) 1 = ⟨1, by omega⟩ := by
          apply Fin.ext
          have := (Fin.le_def).mp hle
          simp at this ⊢
          omega
        exact key1_inj h hmin hfirstzero (by simp [hb0 0]) (by
          rw [hkey, hD01])
    rw [hL0, hfirst, hb0 p]
  · -- rotation canonicity is invariant under block permutation
    intro bl p hp
    exact hmin (π bl) p hp
  · -- blocks 0–7 start with 0
    intro bl hbl
    have hL : bl.val < L.length := by omega
    rw [hπ bl hL, hgetz bl.val hbl hL]
    exact hmemz _ (List.getElem_mem _)
  · -- blocks 8–11 do not contain 0
    intro bl hbl p
    have hL : bl.val < L.length := by omega
    rw [hπ bl hL, hgetn bl.val hbl (by omega) hL]
    intro hEq
    have hp0 : p = 0 := zero_at_pos0 hmin hEq
    subst hp0
    exact hmemn _ (List.getElem_mem _) hEq
  · -- zero-blocks strictly ordered by successor of 0
    intro bl hbl hsucc
    have hL1 : bl.val < L.length := by omega
    have hL2 : bl.val + 1 < L.length := by omega
    rw [hπ bl hL1, hπ ⟨bl.val + 1, hsucc⟩ hL2]
    rw [hgetz bl.val (by omega) hL1, hgetz (bl.val + 1) (by omega) hL2]
    have hle : D (Lzs[bl.val]'(by omega)) 1 ≤ D (Lzs[bl.val + 1]'(by omega)) 1 :=
      List.pairwise_iff_getElem.mp hsortz bl.val (bl.val + 1) (by omega)
        (by omega) (by omega)
    have hnodupz : Lzs.Nodup :=
      ((List.mergeSort_perm Lz _).nodup_iff).mpr
        ((List.nodup_finRange 12).filter P)
    have hne : Lzs[bl.val]'(by omega) ≠ Lzs[bl.val + 1]'(by omega) := by
      intro hEq
      have := List.Nodup.getElem_inj_iff hnodupz |>.mp hEq
      omega
    refine lt_of_le_of_ne hle fun hkeq => hne ?_
    exact key1_inj h hmin (hmemz _ (List.getElem_mem _))
      (hmemz _ (List.getElem_mem _)) hkeq
  · -- remaining blocks ordered by minimum
    intro bl hbl8 hbl11 hsucc
    have hL1 : bl.val < L.length := by omega
    have hL2 : bl.val + 1 < L.length := by omega
    rw [hπ bl hL1, hπ ⟨bl.val + 1, hsucc⟩ hL2]
    rw [hgetn bl.val hbl8 (by omega) hL1,
      hgetn (bl.val + 1) (by omega) (by omega) hL2]
    simp only [show bl.val + 1 - 8 = (bl.val - 8) + 1 from by omega]
    exact List.pairwise_iff_getElem.mp hsortn (bl.val - 8) (bl.val - 8 + 1)
      (by omega) (by omega) (by omega)

end Sorting

/-! ### The WLOG: every design has a canonical form -/

theorem exists_canonical {B : Fin 12 → Fin 6 → Fin 9} (h : IsPMD1 B) :
    ∃ C : Fin 12 → Fin 6 → Fin 9, IsPMD1 C ∧ Canonical C := by
  obtain ⟨C₁, h₁, hb0₁⟩ := exists_relabel h
  obtain ⟨C₂, h₂, hb0₂, hmin₂⟩ := exists_rotate h₁ hb0₁
  exact exists_sorted h₂ hb0₂ hmin₂

end P13

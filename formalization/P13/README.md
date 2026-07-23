# P13 — Lean 4 formalization: no (9,6,1)-perfect Mendelsohn design exists

Machine-checked version of the SAT-based nonexistence result of
`runs/P13/v3` (headline artifacts in `solutions/P13/`).

## Main theorem

```lean
theorem no_pmd_9_6_1 : ¬ PMD1Exists 9 6      -- P13/Cert.lean
```

where (`P13/Defs.lean`)

```lean
/-- `B` is a (v,k,1)-PMD: `b` blocks, each a cyclic sequence of `k` distinct
points, such that every ordered pair of distinct points appears at every
cyclic distance `t ∈ {1, …, k-1}` in exactly one (block, position) slot. -/
def IsPMD1 {v k b : ℕ} (B : Fin b → Fin k → Fin v) : Prop :=
  (∀ bl : Fin b, Function.Injective (B bl)) ∧
  ∀ t : Fin k, t.val ≠ 0 → ∀ u w : Fin v, u ≠ w →
    ∃! s : Fin b × Fin k, B s.1 s.2 = u ∧ B s.1 (s.2 + t) = w

def PMD1Exists (v k : ℕ) : Prop := ∃ b B, @IsPMD1 v k b B
```

This matches the Abel–Bennett 2006 definition as pinned in
`runs/P13/v3/ADVERSARIAL_REVIEW.md` (blocks as cyclic `k`-sequences of
distinct points; “distance `t` from `x` to `y`” read along the cycle).

## Structure of the proof

| File | Content |
|---|---|
| `P13/Defs.lean` | PMD definition; `block_count₉`: any (9,6,1)-PMD has exactly 12 blocks |
| `P13/Encoding.lean` | The CNF of `runs/P13/v3/gen_cnf.py 9`, reconstructed inside Lean (base encoding `pmdCnf` and full symmetry-broken instance `pmdCnfFull`) |
| `P13/Canon.lean` | The WLOG: every design can be relabeled/rotated/reordered into `Canonical` form (soundness of all five symmetry-breaking clause families, proved — not assumed) |
| `P13/Reduction.lean` | Any design induces a satisfying assignment: of the base CNF directly, and of the full CNF after canonicalization ⇒ `no_design_of_unsat_full` |
| `P13/Cert.lean` | Runs Lean’s verified LRAT checker on the certificate ⇒ `pmdCnfFull_unsat`, and the main theorem |
| `P13/Axioms.lean` | `#print axioms` audit |
| `P13/CertTest.lean` | Tiny end-to-end LRAT smoke test |
| `Dump.lean` | `lake exe dump out.cnf [--full]`: writes the Lean-defined CNF as DIMACS for cross-checking |

There is **no `sorry` and no custom axiom** anywhere.

## Correspondence with the shipped SAT artifacts

`P13/Encoding.lean` re-derives the CNF from the PMD structure inside Lean;
the reduction theorems are proved against *that* object, so the Lean proof
does not depend on the generator script. As an engineering cross-check
(not part of the trusted chain), `lake exe dump` output was compared with
the generator output:

- `lake exe dump out.cnf` is **byte-identical** to `gen_cnf.py 9` without
  symmetry breaking;
- `lake exe dump out.cnf --full` is **byte-identical** to the shipped,
  kissat-refuted instance `solutions/P13/pmd9_unsat.cnf.gz` (uncompressed).

## The certificate

`cert/pmd9_unsat.lrat.xz` (10.6 MB compressed, 59 MB raw). Provenance:

1. `kissat --factor=false --preprocessfactor=false pmd9_unsat.cnf proof.drat`
   — same CNF as the shipped one; bounded variable addition is disabled
   because BVA introduces fresh variables, which Lean's LRAT checker cannot
   represent (its variable universe is sized by the CNF). Solves in seconds.
2. `drat-trim pmd9_unsat.cnf proof.drat -L proof.lrat` (`s VERIFIED`).
3. Lemma ids renumbered to be consecutive (Lean's checker addresses clauses
   by array position, `drat-trim` emits sparse ids); re-verified with
   `lrat-check` after renumbering.

None of these steps is trusted: the certificate is *checked from scratch*
inside Lean by `Std.Tactic.BVDecide.LRAT.check`, whose soundness theorem
`LRAT.check_sound` is kernel-checked mathematics.

## Build

```bash
cd formalization/P13
xz -dk cert/pmd9_unsat.lrat.xz   # decompress the certificate first
lake build                        # elan/lake with toolchain v4.32.0
```

Recorded output: `Build completed successfully (8663 jobs).`

## Axiom audit (recorded output of `P13/Axioms.lean`)

```
'P13.block_count₉'            depends on axioms: [propext, Classical.choice, Quot.sound]
'P13.exists_canonical'        depends on axioms: [propext, Classical.choice, Quot.sound]
'P13.eval_pmdCnfVFull'        depends on axioms: [propext, Classical.choice, Quot.sound]
'P13.no_design_of_unsat'      depends on axioms: [propext, Classical.choice, Quot.sound]
'P13.no_design_of_unsat_full' depends on axioms: [propext, Classical.choice, Quot.sound]
'P13.checkResult_true'        depends on axioms: [propext, Classical.choice, Quot.sound,
                               P13.checkResult_true._native.native_decide.ax_1_1]
'P13.pmdCnfFull_unsat'        depends on axioms: [propext, Classical.choice, Quot.sound,
                               P13.checkResult_true._native.native_decide.ax_1_1]
'P13.no_pmd_9_6_1'            depends on axioms: [propext, Classical.choice, Quot.sound,
                               P13.checkResult_true._native.native_decide.ax_1_1]
```

## What is and is not Lean-verified (trusted components)

Kernel-checked (only the three standard Lean/Mathlib axioms):
- the PMD definition and the 12-block count;
- the CNF encoding as a Lean object and the reduction *design ⇒ satisfying
  assignment* (both for the base and the symmetry-broken CNF, including the
  full WLOG argument — the symmetry breaking is **proved** sound, not assumed);
- the LRAT checker's soundness theorem (`LRAT.check_sound`, part of Lean's
  standard library).

Additionally trusted for the final theorem (via `native_decide`, i.e. the
auto-generated axiom `checkResult_true._native.native_decide.ax_1_1` /
`Lean.ofReduceBool`):
- the Lean **compiler/evaluator** correctly evaluates
  `LRAT.check cert pmdCnfFull` to `true` (the checker itself takes ~5 s on
  the 1,005,098-clause instance; kernel-only evaluation is infeasible);
- `include_str` faithfully embeds `cert/pmd9_unsat.lrat` at compile time.

Not trusted (engineering cross-checks only): kissat, drat-trim, lrat-check,
the DIMACS byte-identity comparison, and the certificate provenance above.
The LRAT parser is also untrusted (a mis-parse could only make the check
fail, not succeed wrongly).

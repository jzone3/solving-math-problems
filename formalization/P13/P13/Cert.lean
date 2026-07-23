/-
P13: checking the UNSAT certificate inside Lean, and the final theorem.

`cert/pmd9_unsat.lrat` is an LRAT certificate for the same CNF as the shipped
DRAT certificate (`solutions/P13/pmd9_unsat.cnf.gz` /`pmd9_unsat.drat.gz`).
It was produced by re-running kissat on the identical CNF with bounded
variable addition disabled (`--factor=false --preprocessfactor=false`, since
BVA introduces fresh variables, which Lean's LRAT checker does not support),
converting DRAT to LRAT with drat-trim, and renumbering lemma ids to be
consecutive (Lean's checker addresses clauses by array position).  It is
stored compressed as `cert/pmd9_unsat.lrat.xz`; decompress before building
(see `formalization/P13/README.md`).

The check runs Lean's verified LRAT checker `Std.Tactic.BVDecide.LRAT.check`,
whose soundness theorem `LRAT.check_sound` is kernel-checked.  The *execution*
of the checker on this 1,005,098-clause instance is performed by
`native_decide`, so the compiled Lean evaluator is trusted for the Boolean
fact `checkResult = true` (axiom `Lean.ofReduceBool`).  Everything else —
the PMD definition, the block count, the WLOG, the reduction to the CNF, and
the LRAT checker's soundness — is ordinary kernel-checked mathematics.
-/
import P13.Reduction
import Std.Tactic.BVDecide

namespace P13

open Std.Sat Std.Tactic.BVDecide

/-- The LRAT certificate, embedded at compile time. -/
def lratStr : String := include_str "../cert/pmd9_unsat.lrat"

/-- The parsed certificate (empty on parse failure, which would then simply
make the check fail — parsing is not trusted). -/
def cert : Array LRAT.IntAction :=
  match LRAT.parseLRATProof lratStr.toUTF8 with
  | .ok c => c
  | .error _ => #[]

/-- Run the verified LRAT checker on the full P13 CNF. -/
def checkResult : Bool := LRAT.check cert pmdCnfFull

/-- The checker accepts the certificate.  Evaluated with `native_decide`
(trusted: compiled Lean evaluator). -/
theorem checkResult_true : checkResult = true := by native_decide

/-- The full P13 CNF — byte-identical, as DIMACS, to the kissat-refuted
instance `solutions/P13/pmd9_unsat.cnf.gz` — is unsatisfiable. -/
theorem pmdCnfFull_unsat : CNF.Unsat pmdCnfFull :=
  LRAT.check_sound cert pmdCnfFull checkResult_true

/-- **Main theorem**: there is no (9,6,1)-perfect Mendelsohn design. -/
theorem no_pmd_9_6_1 : ¬ PMD1Exists 9 6 := by
  rintro ⟨b, B, hB⟩
  have hb := block_count₉ B hB
  subst hb
  exact no_design_of_unsat_full pmdCnfFull_unsat ⟨B, hB⟩

end P13

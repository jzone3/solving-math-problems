/-
Axiom audit.  Expected:
- `no_pmd_9_6_1` and `pmdCnfFull_unsat` use `Lean.ofReduceBool` (via
  `native_decide` running the verified LRAT checker) in addition to the three
  standard axioms `propext`, `Classical.choice`, `Quot.sound`.
- Everything else (definition, block count, WLOG, reduction) uses only the
  three standard axioms.  No `sorry`, no custom axioms anywhere.
-/
import P13.Cert

#print axioms P13.block_count₉
#print axioms P13.exists_canonical
#print axioms P13.eval_pmdCnfVFull
#print axioms P13.no_design_of_unsat
#print axioms P13.no_design_of_unsat_full
#print axioms P13.checkResult_true
#print axioms P13.pmdCnfFull_unsat
#print axioms P13.no_pmd_9_6_1

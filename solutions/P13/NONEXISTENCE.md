# P13 result: no (9,6,1)-perfect Mendelsohn design exists

Claim: there is no (9,6,1)-PMD (the smallest open case of the k=6 spectrum).

Three independent machine confirmations (details in `runs/P13/v3/NOTES.md`):

1. **SAT + checked proof**: `runs/P13/v3/gen_cnf.py 9` produces the CNF
   (`pmd9_unsat.cnf.gz` here, 26,568 vars / 1,005,098 clauses; symmetry breaking is
   sound: block (0..5) forced WLOG by relabeling, rotation-canonical blocks, block
   reordering). kissat: UNSAT in 7.3 s; DRAT proof (`pmd9_unsat.drat.gz`) verified by
   drat-trim: `s VERIFIED`.
   Reproduce: `gunzip -k pmd9_unsat.{cnf,drat}.gz && drat-trim pmd9_unsat.cnf pmd9_unsat.drat`
2. **CP-SAT**: independent OR-Tools model (`runs/P13/v3/pmd_cpsat.py 9`), UNSAT in ~6 s.
3. **Exhaustive backtracking**: `runs/P13/v3/pmd_dfs.py 9`, exact-cover DFS with only
   the WLOG first block fixed, exhausts the space in 581,650 nodes (~10 min), no design.

`verify.py` in this directory checks positive witnesses (used to validate the pipeline
on the existing (7,6,1)-PMD; both search programs' v=7 outputs PASS).

Also: kissat reproduced the known nonexistence of the (10,6,1)-PMD (UNSAT, 4.7 h),
benchmarking the method on a known negative case.

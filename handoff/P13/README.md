# Nonexistence of a (9,6,1)-perfect Mendelsohn design

Self-contained verification package for a math researcher.

## Result

**There is no (9,6,1)-PMD.** This was the smallest open case of the block-size-6 PMD
spectrum: Abel–Bennett (Des. Codes Cryptogr. 40, 2006, Thm 1.4) and Bennett–Zwicker–Chang
(Discrete Math. 309, 2009, Thm 1.3) both list v ≡ 3 (mod 6) as open on the interval
[9, 135]. v = 9 is now settled negatively; the smallest open v ≡ 3 (mod 6) case becomes
v = 15 (and the smallest open k=6 case overall is v = 12).

## Definition

A (v,k,λ)-PMD is a collection of cyclically ordered k-tuples (blocks) of distinct points
from a v-set such that for every distance t = 1..k−1, every ordered pair of distinct points
appears t-apart in exactly λ blocks. For (9,6,1): exactly b = v(v−1)/k = 12 blocks.

## Evidence (three independent methods, plus a hostile fourth)

1. **SAT with checked proof**: `gen_cnf.py 9` → `pmd9_unsat.cnf.gz` (26,568 vars /
   1,005,098 clauses; symmetry breaking audited sound — see ADVERSARIAL_REVIEW.md §1).
   kissat: UNSAT; DRAT proof `pmd9_unsat.drat.gz` verified by drat-trim (`s VERIFIED`).
   Reproduce: `gunzip -k pmd9_unsat.{cnf,drat}.gz && drat-trim pmd9_unsat.cnf pmd9_unsat.drat`
2. **CP-SAT**: independent OR-Tools model `pmd_cpsat.py 9` → UNSAT (~10 s; the optional first-occurrence rule is off by default — only audited-sound symmetry breaking).
3. **Exhaustive backtracking**: `pmd_dfs.py 9` exact-cover DFS, only the WLOG first block
   fixed; exhausts in 581,650 nodes, no design.
4. **Adversarial review (ADVERSARIAL_REVIEW.md): CONFIRMED** — an independent reviewer
   re-derived the definition from the primary papers, audited every symmetry-breaking rule,
   regenerated the CNF byte-identically, wrote their own CNF with a different symmetry
   scheme (fresh kissat UNSAT + fresh drat-trim-verified proof), their own exhaustive DFS,
   and re-verified the shipped DRAT proof.

`verify.py` checks *positive* witnesses and validates the pipeline on the known (7,6,1)-PMD.

Bonus: kissat independently reproduced the known nonexistence of the (10,6,1)-PMD
(UNSAT, 4.7 h), benchmarking the method on a known negative case. (Note: v = 10 is
sometimes wrongly listed as open — Abel–Bennett 2006 Thm 1.3 already settles it.)

## Priority

Checked per this project's widened gate: Abel–Bennett 2006 + Bennett–Zwicker–Chang 2009
full texts, Semantic Scholar citation sweeps, GitHub/Zenodo artifact search — no prior
resolution of (9,6,1) found; this appears to be the first.

## Honest limitations

- **Lean formalization (formalization/P13/)**: `theorem no_pmd_9_6_1 : ¬ PMD1Exists 9 6` —
  the PMD definition, 12-block count, all five symmetry-breaking WLOG steps, and the
  design⇒CNF reduction are kernel-checked (standard three axioms only, no sorry). The
  UNSAT certificate is checked inside Lean by Std's verified LRAT checker; the one extra
  trusted component is `native_decide` (ofReduceBool) to evaluate the checker on the
  1M-clause instance — kernel-only evaluation is infeasible. Independently, the same
  certificate chain is validated externally by drat-trim.
- Paywalled sources not directly inspected: printed CRC Handbook table VI.35 and
  Hantao Zhang's Handbook-of-SAT chapter (both derive from / report the same literature;
  nothing suggests either settles (9,6,1)). The Abel–Bennett 2006 PDF is paywalled
  (Springer, DOI 10.1007/s10623-006-0010-x) — full text was accessed for the review but
  cannot be redistributed here.

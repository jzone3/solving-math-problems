# P14 — Nonexistence results (V1 run, 2026-07-22/23)

**Theorem (computer proof).** No BTD exists for any of:
- BTD(14,18; 7,1,9; 7,4)
- BTD(12,15; 6,2,10; 8,6)
- BTD(12,20; 4,3,10; 6,4)

These were the three instances that survived CPro1 (arXiv:2501.17725, arXiv:2505.23881).
The fourth P14 instance, BTD(14,28; 8,3,14; 7,6), **EXISTS** — see EXISTENCE.md and
`witness-14-28-8-3-14-7-6.txt` in this directory.

## Evidence (each instance, two independent methods)
1. OR-Tools CP-SAT INFEASIBLE on the model in `runs/P14/v1/solve_cpsat.py`
   (684 s / 1482 s / 2007 s respectively). For (12,20) a second independently written
   CP-SAT model (`solve_cpsat_alt.py`) also returned INFEASIBLE (575 s).
2. **DRAT-certified SAT proof**: independent CNF encoding (`runs/P14/v1/encode_sat.py`,
   pysat seqcounter cardinalities + AND-aux products), kissat → `s UNSATISFIABLE`,
   proof checked by drat-trim → `s VERIFIED`, for all three instances.

## Reproduce
```
cd runs/P14/v1
python3 encode_sat.py V B p1 p2 R K L f.cnf     # e.g. 12 20 4 3 10 6 4
kissat -q f.cnf f.proof                          # exit 20 = UNSAT (proofs are 1-40 GB)
drat-trim f.cnf f.proof                          # prints "s VERIFIED"
```

## Soundness note
The only solution-removing device in every encoding is double-lex symmetry breaking
(rows and columns lexicographically ordered). This is sound for the full row/column
permutation group (Flener, Frisch, Hnich, Kiziltan, Miguel, Pearson, Walsh, *Breaking Row
and Column Symmetries in Matrix Models*, CP 2002): every matrix can be brought to a
doubly-lex-ordered form, so UNSAT of the constrained problem implies UNSAT of the original.
The lex constraints were implemented independently three times (two CP-SAT models, one CNF).
Positive controls: the same encoders solve the dev instances (witnesses PASS `verify.py`),
and the CNF encoder's kissat output for BTD(4,8;2,3,8;4,6) decodes to a PASSing witness.

# P02 — Lean 4 formalization

Machine-checked refutation of the statement on West's open-problem list
("every maximal triangle-free graph with min degree ≥ n/3 has a regular
supergraph obtainable by vertex multiplications") via the 9-vertex witness
`W` (graph6 `H?q`qjo`) from `solutions/P02/verify.py`.

Main theorems (`P02/Main.lean`): `west_statement_false : ¬WestStatement`
and `W_no_regular_mult_supergraph`. No `sorry`, no extra axioms, no
`native_decide`. See `runs/P02/lean/NOTES.md` for the full verification
record and fidelity review.

Build:

```
cd formalization/P02
lake exe cache get
lake build
```

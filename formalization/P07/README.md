# P07 — Lean 4 formalization of the Graffiti 154 refutation

Machine-checked refutation of Graffiti (WoW) conjecture 154
("deviation of eigenvalues < n / average distance") via the lollipop
`L(K₅₀, P₇₀)` witness (`n = 120`, `m = 1295`, ordered distance sum
`S = 372120`), plus partial lemmas reducing the conjecture-143 refutation
for the dumbbell `D(20,12,7)` to a single spectral inequality.

No `sorry`, no added axioms, no `native_decide`. See
`../../runs/P07/lean/NOTES.md` for full documentation, encoding conventions
and the `#print axioms` audit.

## Layout

- `P07/Lollipop.lean` — the witness graph, closed-form distance, and the
  certificate proofs that it equals `SimpleGraph.dist`.
- `P07/Main.lean` — the conjecture-154 refutation theorems (integer core,
  real form, both μ conventions, original eigenvalue-deviation wording).
- `P07/Dumbbell.lean` — conjecture-143 witness combinatorics + reduction
  lemma (`conjecture143_false_iff`).
- `P07/AxiomCheck.lean` — `#print axioms` for every main theorem.

## Build

```
lake exe cache get
lake build
```

Toolchain: `leanprover/lean4:v4.32.0`, mathlib `v4.32.0`.

# P06 — Lean 4 formalization of WoW conjecture 698 (adjacency reading)

Machine-checked proof (Lean 4 + mathlib `v4.32.0`, same toolchain and layout as
`formalization/P08`) of

> **WoW 698** (Fajtlowicz, *Written on the Wall*): the Euclidean norm ("length")
> of the negative adjacency eigenvalues of a finite simple graph, counted with
> multiplicity, is at most the Randić index:
> `√(∑_{λᵢ<0} λᵢ²) ≤ R(G) = ∑_{uv∈E} (dᵤ dᵥ)^(−1/2)`.

Main theorem: `P06.wow_conjecture_698` in `P06/Main.lean`. It holds for **every**
finite simple graph (the empty graph and isolated vertices included; no
connectivity or `m ≥ 1` hypothesis).

## Files

* `P06/Spectral.lean` — eigen-expansion of the quadratic form `x ⬝ᵥ A *ᵥ x`
  in mathlib's orthonormal eigenbasis (`Matrix.IsHermitian.eigenvalues`),
  Rayleigh bound `exists_eigenvalue_mul_ge`, and `∑ λᵢ² = trace (A·A)`
  (`sum_sq_eigenvalues_eq_trace_mul_self`, via the spectral theorem and trace
  cyclicity).
* `P06/EdgeSums.lean` — the Randić index `randicIndex` and `S(G) = ∑_E √(dᵤdᵥ)`
  as `Sym2.lift` sums over `G.edgeFinset`; dart/edge double-counting lemmas;
  `x ⬝ᵥ A *ᵥ x = 2S` and `x ⬝ᵥ x = 2m` at `x = (√dᵤ)ᵤ`; `trace(A·A) = 2m`;
  Cauchy–Schwarz over the edges `m² ≤ S·R`.
* `P06/Main.lean` — the proof chain of `solutions/P06/PROOF-698.md`:
  Rayleigh gives an eigenvalue `μ ≥ S/m`, Cauchy–Schwarz gives `μR ≥ m`, AM–GM
  gives `μ² + R² ≥ 2m`, and the trace identity converts this into
  `s⁻² ≤ 2m − μ² ≤ R²`.

## Verification

```
lake exe cache get
lake build            # completes with no errors, no sorry
```

`#print axioms P06.wow_conjecture_698` outputs

```
'P06.wow_conjecture_698' depends on axioms: [propext, Classical.choice, Quot.sound]
```

(no custom axioms, no `native_decide`).

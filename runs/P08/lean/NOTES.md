# P08 Lean formalization — Graffiti conjectures 39 and 40

## STATUS: complete

Both conjectures are fully formalized and proven in Lean 4 + mathlib with **no
`sorry`, no added axioms, no `native_decide`**. `lake build` succeeds and
`#print axioms` on both main theorems reports only the standard three axioms.

## Main theorem statements (formalization/P08/P08/Main.lean)

```lean
/-- Graffiti conjecture 39 -/
theorem graffiti_conjecture_39 {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj] [Nonempty V]
    (hconn : G.Connected) (hA : (G.adjMatrix ℝ).IsHermitian) :
    popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))
      ≤ ((Finset.univ.filter fun v => 0 < hA.eigenvalues v).card : ℝ)

/-- Graffiti conjecture 40 -/
theorem graffiti_conjecture_40 {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [DecidableRel G.Adj] [Nonempty V]
    (hconn : G.Connected) (hA : (G.adjMatrix ℝ).IsHermitian) :
    popStdDev (fun p : V × V => (G.dist p.1 p.2 : ℝ))
      ≤ ((Finset.univ.filter fun v => hA.eigenvalues v < 0).card : ℝ)
```

## Encoding fidelity (why this is the ORIGINAL conjecture)

- **Deviation**: `popStdDev f = Real.sqrt ((∑ i, (f i - popMean f)^2) / card)`
  (`P08/Popoviciu.lean`) is the *population standard deviation* (not the
  sample deviation, not the variance). It is taken over the index type
  `V × V`, i.e. over all `|V|²` **ordered** entries of the distance matrix,
  **diagonal included** (the pairs `(v, v)` contribute distance `0`).
  Entries are graph distances `SimpleGraph.dist` cast from `ℕ` to `ℝ`;
  all arithmetic is over `ℝ`.
- **n⁺ / n⁻**: the adjacency matrix is `G.adjMatrix ℝ`, the real 0/1 matrix.
  `hA : (G.adjMatrix ℝ).IsHermitian` is real symmetry (always true:
  `P08.adjMatrix_isHermitian`; `IsHermitian` is a `Prop`, so the count is
  proof-independent). `hA.eigenvalues : V → ℝ` is mathlib's spectral-theorem
  enumeration of all `|V|` eigenvalues *with multiplicity*, so
  `(univ.filter fun v => 0 < hA.eigenvalues v).card` is exactly the number of
  positive eigenvalues counted with multiplicity (resp. `< 0` for negative).
- No deviations: standard deviation itself is bounded (not just variance),
  over `ℝ` (not `ℚ`), on ordered pairs including the diagonal.

## Axiom check output (from `lake build`, via `#print axioms` in Main.lean)

```
info: P08/Main.lean:217:0: 'P08.graffiti_conjecture_39' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P08/Main.lean:218:0: 'P08.graffiti_conjecture_40' depends on axioms: [propext, Classical.choice, Quot.sound]
Build completed successfully (8661 jobs).
```

## Proof structure (formalization/P08/P08/)

1. `Popoviciu.lean` — population mean/variance/std; Popoviciu's inequality:
   `popStdDev_le_of_mem_Icc : (∀ i, f i ∈ Set.Icc a b) → popStdDev f ≤ (b-a)/2`.
2. `Geodesic.lean` — a shortest walk is an induced path:
   `exists_geodesic_seq` produces `x : ℕ → V` with `G.dist u (x i) = i`,
   injectivity on `[0, d]`, and `G.Adj (x i) (x j) ↔ |i - j| = 1`.
3. `Spectral.lean` — inertia/interlacing bound: if the quadratic form
   `x ⬝ᵥ A *ᵥ x` is positive (negative) definite on the span of `m` linearly
   independent vectors, then `A` has ≥ `m` positive (negative) eigenvalues
   (`le_card_pos_eigenvalues`, `le_card_neg_eigenvalues`), by an
   eigenbasis-expansion + dimension-count argument.
4. `PathSubspace.lean` — on an induced path `x 0 … x d`, the
   `m = ⌊(d+1)/2⌋` vectors `e_{x(2t)} ± e_{x(2t+1)}` are linearly independent
   and the adjacency quadratic form on their span is `±(2∑cₜ² + 2∑cₜcₜ₊₁)
   = ±(c₀² + c_{m-1}² + ∑(cₜ+cₜ₊₁)²)`, which is definite (`tridiag_pos`).
   This replaces the explicit path eigenvalues `2cos(kπ/(d+2))` + Cauchy
   interlacing of the informal proof by a direct definite-subspace argument
   giving the same bound `⌊(diam+1)/2⌋ ≤ min(n⁺, n⁻)`.
5. `Main.lean` — assembles the chain
   `dev(D) ≤ diam/2 ≤ ⌊(diam+1)/2⌋ ≤ min(n⁺, n⁻)`
   (`popStdDev_dist_le_diam`, `floor_diam_le_card_pos`,
   `floor_diam_le_card_neg`, `half_le_floor_succ_half`).

## Versions

- Lean: `leanprover/lean4:v4.32.0` (4.32.0 release, pinned in `lean-toolchain`)
- mathlib: tag `v4.32.0` (commit `81a5d257c8e410db227a6665ed08f64fea08e997`,
  pinned in `lakefile.toml` / `lake-manifest.json`)

## Setup / build instructions

```bash
# install elan (Lean toolchain manager) if needed:
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain none
export PATH=$HOME/.elan/bin:$PATH

cd formalization/P08
lake exe cache get   # fetch prebuilt mathlib oleans (much faster)
lake build           # builds all modules incl. Main.lean with #print axioms
```

Project configuration note: `lakefile.toml` disables mathlib's style-linter
set (`weak.linter.mathlibStandardSet = false`, `weak.linter.style.header =
false`). These are *style* linters only; they have no bearing on proof
soundness. No other options were changed.

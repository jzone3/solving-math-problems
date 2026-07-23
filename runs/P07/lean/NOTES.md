# P07 Lean formalization — refutation witnesses for Graffiti 154 (and partial 143)

## STATUS

- **Theorem 1 (conjecture 154 refuted): COMPLETE.** Fully machine-checked in
  Lean 4 + mathlib, **no `sorry`, no added axioms, no `native_decide`** —
  every theorem depends only on the three standard axioms
  `[propext, Classical.choice, Quot.sound]`. This includes not just the
  integer core but the real-number form AND the original
  eigenvalue-deviation wording.
- **Theorem 2 (conjecture 143 refuted): PARTIAL, honestly delivered.** All
  *combinatorial* facts about the witness are fully proven; the refutation
  is reduced to a single remaining *spectral* inequality on the variance of
  the positive (irrational, algebraic) adjacency eigenvalues, which is NOT
  proven (and NOT faked — no `sorry` anywhere; the unproven statement is
  simply not asserted). See §4.

Project: `formalization/P07/` (Lean 4 v4.32.0, mathlib v4.32.0, mirroring
the P08 project setup). `lake build` succeeds; `#print axioms` output below.

## 1. Theorem 1 — Graffiti (WoW) conjecture 154 is FALSE

Original wording (WoW p. 67, re-verified by OCR in `runs/P07/v5/NOTES.md`):

> **154.** "deviation of eigenvalues < n / average distance."

Witness: the lollipop `L(K₅₀, P₇₀)` = dumbbell `D(2, 68, 50)` of
`solutions/P07/verify.py` (`WITNESSES_154[0]`): a 50-clique with a 70-edge
pendant path; `n = 120`, `m = 1295`.

### Files and main statements

- `P07/Lollipop.lean` — the graph `P07.lollipop : SimpleGraph (Fin 120)`
  (vertices `0–49` the clique, attach vertex `49`, path `50–119`), its
  closed-form distance `distN`, and `lollipop_dist_eq :
  lollipop.dist u v = distN u.val v.val`, plus `lollipop_connected`.
- `P07/Main.lean` — the refutation theorems:

```lean
theorem lollipop_card_edges : lollipop.edgeFinset.card = 1295
theorem lollipop_distSum :
    (∑ u : Fin 120, ∑ v : Fin 120, lollipop.dist u v) = 372120
theorem conjecture154_int_violation :
    2 * 1295 * 372120 ^ 2 > 120 ^ 3 * (120 ^ 2) ^ 2
theorem conjecture154_false_real_form :
    ¬ (2 * (lollipop.edgeFinset.card : ℝ) * lollipopMu ^ 2 ≤ 120 ^ 3)
theorem graffiti_conjecture_154_false :   -- original wording, strict '<'
    ¬ (popStdDev (adjMatrix_isHermitian.eigenvalues) < 120 / lollipopMu)
theorem graffiti_conjecture_154_false_le : -- non-strict '≤' reading
    ¬ (popStdDev (adjMatrix_isHermitian.eigenvalues) ≤ 120 / lollipopMu)
```

where `lollipopMu = (∑ u, ∑ v, (lollipop.dist u v : ℝ)) / 120²` and
`popStdDev f = √((∑ i, (f i − mean)²)/card)` (population standard
deviation).

### How `S` is PROVEN (not asserted)

`lollipop.dist` is mathlib's `SimpleGraph.dist`. It is shown equal to the
closed form `distN` by two finite certificates, both proven by pure
linear-arithmetic case analysis (`omega`) — **no** large `decide`, **no**
`native_decide`:

1. **1-Lipschitz certificate** (`distN_lipschitz`): `distN u v ≤ distN u w + 1`
   whenever `v ~ w`; by walk induction this lower-bounds every walk length,
   so `distN u v ≤ dist u v`… i.e. `dist ≥ distN`.
2. **BFS parent certificate** (`exists_parent`): if `distN u v ≠ 0` there is
   a neighbour `w` of `v` with `distN u w + 1 = distN u v`; by recursion
   this constructs an explicit walk of length exactly `distN u v`, so
   `dist ≤ distN` (and gives connectivity).

The finite sum `∑∑ distN = 372120` and `edgeFinset.card = 1295` are then
evaluated by **plain kernel `decide`** (`maxRecDepth 100000`; ~11 s total).
Plain `decide` was feasible, so `native_decide` was **not** used anywhere;
the axiom print (below) confirms `Lean.ofReduceBool` never appears.

### The eigenvalue-deviation connection (proven, not just stated)

Since `trace A = 0` (`SimpleGraph.trace_adjMatrix`) and `trace A² = 2m`
(diagonal of `A²` = degrees, `adjMatrix_mul_self_apply_self` +
`sum_degrees_eq_twice_card_edges`), the population standard deviation of all
`n` eigenvalues (mathlib spectral-theorem enumeration `hA.eigenvalues`,
with multiplicity) is exactly `√(2m/n)`:

- `sum_eigenvalues : ∑ λᵢ = trace A` (mathlib `trace_eq_sum_eigenvalues`);
- `sum_sq_eigenvalues : ∑ λᵢ² = trace A²` (via `spectral_theorem`;
  conjugation by the eigenvector unitary preserves trace —
  `trace_conjStarAlgAut`);
- `dev_eigenvalues_eq : popStdDev eigenvalues = √(2·1295/120)`.

The original strict inequality `dev < n/μ` then fails because
`(n/μ)² = (1728000/372120)² ≤ 2590/120 = dev²` — an exact rational
comparison equivalent to the integer core `2·m·S² > n³·(n²)²`, i.e.
`358645832496000 > 358318080000000` (margin ≈ 0.0915 %).

**Both readings of the wording refuted.** WoW item 154's wording could be
read strictly (`dev < n/μ`) or non-strictly (`dev ≤ n/μ`). Since the
integer violation is STRICT, the witness in fact satisfies `dev > n/μ`,
which refutes both readings: `graffiti_conjecture_154_false` (¬ `<`, via
`Real.sqrt_le_sqrt` on the non-strict rational comparison) and
`graffiti_conjecture_154_false_le` (¬ `≤`, i.e. `dev > n/μ`, via
`Real.sqrt_lt_sqrt` on the strict rational comparison
`(1728000/372120)² < 2590/120`, which clears denominators exactly to
`358318080000000 < 358645832496000`).

### Encoding conventions (reviewed against the original wording)

- **Average distance μ(D)**: mean of ALL `n² = 14400` **ordered** entries of
  the distance matrix, **diagonal included** (`μ = S/n²`, `S = 372120`) —
  the Roucairol–Cazenave (`rc`) convention used by the 2025 search code and
  by `verify.py`. This is the *harder* convention to violate (it makes μ
  smaller). The classical `pair` convention `μ' = S/(n(n−1))` is violated a
  fortiori: `conjecture154_false_pair_convention`,
  `conjecture154_int_violation_pair`.
- **Ordered vs unordered distance sum**: the ordered sum (each unordered
  pair counted twice) is `S = 372120`; the unordered sum over the
  `C(120,2)` pairs is `S/2 = 186060` (`lollipop_distSum_unordered`).
  *Note:* the task brief called `186060` the "ordered distance sum" — that
  value is actually the **unordered** sum; with the ordered sum the
  clean integer form is `2·m·S² > n³·(n²)²` as proven. (Equivalently
  `8·m·(S/2)² > n⁷`.)
- **Deviation**: population standard deviation (not sample, not variance) of
  all `n` adjacency eigenvalues with multiplicity, over ℝ.
- **Eigenvalues**: of the real 0/1 adjacency matrix `G.adjMatrix ℝ`;
  `IsHermitian` = real symmetry (always true); mathlib's `hA.eigenvalues`
  enumerates all `n` eigenvalues with (algebraic = geometric) multiplicity.

## 2. `decide` usage (all plain kernel `decide`, no `native_decide`)

| Fact | Tactic | Cost |
|---|---|---|
| `∑∑ distN = 372120` (14400 closed-form evals) | `decide` | ~5 s |
| `lollipop.edgeFinset.card = 1295` | `decide` | ~5 s |
| `∑∑ distD = 9952`, `dumbbell.edgeFinset.card = 224` | `decide` | ~3 s |

Since `native_decide` is not used, **no** `Lean.ofReduceBool` axiom is
introduced — there is no compiler-trust trade-off to document beyond noting
we avoided it.

## 3. `#print axioms` output (from `lake build` of `P07/AxiomCheck.lean`)

```
info: P07/AxiomCheck.lean:11:0: 'P07.lollipop_dist_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:12:0: 'P07.lollipop_connected' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:13:0: 'P07.lollipop_card_edges' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:14:0: 'P07.lollipop_distSum' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:15:0: 'P07.conjecture154_int_violation' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:16:0: 'P07.conjecture154_int_violation_pair' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:17:0: 'P07.conjecture154_false_real_form' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:18:0: 'P07.conjecture154_false_pair_convention' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:19:0: 'P07.dev_eigenvalues_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:20:0: 'P07.graffiti_conjecture_154_false' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:21:0: 'P07.graffiti_conjecture_154_false_le' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:24:0: 'P07.dumbbell_dist_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:25:0: 'P07.dumbbell_connected' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:26:0: 'P07.dumbbell_card_edges' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:27:0: 'P07.dumbbell_distSum' depends on axioms: [propext, Classical.choice, Quot.sound]
info: P07/AxiomCheck.lean:28:0: 'P07.conjecture143_false_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## 4. Theorem 2 — conjecture 143 (`Var(positive eigenvalues) < m/μ`): honest partial delivery

Witness: dumbbell `D(20, 12, 7)` (= `dumbbell(20,13,7)` in
`verify143.py`'s edge-count naming): `n = 39`, `m = 224`, `S = 9952`.

**Proven** (`P07/Dumbbell.lean`, same certificate technique, only standard
axioms):

- `dumbbell : SimpleGraph (Fin 39)`, `dumbbell_connected`,
  `dumbbell_dist_eq` (closed-form distance = graph distance),
- `dumbbell_card_edges : edgeFinset.card = 224`,
- `dumbbell_distSum : ∑∑ dist = 9952`,
- `dumbbellMu_eq : μ(D) = 9952/1521`, and the **reduction lemma**

```lean
theorem conjecture143_false_iff :
    ¬ (dumbbellVarPos < (dumbbell.edgeFinset.card : ℝ) / dumbbellMu) ↔
      (10647 / 311 : ℝ) ≤ dumbbellVarPos
```

with `dumbbellVarPos` the population variance of the positive eigenvalues
(mathlib spectral enumeration, filtered by `0 < λ`). So the refutation of
143 for this graph is now *exactly* the single spectral inequality
`dumbbellVarPos ≥ 10647/311 ≈ 34.2347` (numerically
`dumbbellVarPos ≈ 34.3103`, margin ≈ 0.22 %, certified to 40 digits — but
outside Lean — by `verify143.py`'s exact charpoly + isolated real roots).

**Not proven, and why.** The positive eigenvalues are irrational algebraic
numbers (roots of a degree-39 integer characteristic polynomial with a
large `(x+1)^k` clique factor). A fully verified Lean proof would need:
(i) computing the characteristic polynomial of the 39×39 adjacency matrix
inside Lean (kernel-infeasible by `decide`; Faddeev–LeVerrier would need
`native_decide` or a verified computation layer), (ii) a verified count of
its positive roots (Sturm chains / Descartes with certified sign
evaluations — not available in mathlib), and (iii) certified rational
isolating intervals tight enough to lower-bound the variance within the
0.22 % margin. Each piece is a substantial formalization project on its
own; rather than fake it (e.g. with `native_decide`-backed numerical
claims that still wouldn't handle irrational roots, or asserted axioms), we
deliver Theorem 1 in full plus the reduction above, per the task's
explicit instruction.

## 5. Reproduction

```
cd formalization/P07
lake exe cache get   # fetch mathlib olean cache
lake build           # builds everything incl. AxiomCheck (#print axioms)
```

Toolchain: `leanprover/lean4:v4.32.0`, mathlib `v4.32.0`
(same as `formalization/P08`). Full build after cache: ~2 min.

## STATUS: Theorem 1 (conj 154) fully formalized & axiom-clean; Theorem 2 (conj 143) reduced to one explicitly-stated spectral inequality, honestly not asserted

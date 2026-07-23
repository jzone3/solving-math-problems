# Graffiti conjectures 154 & 143 — REFUTED (finite counterexamples)

Self-contained verification package for a math researcher.

## The claims (both false)

From Fajtlowicz, *Written on the Wall* (`wow-july2004.pdf`, July 2004 revision):

- **Conjecture 154**: for every connected graph, 2·m·μ² ≤ n³, where μ is the average distance
  (equivalently: the standard deviation of the adjacency spectrum, √(2m/n), is at most n/μ).
- **Conjecture 143**: the variance of the positive adjacency eigenvalues is at most m/μ.

Conventions (matching Roucairol–Cazenave 2025, who list both as open after searching to n = 50;
`roucairol-cazenave-2025.pdf`, arXiv:2409.18626): μ is the mean of all n² ordered distance-matrix
entries (diagonal included); both witnesses also violate the pairwise (off-diagonal) convention,
so the refutation is convention-robust.

## The witnesses

- **154**: lollipop L(K₅₀, P₇₀) — a 50-clique with a 70-edge path attached; n = 120, m = 1295,
  distance sum S = 372120 over all n² ordered entries (186060 unordered). Violation is a pure integer inequality: 2·m·S² > n³·(n²)² with S = 372120.
  Edge list: `witness_edges.txt`.
- **143**: dumbbell(20, 13, 7) — cliques K₂₀ and K₇ joined by a 13-edge path; n = 39, m = 224.
  Note n = 39 ≤ 50: this sits INSIDE the range searched by the 2025 paper's eight algorithms.

## How to verify

- `python3 verify.py` — conjecture 154; integer-exact; checks both μ conventions. Expect PASS.
- `python3 verify143.py` — conjecture 143; needs sympy/mpmath; isolates eigenvalues to rational
  intervals for an exact variance comparison. Expect PASS.
- Search logs and family analysis: `RUN-NOTES-BOTH.md` (V1 run: both conjectures, incl. the 143 dumbbell analysis), `RUN-NOTES-154-V4.md` (V4 run: 154).

## Lean formalization

`lean/` — conjecture 154's refutation is machine-checked end-to-end in Lean 4 + mathlib: the
witness graph is defined concretely, its distance sum (S = 372120) and edge count (m = 1295)
are PROVEN inside Lean (BFS-parent certificates + kernel `decide`; no `native_decide`), and the
conjecture's real-number form is refuted in both μ conventions, plus the original
spectral wording via dev(eigenvalues) = √(2m/n) — under BOTH possible readings of
item 154 ('<' and '≤'): since the integer violation is strict, the witness satisfies
dev > n/μ (`graffiti_conjecture_154_false` for '<', `graffiti_conjecture_154_false_le`
for '≤'). No `sorry`, no added axioms
(`#print axioms` = [propext, Classical.choice, Quot.sound]). Conjecture 143's witness is
defined with proven structure and a reduction lemma, but the final eigenvalue-variance
computation (irrational algebraic numbers) is deliberately NOT claimed in Lean — the exact-
arithmetic `verify143.py` remains the verification for 143. Build: `cd lean && lake exe cache get && lake build`.

## Notes

- The WoW PDF's Type-3 fonts break copy-paste; the statements were decoded glyph-by-glyph
  (two independent sessions agree) and cross-checked against the RC-2025 Rust encoding.
- n = 120 is the smallest violation in the lollipop family for 154; exhaustive small-n scans and
  the 2025 paper's n ≤ 50 search indicate no substantially smaller counterexample is easy to find.

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
  ordered distance sum S = 186060. Violation is a pure integer inequality: 2·m·S² > n³·(n²)².
  Edge list: `witness_edges.txt`.
- **143**: dumbbell(20, 13, 7) — cliques K₂₀ and K₇ joined by a 13-edge path; n = 39, m = 224.
  Note n = 39 ≤ 50: this sits INSIDE the range searched by the 2025 paper's eight algorithms.

## How to verify

- `python3 verify.py` — conjecture 154; integer-exact; checks both μ conventions. Expect PASS.
- `python3 verify143.py` — conjecture 143; needs sympy/mpmath; isolates eigenvalues to rational
  intervals for an exact variance comparison. Expect PASS.
- Search logs and family analysis: `RUN-NOTES-BOTH.md` (V1 run: both conjectures, incl. the 143 dumbbell analysis), `RUN-NOTES-154-V4.md` (V4 run: 154).

## Notes

- The WoW PDF's Type-3 fonts break copy-paste; the statements were decoded glyph-by-glyph
  (two independent sessions agree) and cross-checked against the RC-2025 Rust encoding.
- n = 120 is the smallest violation in the lollipop family for 154; exhaustive small-n scans and
  the 2025 paper's n ≤ 50 search indicate no substantially smaller counterexample is easy to find.

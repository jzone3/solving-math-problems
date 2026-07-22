# P07 (Graffiti/WoW 154 + sibling 143) — V1: dumbbell/lollipop family optimization

Session: https://app.devin.ai/sessions/358b7aa461984ac2a7461393b1db2540
Branch: `runs/P07-v1`

## 0. Source & statement re-verification

- Original citation: Roucairol–Cazenave, "Refutation of Spectral Graph Theory
  Conjectures with Search Algorithms" (arXiv:2409.18626; ECAI 2025 version at
  lamsade.dauphine.fr/~cazenave/papers/ConjectureRefutationECAI2025.pdf).
  Table 1 lists **143 O (open, searched to n=100)** and **154 O (open, searched
  to n=50)**, "any & tree" graph classes, all 8 search algorithms failed.
- Ground truth for the statements = the authors' own Rust code
  (github.com/RoucairolMilo/refutationGBR, `src/models/conjectures/GenerateGraph.rs`):
  - **154**: `std_dev(all adjacency eigenvalues) <= n / mean(dist matrix)`.
  - **143**: `Var(eigenvalues > 1e-4) <= m / mean(dist matrix)`.
  - Their `std_dev`/variance are **population** (÷k); their `mean(dist matrix)`
    averages the **full n×n matrix including the zero diagonal**, i.e.
    μ_full = S_ord/n² where S_ord = Σ_{i,j} d(i,j) (ordered). The classical WoW
    convention is μ_pairs = S/C(n,2). We refute under **both** conventions.
- Since trace A = 0 and Σλ² = 2m, stdev(spectrum) = √(2m/n) **exactly**, so 154
  ⟺ 2m·μ² ≤ n³ — checkable in pure integer arithmetic (matches problem file).
  (Sample stdev √(2m/(n-1)) is larger, so violations only get stronger.)
- Literature check (arXiv + Exa, July 2026): no published refutation of WoW
  143/154 found post-2025; still open. Attempts to pull the original
  "Written on the Wall" list (DeLaViña's site, wayback) got empty frames; the
  paper's code is the authoritative machine-readable statement.

## 1. Encoding / family

dumbbell(a, ℓ, b): cliques K_a, K_b joined by a path with ℓ edges (ℓ−1 internal
vertices) between one vertex of each clique; b=1 degenerates to the lollipop
L(a, ℓ). n = a+b+ℓ−1, m = C(a,2)+C(b,2)+ℓ. Closed-form integer distance sum
S(a,ℓ,b) implemented with an O(ℓ) loop (`dumbbell_search.py`), verified against
all-pairs BFS on assorted small cases.

Violation tests, exact integers:
- pairs convention: 2·m·S² > n³·C(n,2)²
- full-matrix convention: 8·m·S² > n⁷  (S here = unordered sum; S_ord = 2S)

## 2. Asymptotics (why this family wins)

With a=b=cn, ℓ≈(1−2c)n: stdev = √(2m/n) ~ c√(2n) → ∞ while
n/μ ~ 1/(2c²(1−2c)) = O(1). So 154 fails for every fixed c at large n; the
LHS/RHS ratio grows like √n. Optimizing c³(1−2c) gives c = 3/8, predicting
first violations near n ≈ 700 for the balanced dumbbell — but the integer scan
found the *lopsided* optimum much earlier (lollipop-like shapes win at small n).

## 3. Searches run & results

### Conjecture 154 — REFUTED
- `dumbbell_search.py 1500`: windowed scan around a=b≈3n/8 for n≤1500.
  Ratios 2mμ²/n³ at the family optimum: 0.44 (n=50), 0.77 (n=100), first >1 at
  n=133 (pairs) / n=135 (full); ratio 7.1 at n=1500 — divergent, decisive.
- `minimal_scan.py`: **exhaustive** integer scan over ALL (a,ℓ,b), n ≤ 140:
  - minimal pairs-convention violation: n=118, lollipop (a,ℓ,b)=(48,70,1)
    (equivalently (48,69,2)).
  - minimal both-conventions violation: **n=120, lollipop L(K_50, P_70)**:
    n=120, m=1295, S=186060; stdev=√(2m/n)=4.645787 > n/μ_full=4.643663 and
    > n/μ_pairs=4.604966.
- Witness verifier: `solutions/P07/verify.py` (stdlib only, BFS + exact integer
  comparison, no eigensolve) → PASS. Independently cross-checked with numpy
  `eigvalsh` (stdev matches √(2m/n) to 1e-14) in a separately-written script.

### Conjecture 143 (sibling) — REFUTED
- numpy prescan of Var(positive adjacency eigenvalues) vs m/μ over lollipops
  found violations from n≈49 (L(K_21,P_28)); full dumbbell scan n≤49 found the
  minimal family witness **n=39: dumbbell(20,13,7)** (K_20, K_7, path 13 edges):
  n=39, m=224, S_ord=9952, Var+ = 34.31513… > m/μ_full = 34.23473 >
  m/μ_pairs = 33.35691. 8 positive eigenvalues, smallest ≈ 0.4256 (no 1e-4
  threshold ambiguity).
- Rigor: `solutions/P07/verify143.py` computes the characteristic polynomial
  exactly (sympy, integer coefficients), isolates real roots exactly
  (`real_roots` → CRootOf), evaluates Var to 45 digits; violation margins
  (0.0804 full / 0.9582 pairs) exceed numerical error by >30 orders → PASS.
- NB: n=39 < 100, i.e. *inside* the range the paper's MCTS searched — the MCTS
  landscape simply missed this dumbbell (consistent with the problem file's
  remark that dumbbells are hard to reach edge-by-edge).

## 4. Near-misses / dead ends
- Balanced dumbbells (a≈b≈3n/8) are asymptotically optimal but at small n the
  lopsided lollipop shape crosses first (n=118 vs ≈133 for balanced windows).
- No violation of either conjecture exists in the dumbbell/lollipop family for
  n ≤ 117 (154, exhaustive) — consistent with the 1995 exhaustive n ≤ 10 and
  2025 MCTS n ≤ 50 results for 154.

## 5. Compute spent
~10 min total: exhaustive (a,ℓ,b) integer scans to n=140 and windowed scan to
n=1500 (154); numpy eigensolve grid ~5k lollipops/dumbbells n≤200 (143); exact
sympy charpoly root isolation for the 39-vertex witness (<1 s).

## 6. Files
- `runs/P07/v1/dumbbell_search.py` — closed-form S, windowed scan, BFS cross-check
- `runs/P07/v1/minimal_scan.py` — exhaustive minimal-witness scan (154)
- `solutions/P07/verify.py` — standalone 154 witness verifier (PASS)
- `solutions/P07/verify143.py` — standalone 143 witness verifier, exact roots (PASS)

STATUS: SOLVED — both WoW 154 (n=120 lollipop L(K_50,P_70), exact integer
verification, both μ conventions) and sibling WoW 143 (n=39 dumbbell(20,13,7),
exact charpoly-root verification, both μ conventions) are REFUTED.

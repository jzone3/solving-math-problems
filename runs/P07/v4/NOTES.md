# P07 (Graffiti 154) — V4 run notes

Session: https://app.devin.ai/sessions/2c3ab0a8cf1848769f3d20184a275af7
Variant: **V4 — proof attempt** ("it may be an easy unnoticed theorem — settle it either way;
if a proof gap appears, extract the extremal structure and search it").

## 1. Statement re-verification against the original source

- Cited source: Roucairol–Cazenave 2025, open row of Table 1; their code
  https://github.com/RoucairolMilo/refutationGBR, `src/models/conjectures/GenerateGraph.rs`,
  block `CONJECTURE == 154` (cloned and read directly).
- Their exact test: `std_dev(adjacency eigenvalues) <= n / mean(dist_matrix entries)`, where the
  mean runs over **all n² entries of the distance matrix, diagonal zeros included**, and
  `std_dev` is the population standard deviation. So their μ₁ = 2S/n² with
  S = Σ_{unordered pairs} d(u,v).
- Classical "average inter-vertex distance" (Graffiti/WoW usage) is μ₂ = 2S/(n(n−1)) > μ₁, so
  the RC form (RHS n/μ₁ larger) is the *harder* one to violate; a violation of it violates the
  pairs form too. We refute **both**.
- Exact equivalences used (adjacency eigenvalues sum to 0, Σλᵢ² = trace(A²) = 2m, hence
  std = √(2m/n) exactly — no eigensolve needed):
  - RC form:    std ≤ n/μ₁  ⇔  8·m·S² ≤ n⁷
  - pairs form: std ≤ n/μ₂  ⇔  8·m·S² ≤ n⁵(n−1)²
- Openness as of July 2026: conj. 154 is listed open in RC 2025 Table 1 (searched only to
  n = 50); exhaustive check only to n ≤ 10 (Brewster–Dinneen–Faber 1995). No literature hit for
  the reformulation 2mμ² ≤ n³. Consistent with problem file.

## 2. Proof attempt (V4 core) — and where it breaks

Try to prove 2m·μ² ≤ n³ for connected G:

- Erdős-type average-distance bounds: for connected graphs μ ≤ (n+1)/3 (path is extremal), and
  the sharper m-dependent bound μ ≲ n/(δ+1)-type / Kouider–Winkler μ ≤ n/(δ+1) + O(1).
- Naive combination fails badly: with μ ≤ (n+1)/3 one needs 2m ≤ 9n³/(n+1)² ≈ 9n, i.e. only
  graphs with average degree ≤ ~9 could be handled this way — the bound ignores the m–μ
  trade-off entirely.
- The trade-off is the whole content: dense graphs have small μ, sparse graphs have small m.
  Test the product on a mixed family. Dumbbell(a, ℓ, b) (cliques K_a, K_b joined by a path of ℓ
  edges): m ≈ a²+b², and the a·b clique–clique pairs sit at distance ≈ ℓ. With a = b = cn,
  ℓ = (1−2c)n: m ~ 2c²·n²/... precisely m ≈ c²n²·(1)·2/2·... (exact: 2·C(cn,2)+ℓ), μ ≳ 2c²(1−2c)n,
  so 2mμ² ≳ 8c⁶(1−2c)²·n⁴ = Θ(n⁴) ≫ n³.
  Maximizing c⁶(1−2c)² gives c = 3/8, constant ≈ 0.00139 — crossover predicted near n ≈ 700
  from the crude lower bound, and much earlier once all distance contributions are counted.
- **Conclusion of the proof attempt: the conjecture is FALSE; the "proof gap" is exactly the
  dumbbell family**, which the edge-by-edge MCTS at n ≤ 50 could not reach (violations start
  at n ≈ 118–135).

## 3. Exact search of the extremal structure

Code: `runs/P07/v4/dumbbell_search.py` (pure Python, exact integer arithmetic; closed-form
distance sum for dumbbell(a, ℓ, b) validated against brute-force BFS on all a,b ≤ 6, ℓ ≤ 7).

- Full asymmetric scan (all a, b, ℓ) for n ≤ ~140; near-balanced scan for n ≤ 3000.
- **First violation, pairs form**: dumbbell(2, 69, 48), n = 118.
- **First violation, RC form (diagonal-included mean)**: dumbbell(2, 69, 50), n = 120
  (= lollipop: K_50 with a pendant path of 70 edges; m = 1295, S = 186060;
  8mS² = 358 645 832 496 000 > n⁷ = 358 318 080 000 000).
- Smallest **balanced** violation: dumbbell(36, 64, 36), n = 135 (m = 1324, S = 277950).
- Ratio 8mS²/n⁷ grows linearly: ≈ 3.43 at n = 500 (a=136, ℓ=230, b=135), ≈ 6.76 at n = 1000,
  ≈ 20.1 at n = 3000 (a=812, ℓ=1378, b=811) — the asymptotic Θ(n⁴) vs n³ analysis confirmed.
- Compute: minutes of CPU; no randomness anywhere; all comparisons on Python bignums.

## 4. Verification

`solutions/P07/verify.py` — standalone, stdlib-only: builds dumbbell(2,69,50) and
dumbbell(36,64,36) adjacency lists, BFS all-pairs distances, exact integer comparison of
8mS² against both n⁷ and n⁵(n−1)²; prints PASS. Both witnesses violate both μ conventions.

Independent second check (different code path, float): numpy `eigvalsh` population std of the
adjacency spectrum vs n/μ₁ computed from a BFS distance matrix, RC-style:
- dumbbell(2,69,50): std = 4.645787 > n/μ = 4.643663
- dumbbell(36,64,36): std = 4.428862 > n/μ = 4.425931
(RC's own refutation trigger is `std − n/μ > 1e−5`; our margin is ~2×10⁻³.)

## 5. Dead ends / caveats

- Margins near the crossover are thin; anyone re-verifying should use exact arithmetic (the
  verify script does) or the n≥500 witnesses where the ratio is ≥ 3.
- Definition ambiguity of μ (diagonal-included vs pairs) noted and neutralized: witnesses
  violate both.
- Sibling conj. 143 (Var(positive eigenvalues) ≤ m/μ) NOT settled here — it needs an eigensolve
  and is V5's assignment; the dumbbell family is a plausible seed for it too.

## STATUS: SOLVED (refuted) — Graffiti 154 is false; minimal dumbbell witness dumbbell(2,69,50), n = 120 (RC convention; n = 118 for the pairs convention), machine-verified exactly by solutions/P07/verify.py (PASS) plus an independent numpy eigensolve cross-check.

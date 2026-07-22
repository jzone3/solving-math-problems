# P07 / V5 — Graffiti 143 (twin of 154) — session notes

Session: https://app.devin.ai/sessions/d4e120cb42b143b19f33b6bb5e781586
Variant: **V5 — conj-143 twin** (Var(positive adjacency eigenvalues) ≤ m/μ(D)),
plus (bonus) conjecture 154 itself, which fell to the same dumbbell family.

## 1. Statement re-verification against the original source

- Downloaded the original *Written on the Wall* list (Fajtlowicz, July 2004 revision,
  https://independencenumber.wordpress.com/wp-content/uploads/2012/08/wow-july2004.pdf).
  The PDF has broken Type3 font encoding, so OCR'd all 216 pages (pdftoppm 150dpi + tesseract).
  Exact original texts (WoW p. 66–67):
  - **143.** "variance of positive eigenvalues < size / average distance."
  - **154.** "deviation of eigenvalues < n / average distance."
  ("size" = number of edges m.)
- Cross-checked the machine encoding actually used in the 2025 search paper
  (Roucairol–Cazenave, refutationGBR, `GenerateGraph.rs`, blocks `CONJECTURE == 143/154`):
  - Var = population variance of eigenvalues > 1e-4; μ(D) = mean of **all n² entries** of the
    distance matrix (diagonal zeros included).
  - 154: population std-dev of **all** adjacency eigenvalues vs n/μ, same μ convention.
- Ambiguity handling: the classical "average distance" is the mean over the n(n−1) (ordered)
  pairs of distinct vertices, which is **larger** than the n²-mean by a factor n/(n−1).
  Since μ multiplies the LHS-favoring side in both conjectures, the n²-convention ("rc") is the
  **harder** one to violate. All claimed witnesses violate **both** conventions.
- Openness as of 2026-07: both are "O" rows in Roucairol–Cazenave 2025 Table 1
  (143 searched to n = 100, 154 to n = 50); repo research file `research/spectral-and-automated.md`
  (dated 2026-07-22) confirms; a quick Exa literature pass found no refutation/proof since.

## 2. Reasoning (literature-first, per V5 framing)

Key inequality chain: with p = #positive eigenvalues, Q⁺ = Σ_{λ>0} λ² ≤ 2m,
Var ≤ Q⁺/p ≤ 2m/p, so a violation of 143 needs μ(D) > p/2·(roughly): i.e. graphs with **few
positive eigenvalues but large average distance**. Long paths have p ≈ n/2 and μ ≈ n/3 — never
violates. A clique K_a glued to a path contributes ONE huge eigenvalue (≈ a−1) while the path
supplies the distance mass; the clique's λ₁² term makes Var ≈ λ₁²/p huge.

Closed-form asymptotics (lollipop L(a=cℓ, ℓ), n = (1+c)ℓ):
Var·μ/m → 4(c+1/3)/(1+c)², maximized at c = 1/3 with limit **3/2 > 1** ⇒ conjecture 143 is
asymptotically false on lollipops. For symmetric dumbbells D(a, ℓ, a) with a = cn:
ratio → (4/L)(2c²L + 2cL² + L³/3), L = 1−2c; letting ℓ grow sublinearly (c→1/2) the ratio
tends to **2**. Numerics match (see §3).

For 154: 2m·μ² vs n³ on dumbbells with a fixed tiny clique: m ≈ b²/2 grows quadratically while
μ stays ≈ Θ(n), giving 2mμ²/n³ ≈ Θ(n) → ∞; crosses 1 near n ≈ 120.

## 3. Computations

All code in this directory; scorer `score143.py` (BFS distances exact, numpy eigvalsh).

- `scan1.log` — lollipop sweep: first violation of 143 at **n = 50** (L(24,26), ratio_rc 1.025);
  ratio grows to 1.39 at n = 400 (a/n → 1/3, matching the closed form).
- `scan_min.log` — full (a,ℓ,b) dumbbell + lollipop sweep n = 10..60:
  minimal violations found —
  - n = 37: D(6,12,19) violates the pair convention (ratio 1.00245);
  - **n = 39: D(7,12,20) violates BOTH conventions** (ratio_rc 1.00235, pair 1.02873);
  - every n ≥ 39 has dumbbell violations, margins growing.
- `scan_db_large.log` — dumbbell optimum at larger n: D(36,28,36) ratio_rc 1.473 (n=100),
  D(75,50,75) 1.695 (n=200), D(115,70,115) 1.779 (n=300) → consistent with sup = 2.
- `scan154.log`, `scan154_min.log` — conjecture 154 (exact integer test 2m·dsum² vs n³·D²):
  first violations at n = 118 (pair convention, D(2,66,50)) and **n = 120 (both
  conventions, D(2,68,50))**; family D(2, ℓ, b) ≈ one big clique with a long path
  (b/n ≈ 0.42). Ratio 1.60 already at n = 200 (D(2,114,84)), Θ(n) growth.
- `crosscheck_mp.py` / `crosscheck_mp.log` — **independent second verification** of the three
  143 witnesses: exact integer characteristic polynomial (Faddeev–LeVerrier over Fractions),
  exact deflation of the (x+1)^k clique factor, mpmath 50-digit polyroots. Agrees with the
  LAPACK-based verifier to 17+ digits; all VIOLATED.

## 4. Result

**Both Graffiti 143 and Graffiti 154 are FALSE.** Witnesses (dumbbell D(a,ℓ,b) = K_a and K_b
joined by a path with ℓ internal vertices), verified by `solutions/P07/verify.py` (prints PASS):

| Conj | Witness | n | ratio (rc / pair) |
|---|---|---|---|
| 143 | D(7,12,20) | 39 | 1.00235 / 1.02873 (minimal found for both-defs) |
| 143 | D(25,18,17) | 60 | 1.2263 / 1.2471 |
| 143 | D(36,28,36) | 100 | 1.4732 / 1.4881 |
| 154 | D(2,68,50) | 120 | 1.00091 / 1.01781 (minimal found for both-defs) |
| 154 | D(2,114,84) | 200 | 1.60087 / 1.61700 |

Why prior searches missed it: the 1995 exhaustive check stopped at n ≤ 10 (first violation
n = 37/39); the 2025 MCTS built graphs edge-by-edge with 15-minute budgets and evidently never
assembled a ~230-edge two-clique-plus-path structure at n ≥ 39 (and 154's first violation at
n ≈ 118 lies beyond its n = 50 horizon entirely).

Near-misses / dead ends: rigorous-by-inequality lower bounds on Var (energy bound
S⁺ ≤ √(2mn)/2 etc.) were too weak to certify the n=100 witness by hand — resolved instead by
LAPACK backward-stability + exact-trace/nullity cross-checks + independent charpoly/mpmath
verification.

Compute spent: ~1.5 h of scans (single core, numpy), n up to 800 for family sweeps.

## STATUS: SOLVED (counterexamples found and machine-verified for BOTH conj 143 and conj 154; refutes P07 headline statement 2m·μ(D)² ≤ n³)

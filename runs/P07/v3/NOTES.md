# P07 (Graffiti 154) — V3 run notes

Session: https://app.devin.ai/sessions/1f7b189e828243af83cc3797beca148b
Variant: V3 (annealed search at n = 100–2000, sparse rep, BFS scoring, score = 2mμ²/n³, seeds from dumbbell/lollipop near-optima).

## 0. Statement re-verification against original source

- Original cited source: Roucairol & Cazenave, *Refutation of Spectral Graph Theory
  Conjectures with Search Algorithms*, arXiv:2409.18626v1. Table 1 lists Graffiti **154**
  as **O**pen, searched to size **50** ("any & tree"); sibling **143** open, searched to 100.
- Exact operational definition taken from their public solver code
  (github.com/RoucairolMilo/refutationGBR, `src/models/conjectures/GenerateGraph.rs`,
  `CONJECTURE == 154`):
  - stdev = **population** standard deviation of all n adjacency eigenvalues
    (mean eigenvalue = 0 ⇒ stdev = √(2m/n) exactly, since Σλ² = 2m).
  - mean distance = mean of **all n² entries of the distance matrix** (diagonal zeros
    included): μ₂ = 2W/n², W = Wiener index.
  - Refuted iff stdev − n/μ > 1e−5 in their code; mathematically: **2m·μ₂² > n³ ⟺ 8mW² > n⁷**
    (exact integer test — no eigensolve, no floats needed).
- We also track the classical "average distance over unordered pairs" μ₁ = W/C(n,2) ≥ μ₂;
  any μ₂-violation is automatically a μ₁-violation, so the witness refutes the conjecture
  under **both** plausible readings of "average distance".
- Literature check (July 2026): no refutation of Graffiti 154 found in arXiv follow-ups to
  2409.18626 or in the Roucairol–Cazenave COCOON 2022 paper; the 2024/2025 versions still
  list it open. Problem file's n≤50 status confirmed.

## 1. Key structural insight (why the search regime matters)

For dumbbell/lollipop(a, ℓ, b) with a = αn, ℓ = βn: m ≈ α²n², W ≈ (α²β + αβ² + β³/6)n³,
so score = 8mW²/n⁷ ≈ 8α²(α²β + αβ² + β³/6)² · **n** — it grows **linearly in n**.
At the optimum (α ≈ 0.42–0.43 of a-fraction… empirically a ≈ 0.42n, ℓ ≈ 0.57n) the
coefficient is ≈ 1/120, so the family crosses score = 1 near **n ≈ 120** — just above the
n ≤ 50 horizon of the MCTS searches. This explains exactly why the conjecture survived: the
counterexamples live at n ≥ 120.

## 2. Exact dumbbell/lollipop scan (seeding step)

`dumbbell_scan.py` (exact integer arithmetic, closed-form W): scanned all (a, ℓ, b),
b ≤ a, n ≤ 260. Best-score family at each n is a lollipop-like dumbbell with tiny second
clique (b = 1–2). Score at n: 0.851 (n=100), 0.9936 (n=119), **1.000915 (n=120)** —
**first dumbbell violation at n = 120: (a, ℓ, b) = (50, 68, 2), m = 1295, W = 186060,
8mW² / n⁷ = 1.000915 > 1** (also violates μ₁ form, ratio 1.017807).
BFS-based re-scan including b=1 lollipops (n=110–124) confirms: nothing in the family
violates below n=120; at n=120 the best is score 1.000915.

## 3. Witness + verifier

- `solutions/P07/witness_edges.txt`: dumbbell(50, 68, 2), n=120, m=1295 (K50 hub vertex 0 —
  68-vertex path — K2).
- `solutions/P07/verify.py`: standalone stdlib verifier — rebuilds graph from edge list,
  BFS all-pairs distances, exact integer test 8mW² > n⁷ (and μ₁ variant), optional numpy
  eigensolve cross-check of the literal stdev ≤ n/μ statement. **Prints PASS.**
  Output: stdev(eigs) = 4.645787 > n/μ₂ = 4.643663 (and > n/μ₁ = 4.604966).

## 4. Annealed / local search (V3 core): can general graphs beat n = 120?

- `anneal.py`: simulated annealing over connected graphs, edge-toggle moves, scipy
  C-speed BFS all-pairs, float score with exact integer confirmation of any candidate > 1.
- `hillclimb.py`: steepest-ascent over all C(n,2) single-edge toggles from the best
  lollipop seed.
- Runs at n = 115–119 (anneal 1800 s each + full hill climbs): RESULTS_PLACEHOLDER

## 5. Large-n scaling (n up to 2000)

SCALING_PLACEHOLDER

## STATUS

STATUS_PLACEHOLDER

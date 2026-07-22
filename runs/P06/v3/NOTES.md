# P06 — WoW 129/698 (dev of Laplacian eigenvalues vs Randić index) — V3 (large-n asymptotics)

Session: https://app.devin.ai/sessions/c476f264ed76476e90bd2aa97ee05c0c
Variant: **V3 — large-n asymptotics of candidate families; binary-search smallest concrete n on violation.**

## 0. Statement verification (against original sources)

- Operational definition taken from `RoucairolMilo/refutationGBR` (`GenerateGraph.rs`,
  `invariants.rs`), CONJECTURE == 129:
  `std_dev(eigenvalues of Laplacian) <= randic_index`, where `std_dev` divides by **n**
  (population convention) and `randic_index = Σ_{uv∈E} (d_u d_v)^{-1/2}`.
- Roucairol–Cazenave (arXiv 2409.18626, ECAI 2025) Table 1: rows 129 and 698 are **"O"
  (open)**, size 50, graph class **"any"** (no connectivity restriction). Confirmed by
  downloading and grepping the PDF (2026-07-22). No dedicated literature found on
  variance-of-Laplacian-spectrum vs Randić (Exa searches; only Randić-energy /
  normalized-Laplacian papers, different invariants).
- Brewster–Dinneen–Faber 1995 (graffiti1.pdf) tested ~200 conjectures on **all** graphs
  with ≤ 10 vertices (Cameron–Colbourn–Read–Wormald tape — includes disconnected);
  129 not in their failed list ⇒ exhaustively true for n ≤ 10. Their glossary defines
  Laplacian; "deviation" = standard deviation (population).
- **Definitional finding on 698**: the refutationGBR code for 698 computes
  `sqrt(Σ_{μ_i<0} μ_i²)` over **Laplacian** eigenvalues — but L ⪰ 0, so this is
  identically 0 and conjecture 698 *as coded* is vacuously true (0 ≤ R); it can never be
  refuted by that harness. Likely intended reading: norm of negative **adjacency**
  eigenvalues (stars give equality √(n−1) = R there). Flagged; V3 focuses on 129.

## 1. Key structural discoveries (machine-verified, `sanity.py`)

### 1a. dev is degree-only (trace identity)
trace(L) = 2m, trace(L²) = Σd² + 2m ⇒

    dev² = (Σd² + 2m)/n − (2m/n)²  =  Var(degrees) + average degree.

No eigensolve needed, exact rational arithmetic possible. Conjecture 129 ⇔
**Var(d) + d̄ ≤ R(G)²** — a purely degree/edge-weight inequality.

### 1b. Exact equality family (NEW near-miss family, far tighter than stars)
For H = K_t plus k isolated vertices, R is unchanged by padding while dev²(n) =
A/n − 4m²/n² (A = Σd(d+1)) is maximized at n* = 8m²/A. For K_t, n* = 2(t−1), i.e.
k = t−2 isolated vertices, giving **dev = R = t/2 EXACTLY for every t ≥ 2**
(verified exactly in `sanity.py` for t = 3..59). The conjecture is *tight* on an
infinite family — equality, not just o(1) gap (stars have gap R²−dev² → 2).

### 1c. Padding reduction
Adding isolated vertices to any core H changes only n. Max over padding:
dev² ≤ A²/(16m²), attained iff n = 8m²/A ≥ n_H. Hence a padded counterexample from
core H exists iff Φ(H) = max_{n'≥n_H} [A/n' − 4m²/n'² − R²] > 0.
- For d-regular H: A/(4m) = (d+1)/2 ≤ n/2 = R, equality iff H complete. So no regular
  core works, cliques are the unique regular equality cores.
- Stars satisfy A > 4mR (k ≥ 14) but their n* < n_H, padding infeasible; direct value
  is dev² − R² = −2 + 6/n − 4/n² < 0. This explains why stars are near-misses that
  can never cross.

## 2. Exhaustive frontier pushed (C scanner `scan.c`, geng)

Objectives per graph: direct dev − R, and padded Φ (with the n' ≥ n_H constraint).
- n ≤ 9 (python `scan_geng.py`) and n = 10 (12,005,168 graphs, 3.3 s): max dev−R = 0,
  attained **only** by K_t ∪ (t−2)K_1; padded Φ ≤ 0, equality only cliques+padding.
- n = 11 (1,018,997,864 graphs, 8-way geng split, ~1 min): **no violation**;
  best direct −0.0124 (K_7 ∪ 4K_1, one isolated short of optimal padding),
  best Φ = 0 (equality graphs only). Extends Brewster–Dinneen–Faber's 1995 n ≤ 10
  exhaustive frontier to n ≤ 11.
- n = 12 (165,091,172,592 graphs): running (8-way split), see §5.

## 3. Family asymptotics (`families.py`, mpmath 60 dps, t up to 10^4, padded Φ)

All families collapse to Φ = 0 exactly at the clique point and are strictly negative
elsewhere; the penalty for a single-edge deviation tends to ≈ −1 (in dev²−R² units):
- K_t + vertex of degree j: Φ < 0 for j < t, → 0 only at j = t (= K_{t+1}).
- K_t − star(j), K_t − matching(j): best Φ ≈ −1 + O(1/t) at j = 1.
- two K_t sharing s vertices: Φ < 0, best at s = t−1 (= K_t + vertex).
- complete split CS(n,s): Φ = 0 only at s = n−1 (clique); < 0 otherwise.
- pineapple, kite: Φ strongly negative (kite → −Θ(√n)).
Hill-climb / annealing on the padded objective (edge flips, n = 12..60, `hillclimb.py`):
always saturates at Φ = 0 (converges to a clique), never above.

## 4. Interpretation so far

The padded-equality manifold {K_t ∪ kK_1} appears to be a strict global maximum of
dev − R (value 0). Every explored perturbation direction costs Θ(1). Strongly suggests
WoW 129 is TRUE with equality characterization dev = R iff G = K_t ∪ (t−2)K_1
(t ≥ 2). A proof would need: Var(d) + d̄ ≤ R², sharp at those graphs; standard
Cauchy–Schwarz/power-mean bounds checked here are too lossy on stars (which are
within O(1/n) of tightness in a different direction).

## 5. Status: (updated as runs finish)

- n=12 exhaustive: IN PROGRESS
- threshold-graph exhaust: planned
- STATUS (preliminary): negative / frontier-pushed

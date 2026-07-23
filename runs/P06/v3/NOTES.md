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

## 5. Threshold-graph exhaust (`threshold.c`)

All 2^(n−1) threshold creation sequences for every n ≤ 30 (~10^9 graphs): max dev−R = 0
and max Φ = 0, attained only at K_t ∪ kK_1 codes. Extremal graphs for the padded
objective among threshold graphs are exactly the equality family.

## 6. Unified GM reduction — main theoretical finding

AM–GM over Randić edge weights (Σ_{uv∈E} ln(d_u d_v) = Σ_v d_v ln d_v) gives the
standard bound R ≥ m·exp(−(1/2m) Σ_v d_v ln d_v). Hence WoW 129 follows from the
purely **degree-sequence** inequality

  (★)  n² m² ≥ (nA − 4m²) · exp((1/m) Σ_v d_v ln d_v)    [note nA − 4m² = n²·dev²]

for every *graphical* sequence (graphicality essential: (5,5,5,5,0,0) violates (★)
but is not graphical; stars satisfy it with relative slack → 0).

Evidence for (★):
- Annealed adversarial search over graphical sequences (`lemma_opt3.py`,
  n = 8..100, Erdős–Gallai-constrained moves): max g = 0 (up to 1e-15),
  attained only at K_t ∪ (t−2)K_1 sequences.
- Exhaustive over ALL graphical degree sequences (`enum_seq.c`):
  n = 8 (1,212 seqs), 10 (16,015), 12 (222,116), 14 (3,166,851),
  every n ≤ 22 (odd and even): counts include n = 16 (45,967,478),
  n = 18 (675,759,563), n = 19 (2,600,672,457), n = 20 (10,029,832,753),
  n = 21 (38,753,710,485; 8-way partition by d₁),
  n = 22 (149,990,133,773; 8-way partition by d₁).
  Max g = 0 (±2e-15) for even n, attained ONLY at the K_t ∪ (t−2)K_1 sequence
  (t = n/2+1); max g < 0 strictly for odd n (as predicted by the closed form:
  equality needs t−1 = n/2). No violation anywhere.
- Closed form on the equality family: for K_t ∪ zeros, (★) reduces to
  (t−1)(n−t+1) ≤ n²/4 — plain AM–GM, equality iff t−1 = n/2, i.e. exactly
  the K_t ∪ (t−2)K_1 padding. So (★) is sharp precisely at the equality family.
  **Each completed n here verifies conjecture 129 for ALL graphs on n vertices**
  (via R ≥ m·GM), independent of geng — a much cheaper exhaustive frontier.
- Earlier two-case variant (`case_checks.py`, `lemma_opt.py`, `lemma_opt2.py`):
  dense case 4mR ≥ A sharp at cliques; continuous relaxation w/o graphicality fails
  (degrees (n−1,...,n−1,0,...) — non-graphical), with Erdős–Gallai it saturates at 0.

### IMPORTANT CORRECTION: (★) is FALSE for large n — GM route has finite range

Block-threshold asymptotics (`blocks.py`) found integer counterexamples to (★)
among complete split graphs CS(n,s) = K_s ∨ \bar K_{n−s}: the smallest in that
family is **CS(723, 6)** (g ≈ +6.8e-07; g grows to ≈ +0.0034 as n → ∞ at
s ≈ 0.007n). So the AM–GM lower bound on R is asymptotically insufficient:
(★) is a valid *finite verification tool* (its per-n exhausts give the frontier)
but NOT a proof route for all n. The true objective
Φ (using exact R) remains ≤ 0 on all these graphs — CS graphs satisfy 129
comfortably; it is only the GM relaxation that crosses zero. Any full proof
needs an R lower bound tight for split-like graphs (GM is tight only for
edge-weight-regular graphs).

### Proof skeleton for 129 (gap = step 4; steps 2–3 limited by the correction)
1. R ≥ m·exp(−(1/2m) Σ d ln d)  (AM–GM). ✓
2. For fixed (n, m), g = ln(n²dev²) + (1/m)Σ d ln d is Schur-convex in the degree
   vector (variance and Σ d ln d are Schur-convex; increasing transform + sum). ✓
3. Maximal graphical sequences in the dominance order (fixed sum) are threshold
   sequences (Ruch–Gutman); so it suffices to prove (★) for threshold sequences. ✓(lit)
4. (★) for threshold sequences — machine-verified g ≤ 0 for all 2^(n−1) threshold
   creation sequences n ≤ 28 (`threshold.c`, `threshold_g.out`), but FALSE for
   n ≥ 723 (CS(723,6) is a threshold sequence) — so this skeleton proves 129 only
   up to the first (★)-violating sequence (somewhere in 23 ≤ n₀ ≤ 723 given the
   n ≤ 22 exhaust; every exhausted n below n₀ yields a fully verified frontier).

**Corollary of the (★) exhaust (steps 1 + enum): WoW conjecture 129 is TRUE for
every graph on n ≤ 22 vertices** — pushes the exhaustive frontier from n = 10
(Brewster–Dinneen–Faber 1995) to n = 22 without enumerating graphs (only degree
sequences; ~1.9×10^11 sequences total vs ~10^30 graphs), on top of the direct
geng exhaust n ≤ 12.

## 7. Status

- geng n=12 exhaustive: DONE — all 165,091,172,592 graphs on 12 vertices scanned
  in 8 partitions (`scan12_*.err`); best direct dev−R = 0 and best padded Φ = 0,
  both attained only by the equality family (e.g. K??CCEB_{Fo^ = K_7 ∪ 5K_1);
  NO violation. Direct frontier: all graphs n ≤ 12.
- enum_seq ((★) frontier): DONE for every n ≤ 22 — see §6; frontier n ≤ 22.
- block-threshold asymptotics: DONE — Φ ≤ 0 everywhere (max 0 at equality family);
  (★) fails for CS(n≥723, s≈0.007n) (see correction above)
- `find_n0.py`: over all ≤4-block integer threshold configs, the FIRST (★)
  violation is exactly n = 723, CS(723,6) (searched every n on a grid 20..725 +
  exact step-back); so the GM/Schur verification method is sound for n ≤ 722
  within this class, and 23 ≤ n₀ ≤ 723 overall
- padded hill-climb n = 100, 150, 200 (120k annealed edge flips × 4 restarts):
  DONE — max Φ = 0, reached only from clique seeds (equality family); random
  seeds stay far below (Φ ≈ −60..−80)
- STATUS: frontier-pushed (negative: no counterexample; conjecture 129 verified
  for ALL graphs on n ≤ 22 vertices — up from n ≤ 10 in the literature — via the
  (★) degree-sequence exhaust, plus direct verification of all graphs n ≤ 12,
  all threshold graphs n ≤ 30, block-threshold asymptotics to n = 10^6, and
  annealed searches to n = 200; new exact equality family K_t ∪ (t−2)K_1;
  GM proof route shown to fail first at CS(723,6))

## 8. Second push (per follow-up request): bigger frontier + new tooling

- `enum_seq3.c` + `run_enum.sh`: ~3× faster incremental enumerator (O(1) leaf
  stats, parity pruning, (d1,d2) partitioning), logs every sequence with
  g > −1e-6 (NEAR) for post-hoc certification.
- `lp_fallback.py`: NEW certificate — transportation-LP lower bound R_LP ≤ R(G)
  for every realization of a degree sequence (variables x_{ab} = #edges between
  degree classes, degree-sum equalities + simple-graph caps). If dev² ≤ R_LP²
  the sequence is certified even where (★) fails. Validated: certifies
  CS(723,6) (the (★) counterexample; R_LP ≥ 65.38 > dev = 65.05) and is exactly
  tight on the equality family. This makes the degree-sequence frontier method
  sound PAST n₀ ≤ 723.
- Equality-neighborhood targeted anneal (`hillclimb.py` mode 'eq': seed exactly
  K_{n/2+1} ∪ isolateds at Φ = 0, low-T anneal): n = 100, 200, 300, 500, 800 —
  no uphill move ever found; Φ stays ≤ 0 (extremal family locally rigid).
- `enum_seq3` exhausts of n = 23 and n = 24 (with LP fallback for any NEAR/
  VIOLATION lines): RUNNING — results recorded below when complete.

## 9. Conjecture 698 (definitional investigation + test of intended reading)

As coded in refutationGBR, 698 is vacuous (negative Laplacian eigenvalues don't
exist). Under the plausible intended reading — sqrt(Σ λᵢ² over negative
*adjacency* eigenvalues) ≤ R — (`conj698.py`): geng exhaust n ≤ 8 and annealing
n = 10..36 from star seeds give max(lhs − R) = 0 exactly, with a large equality
family: every complete bipartite K_{a,b} (+isolated vertices) has
negative-eigenvalue norm √(ab) = R. No violation found; 698-adjacency looks
tight-but-true as well.

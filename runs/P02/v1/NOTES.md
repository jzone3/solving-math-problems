# P02 V1 — direct counterexample search / exhaustive sweep

Session: devin-1f64b267fc8b41efa25a6e78cdf59a25 (V1 of 5 parallel runs).
Date: 2026-07-22.

## Source verification (IMPORTANT — paraphrase discrepancy found)

Obtained the original paper: S. Brandt, *A 4-colour problem for dense triangle-free
graphs*, Discrete Math. 251 (2002) 33–46 (via IA Scholar / wayback copy of the
Elsevier open-archive PDF; ScienceDirect itself is captcha-walled).

- **Brandt's actual Conjecture 4.1**: "Every maximal triangle-free graph G ∈ G has a
  regular supergraph G' obtained from G by vertex multiplications", where G is defined
  (Section 1) as the class of triangle-free graphs **with minimum degree EXCEEDING n/3**
  (strict inequality).
- **Brandt's Conjecture 5.1** (stated as an equivalent LP relaxation): "If G is a
  maximal triangle-free graph with d_f(G) < 3 then A(G)x = 1 has a rational solution
  x > 0", where d_f(G) = min{1ᵀx : x ≥ 0, Ax ≥ 1} is the fractional total domination
  number. Brandt proves 5.1 ⇒ 4.1 and (via Conjectures 5.2+5.3 machinery) discusses the
  converse direction; he calls them equivalent formulations of the same phenomenon.
- **West's open-problem page** (dwest.web.illinois.edu/openp/regsup.html) paraphrases
  the hypothesis as minimum degree **"at least n(G)/3"** — this is NOT what Brandt
  conjectured. The problem file problems/P02-brandt-regular-supergraph.md follows
  West's (loosened) phrasing.
- Openness check (July 2026): West's page has no SOLVED marker; searches for the
  conjecture find no resolution. Łuczak–Polcyn–Reiher, *Strong Brandt–Thomassé
  Theorems* (arXiv:2406.10745, 2024) still calls characterising maximal triangle-free
  graphs with δ ≥ n/3 "the well-known question" and poses their Question 5.4 about the
  δ ≥ n/3, Δ > n/3 case — so the boundary zone is genuinely not understood, and the
  conjecture is still treated as open in the ≥ form on West's list.

## Reduction used by the verifier

A vertex multiplication with integer multiplicities x_v ≥ 1 produces a (triangle-free,
supergraph) blow-up in which a copy of v has degree Σ_{u∈N(v)} x_u. So G has a regular
multiplication supergraph iff the integer system {x ≥ 1, Ax = d·1 for some d ∈ Z⁺} is
feasible, iff (by clearing denominators / rescaling) the rational system
{x > 0, Ax = c·1} is feasible. This is decided exactly by the LP

    maximize t  s.t.  Ax = λ·1,  x_v ≥ t,  t ≤ 1,  x, λ, t ≥ 0

(always feasible at 0; optimum > 0 ⟺ multiplication-regularizable). Fast filter with
scipy/HiGHS; every non-clearly-feasible case re-decided with an exact Fraction-based
two-phase simplex (exactlp.py, Bland's rule, no floats).

## Finding 1 — West's "≥ n/3" paraphrase is FALSE, smallest counterexample n = 9

Exhaustive sweep (nauty-geng 2.8.x, `-t -d⌈n/3⌉`, then maximality filter) found that
the statement "maximal triangle-free + δ ≥ n/3 ⇒ regular multiplication supergraph"
already fails at n = 9. Witness (graph6 `H?q`qjo`):

    edges: 8~{0,1,2,3}; 0~{4,5}; 1~{4,7}; 2~{5,6}; 3~{6,7}; 4~6; 5~7
    degrees: eight vertices of degree 3, one (vertex 8) of degree 4; δ = 3 = n/3.

Maximal triangle-free (verified), δ = n/3, and the system Ax = d·1 forces
x4=x6, x5=x7, d=2·x4=2·x5, whence x8 = d − x4 − x5 = 0: infeasible (machine-verified
exactly; also verified by independent hand elimination). So it is a counterexample to
the West-phrased statement.

- This graph has d_f = 3 EXACTLY (exact LP), so it does **not** violate Brandt's real
  Conjecture 5.1 (which requires d_f < 3), consistent with the original conjecture.
- n = 12 gives 5 more such boundary (δ = n/3) counterexamples to the ≥ version.

## Search plan for the ORIGINAL conjecture (the actually-open statement)

Track A (Conjecture 4.1): all maximal triangle-free graphs with δ > n/3 (strict),
escalating n; test the multiplication LP.
Track B (Conjecture 5.1, wider class): ALL maximal triangle-free graphs (no degree
condition) up to the largest reachable n; compute d_f; whenever d_f < 3, test the
multiplication LP. Counterexample criterion: d_f < 3 and LP optimum t = 0.

(Heuristic expectation: Brandt–Thomassé's structure theorem [blow-ups of Andrásfai or
Vega graphs for δ > n/3] plus Brandt–Pisanski's regular blow-ups of Vega graphs suggest
Track A should be empty; Track B at δ ≤ n/3 with d_f < 3 is where anything new must
live.)

## Key structural reduction for the sweep

The multiplication system and d_f are invariant under collapsing to the **core**
(quotient by the similarity relation N(u)=N(v); Brandt Sec. 2): if G is a blow-up of H
with class sizes m, then {x>0 : A_G x = c1} is feasible iff {z>0 : A_H z = c1} is
(class sums z_u = Σ x, and conversely distribute), and d_f(G) = d_f(H) by merging
identical rows. **Consequence: sweeping all maximal TF graphs up to n vertices decides
Conjecture 5.1 — and hence 4.1 — for ALL graphs (of any order) whose core has ≤ n
vertices.** So the frontier below is a statement about cores, which covers infinitely
many graphs.

## Sweep results (MTF generator of Brandt–Brinkmann–Harmuth, caagt.ugent.be/mtf,
## compiled against nauty 2.8.9; processing = process.py, exact recheck = exactlp.py)

| n  | #MTF      | δ≥n/3 | δ>n/3 | ≥-infeasible (West CEs) | TrackA CEs | TrackB (df<3 & infeas) |
|----|-----------|-------|-------|-------------------------|------------|------------------------|
| 4–8| 25        | –     | –     | 0                       | 0          | 0 |
| 9  | 16        | 7     | 1     | **1**                   | 0          | 0 |
| 10 | 31        | 3     | 3     | 0                       | 0          | 0 |
| 11 | 61        | 7     | 7     | 0                       | 0          | 0 |
| 12 | 147       | 26    | 2     | **5**                   | 0          | 0 |
| 13 | 392       | 3     | 3     | 0                       | 0          | 0 |
| 14 | 1274      | 15    | 15    | 0                       | 0          | 0 |
| 15 | 5036      | 64    | 3     | **18**                  | 0          | 0 |
| 16 | 25617     | 7     | 7     | 0                       | 0          | 0 |
| 17 | 127355    | 15    | 15    | 0                       | 0          | 0 |
| 18 | 1337848   | 230   | 4     | **77**                  | 0          | 0 |
| 19 | 13734745  | 9     | 9     | 0                       | 0          | 0 |
| 20 | 178587364 | 75    | 75    | 0                       | 0          | 0 |

- All 101 "≥"-counterexamples (n=9,12,15,18; only at n ≡ 0 mod 3, δ = n/3 exactly)
  were **exactly** re-verified (analyze_boundary.py): maximal TF, δ = n/3,
  multiplication system infeasible over Q, and **d_f = 3 exactly for every one** —
  i.e. they all sit exactly on the LP boundary of Conjecture 5.1 and none violates it.
  Their cores have 9–18 vertices (≈18 distinct cores by WL-key).
- Zero Track A (δ > n/3) failures and zero Track B (d_f < 3) failures anywhere.

## Log

- [x] n = 5..12 geng sweep of δ ≥ ⌈n/3⌉ maximal TF graphs; found Finding 1 (n=9).
- [x] Obtained Brandt 2002 original text; found ≥ vs > paraphrase discrepancy.
- [x] solutions/P02/verify.py: standalone stdlib verifier for the n=9 witness
      (maximality, TF, δ=n/3, exact infeasibility + machine-checked hand elimination,
      exact d_f=3 via primal/dual pair). Prints PASS.
- [x] Full MTF sweep n ≤ 18 (Tracks A+B): no counterexample to the original conjecture.
- [x] n = 19 (13.7M graphs) sweep.
- [x] n = 20: 178,587,364 MTF graphs generated (mtf `file` extension of the N19 set,
      1782 s); sweep completed in 26,316 s (7.3 h) on 8 cores: CLEAN — zero Track A
      failures (75 graphs with δ > n/3, all feasible), zero Track B failures
      (no graph with d_f < 3 and infeasible multiplication system), and zero new
      "≥"-boundary counterexamples (none can exist at n = 20 since 3 ∤ 20).
- [x] vega.py: exact verification that every Andrásfai graph Γ_i (2 ≤ i ≤ 40,
      n ≤ 119) and every Vega graph Υ^{µν}_i (µ,ν ∈ {0,1}, 2 ≤ i ≤ 40, n ≤ 127)
      is maximal triangle-free and admits a positive rational solution of Ax = c·1
      (exact rational simplex; out/vega40.txt).  By the Brandt–Thomassé theorem
      (maximal TF, δ > n/3 ⇒ blow-up of an Andrásfai or Vega graph), this
      machine-verifies Conjecture 4.1 for every graph of ANY order whose core is one
      of these 195 graphs — complementing the exhaustive core sweep (n ≤ 20).

## Compute spent

- MTF generation: n ≤ 19 in 134 s; n = 20 (178.6M graphs, 9.4 GB m2so) in 1782 s.
- Sweep processing (LU fast path + HiGHS LP fallback + exact rational simplex for
  every candidate): n ≤ 18 ≈ 4 min; n = 19 ≈ 37 min; n = 20 ≈ 7.3 h on 8 cores.
- Vega/Andrásfai exact verification (i ≤ 40): ≈ 50 min.
- Total ≈ 9–10 CPU-hours wall, ~60 CPU-core-hours.

## Final verdict

1. West's paraphrase of the conjecture (δ ≥ n/3, as stated in this repo's problem
   file) is FALSE: 101 machine-verified counterexamples at n = 9, 12, 15, 18; the
   smallest (n = 9, graph6 `H?q`qjo`) is independently verified by
   solutions/P02/verify.py (stdlib-only, exact rational arithmetic, prints PASS).
2. Brandt's ORIGINAL Conjecture 4.1 (δ > n/3) and its LP form Conjecture 5.1
   (d_f < 3) survive an exhaustive sweep of ALL 193,832,553 maximal triangle-free
   graphs on n ≤ 20 vertices. By core-invariance this decides the conjecture for
   every graph (of any order) whose similarity-core has ≤ 20 vertices.
3. All 101 "≥"-failures have d_f = 3 exactly: the conjecture fails *precisely* on
   the LP boundary and nowhere inside it, sharpening the picture: the strict
   inequality in Brandt's original statement is essential and optimal.
4. Complementary check: every Andrásfai Γ_i and Vega Υ^{µν}_i core (i ≤ 40,
   n ≤ 127) admits a positive rational solution — consistent with (and via
   Brandt–Thomassé, extending) the sweep for the δ > n/3 class.

STATUS: negative (no counterexample to the original conjecture; frontier-pushed:
exhaustive over all cores with ≤ 20 vertices + Andrásfai/Vega families to i = 40;
plus a machine-verified refutation of the common "δ ≥ n/3" paraphrase at n = 9).

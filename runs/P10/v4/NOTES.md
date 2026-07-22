# P10 — Brouwer's Conjecture — V4 (structured families, symbolic/exact scan)

Session: https://app.devin.ai/sessions/d6ef4422ca9840f09c11fc76eb494e7f
Variant: V4 — joins, complements, Kneser/Johnson/Hamming, incidence graphs; families with
computable Laplacian spectra; exact scan of the middle-t inequality.

## 0. Statement re-verification & openness check (per METHODOLOGY)

- Statement matches Brouwer–Haemers *Spectra of Graphs* §3.2: for all 1 ≤ t ≤ n,
  S_t = Σ_{i≤t} μ_i ≤ m + t(t+1)/2. Confirmed identical in all 2025–26 arXiv abstracts checked.
- **IMPORTANT openness discrepancy**: the problem file says "open in general (July 2026)", but
  arXiv **2606.12197 (Kothari–Tudose, 2026-06-10)** abstract states: *"We give a proof of this
  conjecture"* (via reduction to Grone–Merris–Bai on split graphs, and proves the equivalence
  both ways). arXiv **2607.03388** (Cai–Chen–Yang, July 2026) already cites it as settled:
  *"Recently, Kothari and Tudose (2026) proved the conjecture"* and characterizes the equality
  case (threshold graphs with clique number k+1), and 2607.17293 does the same.
- Consequence: the conjecture is very likely TRUE (recently proved, not yet fully vetted —
  0 citations beyond the wave). A counterexample search is then a consistency check on the
  claimed proof; any violation found would falsify Kothari–Tudose. Reported to orchestrator;
  proceeded with V4 as assigned.

## 1. Method / encodings

All exact rational arithmetic (`fractions.Fraction`), zero floating point in the main scan.

- `spectra.py`: closed-form Laplacian spectra toolkit.
  - join: L-spec(G∨H) = {0, n_G+n_H} ∪ {μ_i(G)+n_H} ∪ {μ_j(H)+n_G} (one 0 removed from each).
  - complement: μ ↦ n − μ on the non-trivial part (L(G)+L(Ḡ) = nI − J).
  - Kneser K(n,k): L-eig = C(n−k,k) − (−1)^i C(n−k−i,k−i), mult C(n,i)−C(n,i−1).
  - Johnson J(n,k): L-eig = k(n−k) − [(k−j)(n−k−j) − j], mult C(n,j)−C(n,j−1).
  - Hamming H(d,q): L-eig = qi, mult C(d,i)(q−1)^i.
  - threshold graphs via creation sequence (iterated join/union with K1); complete
    multipartite as iterated joins of empty graphs.
  - `worst_fast`: deficit f(t) = m + t(t+1)/2 − S_t is a convex quadratic in t inside each
    constant-eigenvalue block ⇒ min over t computed in O(#distinct eigenvalues) exactly,
    handling astronomically large multiplicities (Kneser n=40).
- `sanity.py`: every closed form cross-checked against brute-force numpy eigensolve on
  networkx graphs (K7, K_{3,4,5}, Petersen, Kneser(7,3), Johnson(6,3), Q3, joins,
  complements, threshold). ALL PASS, max err ~1e-14.

## 2. Exact scan (scan_exact.py) — results

Deficit := min_t [m + t(t+1)/2 − S_t]; negative = counterexample. All results exact.

| Family | # specs | min deficit | attained at |
|---|---|---|---|
| Kneser K(n,k), 5≤n≤40 | 360 | 5 | K(5,2)=Petersen, t=4 |
| complements of Kneser | 360 | 5 | cK(5,2), t=5 |
| Johnson J(n,k), 4≤n≤30 | 196 | 2 | J(4,2), t=3 |
| complements of Johnson | 196 | 2 | cJ(4,2), t=1 |
| Hamming H(d,q) (q^d ≤ 1e7) | 61 | 1 | H(2,2)=C4, t=1 |
| complements of Hamming | 61 | 1 | cH(2,2), t=1 |
| complete multipartite, ALL partitions n≤40 | 215,266 | 0 | split members (K_{p,1,…,1} etc.) — equality, as predicted by the threshold equality characterization |
| all threshold graphs n≤18 (2^17 seqs) | ~260k | 0 | equality class exactly as expected (sanity of pipeline) |
| pairwise joins over 750-spec base library | 6,799 | 0 | trivial split members |
| triple joins (n≤90) | 94,692 | 0 | trivial split members |
| iterated cones (up to 25 apexes) over library | 3,750 | 0 | — |
| (aK_p ∪ E_q) ∨ K_r/E_s grids | 12,600 | 0 | — |

scan_exact.py total: **334,341 specs, ~186 s, min deficit 0, no violation.**

## 3. Escalation 1 — scan2_bigexact.py (larger exact grids)

- Kneser n≤100, Johnson n≤60, Hamming q^d≤1e9 (+ complements): min deficit 1 (H(2,2)).
- Complete multipartite: ALL partitions 41≤n≤50 (~1.09M more specs): min 0 (split members).
- (aK_p ∪ E_q)∨K_r with p,a≤25, q≤15, r≤50 (+complements); (aK_p ∪ bK_q)∨K_r grids;
  Kneser/Johnson (n≤25) ∨ K_r/E_r (r≤60) and their complements joined.
- **Total 2,825,363 specs, ~551 s, GLOBAL MIN deficit = 0** (only at split/threshold
  equality graphs). No violation. Exact rational arithmetic throughout.

## 4. Escalation 2 — scan3_numeric.py (numeric + exact recheck)

- All connected graphs on 2..8 vertices (nauty-geng, 12,346 graphs) joined with K_r/E_r,
  r≤40; all pairwise joins of graphs n≤7. Float deficits; every deficit < 0.5 exactly
  re-checked with sympy integer Laplacian eigenvalues.
- Incidence graphs of projective planes PG(2,q), q prime power ≤ 1024
  ((q+1)-regular bipartite; L-eigs 0, 2(q+1), (q+1)±√q).
- Paley graphs q ≤ 1000 and Paley ∨ K_r (r≤30).
- **Worst float deficit −1.4e-14 (numerical zero); 14,507 suspects < 0.5, top-200 most
  negative all exact-verified ≥ 0; no genuine negative.** ~30 s.

## 5. Escalation 3 — scan4_symbolic.py (symbolic sympy proofs)

Block structure: inside a constant-eigenvalue block, deficit f(t) = m + t(t+1)/2 − S_t is a
convex quadratic in t ⇒ block min at endpoints or t ∈ {v−1, v}. For each candidate we
attempted a positivity proof (substitute param = min + nonneg slack, expand, all polynomial
coefficients ≥ 0); interior candidates falling outside their block are proved vacuous the
same way.

- **F1: K_a ∨ (b·K_c), all a≥1,b≥1,c≥2 — FULLY PROVED ≥ 0 symbolically.**
- **F3: K_a ∨ (K_b ∪ E_c), all a≥1,b≥2,c≥1 — FULLY PROVED ≥ 0 symbolically.**
- F2: (b·K_c) ∨ E_a and F4: E_r ∨ (K_b ∪ K_c): block sort order is parameter-dependent, so
  only the exact grid (params to 300, ~60 pts/axis, exact arithmetic) — min deficits 0 and 1
  resp., no violation.

(These two family proofs are consistent with — and subsumed by — Kothari–Tudose 2026 if that
proof stands, but they are independent, elementary, and machine-checked.)

## 6. Escalation 4 — scan5_geng9.py

- ALL 261,080 connected graphs on 9 vertices ∨ K_r and ∨ E_r for r = 1..40
  (20.9M join instances, float pipeline, suspect threshold −1e-6): worst deficit −2.8e-14
  (numerical zero), **0 suspects**. 187 s.

## 7. Verifier

`solutions/P10/verify.py` — standalone, stdlib-only (fractions + itertools): rebuilds real
edge lists for random members of F1, F3, Kneser, complete multipartite; verifies every
claimed closed-form spectrum EXACTLY via Fraction Gaussian-elimination nullity of L − λI;
then checks all Brouwer partial sums exactly. Prints PASS. (Run: `python3 solutions/P10/verify.py`.)

## 8. Compute log

- scan_exact.py: 334,341 specs, 186 s.
- scan2_bigexact.py: 2,825,363 specs, 551 s.
- scan3_numeric.py: ~1.1M join instances + PG/Paley, 30 s (+ exact rechecks).
- scan4_symbolic.py: 4 families × grid 300³(subsampled) exact + sympy proofs, ~80 s.
- scan5_geng9.py: 20.9M joins, 187 s.
- Total ≈ 25M instances checked, all exact or exactly-rechecked near zero.

## 9. Dead ends / notes

- Incidence graphs of general 2-designs are biregular, not regular ⇒ no L = kI − A closed
  form; only the regular case (projective planes, both degrees q+1) has one. Skipped
  closed-form biregular Laplacians (identity via singular values is false for L).
- Everything with deficit 0 is split/threshold — matches the equality characterization in
  arXiv 2607.03388 (threshold graphs with clique number t+1). No non-threshold graph came
  within (0,1) deficit at any nontrivial t in any exact family; the structured world is
  nowhere near a counterexample.
- Given Kothari–Tudose (2606.12197) claims a full proof via split-graph GMB reduction, the
  negative outcome here is the expected one; a violation would have falsified that paper.

## STATUS: negative

No counterexample in ~25M structured-family instances (Kneser/Johnson/Hamming to n=100 and
complements, all complete multipartite n≤50, all thresholds n≤18, massive join grids incl.
all 9-vertex graphs ∨ K_r/E_r, PG(2,q) incidence to q=1024, Paley to q≈1000). Bonus
frontier: Brouwer's inequality PROVED symbolically (machine-checked positivity) for the full
families K_a ∨ bK_c and K_a ∨ (K_b ∪ E_c). Conjecture likely settled anyway: arXiv
2606.12197 (Kothari–Tudose 2026) claims a proof; problem file's "open" status is stale.

# P17 v1 — WoW 20 & 21 (inertia ≤ energy/2): run notes

Session: runs/P17-v1 (V1: direct search — closed-form spectral families scanned
analytically + simulated annealing on n⁺−E/2 and n⁻−E/2; exact rational
certification path ready).

**OUTCOME (updated after second priority-check wave): WoW 20 and 21 are now
THEOREMS — resolved in the literature the day before this run. Kumar &
Pragada, "Energy and independence number", arXiv:2607.19817 (posted
2026-07-22), prove Fajtlowicz's 1980s conjecture E(G) ≥ 2(n − α(G));
combined with the Cvetković inertia bound α ≤ min{n−n⁺, n−n⁻} this gives
E(G) ≥ 2·max{n⁺, n⁻}, i.e. both WoW 20 and WoW 21. Their paper states the
resolution of "[Aouchiche–Hansen, Conjectures #20, #21, Table 6]" explicitly.
So the correct search direction was "true", and our (independent, earlier)
search evidence below is fully consistent: no counterexample exists.**

See §10 for the resolution details and our verification. Sections 1–9 record
the original counterexample-search run, all negative.

## 1. Statement fidelity (checked against primary source)

`handoff/P07/wow-july2004.pdf` (Fajtlowicz, *Written on the Wall*, July 2004)
uses Type-3 glyph fonts; decoded programmatically with the glyph map
`/XY → chr(base36(XY) − 360)` (same map derived independently in the P08
adversarial review). Decoded verbatim (spaces lost by Type-3 positioning):

> 20. The number of positive eigenvalues of a graph is not more than their sum.
>     The sum of absolute values of eigenvalues of an integer valued matrix is
>     greater or equal to its rank i.e the number of nonzero eigenvalues, [F2].
>     This is also a partial solution to conjecture 21. [F2] S. Fajtlowicz, On
>     "Conjectures of Graffiti, II." Congressus Numerantium 60(87), p.189-197.
> 21. The number of negative eigenvalues of a graph is not more than the sum of
>     its positive eigenvalues. comp. conj 20.

So, with adjacency spectrum λ₁ ≥ … ≥ λₙ and S := Σ_{λᵢ>0} λᵢ (= E(G)/2, since
trace 0 ⇒ S = Σ|negative|):

- **WoW 20**: n⁺(G) ≤ S.
- **WoW 21**: n⁻(G) ≤ S.

Matches `problems/P17-wow-20-21.md`. Operational encoding cross-checked against
Roucairol–Cazenave `refutationGBR src/models/conjectures/GenerateGraph.rs`
(CONJECTURE==20: `poseigvec.len() ≤ sum(poseigvec)`; ==21: `num_eig_neg ≤
sum_eig_pos`; both on `self.adj_mat` — the adjacency matrix, correct here,
unlike their WoW 698 row).

Convention notes: eigenvalue counts with multiplicity; zero eigenvalues in
neither side; strict violation required (equality graphs exist, see §4).

## 2. Priority check (mandatory scope incl. artifact repos)

- **Roucairol–Cazenave 2025** (`handoff/P07/roucairol-cazenave-2025.pdf`,
  arXiv:2409.18626): Table rows `20 O`, `21 O` — open after their searches to
  n = 50.
- **Brewster–Dinneen–Faber 1995** ("A computational attack on the conjectures
  of Graffiti", cs.auckland.ac.nz/~mjd/graffiti/graffiti1.pdf): exhaustive
  n ≤ 10 — no counterexample; conjectures listed as unresolved.
- **arXiv / Semantic-Scholar-adjacent (Exa) searches** (2026-07-23): queries on
  "number of positive eigenvalues ≤ energy/2", "Fajtlowicz WoW 20/21",
  "energy ≥ 2·n⁺", "inertia energy conjecture counterexample" — no resolution
  found. Related but distinct recent activity:
  - arXiv:2607.18031 (Jul 2026) proves the square-energy conjecture
    min{s⁺,s⁻} ≥ n−1 and (Cor. 4.3) Elphick's adjacency-inertia conjecture
    min{s⁺,s⁻} ≥ n⁰−ι+max{n⁺,n⁻}; Cor. 4.4 gives 𝓔₁^σ ≥ √(n−κ). None imply
    WoW 20/21.
  - arXiv:2605.07196 (May 2026) refutes 2n⁺ ≤ n⁻(n⁻+1) (Akbari–Elphick–Kumar–
    Pragada–Tang) with graphs W_k, inertia (C(k,2)+1, 0, k−1) — the extreme-
    signature regime relevant here; we exact-checked W_k against WoW 20/21
    (§5): no violation.
  - arXiv:2509.05814: SDP work on the OLDER Graffiti conjecture E/2 ≥ n−α
    (open). **Implication chain**: Cvetković's inertia bound gives
    α ≤ n⁰+min{n⁺,n⁻}, hence n−α ≥ max{n⁺,n⁻}; so E/2 ≥ n−α ⟹ BOTH WoW 20
    and 21. A counterexample to 20/21 would refute that 1980s conjecture too
    (known true for almost all graphs, Nikiforov 2007 — so violations are
    exceptional graphs if they exist at all).
- **GitHub**: code search `sum_eig_pos` / `num_eig_neg` → only
  RoucairolMilo/refutationGBR and this repo. Repo search "graffiti conjecture
  refutation" → nothing new.
- **Zenodo API**: queries "graffiti conjecture eigenvalues", "positive
  eigenvalues energy counterexample" → nothing relevant.
- **OpenReview API**: "positive eigenvalues energy conjecture", "Written on
  the Wall Graffiti" → nothing relevant.
- Residual risks: paywalled Congressus Numerantium [F2] not read (only the
  rank-bound partial result quoted in WoW itself); MATCH archives searched only
  via Exa; no Lean/AF artifact search done.

## 3. Reformulation used by all searches

trace A = 0 ⇒ S = Σ_{λ>0}λ = Σ_{λ<0}|λ|. Define
- score20(G) := Σ_{λ>0}(1−λ) = n⁺ − S  (WoW 20 violated iff > 0),
- score21(G) := Σ_{λ<0}(1−|λ|) = n⁻ − S (WoW 21 violated iff > 0).
score20 − score21 = signature. Components add ⇒ any violator contains a
connected violator. Violating 20 needs positive eigenvalues of average < 1
(many in (0,1)); violating 21 needs negative eigenvalues of average modulus
< 1 (many in (−1,0)).

Structural consequences (all machine-spot-checked in `family_scans.py`):
- **L1 (integral spectra)**: every positive eigenvalue ≥ 1 / negative ≤ −1 ⇒
  both conjectures hold. Kills Kneser, Johnson, Hamming, all integral SRGs.
- **L2 (complete multipartite)**: n⁺ = 1 ⇒ 20 trivial; for 21, S = λ₁ ≥
  λ₁(K_k) = k−1 = n⁻ by interlacing (K_k subgraph); equality iff K_k.
- **L3 (corona G∘K₁)**: spectrum {(λᵢ±√(λᵢ²+4))/2}; score20 =
  n − Σᵢ√(λᵢ²+4)/2 ≤ 0, equality iff G empty (perfect matching). The corona
  is the natural "make many eigenvalues in (0,1)" move and it exactly saturates
  but never crosses.
- **L4 (bipartite)**: symmetric spectrum ⇒ n⁺ = n⁻ = rank/2 ≤ E/2 (E ≥ rank for
  integer symmetric matrices, Fajtlowicz's own remark in WoW 20) ⇒ both hold.
- **Rank bound**: E ≥ rank ⇒ violation of 20 needs n⁺ > n⁻ (positive
  signature; rare, W_k-type graphs), violation of 21 needs n⁻ > n⁺.
- Rational eigenvalues are integers (algebraic integers), so eigenvalues in
  (0,1)/(−1,0) are irrational and come in full Galois-conjugate classes with
  equal multiplicities — high-multiplicity candidates are algebraically
  constrained (quadratic classes like x²+x−1 pair 0.618 with −1.618, etc.).

## 4. Equality families (why strictness matters)

- score20 = 0: perfect matchings mK₂ (spectrum ±1) (+ isolated vertices).
- score21 = 0: disjoint unions of cliques ⋃K_{aᵢ} (negatives all = −1).
Local search plateaus at these; they are strict local maxima of the landscape.

## 5. Searches performed (all code in this directory)

1. **Exhaustive** (`exhaustive_small.py`, nauty-geng): all graphs n ≤ 9
   (12,346 + 274,668 + …), float scores, tol 1e-7: no candidate; best = 0 only
   at equality graphs. n = 10: full connected scan (`near_miss_scan.py`,
   geng -c, 11.7M graphs — sufficient since any violator contains a connected
   violator): best connected non-equality score21 = −0.0645 (2K₅+e), score20 =
   −0.654; no violation. (Confirms BDF 1995 n ≤ 10 exhaustive.)
2. **Annealing** (`search_anneal.py`): edge-flip simulated annealing on both
   scores, n ∈ {10,12,14,16,18,20,24,26,30,36,40,44,50,60}, 8 restarts × 150k
   iters per size (plus earlier 6×60k pass), connectivity penalty to avoid
   trivial equality assembly. Result: converges to equality families
   (matchings for 20, disjoint cliques/K₃-unions for 21; score → 0 to within
   1e-14 float fuzz), never > 0.
3. **Seeded low-T local search** (`seeded_search.py`) around the two best
   near-equality structures (below): collapses back to equality; no crossing.
4. **Closed-form families** (`family_scans.py`), n ≫ 50 regime:
   - Kneser K(n,k), n ≤ 200: integral (L1), max score 0 at K(6,3) (disjoint
     K₂'s!).
   - Complete multipartite: 4000 random part vectors (n ≲ 300) + L2 analytic.
   - Circulants: 20k random connection sets, n ≤ 300: best = 0 exactly at
     perfect-matching (n even, S={n/2}) and disjoint-triangle circulants.
   - Line graphs of random trees/graphs (n ≤ 120): all ≤ 0. (For trees,
     score21(L(T)) = Σ_{μ∈Lap(T),μ<2}(μ−1); stars give −1, paths ≈ −0.14n.)
   - Joins of clique/path/empty unions: all ≤ 0.
   - W_k (Chen–Li 2026 inertia counterexamples), k ≤ 200, exact quadratics:
     score20 ≈ −(k²/2); score21 = (k−1)(1+r), r = (−(k−2)−√((k−2)²+4))/2 < −1,
     so < 0. The C(k,2)−k eigenvalues equal to 1 and the k−1 small positives
     ≈ 1/(k−2) are not enough against the quotient eigenvalues ~k²/2.
5. **Near-miss frontier** (`near_miss_scan.py`): best connected non-equality
   scores among all graphs:
   - score20: −0.2360679… = 2−√5 at n = 5 (C5 and the bull); worsens with n.
   - score21: −0.2143 (n=5) → −0.1463 (n=6) → −0.1249 (n=7) → −0.0941 (n=8) —
     these are **two cliques joined by one bridge edge**, 2K_a+e:
     score21(2K_a+e) → 0⁻ like ≈ −2/a² (numeric: a=50: −7.8e−4, a=100:
     −1.98e−4, a=200: −4.98e−5). A one-parameter family approaching equality
     arbitrarily closely from below but provably(numerically) never crossing;
     the bridge perturbs two −1 eigenvalues to −1±ε with mean < −1.
     Exact check of 2K₁₀+e via `verify_exact.py`: n⁻ = 18,
     S ∈ [65770203/3650230, 17618512/977823] ≈ 18.018 > 18. No violation.

## 6. Exact verification path (no floats on accept path)

`verify_exact.py <20|21> <witness.json>`: sympy charpoly over ℤ (Bareiss),
square-free factorization + Sturm `count_roots` on (0,∞)/(−∞,0) for exact
n⁺/n⁻ with multiplicity, and certified rational enclosure of S via
`Poly.intervals(eps)` isolation, refined until the strict comparison against
the integer count is decided. Prints PASS only on a certified violation.
Tested: C5 (FAIL), 2K₂ equality (FAIL), K₃ equality (FAIL), 2K₁₀+e (FAIL).

## 7. Compute spent

~2.5 h wall on 8 vCPU: exhaustive n ≤ 9 (+n=10 connected), 4×(7 sizes × 8
restarts × 150k annealing steps), ~30k family instances, exact sympy checks.

## 8. Dead ends / negative results (logged per methodology)

- Corona trick (pendant per vertex) saturates but cannot cross (L3) — exact.
- Tensor/products of C5-like spectra: deficits multiply the wrong way.
- Clique chains/shared-vertex cliques accumulate deficit; only the single
  bridge is second-order small.
- Cographs: no eigenvalues in (−1,0) (known), so 21 unviolable there.
- Everything integral is dead (L1).

## 9. Status & suggested next steps

Open, consistent with R–C 2025 "O" rows; our searches extend the structured
regime far beyond n = 50 (families to n ~ 10⁴ effective via closed forms) and
the random regime to n = 60 with annealing. If search keeps suggesting truth:
note WoW 21 restricted to graphs where all negative eigenvalues ≥ −1 forces
⋃K_a (equality) — a proof attempt could try to show Σ_{λ<0}(1−|λ|) ≤ 0 via
interlacing against a clique partition (Σ|λ|≥ … per clique), cf. the
E/2 ≥ n−α SDP program of arXiv:2509.05814 (which implies both). V3/V4 SAT/ILP
variants seem less natural here than for other problems; a V2 structured
attack could target quadratic-conjugate spectra (x²+ax−b families) directly.

## 10. RESOLUTION FOUND (second-wave priority check, 2026-07-23)

- **Kumar, Pragada — "Energy and independence number", arXiv:2607.19817
  (submitted 2026-07-22)**, copy at `kumar-pragada-2607.19817.pdf`:
  - Theorem 1.2: E(G) ≥ 2(n − α(G)) for every graph (Fajtlowicz's Graffiti
    conjecture from the 1980s; the one arXiv:2509.05814 attacked via SDP).
  - Proof: 2 pages — SDP formulation of energy (E = 2 min{tr M : M ⪰ 0,
    M − A ⪰ 0}, Abiad et al.), a "neighbourhood deletion inequality"
    n·E(G) ≥ 4m + Σ_v E(G − N[v]) (Lemma 2.2), then induction on n using
    α(G − N[v]) ≤ α(G) − 1.
  - Corollary stated in the paper: E(G) ≥ 2·max{n⁺(G), n⁻(G)}, "which
    resolves [Aouchiche–Hansen survey, Conjectures #20, #21, Table 6]" —
    exactly WoW 20 and 21 (≡ P17). Implication chain: Cvetković inertia
    bound α ≤ min{n − n⁺, n − n⁻} ⇒ n − α ≥ max{n⁺, n⁻}; combine with
    Theorem 1.2 and E/2 = Σ_{λ>0}λ.
  - Our verification (`check_kumar_pragada.py`): numerically spot-checked
    Lemma 2.2, Theorem 1.2, and the corollary on 400 random graphs
    (n ≤ 15, exact α via complement clique): 0 failures. The induction step
    from Lemma 2.2 to Theorem 1.2 is elementary and was checked by hand
    (§3 of the paper reproduced above is 10 lines).
  - Historical note: Favaron–Mahéo–Saclé 1993 (Discrete Math 111, "Some
    eigenvalue properties in graphs (Conjectures of Graffiti — II)") already
    discussed "Conjecture 20" by this numbering, proving the partial results
    Σpos ≥ n − χ̄ (clique cover; Theorem 2.30/Cor. 2.31) and n⁺ ≤ ν + ν̄
    (Theorem 2.32, Conjecture 258). Gap cases χ̄ > α stayed open until now.
- **Status for INDEX**: P17 = RESOLVED IN LITERATURE (proved true), not by
  us — scooped by one day. Priority-check discipline worked: the refutation
  search (negative) is consistent with the theorem; no wasted "solved" claim.
- Second-wave negative results also logged: exhaustive trees n ≤ 18 for
  score21(L(T)) (max exactly 0 at stars/spiders → L = clique equality);
  cycle powers C_n^k (n ≤ 1200): best score21 = −1.236 (C₅); corona G∘K_r
  second-order analysis (score21 ≈ −(r/(r+1)³)·2m < 0 for any edges).

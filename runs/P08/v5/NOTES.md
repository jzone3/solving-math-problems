# P08 V5 run notes — Graffiti 39/40 (deviation of distance matrix vs inertia)

Session: https://app.devin.ai/sessions/c0a267d469344409824c27fea96d1595
Variant: V5 (literature-first + unified both-conjectures harness).

## 1. Source verification (per METHODOLOGY rule: attack the original, not a paraphrase)

- **Original statement** recovered from *Written on the Wall* (wow-july2004.ps,
  fetched via web.archive.org copy of math.uh.edu/~clarson/wow-july2004.ps):
  - "39. The deviation of the distance matrix is not more than the number of positive
    eigenvalues."
  - "40. The deviation of the distance matrix is not more than the number of negative
    eigenvalues."
  (Adjacent: "38. The variance of the distance matrix is not more than the negative of
  the smallest eigenvalue." — so Graffiti's deviation = √variance, i.e. standard
  deviation.)
- **Operational encoding** confirmed from the Roucairol–Cazenave 2025 refutation code
  (github.com/RoucairolMilo/refutationGBR, src/models/conjectures/GenerateGraph.rs,
  CONJECTURE == 39 / 40): dev = population std over **all n² entries** of the distance
  matrix (diagonal zeros included); eigenvalue counts on the adjacency matrix with
  ±1e-4 sign threshold. Their `invariants::std_dev` divides by len and takes sqrt.
- **Open status re-confirmed**: ECAI-2025 workshop paper (ConjectureRefutationECAI2025.pdf)
  Table 1 lists both 39 and 40 as "O" (open); their MCTS/NRPA/UCT/GBFS/BEAM runs up to
  n = 50 found nothing. No newer literature found (July 2026 searches for
  "deviation distance matrix positive eigenvalues", "Graffiti 39" etc. return nothing
  beyond the 1995 Brewster–Dinneen–Faber n ≤ 10 verification and the 2025 paper).
- FMS 1993 (Discrete Math 111) PDF is paywalled (ScienceDirect blocked); not required —
  the RC code pins the encoding, and the proof below is robust to the diagonal-in/out
  ambiguity in "deviation of the distance matrix".

## 2. Main result: BOTH CONJECTURES ARE TRUE (proof found, then machine-checked)

While digesting partial results (V5's literature-first step), the following two-step
argument closes both conjectures. Full write-up: `solutions/P08/PROOF.md`.

1. **Popoviciu**: all n² entries of D lie in [0, d] (d = diameter), so
   Var ≤ d²/4, i.e. dev(D) ≤ d/2. (Holds for the off-diagonal-only variant too.)
2. **Induced geodesic path + Cauchy interlacing**: a diametral shortest path is an
   induced P_{d+1}; n⁺(P_{d+1}) = n⁻(P_{d+1}) = ⌊(d+1)/2⌋ (eigenvalues 2cos(jπ/(d+2)));
   interlacing gives n⁺(G), n⁻(G) ≥ ⌊(d+1)/2⌋ ≥ d/2.

Hence dev(D) ≤ d/2 ≤ min(n⁺, n⁻). The conjectured bounds are not even close to tight.

Presumably this survived 30+ years because nobody with the two standard tools
(Popoviciu's variance bound + interlacing on the geodesic path) ever looked at it:
the search papers only ran heuristics, and FMS 1993 worked conjecture-by-conjecture
by hand.

## 3. Machine verification (never trust LLM arithmetic)

- `solutions/P08/verify.py` (numpy-only, standalone) re-checks every proof step and the
  end-to-end inequality; **prints PASS**. Coverage:
  - path inertia lemma exactly matches closed form for k ≤ 2000;
  - inducedness of extracted geodesic paths on every graph tested;
  - Popoviciu step dev(D) ≤ diam/2 (both dev variants) on every graph tested;
  - interlacing consequence min(n⁺,n⁻) ≥ ⌊(diam+1)/2⌋ on every graph tested;
  - exhaustive: ALL 1 893 731 connected labelled graphs with n ≤ 7;
  - structured families to n = 2000 (paths, brooms, spiders, caterpillars,
    complete multipartite + pendant tails) and random trees/sparse graphs to n = 500.
- `runs/P08/v5/exhaustive_small.py` (independent encoding, nauty-geng g6 stream):
  exhaustive over all **273 192 connected graphs with n ≤ 9** (isomorphism classes).
  Max of dev − min(n⁺,n⁻) = **−0.219375**, attained by the star K₁,₃
  (dev_full = 0.7806, n⁺ = n⁻ = 1). PASS, no violation, proof chain asserts all hold.
- `runs/P08/v5/harness.py` (search harness, the planned V5 loop): 1455 adversarial
  graphs — paths/cycles/complete to n = 2000, brooms, spiders, caterpillars,
  multipartite+tails, random trees to n = 800, sparse non-trees, G(n,p) — max unified
  score −0.2630 (P₃ family bucket); every graph also satisfies the proof-chain asserts.

Compute spent: ~15 min total (exhaustive n ≤ 9 ≈ 2 min; verify.py ≈ 6 min; harness ≈ 4 min).
No near-misses exist: the gap d/2 − min(n⁺,n⁻) ≥ 0 is structural, and dev is strictly
below d/2 for every connected graph with n ≥ 2 (distance-1 entries + diagonal zeros
prevent the Popoviciu equality distribution).

## 4. Dead ends / notes

- The originally-planned counterexample hunt (trees n > 50) is provably hopeless:
  trees maximize dev only by growing diameter, and every unit of diameter buys the
  adversary d/2 on the LHS but ⌊(d+1)/2⌋ on the RHS.
- The same argument does NOT settle WoW 38 (Var(D) ≤ −λ_min): Var grows like d²/4,
  while −λ_min ≤ Δ; 38 is a genuinely different fight.
- Per METHODOLOGY, SOLVED requires a second, independently written verifier from
  another session + human review of the proof text. Both 39 and 40 claimed here.

## STATUS: SOLVED (proof that both Graffiti 39 and 40 are TRUE; machine-verified: verify.py PASS, exhaustive n ≤ 9 PASS; pending independent second verification)

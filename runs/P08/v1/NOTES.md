# P08 V1 run notes — Graffiti 39/40 (dev(D) vs n⁺ / n⁻)

Session: V1 (direct counterexample search: tree exhaust + annealing).
Branch: `runs/P08-v1`. Date: 2026-07-22.

## 1. Source verification (before deep work)

- **Original statement recovered verbatim** from Fajtlowicz's *Written on the Wall*
  (wow-july2004.pdf, independencenumber.wordpress.com mirror). The PDF uses Type-3 fonts with
  no ToUnicode map; decoded by reverse-engineering the glyph-name substitution
  (a=CP, b=CQ, …, A=BT, …, digits BC=0…BL=9). Decoded text:
  - *39. The deviation of the distance matrix is not more than the number of positive eigenvalues.*
  - *40. The deviation of the distance matrix is not more than the number of negative eigenvalues.*
  (Adjacent: *38. The variance of the distance matrix is not more than the negative of the
  smallest eigenvalue* — different conjecture, not attacked here.)
- **Operative encoding** (Roucairol–Cazenave 2025, `refutationGBR`,
  `src/models/conjectures/GenerateGraph.rs` CONJECTURE==39/40): dev = population std over all
  n² entries of the distance matrix (diagonal included); n⁺/n⁻ = # adjacency eigenvalues
  > 1e-4 / < −1e-4. Confirmed by reading their Rust source directly.
- **Openness re-confirmed**: RC ECAI-2025 Table 1 lists 39 and 40 as "O" (open), searched to
  size 50 on "any & tree" with 8 search algorithms, no counterexample. Exa searches for
  2025–2026 work on "Graffiti 39/40 deviation distance matrix" found no resolution.
- WoW never defines "deviation" at the conjecture; A–H survey / RC use std over n² entries.
  All plausible conventions (std or MAD; with or without diagonal; ordered pairs or unordered)
  are handled by the proof below (each is ≤ diam/2).

## 2. Main outcome: BOTH CONJECTURES ARE TRUE — elementary proof

While building the V1 scorer I noticed the score dev − n⁺ is bounded away from 0 by a
diameter argument, which turns into a complete proof (see `solutions/P08/PROOF.md`):

1. **Popoviciu**: all n² entries of D lie in [0, d] (d = diameter) ⇒ dev(D) ≤ d/2.
2. **Geodesic is induced**: G contains an induced path P_{d+1}.
3. **Path inertia**: n⁺(P_{d+1}) = n⁻(P_{d+1}) = ⌊(d+1)/2⌋.
4. **Cauchy interlacing**: inertia counts are monotone under induced subgraphs ⇒
   n⁺(G), n⁻(G) ≥ ⌊(d+1)/2⌋ ≥ d/2.

Chain: dev(D) ≤ d/2 ≤ ⌊(d+1)/2⌋ ≤ min(n⁺, n⁻). Corner case d=0 (K₁): 0 ≤ 0. ∎

This explains why 30+ years of search (exhaustive n≤10 in 1995, 8 MCTS/greedy algorithms to
n=50 in 2025) found nothing: the score dev − min(n⁺,n⁻) is ≤ −(⌊(d+1)/2⌋ − d/2) ≤ 0 always,
and empirically ≤ −0.22.

Machine verification: `solutions/P08/verify.py` (numpy only) — exhaustive over ALL connected
graphs on ≤ 6 vertices (27 475 graphs, generated internally, no nauty), 300 random trees
n ≤ 400, 300 random connected graphs n ≤ 120, plus exact-rational inertia (Sylvester/LDLᵀ
congruence over `Fraction`) cross-checked against the float eigensolver on all n ≤ 5 graphs
and 100 random n ≤ 12 graphs. All three inequalities (a) dev ≤ d/2, (b) ⌊(d+1)/2⌋ ≤ min(n⁺,n⁻),
(c) dev ≤ min(n⁺,n⁻) hold everywhere. **Prints PASS** (runtime ≈ 2m10s).

## 3. V1 search work actually performed (confirmatory)

Code in this directory: `harness.py` (BFS distances + eigensolve invariants),
`exhaust.py` (graph6 stream checker), `anneal_tree.py` (tree annealing; uses the identity
n⁺ = n⁻ = matching number μ for trees — validated against networkx matching + eigensolve on
200 random trees), `anneal_graph.py` (edge-toggle annealing on connected graphs).

| Search | Range | Count | Best score (dev − n⁺ = dev − n⁻) | Result |
|---|---|---|---|---|
| geng exhaustive, connected | n = 5–9 | 273 183 | −0.224 (n=5) → −0.316 (n=9), extremal = stars K_{1,n−1} + edge-ish | negative |
| gentreeg exhaustive trees | n = 4–20 | ~1.6M | −0.482 (n=19), −0.493 (n=20), extremal = spider-like | negative |
| Tree annealing (score dev − μ) | n = 50/100/200, 3 seeds each, 4000 iters | — | −4.19 (n=50), −13.3 (n=100), −42.6 (n=200) | negative, margin grows with n |
| Tree annealing large | n = 500 (1500 it), n = 1000 (600 it) | — | −150.2 (n=500), −350.2 (n=1000) | negative, margin ≈ −0.35n |
| General-graph annealing (score dev − min(n⁺,n⁻)) | n = 30/60/100, 2 seeds, 3000 iters | — | −7.9 (n=30), −15.8 (n=60), −25.9 (n=100); annealer converges to near-paths | negative |
| Proof-chain lemma check | every graph above | ~1.9M | 0 lemma failures | consistent with proof |

Near-miss structure: the max of dev − n⁺ over all graphs seems to be ≈ −0.22, attained at K_{1,4}
(dev = 0.776, n⁺ = 1); as n grows every family loses ground (annealing margins scale linearly
in n on trees, and paths — dev ≈ 0.236n vs n⁺ = ⌊n/2⌋ — lose ≈ 0.264n). The n > 50 tree regime
flagged in the problem file is provably empty: for trees n⁺ = n⁻ = μ ≥ ⌈d/2⌉ ≥ dev(D) directly.

## 4. Dead ends / notes

- FMS 1993 (Discrete Math 111) PDF is paywalled (ScienceDirect block page); statement was
  instead verified against WoW itself (primary source) + RC encoding. If FMS already contains
  this argument the result is a rediscovery, but RC 2025 and the problem file list 39/40 as
  open, and no literature search hit shows a proof.
- Eigenvalue-count tolerance (RC use 1e-4) is irrelevant to the mathematical statement; the
  exact-rational inertia check in verify.py removes any floating-point doubt on small cases.
- Compute spent: ~40 min exhaustive streams, ~35 min annealing, 2m verify.py, single box.

## STATUS: SOLVED (both conjectures proved TRUE; elementary proof, machine-verified lemmas; needs the methodology's second independent verifier + a human check that FMS 1993 didn't already prove it)

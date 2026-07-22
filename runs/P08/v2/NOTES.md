# P08 / V2 — parameterized near-paths (structured construction) — run notes

Session: Devin ultra V2 run, 2026-07-22.

## Source re-verification (before deep work)

- Retrieved Fajtlowicz's original "Written on the Wall" (wow-july2004.ps via web
  archive of math.uh.edu/~clarson). Verbatim: "39. The deviation of the distance
  matrix is not more than the number of positive eigenvalues." "40. … number of
  negative eigenvalues." No inline definition of "deviation" in WoW; conjecture 38
  uses "variance" separately, conjecture 27 says "standard deviation" explicitly.
- FMS 1993 (Discrete Math 111, 197–220), the paper that worked this family, is
  paywalled (Elsevier, not OA anywhere per OpenAlex) — could not extract their
  formal deviation definition. Operational definition taken from the
  Roucairol–Cazenave 2025 code (refutationGBR/GenerateGraph.rs, CONJECTURE==39/40):
  dev = population std-dev over ALL n² distance-matrix entries (diagonal included);
  n± counted with |λ|>1e-4 threshold. Confirmed both rows marked "O" (open) in the
  RC ECAI-2025 paper Table 1. No 2025–26 resolution found in literature search.
- The result below is robust to every plausible reading of "deviation"
  (population/sample SD, MAD, diagonal in or out) — see solutions/P08/PROOF.md.

## Main outcome: PROOF that both conjectures are TRUE

While setting up the V2 family scan I noticed the two-step bound and it checks out:

1. (Popoviciu) all n² entries of D lie in [0, d] (d = diameter) ⇒ dev(D) ≤ d/2,
   strict for n ≥ 3 (equality only for K_2, where the chain still holds).
2. A geodesic realizing the diameter is an INDUCED P_{d+1}; Cauchy interlacing makes
   n⁺ and n⁻ monotone under induced subgraphs; n±(P_{d+1}) = ⌊(d+1)/2⌋ = ⌈d/2⌉.
   ⇒ min(n⁺(G), n⁻(G)) ≥ ⌈d/2⌉.

Chain: dev(D) ≤ d/2 ≤ ⌈d/2⌉ ≤ min(n⁺, n⁻). Both conjectures hold for every
connected graph, every n. Full writeup: solutions/P08/PROOF.md.
Machine verification: solutions/P08/verify.py (numpy only) — checks path inertia
m ≤ 600 vs closed form, interlacing monotonicity (200 random induced-subgraph
trials), and the full chain with the dev ≤ d/2 comparison in EXACT integer
arithmetic on: all 27,475 labeled connected graphs n ≤ 6, structured families,
60 seeded random connected graphs n ≤ 300. Prints PASS (~12 s).

## V2 family search (run anyway, as assigned — doubles as numeric confirmation)

Encodings: exact integer BFS distance sums (S1, S2 ⇒ dev), dense eigvalsh for n±;
for trees n⁺ = n⁻ = matching number (rank(A) = 2μ for forests), computed by exact
leaf-stripping and asserted equal to the eigensolve for every n ≤ 1200 instance.

- `families.py` — generators: brooms, double brooms, caterpillars (periodic legs,
  leg patterns), spiders/subdivided stars, complete multipartite + pendant path,
  kites/lollipops. `evaluate()` returns dev, n±, diam + exact variance fraction.
- `sweep.py` (output: sweep_output_n200.txt): 1305 instances, n ≤ 200, all families,
  score = dev − min(n⁺,n⁻). Best score −0.219 (tiny stars); best ratio 0.78.
  Proof-chain violations: 0.
- `escalate.py` (output: escalate_output_n20000.txt): pushes n to 20,000 in the
  promising direction. Balanced double brooms (handle h, b pendant leaves each end)
  are the extremal family: ratio dev/min(n⁺,n⁻) climbs monotonically with h and b/h:
  0.775 (h=100,b=100) → 0.964 (h=100,b=5000) → **0.96493 (h=800,b=8000, n=16800)**.
  Minimum gap min(n⁺,n⁻) − dev observed: +1.52 (dbroom h=10,b=500). Never ≤ 0,
  exactly as the proof requires — asymptotically sharp, never crossing.
  Caterpillars ratio ≈ 0.236, spiders ≤ 0.32, all far from 1.

Near-miss analysis (why the conjecture survived MCTS): dbroom(h,b→∞) has half the
vertex pairs at distance ~2 and half at ~h+1, so dev → (h−1)/2 while
n⁺ = n⁻ = μ = ⌈h/2⌉+1; the ratio → 1 but the gap stays ≥ ~1.5. No finite instance
wins — consistent with (and explained by) the proof.

Compute spent: ~5 min total family sweeps (1305 + 43 instances, max n = 20,000,
eigensolves to n = 1200, exact tree matching beyond) + verifier runs. Cheap: the
proof removed the need for the planned multi-hour annealing escalation.

## Dead ends / notes

- ScienceDirect (FMS 1993 + A–H survey) blocked by Cloudflare; GERAD PDF 404. Used
  WoW original text (primary source) + RC code as the operational statement instead.
- V2's premise ("hunt spectrally degenerate long-diameter families") is provably
  futile: spectral degeneracy cannot push min(n⁺,n⁻) below ⌈diam/2⌉ (interlacing),
  while dev can never exceed diam/2 (Popoviciu). This closes V1/V3/V4/V5 too.

## STATUS: SOLVED — both conjectures PROVED TRUE (proof + machine-verified chain; no counterexample exists at any n).

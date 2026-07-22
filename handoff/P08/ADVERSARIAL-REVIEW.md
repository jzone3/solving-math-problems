# Adversarial review + priority check — P08 (Graffiti 39/40 proof)

**STATUS: CONFIRMED** — every step of `solutions/P08/PROOF.md` is mathematically correct and the
statement matches both the original WoW 39/40 and the Roucairol–Cazenave 2025 encoding.
**Novelty verdict: (b)** — the composite result is an *easy corollary of known lemmas that nobody
had connected*: the hard half, diam(G) ≤ 2·min(n⁺, n⁻), is already published (Geng–Wu–Wang 2020,
who call it "a simple result"; sharpened by Xu–Zhen–Wong 2023). No published resolution of
Graffiti 39/40 themselves was found — RC (ECAI 2025) still list both as open.

Reviewer: independent session (branch `runs/P08-adversarial`). Verifier written from scratch
(`adv_verify.py`, no code shared with `solutions/P08/verify.py`); full log in `adv_verify.log`.

---

## 1. Step-by-step attack (all steps survive)

### Step 1 — Popoviciu
- Popoviciu (1935) is for **population** variance of a finite multiset in [a,b]: Var ≤ (b−a)²/4.
  Applied to the n² entries (diagonal included) of D, all in [0, d]: correct.
- Off-diagonal-only and unordered-pair conventions: entries lie in [1, d] ⊂ [0, d], so the same
  bound holds (in fact ≤ (d−1)/2). Mean absolute deviation ≤ std, also covered. Verified exactly
  (rational arithmetic) on every connected graph n ≤ 6 and geng n = 7.
- **Real convention edge found (not a flaw in the claimed statement):** if "deviation" were the
  *sample* std (denominator N−1), the intermediate bound dev ≤ d/2 FAILS at K₂
  (sample std over the 4 entries = 1/√3 ≈ 0.577 > 0.5). The end-to-end inequality
  dev_sample ≤ min(n⁺,n⁻) still held on every graph tested (exhaustive n ≤ 7 + randoms), but the
  written proof does not cover the sample convention. Irrelevant in practice: Graffiti/RC use the
  population std (confirmed from RC's Rust source, see §2).

### Step 2 — shortest path is induced
Correct: a chord x_i x_j with |i−j| ≥ 2 shortcuts the geodesic. Verified computationally: for
every graph swept, an explicitly constructed diametral geodesic was checked chord-free.

### Step 3 — inertia of paths, including zero-eigenvalue edge case
Eigenvalues of P_k are 2cos(jπ/(k+1)). For k odd, j = (k+1)/2 gives eigenvalue 0 (this is the
d even case, k = d+1 odd); the count n⁺ = n⁻ = ⌊k/2⌋ correctly excludes it. Verified by
**exact integer characteristic polynomials** (own Faddeev–LeVerrier + Descartes' rule, exact since
all roots real) for k ≤ 40 and by floats against the closed form for k ≤ 2000. No failures.

### Step 4 — Cauchy interlacing direction
For an m×m principal submatrix B of an n×n symmetric A: λ_i(A) ≥ λ_i(B) ≥ λ_{i+n−m}(A).
λ_p(B) > 0 ⇒ λ_p(A) > 0 gives n⁺(A) ≥ n⁺(B); the mirrored inequality gives n⁻(A) ≥ n⁻(B).
Direction used in the proof is the correct one. Also verified exhaustively (chain (b) below).

### Integer inequality d/2 ≤ ⌊(d+1)/2⌋
d even: equality. d odd: (d+1)/2 > d/2. Trivially correct; slack is zero for even d, so Step 1
must genuinely deliver d/2 (it does, for population conventions).

### Corner cases
- K₁: d = 0, dev = 0 = n⁺ = n⁻; holds with equality (0 ≤ 0). Steps 2–4 unused, as the proof notes.
- K₂: d = 1, dev = 1/2 ≤ 1 = min(n⁺,n⁻). Fine.
- Disconnected graphs: distance undefined; both WoW (distance-based invariants) and RC (connected
  generators) restrict to connected graphs, matching the proved statement.
- The proof's remark "max dev − min(n⁺,n⁻) = −0.2194 at K₁,₃ (dev = 0.7806)" re-verified
  independently (K₁,₃: 0.78060 − 1; K₁,₄ gives −0.2244; K₁,₃ is the max).

## 2. Independent machine verification (written from scratch)

`adv_verify.py` — own graph6 parser, own BFS APSP, exact `Fraction` variances, exact integer
inertia (Faddeev–LeVerrier charpoly + Descartes' sign rule), cross-checked against a float
eigensolver. Checks, per graph: (a) Popoviciu dev ≤ d/2 for all population conventions + MAD;
(b) min(n⁺,n⁻) ≥ ⌊(d+1)/2⌋; (c) end-to-end dev ≤ min(n⁺,n⁻) for NINE conventions
(n²/off-diag/pairs × pop/sample std, plus 3 MADs); (d) diametral geodesic is induced.

| Sweep | Count | Arithmetic | Result |
|---|---|---|---|
| ALL connected labeled graphs n ≤ 6 | 27,476 | exact variance; exact inertia n ≤ 5, float n = 6 | PASS |
| nauty-geng connected n = 7 | 853 | exact inertia + exact variance | PASS |
| Path inertia P_k | k ≤ 40 exact, k ≤ 2000 float | exact/float | PASS |
| Random trees + G(n,p), n ≤ 60 | 400 | exact inertia for n ≤ 12 | PASS |

Min margin min(n⁺,n⁻) − dev over all n ≥ 2 graphs seen: **0.2194** (star-like), matching the
proof's tightness remark; the only equality case is K₁ (0 = 0). Full log: `adv_verify.log`.

## 3. Statement fidelity

- **WoW original, decoded independently.** wow-july2004.pdf (independencenumber.wordpress.com
  mirror) uses Type-3 glyph names; I derived the mapping analytically (glyph `/XY` =
  chr(base36(XY) − 360), consistent with a=CP, A=BT, 0=BC) — an independent decode, agreeing with
  the v1 run's reverse-engineering. Decoded verbatim:
  - *39. The deviation of the distance matrix is not more than the number of positive eigenvalues.*
  - *40. The deviation of the distance matrix is not more than the number of negative eigenvalues.*
  Unlike neighbors 37 ("Proved in [FA2]") and 41 ("Disproved by Shui-Tain Chen"), **39/40 carry no
  resolution annotation** in WoW (July 2004). WoW never defines "deviation" at these conjectures.
- **RC 2025 encoding, read from their Rust source** (github.com/RoucairolMilo/refutationGBR,
  `src/models/conjectures/GenerateGraph.rs`, blocks `CONJECTURE == 39/40` +
  `invariants.rs::std_dev`): population std over all n² entries of the BFS distance matrix,
  diagonal included; eigenvalues counted with tolerance ±1e-4; refutation threshold
  dev − count > 1e-5. Exactly the statement proved. Their ECAI-2025 Table 1 lists 39 and 40 as
  "O" (open), searched to size 50 on "any & tree".
- **Convention gaps and coverage:** diagonal in/out, ordered/unordered pairs, MAD — all covered by
  the proof. Sample-vs-population std — NOT covered by the written proof (see §1 Step 1), though
  the conjecture itself survives empirically under it. Float tolerance 1e-4 — immaterial (exact
  inertia used here on small cases). Connectivity — both sources restrict to connected graphs.

## 4. Priority search

- **The spectral lemma is classical/known.**
  - Xianya Geng, Yan Wu, Long Wang, *Characterizations of graphs with given inertia index
    achieving the maximum diameter*, Linear & Multilinear Algebra **68**(8) (2020) 1633–1641,
    doi:10.1080/03081087.2018.1552656. Abstract: "A simple result shows that d(G) ≤ 2p(G) and
    d(G) ≤ 2n(G) … we determine … when each of the equalities holds." This is exactly
    Steps 2–4's conclusion, for BOTH n⁺ and n⁻.
  - Songnian Xu, Wenhao Zhen, Dein Wong, arXiv:2312.02680 (2023): sharpen to 2n⁻(G) ≥ d+1 for
    odd d (= n⁻ ≥ ⌊(d+1)/2⌋), by the identical proof (their Lemma 2.8: diametral path +
    n(P_{2k+2}) = k+1 + interlacing). Cites Geng et al. for the base bound.
  - The ingredients (path inertia ⌊k/2⌋; inertia monotone under induced subgraphs via interlacing)
    are textbook (e.g. Cvetković–Doob–Sachs; Haemers' interlacing survey). The route via "number
    of distinct eigenvalues ≥ d+1" does NOT give the inertia bound; the induced-path route is the
    standard one and is what the literature uses.
- **dev(D) ≤ diam/2**: no published statement found in this exact form; it is a one-line
  application of Popoviciu and unlikely to be quotable prior art on its own.
- **Graffiti 39/40 resolution**: no publication found. Checked: Brewster–Dinneen–Faber 1995
  (refuted 40+ Graffiti conjectures by exhaustive n ≤ 10; 39/40 not among those treated),
  RC 2025 (open, searched to n = 50), Aouchiche–Hansen distance-spectra survey 2014 (no mention),
  Exa/arXiv/Semantic Scholar searches for any 39/40 proof (nothing). Favaron–Mahéo–Saclé,
  Discrete Math. 111 (1993) remains paywalled and could not be read directly — residual risk —
  but RC 2025, who read FMS closely enough to source their invariant definitions from it and to
  audit refutation provenance, classify 39/40 as open; and WoW 2004 (11 years post-FMS) carries
  no resolution note on 39/40 while annotating neighbors. Confident these are unresolved in FMS.

### Honest conclusion on novelty
The proof is **correct** and the *resolution of Graffiti 39/40 appears to be new* — but it is
**(b) an easy corollary of known lemmas nobody connected**: d ≤ 2·min(n⁺,n⁻) is published
(Geng–Wu–Wang 2020) and described there as "a simple result"; the only new content is the
one-line Popoviciu observation dev(D) ≤ d/2 and noticing the two combine. Any public write-up
should cite Geng–Wu–Wang 2020 (and Xu–Zhen–Wong 2023) for the spectral half rather than present
Steps 2–4 as new, and should scope "deviation" to the population conventions.

## 5. Minor errata noticed (non-fatal)

- `runs/P08/v1/NOTES.md` §3 says the extremal near-miss is K₁,₄ (−0.224 at n = 5); the global max
  over n ≤ 9 is K₁,₃ (−0.2194) as PROOF.md states. Both figures re-verified; NOTES' number is the
  n = 5 slice, so this is a phrasing nit only.
- PROOF.md's robustness parenthetical (Step 1) should explicitly exclude the sample-std reading,
  where dev ≤ d/2 is false at K₂ (see §1).

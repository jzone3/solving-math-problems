# P08 V3 (spectral design) — run notes

Session: https://app.devin.ai/sessions/367e42c28fb34f739207a2c9eacafb94
Branch: `runs/P08-v3` (off `devin/1784749757-context-plan`)

## 0. Source & statement re-verification (before deep work)

- Original source: Favaron–Mahéo–Saclé, *Some eigenvalue properties in graphs
  (Conjectures of Graffiti — II)*, Discrete Math. 111 (1993) 197–220.
  ScienceDirect PDF is paywalled/bot-blocked; the "Written on the Wall" July
  2004 PDF (independencenumber.wordpress.com) has CID-mangled fonts and is
  unreadable by text extraction.
- **Authoritative operationalization** taken instead from the paper that
  classifies the conjectures as open: Roucairol–Cazenave, *Refutation of
  Spectral Graph Theory Conjectures with Search Algorithms* (ECAI 2025;
  also arXiv:2409.18626). Their code is public:
  `RoucairolMilo/refutationGBR`, `src/models/conjectures/GenerateGraph.rs`
  blocks `CONJECTURE == 39` / `== 40` and `invariants.rs::std_dev`:
  - dev(D) = **population** std-dev over **all n² entries** of the distance
    matrix (diagonal zeros included);
  - n⁺ = #{adjacency eigenvalues > 1e-4}, n⁻ = #{< −1e-4};
  - conj 39 refuted iff dev − n⁺ > 1e-5; conj 40 iff dev − n⁻ > 1e-5.
- **Openness confirmed as of the ECAI 2025 paper**: Table 1 rows `39 O` and
  `40 O` (size 50, graph type "any & tree"); no algorithm refuted either.
  Quick literature check (Exa search, July 2026) found no later refutation or
  proof; RC's erratum section flags definitional problems for 140/290/322 but
  none for 39/40.
- **Original wording recovered** by OCR of the "Written on the Wall" July-2004
  PDF (tesseract at 150 dpi; text layer is CID-mangled). Page ~23:
  "39. The deviation of the distance matrix is not more than the number of
  positive eigenvalues. 40. The deviation of the distance matrix is not more
  than the number of negative eigenvalues." — no proof/refutation comment
  attached (unlike neighbours 35–37, 41–42), consistent with open status.
  Excerpt saved to `wow-ocr-conj-24-46-excerpt.txt`.
- **Definitional robustness of "deviation"**: WoW conj. 38 says "variance"
  explicitly, so "deviation" (39/40) ≠ variance. Whether deviation means the
  population/sample standard deviation (RC's operationalization) or the mean
  absolute deviation (Graffiti's usage elsewhere), all of these are ≤ (max−min)/2
  = diam/2 for data in [0, diam] (MAD ≤ stddev ≤ d/2 by Popoviciu), so the proof
  covers every plausible reading. (A variance reading would have been refuted by
  any path P_n, n ≳ 10, in 1988 — impossible for a conjecture that survived MCTS
  searches to n = 50.) Full-text FMS 1993 remained inaccessible (ScienceDirect
  Cloudflare captcha, Wayback only has the challenge page; unpaywall: closed).
- Problem-file nit: it says "complete multipartite has n⁺ = k−1"; actually
  n⁺ = 1 and n⁻ = k−1 (Smith 1970: exactly one positive adjacency eigenvalue
  ⟺ complete multipartite + isolated vertices). Doesn't change the V3 plan.

## 1. Encodings / harness

- `core.py`: dev(D) (population, all n² entries), inertia via
  `numpy.linalg.eigvalsh` (tol 1e-6), margins m39 = dev−n⁺, m40 = dev−n⁻
  (positive margin = counterexample).
- Sanity families: paths P_n have dev ≈ 0.2357·n (empirically → n/(3√2)) while
  n⁺ = n⁻ = ⌊n/2⌋, so m39/m40 → −∞ linearly. Cycles worse.

## 2. V3 spectral design — what was searched

`sweep_spectral_design.py` (492 designed graphs, n up to 1000):
- complete multipartite cores K_{p×k} (k∈{2,3,4,6}, part sizes 1–20, also
  unbalanced [1,1,50],[2,2,100],[1,99],…) with 0–2 pendant tails of length
  up to 80;
- double brooms (path 5–80, end-bundles 0–30), spiders (3–30 legs × 2–40),
  paths & random trees to n=1000, random G(n,p) n≤100.
Result: **no positive margin anywhere**; best (largest) margin over the whole
design space is −0.293 (C₄ = K_{2,2}); attaching any tail raises n⁺/n⁻ at
least as fast as dev. Exhaustive nauty-geng sweeps (`exhaustive_geng.py`):

| n | #connected | worst m39 = worst m40 |
|---|---|---|
| 4 | 6 | −0.2194 |
| 5 | 21 | −0.2244 |
| 6 | 112 | −0.2444 |
| 7 | 853 | −0.2687 |
| 8 | 11 117 | −0.2936 |
| 9 | 261 080 | −0.3162 |
| 10 | 11 716 571 | −0.3295 |

Worst margins get MORE negative with n — the conjectures are not tight
anywhere except at tiny complete-multipartite-like graphs.

## 3. Why the trade-off can never be won → PROOF that 39 & 40 are TRUE

The V3 balancing act (small inertia core + long tails) revealed the reason no
search can succeed, and it converts into a 4-line proof
(`solutions/P08/PROOF.md`):

1. **Popoviciu**: entries of D lie in [0, d] (d = diameter), so
   dev(D) ≤ d/2.
2. A diameter geodesic is an **induced** P_{d+1} (shortest ⇒ no chords).
3. **Path inertia**: n⁺(P_{d+1}) = n⁻(P_{d+1}) = ⌊(d+1)/2⌋ ≥ d/2.
4. **Cauchy interlacing** (inertia monotone under induced subgraphs):
   n⁺(G), n⁻(G) ≥ ⌊(d+1)/2⌋ ≥ d/2.

Hence dev(D) ≤ d/2 ≤ min(n⁺, n⁻), strict for n ≥ 2. Robust to definitional
variants of dev (off-diagonal-only, pairs-only, sample normalization) since
those only shrink the range/bound or are absorbed by the strict slack.

## 4. Verification

- `solutions/P08/verify.py` — standalone, numpy+stdlib only. Machine-checks
  each lemma (path inertia to k=400, interlacing inertia monotonicity on 300
  random principal submatrices, geodesic-is-induced on 200 random graphs) and
  the final inequality + full chain on 27 476 exhaustive labeled connected
  graphs (n ≤ 6), 49 spectral-design graphs to n = 1000, and 152 random
  graphs/trees to n = 500. **Prints PASS** (~8 s).
- `exhaustive_geng.py` re-checks conjectures + chain over all connected
  graphs n ≤ 10 (11.99M graphs total) with an independent BFS/g6 code path —
  zero violations of the conjectures or of any proof step.
- `exact_crosscheck.py`: exact rational dev² vs exact root counts of the
  integer characteristic polynomial (sympy real-root isolation) on the
  worst-margin graphs and samples — agrees with the float pipeline, so no
  tolerance artifacts.
- Per methodology, SOLVED status still wants a second independently written
  verifier from another session.

## 5. Compute spent

~15 min harness sweeps + ~5 min geng n≤9 + ~2.5 h geng n=10 (11.7M graphs).
No SAT/annealing needed — the analytic bound closed the problem.

## 6. Dead ends / near-misses

- No near-misses exist in the usual sense: the margin is bounded away from 0
  (worst −0.219 at K_{1,3}, n=4) and decays as sizes grow.
- ScienceDirect + WoW PDFs unreadable (paywall / CID fonts) — definition
  authenticated via the RC reference implementation instead.

## STATUS: SOLVED (proved TRUE — both conjectures; no counterexample exists)

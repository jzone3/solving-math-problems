# P08 — Graffiti 39/40 — V4 (asymptotic analysis) run notes

Session: https://app.devin.ai/sessions/9ad07c31e13a4f059b95fccb734a449e
Date: 2026-07-22. Variant V4: derive growth rates of dev(D) vs n⁺/n⁻ on candidate
families; find a crossover instance if any family wins asymptotically.

## 1. Source re-verification (per METHODOLOGY)

- Located the ORIGINAL statement in Fajtlowicz, "Written on the Wall" (July 2004 PDF,
  bundled in RoucairolMilo/refutation-COCOON2022 as `wow-july2004.pdf`). The PDF has
  broken CID font maps (pdftotext/pdfminer output garbage), so pages were OCR'd with
  tesseract (page 24 of 216):
  - "38. The variance of the distance matrix is not more than the negative of the
    smallest eigenvalue."
  - "39. The deviation of the distance matrix is not more than the number of positive
    eigenvalues."
  - "40. The deviation of the distance matrix is not more than the number of negative
    eigenvalues."
  WoW's global convention (intro): "eigenvalues" = adjacency-matrix eigenvalues unless
  stated otherwise (cf. conj. 30 which says "positive distance eigenvalues" explicitly).
- Operational definition of "deviation": std of all n² entries of D, exactly as
  implemented for conjectures 39/40 in Roucairol–Cazenave's own search code
  (RoucairolMilo/refutationGBR, `src/models/conjectures/GenerateGraph.rs`, CONJECTURE==39/40
  branches: vecDist over all (i,j) incl. diagonal; std_dev; count of adjacency eigenvalues
  >1e-5 / <-1e-5). Their arXiv:2409.18626 Table 1 lists 39 and 40 as **O (open)**.
- Consistency check on the definition: under it, P₁₀ refutes conj. 38
  (var = 5.61 > 1.92 = −λ_min) — consistent with 38 being refuted historically while
  39/40 survived exhaustive n ≤ 10 (Brewster–Dinneen–Faber 1995) and MCTS n ≤ 50 (RC).
  A "distance-eigenvalue" reading of 39 would be refuted by any longish path at tiny n
  (trees have exactly one positive distance eigenvalue), contradicting "open" — so the
  adjacency reading is the right one.
- Literature check (Exa + arXiv, July 2026): no paper proving or refuting Graffiti 39/40
  found; latest status remains the open rows in Roucairol–Cazenave.
- Could not access Favaron–Mahéo–Saclé, Discrete Math. 111 (1993) full text (ScienceDirect
  captcha-blocked, core.ac.uk 403/404); not needed — original WoW statement + RC's
  operational encoding suffice.

## 2. V4 asymptotic analysis → outcome: the conjectures are TRUE (proof found)

Growth-rate ledger for high-deviation candidate families (`families.py`, machine-checked):

| family                | dev(D)   | n⁺  | n⁻  | diam | dev − min(n⁺,n⁻) |
|-----------------------|----------|-----|-----|------|-------------------|
| path n=1000           | 235.70   | 500 | 500 | 999  | −264.30 |
| broom h=b=500 (n=1000)| 155.50   | 250 | 250 | 500  | −94.50  |
| spider k=3 L=300      | 143.63   | 450 | 450 | 600  | −306.37 |
| caterpillar s=300 l=1 | 70.72    | 300 | 300 | 301  | −229.28 |
| K₂ₓ₅₀ + P₃₀₀          | 84.07    | 151 | 151 | 302  | −66.93  |

Every family loses, and the gap → −∞. Chasing why: dev(D) is bounded by half the range of
the entries, i.e. dev ≤ diam/2 (Popoviciu's variance inequality, exact). Meanwhile any
graph of diameter d contains its diametral geodesic as an *induced* P_{d+1}, and inertia is
monotone under induced subgraphs (Cauchy interlacing), so n⁺, n⁻ ≥ n±(P_{d+1}) = ⌈d/2⌉.
Chain:

    dev(D) ≤ d/2 ≤ ⌈d/2⌉ ≤ min(n⁺, n⁻).

That proves BOTH conjectures for every connected graph — no crossover instance can exist
at any n. The asymptotic race is structurally rigged: the same parameter (diameter) that
drives dev up forces at least ⌈d/2⌉ positive and ⌈d/2⌉ negative adjacency eigenvalues.
Full write-up: `solutions/P08/PROOF.md`.

Why it plausibly survived 30+ years: attention went to search (n ≤ 10 exhaustive, n ≤ 50
MCTS) and to the harder neighbors (38 is false; 30 involves distance eigenvalues); the
half-range bound on "dev" trivializes 39/40 once the interlacing observation is made.
The bound is extremely slack (best family, brooms, reaches dev ≈ 0.62·(d/2)), which also
explains why heuristic search never came close and why the "unsearched n > 50 tree regime"
was a mirage.

## 3. Verification

`solutions/P08/verify.py` (standalone, numpy-only; uses nauty geng if present, otherwise a
built-in exhaustive enumerator for n ≤ 7):

- **C1 (Lemma 1) exact:** 4·Var(entries of D) ≤ d², in rational arithmetic (Fractions).
- **C2 (Lemma 2):** n⁺, n⁻ ≥ ⌈d/2⌉ with tolerance 1e-8 in the safe (under-counting)
  direction.
- **C3 (conjectures):** 4·Var ≤ (2n⁺)² and ≤ (2n⁻)² (exact rational vs integer counts).

Corpus: ALL connected graphs n ≤ 8 (counts matched OEIS A001349: 1,1,2,6,21,112,853,11117),
760 random connected graphs up to n = 120 across densities, and the structured families up
to n = 1000. Result: **PASS** on all 12,879 graphs, no violation of any step.

Compute spent: seconds (the run is a proof-check, not a search). Per METHODOLOGY, a second
independently-written verifier from another session is still wanted before marking the
problem SOLVED in INDEX.md.

## 4. Dead ends / notes for the orchestrator

- WoW pdf needs OCR; don't trust pdftotext on it.
- ScienceDirect and core.ac.uk are bot-blocked from this box; FMS 1993 remains unread.
  If someone can pull it: check whether their partial results already contain Lemma 1/2
  (they proved several neighboring conjectures; if they had this argument they'd have
  closed 39/40, so presumably their "dev" work centered on conj. 27/38).
- The result also kills the other P08 variants (V1–V3, V5): no witness exists.

## STATUS: SOLVED (proof, both conjectures TRUE; pending independent re-verification per METHODOLOGY)

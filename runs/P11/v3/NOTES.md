# P11 V3 — Algebraic construction / composition-theorem attack

Session: https://app.devin.ai/sessions/6832b5364f1e481489c60297f71541ef
Branch: runs/P11-v3

## Problem statement re-verification (2026-07-22)

- Source of truth: github.com/dmgordo/circulant-weighing-matrices `cwm.json` (fetched from master).
  NOTE: the repository indexes cells as CW(n, s) where the weight is k = s².
  Our six target cells map to keys: CW(96,6), CW(105,6), CW(112,6), CW(117,6), CW(120,7), CW(132,9).
- All six confirmed `"status": "Open"` in the fetched cwm.json. Statement in problems/P11 matches
  the repository definition (ternary first row, all nontrivial periodic autocorrelations 0, weight k).
- Witness format in DB: `sets: [[P, N]]` = positions of +1 and −1 in Z_n.

## Verifier

`solutions/P11/verify.py` — standalone stdlib-only checker (weight + all n−1 PACF values = 0),
prints PASS. Written before any search.

## Plan (V3 framing)

1. Extract full known existence table from cwm.json (all Yes/All cells with their witness sets).
2. Implement classical composition closure: (a) CW(n,k) ⇒ CW(mn,k) (padding); (b) coprime product
   CW(n1,k1)×CW(n2,k2) ⇒ CW(n1n2,k1k2). Confirm none of the six open cells is reachable (sanity —
   expected, else they wouldn't be open).
3. Generalized group-ring product search: for known witness polynomials f, g (from DB sets),
   consider a(x) = f(x^u)·g(x^v) mod (x^n − 1) in Z[x]/(x^n−1) for the target n, over all u, v;
   accept if resulting coefficient vector is ternary of weight k with zero PACF. This strictly
   generalizes the coprime product theorem (allows overlapping supports / non-coprime maps).
4. Known algebraic families as base material: CW(q²+q+1, q²) for prime powers q (q=2..9),
   CW((q^d−1)/(q−1), q^{d−1}) GMW-type, circulant Hadamard CW(4,4), negacyclic doublings from DB.
5. Near-cell parameter exploration + LLM-guided identity search if 3 is exhausted.

## Log

### 2026-07-22 — statement verification: CRITICAL convention discovered

- Fetched cwm.json (master). Keys are CW(n, s), weight k = s². Six targets = CW(96,6),
  CW(105,6), CW(112,6), CW(117,6), CW(120,7), CW(132,9); all `"Open"` in the DB.
- **The DB statuses refer to PROPER CWMs** (not paddings B(x^d) of smaller CWMs). Proof by
  machine check: DB has CW(21,4)="No" (Eades–Hain) yet padding the DB's own CW(7,4) witness
  {P=[1,2,4],N=[0]} by x→x³ gives a ternary vector on Z_21 with weight 4 and all 20 PACF
  values 0 (verified two ways: direct PACF and numpy W·Wᵀ=4I). So "No"/"Open" cells can admit
  improper CWMs; the table is about proper ones. verify.py updated with an is_proper check.
- Corollary: an IMPROPER CW(96,36) exists trivially — pad the Schmidt–Smith CW(48,36)
  (DB set for CW(48,6)) by x→x². Verified (PACF + numpy). Saved as solutions/P11/CW96_36.json
  with "proper": false. It does NOT settle the DB cell. Also (21,4)-style closure audit
  (runs/P11/v3/closure.py) found 73 DB-"Open" cells and hundreds of DB-"No" cells reachable by
  padding/Kronecker closure — all consistent once statuses are read as proper-CWM statuses.
- Cross-check vs Arasu–Gordon–Zhang (arXiv:1908.08447, downloaded, runs/P11/v3/agz.txt):
  Table 10 "Remaining Open Cases (n≤200,k≤100)" = 22 cells; it CONTAINS (105,36), (112,36),
  (117,36), (120,49) but NOT (96,36) and NOT (132,81).
  - (96,36): absent because a (plain) CW(96,36) exists; the DB Open is for a proper one.
  - (132,81): AGZ **Proposition 4.2 proves no CW(132,81) exists at all** (via ICW_3(44,81)
    multiplier/orbit argument). Yet DB v1.3 (Apr 2026) lists CW(132,9) as Open — tension:
    either the proposition was later retracted/corrected or the DB entry is stale. Flag; treat
    the cell as open per the DB, but nonexistence may already be known.

### Composition-route exhaustion (the core V3 question)

Ops: padding (excluded — never proper) and coprime Kronecker CW(n1,k1)⊗CW(n2,k2) ⇒
CW(n1n2,k1k2), plus general subgroup-product h = F·G in Z[x]/(x^n−1) with F, G embedded CWMs
from divisor cells (h·h* = k1k2 automatically; only ternarity is at issue). Weight
factorizations of 36 into ≥2 square factors: 4·9. For 49: none (49·1 only). For 81: 81·1 only
(9·9 needs two CW(d,9), d|132: none divide 132).
- n=105 (div 3,5,7,15,21,35): CW(d,4) exists only d∈{7,21(improper),35(improper)};
  CW(d,9): none (13,24,26 ∤ 105). 4·9 route DEAD.
- n=112 (div 4,7,8,14,16,28,56): CW(d,4) plentiful; CW(d,9): none divide 112. DEAD.
- n=117 (div 3,9,13,39): CW(13,9) EXISTS, but CW(d,4) with d|117: none (117 odd, 7∤117). DEAD.
- n=120, k=49: CW(d,49) for d|120: none (57,87,114,171 ∤ 120). DEAD.
- n=96, k=36: CW(d,9),(d,4) with d|96: CW(48? no—k=9 needs 13|d or 24|d): CW(24,9) EXISTS,
  CW(4,4)/CW(8,4)... but 24 and 4 not coprime; coprime split 96=3·32: CW(3,·) none; subgroup
  product F·G with F from CW(24,9)⊂Z_96, G from CW(d,4)⊂Z_96 has h·h*=36 but supports overlap
  (24 and d not coprime) → ternarity not automatic; SEARCHABLE (see below).
- n=132, k=81: no route.
Conclusion: classical composition routes into all six cells are exhausted-NEGATIVE, except a
non-coprime subgroup-product search inside Z_96 (and Z_112 4·9? no CW(d,9) — only Z_96), which
we run next.

Machine runs:
- runs/P11/v3/product_search.py: all divisor-embedded products F·G (h·h* = k1k2 identity),
  every DB witness pair, every embedding: 1472 products for (96,36) via 4·9, ZERO ternary hits;
  all other five cells have empty factor material. NEGATIVE.
- runs/P11/v3/block96.py: exhaustive "sum of four weight-9 CWM blocks" ansatz for CW(96,36)
  (every weight-9 CWM on Z_96 is an embedded CW(24,9); 64 sign/residue patterns passing the
  mod-4 spectral test × all multipliers/shifts, ~4.5×10⁸ candidates, FFT-flatness filter +
  exact recheck): ZERO hits. A CW(96,36) is NOT a sum of four weight-9 CWMs. NEGATIVE
  (structural), see block96.log.

### 2026-07-22 — BREAKTHROUGH on CW(96,36): settled YES by Schmidt–Smith 2013

Literature re-check paid off: Schmidt & Smith, "Circulant weighing matrices whose order and
weight are products of powers of 2 and 3", JCTA 120 (2013) (runs/P11/v3/ss.txt, fetched from
Bernhard Schmidt's page):
- **Corollary 6.9: proper CW(v,36) exist for ALL v ≡ 0 (mod 48)** — in particular v = 96.
  The DB cell CW(96,6)="Open" is simply an un-applied published result.
- Implemented Theorem 6.7/6.8 explicitly on Z_96 (runs/P11/v3/ss96.py; γ=6 order 16, α=32
  order 3): brute-forced all (i,c,d) ∈ {1,2}×Z_96×Z_96; 4992 members of the family are valid
  CW(96,36), 4800 of them PROPER. Witness saved: solutions/P11/CW96_36_proper.json —
  verified by BOTH verify.py (PACF + properness) and the independently-written verify2.py
  (full W·Wᵀ = 36I matrix product + properness). PASS/PASS.
  (Bug caught on the way: Python Counter.__add__ silently drops negative coefficients —
  first implementation produced weight-6 "B"; fixed with an explicit add().)
- **Theorem 6.10 settles SIX more DB-Open cells (all v,k products of 2- and 3-powers):**
  proper CW(v,k) with v,k both 2^a3^b requires k ∈ {4,9,36}; k=36 requires an order-16
  element (16 | v). Hence DB-Open cells (288,81), (384,81), (576,81), (768,81), (864,81)
  [k=81 ∉ {4,9,36}] and (648,36) [16 ∤ 648] are all NONEXISTENT (proper). DB corrections.


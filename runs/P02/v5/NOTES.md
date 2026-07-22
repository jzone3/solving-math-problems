# P02 V5 — literature-first attack on Brandt's regular-supergraph conjecture

Session: V5 of 5 parallel runs. Date: 2026-07-22.

## STATUS line (see bottom): SOLVED (counterexample, subject to source-wording caveat)

## 1. Statement re-verification (against cited sources)

- Fetched West's page (dwest.web.illinois.edu/openp/regsup.html) directly. Exact wording:
  "If G is a maximal triangle-free graph and has minimum degree at least n(G)/3, then G has a
  regular supergraph obtainable by vertex multiplications [B]." — i.e. **δ ≥ n/3, boundary
  included**, and the object is a **supergraph** (so every multiplicity x_v ≥ 1).
- Openness re-check (July 2026): West's page still lists it with no partial results; searches
  (Exa) for any resolution / computational attack found nothing. The closest recent work,
  "Strong Brandt–Thomassé Theorems" (arXiv:2406.10745), strengthens the δ > n/3 structure
  theorem but does not touch the regular-supergraph question or the boundary.
- **Caveat**: Brandt's original paper (Discrete Math. 251 (2002) 33–46, Conjecture presumably
  3.8) is paywalled (ScienceDirect/zbMATH behind Cloudflare; no OA copy via
  OpenAlex/CORE/Semantic Scholar/Wayback of Brandt's homepage). I could NOT verify whether
  Brandt wrote "≥ n/3" or "> n/3". Brandt–Thomassé (Corollary 4.3(1)) say Conjecture 3.8 of
  [Brandt 2002] is "every maximal triangle-free graph with min degree **> n/3** has a regular
  weight function", which they prove. If Brandt's original is strict, the surviving open
  content is exactly the boundary version curated by West — which is what we refute below.

## 2. Literature digestion (V5 core)

Brandt–Thomassé ("Dense triangle-free graphs are four-colorable", Thomassé's site) prove:
every maximal triangle-free **twin-free weighted** graph with weighted min degree δ > 1/3 is
one of the Andrásfai graphs Γ_i (3-chromatic) or a Vega graph (4-chromatic), and (Theorem 3 +
uniqueness remark) each admits a **regular weight function with all weights positive and
rational**.

Consequence (folklore-level argument, written out here): if G is maximal triangle-free with
δ(G) > n/3, collapse twin classes to get a weighted twin-free graph with δ > 1/3; it is a Γ_i
or Vega graph H; take its positive rational regular weight ω; scale by a large integer M so
that M·ω_v is an integer ≥ (size of the twin class of v) for all v; distributing these
multiplicities over each twin class gives integers x_u ≥ 1 on V(G) with Σ_{u∈N(v)} x_u
constant — i.e. a regular triangle-free supergraph of G by vertex multiplications.
**So the δ > n/3 case of the conjecture is TRUE (implied by Brandt–Thomassé).**
The genuinely open residual class is δ = n/3 exactly (n ≡ 0 mod 3).

## 3. Key reformulation

G has a regular supergraph by vertex multiplications  ⟺  ∃ integers x_v ≥ 1, d with
Σ_{u∈N(v)} x_u = d ∀v  ⟺  the **rational** LP {x_v ≥ 1, A x = c·1} is feasible
(scale a rational solution by the lcm of denominators; conversely trivial).
So no sweep over d is needed: one exact LP per graph decides everything, and rational
infeasibility is certified by an integer Farkas vector y with
  Σ_v y_v = 0,  yᵀA ≥ 0,  yᵀA ≠ 0
(then 0 = d·Σy = yᵀAx = Σ_v (yᵀA)_v x_v ≥ 1, contradiction).

## 4. Computation

Pipeline (`search.py`): `nauty-geng -q -t -d⌈n/3⌉ n` → maximality filter (triangle-free +
diameter ≤ 2) → exact Phase-1 simplex over `fractions.Fraction` (Bland's rule). Every feasible
graph gets an integer witness (x, d), machine-verified on the spot; every infeasible graph is
re-checked by scipy/HiGHS LP (independent solver) and by sympy `linsolve` structure, and gets
an exact integer Farkas certificate (`certs.py` → `counterexamples.json`).

Results (boundary cases δ = n/3):

| n  | δ | geng output | maximal TF | infeasible (counterexamples) |
|----|---|------------|-----------|------------------------------|
| 9  | 3 | 23         | 7         | **1** (`H?q``qjo`)           |
| 12 | 4 | 292        | 26        | **5**                        |
| 15 | 5 | 5962       | 64        | **18**                       |
| 18 | 6 | 2438356    | 230       | **77**                       |

Consistency checks (strict δ > n/3 — must all be feasible by Brandt–Thomassé + §2):

| n  | δ | maximal TF | infeasible |
|----|---|-----------|-----------|
| 10 | 4 | 3         | 0 ✓ |
| 11 | 4 | 7         | 0 ✓ |
| 13 | 5 | 3         | 0 ✓ |
| 14 | 5 | 15        | 0 ✓ |
| 16 | 6 | 7         | 0 ✓ |
| 17 | 6 | 31        | 0 ✓ |

The strict-case zeros are a strong end-to-end falsification test of the whole pipeline.

Full small sweep n = 3..8 with δ ≥ ⌈n/3⌉ (12 maximal TF graphs total): all feasible —
so **n = 9 is the smallest counterexample**, and G0 is the unique one at n = 9.

## 5. The counterexample (smallest possible)

G0 = graph6 `H?q\`qjo`, n = 9, degrees (3,3,3,3,3,3,3,3,4), δ = 3 = n/3, triangle-free,
maximal (diameter 2). Edges:
(0,4)(0,5)(0,8)(1,4)(1,7)(1,8)(2,5)(2,6)(2,8)(3,6)(3,7)(3,8)(4,6)(5,7).
Any rational x ≥ 0 with Ax = c·1 forces x_8 = 0 (sympy: solution space is
x = (t, c/2−t, c/2−t, t, c/2, c/2, c/2, c/2, 0)), so no supergraph witness exists.
Integer certificate y = (0,1,1,0,−1,−1,−1,−1,2): Σy = 0, yᵀA = 2·e_8.
n = 9 is the smallest possible: all boundary cases are n ∈ {9,12,15,...} and the 6 other
n = 9 maximal TF graphs with δ = 3 are feasible; n < 9 boundary means n ∈ {3,6}, where
δ ≥ n/3 forces strict cases or trivial graphs (and geng sweeps found nothing).

Verifier: `solutions/P02/verify.py` — standalone stdlib-only script; checks triangle-freeness,
maximality, δ ≥ n/3, the Farkas certificate arithmetic, plus a brute-force sanity sweep over
all x ∈ {1..4}^9; prints PASS.

All 24 counterexamples found (n ≤ 15) with their integer certificates are in
`runs/P02/v5/counterexamples.json`; feasible witnesses in `witnesses_n*_d*.jsonl`.

## 5b. Infinite family

G0 is twin-free. Its blow-ups G0(t) (each vertex → t twins) remain maximal triangle-free with
δ = n/3 (n = 9t), and infeasibility lifts: any solution on G0(t) aggregates (class sums
X_v ≥ t ≥ 1) to a solution on G0. So {G0(t)}_{t≥1} is an **infinite family of
counterexamples**, one for each n ≡ 0 (mod 9). Machine-checked for t = 1..4 (n up to 36) in
`blowup_family.py` (exact rational LP). The same certificate y lifts (assign y_v/t to each
copy).

## 5c. Structural observation

For every counterexample found, the certificate support (vertices forced to multiplicity 0 in
any nonnegative solution) consists solely of vertices of degree **strictly above** δ = n/3
(e.g. the degree-4 vertex of G0). Heuristic picture: at the boundary the regular weighting of
the underlying Andrásfai/Vega-like frame is so rigid that "extra" high-degree vertices must
carry weight 0, which a supergraph cannot afford. This suggests the "right" fix of the
conjecture is either strict inequality (then it is Brandt–Thomassé's theorem) or allowing
multiplicities x_v ≥ 0 ("G is homomorphic to a regular triangle-free graph obtained by
multiplications of an induced subgraph").

## 6. Interpretation, near-misses, dead ends

- Dead end: obtaining Brandt 2002 full text (ScienceDirect, zbMATH, CORE, OpenAlex, CiteSeerX,
  Wayback of TU Ilmenau homepage all failed — Cloudflare or no OA copy). This leaves the
  ≥ vs > wording of Brandt's own Conjecture 3.8 unconfirmed; West's curated statement (≥) is
  refuted unconditionally.
- The mechanism of failure at the boundary is exactly the phenomenon Brandt–Thomassé mention
  for weighted graphs: optimal regular weight functions can have **zero** weights. At δ = n/3
  a vertex can be forced to weight 0, which is fine for a "regular weight function" but fatal
  for a **supergraph** (needs weight ≥ 1). G0 is the smallest graph where this bites.
- If the community reading of the conjecture is the strict inequality, then the conjecture is
  simply TRUE via Brandt–Thomassé (§2) and the West page should be updated; either way the
  problem as listed is resolved.
- Compute spent: minutes for n ≤ 16 (exact rational LP per graph is fast; MTF graphs with
  δ ≥ n/3 are very rare); n = 18 took ~3.5 h wall-clock (geng enumeration of 2,438,356
  candidates is the bottleneck). Boundary counterexample counts grow: 1/7 (n=9), 5/26 (n=12),
  18/64 (n=15), 77/230 (n=18) — failure at the boundary is the norm, not an accident.

## STATUS: SOLVED (counterexample to the conjecture as stated on West's open-problems page;
smallest witness n=9, machine-verified with exact Farkas certificate; caveat: Brandt's
original 2002 wording (≥ vs >) unverified due to paywall — under the strict reading the
statement is instead a theorem via Brandt–Thomassé, so the listed problem is resolved in
either reading.)

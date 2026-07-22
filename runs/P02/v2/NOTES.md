# P02 V2 — boundary-focused (δ = n/3 tight cases) — run notes

Session: https://app.devin.ai/sessions/4c8647eedcf24d03b3b7a300491fb7a0
Variant: V2 (structured / boundary-focused: δ = n/3 equality, n divisible by 3;
Andrásfai/Vega blow-up structure at equality).

## Statement verification (2026-07-22)

Fetched https://dwest.web.illinois.edu/openp/regsup.html (curl, plain-text dump).
Statement on West's page matches problems/P02-brandt-regular-supergraph.md verbatim in
substance: G maximal triangle-free (MTF), δ(G) ≥ n/3 ⇒ G has a regular supergraph
obtainable by vertex multiplications. "Comments/Partial results" section on the page is
EMPTY — no recorded progress; problem still listed open. Reference: Brandt,
Discrete Math. 251 (2002) 33–46.

## Key reformulation (machine-checkable)

Vertex multiplication of a triangle-free graph is triangle-free (a triangle in the blow-up
projects to a triangle in G, since the three vertices lie in three distinct classes that are
pairwise adjacent in G). So the conjecture for a given G is exactly:

  ∃ integers x_v ≥ 1 and d with  Σ_{u∈N(v)} x_u = d  for all v,   i.e.  A x = d·1, x ≥ 1.

Scaling: if a RATIONAL x > 0 with A x = d·1 exists, an integer solution exists (clear
denominators). Conversely integer ⇒ rational. So per-graph feasibility is a single LP:

  variables x_v ≥ 1 (rational), d free;  A x − d·1 = 0.

A counterexample = MTF graph with δ ≥ n/3 whose LP is infeasible (certified by an exact
Farkas certificate y with yᵀA ≤ -1 componentwise... see verify script if found).

Twin reduction: if G = H[w] is a multiplication of a twin-free core H, then G's system is
feasible iff H's is (fold weights). So it suffices to test twin-free MTF graphs; any
counterexample yields a twin-free one. We therefore filter to twin-free representatives
but must keep the δ ≥ n/3 condition on G itself — note a twin-free core of a boundary
graph may itself violate δ ≥ n/3, so we test ALL enumerated graphs (twin filtering used
only as a dedup/heuristic lens, not to discard).

## Plan (V2)

1. Enumerate MTF graphs with δ(G) = n/3 exactly, n = 3k (k = 2,3,4,...) via
   nauty-geng -t -d{k}, filter maximality (every non-adjacent pair has a common neighbor)
   and δ == k. LP-check each (float screen, exact re-check of any infeasible candidate).
2. Structure study at equality: which Andrásfai/Vega multiplications achieve δ = n/3
   exactly; hunt failures among weighted blow-ups of Andrásfai/Vega/other MTF cores at
   the boundary.
3. Progressive escalation of n while compute lasts.

## Source verification details

- West's page (regsup.html): "minimum degree at least n(G)/3" — INCLUDES boundary δ = n/3.
- Brandt–Thomassé "Dense triangle-free graphs are four-colorable" (vega11.pdf from
  Thomassé's page): their Corollary 4.3(1) proves "Every maximal triangle-free graph with
  minimum degree > n/3 has a regular weight function ω" — this was Brandt's
  Conjecture 3.8 in [DM 251 (2002)], with STRICT inequality, and weights allowed to be 0
  ("A weighted graph can have different optimal weight functions and vertices of weight 0").
  For twin-free 4-chromatic "good" graphs (δ > 1/3) they additionally note the optimal
  regular weight function has all weights non-zero; 3-colorable strict cases are Γ_i
  (Andrásfai) blowups, which trivially admit positive regular weightings.
- Hence the genuinely open residual of West's ≥-version is exactly the boundary δ = n/3
  (n ≡ 0 mod 3) — precisely V2's assigned zone.
- Could not access Brandt DM 251 (2002) itself (ScienceDirect bot-wall/captcha; no OA copy
  found via OpenAlex/CORE/Exa). Conjecture 3.8's wording is taken from Brandt–Thomassé's
  attribution, which states it with strict >.

## MAIN FINDING (candidate counterexample to West's ≥-statement, at the boundary)

W = graph6 `H?q`qjo`, n = 9, degrees (3,3,3,3,3,3,3,3,4), δ = 3 = n/3, verified maximal
triangle-free, χ(W) = 3 (n < 11 so triangle-free ⇒ χ ≤ 3; non-bipartite: contains C5).

Adjacency (vertex: neighbors):
0: 4 5 8 | 1: 4 7 8 | 2: 5 6 8 | 3: 6 7 8 | 4: 0 1 6 | 5: 0 2 7 | 6: 2 3 4 | 7: 1 3 5 | 8: 0 1 2 3

Exact linear algebra over Q: the solution space of A x = d·1 is 2-dimensional and every
solution has x_8 = 0. Certificate y = (0,1,1,0,−1,−1,−1,−1,2)/2 satisfies yᵀA = e_8ᵀ and
yᵀ1 = 0, so x_8 = yᵀ(Ax) = d·(yᵀ1) = 0 for any solution. Hence no x ≥ 1 exists: W has NO
regular supergraph obtained by vertex multiplications. Verified by
solutions/P02/verify.py (stdlib-only, exact integers, prints PASS).

Weak-reading robustness: even allowing empty classes (x ≥ 0, asking only that some
regular multiplication CONTAIN W as a subgraph), every solution has x_8 = 0, so a regular
blowup is a blowup of W−8; any copy of W inside a blowup of W−8 projects to a graph
homomorphism W → W−8, and exhaustive backtracking shows NO homomorphism W → W−8 exists.
So W fails the conjecture under the weak reading too.

Caveat (paraphrase risk, per METHODOLOGY): Brandt's own Conjecture 3.8 was for strict
δ > n/3 (per Brandt–Thomassé) and is proved there; the ≥-version is West's page's
formulation. W is a counterexample to the statement AS POSTED ON WEST'S PAGE (and as
curated in problems/P02), i.e. it shows the boundary case δ = n/3 of the regular
supergraph statement is FALSE. Whether West intends "at least" literally is the only
residual interpretation question; the problem file explicitly targets the boundary.

## Exhaustive boundary sweep (nauty-geng -t -d⌈n/3⌉, filter MTF + δ≥n/3, LP screen
## via scipy/HiGHS, every flagged instance re-verified EXACTLY over Q — see exact_check.py)

| n  | geng graphs read | MTF with δ≥n/3 | infeasible (exact) |
|----|------------------|----------------|--------------------|
| 6  | 6                | 3              | 0 |
| 7  | 1                | 1              | 0 |
| 8  | 8                | 4              | 0 |
| 9  | 23               | 7              | **1** (W) |
| 10 | 8                | 3              | 0 |
| 11 | 24               | 7              | 0 |
| 12 | 292              | 26             | **5** |
| 13 | 21               | 3              | 0 |
| 14 | 346              | 15             | 0 |
| 15 | 5962             | 64             | **18** |
| 16 | 584              | 7              | 0 |
| 17 | 14143            | 31             | 0 |
| 18 | (running, 8-way parallel) | — | ≥36 candidates so far |

All infeasible instances occur exactly at n ≡ 0 (mod 3) with δ = n/3 (boundary) —
fully consistent with the strict case δ > n/3 being true (Brandt–Thomassé + positivity
argument via twin-free cores Γ_i / Vega, both of which admit positive regular weights).

All 24 candidates at n ≤ 15 re-verified infeasible with exact rational arithmetic
(exact_check.py: nullspace of [A|−1] + Fourier–Motzkin over the ≤8-dim solution space);
most exhibit forced-zero coordinates with explicit certificates y (yᵀA = e_v, yᵀ1 = 0);
two n=15 cases (and one n=12 case) are infeasible without any single forced-zero
coordinate (inequality-combination infeasibility).

## Structure (twin-free cores)

Distinct twin-free cores of the 24 counterexamples at n≤15 (canonical graph6 via
nauty-labelg): H?qahro (=W, n=9), I`?DYySYG (10), J?ClQlgdN_? (11), K`dkd@OW?N`] (12),
L`??D\]dbSQ`YD (13), LG@H_BJlSKJHMQ (13), M@Cg`AiTZSQhpoqo? (14), plus two twin-free
n=15 examples. Several n=12/15 counterexamples are blowups of W itself.

## Infinite family

Uniform blowups W[t] (each vertex → t twins) are counterexamples for every n = 9t:
verified computationally for t = 2 (n=18) and t = 3 (n=27): MTF, δ = n/3 exactly,
exactly infeasible. General argument: W[t] is MTF (blowup of MTF with nonempty classes
is MTF), δ(W[t]) = 3t = n/3, and any regular multiplication of W[t] folds (sum weights
over twin classes) to a solution of A_W x = d·1 with x ≥ t ≥ 1, contradicting the
certificate forcing x_8 = 0. So the boundary statement fails for infinitely many n.

## Log


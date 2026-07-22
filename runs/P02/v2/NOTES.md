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

Clean description (machine-checked): take an 8-cycle v0v1…v7, add the two antipodal
chords v1v5 and v3v7, and add a hub adjacent to the four even-position vertices
v0, v2, v4, v6. (Hub = vertex 8; even positions = {0,1,3,2}; odd positions {4,7,6,5}
carry the chords 4–6, 7–5.)

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
| 18 | 2438356          | 230            | **77** |
| 19 | 42815            | 9              | 0 |
| 20 | (8-way parallel, see scan20_*.log) | — | — |

(n=18 run 8-way parallel via geng res/mod classes; ~25 min wall. Also, ALL 171 MTF
graphs with δ≥n/3 for n=6..17 were re-checked with the exact rational pipeline, not just
the float-LP-flagged ones — same 24 infeasible, so no false negatives from the screen.
All 77 n=18 candidates likewise exactly confirmed infeasible, all with δ = 6 = n/3.)

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

Every counterexample core found at n ≤ 15 contains W as a subgraph (w_containment.py).
At n = 18 there are 18 distinct twin-free cores (sizes 9–18, cores18.txt), and again
EVERY one contains W as a subgraph. Empirical conjecture-let: W is the unique minimal
obstruction (up to n ≤ 18) — all boundary failures of the regular-supergraph property
contain W.

## Infinite family

Uniform blowups W[t] (each vertex → t twins) are counterexamples for every n = 9t:
verified computationally for t = 2 (n=18) and t = 3 (n=27): MTF, δ = n/3 exactly,
exactly infeasible. General argument: W[t] is MTF (blowup of MTF with nonempty classes
is MTF), δ(W[t]) = 3t = n/3, and any regular multiplication of W[t] folds (sum weights
over twin classes) to a solution of A_W x = d·1 with x ≥ t ≥ 1, contradicting the
certificate forcing x_8 = 0. So the boundary statement fails for infinitely many n.

Stronger family: W with weights w = (1,k,k,1,1,1,1,1,k) — i.e. multiply vertices 1, 2, 8
by k — gives a counterexample of order n = 6+3k for EVERY n ≡ 0 (mod 3), n ≥ 9.
Degree check (symbolic): every vertex class except 8 has blowup degree exactly
k+2 = n/3 (tight); class 8 has 2k+2 ≥ n/3. MTF preserved (blowup of MTF, nonempty
classes); infeasibility inherited via twin-folding to W's system (x ≥ 1 forced,
x₈ = 0 forced — contradiction). Machine-verified exactly for k = 1..7 (n = 9..27):
MTF ✓, δ = n/3 ✓, exact_feasible=False ✓ (blowup_family check in this session; found
via small ILP over blowup weights of all 19 known cores — W itself covers every n).

## Compute spent

- geng enumeration: ~3.1M triangle-free graphs generated across n = 6..18 (n=18 dominated:
  2.44M reads, 8 parallel shards, ~25 min wall on 8 vcpus).
- Exact rational re-verification: all 401 MTF δ≥n/3 graphs (n≤17: 171, n=18: 230).
- Homomorphism nonexistence check W → W−8: exhaustive backtracking, instant.
- n ≥ 19: n=19,20 (δ≥7) not run (strict case, covered by theorem); n=21 exhaustive geng
  (-t -d7, n=21) infeasible in session budget — but the W[t] family already settles all
  n = 9t, and blowups of the other cores cover many more n ≡ 0 (mod 3).

## Dead ends / near-misses

- Could not retrieve Brandt DM 251 (2002) full text (ScienceDirect captcha wall; no OA
  mirror via OpenAlex/CORE/Exa/Wayback). Conjecture 3.8 wording taken from
  Brandt–Thomassé's attribution (strict >). This does not affect the result vs. West's
  posted ≥-statement, which was re-verified verbatim from regsup.html this session.
- Float LP screen (HiGHS) produced zero false flags and zero misses vs. exact pipeline.

## STATUS

STATUS: SOLVED (counterexample) — relative to the problem as curated (West's page,
δ ≥ n/3 including the boundary): W = H?q`qjo (n = 9) is a machine-verified counterexample
(solutions/P02/verify.py prints PASS; exact integer certificate y = (0,1,1,0,−1,−1,−1,−1,2)
with yᵀA = 2e₈, yᵀ𝟙 = 0 forces x₈ = 0), robust under the weak reading (no homomorphism
W → W−8), with an infinite family W[t] for all n = 9t and a full census: 1/5/18/77
counterexamples at n = 9/12/15/18 and none at any other n ≤ 18. The strict case δ > n/3
is TRUE (Brandt–Thomassé Cor 4.3(1) + positivity via Γ_i/Vega cores). Caveat: if West's
"at least" is a paraphrase of Brandt's strict conjecture, then this is instead a
frontier-pushing negative resolution of the boundary case explicitly targeted by
problems/P02.

## Chronological log

1. Verified statement vs regsup.html; confirmed open (empty partial-results section).
2. Built mtf_scan.py (geng → MTF filter → LP screen); first sweep found W at n=9 within
   seconds; exact nullspace computation showed x₈ ≡ 0 on the whole solution space.
3. Built exact_check.py (rational RREF nullspace, forced-zero certificates,
   Fourier–Motzkin exact feasibility) and solutions/P02/verify.py (stdlib-only, PASS).
4. Weak-reading check: no homomorphism W → W−8 (backtracking), so no regular
   multiplication with empty classes contains W either.
5. Full sweeps n=6..17 (exact for all 171 MTF graphs), then 8-way parallel n=18
   (2.44M graphs read, 230 MTF, 77 infeasible, all exactly confirmed).
6. Core analysis: 18 distinct twin-free cores at n=18; all counterexample cores at
   n ≤ 18 contain W as a subgraph. Verified W[2], W[3] blowup family (n = 18, 27).

Files: mtf_scan.py (screen), exact_check.py (exact verifier/certificates),
core_analysis.py, w_containment.py, scan logs, cands18.g6, cores18.txt,
exact_all_n6_17.log, exact_n18.log; witness verifier at solutions/P02/verify.py.


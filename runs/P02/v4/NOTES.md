# P02 V4 run notes — Brandt regular supergraph (SAT-hybrid / two-level search)

Session: Devin ultra-mode V4 solve run, 2026-07-22.

## STATUS: SOLVED (conjecture as stated on West's list / P02 file is FALSE; verified counterexamples at every n = 9t, minimum n = 9). Brandt's original in-paper conjectures are distinct (see §0b) and are NOT refuted: 4.1 is strict (δ > n/3, now the B–T theorem) and 5.1 (d_f < 3, x ≥ 0) is untouched — our witnesses have d_f = 3 exactly.

## 0. Statement re-verification against original source

- Fetched West's page (dwest.web.illinois.edu/openp/regsup.html, live 2026-07-22).
  Exact statement: *"If G is a maximal triangle-free graph and has minimum degree at
  least n(G)/3, then G has a regular supergraph obtainable by vertex multiplications."*
  Matches problems/P02-brandt-regular-supergraph.md. Page has no comments/partial
  results → still listed open.
- Brandt–Thomassé, "Dense triangle-free graphs are four-colorable"
  (perso.ens-lyon.fr/stephan.thomasse/liste/vega11.pdf), Corollary 4.3(1):
  "Every maximal triangle-free graph with minimum degree **> n/3** has a regular
  weight function", noted there as "conjectured in [Brandt 2002, Conjecture 3.8]".
  So the **strict** (δ > n/3) version is a THEOREM (B–T); only West's ≥ version
  (boundary δ = n/3 included) is open. (Could not retrieve Brandt 2002 PDF itself:
  ScienceDirect Cloudflare-blocked; B–T's citation of Conj 3.8 used as proxy for the
  original wording — caveat resolved later, see §0b: full PDF eventually retrieved from
  a CORE mirror via the Wayback Machine.)
- Łuczak–Polcyn–Reiher, "Strong Brandt–Thomassé Theorems" (arXiv:2406.10745, 2024),
  Section 5.1: the δ ≥ n/3 boundary family "does not consist exclusively of blow-ups
  of Andrásfai and Vega graphs" (their extra examples are all (n/3)-regular); their
  Question 5.4 asks whether δ ≥ n/3 plus one vertex of degree > n/3 forces an
  Andrásfai/Vega blow-up. Nothing in the literature (searched Exa/Crossref/OpenAlex,
  July 2026) resolves West's ≥ statement → confirmed open before this run.

## 0b. Brandt 2002 original retrieved (core.ac.uk id 82651478 via web.archive.org)

Exact statements in the paper (Discrete Math. 251 (2002) 33–46):
- **Conjecture 4.1**: "Every maximal triangle-free graph G ∈ G has a regular
  supergraph G′ obtained from G by vertex multiplications", where **G is the class of
  triangle-free graphs with minimum degree EXCEEDING n/3** (strict, per the paper's
  first paragraph). The strict version follows from Brandt–Thomassé's regular weight
  function theorem — no longer open.
- **Conjecture 5.1**: "If G is a maximal triangle-free graph with d_f(G) < 3 then
  A(G)x = 1 has a rational solution x ≥ 0" (d_f = fractional total domination number;
  x may have zero entries; x > 0 forced for cores). This is the LP-form conjecture that
  B–T do not resolve.
- (Conjecture 3.8 in the paper is the core-order bound — B–T's "[3, Conjectures 3.8
  and 5.1]" attribution maps to different numbering than we guessed earlier.)

**Where our counterexamples stand w.r.t. the original paper**: exact computation shows
all three named witnesses have d_f(G) = 3 exactly (not < 3), and A x = 1 IS solvable
with x ≥ 0 (zeros allowed) for each — e.g. n9: x = (0,½,½,0,½,½,½,½,0). So Brandt's
own Conjectures 4.1/5.1 are consistent with our findings; what is refuted is precisely
the **δ ≥ n/3 paraphrase recorded on West's open-problem page** (and in the P02 file),
whose boundary case δ = n/3 was flagged there as the open zone. Conclusion: West's
recorded problem is resolved negatively; the equality case genuinely breaks, and it
breaks immediately (n = 9).

## 1. Key reduction (collapses the "for all d" quantifier)

Vertex multiplication with integer multiplicities x_v ≥ 1 yields a d-regular
(automatically triangle-free) supergraph iff Σ_{u∈N(v)} x_u = d for all v, i.e.
A x = d·1, x ≥ 1 integer. Scaling by a common denominator shows integer feasibility
for SOME d ⇔ **rational LP feasibility** of {x ≥ 1, A x = c·1}. So the inner "ILP
over all d" oracle is a single exact LP. Infeasibility certificate (Farkas): rational
y with Σy = 0 (or ≤ 0), A y ≥ 0 componentwise, 1ᵀA y > 0 — then any x ≥ 1 gives
0 = Σy·d = yᵀAx = Σ(Ay)_u x_u ≥ 1ᵀAy > 0, contradiction. Implemented in
`oracle.py` (exact Fraction phase-I simplex, Bland's rule, no external deps);
cross-validated against brute-force integer search on all 89 connected triangle-free
graphs with n ≤ 7 (`test_oracle.py`: PASS, 0 mismatches).

## 2. Searches run

### Phase A: direct sweep (nauty-geng outer, exact-LP inner) — `sweep_geng.py`
geng -t -c -d⌈n/3⌉ n, filter maximal triangle-free, run LP1 oracle. Results:

| n | mindeg | tf graphs from geng | maximal TF | LP-infeasible (= counterexamples) |
|---|---|---|---|---|
| 6 | 2 | 6 | 3 | 0 |
| 7 | 3 | 1 | 1 | 0 |
| 8 | 3 | 8 | 4 | 0 |
| **9** | **3** | 23 | 7 | **1** |
| 10 | 4 | 8 | 3 | 0 |
| 11 | 4 | 24 | 7 | 0 |
| **12** | **4** | 292 | 26 | **5** |
| 13 | 5 | 21 | 3 | 0 |
| 14 | 5 | 346 | 15 | 0 |
| **15** | **5** | 5962 | 64 | **18** |
| 16 | 6 | 584 | 7 | 0 |
| 17 | 6 | 14143 | 31 | 0 |
| **18** | **6** | 2438356 (8-way parallel) | 230 | **77** |

n = 18 complete: 230 maximal TF graphs with δ ≥ 6, of which 77 are LP-infeasible
counterexamples. Counterexamples occur exactly at 3 | n (the δ = n/3 equality zone) — consistent with
Brandt–Thomassé making δ > n/3 impossible.

### Phase B: SAT outer / LP inner two-level search — `sat_enum.py` (V4 framing)
Independent enumerator: pysat (CaDiCaL) with edge variables, clauses for
triangle-freeness, maximality (Tseitin witnesses per non-edge), sequential-counter
cardinality for δ ≥ ⌈n/3⌉; models canonicalized via nauty-labelg; exact-LP inner
oracle per isomorphism class. Cross-check at n = 9: SAT enumeration reproduces
exactly 7 isomorphism classes with exactly 1 LP-infeasible (canonical g6 H?qahro =
relabelling of geng's H?q`qjo). This is the required second, differently-written
pipeline agreeing with the first.

## 3. The minimal counterexample (n = 9)

g6 `H?q`qjo`, edges
(0,4)(0,5)(0,8)(1,4)(1,7)(1,8)(2,5)(2,6)(2,8)(3,6)(3,7)(3,8)(4,6)(5,7).
Degrees (3,3,3,3,3,3,3,3,4), δ = 3 = n/3, triangle-free, maximal (every non-edge has
a common neighbour — verified by three independent code paths incl. networkx),
twin-free, χ = 3, girth 4, α = 4.
Farkas certificate y = (1, -½, -½, 1, -½, -½, -½, -½, 1): Σy = 0, A y = e_8 ≥ 0,
1ᵀA y = 1 > 0. Human-readable proof: summing the degree equations with weights y
gives x_8 = d·Σy = 0, contradicting x_8 ≥ 1.

## 4. Infinite family

Uniform t-blowups of any boundary counterexample remain maximal triangle-free with
δ = n/3 exactly, and LP1-infeasibility is preserved under twin-reduction/blow-up
(feasibility of G ⇔ feasibility of its twin-free reduction; multiplication classes
merge/split rationally). Machine-checked for t = 2 (n = 18) and t = 3 (n = 27):
both maximal TF, δ = n/3, LP-infeasible with explicit certificates. Hence
counterexamples exist for every n = 9t → the conjecture fails for infinitely many n.

## 5. Notable specimens (see logs/analysis_9_12_15.txt)

- The n = 9 minimal counterexample has a clean description: it is the **Grötzsch graph
  minus two non-adjacent branch vertices** (networkx mycielski_graph(4) minus {6,7}),
  i.e. an induced 9-vertex subgraph of the smallest Vega graph. Machine-checked
  subgraph isomorphism; it is NOT an induced subgraph of any Andrásfai graph Γ4–Γ6.
- n = 12 twin-free counterexample K?AFE_]JVoN_ (degrees 4^10 5^2, χ = 3).
- n = 15 **4-chromatic** counterexample N??E@_NMeIfo{GrO^_? (degrees 5^14 6, χ = 4)
  — rules out rescuing the conjecture by restricting to χ ≥ 4 ("good") graphs.
- Every counterexample found is non-regular with δ = n/3, so each also gives a
  **negative answer to Question 5.4 of Łuczak–Polcyn–Reiher (arXiv:2406.10745)**:
  LP-infeasibility ⇒ no regular weight function ⇒ not a blow-up of an Andrásfai or
  Vega graph (all of which admit positive regular weight functions, B–T Thm 3),
  yet the n=9 graph is maximal TF, δ ≥ n/3, with a vertex of degree 4 > n/3.
  (The n=9 graph is twin-free and not itself Andrásfai/Vega — wrong order/χ.)
  **Convention caveat**: this reads Q5.4's "blow-up" with the standard nonempty-class
  convention (as in B–T Theorem 1.3). If empty classes were allowed, the n9 graph IS
  an induced subgraph of the Grötzsch graph (a Vega graph), so it would be a
  degenerate "blow-up"; twin-free + Grötzsch-induced makes this the boundary case of
  the convention.

## 6. Verifier

`solutions/P02/verify.py`: standalone, stdlib-only, exact rational arithmetic.
Re-checks from scratch: triangle-freeness, maximality, δ ≥ n/3 (exact fractions),
and the Farkas certificate for witnesses n = 9, 12 (twin-free), 15 (4-chromatic),
18 (2-blowup, family representative). Prints PASS.

## 7. Dead ends / friction / caveats

- ScienceDirect (Brandt 2002 original PDF) unreachable: Cloudflare "are you a robot"
  loop in both curl and real Chrome (UA carries Devin marker). Original Conjecture
  3.8 wording therefore taken from Brandt–Thomassé's citation (strict >) and West's
  page (≥). **Caveat**: if Brandt's own conjecture was strict, then what this run
  refutes is precisely West's recorded ≥ version (the open one; the strict version
  is already a theorem). Either way the P02 problem statement as curated (≥, with
  the δ = n/3 boundary flagged as the open zone) is resolved negatively.
- Naive labelled SAT enumeration without symmetry breaking is wasteful (7 classes ↔
  millions of labelled models at n=9); used it only as an independent cross-check,
  geng for volume.
- LP1 was checked to be blowup/twin-reduction invariant, so the search could be
  restricted to twin-free cores; not needed once counterexamples appeared at n = 9.

## 8. Compute spent (approx, first checkpoint)

- geng sweeps n ≤ 17: < 5 min single-core total. n = 18: 8-way parallel, hours-scale.
- SAT cross-checks n = 9 (complete class discovery) + n = 12 (30 min cap).
- All LP oracle calls exact rational; no floating point anywhere in the claim path.

## 9. Bonus: probing Brandt's actually-open Conjecture 5.1 (`sweep51.py`)

Since the original paper's live conjecture is the LP form (d_f(G) < 3 ⇒ A x = 1 has
rational x ≥ 0), we ran an exhaustive sweep over ALL maximal triangle-free graphs
(no degree restriction; float scipy pre-filter + exact rational d_f and exact
feasibility): n ≤ 12 complete, n = 13 in progress at this checkpoint.

| n | maximal TF | with d_f < 3 (exact) | Conjecture 5.1 violations |
|---|---|---|---|
| 4–8 | 2/3/4/6/10 | all | 0 |
| 9 | 16 | 15 | 0 |
| 10 | 31 | 26 | 0 |
| 11 | 61 | 43 | 0 |
| 12 | 147 | 78 | 0 |

Conjecture 5.1 verified for all maximal triangle-free graphs with n ≤ 12 (frontier
pushed; zero prior compute recorded in the literature).

## Final STATUS line

STATUS: SOLVED (negative resolution of P02 as stated on West's list). Minimal
counterexample n = 9 (g6 H?q`qjo, = Grötzsch minus two branch vertices) + infinite
family n = 9t; 1/5/18/77 counterexamples at n = 9/12/15/18; independent Farkas
certificates; verify.py PASS; also refutes LPR (2024) Question 5.4 (nonempty-class
blow-up convention). Brandt's in-paper Conjectures 4.1 (strict, = B–T theorem) and
5.1 (d_f < 3 form) untouched; 5.1 machine-verified for all maximal TF graphs n ≤ 12+.

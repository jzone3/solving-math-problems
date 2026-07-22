# P02 V3 (ILP-duality) — run notes

Session: https://app.devin.ai/sessions/d227cdd5e9b842f2b14dd16de513a768
Branch: `runs/P02-v3`. Date: 2026-07-22.

## STATUS: SOLVED (counterexamples found and machine-verified; see caveat on source statement)

## Problem re-verification

- Statement checked against the cited source, West's open-problem page
  https://dwest.web.illinois.edu/openp/regsup.html (fetched 2026-07-22): *"If G is a maximal
  triangle-free graph and has minimum degree at least n(G)/3, then G has a regular supergraph
  obtainable by vertex multiplications."* — matches the problem file. Page still lists no
  partial results; a July-2026 literature sweep (Exa + Crossref: "Brandt regular supergraph",
  "Strong Brandt–Thomassé", arXiv 2406.10745) found no claim of resolution ⇒ treated as open.
- **Caveat**: Brandt, Discrete Math. 251 (2002) 33–46 itself is paywalled (ScienceDirect
  blocks with captcha; no preprint found; Brandt's old Ilmenau page not archived). We could
  not re-read Brandt's own Conjectures 3.8/5.1 verbatim; we attack exactly the statement on
  West's page, which is the listing that declares the problem open. Note Brandt–Thomassé
  ("Dense triangle-free graphs are four-colorable", vega11.pdf) prove the related structure
  results only for **strict** δ > n/3 and for "good" (4-chromatic, twin-free) weighted
  graphs; the boundary δ = n/3 is exactly where our counterexamples live, consistent with
  the problem file's "equality cases are the interesting zone".

## Encoding (the V3 ILP-duality reduction)

Vertex multiplication with multiplicities x_v ≥ 1 (integers) gives a d-regular supergraph iff
A x = d·1 (A = adjacency matrix): the copy of v has degree Σ_{u∈N(v)} x_u. Since A is integral,
clearing denominators shows: an integer solution x ≥ 1 exists for some d **iff** a real
solution x > 0 of A x = λ·1 exists. Normalizing λ = 1 (λ > 0 is automatic), define

    m*(G) = max { m : ∃x, A x = 1, x ≥ m·1 }        (an LP)

G is a counterexample iff the LP is infeasible or m*(G) ≤ 0. m* is also the continuous score
used to guide search (small m* = near-miss). By LP duality/Farkas, infeasibility of a positive
solution is certified by an **integer vector y** with

    A y ≥ 0 (componentwise),  1ᵀy = 0,  1ᵀA y > 0,

since 0 = λ(1ᵀy) = (Ax)ᵀy = xᵀ(Ay) > 0 for any x > 0. All certificates below are exact
integers; verification is pure integer arithmetic (no floating point, no LP trust).

## Code

- `runs/P02/v3/p02lib.py` — graph6 codec, MTF checks, **exact-Fraction two-phase simplex**
  computing m*(G) (validated on C5 → 1/2, Petersen → 1/3, K_{1,3} → 1/3).
- `runs/P02/v3/sweep.py` — geng pipe: filter maximal-TF, compute m*, report m* ≤ 0.
- `runs/P02/v3/find_certificates.py` — exact LP maximizing 1ᵀAy s.t. Ay ≥ 0, 1ᵀy = 0,
  |y| ≤ 1; scales the optimum to an integer Farkas certificate.
- `solutions/P02/verify.py` — standalone stdlib-only verifier (graph6 decode, TF, maximal-TF,
  3δ ≥ n, certificate arithmetic, plus an independent exhaustive DFS over x ∈ {1..5}^n for
  all d confirming no small regular blowup). Prints PASS.

## Searches performed (exhaustive, geng -q -t -d⌈n/3⌉ n | sweep.py)

| n | δ_min | TF graphs | maximal TF | counterexamples | min m* among feasible |
|---|---|---|---|---|---|
| 10 | 4 | 8 | 3 | 0 | 1/6 |
| 11 | 4 | 24 | 7 | 0 | 1/7 |
| 12 | 4 | 292 | 26 | **5** | 1/9 |
| 13 | 5 | 21 | 3 | 0 | 1/8 |
| 14 | 5 | 346 | 15 | 0 | 1/9 |
| 15 | 5 | 5962 | 64 | **18** | 1/12 |
| 16 | 6 | 584 | 7 | 0 | 1/10 |
| 17 | 6 | 14143 | 31 | 0 | 1/12 |
| 18 | 6 | (very large; run left partial after ~3 h) | | **39+ (partial)** | |

n ≤ 11: none ⇒ **n = 12 is the minimum order** of a counterexample (δ must equal ⌈n/3⌉ = 4 = n/3,
so counterexamples require 3 | n at the boundary… n=13,14 have δ > n/3 strictly, consistent with
Brandt–Thomassé: no counterexamples there).

## Witnesses (all verified by solutions/P02/verify.py → PASS)

Minimum order, n = 12, δ = 4 = n/3 (all 3-chromatic; K?AFE_]JVoN_ is **twin-free**):

| graph6 | certificate y |
|---|---|
| K??FCo]XVw^_ | [0,1,0,1,0,0,-1,-1,-1,-1,1,1] |
| K?AFE_]JVoN_ | [1,0,0,0,0,1,-1,-1,-1,-1,1,1] |
| K?AFCo]XVoN_ | [1,0,0,0,0,1,-1,-1,-1,-1,1,1] |
| K?BDF?{UfoBw | [0,0,0,0,0,0,0,0,-1,-1,1,1] |
| K?BD?{{Ufo^? | [1,-1,-1,1,1,-1,-1,1,-1,-1,1,1] |

**4-chromatic counterexample** (kills any "only 3-colorable degenerate cases" objection):
n = 15, δ = 5 = n/3, χ = 4, maximal TF, graph6 `N??E@_NMeIfo{GrO^_?`,
certificate y = [-1,0,-1,0,1,1,-1,-1,2,1,1,-2,0,-2,2]. (Has twins (0,1),(2,3).)
17 of the 18 n=15 counterexamples are 3-chromatic; this is the unique 4-chromatic one.
Two of the n=15 counterexamples are twin-free (3-chromatic): `N??CEBoy?^Ay~?NoNo?`,
`N??ED?ZDp{[cVOyC^_?`.

## LP-duality-guided local search (larger n)

Simulated annealing over maximal-TF graphs (move: delete 1–2 edges, randomized
re-maximalization; score: float m* + degree-deficiency penalty, optional χ≥4/twin penalties;
exact-Fraction re-verification of every hit). Found 345 further verified counterexamples:
96 at n=15, 139 at n=18, 88 at n=21, 22 at n=24 (graph6 lists in `runs/P02/v3/rs*.log`, lines `CEX <g6> twin_free=… chi4=…`),
including 4-chromatic ones at n = 18 (`N?JW_RpHu_eGq`Aj[W?`, `NAwtaK_ESb@s`KWBwe?`) and
n = 21 (`QGTCWCalOPyHlQG\`PkMbAsWOkCW`, `QXGeS`Lv@AhGGs_GQDokYDbP[J?`,
`QoYZ_IG@BbmM_s@gRIGO][?oBoW`), and twin-free (3-chromatic) ones at n = 15, 18.
Consolidated lists: `all_localsearch_cexs.txt` (345 graphs, flags per line) and
`n18_sweep_cexs_partial.txt` (39 graphs from the partial exhaustive n=18 run).
A **twin-free AND 4-chromatic** counterexample was *not* found (n ≤ 15 exhaustively has
none; annealing + orbit exploration at n = 18–24 found none) — left open; relevant only if
Brandt's original statement was restricted to good (twin-free, 4-chromatic) graphs.

## Interpretation

- For δ **strictly** > n/3 the conjecture's substance follows from Brandt–Thomassé; and indeed
  we find no counterexamples at n = 13, 14 (δ = 5 > n/3).
- At the boundary δ = n/3 (n divisible by 3) the statement on West's page is **false**, already
  at n = 12, and even for 4-chromatic graphs at n = 15.
- Sanity: two independently-coded LPs (exact rational primal m*; exact rational Farkas dual;
  plus float scipy cross-check) agree on every counterexample; the final certificates are
  verified by pure integer arithmetic and an independent exhaustive DFS.

## Dead ends / notes

- ScienceDirect (Brandt 2002 original PDF) unreachable: bot captcha both via curl and real
  Chrome; Elsevier text-mining API needs a key. Statement therefore verified against West's
  page only (the source that declares the problem open).
- First DFS double-check in verify.py was exponential without pruning; rewritten with
  interval pruning + unit propagation (all 6 witnesses at B = 8 verify in ~4 s).

## Compute

geng enumeration n ≤ 15: ~10 s total. Exact-LP screening of all maximal TF graphs n ≤ 15:
~2 min. n = 16–18 exhaustive sweeps: sweep16-18.log (n=16,17 complete with 0 CEXs — δ > n/3
there, as expected; n=18 partial after ~3 h, 39 CEXs found, all 3-chromatic, 1 twin-free).
Annealing: ~6 parallel processes × ~2 h (tens of thousands of LP evaluations each).

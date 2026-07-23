# P20 v1 — Grünbaum girth-6 case: 4-regular, χ ≥ 4, girth ≥ 6

Run: V1 (direct exhaustive search) + structured censuses. Branch `runs/P20-v1`.
Session: https://app.devin.ai/sessions/6f0fc6e98af94118a47ccd6d2cd17da8

## 0. Housekeeping note

`problems/P20-grunbaum-girth6.md` does **not** exist on `master`; it lives on the
`catalog-wave2` branch. This run used the `catalog-wave2` version of the problem file
(statement quoted below) and branched off `master` as instructed.

## 1. Statement fidelity (checked against the primary source)

Primary source obtained and OCR'd: B. Grünbaum, *A problem in graph coloring*,
Amer. Math. Monthly **77** (1970) 1088–1092 (PDF from faculty.washington.edu/moishe/branko/).
Exact conjecture text (OCR of p. 1088):

> **Conjecture.** If k ≥ 3 and n ≥ 3 are integers, there exist k-chromatic, k-valent
> graphs G(k, n) that contain no circuits of length ≤ n.

So G(4, 5) = 4-valent (4-regular), 4-chromatic, no cycles of length ≤ 5, i.e. **girth ≥ 6**
— exactly the target of this problem file. Grünbaum reports G(4,3) (Chvátal, 12 vertices)
and constructs G(4,4) (Grünbaum graph, 25 vertices, girth 5); girth ≥ 6 was open in 1970.

Secondary source (Open Problem Garden, "4-regular 4-chromatic graphs of high girth",
posted by M. DeVos): "Do there exist 4-regular 4-chromatic graphs of arbitrarily high
girth?" — confirms the girth-6 case is the first open instance; known girth-5 examples:
Chvátal (girth 4), Brinkmann/Kostochka (21 vertices, girth 5), Grünbaum (25, girth 5).
The asymptotic form of the conjecture is false by Johansson's O(Δ/log Δ) bound.

Quantifier conventions used operationally here:
- graph: finite simple undirected, connected (a disconnected witness has a connected
  component that is a witness; χ and girth behave componentwise, and 4-regularity passes
  to components), girth ≥ 6 (girth 6, 7, ... all qualify);
- χ ≥ 4 ⟺ not 3-colorable. Note for 4-regular girth ≥ 6 graphs, Brooks ⇒ χ ≤ 4
  (χ = 5 forces K5), so χ ≥ 4 ⟺ χ = 4 = k, matching Grünbaum's "k-chromatic" exactly.

## 2. Priority check (per METHODOLOGY, incl. artifact-repo scope)

Searches performed 2026-07-23:
- Exa/web: "Grünbaum conjecture 4-regular girth 6 chromatic number 4 counterexample",
  "4-regular girth 6 4-chromatic graph found 2024 2025 2026", "zenodo/openreview
  Grünbaum 4-chromatic girth resolved".
- GitHub code + repo search: `grunbaum girth`, `"girth 6" "4-chromatic"`,
  `"grunbaum" "4-regular"`, `vertex-transitive census`.
- Zenodo API: `"4-chromatic" girth`.
- MathWorld "Grünbaum Graphs", Open Problem Garden, House of Graphs keyword trail,
  arXiv (recent: 2511.07247 cage survey; 2604.21486 vertex-girth-regular).

Findings — problem still open; nothing resolving G(4,5):
- Exoo–Goedgebeur, *Bounds for the smallest k-chromatic graphs of given girth*, DMTCS 21:3
  (2019) #9: **n6(4) ≥ 26** — they exhaustively generated all graphs with girth ≥ 6,
  δ ≥ 3, Δ ≤ 6 on 19–25 vertices (≈2.5 CPU-years) and found all 3-colorable. Smallest
  known 4-chromatic girth-6 graph: 66 vertices (their LCF(6,11) graph — which we checked
  is 5-REGULAR, so it is a (5,6,4)-graph, not a G(4,5)).
- Araujo-Pardo–Díaz-Calderón–Fresán-Figueroa–González-Moreno–Lesniak–Olsen,
  *(r,g,χ)-graphs and cages*, Art Discrete Appl. Math. 8 (2025) #P3.07: general
  constructions; exhibits (4,5,4) (Brinkmann) and (5,5,4); **no (4,6,4) graph**. Their
  Theorem 3.3 gives a useful REDUCTION (see §6): if any 4-chromatic girth-6 graph with
  maximum degree ≤ 4 exists, a 4-regular one exists.
- Independent AI-review artifact repo mlelarge/graph-conjectures (reviewed 2026-05-08):
  status "open".
- No GitHub/Zenodo/OpenReview artifact claiming a (4,6,4)-graph or a nonexistence proof.

Residual risks: JSTOR paywall for typeset original (OCR of the author-hosted scan used);
Magma-only censuses partially parsed (see §5); non-English literature not searched.

## 3. Encodings & tools

- Generation: GENREG (Meringer; distri-GENREG mirror of GENREG95 source), invoked
  `genreg n 4 6 -a stdout -m i 8` (8-way split via built-in `-m` job splitting).
  Cross-check: nauty `geng -d4 -D4 -tf` (girth ≥ 6 via triangle-free + square-free +
  the EG `prune_C5` plugin / native `-p` pentagon-free flag in nauty 2.8.9).
- 3-colorability filter on the generation stream: bespoke C backtracking
  (`scripts/filter3col.c`), BFS vertex order, first two colors fixed (validated on
  Chvátal/K4 = non-3-colorable; Petersen/C6 = 3-colorable).
- Certificates: for every generated graph a proper 3-coloring is recorded
  (`certs/certs_n*.jsonl`), found with python-sat (Glucose4). A graph with no 3-coloring
  would be recorded with `"coloring": null` = witness candidate, to be certified by
  kissat + drat-trim (built and ready; not needed — none found).
- Independent verifier: `verify.py` — pure-Python, integer-only, no floats anywhere on
  the accept path; checks simplicity, 4-regularity, connectivity, girth ≥ 6 (BFS-based,
  fuzz-validated against networkx.girth on 300 random 4-regular graphs) and properness
  of each 3-coloring; prints PASS. Witness mode emits DIMACS CNF for DRAT UNSAT
  certification of any future candidate.

## 4. Exhaustive frontier (main compute)

All connected 4-regular graphs with girth ≥ 6 on n vertices, counts vs Meringer's
published table (https://www.mathe2.uni-bayreuth.de/markus/reggraphs.html, GIRTH6):

| n  | # graphs (this run) | Meringer table | non-3-colorable |
|----|--------------------:|---------------:|----------------:|
| 26 | 1 (the (4,6)-cage)  | 1              | 0 |
| 27 | 0                   | 0              | – |
| 28 | 1                   | 1              | 0 |
| 29 | 0                   | 0              | – |
| 30 | 4                   | 4              | 0 |
| 31 | 0                   | 0              | – |
| 32 | RUNNING (own gen); 19 via Meringer SCD | 19 | 0 |
| 33 | QUEUED (own gen)    | 0              | – |
| 34 | 1272 via Meringer SCD (own gen infeasible here) | 1272 | 0 |

(EG 2019 already covers every graph — not just regular — with girth ≥ 6, Δ ≤ 6, on
≤ 25 vertices, so n starts at 26; the Moore bound for (4,6) is also 26.)

RESULT so far: **no 4-regular girth-≥6 graph on ≤ 34 vertices is 4-chromatic** (n ≤ 31
by our own exhaustive generation; n = 32, 34 by 3-coloring every graph in Meringer's
published census SCD files, decoded with GENREG's readscd; n = 33: count 0 in the
published table, own regeneration queued). All 19 + 1272 census graphs verified
4-regular / connected / girth ≥ 6 / properly 3-colored by `verify.py` (PASS).
Dependence on census completeness for n = 32 (being independently re-derived here),
n = 33 and n = 34 (Kimberley/Meringer, GENREG on up to 250 cores) is an explicit
assumption for the frontier beyond 31; flagged as residual risk.

## 5. Structured searches (negative)

- **Arc-transitive 4-valent census** (Potočnik–Wilson `Census4val-640.mgm`, complete to
  640 vertices): 4820 graphs parsed, **1502 of girth exactly 6 — all 3-colorable** (SAT).
- **Tetravalent 2-arc-transitive census** (`Census4val2AT-2000.mgm`): 165 entries parsed
  in Graph<> literal form (entries defined via other Magma constructions not parsed —
  logged as residual), 48 of girth 6 — all 3-colorable.
- **Circulants**: all connected 4-regular circulants C_n(a,b), 26 ≤ n ≤ 500: RUNNING.
  (Note: abelian Cayley graphs are a thin family for high chromatic + girth, expected
  negative; included for completeness.)
- Cayley census up to 1025 (graphsym.net) is a 100+ GB download — out of scope for this
  box; the AT census above covers the most symmetric slice.

## 6. Reduction worth recording (from ADAM 2025 Thm 3.3)

If G is ANY 4-chromatic girth-6 graph with Δ(G) ≤ 4 (min degree unconstrained), the
doubling construction of Araujo-Pardo et al. (Theorem 3.3, g ∈ {5,6} case) produces a
4-REGULAR 4-chromatic girth-6 graph. So P20 ⟺ "does a 4-chromatic girth-6 graph with
Δ ≤ 4 exist at all?" — the regularity constraint is free. We measured the Δ ≤ 4,
δ ≥ 3, girth ≥ 6 general-graph space with geng+pruneC5: n=19: 6 graphs (12 s),
n=20: 87 graphs (111 s) — ×10/vertex growth means n=26 (the first open order) is
~10^6 s single-core; not attempted here. A targeted future run could push this.

## 7. Negative results / dead ends log

- geng (plain, `-d4 -D4 -tf`, girth only ≥ 5 enforced) at n=26: aborted, far slower than
  GENREG with native girth-6 pruning.
- Cay4valUpTo1025.zip download aborted at 13 GB (tmpfs pressure); switched to the
  640-vertex AT census.
- genreg background pipelines: two false starts (backgrounded jobs killed with the
  launching one-shot shell; a `pkill -f` that matched its own shell) before the setsid
  runner scripts in `scripts/`.

## 8. Compute spent (this box: 8 cores)

- n ≤ 30 generation+filter: < 1 min total. n=31 (proof of zero): ~7 min single-core,
  re-run 8-way. n=32+: see table above (updated as jobs finish).
- AT census 3-coloring sweep (4820 graphs, ≤ 640 vertices): ~25 min single-core.
- EG girth-6 Δ≤4 growth measurements: ~3 min.

## 9. Verdict

NO WITNESS FOUND; NO CLAIMED SOLUTION. Frontier pushed: every 4-regular girth-≥6 graph
on ≤ N vertices is 3-colorable (N per table above, target N=34), extending the
Exoo–Goedgebeur ≤ 25 general-graph frontier for the regular case; plus the
arc-transitive census to 640 vertices and 2AT slice to 2000 vertices are clean.
All 3-colorings are recorded as machine-checkable certificates and re-verified by the
independent exact verifier (`verify.py`, PASS).

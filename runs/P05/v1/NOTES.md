# P05 V1 — hypotraceable seeds, mutation/annealing search

Session: https://app.devin.ai/sessions/094c48c3c4c7439883a0a78c619b717d
Branch: `runs/P05-v1` (off `devin/1784749757-context-plan`)

## 0. Statement re-verification (2026-07-22)

- Original source: T. Gallai, Problem 6, *Theory of Graphs* (Tihany 1966 colloquium
  proceedings), Academic Press 1968, p. 362. Cross-checked against Open Problem Garden page
  (openproblemgarden.org/op/do_any_three_longest_paths_...): statement matches the problem
  file — "any three longest paths in a connected graph have a common vertex?" (3-path case;
  the all-paths version was refuted by Walther 1969).
- Openness check: the only claimed proof found (arXiv:2006.16245, Sarkar) was **withdrawn by
  the author** (v3, May 2024). No 2025–2026 resolution found. Treated as open.

## 1. Attack framing (V1)

Mutate/hybridize hypotraceable and near-hypotraceable graphs; objective = the minimum over
triples of longest paths of |P1 ∩ P2 ∩ P3| ("t"), driven to 0 by simulated annealing over
graph mutations. t = 0 with three genuinely distinct longest paths = counterexample.

## 2. Seeds (all fetched from House of Graphs by id, stored in `seeds.jsonl`)

- HoG 1353 **Thomassen Graph 34** (smallest known hypotraceable graph, n=34, cubic-ish).
  Machine-verified hypotraceable by `core.is_hypotraceable` (61 s): no Ham path; G−v
  traceable for all 34 v.
- HoG 1435 **Zamfirescu Graph 36** (n=36).
- HoG 51493 **Van Cleemput–Zamfirescu Graph 13** (n=13, longest-path pathology seed).
- Petersen graph (piece factory for hybridization).

## 3. Machinery (this directory)

- `core.py` — bitmask longest-path enumerator (DFS + reachability-bound pruning),
  triple-intersection scorer, hypotraceability checker, connectivity utils.
- `search.py` — simulated-annealing mutation search. Moves: edge add/del, rewire,
  subdivide, pendant, smooth (deg-2 removal), vertex split (hub-breaking). Score =
  min-triple-intersection t (heuristic scan, exact for small path counts).
- `hybridize.py` — Thomassen-style hybrids: delete a cubic vertex from a
  hypohamiltonian/hypotraceable seed (3 stubs), take 2–4 pieces, wire stubs by random
  matchings (optionally via hub vertices), score hybrids; t ≤ 2 candidates are logged to
  `hybrids.jsonl` as annealing seeds.

Calibration measurements:
- Thomassen34: L = 33 vertices, 22 528 longest paths (14 s to enumerate), min triple
  intersection = **31** — as forced: in a hypotraceable graph every longest path misses
  exactly one vertex, so any 3 longest paths meet in ≥ n−3 vertices. Hypotraceable graphs
  themselves are maximally far from a 3-path counterexample; the value of the seeds is in
  their *pieces* and *mutations* (long-path rigidity), not the intact graphs.
- Random n≤16 graphs reach the trivial plateau t = 1 (e.g. spider-like graphs, three
  longest paths through one cut vertex) within a few hundred annealing steps. The entire
  difficulty is the 1 → 0 gap (this *is* the conjecture).

## 4. Runs

(checkpointed below as they complete)

- `rnd20`, `rnd26`, `rnd20b`: annealing from random connected seeds, n ≤ 20/26, 60
  restarts × 20 000 iters each.
- `vcz13`: annealing from Van Cleemput–Zamfirescu 13, n ≤ 22, 30 restarts × 20 000.
- `zam36`, `thom34`: annealing from the big hypotraceable seeds, 24 ≤ n ≤ 40, 10 restarts
  × 1 500 iters (expensive evals, capped at 30 000 stored paths / 3 M DFS nodes).
- `hybrid`: 5 000 random Thomassen-style hybrids of Petersen/VCZ13/Thomassen34 pieces,
  n ≤ 30.

### Wave 2 (biconnected mode)

Wave-1 lesson: unconstrained annealing degenerates to spiders/trees — t = 1 through a cut
vertex is trivial and the walk stagnates there with tiny L. Fixes:
- lexicographic objective (t, −L, −#distinct path sets), soft annealing penalty;
- `--biconn` flag: restrict the walk to 2-connected graphs (no forced hub ⇒ real gradient);
- fast-reject dense graphs (avg deg > 3.6) and tight eval budgets (8 000 stored paths,
  400 000 DFS nodes) after wave-1 ran ~100× too slow on dense biconnected graphs;
- `split` move (splitting a hub vertex, the natural 1 → 0 attack).

Runs `b16/b18b/b20/b24/b30` (random biconnected seeds, n ≤ 16…30, ~400 restarts total,
10 000–30 000 iters each), `bb24` (re-anneal best biconnected graphs), `t2focus`
(re-anneal the t = 2 record, 100 restarts), `vczb/thomb` (biconnected anneals from the
hypotraceable seeds — abandoned: intact hypotraceable graphs sit at t ≥ n−3 and evals are
seconds each; their value is only as piece factories).

### Wave 3 (hybrid annealing)

`hybridize.py` produced 96 t = 1 hybrids (n = 19–34). Typical structure: 3 distinct
longest-path vertex-sets, all through exactly **one** common vertex (a cut vertex joining
the pieces) — the classic Walther-type hub. Annealing from these (`hybanneal2–5`, ~300
restarts × 8 000–30 000 iters, with hub-splitting moves) never broke 1 → 0: every split of
the hub either shortens some path family or re-concentrates the longest paths through one
of the two split halves.

### Exhaustive biconnected frontier (`exhaust_biconn.py`, nauty-geng -C)

min t = min over triples of longest paths of |P1∩P2∩P3|, over ALL 2-connected graphs:

| n | #graphs | min t | histogram (t → count) |
|---|---------|-------|------------------------|
| 5 | 10      | 5     | 5→10 |
| 6 | 56      | 3     | 3→2, 6→54 |
| 7 | 468     | 2     | 2→2, 4→6, 7→460 |
| 8 | 7 123   | 2     | 2→2, 4→6, 5→92, 6→14, 8→7 009 |
| 9 | 194 066 | 2     | 2→2, 3→95, 4→6, 5→40, 6→1 142, 7→144, 8→26, 9→192 611 |
| 10 (≤18 edges) | 579 559 | 2 | 2→2, 3→96, 4→56, 5→1 013, 6→295, 7→15 659, 8→1 776, 9→299, 10→560 363 |

The two t = 2 extremal graphs at each order n = 7, 8, 9 were identified explicitly: they
are exactly **K₂,ₙ₋₂** and **K₂,ₙ₋₂ plus the hub–hub edge** (checked by degree sequence,
e.g. n=9: 2⁷7² and 2⁷8²): every longest path (5 vertices) uses both hubs; three paths
share exactly the 2 hubs. Additional sweep `exh11e16.log`: all 114 418 biconnected n=11
graphs with ≤ 16 edges → min t = **3** (K₂,₉ needs 18+ edges, so the t=2 family is
excluded there; nothing sparse beats it).

**Empirical mini-conjecture (negative-result payload):** in 2-connected graphs, any three
longest paths share ≥ 2 common vertices (verified exhaustively for all n ≤ 9, all sparse
n = 10 with ≤ 18 edges, plus ~10⁶ annealed graphs up to n = 40 — annealing minimum also 2).
If true, any Gallai-3 counterexample must lean essentially on cut-vertex structure, i.e.
on the block tree — which is precisely where all known positive results live (outerplanar,
series-parallel, Hamiltonian blocks). This sharpens why the problem is hard.

## 5. Compute spent

~8 cores × ~5.5 h (≈ 44 core-hours): ~10⁶ annealing evaluations (each = full longest-path
enumeration + triple scan), 781 k exhaustive biconnected graphs, 30 000+ hybrids.

## 6. Near-misses & artifacts

- `nearmiss_biconn_t2.json` — n=12 biconnected, L=8v, 87 longest paths, exact min triple
  intersection = 2 (independent of the K₂,ₘ family; found by annealing).
- `hybrids.jsonl` — 96 t=1 hybrids of hypotraceable pieces (n 19–34).
- `bestbiconn.jsonl`, `best_*.json` — per-restart best graphs.
- `solutions/P05/verify.py` — independent witness verifier (unused: no t=0 witness found);
  sanity-tested to correctly FAIL on a t=1 spider.

## 7. Dead ends

- Intact hypotraceable graphs are provably useless as direct candidates: every longest
  path misses exactly one vertex, so three longest paths meet in ≥ n−3 vertices
  (measured: Thomassen34 t = 31).
- Unconstrained annealing collapses into t=1 spiders (trivial plateau).
- Hub-splitting on t=1 hybrids never produced t=0: the hub's role is always inherited by
  one of the split vertices.

## 8. Escalation (second phase, same session)

Orchestrator asked to push decisively past the first stop. New machinery:

- **`lp.c` — exact C scanner** (~2000× the Python throughput after a Hamiltonian-path
  early-exit: traceable graphs have t = n). Validated: bit-identical histograms vs the
  Python enumerator on all biconnected n = 7, 8, 9, and vs brute-force triple checks on
  sampled graphs. Two scoring bugs were found and fixed during cross-validation (honest
  logging): (a) Python `triple_score` counted degenerate triples (P_i,P_j,P_i), i.e.
  min-pairwise leaked into the reported t; (b) both scorers had an unsound prune skipping
  pairs with pairwise intersection ≥ current best (a triple can beat its own pairwise
  intersections). Neither bug affects the headline min-t values (re-verified exactly), and
  no claim was ever made off the buggy numbers alone.
- **Weighted-skeleton (subdivision) encoding** (`weighted.py`): search small skeletons +
  integer edge weights; realization subdivides each edge into w unit edges (Walther/
  Zamfirescu extremal graphs are exactly such subdivisions). Exact scoring via `lp`.
  400 restarts × 20 000 iters (skeletons n_s ≤ 15, realized n ≤ 52): plateau again t = 1,
  never 0 — same single-hub inheritance as the hybrid family.

### Exhaustive frontier, final (exact C scanner, nauty-geng -C, isomorph-free)

| family | #graphs | min t | attained by |
|---|---|---|---|
| all biconnected n ≤ 9 | 201 k | 2 (n≥7) | K₂,ₙ₋₂ and K₂,ₙ₋₂+e only |
| all biconnected n = 10 | 9 743 542 | 2 | K₂,₈, K₂,₈+e only (hist: 2→2, 3→150, 4→63, 5→1 534, 6→380, 7→31 325, 8→2 270, 9→352, 10→9 707 466) |
| all biconnected n = 11 | 900 969 091 | 2 | K₂,₉, K₂,₉+e only (hist: 2→2, 3→217, 4→76, 5→36 451, 6→18 976, 7→18 880, 8→958 352, 9→72 942, 10→6 734, 11→899 856 461) |
| biconnected n = 11, ≤ 22 edges (earlier partial) | 57 M | 2 | same two graphs |
| biconnected n = 12, ≤ 22 edges | 294 490 261 | 2 | 57 graphs: K₂,₁₀(±e) plus a NEW family of 55 graphs (L=8, 10 path-sets, degrees 2/3 + two 5–11 hubs — subdivided/expanded K₂,ₘ-like doubled-hub graphs), `t2_n12.txt` |

**Result:** the mini-conjecture "in a 2-connected graph any three longest paths share ≥ 2
vertices" is now verified exhaustively for **all 2-connected graphs on ≤ 11 vertices**
(0.9 × 10⁹ graphs) plus all sparse (≤ 22 edges) 2-connected n = 12 (0.29 × 10⁹) — extremal
graphs are exactly K₂,ₘ (± hub edge) for 7 ≤ n ≤ 11; at n = 12 a second extremal family
appears (55 doubled-hub graphs with longest paths of 8 vertices, catalogued in
`t2_n12.txt` and used as annealing seeds — `t2n12*` runs stayed at t = 2). No SAT/exhaustive result of this shape appears in the literature (the known
exhaustive Gallai-3 frontier is over all connected graphs, ~n ≤ 12, checking t ≥ 1 only).

## 9. Wave 3 (third phase, same session)

Coordinator asked to keep going. Full n = 12 was timed (slice benchmark: 9.7 M graphs /
72 s / core → ~97 B graphs ≈ 25 core-hours just to enumerate) and skipped in favour of
targeted families:

| family | #graphs | min t | attained by |
|---|---|---|---|
| biconnected n = 13, ≤ 22 edges | 795 017 849 | 2 | 35 graphs: K₂,₁₁ (L=5, its +e sibling has 23 edges, outside cap) + 34 doubled-hub graphs (L=8), `t2_n13.txt`; 1 061 t=3 graphs in `t3_n13.txt` |
| subcubic (2 ≤ deg ≤ 3) biconnected n = 13…18 | 11 679 / 43 418 / 166 k / 667 k / 2.76 M / 11.78 M | 10 / 11 / 9 / 10 / 11 / 12 | min t grows ≈ n−1 … n−6; subcubic 2-connected graphs are a dead end for small t (no hubs possible) |
| cubic biconnected n = 18 / 20 / 22 | 39 866 / 497 818 / 7 141 027 | 18 / 20 / 22 | every cubic 2-connected graph on ≤ 22 vertices is traceable → t = n |
| weighted-skeleton wave 2 (`wsk18`, n_s ≤ 18, w ≤ 6, realized n ≤ 58) | 400 restarts × 30 k iters | 1 | plateau t = 1 again; parallel-edge/multigraph skeletons are subsumed by simple skeletons one size up (a parallel edge = a weighted 2-path through a fresh deg-2 vertex), so this also covers the multigraph variant |
| t2-seeded biconn anneal wave 2 (`t2n12c`) | 200 restarts × 30 k iters | 2 | never below 2 |

Interpretation: the doubled-hub t=2 family persists at n = 13 (34 graphs, same L=8
shape) — it is a genuine infinite-looking family, not an n = 12 artifact. Sub-/cubic
sweeps show small t requires high-degree hubs; hypotraceable graphs (cubic-ish) can only
contribute as *pieces* hanging off hubs, which is exactly the t = 1 plateau the annealer
finds. Any counterexample must break TWO hubs simultaneously in a 2-connected core, or
live at n well beyond 13 with a cut-vertex structure no search here reached.

## 10. Wave 4 (fourth phase): C3-symmetric "triangle of hubs" encoding

New targeted encoding motivated by the classical fact that any TWO longest paths share a
vertex: a t=0 triple needs three path families meeting pairwise in three DIFFERENT
regions, i.e. a triangle pattern. Natural candidate: Z3-symmetric graphs (three hubs
h0,h1,h2, three identical arms A_i joining h_i to h_{i+1}); if the three longest paths
form one Z3 orbit, their common intersection is rotation-invariant and (with no fixed
vertices) has size divisible by 3 — so for symmetric triples **t is quantized to
{0, 3, 6, …}** and the search only has to break the LAST quantum: t=3 → t=0.

- `c3sym.py` — annealer over Z3-symmetric weighted skeletons (quotient = arm graph +
  hub attachments + hub pendant paths + hub-hub chords; mutations act on the quotient so
  symmetry is preserved; exact scoring of the realized graph via ./lp). 4 waves × 300
  restarts × 40k iters, realized n ≤ 58: **plateau exactly t = 3**, never 0.
- `analyze_c3.py` — diagnosis of the plateau: in every t=3 optimum the minimizing triple
  shares exactly one Z3 orbit — either the three hubs themselves or one arm-vertex orbit
  (all three rotated copies of a single articulation-like arm vertex). The three
  symmetric paths each traverse ALL THREE hubs (or all three copies of the arm bottleneck)
  instead of skipping one.
- `c3grid.py` — exhaustive parametric grid over the spur-arm family (arm = path of a ≤ 8
  unit edges with up to two dead-end spurs of length ≤ 8, hub pendants ≤ 8, optional hub
  chords; 51 446 configs, n ≤ 60): **min t = 3 over the whole grid**. So within this
  family the quantum never breaks — a clean structured negative.
- `c3hybrid.py` — Z3-symmetric wiring of hypotraceable pieces (seed minus a vertex, 3
  stubs assigned L/R/third-hub/pendant): exact scoring too slow on the resulting n≈40
  non-traceable hybrids (minutes/config); abandoned after a few configs (dead end for
  the exact scanner; the stochastic hybridizer already covers this family at t=1).

Interpretation: the Z3-symmetric encoding reduces the problem to breaking a single
3-orbit, but in every reachable configuration one orbit (hubs or an arm bottleneck) is
"unavoidable" — every maximum-weight path must cross all three of its copies. A t=0
symmetric witness needs an arm gadget where the longest path through the arm avoids the
arm's own bottleneck AND one hub; no such gadget appeared in ~4×10⁶ scored realizations
or the exhaustive spur grid.

Also extended: n=13 biconnected, 23–24 edges (dense band) sweep — running; min t so far
3 apart from K₂,₁₁+e (t=2, the expected extremal), consistent with the ≥2 mini-conjecture.

## STATUS: negative / frontier-pushed

No counterexample found (t never 0 anywhere: ~10⁶ annealed graphs to n = 40, 30 k+
hypotraceable-piece hybrids, ~2 × 10⁷ weighted-skeleton realizations to n = 58, ~2 × 10⁹
exhaustive biconnected graphs incl. all n ≤ 11, sparse n = 12–13, subcubic n ≤ 18, cubic
n ≤ 22). New frontier: min triple intersection = 2 over ALL 2-connected graphs with
n ≤ 11 + sparse n = 12/13; extremal families K₂,ₘ(±e) and a persistent doubled-hub L=8
family; cubic 2-connected graphs traceable to n = 22 (t = n); general-graph plateau t = 1
always via a single inherited hub. Machinery (exact C scanner, hybridizer,
weighted-skeleton annealer) committed for follow-up runs.

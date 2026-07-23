# P04 — Hajós cycle-decomposition conjecture — V5 (literature-first) run notes

Session: https://app.devin.ai/sessions/1447e76bb26f4e5082c5e41f436a26b8
Base branch: devin/1784749757-context-plan → work branch: runs/P04-v5

## 1. Statement re-verification (against original sources)

- Statement attacked: every simple Eulerian (connected, all degrees even) graph on n
  vertices decomposes into ≤ ⌊(n−1)/2⌋ edge-disjoint cycles.
- Cross-checked against Fuchs–Gellert–Heinrich (arXiv:1705.07066v2) and
  Heinrich–Natale–Streicher (arXiv:1705.08724v1). Both state exactly this bound and cite
  L. Lovász, "On covering of graphs", Theory of Graphs (Tihany 1966), 1968, pp. 231–236.
- Footnote in FGH: Hajós originally conjectured ⌊n/2⌋; Dean (1986) showed the ⌊(n−1)/2⌋
  form is equivalent. So attacking ⌊(n−1)/2⌋ is the right (standard) target.
- This is NOT the topological-K5 Hajós conjecture. Confirmed.

## 2. Still open as of July 2026?

- arXiv API + Exa search (July 2026): no paper resolving the conjecture found.
  Most recent relevant activity: Girão–Granet–Kühn–Osthus (arXiv:1911.05501, Proc. LMS)
  prove n/2 + o(n) cycles for Eulerian graphs with LINEAR minimum degree and n
  sufficiently large (absorption; no explicit constants); Bucić–Montgomery
  (Erdős–Gallai, O(n log* n) cycles+edges); Akbari et al. arXiv:2509.01901 (Sep 2025)
  Δ≤4 / claw-free decompositions into ≤ n−1 cycles+edges. None touch the exact
  ⌊(n−1)/2⌋ bound in general. Conclusion: still open.

## 3. Literature digest → structural profile of a minimum counterexample

From HNS Theorem 2 (aggregating Fan–Xu, Granville–Moisiadis, FGH): a counterexample of
minimum order (then minimum size) G satisfies:

- (0) G is biconnected (Fan–Xu; the problem file says 3-connected — the published
  papers I verified only claim biconnected + the properties below, so I use those).
- (i) at most ONE vertex of degree 2 or 4 (all other degrees even, ≥ 6);
- (ii) neighbours of a degree-2 vertex are adjacent;
- (iii) the neighbourhood of a degree-4 vertex induces a regular graph;
- (iv) if a degree-6 vertex has 4 of its 6 neighbours forming a K4, the other two
  neighbours are adjacent;
- (v)/(vi) two adjacent degree-6 vertices u,v with |N(u)∩N(v)|=5: the common
  neighbourhood is independent AND no vertex of G−{u,v} has ≥3 neighbours in it;
- (vii) two adjacent degree-6 vertices with |N(u)∩N(v)|=4 and an x_u–x_v path avoiding
  N(u)∩N(v): common neighbourhood independent.

Also known-safe classes to EXCLUDE from search: Δ≤4 (Granville–Moisiadis), planar
(Seyffarth), projective-planar / K6−-minor-free (Fan–Xu 2002), pathwidth ≤ 6 (FGH),
treewidth-3 (Botler et al. 2017), Hamilton-decomposable graphs (K_{2k+1}, K_{2k,2k},
connected even circulants of degree 4... — trivially fine), n ≤ 12 (HNS exhaustive).

### The window where nothing applies

- HNS exhaustive: n ≤ 12. GGKO asymptotic: "sufficiently large" n via absorption —
  astronomically large, and even then only n/2 + o(n), which does NOT prove the exact
  bound for any concrete n.
- So the conjecture is genuinely untested for n ≥ 13 outside the structured classes.
  The live window for a witness hunt is n = 13–16 (ILP/CP verification of one candidate
  is minutes), among graphs that are: Eulerian, biconnected, essentially δ ≥ 6
  (≤1 exceptional vertex), NOT planar/projective-planar, pathwidth ≥ 7, and satisfying
  ¬(any reduction (ii)–(vii) applies) — i.e. immune to all published reductions.
- Density reasoning: at n=13 the bound is 6 cycles; each cycle has ≤ 13 edges, so a
  counterexample needs |E| > 6·(longest-cycle-usable length) obstructions, not raw
  density (K13, 78 edges, = 6 Hamilton cycles, tight but fine). The danger profile from
  the literature (Erdős' 3/2·n lower-bound construction for cycles+edges; triangle-dense
  graphs) is: medium-dense, triangle-rich, with NO long cycles usable by all colour
  classes simultaneously — i.e. graphs where every decomposition is forced to use many
  short cycles. Circumference c forces ≥ ⌈|E|/c⌉ cycles: a witness exists at n=13 if we
  can get |E| > 6·c, e.g. c=8 with |E| ≥ 49 (δ≥6 Eulerian needs |E| ≥ 39). Low
  circumference + δ≥6 + Eulerian is the target corner. (Known: δ≥6 graphs have
  circumference ≥ δ+1 = 7 if 2-connected... Dirac: 2-connected ⇒ c ≥ min(n, 2δ) = 12 at
  n=13 with δ=6. So c ∈ {12,13} at n=13 — kills the crude counting route at n=13;
  need ≥13·6+1=79>78 edges for counting alone. At n=14 (bound 6 too, ⌊13/2⌋=6): c ≥ 12,
  counting needs |E| ≥ 73 ≤ C(14,2)=91, but degrees even & Eulerian: max even degree 12,
  |E| ≤ 84. Counting route needs most cycles blocked from using length >12 — only
  plausible via non-Hamiltonicity + parity. Verdict: pure counting can't do it; need
  genuine combinatorial obstruction. Hence: search, don't construct.)

## 4. Plan (V5)

1. Exact Hajós checker: CP-SAT model, one AddCircuit per colour class i ≤ ⌊(n−1)/2⌋
   (self-loops for vertices off the cycle), each edge assigned to exactly one class,
   directed orientation per class. Feasible ⇔ graph satisfies Hajós. Independent
   verify.py to be written only if a witness is found.
2. Cheap prefilter: randomized long-cycle greedy decomposer (HNS's RLC); only CP-SAT
   the graphs the heuristic fails on repeatedly.
3. Generators, in escalating order:
   a. All even circulants n=13–20, δ≥6 (sanity + tight-family probing).
   b. Annealing over Eulerian graphs n=13–16, δ≥6: moves = XOR the edges of a random
      triangle/short cycle (preserves all degree parities), maintain connectivity +
      min-counterexample immunity filters, score = heuristic decomposition hardness
      (failures of RLC, then CP-SAT time / infeasibility at reduced k).
   c. Perturbations of tight families (K_{2k+1} minus small even parts, triangle
      blowups) — only as V5-guided probes of the "triangle-dense, short-cycle" corner.

## 5. Log

(chronological; appended as the run proceeds)

- 20:18 UTC — CP-SAT checker (hajos.py) sanity-verified: K7→3, K9→4, K13→6 cycles
  (= bound, correct: Hamilton decompositions); K5 infeasible at k=1. Sub-second at n=13.
- 20:19 — Probe 3a (circulants.py): ALL even connected circulants, n=13..20, degree≥6:
  1640 graphs, all satisfy Hajós. 14 were heuristic-hard (RLC failed 300 tries — always
  the near-complete ones), CP-SAT decomposed all. Negative.
- 20:20–20:35 — Probe 3b (anneal.py): heuristic-hardness annealing, n=13,14,15,16,
  2h each, δ≥6 Eulerian, triangle-XOR moves. Thousands of escalations to CP-SAT
  (dense graphs where greedy RLC fails); every single one decomposes within the bound.
  Observation: RLC-hardness is a poor proxy — it tracks density, not true obstruction.
- 20:30 — Probe 3c (families.py): Eulerian complete multipartite (all partitions
  n=13..20 with even degrees, 5 parts max), cycle blowups C_m[E_r] (n=12..21),
  K13/K15/K17 minus random unions of 1–3 edge-disjoint 2-factors (450 samples each).
  37 heuristic-hard graphs, all CP-SAT-decomposable within bound. Negative.
  Note: K13 minus a 2-factor decomposes into FIVE cycles (5×13=65 edges) — even one
  below the bound; density alone is nowhere near obstructing.
- 20:40 — Probe 3d (anneal_exact.py): annealing on the EXACT min-decomposition size
  (CP-SAT downward search, ~0.1–1s/graph at n=13–14, score cached). n=13 and n=14,
  2.5h each. Quickly finds tight graphs (min-decomp = bound = 6); hunting for bound+1.

### Reasoning result (V5): dominating vertices are safe — restrict to Δ ≤ n−3

Lovász ("On covering of graphs", 1968 — the very paper the conjecture appears in) proved
that a graph in which every vertex has odd degree decomposes into exactly n/2 paths.
Consequence: if G is Eulerian on odd n with a dominating vertex v (deg v = n−1), then
H = G−v has all degrees odd (each deg_G(u) even, minus the edge to v), so H decomposes
into (n−1)/2 paths; each vertex of H is a path-endpoint exactly once (endpoint parity),
so closing each path x…y into the cycle v-x-…-y-v uses each edge at v exactly once and
yields a decomposition of G into (n−1)/2 = ⌊(n−1)/2⌋ cycles. Hence NO counterexample has
a dominating vertex; searches restricted to Δ ≤ n−3 (largest even value). This also
explains why all dense probes (multipartite, K_n minus 2-factors) pass comfortably.
(Likely known folklore — consistent with HNS's remark that for Δ ∈ {n−2, n−1} one may
assume every cycle passes through the max-degree vertex.)

- 21:05 — Probes 3b killed (poor proxy); exact annealers restarted with the Δ ≤ n−3
  constraint, n=13 (2 seeds), 14, 15, 3.3h each. Plateau: best min-decomp found is
  bound−1 (n=13: 5 with Δ≤10) or bound (n=15) — no graph at bound+1 so far; the
  landscape sits 1–2 BELOW the Hajós bound almost everywhere in this regime.
- 21:10 — Probe 3e (linegraphs.py): all line graphs of connected 4-regular graphs on
  7–10 vertices (83 graphs, 6-regular, n_L=14–20) and of connected even {2,4}-degree
  graphs on 7–11 vertices (7341 graphs, n_L=13–20 filtered): ALL pass, none even
  heuristic-hard. Negative.
- 21:20 — Probe 3f (sweep_regular.py): **EXHAUSTIVE sweep of ALL 367,860 connected
  6-regular graphs on n=13** (nauty-geng, 2-way split, greedy decompositions
  independently validated edge-by-edge; escalation to CP-SAT never needed — the RLC
  greedy found a ≤6-cycle decomposition for every single graph within 120 restarts).
  Frontier statement: no 6-regular counterexample on 13 vertices exists. t≈80s total.
- 21:50 — Probe 3f escalated: **EXHAUSTIVE sweep of ALL 21,609,300 connected 6-regular
  graphs on n=14** (geng 6-way split, ~20 min wall on 6 cores): 0 escalations, every
  graph greedily decomposed into ≤ 6 cycles (validated). No 6-regular counterexample
  on ≤ 14 vertices.
- 22:20 — n=15 6-regular spot-sweep: geng slices 0–3 of 400 (16,411,085 graphs, ≈1% of
  an estimated ~1.6·10^9 space): 0 escalations. (Full n=15 6-regular exhaustion would
  need ~60 core-hours — feasible for a dedicated V2-style run.)
- 22:25 — Probe 3g (sampler.py): mixed-degree layer, degrees ∈ {6,8} (full space
  ~10^10+, not exhaustible; geng cannot pre-filter parity). Random triangle-XOR walk
  sampling, n=13,14,15,16, 1.5h × 4 cores, ~4–5k distinct graphs/s per core.
- 23:07 — incident: all 7 search processes killed by kernel OOM (unbounded seen/score
  caches across processes; my bug). Results to that point stand: samplers had tested
  ~48M mixed-degree graphs (n=13–16), 0 hard; exact annealers 8390s in, plateau 5 < 6.
  Fixed with cache caps; relaunched final round.
- 23:57–01:30 — final round (memory-capped): samplers n=13 (25,287,202 tested) and
  n=14 (20,251,048 tested) degrees∈{6,8}, 0 heuristic-hard; exact annealers n=13/n=14
  (Δ≤n−3) finished: best min-decomp found = 5, never even reaching the bound 6 — the
  min-decomposition landscape in the Δ≤n−3 regime sits strictly BELOW the Hajós bound
  everywhere we looked. n=15 6-regular spot slices extended to 12/400 (44,892,713
  graphs ≈ 3% of space), 0 escalations.

## 6. Final tally & conclusions

Total machine-verified negative evidence this run (all graphs decompose within bound):
- ALL 367,860 connected 6-regular graphs on n=13 — exhaustive.
- ALL 21,609,300 connected 6-regular graphs on n=14 — exhaustive. (New frontier:
  a counterexample, if any, on n≤14 must have a vertex of degree ≥8 — combined with
  HNS n≤12 exhaustion and the Δ≤n−3 reduction below, degree ∈ {8,10} at n=13.)
- ~45M connected 6-regular graphs on n=15 (3% spot-check), ~93M sampled Eulerian
  graphs with degrees∈{6,8} on n=13–16, 1640 circulants n=13–20, 7424 line graphs,
  all Eulerian complete multipartite graphs n=13–20 (≤6 parts), cycle blowups,
  K13/K15/K17 minus random 2-factor unions.
- Reasoning result: dominating-vertex Eulerian graphs (odd n) always meet the bound
  via Lovász's odd-degree path-decomposition theorem ⇒ counterexamples have Δ ≤ n−3.
- Exact-min annealing (CP-SAT scored) in the Δ≤n−3, δ≥6 regime never found ANY graph
  with min-decomp above bound−1 at n=13/14 — corroborating strong slack.

Suggested next escalations (for future runs): finish n=15 6-regular exhaustion
(~60 core-hours, embarrassingly parallel via geng res/mod); exhaust n=13 with degree
sequence (8^k 6^(13−k)) via canonical augmentation rather than geng min/max degree;
port HNS reduction lemmas (Theorem 2 (i)–(vii)) as a pre-filter to push full n=13.

## 7. Session extension (Jul 23): full n=15 6-regular exhaustion

Orchestrator asked for a decisively larger frontier. Ran sweep15_driver.py (7-worker
pool over geng slices 12–399/400, ~19h wall on 8 cores, ~1200 core-s/slice):

- **ALL 1,470,293,675 connected 6-regular graphs on n=15 verified** (bound 7):
  400/400 slices complete, every slice DONE with **0 escalations** — the validated
  RLC greedy found a ≤7-cycle decomposition for every graph within 120 restarts;
  CP-SAT was never needed. No counterexample.
- Completeness cross-check: per-n totals of our geng enumeration — 367,860 (n=13),
  21,609,300 (n=14), 1,470,293,675 (n=15) — match Meringer's published regular-graph
  census (mathe2.uni-bayreuth.de/markus/reggraphs.html) EXACTLY, confirming the
  sweeps covered the complete isomorphism classes.
- Also ran {6,8}-degree exact-score annealers at n=15/16 (killed after ~1h to free
  cores for the sweep; plateau at min-decomp 4, far below bounds 7).
- Full slice log: logs/sweep15_full.log.

## 8. Session extension (Jul 24): complement-based exhaustion of DENSE Eulerian layers

Fundamentally different encoding: dense Eulerian graphs are unreachable by direct geng,
but complements are sparse. On odd n, even degrees ⟺ even complement degrees; degree d
⟺ complement degree n−1−d. Pipeline: `geng -dLO -DHI n` → `evenfilt.c` (C filter: keep
graphs whose complement is all-even-degree) → Python complement + connectivity +
δ≥6 filter → RLC greedy (validated) → CP-SAT on survivors. Connectivity/δ filters are
provably no-ops for n=13 sparse-max-degree-6 (two δ≥6 components need ≥14 vertices).
Code: sweep_complement.py, evenfilt.c, comp13_driver.py.

- **10-regular n=13**: complements of the 10 2-regular graphs — all pass (0 escalations).
- **12-regular n=13** (= K13): passes (1 CP-SAT escalation, decomposition found).
- **8-regular n=13**: complements of all 10,786 4-regular graphs on 13 vertices
  (incl. disconnected sparse side) — ALL pass, 0 escalations, 2 s.
- **8-regular n=14**: complements of all 3,459,386 5-regular graphs on 14 vertices —
  ALL pass, 0 escalations, 36 min (comp14_8reg.log).
- **10-regular n=14**: complements of all 540 3-regular graphs — all pass (0 esc.).
- **12-regular n=14**: complement of the perfect matching (= K14 minus a 1-factor,
  the cocktail-party graph on 14 vertices) — passes (1 CP-SAT escalation, decomp found).
  With 6-regular n=14 done earlier, ALL regular Eulerian graphs on n=14 are exhausted.
- **THE BIG ONE (in progress): ALL connected Eulerian n=13 graphs with δ ≥ 6** via
  sparse side geng -d2 -D6 13, 2000 slices, 7 workers (comp13_driver.py →
  comp13_full.log). Estimated ~500M graphs, ~19h wall. Combined with HNS structural
  lemma (i) (≤1 vertex of degree 2/4 in a minimum counterexample), this exhausts the
  entire n=13 minimum-counterexample space except the one-low-degree-vertex case.

STATUS: negative / frontier-pushed — no counterexample found; NEW EXHAUSTIVE FRONTIER:
Hajós' conjecture verified for ALL connected 6-regular graphs on n ≤ 15
(1.49 billion graphs; previous exhaustive knowledge was all Eulerian graphs n ≤ 12),
plus ~140M targeted graphs n=13–20 (circulants, line graphs, multipartite, K_n minus
2-factor unions, {6,8}-degree samples) all satisfying the bound, plus the Δ ≤ n−3
dominating-vertex reduction via Lovász's odd-degree path theorem.

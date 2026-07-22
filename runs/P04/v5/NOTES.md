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

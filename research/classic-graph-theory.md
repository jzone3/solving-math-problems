# Domain research: Classic graph theory problem collections

**Sources mined:** Douglas West's Open Problems pages (dwest.web.illinois.edu/openp), Barbados Graph
Theory Workshop lists 2024–2026 (web.math.princeton.edu/~pds/barbados26/problems.pdf), Dan
Archdeacon's *Problems in Topological Graph Theory*, Bondy–Murty unsolved problems appendix,
Open Problem Garden, and follow-up literature checks (arXiv, journals) for status as of July 2026.

**Scoring:** Obscurity 1–5 (5 = essentially untouched by modern compute), Tractability 1–5
(5 = a witness at reachable size is plausible and cheap to verify). All problems below were
verified still open as of July 2026 via recent literature; none appear on the teorth/erdosproblems
AI-contributions ledger (that wiki covers Erdős-numbered problems; these classic-collection
problems are outside its scope, which itself is evidence of low AI attention).

---

## 1. Sheehan's conjecture (uniquely Hamiltonian 4-regular graphs)

- **Statement.** Every Hamiltonian 4-regular *simple* graph has at least two Hamiltonian cycles.
  Equivalently: no 4-regular simple graph is uniquely Hamiltonian.
  Source: J. Sheehan, "The multiplicity of Hamiltonian circuits in a graph," in *Recent Advances
  in Graph Theory* (Proc. Symp. Prague 1974), 1975. Listed in Bondy–Murty, *Graph Theory* (GTM
  244), unsolved problems appendix (#57-adjacent block on Hamiltonian cycles); Open Problem
  Garden: https://www.openproblemgarden.org/op/uniquely_hamiltonian_graphs
- **Provenance/importance.** By Petersen's theorem plus results of Thomassen (odd r) and
  Haxell–Seamone–Verstraëte (even r > 22), Sheehan's r=4 case is THE remaining case of "no
  r-regular graph (r>2) is uniquely Hamiltonian." Central in the Hamiltonian-cycle-counting
  community (Thomassen, Fleischner, Zamfirescu).
- **Status/frontier.** Verified for all 4-regular graphs up to **n = 21** (Goedgebeur, Meersman,
  Zamfirescu, "Graphs with few hamiltonian cycles," Math. Comp. 2020; and SIAM J. Discrete Math.
  2022, doi:10.1137/21m1414048). Girão–Kittipassorn–Narayanan settled it asymptotically (second
  cycle of length ≥ n − cn^{4/5}), so a counterexample, if any, is *small-to-medium*. Multigraph
  counterexamples exist (Fleischner), showing tightness of the simplicity hypothesis.
- **Finite witness.** A single 4-regular simple graph with exactly one Hamiltonian cycle.
  Verification: exact Hamiltonian cycle count (DP/ILP/#SAT) — seconds for n ≤ 40.
  Estimated witness size: n in 22–50 if it exists.
- **Attack.** (a) Direct search seeded from Fleischner's uniquely-Hamiltonian multigraphs and
  Entringer–Swart near-4-regular uniquely Hamiltonian graphs (two vertices of degree 4 known);
  local moves preserving 4-regularity, objective = number of Hamiltonian cycles. (b) SAT-modulo-
  symmetries encoding "4-regular + exactly one HC" (cardinality-one over cycle variables via
  incremental blocking).
- **Obscurity: 4** — known to specialists, absent from popular lists; last compute push 2020–22
  stopped at n=21 by exhaustive generation, not by targeted heuristic search.
- **Tractability: 4** — cheap verifier, strong near-miss seeds, asymptotic result confines the
  search window.

## 2. Gallai's three-longest-paths question (Zamfirescu's conjecture)

- **Statement.** In every connected graph, any three longest paths share a common vertex.
  Source: T. Gallai, Problem 6, in *Theory of Graphs* (Proc. Colloq. Tihany 1966), Academic
  Press 1968, p. 362 (Gallai asked about all longest paths; the 3-path version is due to
  T. Zamfirescu, 1980s). Open Problem Garden:
  https://openproblemgarden.org/op/do_any_three_longest_paths_in_a_connected_graph_have_a_vertex_in_common
- **Provenance/importance.** Gallai's original question (all longest paths) was answered
  negatively (Walther 1969, hypotraceable graphs); Skupień gave 7 longest paths with empty
  intersection. Whether **3** suffice is the surviving open case, a benchmark problem in
  longest-path structure theory (Axenovich, de Rezende–Fernandes–Martin–Wakabayashi).
- **Status/frontier.** Open. Known true for outerplanar graphs, graphs whose nontrivial blocks
  are Hamiltonian, series-parallel graphs. Computation: any *polyhedral* counterexample needs
  ≥ 18 vertices (Brown, PhD thesis, Univ. of Canterbury 2025, doi:10.26021/15960, using plantri).
  General small-graph exhaustive frontier is much lower (~n≤12 folklore); no SAT-based attack
  in the literature.
- **Finite witness.** One connected graph plus three explicit longest paths with empty common
  intersection. Verification: compute longest path length (exact DP/ILP feasible to n≈60 for
  sparse graphs), check the three paths attain it and share no vertex.
- **Attack.** Direct search over structured candidates: known counterexamples for 7 paths come
  from hypotraceable graphs (Thomassen's 34-vertex graph); mutate/hybridize hypotraceable and
  near-hypotraceable graphs, objective = min over vertex of number-of-longest-paths-through-it.
  Also SMS/SAT for "3 vertex-disjoint-intersection longest paths" at fixed n and path length.
- **Obscurity: 3** — moderately known in the paths-and-cycles community, but compute attacks
  are rare and recent (one 2025 thesis restricted to polyhedral graphs).
- **Tractability: 3** — longest-path certification is NP-hard in general (bounds the graph size
  we can verify), but the 7-path counterexamples suggest structured families to interpolate.

## 3. Hajós' conjecture on cycle decompositions of Eulerian graphs

- **Statement.** Every simple Eulerian graph on n vertices decomposes into at most ⌊(n−1)/2⌋
  edge-disjoint cycles. Source: attributed to G. Hajós, stated in L. Lovász, "On covering of
  graphs," in *Theory of Graphs* (Tihany 1966), 1968. (Distinct from the famous Hajós
  topological-K5 conjecture.)
- **Provenance/importance.** The Eulerian analogue of the Erdős–Gallai/Gallai path-decomposition
  problems; implies the small cycle double cover conjecture (#4 below) for Eulerian graphs.
  Actively cited in the decomposition community (Fan–Xu, Girão–Granet–Kühn–Osthus partial
  results for large n via absorption).
- **Status/frontier.** Open. Proved for max degree ≤ 4 (Granville–Moisiadis), planar (Seyffarth),
  projective-planar / K6-minor-free (Fan–Xu 2002), pathwidth ≤ 6 (Fuchs–Gellert–Heinrich 2020).
  **Verified exhaustively only up to n = 12** (Heinrich–Natale–Streicher, "Hajós' cycle
  conjecture for small graphs," arXiv:1705.08724, 2017 — ILP + heuristics). For large n,
  Girão et al. proved an O(n) bound, not (n−1)/2.
- **Finite witness.** A single Eulerian graph whose minimum cycle decomposition size exceeds
  ⌊(n−1)/2⌋. Verification: minimum cycle-decomposition ILP (or exhaust); the same 2017-era ILP
  machinery verifies a candidate in minutes for n ≤ 20.
- **Attack.** LP/ILP gap search in DGG style: generate dense Eulerian graphs (degree-6+ vertices
  are required in a minimum counterexample per Fuchs–Gellert–Heinrich lemmas), score =
  (min decomposition size) − ⌊(n−1)/2⌋ via ILP with column generation; anneal over graph space.
  A counterexample must be 3-connected, δ ≥ 6, and have few degree-4 vertices — strong pruning.
- **Obscurity: 4** — overshadowed by its famous namesake; exactly one small-graph compute paper
  (2017, n ≤ 12) and nothing since.
- **Tractability: 3** — verification ILP is nontrivial but standard; frontier n=12 is very low,
  so even a negative push to n=14 is publishable-adjacent.

## 4. Bondy's small cycle double cover (SCDC) conjecture

- **Statement.** Every simple bridgeless graph on n vertices has a cycle double cover using at
  most n − 1 cycles. Source: J.A. Bondy, "Small cycle double covers of graphs," in *Cycles and
  Rays* (Kluwer 1990), pp. 21–40. Also in Bondy–Murty GTM 244 unsolved problems appendix.
- **Provenance/importance.** Strengthening of the Cycle Double Cover Conjecture; even assuming
  CDCC, the *size* bound is open. Community: cycle-cover school (Zhang's monograph devotes a
  section). K_n needs exactly n−1 cycles, so the bound is tight.
- **Status/frontier.** Open. Known for 4-connected planar graphs (Seyffarth), triangulations,
  complete/complete-bipartite graphs, various line graphs (Klimmek; MacGillivray–Seyffarth,
  Australas. J. Combin. 24 (2001) 91–114). No exhaustive small-graph verification is published
  at all — the verification frontier is essentially empty.
- **Finite witness.** A bridgeless graph where every CDC has ≥ n cycles. Verification is a
  finite (if expensive) check: ILP/#SAT over cycle space, minimize number of cycles subject to
  double-cover constraints. Witness likely small (n ≤ 20) if it exists among sparse graphs with
  many triangles forced.
- **Attack.** ILP min-#cycles-CDC oracle + annealed graph search maximizing (min CDC size − n).
  Cubic graphs are natural first hunting ground (CDC size ≤ n/2 known for planar 2-connected
  cubic, arXiv:2506.10604 (2025) — so hunt in *nonplanar* cubic + dense chordal-ish graphs).
- **Obscurity: 4** — cited steadily but nobody has even published an n ≤ 12 exhaustive check.
- **Tractability: 2** — counterexample would contradict a widely-believed strengthening pattern;
  min-CDC ILP is heavy. Value is mostly in frontier-pushing.

## 5. Brandt's regular supergraph conjecture (dense maximal triangle-free graphs)

- **Statement.** If G is maximal triangle-free with δ(G) ≥ n(G)/3, then G has a regular
  triangle-free supergraph obtainable from G by vertex multiplications (expanding vertices into
  independent sets inheriting neighborhoods). Source: S. Brandt, "A 4-colour problem for dense
  triangle-free graphs," Discrete Math. 251 (2002) 33–46; listed on West's open problems page:
  https://dwest.web.illinois.edu/openp/regsup.html
- **Provenance/importance.** Was the proposed route to "δ > n/3 triangle-free ⇒ 4-colorable."
  That coloring statement was later PROVED (Brandt–Thomassé: every such maximal graph is a
  blow-up of an Andrásfai or Vega graph), but the *regular supergraph* statement — note it
  allows equality δ = n/3 — is not resolved by Brandt–Thomassé and still sits open on West's
  list (checked July 2026; no resolution found in literature).
- **Status/frontier.** No computational attack in the literature whatsoever. The δ = n/3
  boundary cases (where Brandt–Thomassé structure may fail) are the interesting zone.
- **Finite witness.** A single maximal triangle-free graph G with δ ≥ n/3 such that no vertex
  multiplication yields a regular triangle-free graph. Deciding "no multiplication works"
  reduces to an integer feasibility problem: find multiplicities x_v ≥ 1 with
  Σ_{u∈N(v)} x_u = d (constant) for all v — an ILP with n variables; infeasibility certificate
  = LP duality/Farkas or small-range exhaustion.
- **Attack.** Enumerate maximal triangle-free graphs with δ ≥ n/3 (nauty/triangle-free
  generation, feasible to n≈25 with δ-pruning); for each, test ILP feasibility of the
  multiplication system. Any infeasible instance is a counterexample.
- **Obscurity: 5** — a single-author conjecture living only on West's page and one paper;
  zero recorded compute.
- **Tractability: 4** — the whole pipeline (generation + tiny ILP) is a weekend of compute;
  either a counterexample or a clean verified frontier to n≈25.

## 6. Double-critical graph conjecture, first open case k = 6 (Erdős–Lovász)

- **Statement.** If G is connected and χ(G − x − y) = χ(G) − 2 for every edge xy, then G is
  complete. Source: P. Erdős, Problem 2, in *Theory of Graphs* (Tihany 1966), 1968 (with
  Lovász; the s=2 case of the Erdős–Lovász Tihany conjecture). On West's list ("Lovász Doubly
  Critical Graph Conjecture," dwest.web.illinois.edu/openp).
- **Provenance/importance.** The most approachable case of Erdős–Lovász Tihany; a
  counterexample would be spectacular, and the first open case is very concrete.
- **Status/frontier.** Proved for χ ≤ 5 (Stiebitz 1987). **Open for χ = 6.** Partial: every
  double-critical 6-,7-,8-chromatic graph has a K6/K7/K8-minor resp. (Kawarabayashi–Pedersen–
  Toft 2010; Albar–Gonçalves); claw-free cases settled (Rolek–Song et al.). (A 2022 paper
  claiming a full proof, doi:10.1142/s1793830922501336, is not accepted by the community —
  the conjecture is still listed open in 2024–2026 literature; treat with care and re-verify.)
- **Finite witness.** A non-complete 6-chromatic double-critical graph. Verification: χ and
  χ(G−x−y) for all edges — trivial SAT/DSATUR checks.
- **Attack.** SAT-modulo-symmetries: encode "χ(G) ≥ 6" (no 5-coloring), "G−x−y 4-colorable for
  every edge," "G ≠ K6, no K6 subgraph" at fixed n = 10…16. Known constraints (min degree ≥ 6,
  no two adjacent low-degree vertices, connectivity ≥ 6) prune hard. This is precisely the
  shape of problem where SMS (Kirchweger–Szeider) shines and has never been applied.
- **Obscurity: 3** — known conjecture, but the k=6 finite search angle is untouched by
  modern SAT.
- **Tractability: 3** — witness (if any) may be larger than SAT range; but exhaustive "no
  counterexample to n=15" would itself be a new result.

## 7. Negami's planar cover conjecture ⇔ K_{1,2,2,2} has no finite planar cover

- **Statement.** A connected graph has a finite planar cover iff it embeds in the projective
  plane. Source: S. Negami, "The spherical genus and virtually planar graphs," Discrete Math.
  70 (1988) 159–168. Equivalent (Archdeacon, Fellows, Hliněný, Negami) to: **K_{1,2,2,2} has no
  finite planar cover.** Featured in Archdeacon's *Problems in Topological Graph Theory* and
  Hliněný's survey "20 years of Negami's planar cover conjecture" (Graphs Combin. 26 (2010)).
- **Provenance/importance.** THE central open problem of the covering-graphs subfield of
  topological graph theory; 35+ years, ~15 papers, reduced to one concrete 7-vertex graph.
- **Status/frontier.** Open. Fold number of a planar cover must be even (Archdeacon–Richter);
  recent: no n-fold planar cover of K_{1,2,2,2} exists for **n < 14** (Graphs and Combinatorics,
  2025, doi:10.1007/s00373-025-02983-w); minimal planar cover must be 4-connected
  (arXiv:2412.19560). So the first open case is 14-fold: a planar graph on 7·14 = 98 vertices.
- **Finite witness.** To *disprove* the conjecture: a concrete finite planar graph + covering
  map onto K_{1,2,2,2}. Verification: check covering (local bijection) + planarity — instant.
- **Attack.** Structured construction/SAT: search 14-fold covers = assignments of a permutation
  in S_14 to each of the 12 edges of K_{1,2,2,2} (voltage-graph style), subject to planarity of
  the derived graph; use symmetry of the octahedron+apex, SAT encoding of planarity via
  forbidden K5/K3,3 minors is hard, but incremental planarity check inside a DPLL-style search
  over voltage assignments is feasible; also local search over voltages scoring genus of the
  derived graph (minimize genus → 0).
- **Obscurity: 3** — well known within topological graph theory, invisible outside; compute so
  far is bespoke case analysis, not modern search.
- **Tractability: 2** — most experts believe no cover exists (so witness search may be hunting
  a ghost); but the voltage-search formulation has genuinely never been machine-attacked, and
  a genus-minimizing search is cheap to run.

## 8. Harary–Kainen–Schwenk conjecture, first open cases: cr(C8 × C8) etc.

- **Statement.** cr(C_m □ C_n) = (m−2)n for all n ≥ m ≥ 3. Source: F. Harary, P.C. Kainen,
  A.J. Schwenk, "Toroidal graphs with arbitrarily high crossing numbers," Nanta Math. 6 (1973)
  58–67. Prominent in Archdeacon's *Problems in Topological Graph Theory* (crossing numbers
  section) and the Clancy–Haythorpe–Newcombe survey (arXiv:1901.05155).
- **Provenance/importance.** The oldest crossing-number conjecture for graph products; drove
  the development of arrangement/tile methods (Adamsson–Richter, Salazar).
- **Status/frontier.** Proved for m ≤ 7 (all n) and for n ≥ m(m+1) (Glebsky–Salazar 2004).
  **Open window: 8 ≤ m ≤ n < m(m+1)** — a *finite* family for each m; first open case
  cr(C8 × C8) (conjectured 6·8 = 48). No published computational drawing search below the
  conjectured value; upper-bound drawings achieving (m−2)n are classical.
- **Finite witness.** To disprove: a drawing of C8 × C8 (64 vertices, 128 edges) with ≤ 47
  crossings. Verification: count crossings of an explicit drawing — trivial.
- **Attack.** Direct search with crossing-minimization heuristics (QuickCross, star-insertion
  ILP, planarization heuristics) on C8×C8 … C10×C10; also SAT-based book/page drawing encodings.
  Modern crossing minimizers have never been reported on this family's open cases.
- **Obscurity: 3**; heavily cited but the open cases sit untouched since 2004.
- **Tractability: 3** — heuristic drawing search is cheap; conjecture is likely true, but even
  matching-value certified lower bounds for C8×C8 (via ILP lower-bounding) would be new.

## 9. Zarankiewicz's conjecture, smallest unsettled cases K_{7,11} and K_{9,9}

- **Statement.** cr(K_{m,n}) = ⌊m/2⌋⌊(m−1)/2⌋⌊n/2⌋⌊(n−1)/2⌋. Source: K. Zarankiewicz, "On a
  problem of P. Turán concerning graphs," Fund. Math. 41 (1954) 137–145. Bondy–Murty appendix;
  DIMACS-era crossing number program.
- **Provenance/importance.** The flagship bipartite crossing number problem (Turán's brick
  factory). Kleitman proved m ≤ 6; Woodall (J. Graph Theory 17 (1993) 657–671) machine-verified
  K_{7,7} and K_{7,9} via cyclic-order graphs. **Smallest unsettled: K_{7,11} and K_{9,9}** —
  unchanged since 1993(!).
- **Status/frontier.** de Klerk–Maharry–Pasechnik–Richter–Salazar (SIAM J. Discrete Math 2006)
  gave SDP lower bounds ~0.83 of conjectured value asymptotically. The specific instances
  K_{7,11} (conjectured cr = 225) and K_{9,9} (conjectured 256) have seen no published attack
  with modern SAT/ILP/SDP in 30 years.
- **Finite witness.** To disprove: an explicit drawing of K_{7,11} with ≤ 224 crossings (or
  K_{9,9} ≤ 255). Verification: count crossings — instant. To settle positively: exhaust
  cyclic-order structures (Woodall's method) with modern hardware + symmetry breaking —
  plausibly now feasible for K_{7,11}.
- **Attack.** Two-pronged: (a) heuristic drawing search (QuickCross/simulated annealing over
  2-page and cylindrical drawings) hunting a sub-Zarankiewicz drawing; (b) resurrect Woodall's
  cyclic-order-graph shortest-path bound with 2026 compute + SAT. Either outcome is a result.
- **Obscurity: 2** — famous conjecture, but the *specific frozen instances* are obscure as
  computational targets (no attempts since 1993).
- **Tractability: 4** — verifier is trivial; Woodall's method is documented and was at the
  edge of 1993 hardware; 30 years of Moore's law + SAT is a big hammer.

## 10. Woodall's conjecture on packing dijoins (unweighted)

- **Statement.** In every finite digraph, the minimum size of a (nonempty) dicut equals the
  maximum number of pairwise disjoint dijoins. Source: D.R. Woodall, "Menger and König
  systems," in *Theory and Applications of Graphs* (LNM 642, Springer 1978) 620–635.
- **Provenance/importance.** The planar-dual/directed counterpart of Lucchesi–Younger; one of
  the central open min-max questions in combinatorial optimization (Cornuéjols–Guenin,
  Abdi–Cornuéjols et al. 2023–2025 papers). The weighted version (Edmonds–Giles) is FALSE
  (Schrijver 1980) — so the unweighted conjecture is exactly the DGG shape: an LP-style min-max
  that might fail on a small concrete instance.
- **Status/frontier.** Open even for τ = 3 in general digraphs (partial: ρ-based results,
  Abdi–Cornuéjols–Zlatin 2023). True for source-sink connected digraphs (Schrijver), planar
  digraphs (by Lucchesi–Younger duality). Known Schrijver/Cornuéjols-style weighted
  counterexamples are tiny (≤ 10 arcs) — the unweighted analogue search space is very
  concrete. No published large-scale ILP search for unweighted counterexamples.
- **Finite witness.** A digraph with min dicut τ but max dijoin packing ≤ τ − 1. Verification:
  min dicut = flow computation; max disjoint dijoins = small ILP (partition arcs into τ sets
  each meeting every dicut). Witness likely ≤ 30 arcs if it exists.
- **Attack.** DGG playbook verbatim: enumerate/anneal small digraphs (start from perturbations
  of Schrijver's weighted counterexample, replacing weights by parallel subdivided arcs —
  subdivision changes dicut structure, which is exactly where intuition fails); score =
  τ − (ILP max packing). LP relaxation of packing is exact by Lucchesi–Younger duality
  considerations, so the integrality-gap framing is natural.
- **Obscurity: 3** — famous within combinatorial optimization, unknown outside; compute
  attacks unpublished.
- **Tractability: 4** — tight, cheap ILP loop; expert opinion is genuinely split on truth for
  τ ≥ 4 (Cornuéjols has offered money for τ = 3).

## 11. Murty–Simon conjecture (diameter-2-critical graphs), small-n regime

- **Statement.** Every diameter-2-critical graph on n vertices has at most ⌊n²/4⌋ edges, with
  equality iff G = K_{⌊n/2⌋,⌈n/2⌉}. Source: attributed to Murty and Simon (also Ore 1968,
  Plesník 1975); see Caccetta–Häggkvist, Proc. 9th SE Conf. Combinatorics (1979). Surveyed in
  Haynes–Henning–van der Merwe–Yeo, J. Comb. Optim. 30 (2015) 579–595.
- **Provenance/importance.** Cornerstone of the diameter-critical-graphs community; equivalent
  formulation via total domination in complements powers a decade of papers.
- **Status/frontier.** Proved for **sufficiently large n** (Füredi 1992 — but with a
  tower-type n₀ around 10^10^... via a Ramsey argument), for n ≤ 24 and n = 26 (Fan 1987),
  triangle-free, dominating-edge cases. **Open window: 27 ≤ n < Füredi's astronomically large
  n₀** — a counterexample must be a *specific medium-sized graph*, which nobody has searched
  for with modern tools.
- **Finite witness.** A diameter-2-critical graph with > ⌊n²/4⌋ edges. Verification: diameter,
  edge-criticality, edge count — all trivial polynomial checks.
- **Attack.** Local search / SAT at n = 27…40: maximize edges subject to diam = 2 and
  criticality (every edge's removal creates a distance-3 pair). SAT encoding is compact
  (distance-≤2 via common-neighbor clauses). SMS-style canonical search prunes isomorphs.
- **Obscurity: 3**; well-surveyed, but the "search the gap between Fan's n=26 and Füredi's n₀"
  angle appears computationally untouched since 1987.
- **Tractability: 3** — trivial verifier; but most experts believe it's true, and the open
  window is unbounded above (still, pushing n=26 → n=40 is a concrete deliverable).

## 12. Antimagic tree conjecture (Hartsfield–Ringel), tree case

- **Statement.** Every tree other than K₂ admits an antimagic labeling: a bijection
  E → {1,…,m} such that all vertex label-sums are distinct. Source: N. Hartsfield, G. Ringel,
  *Pearls in Graph Theory*, Academic Press 1990, pp. 108–109 (conjectured there for all
  connected graphs ≠ K₂; the tree case is the flagship subcase). On West's list
  (Arrangements/labeling section).
- **Provenance/importance.** THE test case of the general antimagic conjecture; 35 years of
  partial results (caterpillars antimagic, trees with ≤ 1 degree-2 vertex, regular graphs
  antimagic — Chang et al.). A counterexample tree would collapse the general conjecture.
- **Status/frontier.** Verified for all trees up to **order 25** (Bereg–Sudborough et al. /
  evolutionary-search paper, GECCO 2023, par.nsf.gov/servlets/purl/10434328). Trees with many
  degree-2 vertices are the hard case (the known partial results all exclude them).
- **Finite witness.** To disprove: a tree + an ILP/SAT infeasibility certificate that no
  antimagic labeling exists. Infeasibility of a bijection-labeling system is certifiable via
  DRAT proof from a SAT solver — machine-checkable.
- **Attack.** SAT/ILP infeasibility hunt over "spider-with-long-legs" and subdivided-star
  trees at n = 26–40 (heuristics fail longest there); or prove feasibility fast and push the
  verified frontier to n = 30+ via the published EA + SAT fallback.
- **Obscurity: 2** — the conjecture is well known in labeling circles; but SAT-certificate
  search for a *negative* witness is unexplored (all prior compute searched for labelings,
  not for infeasible trees).
- **Tractability: 3** — each instance is a clean SAT problem; conjecture very likely true, so
  main value is frontier-pushing plus a small chance of an infeasible sporadic tree.

---

## Ranking summary (obscurity × tractability, DGG-profile fit)

| # | Problem | Obs | Tract | Best attack |
|---|---|---|---|---|
| 5 | Brandt regular supergraph | 5 | 4 | enumerate + ILP feasibility |
| 1 | Sheehan (4-regular uniquely Ham.) | 4 | 4 | seeded local search + #SAT |
| 10 | Woodall dijoins | 3 | 4 | LP/ILP gap search (DGG playbook) |
| 9 | Zarankiewicz K_{7,11}/K_{9,9} | 2 | 4 | drawing heuristics + cyclic-order exhaustion |
| 3 | Hajós cycle decomposition | 4 | 3 | ILP decomposition oracle + anneal |
| 2 | Gallai 3 longest paths | 3 | 3 | hypotraceable-seeded search |
| 6 | Double-critical k=6 | 3 | 3 | SAT-modulo-symmetries |
| 11 | Murty–Simon n≥27 | 3 | 3 | SAT max-edges search |
| 8 | HKS cr(C8×C8) | 3 | 3 | crossing minimizers |
| 12 | Antimagic trees n>25 | 2 | 3 | SAT infeasibility hunt |
| 4 | SCDC (Bondy) | 4 | 2 | min-CDC ILP + search |
| 7 | Negami / K_{1,2,2,2} | 3 | 2 | voltage-assignment planarity search |

**Top 3 recommendation:** #5 (Brandt — essentially zero prior compute, complete pipeline in days),
#1 (Sheehan — sharp frontier n=21, strong near-miss seeds, trivial verifier), #10 (Woodall — the
closest structural match to the DGG success: an exact-min-max conjecture whose weighted version
is already false, attackable with the identical LP-vs-ILP harness).

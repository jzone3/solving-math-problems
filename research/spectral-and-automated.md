# Domain research: Spectral & automated-conjecture graph theory

Slug: `spectral-and-automated`. Researched 2026-07-22.

Scope: surviving open conjectures from Graffiti / "Written on the Wall" (Fajtlowicz),
Graffiti.pc (DeLaViña), AutoGraphiX (Aouchiche–Hansen), spectral conjectures that survived the
Wagner 2021 RL refutations and the Roucairol–Cazenave Monte Carlo / search refutations, and
chemical graph theory index conjectures.

## Key sources

- M. Aouchiche, P. Hansen, *A survey of automated conjectures in spectral graph theory*,
  Linear Algebra Appl. 432 (2010) 2293–2322. doi:10.1016/j.laa.2009.06.015 (also GERAD G-2009-18).
  Catalogs Graffiti conjectures with "Written on the Wall" (WoW) numbering.
- T.L. Brewster, M.J. Dinneen, V. Faber, *A computational attack on the conjectures of Graffiti*,
  Discrete Math. 147 (1995) 35–55 — exhaustively checked ~200 Graffiti conjectures on **all graphs
  with ≤ 10 vertices** (1990s hardware). That is still the exhaustive frontier for most of them.
- A.Z. Wagner, *Constructions in combinatorics via neural networks*, arXiv:2104.14516 (2021) —
  RL (deep cross-entropy) refuted 3 spectral conjectures.
- M. Roucairol, T. Cazenave, *Refutation of spectral graph theory conjectures with Monte Carlo
  Search*, COCOON 2022, arXiv:2207.03343; and *Refutation of Spectral Graph Theory Conjectures
  with Search Algorithms*, IASE/ECAI-workshop 2025,
  https://www.lamsade.dauphine.fr/~cazenave/papers/ConjectureRefutationECAI2025.pdf
  — applied NMCS/LNMCS/NRPA/UCT/GRAVE/RAVE/GBFS/BEAM (15 min budget each, single core,
  graphs up to size 50, exceptionally 100) to **all Graffiti conjectures from the A–H survey whose
  invariants are polynomial-time**. They refuted Graffiti 197 (previously open) and re-refuted 12
  known-refuted ones, but **failed on ~20 open conjectures** — those survivors are Table 1 rows
  marked "O": Graffiti 20, 21, 39, 40, 129, 143, 154, 195, 198, 219, 252, 254, 262, 284, 290, 292,
  295, 322, 698, 712, 714. Their Rust encodings of every invariant are public:
  https://github.com/RoucairolMilo/refutationGBR (src/models/conjectures/GenerateGraph.rs).
- L. Taieb, M. Roucairol, T. Cazenave, A. Harutyunyan, *Automated Refutation with Monte Carlo
  Search of Graph Theory Conjectures on the Maximum Laplacian Eigenvalue* (LION19, 2025) —
  same toolchain applied to 68 automated (AGX-style) λ_max(L) conjectures.

**Verification frontier for the whole Graffiti family**: exhaustive to n ≤ 10 (1995);
non-exhaustive MCTS/greedy search to n = 50 (100 for two of them) with a 15-minute single-core
budget per algorithm (2025). Nobody has run SAT/SMS, ILP, simulated annealing at scale, GPU
eigenvalue pipelines, or LLM-guided structured-family search on the survivors. This is exactly
the "low prior compute" profile in PLAN.md — and this exact pipeline (build graph edge-by-edge,
score = LHS−RHS of the inequality) is the cheapest evaluation loop of any domain.

Invariant definitions used below (Fajtlowicz's, per WoW / Favaron–Mahéo–Saclé, *Some eigenvalue
properties in graphs (Conjectures of Graffiti — II)*, Discrete Math. 111 (1993) 197–220):
- **temperature** of vertex v: t(v) = d(v)/(n − d(v)).
- **dual degree** of v: sum of degrees of v's neighbors divided by d(v) (average neighbor degree).
- **derivative** of a sorted vector: vector of consecutive differences (min derivative = smallest
  spectral gap).
- **gravity matrix**: Gr(G)[u,v] = 0 if u=v, else (1/(n−1))·d(u)d(v)/dist(u,v)
  (WoW p. 52; Brewster–Dinneen–Faber 1995). NB: the A–H survey uses a *different* (erroneous)
  definition — any attack must use the WoW definition (see the erratum in the 2025
  Roucairol–Cazenave paper).
- n⁺(G), n⁻(G): number of positive / negative adjacency eigenvalues.

---

## Candidate 1 — Graffiti 20: number of positive eigenvalues ≤ sum of positive eigenvalues

- **Statement**: For every graph G, n⁺(G) ≤ Σ_{λᵢ>0} λᵢ (i.e. n⁺ ≤ E(G)/2 since positive and
  negative eigenvalue sums are ±E/2). Source: WoW conj. 20; listed open in Aouchiche–Hansen 2010
  survey; open row in Roucairol–Cazenave 2025 Table 1.
- **Provenance/importance**: One of the oldest surviving Graffiti conjectures (1980s); directly
  adjacent to the "square energy" line (min{s⁺,s⁻} ≥ n−1) that generated a flurry of 2024–2026
  papers and was just proved in July 2026 (arXiv:2607.18031) — this sibling inequality is the
  natural next target for that community and is explicitly weaker-frontier.
- **Status/frontier**: exhaustive n ≤ 10 (1995); MCTS to n = 50 (2025), no counterexample.
- **Finite witness**: a single graph with n⁺ > E/2. Verify with one eigendecomposition.
  Estimated witness size if false: 20–200 vertices, likely highly structured (many small positive
  eigenvalues ⇒ complete multipartite-like / Kneser-like spectra).
- **Attack**: direct search (annealing on structured perturbations), structured construction over
  graph joins/blowups whose spectra are computable, plus exhaustive geng to n = 12–13.
- **Obscurity 4**: appears only in the WoW list and the two refutation papers; no dedicated
  literature. **Tractability 5**: one dense eigensolve per candidate; the tightness ratio is a
  perfect smooth score function.

## Candidate 2 — Graffiti 21: number of negative eigenvalues ≤ sum of positive eigenvalues

- **Statement**: For every graph G with ≥ 3 vertices, n⁻(G) ≤ Σ_{λᵢ>0} λᵢ = E(G)/2.
  Source: WoW conj. 21; open row in Roucairol–Cazenave 2025 Table 1 (their Rust encoding
  compares `num_eig_neg` vs `sum_eig_pos`).
- **Provenance**: same family as Candidate 1; together they say the inertia is controlled by
  energy. Related to Elphick–Farber–Goldberg–Wocjan square-energy work (n⁻ large forces s⁺ large).
- **Status/frontier**: exhaustive n ≤ 10; MCTS to n = 50.
- **Finite witness**: one graph with many negative eigenvalues but tiny energy — the tension is
  real for K_n minus structure / strongly-regular-like graphs; single eigensolve verification.
  Estimated size 20–300.
- **Attack**: direct search + structured construction (line graphs, complements of sparse graphs,
  Kneser graphs have n⁻ huge; compute E exactly in closed families before any search).
- **Obscurity 4**: untouched outside WoW + refutation papers. **Tractability 5**: same loop as #1.

## Candidate 3 — Graffiti 39 & 40: deviation of the distance matrix vs inertia

- **Statement (39)**: for every connected G, the standard deviation of the n² entries of the
  distance matrix satisfies dev(D) ≤ n⁺(G). **(40)**: dev(D) ≤ n⁻(G).
  Source: WoW conj. 39, 40; open rows in Roucairol–Cazenave 2025 Table 1 (their code computes
  std-dev over all entries of the distance matrix, adjacency eigenvalue counts on the other side).
- **Provenance**: classic Graffiti "metric vs spectral" pairing; Favaron–Mahéo–Saclé (Discrete
  Math. 111, 1993) worked this family manually and left these open.
- **Status/frontier**: exhaustive n ≤ 10 (1995); MCTS to n = 50 (2025).
- **Finite witness**: a connected graph with large distance-variance but few positive (resp.
  negative) eigenvalues. Long paths/brooms maximize dev(D) but paths have n⁺ ≈ n/2, so the fight
  is real: need diameter ~ n with spectrally degenerate structure. Witness plausibly a tree or
  tree-like graph with 50–500 vertices — MCTS stopped at 50, and dev(D) grows with diameter, so
  **the unexplored regime n > 50 is precisely where a counterexample would live**.
- **Attack**: direct search over trees only (cheap, D computable by BFS), annealing on caterpillars
  /spiders/brooms with parameterized closed-form distance variance; exhaustive over trees to n≈24.
- **Obscurity 5**: no dedicated papers found. **Tractability 4**: needs APSP + eigensolve, still
  milliseconds at n ≤ 500; score is smooth.

## Candidate 4 — Graffiti 143 & 154: eigenvalue dispersion vs average distance

- **Statement (143)**: for connected G with m edges and average inter-vertex distance μ(D),
  Var(positive adjacency eigenvalues) ≤ m/μ(D). **(154)**: std-dev of *all* adjacency eigenvalues
  ≤ n/μ(D). Source: WoW conj. 143, 154; open rows in Roucairol–Cazenave 2025 Table 1 (143 was
  searched to n = 100, 154 to n = 50).
- **Provenance**: Graffiti's "spectral dispersion vs metric compactness" family; note
  std-dev of adjacency eigenvalues = √(2m/n), so 154 is equivalent to the clean inequality
  **2m·μ(D)² ≤ n³** — a crisp, apparently unrecorded extremal statement the community has never
  attacked in this form.
- **Status/frontier**: exhaustive n ≤ 10; MCTS to n = 100 (143) / 50 (154).
- **Finite witness**: one connected graph. For 154 the reformulation makes the search transparent:
  maximize m·μ(D)²/n³. Dumbbells (two cliques + long path) are the natural extremal family and are
  fully parameterized — a 3-parameter closed-form optimization decides the dumbbell family
  instantly, something the edge-by-edge MCTS could not represent at n > 50. Witness size if false:
  likely 100–10,000 (asymptotic regime), still trivially verifiable.
- **Attack**: structured construction first (closed-form over dumbbell/lollipop/kite families at
  arbitrary n), then LP/parameter search; direct search only as fallback.
- **Obscurity 5**: the 2m·μ² ≤ n³ form appears nowhere. **Tractability 5**: candidate families are
  closed-form; verification is one BFS + eigensolve.

## Candidate 5 — Graffiti 712 & 714: temperature vs non-positive spectrum

- **Statement (712)**: for every graph, min_v t(v) ≤ #{i : λᵢ ≤ 0}, where t(v)=d(v)/(n−d(v)).
  **(714)**: −mean(non-positive adjacency eigenvalues) ≤ Σ_v 1/t(v).
  Source: WoW conj. 712, 714; open rows in Roucairol–Cazenave 2025 Table 1 (714 searched to
  n = 100).
- **Provenance**: Fajtlowicz's "temperature" invariants are a signature Graffiti product
  (cf. Fajtlowicz, *On conjectures of Graffiti*, Discrete Math. 72 (1988) 113–118); several
  temperature conjectures fell to Brewster–Dinneen–Faber but these survived 30+ years.
- **Status/frontier**: exhaustive n ≤ 10; MCTS to n = 50/100.
- **Finite witness**: single graph; 712 needs a graph where *every* vertex has degree > n/2·(#
  non-positive eigenvalues)/(1+…) — i.e. very dense graphs with few non-positive eigenvalues; but
  dense graphs have n⁻ ≈ n−ω… the tension suggests near-complete multipartite graphs, an easily
  enumerable family. Witness size 15–100.
- **Attack**: structured construction over complete multipartite + perturbations (their spectra
  are explicit); direct annealed search; exhaustive n ≤ 12.
- **Obscurity 5**: temperature invariants exist only in the Graffiti orbit. **Tractability 5**:
  trivial invariants, one eigensolve.

## Candidate 6 — Graffiti 129 & 698: Laplacian eigenvalue deviation vs Randić index

- **Statement (129)**: for every graph, std-dev of Laplacian eigenvalues ≤ R(G), the Randić index
  Σ_{uv∈E}(d(u)d(v))^{−1/2}. **(698)**: a variant with an L²-type norm of part of the Laplacian
  spectrum ≤ R(G) (per refutationGBR encoding). Source: WoW conj. 129, 698; open rows in
  Roucairol–Cazenave 2025 Table 1.
- **Provenance**: connects two of the most-studied invariants in chemical graph theory (Laplacian
  spread / Randić index) yet has zero dedicated literature; Randić-index lower bounds are a large
  MATCH-journal industry, so a refutation or proof would land in an active community.
- **Status/frontier**: exhaustive n ≤ 10; MCTS to n = 50.
- **Finite witness**: one graph with spread-out Laplacian spectrum (e.g. one huge degree) and tiny
  Randić index — stars have R = √(n−1) and Laplacian dev ~ √n, an O(1) gap: **near-miss family
  already visible**, strongly suggesting a counterexample among star-like graphs with pendant
  structure at moderate n. Estimated witness size 20–200.
- **Attack**: structured construction on double-stars/spiders (closed-form both sides), then
  direct search seeded there.
- **Obscurity 5** / **Tractability 5**: the near-miss family makes this arguably the single most
  promising quick target in this whole domain.

## Candidate 7 — Graffiti 252 & 254: minimum Laplacian spectral gap conjectures

- **Statement (252)**: for connected G, the minimum gap between consecutive sorted Laplacian
  eigenvalues ≤ Σ_v 1/dualdeg(v). **(254)**: min Laplacian gap ≤ Σ_v 1/odd(v), where odd(v) = #
  vertices at odd distance from v. Source: WoW conj. 252, 254; open rows in Roucairol–Cazenave
  2025 Table 1.
- **Provenance**: Graffiti's "derivative of the spectrum" family; minimum spectral gaps are
  notoriously hard to control analytically, which is why these never got proofs — but they are
  perfect for numerical search.
- **Status/frontier**: exhaustive n ≤ 10; MCTS to n = 50.
- **Finite witness**: one connected graph whose Laplacian spectrum has *all* consecutive gaps
  large (≥ RHS). RHS shrinks when dual degrees / odd-distance counts are large, i.e. dense graphs;
  dense graphs tend to have repeated Laplacian eigenvalues (gap 0) — a counterexample needs a
  dense graph with simple, well-separated spectrum. Conference/Paley-like graphs are the obvious
  family (quasi-random, near-simple spectra). Witness size 20–100.
- **Attack**: structured construction (Paley graphs, random dense graphs — check RHS vs known gap
  statistics), then annealing maximizing (min gap − RHS).
- **Obscurity 5**: never studied. **Tractability 4**: gap statistics of random graphs may make
  this provably-true-like; still a cheap loop.

## Candidate 8 — Graffiti gravity-matrix family: 219, 284, 290, 292, 295

- **Statement (representatives)**: with Gr(G) the WoW gravity matrix (definition above):
  - **219** (triangle-free G): λ₂(Gr(G)) ≤ n(n−1)/2 − m.
  - **292 / 295** (girth ≥ 5): smallest positive adjacency eigenvalue (292), resp. number of
    positive *distance* eigenvalues (295), ≤ n / mean(Gr(G)).
  - **284, 290** (girth ≥ 5): related gravity bounds (290 is the one whose status flips depending
    on which gravity definition is used — resolved erratum in Roucairol–Cazenave 2025 §5.2).
  Source: WoW conj. 219, 284, 290, 292, 295; open rows in Roucairol–Cazenave 2025 Table 1.
- **Provenance**: the gravity matrix is a Fajtlowicz invention studied only in
  Brewster–Dinneen–Faber 1995; whole sub-family untouched for 30 years partly because the
  definition itself got garbled in the A–H survey.
- **Status/frontier**: exhaustive n ≤ 10 (1995, with correct definition); MCTS to n = 50 (2025,
  but note the 2022 run of some of these used the *wrong* gravity definition — effective modern
  frontier is thinner than it looks).
- **Finite witness**: one triangle-free / girth-5 graph; girth constraints make SAT-modulo-
  symmetries (Kirchweger–Szeider SMS) genuinely applicable for exhaustive small-n sweeps, which
  nobody has done. Witness size 15–60.
- **Attack**: SAT/SMS exhaustive for triangle-free/girth-5 up to n≈25 with eigenvalue check as
  oracle, plus incidence-graph/generalized-polygon constructions (extremal girth-5 graphs).
- **Obscurity 5**: maximal — even the definition is nearly lost. **Tractability 3**: girth
  constraints shrink the space but the double definitional ambiguity requires care (must re-check
  both definitions against WoW p. 52 before any run).

## Candidate 9 — Fajtlowicz's Randić-index conjectures: R ≥ r − 1 and R ≥ ad(G)

- **Statement**: (a) For every connected graph, R(G) ≥ r(G) − 1 where r is the radius
  (Fajtlowicz 1988, Graffiti; see S. Fajtlowicz, *On conjectures of Graffiti*, Discrete Math. 72
  (1988) 113–118). Caporossi–Hansen (AGX) conjectured the stronger R(G) ≥ r(G) for all connected
  graphs except even paths. (b) R(G) ≥ ad(G), the average distance (also Fajtlowicz 1988).
- **Provenance/importance**: the Randić index is *the* central invariant of chemical graph theory;
  these are the flagship surviving Graffiti conjectures in that community (dozens of MATCH/Filomat
  papers chip at them).
- **Status/frontier**: (a) proved for chemical graphs (Δ ≤ 4) by Cygan–Pilipczuk–Škrekovski,
  MATCH Commun. Math. Comput. Chem. 67 (2012) 451–466; for unicyclic/bicyclic and cyclomatic
  number ≤ 5 (Liu–Gutman, MATCH 62 (2009) 143–154); cactus graphs (arXiv:2107.00071); general
  case open. Best general bounds leave a constant-factor gap (e.g. Deng–Tang–Zhang, Filomat 29
  (2015) 6). (b) proved for trees (Cygan–Pilipczuk–Škrekovski 2011); general case open.
  No evidence of any modern metaheuristic/SAT compute ever aimed at a counterexample — all effort
  has gone into proofs.
- **Finite witness**: one connected graph with R < r − 1 (resp. R < ad). Needs Δ ≥ 5 and huge
  radius with tiny Randić index — vertex-heavy "theta/spider of long subdivided legs with dense
  hubs" families. Witness, if it exists, plausibly 50–1000 vertices; verification trivial.
- **Attack**: LLM-guided structured families + annealing over degree sequences with subdivisions
  (R and r are both closed-form on parameterized spiders/theta graphs); AGX-style variable
  neighborhood search was only ever run as *support* for the conjecture, not at scale against it.
- **Obscurity 3**: known in chemical graph theory, unknown outside. **Tractability 4**:
  invariants are trivial to compute; the risk is that it is simply true (partial results are
  strong), but the Δ ≥ 5 regime is genuinely unexplored.

## Candidate 10 — Bollobás–Nikiforov conjecture

- **Statement**: for every non-complete graph G with m edges and clique number ω,
  λ₁(G)² + λ₂(G)² ≤ 2m(1 − 1/ω). Source: B. Bollobás, V. Nikiforov, *Cliques and the spectral
  radius*, J. Combin. Theory Ser. B 97 (2007) 859–865, Conjecture 1.
- **Provenance**: the central open "spectral Turán" strengthening; active community
  (Lin–Ning–Wu proved the triangle-free case, Combin. Probab. Comput. 30 (2021); complete
  multipartite & dense K₄-free cases 2026, arXiv:2603.26379; holds a.a.s. for random graphs,
  arXiv:2501.07137; "not so many triangles" case, arXiv:2407.19341).
- **Status/frontier**: verified in many classes and asymptotically a.a.s.; **no published
  large-scale numerical counterexample search** — all compute has been incidental. Open as of
  July 2026.
- **Finite witness**: one graph violating the inequality; both sides computable in ms (ω via
  clique solver, fine to n≈100). Expert consensus leans true, but the λ₂ term is loose in known
  proofs — a violation, if any, would be a dense graph with two large eigenvalues, e.g. two
  near-cliques sharing structure; witness size 20–80.
- **Attack**: direct search (annealing over dense graphs, score = LHS−RHS with exact ω from a
  MaxClique ILP); Kneser/quasi-random structured families.
- **Obscurity 2**: well known in spectral graph theory (though invisible outside).
  **Tractability 5**: the evaluation loop is as cheap as Wagner's refuted conjectures, and this
  is the highest-prestige target with such a cheap loop.

## Candidate 11 — Brouwer's conjecture on Laplacian eigenvalue partial sums

- **Statement**: for every graph G with m edges and Laplacian eigenvalues μ₁ ≥ … ≥ μₙ, for every
  1 ≤ t ≤ n: Σ_{i=1}^t μᵢ ≤ m + t(t+1)/2. Source: A.E. Brouwer, W.H. Haemers, *Spectra of Graphs*,
  Springer 2012, §3.2 (conjectured 2006).
- **Provenance**: the standing "Grone–Merris–Bai analogue" (Grone–Merris was proved by Bai 2011);
  very active: proved for t=1,2,n−1,n, trees, split/cographs; 2025–2026 wave includes
  arXiv:2503.11165, 2606.12197, 2607.03388 ("full Brouwer"), 2607.08452, 2607.17293 —
  still open in general as of July 2026.
- **Status/frontier**: exhaustively verified for n ≤ 10 (Brouwer, via computer); classes above.
  No reported modern metaheuristic attack on the middle-t regime (t ≈ n/2 dense graphs), where
  the inequality is tightest.
- **Finite witness**: a graph + index t with the sum exceeding m + t(t+1)/2; instant verification.
  If false, witness likely 15–60 vertices, dense, near split-graph threshold structure.
- **Attack**: direct annealed search on score max_t(Σμᵢ − m − t(t+1)/2); structured perturbations
  of threshold/split graphs (which achieve equality); exhaustive n ≤ 12.
- **Obscurity 2**: prominent within spectral graph theory. **Tractability 5**: single eigensolve,
  built-in tightness certificate (equality cases known), perfect smooth score.

## Candidate 12 — Surviving AGX λ_max(Laplacian) conjectures from Taieb et al. 2025

- **Statement (family)**: Taieb–Roucairol–Cazenave–Harutyunyan (LION 2025; T&F preprint
  lamsade.dauphine.fr/~aharutyunyan/TaylorFrancisDisproofSpectralConjectures.pdf) attacked 68
  automated conjectures on μ₁ = λ_max(Laplacian) of the form μ₁ ≤/≥ f(invariants) (the
  Aouchiche–Hansen AGX corpus, *A survey of automated conjectures in spectral graph theory* §
  Laplacian, and GERAD G-2012-27 *Open problems on graph eigenvalues studied with AutoGraphiX*).
  A subset resisted all their searches — the exact surviving IDs are enumerated in their Table
  (paper + code public); each survivor is an independent finite-witness target.
- **Provenance**: AGX conjectures are the second big automated-conjecture corpus; Aouchiche–Hansen
  explicitly published them as open problems to the community.
- **Status/frontier**: the 2025 MCTS sweep (graphs to n≈50, minutes/conjecture) is the *only*
  compute ever aimed at most of them.
- **Finite witness**: one graph per conjecture; μ₁ + elementary invariants, ms verification.
- **Attack**: re-run their open list with (i) much larger n, (ii) annealing/ILP over structured
  families, (iii) LLM-guided proposals; their Rust scoring code can be reused directly.
- **Obscurity 4**: corpus known, individual conjectures anonymous. **Tractability 4**: need to
  first extract the precise surviving list from the paper's table (curation step), then the loop
  is trivial.

---

## Verified-resolved (checked July 2026 — do NOT select)

- **Elphick–Farber–Goldberg–Wocjan square-energy conjecture** min{s⁺,s⁻} ≥ n−1: **proved**
  July 2026 (Liu–Tang–Zhang, arXiv:2607.18031).
- **Graffiti 197**: refuted (C₁₇) by Roucairol–Cazenave 2025; **Graffiti 137, 139, 29, 30, 289,
  301, 302, 321, 166, 189, 711, 715**: previously refuted; **140**: refutation attributed to
  Favaron but source lost — status murky, avoid.
- **Graffiti 322 vs 197 definitional pair**: one of the two is refuted depending on the "range"
  definition — avoid 322 unless the original WoW definition is recovered.
- **Stevanović's Nordhaus–Gaddum conjecture** for λ₁(G)+λ₁(Ḡ): **resolved** June 2025
  (Cheng–Weng, arXiv:2506.11401). The related A–H AGX NG-conjectures should be re-checked
  individually against this paper before selection.
- **Spread conjecture** (Gregory–Hershkowitz–Kirkland / AGX Problem): proved for large n, and the
  **bipartite spread conjecture disproved**, by Breen–Riasanovsky–Tait–Urschel (2022).
- **Wagner 2021 targets**: A–H conjectures 2.1, 2.3 and the Brualdi–Cao problem are refuted;
  Roucairol–Cazenave re-refuted them in seconds.

## Domain-level recommendation

Highest expected value per compute: **Candidates 6, 4, 3** (near-miss families visible, n > 50
regime never searched, closed-form structured families the MCTS could not express), then **10/11**
as high-prestige cheap-loop targets, then the gravity family **8** for maximal obscurity with an
SMS-exhaustive angle. All Graffiti candidates share one harness: graph → invariants → score =
LHS−RHS; the refutationGBR Rust code provides reference implementations of every exotic invariant
(temperature, dual degree, gravity matrix) for cross-checking.

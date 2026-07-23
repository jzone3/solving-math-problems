# Domain research: Curated open-problem lists (West, OPG, Bondy–Murty, erdosproblems.com, covering systems / unit fractions)

Researched 2026-07-23. Focus: NEW candidates not duplicating P01–P15 or the 37 candidates already in
`research/*.md`. All statuses checked against July-2026 literature (Exa search over arXiv/journals; the
teorth/erdosproblems metadata dump was cloned and filtered for open problems by tag).

Scoring: **Obscurity** 1–5 (5 = essentially untouched by modern compute), **Tractability** 1–5
(5 = witness plausibly findable at reachable size, cheap verifier), **Headline** 1–5 (5 = would make
serious news in the relevant community).

**Excluded during vetting** (found settled or duplicated):
- Payan's three-chromatic (0,2)-graph problem — solved: arXiv:2607.10125 (2026), "Finite Three-Colourable (0,2)-Graphs Are Bipartite".
- West's "Traversal by Prime Sum" — Hamiltonicity of prime-sum graphs proved by Chen–Fu–Guo, *Graphs Comb.* 37 (2021), doi:10.1007/s00373-020-02241-1.
- Symmetric chain decomposition of L(5,n) — claimed constructions: arXiv:2212.02700 and ECA 2024 (ECA2024_S2A5); next case L(6,n) is open but the L(5,n) verification burden makes it a poor target now.
- Erdős #204 (covering from divisors of n, coprimality condition) — resolved by Adenwalla, INTEGERS 26 (2026) #A52 / arXiv:2501.15170.
- Erdős #313 (primary pseudoperfect) — duplicates `research/number-theory-discrete-geometry.md` #8; Seymour's 2nd Neighborhood / Barnette / Tuza — already in `context/initial-candidates.md`.

---

## 1. Hoffman–Singleton decomposition of K₅₀

- **Statement.** Does the complete graph K₅₀ decompose into 7 edge-disjoint copies of the
  Hoffman–Singleton graph? (HoSi is the unique (7,5)-cage: 7-regular, girth 5, 50 vertices,
  175 edges; 7 × 175 = C(50,2) = 1225, so the arithmetic is exact.)
  Source: Douglas West's open problem pages, http://dwest.web.illinois.edu/openp/hoffsing.html.
- **Why it matters.** The analogous decomposition of K₁₆ into 3 Clebsch graphs is a celebrated
  Ramsey-theoretic gem (proves R(3,3,3)=17 lower bound structure). A HoSi decomposition of K₅₀
  would be the natural next jewel and would immediately enter textbooks on Moore graphs.
- **Openness evidence.** West's page lists it open; best known result remains 5 edge-disjoint
  copies (Meszka–Šiagiová, J. Combin. Des. 2003, doi:10.1002/jcd.10049). Math.SE 69399 (still
  tagged open-problem); no later construction or nonexistence proof found in 2024–2026 searches.
- **Witness / verifier.** 7 permutations of V(K₅₀) mapping a fixed HoSi copy to edge-disjoint
  copies (or 7 explicit edge lists). Verifier: ~20 lines — check each copy is isomorphic to HoSi
  (or just 7-regular girth-5, which forces HoSi) and edges partition K₅₀. Milliseconds.
  Nonexistence: much harder (huge SAT), so treat as a construction hunt.
- **Attack.** Exploit HoSi's automorphism group (PSU(3,5):2, order 252000): search for
  decompositions invariant under a prescribed subgroup (e.g. order 25 or 7) — reduces to a small
  exact-cover/SAT instance; also voltage-graph liftings extending Meszka–Šiagiová's method.
- **Difficulty.** Medium: prescribed-automorphism searches are cheap; the fully asymmetric case is
  out of reach, but historically such decompositions are symmetric when they exist.
- **Scores.** Obscurity 4, Tractability 3, **Headline 5**.

## 2. Chvátal's conjecture on hereditary families — first open case n = 8

- **Statement.** If D is a downset (ideal) of subsets of [n], then some star (all members of D
  containing a fixed element x) is a maximum intersecting subfamily of D.
  Source: Chvátal 1972/1974; his page https://users.encs.concordia.ca/~chvatal/conjecture.html
  (offers a prize); listed under "Order Ideals" on West's pages.
- **Why it matters.** A 50-year-old cornerstone of extremal set theory (sits next to
  Erdős–Ko–Rado and Frankl); Chvátal actively advertises it.
- **Openness evidence.** Open. Verified for ground sets of ≤ 7 elements by exact rational IP with
  Coq-checkable certificates (Eifler–Gleixner–Pulaj, ZIB 18-49; ACM TOMS 2022,
  doi:10.1145/3485630; code: github.com/leoneifler/ChvatalIP). Partial cases: Olarte–Santos–Spreer
  arXiv:1804.03646. No progress on n = 8 found.
- **Witness / verifier.** A counterexample is a single downset D ⊆ 2^[8] (≤ 256 sets) plus an
  intersecting subfamily larger than every star — verifiable in microseconds by brute force.
  Negative direction: settling n = 8 via the existing safe-IP framework is a publishable
  frontier push (the authors stopped at 7 for compute reasons in 2018).
- **Attack.** Rerun/extend ChvatalIP with modern hardware + symmetry breaking (downsets modulo
  S₈); local search / simulated annealing over downsets scoring max-intersecting-minus-max-star
  (both computable exactly per candidate via ILP or DP).
- **Difficulty.** Counterexample unlikely but the search loop is dirt cheap; n = 8 verification is
  a serious but bounded compute project. Lean-formalizable statement (finite, purely set-theoretic).
- **Scores.** Obscurity 3, Tractability 4, Headline 4.

## 3. Laborde–Payan–Xuong conjecture (stable set meeting all longest directed paths)

- **Statement.** Every digraph contains a stable (independent) set that intersects every longest
  directed path.
  Source: Laborde, Payan, Xuong, "Independent sets and longest directed paths in digraphs" (1982);
  Open Problem Garden ✭✭: openproblemgarden.org/op/stable_set_meeting_all_longest_directed_paths.
- **Why it matters.** Would give a clean inductive proof of the Gallai–Roy theorem; a directed
  cousin of the Gallai longest-path problems (complements P05 thematically without overlapping it).
- **Openness evidence.** OPG lists it open; proved only for stability number ≤ 2 (Havet),
  tournaments (Rédei), and locally semicomplete/transitive classes (Galeana-Sánchez–Gómez–
  Montellano-Ballesteros, Discrete Math. 2004–2011). No general progress found through 2026;
  essentially zero recorded compute.
- **Witness / verifier.** A counterexample is one digraph D where max over stable sets S of
  "S hits all longest paths" fails: verifier computes the longest-path length (exhaustive/DP,
  fine for n ≤ 15–18), enumerates longest paths implicitly, and solves a small ILP/SAT: does a
  stable transversal of longest paths exist? Minutes for small n.
- **Attack.** SAT-modulo-symmetries over digraphs on 8–16 vertices (search restricted to
  strongly connected oriented graphs with small stability number ≥ 3, where nothing is known);
  seed with blow-ups of odd cycles and known Gallai-type extremal digraphs.
- **Difficulty.** Low-medium — the double quantifier is small at these orders. Plausibly false:
  the undirected analogue's intuition does not transfer, and experts have no strong belief.
- **Scores.** Obscurity 5, Tractability 4, Headline 3.

## 4. Wide Partition Conjecture (Chow–Taylor), a.k.a. Latin Tableau Conjecture

- **Statement.** A partition λ is *Latin* iff it is *wide*. (λ is Latin if there is a tableau of
  shape λ whose i-th row is a permutation of {1,…,λᵢ} with all columns having distinct entries;
  λ is wide if μ ⪰ μ′ (dominance vs conjugate) for every subpartition μ of λ. Latin ⇒ wide is
  easy; the converse is the conjecture.)
  Source: Chow–Fan–Goemans–Vondrák, Adv. Appl. Math. 31 (2003) 334–358; OPG ✭✭
  openproblemgarden.org/op/wide_partition_conjecture.
- **Why it matters.** It is the "toy case" of Rota's basis conjecture (implied by it for free
  matroids) — refuting it refutes a natural strengthening path to Rota; proving small cases feeds
  the discrete tomography "atom problem" literature (Chile/uchile 2014 reformulation).
- **Openness evidence.** Open; freshly active: Chow–Tiefenbruck, "The Latin Tableau Conjecture,"
  Electron. J. Combin. 32(2) #P48 (published June 2025) reformulates and proves special cases —
  clear evidence it is open and cared about in 2025–26.
- **Witness / verifier.** A counterexample is a single wide-but-not-Latin partition λ.
  Verifier: wideness = check dominance for all subpartitions (fast for |λ| ≤ 60 with pruning);
  non-Latinness = exhaustive/CP/SAT proof that no Latin tableau exists (columns-distinct latin-
  style constraints — a small exact cover). Both directions fully mechanical.
- **Attack.** Enumerate wide partitions in increasing size (they are sparse), test Latinness with
  a CP-SAT model; bias toward the "near-tight" wide partitions where dominance holds with
  equality in many subpartitions (the regime where Rota-style obstructions could live). Prior
  exhaustive checking appears to stop at very small sizes (nothing systematic published) — the
  frontier itself is publishable.
- **Difficulty.** Low to start, unbounded upward. Lean-formalizable (finite combinatorics).
- **Scores.** Obscurity 4, Tractability 4, Headline 4 (headline 5 if false, via Rota linkage).

## 5. Grünbaum's problem: a 4-regular 4-chromatic graph of girth ≥ 6

- **Statement.** Does there exist a 4-regular graph with chromatic number 4 and girth at least 6?
  (Surviving case of Grünbaum's 1970 conjecture — the general form was killed by Johansson's
  O(Δ/log Δ) bound, but small cases like this one are wide open.)
  Source: Grünbaum, Amer. Math. Monthly 77 (1970) 1088–1092; OPG ✭✭
  openproblemgarden.org/op/high_girth_low_degree_4_chromatic_graphs.
- **Why it matters.** Girth-5 examples are famous small graphs (Chvátal, Brinkmann, Grünbaum
  graphs); producing the first girth-6 example (or showing none exists up to n vertices) extends
  a 55-year-old classification effort with named graphs.
- **Openness evidence.** OPG open; MathWorld's Grünbaum Graphs page (checked 2026) still lists
  only girth-5 examples; the MOLGEN group's exhaustive "smallest 4-regular 4-chromatic graphs
  with girth 5" enumeration is the last compute datapoint. No girth-6 example in literature.
- **Witness / verifier.** One graph: check 4-regularity, girth ≥ 6 (trivial), and χ ≥ 4 = UNSAT
  certificate of 3-colorability (DRAT from any SAT solver) — fully machine-verifiable, and
  3-colorability UNSAT proofs are Lean/DRAT-checkable.
- **Attack.** (a) geng/genreg generation of 4-regular girth-6 graphs up to ~40 vertices with
  incremental 3-colorability filtering (most are 3-colorable; hunt the exceptions);
  (b) structured candidates: Cayley graphs, generalized Petersen-like and incidence-geometry
  constructions, vertex-transitive census (girth-6 4-valent graphs start at 26–35 vertices);
  (c) simulated annealing maximizing fractional chromatic number over girth-6 4-regular space.
- **Difficulty.** Medium; the search space is well within nauty range for a first sweep, and any
  exhaustive "no example with ≤ N vertices" is itself a citable frontier.
- **Scores.** Obscurity 4, Tractability 4, Headline 4.

## 6. Mácajová–Škoviera conjecture (two perfect matchings avoiding an odd edge-cut)

- **Statement.** Every bridgeless cubic graph has two perfect matchings M₁, M₂ such that
  M₁ ∩ M₂ contains no odd edge-cut (equivalently, M₁ ∪ M₂-complement behaves so that
  G − (M₁∩M₂) is 5-flowable-adjacent — see OPG for the flow reformulation).
  Source: Mácajová–Škoviera 2005; OPG ✭✭ openproblemgarden.org/op/intersecting_two_perfect_matchings.
- **Why it matters.** Implied by the Fulkerson conjecture and implies the Fan–Raspaud conjecture
  direction of study; it is the weakest open member of the perfect-matching-intersection family
  around cubic graphs/snarks — exactly where SAT-based snark hunting has repeatedly worked
  (cf. recent snark counterexamples to other conjectures by Brinkmann/Goedgebeur pipelines).
- **Openness evidence.** Open; partial results Fouquet–Vanherpe arXiv:0809.4839, Discuss. Math.
  Graph Theory 30 (2010) 315–333 (oddness-2 case). Not covered by the Fan–Raspaud verification
  literature; no exhaustive snark verification published for this specific statement.
- **Witness / verifier.** Counterexample = one cubic graph where for ALL pairs of perfect
  matchings the intersection contains an odd cut. For n ≤ 36 snarks, perfect matchings enumerate
  in milliseconds; odd-cut containment is a small check (cuts = edge-cuts whose sides are odd —
  test via T-join/parity). Full verification per graph is an honest double-exponential but fine
  at snark sizes; ILP formulation also natural.
- **Attack.** Sweep the House-of-Graphs snark census (complete to 36 vertices) — this alone is
  either a counterexample or a new "verified up to 36 vertices" theorem; then targeted
  constructions (dot products of snarks known to nearly-fail Fan–Raspaud).
- **Difficulty.** Low for the census sweep; the census sweep is a guaranteed deliverable.
- **Scores.** Obscurity 4, Tractability 5, Headline 3 (5 if a counterexample — would refute Fulkerson).

## 7. Thomassen's chord conjecture, small-graph frontier

- **Statement.** Every longest cycle in a 3-connected graph has a chord.
  Source: Thomassen 1976; Bondy–Murty (GTM 244) unsolved problems appendix; OPG ✭✭✭
  openproblemgarden.org/op/chords_of_longest_cycles.
- **Why it matters.** One of Thomassen's flagship conjectures; Zhan (Bull. Iran. Math. Soc. 2024,
  doi:10.1007/s41980-024-00909-5) just published a generalization — active in 2024–26.
- **Openness evidence.** Open in general. Proved for planar (Thomassen 2018, "Chords in longest
  cycles in 3-connected graphs", JCTB), cubic, and min-degree-≥4-longest-cycle variants (Harvey,
  EJC 24(4) #P33). No published exhaustive small-order verification found — the computational
  frontier is essentially virgin.
- **Witness / verifier.** Counterexample = graph G + a longest cycle C with no chord. Verifier:
  confirm 3-connectivity, confirm no cycle longer than |C| (exact DP/ILP: fine to n ≈ 20–24,
  #SAT beyond), confirm C is induced. All standard.
- **Attack.** SMS/geng over 3-connected graphs where some longest cycle is induced — encode
  "exists induced cycle of length L, no cycle of length > L" as SAT with incremental L;
  prioritize graphs that are near-bipartite/sparse where chords are scarce. Also exhaustively
  verify n ≤ 14–16 (new theorem, publishable frontier).
- **Difficulty.** Medium (the "no longer cycle" side is the costly part). Counterexample would be
  a major result; frontier push is the realistic outcome.
- **Scores.** Obscurity 2, Tractability 3, Headline 5 (if false) / 2 (frontier push).

## 8. Grünbaum–Nash-Williams conjecture (4-connected toroidal graphs are Hamiltonian)

- **Statement.** Every 4-connected graph embeddable on the torus has a Hamiltonian cycle.
  Source: Grünbaum 1970, Nash-Williams 1973; OPG ✭✭; Wikipedia "Grünbaum–Nash-Williams conjecture";
  Bondy–Murty appendix (Hamiltonicity block).
- **Why it matters.** Torus analogue of Tutte's theorem (4-connected planar ⇒ Hamiltonian);
  the last surface where the 4-connected question is genuinely open (5-connected toroidal is
  Hamiltonian-connected, Kawarabayashi–Ozeki SIDMA 2016; 4-connected toroidal *triangulations*
  are Hamiltonian).
- **Openness evidence.** Open (Wikipedia "unsolved problem" box, 2025 revision); known cases:
  triangulations (Thomas–Yu; Kawarabayashi–Ozeki 2011), graphs with toughness/connectivity extras.
  A counterexample must be a non-triangulation 4-connected toroidal graph — a class nobody has
  computationally enumerated for Hamiltonicity.
- **Witness / verifier.** One graph + a torus embedding (rotation system, Euler genus 1 check) +
  a Hamiltonicity UNSAT certificate (SAT/DRAT or exhaustive DP for n ≤ 30). All finite and clean.
- **Attack.** Generate 4-connected toroidal non-triangulations (surftri/plantri -g1 derivatives,
  or quadrangulation-rich embeddings — quadrangulations are the natural suspects since
  triangulations are settled) and batch-test Hamiltonicity with SAT; seed with toroidal
  grid-like graphs C_m × C_n modifications (known Hamiltonian, but local surgeries may kill it
  while preserving 4-connectivity).
- **Difficulty.** Medium-high (experts lean "true"; but the non-triangulation search space is
  untouched, and "verified for all 4-connected toroidal graphs ≤ n" is new).
- **Scores.** Obscurity 3, Tractability 3, Headline 5 (if false).

## 9. Jones' conjecture (cycle packing vs covering in planar graphs)

- **Statement.** For every planar graph, the minimum feedback vertex set (vertices meeting all
  cycles) is at most twice the maximum number of vertex-disjoint cycles: τ_c(G) ≤ 2·ν_c(G).
  Source: Kloks–Lee–Liu 2002; OPG ✭✭ openproblemgarden.org/op/jones_conjecture.
- **Why it matters.** The planar vertex analogue of Tuza's conjecture; tight for K₅ minus
  structure; drives the integrality-gap literature for disjoint cycles (Schlomberg,
  arXiv:2404.17813 improved the gap in 2024 — active community).
- **Openness evidence.** Open. Known: τ ≤ 3ν always (Chappell–Gimbel–Hartman line), proved for
  outerplanar/Halin+ (Bärnkopf–et al. arXiv:2401.07376, 2024) and for ν ≤ 2. General planar
  case open as of 2024–26 papers' introductions.
- **Witness / verifier.** Counterexample = one planar graph with τ_c > 2ν_c: both quantities are
  small ILPs (exact for n ≤ 60 with CP-SAT/Gurobi); planarity check trivial. Perfect DGG-shape
  "two optimization quantities, search the gap" problem — the exact harness style of
  `initial-candidates.md` #4 (Tuza), but NOT yet in problems/ or research/.
- **Attack.** LP/ILP gap search over planar triangulation-adjacent graphs (plantri generation +
  local mutations maximizing τ−2ν); known extremal families (wheels, K₅-expansions) as seeds.
- **Difficulty.** Low to run; conjecture is believed true but the constant is not known to be
  beatable below 3 — even a planar graph with τ/ν > 2−ε for the LP versions is interesting.
- **Scores.** Obscurity 3, Tractability 4, Headline 4 (if false).

## 10. Erdős #273: a covering system whose moduli are all p−1, p ≥ 5 prime

- **Statement.** Is there a (finite) covering system of the integers all of whose moduli are of
  the form p−1 for primes p ≥ 5 (i.e. moduli from {4, 6, 10, 12, 16, 18, 22, 28, …})?
  Source: Erdős–Graham 1980, p.24; erdosproblems.com/273 (status: open, statement formalized in
  Lean via Google DeepMind Formal Conjectures).
- **Why it matters.** Directly tied to the classical "primitive root / Sierpiński-number"
  covering machinery: Selfridge solved the variant allowing p = 3 using divisors of 360. It is
  the natural sibling of the min-modulus problems (P15) but with a completely different flavor —
  an allowed-moduli-set constraint rather than a size constraint.
- **Openness evidence.** erdosproblems.com marks open (page last edited Oct 2025, 1 comment, no
  claimed proofs); the 2026 Adenwalla paper resolving the neighboring #204 confirms this cluster
  is active yet #273 untouched. Not on the AI-contributions ledger.
- **Witness / verifier.** A finite list of congruences a_i (mod p_i−1); verifier checks every
  residue class mod lcm of moduli is covered and each modulus+1 is prime ≥ 5 — 10 lines, exact,
  instant. **Ideal Lean target** (statement already formalized; a witness gives a `decide`-style
  proof).
- **Attack.** Greedy/exact-cover search mirroring known covering-system construction techniques:
  choose a smooth lcm L (e.g. lcm of many p−1 values dividing 2^a·3^b·5^c·7^d), formulate
  covering as set cover over Z/L with classes from allowed moduli, run ILP/SAT; Selfridge's
  360-based p=3 example is the structural seed. Nonexistence heuristic: density sum Σ1/(p−1)
  over usable moduli diverges, so no obvious obstruction — construction plausibly exists.
- **Difficulty.** Low-medium; exactly the machinery the repo already built for P15.
- **Scores.** Obscurity 4, Tractability 4, Headline 4 (Erdős-problem resolution + Lean witness).

## 11. Erdős #274 / Herzog–Schönheim conjecture, finite-group counterexample search

- **Statement.** Can a group G be partitioned into finitely many (>1) cosets a₁G₁,…,a_kG_k whose
  indices [G:Gᵢ] are pairwise distinct? Herzog–Schönheim (1974) conjecture: no.
  Source: Erdős 1977/Erdős–Graham 1980 p.26; erdosproblems.com/274; Herzog–Schönheim,
  Canad. Math. Bull. 17 (1974).
- **Why it matters.** The group-theoretic generalization of the Mirsky–Newman/Davenport theorem
  (distinct-modulus exact covers of Z don't exist); 50 years old, actively worked
  (Garonzi–Margolis arXiv:2509.25118 settled simple and symmetric groups, Sept 2025; Sun 2004
  did subnormal; abelian case closed).
- **Openness evidence.** Open in general (2025 paper's introduction); erdosproblems.com open.
  A counterexample must be a finite non-solvable-ish group avoiding all settled classes — the
  remaining window is concrete and small-order searchable, and nobody reports a systematic
  GAP sweep.
- **Witness / verifier.** Finite: a group of order n (given by its multiplication table or
  generators), k subgroups with distinct indices, coset representatives; verifier checks the
  cosets partition G — pure finite computation, seconds in GAP or plain Python. Highly
  Lean-formalizable (finite group + explicit partition).
- **Attack.** GAP sweep over the small-groups library (order ≤ 2000, skipping classes covered by
  Sun/Garonzi–Margolis), for each group solve an exact-cover instance over coset systems with
  distinct indices (strong pruning: index sum of reciprocals must equal 1 with distinct terms —
  Egyptian-fraction precondition massively restricts candidate index multisets).
- **Difficulty.** Medium; counterexample considered unlikely, but the settled-classes map makes
  "verified for all groups of order ≤ N" a well-defined new frontier, and the Egyptian-fraction
  index filter is a cute, cheap search.
- **Scores.** Obscurity 3, Tractability 3, Headline 5 (if false; it's a named 50-year conjecture).

## 12. Erdős #317 (second part): signed harmonic sums cannot beat 1/lcm(1..n)

- **Statement.** Is it true that for all sufficiently large n, for every choice δ_k ∈ {−1,0,1},
  if Σ_{k≤n} δ_k/k ≠ 0 then |Σ δ_k/k| > 1/lcm(1,…,n)? (Non-strict is trivial; equality happens
  for small n, e.g. 1/2 − 1/3 − 1/4 = −1/12 = −1/lcm(1..4).)
  Source: Erdős–Graham 1980, p.42; erdosproblems.com/317 (open; only weak progress on part 1 by
  Kovač and van Doorn in comments).
- **Why it matters.** Sits at the heart of the Egyptian-fraction/unit-fraction cluster
  ([ErGr80]'s own favorite chapter); equality cases correspond to exact unit-fraction identities
  hitting the lcm bound — structurally linked to dozens of neighboring problems (#311, #319).
- **Openness evidence.** erdosproblems.com: open, no claimed solutions; comment activity 2025
  gives only a 2^{-n(loglog n/log n)} bound for the companion question — nobody has searched for
  large-n equality cases.
- **Witness / verifier.** A counterexample is a pair (n, δ) with |Σ δ_k/k| exactly 1/lcm(1..n)
  (or any nonzero value ≤ it, impossible except equality) for n beyond a provable threshold —
  one exact-rational check. Also valuable: exhaustively determine ALL equality cases for n ≤ 40
  (2^n·3-ary space but meet-in-the-middle/lattice methods apply) — clean dataset, likely a short
  paper, and equality-case structure may suggest the proof.
- **Attack.** Multiply through by L = lcm(1..n): need Σ δ_k·(L/k) = ±1 with δ ∈ {−1,0,1}ⁿ — a
  signed subset-sum hitting ±1 exactly: LLL/lattice (target vector very short) and
  meet-in-the-middle both natural; p-adic filters (for each prime power ‖L, the δ's on the
  top block are constrained) prune brutally.
- **Difficulty.** Low-medium for the exhaustive small-n frontier; the lattice search scales
  surprisingly far. Fully Lean-witnessable (exact rational arithmetic).
- **Scores.** Obscurity 4, Tractability 4, Headline 3.

---

## Summary table

| # | Problem | Domain | Obs | Tract | Headline | Witness |
|---|---------|--------|-----|-------|----------|---------|
| 1 | Hoffman–Singleton decomposition of K₅₀ | design/graph | 4 | 3 | 5 | 7 edge-disjoint HoSi copies |
| 2 | Chvátal's conjecture, n = 8 | extremal sets | 3 | 4 | 4 | one downset + intersecting family |
| 3 | Laborde–Payan–Xuong | digraphs | 5 | 4 | 3 | one digraph, ILP check |
| 4 | Wide Partition / Latin Tableau | alg. combin. | 4 | 4 | 4 | one partition + UNSAT tableau cert |
| 5 | 4-regular 4-chromatic girth ≥ 6 | coloring | 4 | 4 | 4 | one graph + 3-col UNSAT (DRAT) |
| 6 | Mácajová–Škoviera 2-PM | snarks | 4 | 5 | 3–5 | one cubic graph, PM enumeration |
| 7 | Thomassen chord conjecture | cycles | 2 | 3 | 5/2 | graph + chordless longest cycle |
| 8 | Grünbaum–Nash-Williams toroidal | topological | 3 | 3 | 5 | graph + embedding + Ham-UNSAT |
| 9 | Jones' conjecture (planar τ ≤ 2ν) | packing/covering | 3 | 4 | 4 | planar graph, two ILPs |
| 10 | Erdős #273 covering, moduli p−1 | covering systems | 4 | 4 | 4 | finite congruence list |
| 11 | Herzog–Schönheim (Erdős #274) | group/covering | 3 | 3 | 5 | finite group + coset partition |
| 12 | Erdős #317(b) signed harmonic sums | unit fractions | 4 | 4 | 3 | (n, δ) pair, exact rational check |

**Best DGG-profile picks** (finite witness + cheap loop + low prior compute): #6 (guaranteed
census deliverable), #10 (repo already has P15 machinery + Lean-formalized statement), #3 and #4
(virtually zero prior compute), #1 (highest headline per plausible success).

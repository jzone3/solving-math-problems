# Wave-3 research: NOTABLE open problems with a plausible finite attack

Date: 2026-07-23. Scope per orchestrator prompt: named, community-recognized open problems
(surveys, textbooks, Erdős prize list, OPG-outstanding tier) whose resolution would be genuinely
newsworthy AND which could plausibly be settled by a finite computation, an explicit certificate,
or a short computer-assisted proof. Excluded: Graffiti/WoW/AGX/automated-conjecture corpora
(already mined) and everything in P01–P21.

Every candidate below got a **widened priority check** (arXiv, general web, GitHub, Zenodo,
OpenReview, agentic artifact repos — the demonstrandum/Archivara/Sanexxxx777 ecosystem). Searches
performed and hits found are recorded per candidate. Cross-cutting finding: the agentic-artifact
ecosystem is *very* active in exactly this niche (see §0), so any run on these problems must
re-run the priority check at claim time.

## 0. Agentic-artifact ecosystem status (affects existing catalog too)

- **Demonstrandum** (John Erlbacher; Zenodo DOI 10.5281/zenodo.20673865, 2026-06-13): 5-paper
  bundle incl. the Graffiti 143/154 refutation that scooped P07, a Z.-W. Sun conjecture disproof,
  and a Lean-verified lattice-Borsuk disproof. Actively producing Lean-verified
  counterexamples/records.
- **Archivara** (team): attempted a *proof* of Erdős #7 (odd covering nonexistence) Jan 2026;
  publicly critiqued as flawed (gist by llllvvuu, 2026-01-11:
  https://gist.github.com/llllvvuu/7afe1e1d51cc1f9f6a24644c2d057317). Problem still open, but
  Archivara is circling it.
- **Sanexxxx777/erdos-computational-bounds** (GitHub): LRAT-certified UNSAT bound for **Erdős #273
  = our P18** — "no covering system with distinct moduli p−1 ≤ 50 (p ≥ 5 prime)"; plus verified
  sieve ranges for #385/#647. ⚠ **Action item outside this report: P18 runs must treat the B≤50
  UNSAT bound as prior art.**
- **Arjun Balaji** (Zenodo 10.5281/zenodo.20782738, 2026-06-21): SMS verification of
  Erdős–Gyárfás min-degree-3 up to n=30 (bound 17→31). Directly relevant to candidate C5.
- A crank/LLM-noise layer also exists (e.g. Zenodo "Triadic Validator" claiming Happy Ending
  resolution, 2025-09; Zenodo "A Proof of the Erdős–Gyárfás Conjecture", 2026-01, uncredentialed).
  These do not settle problems but pollute search results; check each hit carefully.

---

## Candidate table (ranked by impact × feasibility)

| # | Problem | Named/prize | Witness type | Feasibility (P(success) in one ultra campaign) |
|---|---------|-------------|--------------|-----------------------------------------------|
| C1 | Erdős #7: odd covering system (Erdős–Selfridge) | $2000 Selfridge / $25 Erdős | explicit finite congruence list (SAT-findable) | 3–8% but enormous payoff; partial results publishable |
| C2 | Erdős–Szekeres ES(7) = 33 (Happy Ending) | textbook-famous, first open case | UNSAT certificate (order types, SAT) | 10–20% for full result via cube-and-conquer; active competition |
| C3 | Conway 99-graph SRG(99,14,1,2) | $1000 Conway prize | one adjacency matrix OR nonexistence | <5% full; structural-subcase eliminations realistic |
| C4 | Hadwiger–Nelson: 6-chromatic unit-distance graph | Soifer's "favorite problem", Polymath16 | finite UDG + 5-col UNSAT cert | 5–10%; even improved 5-chromatic records notable |
| C5 | Erdős–Gyárfás power-of-2 cycles, cubic case | $100/$50 Erdős prize | cubic graph, no 4/8/16/32-cycle | counterexample <5%; frontier-pushing (n=31→36+) near-certain |
| C6 | R(3,10) ∈ {40,41} | Radziszowski dynamic survey; one of the 2 smallest open Ramsey | enumeration certificate | <3% full closure (needs ≫3 CPU-yr-equivalent + new algorithms); structural side-results possible |
| C7 | Football pool problem K₃(6,1) ∈ [71,73] | 40+ yr classic covering-code problem | code of size 72 (SAT/ILP) or LB 72 | 5–15%: UB 73 is 1987-era tabu search; modern SAT may find 72 or kill it |
| C8 | Earth–Moon problem: 10-chromatic biplanar graph | Ringel 1959; Gardner-popularized | two planar layers + 9-col UNSAT cert | 3–8%; frontier untouched since 2008 (9-critical graphs) |
| C9 | Magic square of squares (LaBar–Gardner) | $100 Gardner + €1000 Boyer | 9 squares (or hourglass sub-problem) | <2% direct; elliptic-curve-structured search; heavily raced |
| C10 | R(4,6) ∈ [36,40] | the other smallest open Ramsey number | coloring of K₃₆₊ or enumeration | lower-bound improvement 5–10%; closure <2% |
| C11 | EFL conjecture small-n gap (n = 13…N₀) | Erdős's favorite; proven for large n (Kang et al. 2021) | SMS enumeration + DRAT per n | incremental n=13,14 realistic (20–40%); full gap impossible (N₀ astronomical) |

---

## C1. Erdős #7 — odd covering system (Erdős–Selfridge)

**Statement.** Does there exist a covering system of ℤ (finite set of congruences a_i mod n_i
covering every integer) with all moduli distinct, odd, and > 1?
**Source:** erdosproblems.com/7; Erdős 1950 lineage; Filaseta–Ford–Konyagin (J. AMS 2000,
PDF free); Balister–Bollobás–Morris–Sahasrabudhe–Tiba, "The Erdős–Selfridge problem with
square-free moduli" (arXiv:1901.11465, free PDF).
**Why notable.** Selfridge raised his award to **$2000 for an explicit example**; Erdős offered
$25 for nonexistence. One of the most-cited covering-system problems; BBMST's square-free
resolution was a major Annals-adjacent result. An explicit odd covering would be front-page
news in number theory; it is *exactly* a finite certificate.
**Frontier.** Known constraints: no square-free odd covering (BBMST 2022); some modulus divisible
by 2 or 3 (Hough–Nielsen 2019); lcm divisible by 9 or 15 (BBMST). Nobody has published a serious
*search* for an odd covering with high prime-power moduli — the structural results all push
toward nonexistence, but Erdős believed it exists.
**Attack.** SAT/ILP over candidate modulus pools built from {3^a 5^b 7^c 9 11 ...} with lcm
control (same machinery as P15/P18 but with the odd+distinct constraint and prime-power-heavy
pools that evade the BBMST sieve obstruction, i.e. exploiting exactly the p^e block-size loophole
Archivara's failed proof highlighted). Nonexistence for bounded lcm gives LRAT-certified partial
results in the style of Sanexxxx777's #273 bound.
**Priority check.** erdosproblems.com marks OPEN (checked 2026-07). Archivara's Jan-2026
nonexistence proof publicly debunked (llllvvuu gist). LeanGenius hosts a formalized *statement*,
not a solution. GitHub/Zenodo search "odd covering system": no explicit-example search artifacts
found. Residual risk: Archivara iterating privately.
**Feasibility.** Compute: days–weeks of SAT per pool; the honest obstacle is that the true lcm
may be enormous. P(explicit witness) ≈ 3–8%; P(publishable certified partial bound) high.

## C2. Erdős–Szekeres ES(7) = 33 (Happy Ending problem, first open case)

**Statement.** Does every set of 33 points in general position in the plane contain 7 points in
convex position? (Conjecture ES(k) = 2^{k−2}+1; verified k ≤ 6, Szekeres–Peters 2006.)
**Source:** Erdős–Szekeres 1935; Suk (2017); Notes on the 33-point problem, arXiv:2512.24061
(free PDF); Heule–Scheucher h(6)=30 (empty hexagon, SAT 2024) as the method template.
**Why notable.** Textbook problem that founded Ramsey-theoretic combinatorial geometry.
Heule–Scheucher's empty-hexagon SAT proof (CPP/SAT 2024, later Lean-verified) shows the exact
pipeline; ES(7) is the community's acknowledged next target and would be a headline SAT result.
**Frontier.** arXiv:2512.24061 (Dec 2025) gives a triple-orientation SAT encoding with
convex-layer anchoring; UNSAT only for anchored subfamilies; reports heavy-tailed runtimes
("weeks on commodity hardware" for some cubes). Full problem ≈ estimated 10⁴–10⁵ CPU-days with
current encodings — big but Heule-class, not impossible; encoding improvements are the leverage.
**Attack.** Reproduce+improve the 2512.24061 encoding (better symmetry breaking on order types
via Scheucher's tools; smarter cube split on convex-layer templates), cube-and-conquer with DRAT.
Alternative cheap deliverable: independent verification/extension of anchored subfamilies.
**Priority check.** No claimed resolution (the Zenodo "Triadic Validator" claim is crank). Active
legitimate competition: Scheucher, Heule, and the 2512.24061 authors. GitHub: Scheucher's
SAT-for-order-types repos; no ES(7)-closed artifact.
**Feasibility.** P(full UNSAT closure by us) 10–20% given ultra-scale compute; scoop risk HIGH
(this is the community's #1 target). Impact if landed: very high.

## C3. Conway's 99-graph problem — SRG(99,14,1,2)

**Statement.** Does a strongly regular graph with parameters (99,14,1,2) exist? Equivalently: a
99-vertex graph where every edge lies in a unique triangle and every non-edge in a unique C₄.
**Source:** Conway's $1000 problem list (OEIS/Five $1000 problems, 2017); Biggs 1971/ Norman
lineage. Recent: "On the automorphism group of a putative Conway 99-graph", Algebraic
Combinatorics 8 (2025) 379–398 (open access); "Approaching the Conway-99 problem using SAT
solvers", arXiv:2604.23037 (Apr 2026, free PDF); U.Chicago REU SAT framework (Selub 2023, PDF).
**Why notable.** Carries an explicit **$1000 Conway prize**; the (99,14,1,2) parameter set is the
smallest feasible SRG parameter set whose existence is unknown. Either outcome is newsworthy.
**Frontier.** Automorphism group of any example is now known to be very restricted (order ≤ 3
type results, 2025 paper); raw SAT shown to stall (2026 arXiv paper analyzes why: 4851 edge vars,
weak propagation from the unique-triangle constraints). Nobody has combined the 2025
automorphism restrictions with SMS/orderly generation of the triangle structure (the graph is
locally a perfect matching plus structure — edges partition into 693 triangles ⇒ search over
Steiner-like triangle systems instead of edges).
**Attack.** V2/V3 hybrid: enumerate the 1-factorization-like local structure (each vertex: 14
neighbors forming 7 disjoint edges) as a combinatorial design, feed to SMS with the 2025
automorphism constraints; target either the graph or nonexistence of highly-structured subcases
(e.g. rule out any automorphism of order 3, finishing the "vertex-transitive impossible" line).
**Priority check.** Open per 2026 arXiv paper. GitHub: several stalled SAT repos (conway99
searches by hobbyists, none conclusive). No Zenodo/agentic claims found.
**Feasibility.** Full resolution <5% (search space genuinely huge); a rigorous new structural
elimination (automorphism order 3, or triangle-system classification for a subcase) is realistic
and publishable. Compute: weeks of SMS.

## C4. Hadwiger–Nelson: a 6-chromatic unit-distance graph

**Statement.** Exhibit a finite unit-distance graph in the plane with chromatic number ≥ 6
(would prove CNP ≥ 6; currently 5 ≤ CNP ≤ 7).
**Source:** de Grey, "The chromatic number of the plane is at least 5" (arXiv:1804.02385, free);
Polymath16 (Mixon's blog + polymath wiki); Parts, Geombinatorics 2020 (509-vertex record
5-chromatic graph); Soifer, *The Mathematical Coloring Book*.
**Why notable.** The 2018 CNP ≥ 5 breakthrough (by an amateur!) was covered by Quanta and
launched Polymath16. CNP ≥ 6 would be a *bigger* story. Verification is exact: rational-ish
coordinate certificate + SAT UNSAT certificate for 5-colorability.
**Frontier.** Polymath16 wound down (~2021) without reaching 6; best tools: de Grey's spindle
tensoring, Heule's minimization SAT pipeline, Parts' human-verifiable 509-vertex graph;
Exoo–Ismailescu independent constructions; fractional/ring-based obstructions studied. No
serious public 6-chromatic attempt since.
**Attack.** V2+V3: build candidate graphs from rings ℤ[ω₁,ω₂] with several spindle distances
(Polymath16's leftover ideas: ε-spindles, Minkowski sums of known 5-chromatic cores), test
5-colorability with incremental SAT + clause reuse à la Heule. Cheap intermediate deliverables:
smaller-than-509 5-chromatic graph (record), or 5-chromatic graphs with extra properties.
**Priority check.** No 6-chromatic claim anywhere (arXiv/GitHub/Zenodo checked; Wikipedia and
polymath wiki current as of 2026 say 5 ≤ CNP ≤ 7). Exoo–Ismailescu occasionally publish; watch.
**Feasibility.** P(6-chromatic) 5–10% — genuinely unknown whether 6-chromatic finite graphs are
even "small"; P(record 5-chromatic graph) moderate. Compute: heavy SAT but embarrassingly
parallel.

## C5. Erdős–Gyárfás conjecture — cubic counterexample search / frontier push

**Statement.** Every graph with min degree 3 contains a cycle of length a power of 2. ($100 for
proof, $50 for counterexample — Erdős.)
**Source:** erdosproblems.com PowerOfTwoCycles page; Markström 2004 (cubic bound 30, PDF free);
Wikipedia; Heckman–Krakovski 2013 (3-connected cubic planar case, free).
**Why notable.** Named Erdős-prize conjecture, Wikipedia-famous, 30 years open. A cubic
counterexample (finite graph, machine-checkable: no 4-, 8-, 16-, 32-cycles) would collect the
prize and be genuinely newsworthy.
**Frontier + prior computational attack.** Royle/Markström: general ≥17, cubic ≥30 (2004);
Markström's four 24-vertex cubic graphs whose only power-of-2 cycles are C₁₆ are the best
near-misses. **June 2026 (Zenodo 10.5281/zenodo.20782738, Arjun Balaji): SMS verification pushes
the general min-degree-3 bound to 31.** That artifact is the state of the art and shows SMS +
Glasgow-subgraph-propagator works; it stopped at n=30 for compute reasons.
**Attack.** (a) Extend the SMS search on the *cubic* class (much sparser) to n≈36–40, using
girth ≥ 5 and no-C₈ as propagators — every increment is a citable record; (b) structured
counterexample hunt: blow-ups/covers of Markström's 24-vertex near-misses designed to kill the
16-cycles while avoiding 32-cycles (V2).
**Priority check.** Conjecture open (the Jan-2026 Zenodo "proof" is uncredentialed noise;
erdosproblems page still lists open). Balaji artifact = direct prior art to cite and build on.
GitHub: no cubic-class extension found.
**Feasibility.** Frontier push near-certain (weeks of SMS); counterexample <5% but the near-miss
structure gives a real angle. Best effort/reward ratio in this list.

## C6. R(3,10) — one of the two smallest unknown Ramsey numbers

**Statement.** Decide R(3,10) ∈ {40, 41}. (Exoo 1989: ≥40; Angeltveit, El. J. Comb. 2025:
≤41, free PDF — brought 42→41 with ~3 CPU-years after algorithmic speedups over the
50-CPU-year Goedgebeur–Radziszowski 2013 computation.)
**Why notable.** Small Ramsey numbers are the marquee benchmark of computational combinatorics
(Radziszowski's Dynamic Survey). Closing R(3,10) would be the first diagonal-adjacent closure
since R(3,9)/R(4,5) era and heavily cited.
**Frontier.** Angeltveit states 40→closure requires "several orders of magnitude more" work than
41. arXiv:2601.03572 (Jan 2026) develops structural constraints on hypothetical (3,10,40)-critical
graphs (degree sequences, connectivity 6–8, diameter ≤3) explicitly intended to shrink the search.
**Attack.** Combine 2601.03572's degree-sequence restrictions with Angeltveit's gluing pipeline;
alternatively hunt a (3,10)-graph on 40 vertices (proving =41) by SAT/annealing from Exoo-style
seeds — asymmetric: a single SAT witness on 40 vertices settles it upward.
**Priority check.** No closure claimed (EJC 2025 + Jan 2026 arXiv are latest). AlphaEvolve-type
papers (arXiv:2603.09172) match but don't beat these bounds.
**Feasibility.** Full closure <3% without a new algorithmic idea; witness-on-40 search is cheap
to try and high-payoff if R(3,10)=41. Rank kept high on impact.

## C7. Football pool problem for six matches — K₃(6,1) ∈ [71,73]

**Statement.** Minimum size of a radius-1 covering code of ternary words of length 6.
Known 71 ≤ K₃(6,1) ≤ 73; values known for v ≤ 5.
**Source:** Linderoth–Margot–Thain, INFORMS J. Computing 2009 (LB 65→71; "two CPU-centuries",
free TR PDF); Wille 1987 (UB 73, tabu search); Östergård–Wassermann 2002.
**Why notable.** 40+-year-old named problem in covering codes (Golay-adjacent community, CRC
Handbook of Combinatorial Designs entry); the 2009 computation was celebrated as one of the
largest grid computations ever. Any bound improvement is a JCTA-level result; closure would be
definitive.
**Frontier.** Untouched since 2009 (searched arXiv/GitHub 2010–2026: nothing). The UB 73 predates
modern SAT entirely — a size-72 code may simply have been unreachable by 1987 tabu search.
**Attack.** V3/V4: exact cover SAT/ILP for size-72 codes with the full wreath-product symmetry
group (2⁶·6!·... order 6!·2⁶·... — use isomorph-free subcode seeding as in Linderoth et al.);
modern kissat + symmetry breaking vs. 1987 heuristics is a genuine generational advantage. LB
72 via their published subcode-enumeration decomposition rerun with今日 ILP.
**Priority check.** No post-2009 progress found anywhere (incl. covering-code tables of Kéri —
site archived; Zenodo/GitHub clean).
**Feasibility.** P(finding size-72 code) unknown-but-testable; P(some bound move) 5–15%.
Compute: heavy but decomposable. Low scoop risk.

## C8. Earth–Moon problem — a 10-chromatic thickness-2 graph

**Statement.** The maximum chromatic number of biplanar (thickness-2) graphs is between 9 and 12
(Ringel 1959). Exhibit a biplanar graph with χ ≥ 10.
**Source:** Ringel 1959; Sulanke's K₆+C₅ (9-chromatic); Boutin–Gethner–Sulanke, J. Graph Theory
2008 (40 new 9-critical thickness-2 graphs, infinite family; PDF via Hamilton College); Gethner
2018 survey ("To the Moon and beyond") conjecturing the answer is 11; teorth optimization-
problems constant C₂₇ᵦ page tracks it.
**Why notable.** Gardner-popularized successor to the Four Color Theorem, 65 years open with the
lower bound stuck at 9 since 1980. A 10-chromatic biplanar graph is a *fully certifiable*
witness: two planar edge-layers (each checkable in linear time) + a DRAT UNSAT proof of
9-colorability.
**Frontier.** No computational lower-bound attack has ever been published (2008 construction work
was by hand). The search space issue: thickness is NP-hard to *decide*, but we only need to
*construct* graphs with an explicit 2-layer decomposition — e.g. r-inflations and joins of
planar pairs (Albertson–Boutin–Gethner studied 2-inflations; C₅-inflation-type graphs are the
known extremal family).
**Attack.** Parameterized generator of layered graphs (two planar triangulations on shared
vertex set, maximizing density 6n−12) + chromatic-number SAT; local search over layer pairs
guided by fractional chromatic number; seed from Sulanke-type joins and Catlin/inflation
families.
**Priority check.** teorth constants page + Wikipedia (updated Feb 2026) confirm 9 ≤ · ≤ 12
still. arXiv/GitHub/Zenodo: no 10-chromatic claim, no search code found.
**Feasibility.** Honest unknown — extremal examples may be large; but the field has literally
never had a computational attack, so cheap experiments have real information value. P ≈ 3–8%.

## C9. Magic square of squares (LaBar–Gardner problem)

**Statement.** Does a 3×3 magic square exist whose nine entries are distinct perfect squares?
**Source:** LaBar 1984 (College Math. J.); Gardner 1996 ($100 prize); Guy UPINT D15; Boyer's
multimagie.com tracks the frontier (+ €1000 prize for the 7-distinct-squares sub-problem).
**Why notable.** Arguably the most famous open recreational-number-theory problem (Numberphile
"Parker Square"); equivalent to rational points on specific elliptic-curve families / three
3-term APs of squares with constraints.
**Frontier.** Brute force exhausted to entries > 10¹⁴ (distributed searches, Zimmermann et al.);
near-misses with one bad sum (Sallows, Parker); strong heuristic + elliptic-curve arguments
against existence (Vaknin/Várilly-Alvarado-type descent arguments suggest obstructions but no
proof).
**Attack.** Only sensible angles: (a) the €1000 "magic hourglass" (7 squares) sub-problem via
elliptic-curve section search on the known parametrization (Pech's TIPE approach, modern
compute); (b) a *conditional impossibility proof* for structured families via descent. Raw
search is dominated by decades of specialist compute — do NOT re-run brute force.
**Priority check.** multimagie.com status page (2025-06 update): both prizes unclaimed.
**Feasibility.** <2% for the main prize; the hourglass sub-problem is a genuine, less-crowded
finite-ish target. Included mainly for completeness; rank low.

## C10. R(4,6) ∈ [36, 40]

**Statement.** Decide R(4,6). Exoo 2012: ≥36 (explicit K₃₅ coloring); Angeltveit–McKay
(2019–2024, via dynamic survey): ≤40.
**Why notable.** The other "smallest unknown Ramsey number" alongside R(3,10).
**Frontier.** Gap of 4 — much wider than R(3,10); upper-bound machinery (gluing (3,6)/(4,5)
graphs) is many orders beyond feasible closure. Lower bound: heuristic searches (incl.
AlphaEvolve 2026) only *match* 36; a K₃₆ witness would set a record.
**Attack.** Lower-bound search only: seeded annealing/tabu from Exoo's order-4-automorphism
coloring; algebraic seeds (block-circulant with fixed points). A new LB is a citable record; a
closure is out of reach.
**Priority check.** Dynamic Survey rev. 2024-09 + AlphaEvolve paper (2026): 36–40 stands.
**Feasibility.** LB +1: 5–10%; closure <2%. Keep as a cheap V1-style side campaign.

## C11. Erdős–Faber–Lovász — closing small-n cases

**Statement.** Every n-uniform linear hypergraph with n edges is n-vertex-colorable. Proven for
all n ≥ N₀ (Kang–Kelly–Kühn–Methuku–Osthus, Ann. of Math. 2023) with N₀ ineffective/huge;
verified exhaustively only for n ≤ 12 (Romero–Alonso 2014); SMS-based extension attempted in
"A SAT Solver's Opinion on the EFL Conjecture" (SAT 2023, open access, Kirchweger–Peitl–Szeider).
**Why notable.** One of Erdős's three favorite problems ($500 prize historically). The
large-n proof makes small-n the *only* thing left — a clean "we pushed the verified frontier"
story with DRAT certificates, and any counterexample at small n would be spectacular (nobody
expects one).
**Frontier.** SAT 2023 paper's generate-and-reject SMS loop is the tool; they report n ≈ 13–14
becoming hard. No progress artifacts since (GitHub/Zenodo checked; only the SAT-2023 artifact).
**Attack.** Improve the SMS candidate-generation with the known reductions (only intersecting,
"dense" hypergraphs matter; cores after removing degree-1 vertices), close n = 13, 14 with DRAT.
**Priority check.** No n ≥ 13 verification published as of 2026-07.
**Feasibility.** n=13 likely lands with weeks of compute (20–40%); each n is citable. Impact
moderate (incremental), certainty high.

---

## Investigated and REJECTED (do not spend runs)

| Problem | Reason |
|---|---|
| 2-(22,8,4) design (was "smallest open BIBD") | **RESOLVED**: nonexistent — Bilous et al., J. Comb. Designs 15 (2007) |
| cr(K₁₃) | **RESOLVED**: = 225, computer-assisted (Aichholzer et al., Graz, ~2024–25); cr(K₁₄)=315 follows |
| R(3,3,4) | **RESOLVED**: = 30 (Codish–Frank–Itzhakov–Miller 2016, SAT) |
| R(3,3,3,3) ∈ [51,62] | gap 11; upper-bound machinery (Fettes–Kramer–Radziszowski 2004) hopeless to extend; LB believed tight |
| Projective plane of order 12 | search space ≫ Lam's order-10 computation; decades away |
| Moore graph of degree 57 / SRG(3250,57,0,1) | 3250 vertices — far beyond any exact method; only structural results possible |
| Seymour's 2nd-neighborhood conjecture | no meaningful finite frontier (verified only n≤7); no minimal-counterexample size theory; noisy claimed proofs |
| Barnette's conjecture | verified <86 vertices; faces ≤8 case just closed (arXiv:2508.03531, Aug 2025) — active specialists; counterexample widely disbelieved; frontier push = enumeration slog with weak payoff |
| Kaplansky unit conj., Keller dim 7, Hedetniemi, empty hexagon h(6), Erdős discrepancy | all resolved (2020–2024) — listed to save future search time |
| Hadamard 668, Costas 32/33, S(2,6,46), lonely runner k=9, D(61), u(n) | already excluded in problems/README.md wave-1/2 vetting |

## Recommended wave-3 intake (if promoting to problems/)

1. **C5 Erdős–Gyárfás cubic frontier** (near-certain deliverable + prize-problem counterexample lottery; builds directly on the Balaji Zenodo artifact — cite it),
2. **C1 Erdős #7 odd covering** (highest prize, fits our covering-system toolchain from P15/P18),
3. **C7 Football pool K₃(6,1)** (dormant since 2009, modern-SAT generational edge, low scoop risk),
4. **C2 ES(7)** (highest headline value; accept the scoop risk, or scope to independent
   verification + one new anchored-family closure),
5. **C11 EFL n=13** (high-certainty citable result),
6. **C3 Conway-99 structural subcase** and **C8 Earth–Moon 10-chromatic** as exploratory V2/V3
   campaigns; **C4, C6, C10** as background lottery-ticket searches sharing infrastructure.

⚠ Reminder recorded in §0: P18 (Erdős #273) has certified prior art (Sanexxxx777 LRAT bound,
moduli p−1 ≤ 50) that our runs must acknowledge.

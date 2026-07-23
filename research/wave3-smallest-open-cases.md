# Wave-3 research: notable named problems whose smallest open case is a concrete finite object

Researched 2026-07-23. Scope per tasking: problems a research mathematician recognizes **by name**
(no Graffiti/WoW/AGX lists), not duplicating P01–P21, where the smallest open case is a finite
object within reach of serious SAT/ILP/exhaustive computation. All statuses verified against
July-2026 literature via Exa search (arXiv, journals, Radziszowski's DS1 survey rev. #17 of
June 2024, Wikipedia tables) **plus** the mandatory widened priority sweep (GitHub, Zenodo,
OpenReview, AI-artifact repos) — see the per-candidate "Priority check" blocks; several live
AI-agent artifact claims were found and are flagged.

Feasibility grading is deliberately brutal: anything estimated > ~10^12 core-ops for the full
decision is marked **INFEASIBLE (full)** and only credited for feasible *subproblems*.

Overlap notes with existing repo files: Zarankiewicz cells K_{7,11}/K_{9,9} and skew-Hadamard 356
are already in `research/classic-graph-theory.md` / `research/combinatorial-designs.md`; perfect
1-factorization smallest open case is K₆₄ (K₅₆ was settled by Pike 2019, arXiv:1810.08734) and is
already cataloged. Those are not repeated here.

---

## C1. Edge Folkman number Fe(3,3;4) — Graham's $100 "< 100" problem  ★ top pick

- **Statement.** Fe(3,3;4) = min n such that there is a K₄-free graph G on n vertices with
  G → (3,3)ᵉ (every 2-coloring of E(G) has a monochromatic triangle). Known: 20 ≤ Fe(3,3;4) ≤ 786.
  Primary sources: Radziszowski–Xu, "On the Most Wanted Folkman Graph", Geombinatorics XVI (2007),
  PDF: https://www.cs.rit.edu/~spr/PUBL/paper53.pdf ; upper bound 786: Lange–Radziszowski–Xu,
  "Use of MAX-CUT for Ramsey Arrowing of Triangles" (2012), PDF: https://www.cs.rit.edu/~spr/PUBL/fe334mc12.pdf ;
  lower bound > 19: Bikov–Nenov, arXiv:1609.03468 (PDF: https://arxiv.org/pdf/1609.03468).
- **Notability.** Erdős paid two $100 prizes on this exact quantity (for < 10^10, Spencer; and the
  original 1975 Erdős–Hajnal question); Graham's standing $100 prize for Fe(3,3;4) < 100 is still
  unclaimed. Radziszowski calls it "the most wanted Folkman graph"; it headlines his DS1-adjacent
  survey "On Some Open Questions for Ramsey and Folkman Numbers" (https://cs.rit.edu/~spr/PUBL/sur14.pdf).
- **Smallest open cases / concrete targets.**
  (a) Decide whether the 63-vertex Hermitian-unital graph H₃ of Mulrenin–van Overberghe
  (arXiv:2506.14942, PDF: https://arxiv.org/pdf/2506.14942) contains a Folkman subgraph after
  K₄-destroying alterations — the authors themselves present evidence and leave it open. A YES
  gives Fe(3,3;4) ≤ 63 and claims Graham's prize.
  (b) Test arrowing for the known 127-vertex G₁₂₇ = G(127,{cubic residues}) candidate (open since
  1970s; best partial: MAX-CUT/spectral methods fail just short).
  (c) Push the lower bound past 20 (Bikov–Nenov's 19 used clever local analysis + compute).
- **Computational frontier.** Arrowing G → (3,3)ᵉ is coNP-complete in general, but for a *fixed*
  ~63–127-vertex graph it is one SAT instance (vars = edges, clauses = triangles, UNSAT of
  "2-color with no mono triangle"); modern CDCL + symmetry breaking handles the 63-vertex case
  comfortably (≤ 10^10–10^11 ops est.); G₁₂₇ is harder but its huge automorphism group (order
  divisible by 127·7·3) makes SMS plausible. Lange et al. stopped in 2012 with far weaker solvers.
- **Feasibility.** FEASIBLE for (a) and plausibly (b); lower-bound push (c) is harder
  (enumeration over K₄-free graphs) — marginal.
- **Lean.** Statement trivial to formalize (finite graph arrowing); an UNSAT certificate can be
  replayed via verified DRAT/LRAT checking (cake_lpr) — same pipeline as P20.
- **Priority check (widened).** arXiv: nothing newer than 2506.14942 (v4, 2026-03). GitHub/Zenodo:
  only the 2019 QSAT vertex-Folkman benchmark (doi:10.5281/zenodo.3548976) and Bikov's older code;
  **no artifact claiming Fe(3,3;4) improvements found** (searched "Folkman 786", "Folkman number
  SAT", "arrowing triangle"). OpenReview: nothing. Clean.
- **Impact 5 × Feasibility 4.**

## C2. Ramsey number R(3,10): the last gap is one — 40 or 41

- **Statement.** R(3,10) ∈ {40, 41}. Upper bound 41: Angeltveit, EJC 32(4) #P30 (2025),
  PDF: https://www.combinatorics.org/ojs/index.php/eljc/article/download/v32i4p30/pdf
  (arXiv:2401.00392). Lower bound 40: Exoo 1989. Survey: Radziszowski, "Small Ramsey Numbers",
  DS1 rev.#17 (2024), PDF: https://www.combinatorics.org/files/Surveys/ds1/ds1v17-2024.pdf.
- **Notability.** Classical two-color Ramsey number; any exact determination of a new R(3,k) is a
  headline result in combinatorics (last was R(3,9)=36 in 1982!). Worked on by Exoo, Grinstead–
  Roberts, Goedgebeur–Radziszowski (arXiv:1210.5826), Angeltveit–McKay, and (certificates)
  Bright's MathCheck group (R(3,8)/R(3,9) verified certificates, IJCAI-2025, arXiv:2502.06055).
- **Smallest open case.** Decide existence of a (3,10;40)-graph: a triangle-free graph on 40
  vertices with independence number ≤ 9. Exists ⇒ R(3,10)=41; UNSAT ⇒ R(3,10)=40.
- **Computational frontier.** Angeltveit's 41-proof combined gluing of (3,9)- and (3,8)-graph
  classifications with LP; the 2026 structural paper (Pandey–Ravi, arXiv:2601.03572, PDF:
  https://arxiv.org/pdf/2601.03572) narrows properties of hypothetical critical graphs (regularity
  ~ degree 13). Full enumeration of 40-vertex triangle-free graphs is absurd (~10^40+), but the
  gluing search space left after Angeltveit's reductions is estimated by him as "large but not
  hopeless"; a dedicated attack is plausibly 10^12–10^14 core-ops.
- **Feasibility.** **MARGINAL–INFEASIBLE (full)** at our scale; FEASIBLE subproblems: extend the
  Pandey–Ravi structural constraints (degree-sequence and neighborhood-graph eliminations are
  independent SAT/ILP cells), or enumerate (3,10;39,e)-graphs at extremal edge counts to squeeze
  the LP. Frontier-push publishable even without full resolution.
- **Lean.** Statement easy; full proof would be certificate-gigantic (R(3,9) cert ≈ TB-scale) —
  Lean statement-only, verified-checker replay for subcells.
- **Priority check (widened).** No claim of R(3,10)=40 or =41 resolution found on arXiv (through
  2026-07), GitHub, Zenodo, or OpenReview. Active-competition risk: HIGH — Angeltveit/McKay and
  the MathCheck group are both visibly working this exact number (the 2026 critical-graphs paper
  confirms outside interest). RL-based construction attempts (arXiv:2603.09172) target lower
  bounds, none for (3,10;40) yet.
- **Impact 5 × Feasibility 2 (full) / 4 (subproblems).**

## C3. Smaller 5-chromatic unit-distance graphs (Hadwiger–Nelson subproblem)

- **Statement.** Find a unit-distance graph in the plane with χ = 5 and fewer than 509 vertices
  (current record: Parts, Geombinatorics 2020; method paper arXiv:2010.12665, PDF:
  https://arxiv.org/pdf/2010.12665). Related lower bounds: any 5-chromatic UDG has ≥ 26 vertices
  (de Grey–Parts, arXiv:2303.14714, PDF: https://arxiv.org/pdf/2303.14714).
- **Notability.** THE headline computational combinatorics story of 2018 (de Grey's 1581-vertex
  graph, arXiv:1804.02385; Polymath16 devoted itself to exactly this minimization; Heule's SAT
  minimization to 553 vertices, arXiv:1805.12181). Every record is tracked on MathWorld
  (de Grey/Heule/Mixon/Parts graphs pages).
- **Smallest open case.** A single finite witness: vertex coordinates (algebraic numbers) + a
  DRAT proof that the graph is not 4-colorable. Verifier: exact arithmetic distance check +
  verified UNSAT replay — minutes.
- **Computational frontier.** Heule: clausal-proof minimization (553 → 529); Parts: manual+local
  "graph minimization" to 509. Nobody has published a sub-500 graph since 2020; Polymath16 wound
  down. Modern SMS/local-search + Heule's public tooling is a genuine opening.
- **Feasibility.** FEASIBLE. Each candidate test is a small SAT instance (~500 vertices, ~2500
  edges); the search over spindle-assemblies is heuristic, cheap per iterate. Also feasible:
  improve the 26-vertex lower bound (de Grey–Parts method is explicitly incremental).
- **Lean.** Coordinates are algebraic — exact verification in Lean is real work but bounded;
  4-col UNSAT via cake_lpr. Statement formalization easy.
- **Priority check (widened).** arXiv through 2026-07: nothing below 509. GitHub: Heule's
  marijnheule/UDG repos unchanged since ~2019. Zenodo/OpenReview: no claims. Polymath16 wiki
  frozen. Clean, low scoop risk (field dormant = opportunity).
- **Impact 4 × Feasibility 4.**

## C4. Biplane (121, 16, 2) — smallest undecided biplane

- **Statement.** Does a symmetric 2-(121,16,2) design (biplane of order 14) exist? Only 16
  nontrivial biplanes are known (k ≤ 13); k = 16 with v = 121 is the smallest undecided parameter
  set. Sources: Crnković–Dumičić Danilović–Rukavina, "On automorphism groups of a biplane
  (121,16,2)", Discrete Math. 344 (2021) 112508, arXiv:2010.12944 (PDF:
  https://arxiv.org/pdf/2010.12944); Alavi–Daneshkhah–Praeger, "Symmetries of biplanes",
  Des. Codes Cryptogr. 88 (2020), arXiv:2004.04535.
- **Notability.** Biplane existence is a marquee question of design theory (Hall, Assmus, Salwach;
  Marshall Hall's problem list); the (121,16,2) case is singled out in the Handbook of
  Combinatorial Designs and by Praeger's group.
- **Smallest open case / targets.** Full decision is a giant exact-cover problem; the live
  frontier is eliminating automorphism groups: Crnković et al. (2021) show |Aut| ∈ {1,2,3} up to a
  few residual prime-order cases, building on Alaeiyan–Safakish 2009 and Praeger's flag-transitive
  eliminations. Concrete cells: finish killing order-2 and order-3 automorphisms (orbit-matrix +
  indexing = clean ILP/SAT instances), leaving only the (hopeless-for-everyone) rigid case.
- **Feasibility.** FEASIBLE for the remaining prescribed-automorphism cells (each is orbit-matrix
  enumeration ≈ 10^8–10^11 ops with modern SAT; the 2021 paper used older tooling). Full rigid
  case: **INFEASIBLE** (>> 10^15).
- **Lean.** Nonexistence-under-symmetry = UNSAT certificates, replayable; statement easy.
- **Priority check (widened).** arXiv 2021–2026: no elimination beyond Crnković et al.; the 2023
  Zenodo "bigeodetic blocks" paper (doi:10.5281/zenodo.8204536) proposes a connection but proves
  no existence result. GitHub: no repos. Clean.
- **Impact 4 × Feasibility 4 (symmetry cells).**

## C5. The missing Moore graph (3250, 57, 0, 1): symmetry-elimination frontier

- **Statement.** Does a Moore graph of degree 57, diameter 2 (SRG(3250,57,0,1)) exist? Last open
  case of Hoffman–Singleton (1960). Survey: Dalfó, "A survey on the missing Moore graph", Linear
  Algebra Appl. 569 (2019). Known: |Aut| ≤ 375 (Mačaj–Širáň 2010); NEW 2026: it has no involutions
  — Ishida, arXiv:2606.29183 (PDF: https://arxiv.org/pdf/2606.29183), so |Aut| is odd, ≤ 375.
- **Notability.** One of the most famous open problems in algebraic graph theory, in every
  spectral/SRG textbook (Brouwer–van Maldeghem, Godsil–Royle).
- **Smallest open cases / targets.** With involutions gone, the remaining automorphism orders are
  odd divisors of 375 and a few others from Mačaj–Širáň's list: rule out order 3 and order 5
  automorphisms by fixed-substructure analysis + SAT on quotient/orbit structures (Ishida's paper
  is exactly this pattern and cites explicit open next cases). Each elimination is a publishable
  increment; ruling out all of 3,5 would force |Aut| = 1 — a striking statement.
- **Computational frontier.** Ishida 2026 (computer-assisted, code released); earlier
  Brouwer's notes (https://aeb.win.tue.nl/preprints/3250.pdf). Full existence decision:
  **INFEASIBLE** by any known method (3250 vertices, ~10^100 search space).
- **Feasibility.** Symmetry cells FEASIBLE-to-MARGINAL: order-5 fixed structure is a Moore-like
  650-point quotient — sizable but SMS-attackable; order-3 likely harder. Honest estimate
  10^10–10^13 ops per cell depending on encoding quality.
- **Lean.** Statement easy; eliminations = UNSAT replay. A Lean-verified "no odd-order-5
  automorphism" would be novel.
- **Priority check (widened).** **FLAGS:** Zenodo hosts two 2026 nonexistence *claims* —
  doi:10.5281/zenodo.19791890 ("Disproving existence of Moore Graph", 2026-04-26) and
  doi:10.5281/zenodo.18501730 (Ihara–Bass/p-adic "rigorous proof", 2026-02-06) — both
  non-peer-reviewed AI-era artifacts; also arXiv:2010.13443 (2020, Russian) claimed nonexistence
  and was rebutted by Faber–Keegan (arXiv:2210.09577: "still open"). Any work here MUST first
  audit these claims (expected outcome: flawed, as with the 2020 one — Ishida 2026 treats the
  problem as open). Competition: active (Ishida / AI System Research, Kyoto).
- **Impact 5 × Feasibility 3.**

## C6. Three MOLS of order 10 (N(10) ≥ 3?) — structured subcases

- **Statement.** Do three mutually orthogonal Latin squares of order 10 exist? Open since Parker's
  1959 pair; the most famous small open case in Latin-square theory (post-Lam N(10) ≤ 6 known,
  ≥ 2 known; conjecture N(10) = 2). Survey context: McKay–Meynert–Myrvold, J. Combin. Des. 2007.
- **Notability.** Euler-adjacent; discussed in every design-theory text; MathOverflow 309010;
  active peer-reviewed SAT program (below).
- **Smallest open cases / targets.** Full search: **INFEASIBLE** (~10^18+ even with best
  symmetry breaking; Delisle's thesis covered only transversal-dimension ≤ 35 pairs). Feasible
  named subcases, following the Bright–Keita–Stevens SAT program (EJC 33(1)#P30, 2026,
  arXiv:2503.10504, PDF: https://arxiv.org/pdf/2503.10504; code
  https://github.com/curtisbright/Myrvold-MOLS, Zenodo doi:10.5281/zenodo.18130632; sequel
  "Two Relations", arXiv:2509.09633): e.g. finish the remaining Myrvold-style structural classes
  (SOLS-with-transpose was killed by Stones' MathOverflow question — verify residual cells), or
  extend the two-relation enumeration to the next dimension class.
- **Feasibility.** Subcases FEASIBLE (each published cell ran in ~CPU-weeks with kissat + SMS).
- **Lean.** Witness (a triple) trivially checkable; nonexistence cells via DRAT replay.
- **Priority check (widened).** Active competition is the main risk: Bright's group published
  Feb-2026 and Sep-2025 papers and keeps public repos; Zaikin's olegzaikin/latinsquares (SAT,
  ESODLS) is also active. No resolution claims found. Choose cells they have *not* announced.
- **Impact 5 × Feasibility 3 (subcases; scoop risk high).**

## C7. Union-Closed Sets (Frankl) conjecture, ground set n = 13

- **Statement.** Frankl 1979: every finite union-closed family (≠ {∅}) has an element in ≥ half
  the sets. Verified for |X| ≤ 12: Vučković–Živković, IPSI Trans. 2017, PDF:
  http://ipsitransactions.org/journals/papers/tir/2017jan/p9.pdf. Also true for families of ≤ 46
  sets. n = 13 is the smallest open ground-set case.
- **Notability.** Among the most famous conjectures in extremal set theory; Gilmer's 2022
  information-theoretic 0.01 breakthrough and the 3−√5/2 barrier (Alweiss–Huang–Sellke, EJC 2024)
  made it mainstream news. Polymath11 attacked it.
- **Computational frontier.** Vučković–Živković's n=12 proof used heavy local analysis + clever
  reductions, not raw enumeration (Moore families on 12 elements ≈ 10^24 — enumeration dead:
  Brinkmann–Deklerck JIS 21 (2018) only reached n=7 constructively). Pulaj's cutting-plane /
  Chvátal-style IP framework (github.com/JoniPulaj/cutting-planes-UC-families; Pulaj–Wood
  arXiv:2301.01331) gives certified finite reformulations (FC(k) families).
- **Feasibility.** n = 13 by brute force: **INFEASIBLE**. Via the Vučković–Živković reduction
  machinery + modern SAT for the residual cases: MARGINAL, genuinely uncertain — their paper does
  not quantify the n=13 blowup. Feasible adjacent target: extend Pulaj's FC(4)/FC(5) local
  configuration classification (clean ILP cells, publishable in the same venues).
- **Lean.** Statement one line; the reduction lemmas are human-paper-hard; certificate replay OK.
- **Priority check (widened).** **FLAG:** GitHub AEjonanonymous/Union-Closed-Sets-Conjecture +
  Zenodo 19441515 (2026-04) claims a *Lean-certified full proof* ("collision-restitution
  invariants") — 1 star, anonymous, not in any venue; near-certainly formalizes a weaker statement
  (audit before citing the problem as open in a solutions PR, per P07 lesson). arXiv:2405.03731
  (Demontis, "is true") remains unrefereed/uncited. Mainstream consensus: open.
- **Impact 5 × Feasibility 2.**

## C8. Erdős–Gyárfás power-of-two-cycle conjecture — minimum-counterexample push

- **Statement.** Every graph with minimum degree ≥ 3 has a cycle of length 2^k (Erdős–Gyárfás
  1994; Erdős offered $100). Source: erdosproblems.com "PowerOfTwoCycles"; Wikipedia. NEW 2026:
  every minimal counterexample is "predominantly cubic" (arXiv:2605.22844, PDF:
  https://arxiv.org/pdf/2605.22844); known true for cubic planar (Heckman–Krakovski, EJC 2013),
  3-connected cubic, large min-degree (Liu–Montgomery 2020).
- **Notability.** A named Erdős prize problem; Liu–Montgomery's partial solution appeared in JAMS-
  adjacent venues; genuinely recognizable.
- **Smallest open case.** A minimal counterexample would need > 30 vertices: SMS verification for
  min-degree-3 graphs up to 30 vertices, Zenodo doi:10.5281/zenodo.20782738 (2026-06-21) — note
  this frontier is itself an AI-agent artifact, not a journal paper. Target: push the SMS
  verification to 32–36 vertices (each vertex count is a separate SMS run; cost grows ~30–100×
  per +2 vertices — 32 is FEASIBLE, 36 is MARGINAL), and/or specialize to cubic graphs where
  geng-based exhaustion reaches further (cubic graphs on ≤ 36 vertices ≈ 10^12 — borderline).
- **Feasibility.** FEASIBLE (incremental, embarrassingly parallel, verifier = cycle-length check).
- **Lean.** Statement trivial; per-graph certificates trivial; "no counterexample ≤ n" needs
  verified isomorph-free generation (hard) or SMS-with-certificates (emerging tech).
- **Priority check (widened).** **FLAGS:** Zenodo doi:10.5281/zenodo.18249575 ("The Erdős-Gyárfás
  Conjecture (v1.0: falsified)", 2026-01-14) — an artifact claiming a counterexample; must be
  audited first (a valid counterexample would end the problem; overwhelmingly likely an error,
  since the 2026-05 arXiv paper and the 2026-06 SMS artifact treat it as open). Also the ≤30 SMS
  artifact means the low-vertex frontier is claimed — start above it.
- **Impact 4 × Feasibility 4 (audit risk noted).**

## C9. Football pool problem for 6 matches — K₃(6,1) ∈ [65, 73]

- **Statement.** Minimum size of a ternary covering code of length 6, radius 1:
  65 ≤ K₃(6,1) ≤ 73. Upper 73: Wille 1987 (simulated annealing), JCTA 44; lower 65:
  Linderoth–Margot–Thain, INFORMS J. Comput. 21 (2009), doi:10.1287/ijoc.1090.0334, TR PDF:
  https://jlinderoth.github.io/papers/Linderoth-Margot-Thain-07-TR-2.pdf (prior 64:
  Östergård–Wassermann, JCTA 99 (2002), doi:10.1006/jcta.2002.3260).
- **Notability.** "One of the most famous problems in coding theory" (Linderoth et al.); OEIS
  A004044; decades of work by Östergård, van Lint, Hämäläinen, Wille.
- **Smallest open case.** Either a 72-word covering code (witness: 72×6 ternary array, verifier
  trivial) or lower-bound 66 (IP + isomorph-pruned branch-and-bound).
- **Computational frontier.** The 2009 lower-bound-65 run consumed ~140 CPU-*years* of 2007
  hardware via Condor. A 2026 rerun with symmetry-exploiting ILP (or SAT with cardinality
  encodings) buys maybe 100× — pushing 66 is ~10^13–10^14 ops: **MARGINAL-INFEASIBLE**. The
  *upper* bound (find a 72-cover) has had no published improvement since 1987 despite heuristics —
  either 73 is optimal or the search landscape defeats annealing; modern local search/SAT hybrid
  is cheap to try (FEASIBLE attempt, uncertain payoff).
- **Lean.** Witness direction trivial to verify in Lean (finite check). Lower bound: no.
- **Priority check (widened).** No post-2009 bound improvements found (MaRDI, OEIS A004044 current
  as of 2026-05 still lists 65–73). GitHub: Slavov88/football-pool-problem and florath/
  covering-codes are hobby/heuristic repos, no claims. Clean.
- **Impact 3 × Feasibility 3.**

## C10. van der Waerden W(2,7) — and the honest verdict

- **Statement.** W(2,7): least n forcing a monochromatic 7-term AP in any 2-coloring of [n].
  Known: W(2,7) ≥ 3704 (Rabung–Lotts 2012); W(2,6) = 1132 (Kouril–Paul 2008). Tables: Wikipedia
  "Van der Waerden number"; https://leapsinbounds.org/constants/van-der-waerden-2-7/.
- **Notability.** Canonical Ramsey-theory quantities; W(2,6) was a SAT-community milestone.
- **Feasibility.** Exact W(2,7): **INFEASIBLE** (W(2,6) needed ~10^4 CPU-days of 2008 FPGA-assisted
  search over n=1132; scaling heuristics put W(2,7) ≥ 10^5–10^6× harder). FEASIBLE target: improve
  the *lower* bound 3704 via the template/zipper constructions (Rabung–Lotts; Heule's constructive
  methods, EJC 14 #R6) — cheap, witness = explicit coloring, verifier trivial, but modest impact.
  Mixed numbers w(k₁,k₂) smallest open cells (Ahmed's INTEGERS 11 tables) are FEASIBLE and exact,
  though individually minor.
- **Lean.** Lower-bound witnesses trivially verifiable.
- **Priority check.** Leapsinbounds (2026-current) confirms 3704 stands; no artifacts found.
- **Impact 3 × Feasibility 2 (exact) / 4 (lower bounds).**

## C11. Crossing number of K₁₅ (and the Aichholzer update) — status note, mostly infeasible

- **Statement/UPDATE.** Guy's conjecture cells: cr(K₁₃) = 225 and cr(K₁₄) = 315 were **settled**
  by Aichholzer et al. (Graph Drawing 2024/2025; TU Graz record "Another Small but Long Step for
  Crossing Numbers: cr(13)=225 and cr(14)=315"), superseding McQuillan–Pan–Richter's 219–225
  window (arXiv:1307.3297). Smallest open complete-graph cell is now cr(K₁₅) (Guy predicts 441;
  parity ties K₁₅/K₁₆).
- **Feasibility.** The cr(13) computation was already at the edge of feasibility for a dedicated
  group with bespoke machinery; cr(K₁₅): **INFEASIBLE** for us. Kept here mainly so the catalog's
  Zarankiewicz entries (K_{7,11}, K_{9,9} in `research/classic-graph-theory.md`) get re-baselined:
  Aichholzer's ODP/semidefinite machinery is the current state of the art and should be cited
  there; the bipartite cells remain open and are the better target.
- **Priority check.** Verify at write-up time whether the GD paper also touched K_{7,11}/K_{9,9}
  (no evidence found that it did).
- **Impact 4 × Feasibility 1 (K₁₅) — catalog-maintenance value only.**

---

## Ranking by impact × feasibility

| Rank | Candidate | I×F | One-line pitch |
|---|---|---|---|
| 1 | C1 Folkman Fe(3,3;4) ≤ 63? (H₃ subgraph test) | 20 | One SAT instance could claim Graham's $100 and a 786→63 headline |
| 2 | C3 5-chromatic UDG < 509 vertices | 16 | Dormant record, public tooling, trivial verifier |
| 3 | C4 Biplane (121,16,2) symmetry cells | 16 | Finish |Aut| eliminations with modern SAT |
| 4 | C8 Erdős–Gyárfás min-counterexample ≥ 32 | 16 | SMS push past the (AI-artifact) 30-vertex frontier; audit the "falsified" Zenodo claim first |
| 5 | C5 Moore graph 57: kill order-3/5 automorphisms | 15 | Ride the 2026 no-involutions momentum; audit 2 Zenodo disproof claims |
| 6 | C6 3-MOLS(10) structured subcases | 15 | Publishable cells, but Bright's group is live — pick unclaimed cells |
| 7 | C2 R(3,10) structural subproblems | 10 (4 sub) | Highest headline, heaviest compute; competition hot |
| 8 | C7 Union-closed n = 13 | 10 | Famous but reduction machinery unquantified; audit anon Lean "proof" artifact |
| 9 | C9 Football pool K₃(6,1) | 9 | Cheap upper-bound attempts; lower bound needs Condor-scale |
| 10 | C10 W(2,7) lower bounds | 8 | Easy witnesses, modest glory |
| 11 | C11 cr(K₁₅) | 4 | Infeasible; catalog re-baseline only |

## Cross-cutting AI-artifact audit queue (from the widened priority sweep)

Before any solve run cites these problems as open, audit (P07-scoop protocol):
1. Zenodo 18249575 — Erdős–Gyárfás "falsified" counterexample claim (2026-01).
2. Zenodo 19791890 + 18501730 — Moore-graph-57 nonexistence claims (2026-02/04).
3. GitHub AEjonanonymous + Zenodo 19441515 — Lean "proof" of union-closed (2026-04).
4. arXiv:2210.09577 (Faber–Keegan) — confirms the 2020 Moore nonexistence claim is not accepted.

## Explicitly considered and excluded (this wave)

- **Schur S(6)** — lower bound 536 (Ageron et al., arXiv:2112.03175; shifted templates
  arXiv:2607.15034 is active); exact value INFEASIBLE (S(5)=160 took a 2-petabyte proof, Heule
  AAAI-18; S(6) is ≥ 10^6× harder). Lower-bound race is alive but crowded.
- **Perfect 1-factorization K₅₆** — settled (Pike 2019); repo already tracks K₆₄; asymptotic
  P1F conjecture now proven (Cheng–Sgueglia, arXiv:2607.09459) — small cases remain open but
  K₆₄'s entry in `research/combinatorial-designs.md` already covers it.
- **cr(K₁₃)/cr(K₁₄)** — settled 2024/25 (see C11).
- **R(3,3,4)** — settled (=30, Codish–Frank–Itzhakov–Miller 2016).
- **Hadamard 668, Costas 32/33, S(2,6,46), lonely runner k=9, D(61), u(n)** — per wave-2
  exclusion list (active specialist races / picked over).
- **Projective plane of order 12** — recognizable, but Lam-scale: >> 10^15 even with modern SAT.
- **Erdős–Straus 4/n** — verified to ≥ 10^17; pushing the verification bound is not a "smallest
  open case" in any meaningful sense.

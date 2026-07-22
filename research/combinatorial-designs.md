# Domain research: Combinatorial designs & algebraic combinatorics

Researched 2026-07-22. Scored against `context/PLAN.md` selection criteria.

Primary sources mined:
- Rosin, *Using Code Generation to Solve Open Instances of Combinatorial Design Problems*, arXiv:2501.17725 (Jan 2025) — "CPro1 paper 1".
- Rosin, *Using Reasoning Models to Generate Search Heuristics that Solve Open Instances of Combinatorial Design Problems*, arXiv:2505.23881 (May 2025) — "CPro1 paper 2".
- CPro1 code repo (https://github.com/Constructive-Codes/CPro1) — contains the exact `OPEN_INSTANCES` parameter lists per design type; instances below marked "survived CPro1" were attacked by 1000 LLM-generated heuristics × 48h runs in both papers and remain unsolved.
- Handbook of Combinatorial Designs, 2nd ed. (Colbourn & Dinitz, 2006) — chapter numbers as cited by Rosin.
- Brouwer's SRG tables (https://aeb.win.tue.nl/graphs/srg/srgtab.html), fetched 2026-07-22.
- La Jolla Combinatorics Repository (https://ljcr.dmgordon.org/), incl. the Circulant Weighing Matrix branch (github.com/dmgordo/circulant-weighing-matrices, Zenodo v1.3, Apr 2026).

Key context: Rosin's CPro1 (LLM-generated C search heuristics, ~48h/instance) solved open
instances for 7 of 16 Handbook design types. **The instances and whole design types that
survived CPro1 are the sharpest "verification frontier" markers we have** — they resisted a
serious 2025 LLM-guided attack but (for the failed types) apparently only via generic local
search, not SAT/ILP/algebraic methods. That's our opening: different attack machinery on
exactly-catalogued open instances.

A note on witnesses: every candidate below has a witness that is a single small matrix/array
(≤ a few hundred entries) verifiable in milliseconds by a 20-line script — the ideal
PLAN.md shape. Nonexistence directions would require exhaustive/SAT UNSAT proofs, which are
also finite certificates (DRAT) for the smaller instances.

---

## 1. Symmetric weighing matrices SymmW(25,16), SymmW(27,16), SymmW(29,16), SymmW(28,25)

- **Statement**: Does there exist an n×n symmetric matrix W with entries in {0,±1},
  W·Wᵀ = wI, for (n,w) ∈ {(25,16), (27,16), (29,16), (28,25)}?
  Source: Handbook of Combinatorial Designs 2nd ed., ch. V.2 (Craigen & Kharaghani, table of
  open W(n,w)); listed as open in Rosin paper 1, Table 2 (arXiv:2501.17725) with progress refs
  Georgiou et al. 2023 and Dinitz 2018.
- **Provenance/importance**: Weighing matrices are a core Hadamard-adjacent object (optimal
  weighing experiments, orthogonal designs, codes); the symmetric-existence table has been a
  standing Handbook challenge since 2006.
- **Status/frontier**: CPro1 solved (19,9), (21,9), (22,16) [reasoning model, 2025] and
  (23,16) was solved in the literature. The four above were among the Handbook's smallest open
  and were NOT in CPro1's attempted list ((22,16),(23,16) were the largest attempted) —
  i.e. essentially untouched by modern compute.
- **Witness**: one 25×25 to 29×29 {0,±1} matrix; verify = one matrix multiply.
- **Attack**: SAT encoding with symmetry breaking (entries as 2-bit vars, orthogonality as
  pseudo-Boolean constraints), plus structured search over block-circulant/bordered forms
  (the successful 2021 SRG(65,32,15,16) construction used exactly circulant-block structure).
  Also simulated annealing on ±1 supports.
- **Obscurity 4/5**: in the Handbook table but unknown outside design theory; no SAT attack on record.
- **Tractability 4/5**: n≤29, tight verifier, near-misses (22,16 fell to a heuristic).

## 2. Skew weighing matrix SkewW(30,25)

- **Statement**: Does there exist a 30×30 matrix W, entries {0,±1}, W·Wᵀ = 25I, Wᵀ = −W?
  Source: Handbook ch. V.2; Rosin paper 1 Table 1 open list {(18,9),(30,25)}.
- **Provenance**: skew weighing matrices ↔ orthogonal designs OD; long-standing V.2 table entry.
- **Status**: CPro1 solved (18,9) (2025). (30,25) survived both CPro1 papers (in the attempted
  `OPEN_INSTANCES` list) — 48h × top-2 heuristics × 2 papers failed.
- **Witness**: one 30×30 matrix; instant verification.
- **Attack**: SAT/SMS. Skewness halves the variables (determined by upper triangle, zero
  diagonal — note w=25 odd forces... actually diagonal is 0 by skewness, row weight 25). Strong
  algebraic structure: search skew-type matrices from two circulants (Goethals–Seidel arrays).
- **Obscurity 4/5**: single Handbook cell; only generic heuristics tried.
- **Tractability 4/5**: 435 upper-triangle ternary variables — well within SAT range.

## 3. Balanced ternary designs — 4 surviving open instances

- **Statement**: Does a BTD(V,B; p1,p2,R; K,Λ) exist for
  (14,18;7,1,9;7,4), (12,15;6,2,10;8,6), (12,20;4,3,10;6,4), (14,28;8,3,14;7,6)?
  (V elements in B blocks of size K with entries multiplicity ≤2; each element has p1 blocks at
  multiplicity 1, p2 at multiplicity 2; every pair appears Λ times.)
  Source: Handbook ch. VI.2 open list; Rosin paper 1 Table 1 (with Greig 2002 progress notes).
- **Status**: CPro1 solved (17,17;8,2,12;12,8), (14,21;6,3,12;8,6), (12,16;4,4,12;9,8),
  (16,16;7,3,13;13,10), (12,21;4,5,14;8,8), (16,22;9,1,11;8,5), (21,21;12,1,14;14,9);
  (12,26;3,5,13;6,5) was shown NOT to exist (Greig). The first three above were in CPro1's
  attempted list and survived; (14,28;8,3,14;7,6) is Handbook-open and apparently unattempted.
- **Witness**: a V×B matrix over {0,1,2} (≤ 14×28); trivial verifier.
- **Attack**: ILP feasibility (row/column sums + pairwise inner products = Λ are all linear in
  the multiplicity indicator expansion) — surprisingly nobody appears to have run a MIP solver
  on these; also SAT and annealing.
- **Obscurity 5/5**: BTDs are niche even within design theory; zero evidence of ILP/SAT attacks.
- **Tractability 4/5**: ≤392 ternary cells; the 7 sibling instances all fell quickly once attacked.

## 4. Circular Florentine rectangles CFR(6,21), CFR(5,25), CFR(5,27), CFR(4,33)

- **Statement**: Does an r×n array exist, each row a permutation of {0..n−1}, such that for
  every ordered pair of distinct symbols (a,b) and every m ∈ {1..n−1}, at most one row has b
  exactly m cyclic steps to the right of a? Open (r,n): (6,21), (5,25), (5,27), (4,33).
  Source: Handbook ch. VI.62 (Tuscan squares chapter, Golomb–Taylor problem area); exact open
  instances from CPro1 repo `circular-florentine-rectangle/problem_def.py`.
- **Provenance**: circular Florentine arrays determine F_c(n), tied to frequency-hopping radar
  /communication sequence design (Golomb & Taylor 1985, "Tuscan squares — a new family of
  combinatorial designs", IEEE Trans. IT); F_c(n) values are a standing table with gaps.
- **Status**: **CPro1 failed on this entire design type in both papers** (solved dev instances,
  no open instance) — one of the 9 resistant types. No published SAT attack found.
- **Witness**: e.g. a 4×33 array of symbols; verification is O(r²n²), instant.
- **Attack**: SAT with row-symmetry breaking (fix first row = identity); alternatively model as
  edge-disjoint decomposition of circulant digraphs (each row is a Hamiltonian-type sequencing);
  metaheuristics on permutation space failed → prefer complete solvers.
- **Obscurity 5/5**: essentially untouched by modern complete-search compute.
- **Tractability 3/5**: permutation constraints are SAT-heavy but n≤33 is plausible.

## 5. Tuscan-2 squares T2(11) and T2(13)

- **Statement**: Does an n×n array exist (n=11, 13), each row a permutation of n symbols, such
  that every ordered pair (a,b) appears with b directly right of a in exactly one row, and with
  b two steps right of a in at most one row?
  Source: Handbook ch. VI.62; open instances from CPro1 repo `tuscan-2-square/problem_def.py`.
- **Provenance**: Golomb–Taylor 1985; Tuscan-k squares interpolate between row-complete Latin
  squares and full Vatican squares; T2 existence for odd non-prime-adjacent orders is the open
  frontier (known: T2(n) exists for n+1 prime, and various small orders).
- **Status**: CPro1 failed on the type entirely (both papers). Only 11×11 and 13×13 — decades-old
  open cells at tiny size.
- **Witness**: an 11×11 or 13×13 Latin-row array; instant check.
- **Attack**: SAT/SMS (this is exactly the shape SAT-modulo-symmetries handles: row/column
  permutation symmetry); also exhaustive DFS with strong pruning may even be feasible for n=11 —
  worth an attempt at full resolution (exists or not).
- **Obscurity 5/5**: nobody appears to have thrown complete search at n=11 despite its size.
- **Tractability 4/5**: n=11 possibly exhaustible; n=13 SAT-plausible.

## 6. Perfect Mendelsohn designs with block size 6: (9,6), (10,6), (12,6), (15,6), (16,6), (18,6)-PMD (+ (14,7), (15,7))

- **Statement**: A (v,k)-PMD is a collection of cyclically ordered k-tuples of a v-set such that
  every ordered pair (x,y) is "i-apart" in exactly one block, for each i=1..k−1. Open: k=6 with
  v ∈ {9,10,12,15,16,18} and k=7 with v ∈ {14,15} (b = v(v−1)/k blocks).
  Source: Handbook ch. VI.35; open instances from CPro1 repo `perfect-mendelsohn-design/problem_def.py`.
- **Provenance**: PMDs generalize Mendelsohn triple systems; k=5 spectrum was only completed in
  2020 (Griggs & Kozlik, "The last two perfect Mendelsohn designs with block size 5", J. Combin.
  Des. 28:865–868) — the community actively closes these tables; k=6 is the live frontier.
- **Status**: CPro1 failed on the type entirely. k=6 spectrum open cases are exactly these small v.
- **Witness**: b×6 array (e.g. 12 blocks for v=9 — tiny); trivial verifier.
- **Attack**: v=9,k=6: only 12 blocks — full exhaustive/SAT resolution likely feasible (settle
  existence either way, like the 2-(22,8,4) precedent). Larger v: prescribe automorphism groups
  (rotational constructions) + SAT, the standard trick Rosin's generic heuristics didn't use.
- **Obscurity 4/5**: known to design theorists (JCD papers through 2020) but no complete-search records.
- **Tractability 5/5**: smallest instance has 72 cells; realistic full resolution.

## 7. Supersimple 2-designs — 8 open instances

- **Statement**: Does a supersimple BIBD (any two blocks share ≤2 points) exist with
  (v,b,r,k,λ) ∈ {(21,105,25,5,5), (21,126,30,5,6), (25,90,18,5,3), (21,42,12,6,3),
  (24,92,23,6,5), (26,65,15,6,3), (31,93,18,6,3), (29,58,14,7,3)}?
  Source: Handbook ch. VI.57; open instances from CPro1 repo `supersimple-design/problem_def.py`.
- **Provenance**: supersimple designs are needed for optical orthogonal codes and superimposed
  codes; spectra for k=4,5 are mostly settled in JCD literature; these are the outstanding small cells.
- **Status**: In Rosin's manual prototyping, hand-tuned local search failed; CPro1 failed in both
  papers. So this type resisted both hand-crafted and LLM-generated incomplete search.
- **Witness**: v×b 0/1 incidence matrix (≤ 31×93); instant check.
- **Attack**: ILP (all constraints linear) with orbit-based column generation under a prescribed
  cyclic automorphism (Kramer–Mesner method) — the classical tool, apparently never run on these
  specific cells; SAT as fallback.
- **Obscurity 4/5**: subcommunity-current, globally invisible.
- **Tractability 3/5**: bigger matrices; Kramer–Mesner reduction makes them plausible.

## 8. Equidistant permutation arrays: R(10,7)≥18?, R(11,7)≥18?, R(9,8)≥21?, R(10,8)≥21?, R(11,8)≥21?

- **Statement**: An EPA(n,d,m) is m permutations of {0..n−1} pairwise differing in exactly d
  positions. Open: do EPA(10,7,18), EPA(11,7,18), EPA(9,8,21), EPA(10,8,21), EPA(11,8,21) exist?
  Source: Handbook ch. VI.44 (table of lower bounds m); CPro1 repo `equidistant-permutation-array/problem_def.py`.
- **Status**: CPro1 (which solved EPA(12,8,21), raising that bound to 21) failed on these five in
  both papers. Handbook lower bounds date to the 1970s–80s (Deza et al. era).
- **Witness**: an 18×10 array of permutations; trivial verify.
- **Attack**: clique search in the graph of permutations at Hamming distance exactly d (max-clique
  solvers, e.g. through nauty-canonical pruning), SAT, and annealing over permutation tuples.
  The exact-clique formulation has apparently never been run with modern max-clique codes.
- **Obscurity 4/5**; **Tractability 3/5**: S₁₀ is big but clique formulation is clean.

## 9. Strongly regular graph SRG(69,20,7,5)

- **Statement**: Does a strongly regular graph with parameters (v,k,λ,μ) = (69,20,7,5) exist?
  Source: Brouwer's SRG table (https://aeb.win.tue.nl/graphs/srg/srgtab.html, entry "? 69 20 7 5",
  checked 2026-07-22); also Brouwer–Van Maldeghem, *Strongly Regular Graphs* (2022).
- **Provenance**: the FIRST open entry in Brouwer's table — the smallest v for which SRG existence
  is undecided. Every design theorist knows the table; the specific cell is obscure to outsiders
  (unlike Conway's 99-graph which carries a $1000 prize). Others nearby also open:
  (85,30,11,10), (85,42,20,21) [conference graph on 85 vertices], (88,27,6,9), (96,35,10,14),
  (99,42,21,15), (100,33,8,12).
- **Status**: (65,32,15,16) — previously the smallest open — was constructed in 2021 by Gritsenko
  (arXiv:2102.05432) using block-circulant structure, proving these cells DO fall to structured
  search. No published exhaustive or large-scale structured search for (69,20,7,5).
- **Witness**: one 69-vertex graph (2346 edge bits); verification = check A² = 20I + 7A + 5(J−I−A).
- **Attack**: structured construction (assume automorphism of prime order p | plausible group
  orders; block-circulant adjacency à la Gritsenko: 3 circulant blocks of size 23); SAT with
  cardinality constraints for the unstructured case; orderly generation for partial classification.
- **Obscurity 3/5**: the table is famous in-community; this cell has seen some (unrecorded) attempts.
- **Tractability 3/5**: 69 vertices is large for SAT but small for prescribed-symmetry search;
  the 2021 (65,...) success is a direct proof-of-concept.

## 10. Circulant weighing matrices CW(96,36), CW(105,36), CW(112,36), CW(117,36), CW(120,49), CW(132,81)…

- **Statement**: Does an n×n circulant matrix W (first row cyclic-shifted), entries {0,±1},
  with W·Wᵀ = kI exist for the open (n,k) cells? Smallest open (from the La Jolla CWM repository
  database, status "Open"): (96,36), (105,36), (112,36), (112,100), (117,36), (120,49), (120,100),
  (132,81), (140,36), (140,64), …
  Source: La Jolla Circulant Weighing Matrix Repository (https://ljcr.dmgordon.org/cwm/;
  data github.com/dmgordo/circulant-weighing-matrices, `cwm.json`, v1.3 Apr 2026); Tan's tables
  (n≤200, k≤100) had 34 open cases; Arasu–Gordon–Zhang (arXiv:1908.08447, Crypt. Commun. 2021)
  settled 12, leaving 22 open in that range.
- **Provenance**: CWMs ↔ perfect ternary sequences with two-level autocorrelation (radar,
  spread spectrum); actively maintained repository = community cares about each cell.
- **Status**: nonexistence results come from multiplier/field-descent theory; existence searches
  have been limited — a CW(n,k) is just a subset-pair (P,N) of Z_n with |P|+|N| = k and
  autocorrelation 0, a perfect target for SAT/ILP over 96–140 binary-ish variables.
- **Witness**: the first row (one ternary vector of length n); verify all n−1 autocorrelations.
- **Attack**: direct SAT/ILP on the first row with multiplier-orbit symmetry breaking
  (search over union of orbits of the multiplier group — often reduces to <30 orbit variables);
  exhaustive orbit-subset search may fully resolve several cells (either way).
- **Obscurity 4/5**: repository-tracked but no recorded modern SAT attack on the open cells.
- **Tractability 5/5**: 1-dimensional witness, massive algebraic symmetry, tiny verifier.

## 11. Small open BIBDs: 2-(46,6,1) [=S(2,6,46)], 2-(51,6,1), 2-(40,13,3), 2-(39,13,6), 2-(40,14,7)

- **Statement**: Does a 2-(v,k,λ) design exist for (46,6,1) and (51,6,1) (Steiner systems
  S(2,6,46), S(2,6,51)), and for (40,52,13,10,3), (39,57,19,13,6), (40,60,21,14,7) (Handbook
  ch. II.1 open list, as encoded in CPro1 repo `balanced-incomplete-block-design/problem_def.py`)?
- **Provenance**: S(2,6,46) is the smallest admissible open Steiner 2-design instance — a
  benchmark question in every design-theory survey since the 1970s (after 2-(22,8,4) was killed
  by Bilous–Lam et al. 2007, JCD 15:262–267, via a huge exhaustive computation).
- **Status**: active subcommunity progress on larger k=6 cases (Hetman et al. 2024–2026 solved
  S(2,6,121), S(2,6,126), S(2,6,226), S(2,6,441) — arXiv:2401.08274, arXiv:2511.05191), which
  shows the area is warm, but v=46,51 resist because point-transitive assumptions fail; CPro1
  failed on all BIBD open instances.
- **Witness**: 46 points × 69 blocks incidence matrix (for S(2,6,46)); trivial verify.
- **Caveat**: S(2,6,46) has absorbed real (group-restricted) compute over decades → less "untouched"
  than others here; the non-Steiner cells (40,13,3) etc. are far less picked-over.
- **Attack**: Kramer–Mesner ILP with small prescribed groups (order 2,3,5 automorphisms —
  the unexplored middle ground between trivial and transitive); SAT with DRAT for nonexistence
  of strongly-structured subcases.
- **Obscurity 2/5** (S(2,6,46)) to **4/5** (the λ>1 cells); **Tractability 2/5**: large search spaces.

## 12. Costas arrays of order 32 and 33

- **Statement**: Does a permutation matrix of order n=32 (resp. 33) exist with all n(n−1)/2
  displacement vectors between dots distinct? Source: Handbook ch. VI.9; open instances in CPro1
  repo `costas-array/problem_def.py`.
- **Provenance**: sonar/radar signal design (Costas 1975); orders 32, 33 are the smallest unknown.
- **Status**: exhaustive search completed through n=29 (Drakakis et al. 2011); 32/33 have seen
  DECADES of serious compute (FPGA-based enumeration attempts, IEEE literature) — including CPro1
  (failed). Included for completeness as the domain's most famous small open instance.
- **Witness**: one permutation of length 32.
- **Attack**: only plausibly via new structural insight (e.g. LLM-guided restriction to
  near-algebraic constructions); raw search is hopeless (~10³⁵ space).
- **Obscurity 1/5** (well-known, heavily attacked); **Tractability 1/5**. Anti-candidate — listed
  so Phase 2 knows it was considered and why it's excluded.

## 13. Perfect 1-factorization of K₆₄ (smallest open case of Kotzig's conjecture)

- **Statement**: Does K₆₄ admit a 1-factorization into 63 perfect matchings such that the union
  of every two distinct 1-factors is a Hamiltonian cycle? (Kotzig 1963 conjectures yes for all
  K₂ₙ.) Source: Handbook ch. VI. (one-factorizations); Pike, *A perfect one-factorisation of K₅₆*,
  arXiv:1810.08734 (J. Combin. Des. 2019), which states the then-smallest open orders; after
  K₅₆, the smallest order covered by no known family/sporadic result is 64 (2n with neither
  2n−1 nor n prime, no sporadic solution).
- **Provenance**: Kotzig's conjecture is a top-listed open problem in one-factorization surveys
  (Wallis; Dinitz); each new order is a JCD-publishable result. A 2026 preprint proves the
  conjecture asymptotically (arXiv:2607.09459), sharpening interest in small cases.
- **Status/frontier**: K₅₂ (Wanless et al.), K₅₆ (Pike 2019, found via starter-based search with
  ~months of CPU). K₆₄ has no published dedicated search.
- **Witness**: a 63×32 schedule (or a starter in a group of order 63 + one vertex ∞);
  verification: check 63·62/2 pairwise unions are Hamiltonian — seconds.
- **Attack**: starter-based search in Z₆₃ (even-starters), as Pike did for K₅₆ — the search space
  for starters is astronomically smaller than raw 1-factorizations; SAT on the starter vector;
  simulated annealing on starters scores well.
- **Obscurity 3/5**: conjecture known, specific order untouched.
- **Tractability 3/5**: K₅₆ took heavy but not extreme compute; 64 is the next rung.

## 14. Skew-Hadamard matrix of order 356

- **Statement**: Does a Hadamard matrix H of order 356 exist with H = I + S, Sᵀ = −S?
  Source: Đoković, *Hadamard matrices: skew of orders 276 and 292…*, arXiv:2301.02751 (2023),
  which constructed the previous two smallest open skew orders (4·69, 4·73) and states the
  remaining open v ≤ 100 list; smallest remaining open skew order is 4·89 = 356.
- **Provenance**: skew-Hadamard existence (conjectured for all n ≡ 0 mod 4) is the main open
  sub-conjecture of the Hadamard program; tracked in Cati–Pasechnik's Hadamard database
  (arXiv:2411.18897).
- **Status**: standard attack (Goethals–Seidel with good matrices / D-optimal-style pairs of
  length 89) has been tried by Đoković's school with classical annealing; no SAT-era attack known.
- **Witness**: four circulant ±1 sequences of length 89 (Goethals–Seidel plug-in) — a 356-bit
  effective witness; instant verification.
- **Attack**: LP/SAT hybrid on the four-sequence autocorrelation system; compression/DFT filtering
  (as in Legendre-pair searches) to prune; note the full-orbit space ~2³⁵⁶ but PSD/DFT constraints
  cut it drastically.
- **Obscurity 3/5**; **Tractability 2/5**: the 668 Hadamard analogue has an active dedicated
  project (ulam.ai 2026 status report) — skew-356 is comparatively neglected. Avoid plain
  Hadamard-668 itself (heavy prior compute).

---

## Ranking summary (best DGG-profile first)

| # | Problem | Obscurity | Tractability | One-line pitch |
|---|---|---|---|---|
| 10 | Circulant weighing matrices CW(96,36)… | 4 | 5 | 1-D witness, huge algebraic symmetry, repository-tracked, no SAT attack on record |
| 6 | (v,6)-PMDs, v=9..18 | 4 | 5 | (9,6)-PMD has a 12-block witness; full resolution plausible; community just closed k=5 in 2020 |
| 3 | BTD 4 surviving instances | 5 | 4 | Pure ILP-feasibility problems nobody has given to a MIP solver; 7 siblings fell instantly |
| 5 | Tuscan-2 squares T2(11), T2(13) | 5 | 4 | 11×11 open since 1985; CPro1-resistant; SAT/exhaustive could settle either way |
| 1 | SymmW(25,16)+3 more | 4 | 4 | Handbook cells just past the 2025 frontier; unattempted |
| 2 | SkewW(30,25) | 4 | 4 | Survived 2× CPro1; skew structure halves the SAT encoding |
| 4 | Circular Florentine CFR(6,21)… | 5 | 3 | Whole type resisted CPro1; radar-sequence community cares |
| 7 | Supersimple designs (8 cells) | 4 | 3 | Resisted manual + LLM search; Kramer–Mesner ILP unexplored |
| 8 | EPA five open cells | 4 | 3 | Clean max-clique formulation never run with modern solvers |
| 9 | SRG(69,20,7,5) | 3 | 3 | Smallest open SRG; 2021 (65,…) success is the blueprint |
| 13 | Perfect 1-factorization K₆₄ | 3 | 3 | Next rung after Pike's K₅₆; starter search is compact |
| 14 | Skew-Hadamard 356 | 3 | 2 | 356-bit witness via Goethals–Seidel; neglected vs Hadamard-668 |
| 11 | S(2,6,46) & small open BIBDs | 2–4 | 2 | Landmark but picked-over; λ>1 cells fresher |
| 12 | Costas 32/33 | 1 | 1 | Anti-candidate: decades of exhaustive compute already |

### Verification-of-openness notes (as of 2026-07-22)
- All Rosin-derived instance lists cross-checked against both arXiv papers (v-latest) and the
  CPro1 GitHub `OPEN_INSTANCES`; instances CPro1 or 2025 literature solved are excluded above.
- SRG(65,32,15,16) is SOLVED (Gritsenko 2021) — do not use; (69,20,7,5) confirmed "?" in
  Brouwer's live table.
- 2-(22,8,4) is SOLVED (nonexistent, 2007) — the "smallest open BIBD" folklore is stale; do not use.
- Skew-Hadamard 276 and 292 SOLVED (Đoković 2023); 356 is the frontier.
- Hadamard 668 has an active dedicated compute project (ulam.ai, Mar 2026) — excluded per
  "low prior compute" criterion.
- No design-theory entries found among the 2025–26 AI-assisted Erdős-problem resolutions that
  affect the above.

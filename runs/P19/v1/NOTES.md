# P19 v1 — Wide Partition Conjecture (free-matroid case): direct CP-SAT search

Run: 2026-07-23, branch `runs/P19-v1`. Variant V1: enumerate wide partitions by
increasing size, test Latinness with CP-SAT, bias to near-tight dominance.

## Statement fidelity (checked against primary sources)

- **CFGV 2003** (Chow–Fan–Goemans–Vondrák, *Adv. Appl. Math.* 31 (2003) 334–358;
  arXiv math/0205288, re-read this run via ar5iv):
  - Def. 1: μ ⊆ λ iff the multiset of parts of μ is a **submultiset of the parts** of λ
    (equivalently: delete rows of the Young diagram). NOT arbitrary sub-diagrams.
  - Def. 2: λ is **wide** iff μ ⪰ μ′ (dominance vs conjugate) for **all** μ ⊆ λ.
  - Conjecture 1 (**WPC for free matroids**): λ is wide iff there is a tableau of shape λ
    with (1) row i containing exactly the integers 1..λ_i and (2) all columns having
    pairwise-distinct entries (= λ is **Latin**). Latin ⇒ wide is proved there
    (Reiner's argument); the converse is the open direction.
  - Matches Open Problem Garden "Wide partition conjecture" (Chow–Taylor) word for word.
- **Chow–Tiefenbruck 2025** (*Electron. J. Combin.* 32(2) #P48; arXiv 2408.04086): the more
  general Latin Tableau Conjecture (shape λ, type μ). Its λ-Latin specialization agrees.
- The problem file `problems/P19-wide-partition.md` says "μ ⊆ λ ... subpartition"; per the
  original source this means submultiset of PARTS (rows), which is what we encode.

Encoding conventions: partitions as weakly-decreasing tuples of positive ints; dominance
compared by prefix sums with zero-padding (|μ| = |μ′| always, so dominance is well-defined).

## Priority check (per METHODOLOGY.md widened scope)

Searched 2026-07-23:
- **Exa web/literature search**: "wide partition conjecture counterexample", "Latin tableau
  conjecture resolved/proof", "…refuted", "exhaustive verification". Result: conjecture is
  OPEN. Newest primary work is Chow–Tiefenbruck (published 2025-06-20), which states the
  conjecture is open and proves the type-conjecture correct for the first 4 parts of μ.
- **arXiv API** (all:"wide partition conjecture", newest first): nothing resolving it.
- **GitHub repo+code search (authenticated)**: "wide partition conjecture", "latin tableau
  conjecture", "latin tableau". Only hits: google-deepmind/formal-conjectures
  `Paper/LatinTableau.lean` (statement only, merged PR #1385, status open);
  AllenGrahamHart/FormalConjectures-Bench (prove/refute benchmark tasks, no resolution);
  OEIS/RSS mirrors. No resolution artifacts.
- **Zenodo API**: `"wide partition conjecture"` → 0 hits. `"Latin tableau"` → 1 hit:
  `seventh-horizon/latin-tableau-proof` v1.0.9-arxiv (DOI 10.5281/zenodo.17345030,
  2025-10-13, author "kaleb-horizon"). **Inspected the archive**: the LaTeX source is a
  14-line stub whose abstract literally reads "Replace this with your full proof text";
  no mathematics at all; GitHub repo deleted. NOT a scoop — telemetry-pipeline test junk.
- **OpenReview API**: no relevant notes.
- Residual risks: an academia.edu item "A CONSTRUCTIVE AI PROOF OF THE LATIN TABLEAU
  CONJECTURE WITH APPLICATIONS" (2025, not peer-reviewed, contradicted by the June-2025
  EJC paper stating the conjecture open; treated as noise, not downloaded/verified).
  Paywalled venues not exhaustively swept.

## Known verification frontiers (prior art — what "new" must exceed)

- CFGV 2003: WPC for free matroids verified for **all |λ| ≤ 65** and for all λ fitting in a
  **10×10 square**; includes all indecomposable wide partitions with ≤ 5 parts.
- Chow–Tiefenbruck 2025: the (stronger) Latin Tableau Conjecture verified for all λ fitting
  in a **12×12 square**.
- So a new citable frontier for wide ⇒ Latin requires exhaustive |λ| ≤ N with **N ≥ 66**
  (the new territory being wide λ with |λ| in 66..N that do not fit in a 12×12 box, i.e.
  λ₁ ≥ 13 or ℓ(λ) ≥ 13).

## Method / encodings

- `search.py`: pure-Python partition enumeration (descending parts); wideness by exact
  integer dominance over all distinct submultisets of parts (product of (mult+1) subsets;
  quick reject λ ⪰̸ λ′ first). Sanity check: wide-partition counts for n = 1..15 match
  OEIS **A070830** (1,1,2,3,3,5,6,9,11,14,18,23,29,35,45).
- Latin test: CP-SAT (OR-Tools 9.15) model — x[r][c] ∈ [1, λ_r], AllDifferent per row
  (λ_r cells with domain size λ_r ⇒ row is a permutation of 1..λ_i), AllDifferent per
  column (column lengths from conjugate). SAT ⇒ tableau re-checked in exact Python ints
  (`check_tableau`). UNSAT ⇒ counterexample candidate → confirm with `verify.py`.
  8-way multiprocessing, 1 CP-SAT worker per instance, 300 s cap per instance
  (none hit; `unknown.txt` would log them).
- **Near-tight bias**: within each size n, wide partitions are ordered by a tightness
  score (number of dominance equalities across all submultisets) descending, so the
  most constrained shapes — where Rota-style obstructions would live — are tested first.
- `verify.py`: independent verifier, **no external deps, no floats anywhere**. Wideness by
  the same exact-integer dominance definition (independently rewritten); Latinness decided
  by exhaustive DFS with a minimum-remaining-values cell order and zero-candidate pruning
  (heuristics affect only search order, not completeness — a NOT-LATIN answer is a full
  exhaustive proof). `--frontier N` re-verifies the whole frontier independently of
  OR-Tools. Cross-check run: see `verify_frontier_log.txt` for the n reached, with wide
  counts and all-Latin outcomes identical to the CP-SAT sweep.
- Dead end fixed mid-run: the first verifier DFS filled cells row-major with a row-only
  forward check; (13,1) already thrashed (12! backtracks: the bottom cell forces 1, but
  the conflict is only seen after row 1 completes). MRV ordering fixed it instantly.

## Results (final, after coordinator-requested extension)

- **No counterexample found. Exhaustive frontier: wide ⇒ Latin verified for all
  |λ| ≤ 78** (3,912,370 wide partitions tested in total; per-size counts in
  `search_log.txt` + `search_log_73up.txt` match OEIS A070830 for every n = 1..78,
  e.g. a(78) = 431244).
- Sizes **66..78 are new territory** beyond the published |λ| ≤ 65 frontier (CFGV 2003);
  in particular this includes all wide λ of size ≤ 78 with λ₁ ≥ 13 or ℓ(λ) ≥ 13, which
  are not covered by the 12×12-box check of Chow–Tiefenbruck 2025 either.
- **Targeted deep search beyond the frontier** (`deep_search.py`, `deep_log.txt`):
  near-tight-biased hill-climb over wide partitions at each size n = 79..120, seeded
  with padded staircases (self-conjugate ⇒ maximally tight dominance) and random wide
  partitions; 150 distinct wide partitions CP-SAT-tested per size (6,300 additional
  instances, all SAT with exact tableau re-check). No candidate, no timeout.
- Every CP-SAT model was SAT (Latin tableau found) and every returned tableau re-checked
  with exact integer arithmetic; `candidates.txt` / `unknown.txt` were never created
  (no UNSAT, no timeout at 300 s cap).
- Independent cross-check: `verify.py --frontier` (pure Python, MRV DFS, no OR-Tools,
  no floats) independently re-verified the entire frontier for **n ≤ 62** with identical
  wide counts and all-Latin outcomes (`verify_frontier_log.txt`; stopped there — single
  core, is_wide enumeration dominates).
- Negative result, but the frontier extension is itself citable per the problem file.
- Wall time: 18,002 s for the n ≤ 72 CP-SAT sweep + 27,601 s for n = 73..78
  (concurrent with the deep search, ~25,700 s), 8 cores.

## Second extension: full Latin Tableau Conjecture (shape + type) sweep

Coordinator asked to push further "another way", so we attacked the **stronger**
conjecture (Chow–Tiefenbruck 2025, of which wide ⇒ Latin is the specialization):
*a Latin tableau of shape λ and type μ exists iff δ(λ) ⪰ μ*, δ = chromatic
difference sequence. A counterexample here could exist even if wide ⇒ Latin holds.

- **Reduction used (proved, CT Prop. 2)**: achievable types form a down-set in
  dominance order, so LTC ⟺ for every shape λ a Latin tableau of type exactly δ(λ)
  exists. One feasibility test per shape.
- δ computed exactly (integers only) via CT Theorem 1 corner constraints:
  α_r = min_{i,j≥0} [ r(i+j) + Σ_{k>i} max(λ_k − j, 0) ], δ_r = α_r − α_{r−1};
  sanity-checked (δ((4,2,1)) = (3,2,1,1), δ((3,3,3)) = (3,3,3), δ weakly
  decreasing and summing to |λ| asserted for every shape).
- `ltc_search.py`: CP-SAT boolean encoding x[r,c,k] (cell gets color k), exactly-one
  per cell, at-most-one per color per row/column, Σ x[·,k] = δ_k; SAT tableaux
  re-checked exactly (shape, distinctness, sorted multiplicities == δ).
- `ltc_verify.py`: independent pure-Python verifier (no OR-Tools, no floats):
  independent δ computation + exhaustive MRV DFS with one sound symmetry reduction
  (untouched equal-multiplicity colors are interchangeable).

**Result: LTC verified exhaustively for ALL shapes with |λ| ≤ 55** — 2,984,864
shapes, every one SAT with exact re-check; `ltc_candidates.txt`/`ltc_unknown.txt`
never created (no UNSAT, no timeout at 600 s). Prior art was the 12×12 box (CT
2025), which by size covers all shapes only for |λ| ≤ 13 — so sizes 14..55 add a
large new by-size frontier (every shape with λ₁ ≥ 13 or ℓ(λ) ≥ 13 up to size 55
was previously unchecked). Independent cross-check via `ltc_verify.py --frontier`
to n ≤ 20 with identical outcomes (`ltc_verify_log.txt`). Wall time 25,399 s
(~7 h) on 8 cores (`ltc_log.txt`).

## Fourth attack: ALL indecomposable wide partitions with ≤ 6 parts are Latin

CFGV Def. 5: a wide λ is *decomposable* if λ = μ + ν (partwise sum) with μ, ν wide;
Prop. 5: for each fixed number of parts ℓ there are only finitely many indecomposable
wide partitions. CFGV's 2003 check covered all indecomposables with **≤ 5 parts**
(their |λ| ≤ 65 sweep). This run pushes that class-complete milestone to **ℓ = 6**,
a result covering partitions of unbounded size (up to decomposition).

Method (`indec6.py`): DFS-enumerate wide partitions with exactly ℓ parts and first
part ≤ B (sound pruning: every prefix is a subpartition, hence must be wide); filter
to indecomposables by exhaustive search over wide summand splits; CP-SAT Latin test
with exact integer re-check of every tableau (rows are exact permutations, columns
distinct).

Results (logs `indec5_log.txt`, `indec6_log.txt`):
- ℓ = 2: 3 indecomposables (max λ₁ = 3), all Latin.
- ℓ = 3: 11 (max λ₁ = 5, max |λ| = 15), all Latin.
- ℓ = 4: 45 (max λ₁ = 8, max |λ| = 30), all Latin.
- ℓ = 5: 193 (max λ₁ = 10, max |λ| = 48 ≤ 65 — consistent with CFGV's claim that
  their sweep covered all ℓ ≤ 5 indecomposables), all Latin.
- **ℓ = 6: 852 indecomposable wide partitions (max λ₁ = 12, max |λ| = 70), all
  Latin — zero UNSAT/UNKNOWN.** Note max |λ| = 70 > 65: some ℓ = 6 indecomposables
  lie beyond CFGV's sweep (though inside our |λ| ≤ 78 frontier).
- Completeness margin (`indec6_margin.py`, log `indec6_margin_log.txt`): enumerated
  all 14,077,760 wide 6-part partitions with λ₁ ∈ [31, 45] (tails are wide 5-part
  partitions) and verified **every one is decomposable** — so the B = 30 cutoff
  misses no indecomposable (empirical max λ₁ is 12, margin 12 → 45).

Caveat recorded honestly: "sum of Latin partitions is Latin" is NOT a proved closure
(CFGV prove wideness is closed under +, Prop. 4/Cor.), so this does not formally
reduce the WPC to indecomposables; it is the same class-complete verification level
CFGV themselves reported for ℓ ≤ 5, advanced one level to ℓ = 6.

## Dead ends / notes

- (2,1,1): not wide (submultiset (1,1) ⪰̸ (2)) and not Latin — consistent.
- Wideness check cost is dominated by submultiset enumeration for many-distinct-part
  partitions; fine through n ≈ 72. CFGV Prop. 3 ("lower subpartitions suffice") could
  speed this up but was not needed (we deliberately check the raw definition).
- CP-SAT per-instance time ~15–30 ms at n ≈ 30; all instances SAT so far, i.e. the
  models are easy; the compute is dominated by instance count (A070830 growth ~52k at
  n = 60, ~174k at n = 70).

## Compute

Single 8-core VM (Devin session), OR-Tools CP-SAT 9.15.6755, Python 3.
Total wall time: see final line of `search_log.txt`.

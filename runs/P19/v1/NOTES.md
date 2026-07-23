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
  by exhaustive DFS with forward checking (no symmetry breaking — a NOT-LATIN answer is a
  full exhaustive proof). `--frontier N` re-verifies the whole frontier independently
  of OR-Tools. Cross-check run: frontier re-verified to n ≤ 40 with identical wide counts
  and all-Latin outcomes (see `verify_frontier_log.txt`).

## Results

See `search_log.txt` (per-size wide counts + timing) and `frontier.txt` (final frontier).

- **No counterexample found.** Every wide partition tested is Latin (CP-SAT SAT + exact
  re-check of the returned tableau). `candidates.txt` / `unknown.txt` never created.
- Exhaustive frontier reached: see `frontier.txt` (target N = 72; prior published
  frontier |λ| ≤ 65, so sizes 66..N are new territory).
- Negative result, but the frontier extension is itself citable per the problem file.

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

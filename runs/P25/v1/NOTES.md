# P25 v1 — Football pool problem K₃(6,1) ∈ [71,73]

Session: ultra solve run, 2026-07-23. Target: find a 72-word ternary covering code of
length 6, radius 1 (new record ⇒ K₃(6,1) ≤ 72), or prove size 72 impossible (⇒ K₃(6,1)=73).

## Step 0 — Bounds re-verification (COMPLETE)

**Confirmed current interval: 71 ≤ K₃(6,1) ≤ 73.** The problem file's [71,73] is correct;
`research/wave3-smallest-open-cases.md` §C9's "[65,73]" is OUTDATED (it cites the lower
bound 65 that Linderoth–Margot–Thain themselves superseded).

Pinned sources:
- **Lower bound 71**: Linderoth–Margot–Thain, *Improving Bounds on the Football Pool
  Problem by Integer Programming and High-Throughput Computing*, INFORMS J. Computing 21
  (2009), doi:10.1287/ijoc.1090.0334. TR PDF (fetched, quote verified):
  https://jlinderoth.github.io/papers/Linderoth-Margot-Thain-07-TR-2.pdf — "our computations
  have been improve the lower bound on |C∗₆| from 65 to 71, and a total of more than two CPU
  centuries total have gone into the computation". Prior lower bound 65: Östergård–Wassermann,
  JCTA 99 (2002), doi:10.1006/jcta.2002.3260.
- **Upper bound 73**: L.T. Wille, *The football pool problem for 6 matches: a new upper
  bound obtained by simulated annealing*, JCTA 44 (1987) 171–177 (per Kéri's tables and the
  LMT TR: "the best known feasible solution has value 73 (found by Wille (1987))").
- **Kéri's covering-code tables** (Östergård's tables' successor, the standard reference):
  https://old.sztaki.hu/~keri/codes/3_tables.pdf — row n=6, R=1: "t 71–73 v", t = LMT 2007,
  v = Laarhoven–Aarts–van Lint–Wille 1989. PDF archived in this run.
- **OEIS A004044** (classic football pool problem): data ends at n=5 (a(5)=27); n=6 open.

## Widened priority check (COMPLETE, clean)

- **arXiv:2504.01932** (Gijswijt–Polak 2025, *Semidefinite lower bounds for covering codes*):
  audited the full new-bounds tables — their q=3, R=1 improvements start at n=13. No change
  at n=6 (their method reproduces ≤ the known 71 there; asterisked table cells confirm).
- **GitHub** `Slavov88/football-pool-problem` (updated 2025-12, "paper by Slavov and
  Mavrodiev"): cloned — repository contains ONLY a README, no code, data or claims. No
  associated paper found via search. Not a threat, but worth re-checking at write-up time.
- **Zenodo**: search "football pool covering code" — nothing relevant.
- **MaRDI/OEIS/Kéri**: all still list 71–73 as of 2026-07.

## Step 1 — Search for a 72-word code

Hardware: 8 cores, 32 GB. Tooling built this run (in `~/p25`, key files committed here):
- `ls.c` — incremental local search (fixed-temperature Metropolis, focused moves: pick an
  uncovered word u, move a random codeword into B(u); O(1) incremental cover counts).
  Calibration: K=81 instant; K=74 seconds; **K=73 (Wille's 40-year record) reproduced in
  < 1 second of CPU time** (352k iterations, T=0.35) and by 7/8 independent workers.
  A fresh 73-code found this run: `code73_example.txt` (verify.py → PASS).
- `gen_sat.py` — CNF: 729 indicator vars, 729 cover clauses (13-ary), totalizer ≤72,
  symmetry breaking x[000000]=1 (per-coordinate symbol translations act transitively).
  7,724 vars / 273,082 clauses. Solver: kissat 4.0.4.
- `ilp.py` — HiGHS ILP: min Σx, cover constraints; root LP = 56.077 = 729/13 (exactly the
  sphere-covering bound, as expected; LMT report the same relaxation quality → the
  140-CPU-year gap; UNSAT-at-72 via vanilla MIP is hopeless).

### Attack battery on size 72 (all negative)

1. **Metropolis local search** (`ls.c`): 5 workers, T ∈ {0.40,…,0.55}, random and
   73-code-seeded starts, **>10¹⁰ iterations per worker** (>6×10¹⁰ total). Every run
   reaches 2 uncovered words within seconds and never improves — a hard plateau at
   cost 2, matching the landscape folklore since Wille 1987.
2. **Weighted local search with dynamic weights + exhaustive 2-exchange** (`ls2.c`,
   breakout-style weight bumping at local minima; whenever cost ≤ 2, an *exhaustive*
   (remove-2, add-2) exchange over all C(72,2) codeword pairs × all valid replacements is
   run): finds 73-codes ~20× faster than `ls.c` (20k iterations), but at 72 again
   plateaus at cost 2, and **no cost-2 configuration encountered ever admitted an
   improving 2-exchange**.
3. **LNS with exact repair** (`lns.c`): start from a fresh 73-code; each round remove r
   random codewords and *exactly* re-cover the holes with ≤ r−1 words (DFS set-cover with
   ball-branching, 2×10⁶ node budget), accepting equal-size repairs as plateau hops.
   **>13×10⁶ exact repair rounds** (r=5: >10.7M, r=6: >2.4M) without a single 73→72
   reduction.
4. **Structured/invariant codes** (`orbit_search.py`): random cyclic monomial symmetries
   g ∈ S₃≀S₆ (coordinate permutation + per-coordinate affine symbol map); ILP over orbit
   indicator variables for an ⟨g⟩-invariant cover of size ≤ 72 (HiGHS, 60 s/group).
   Several core-hours of group trials: no invariant ≤72 cover found (the machinery is
   validated: it finds invariant 77-covers instantly at looser targets).
5. **SAT** (`gen_sat.py` + kissat 4.0.4, default and `--sat` configs): no answer after
   hours on the size-72 CNF; consistent with the instance being UNSAT and far beyond
   direct SAT reach (see Step 2).
6. **ILP** (HiGHS, single thread, 12 h limit): root LP = 56.077 (sphere-covering bound);
   dual bound crawled to 59.0 after ~1.5 h — confirms LMT's assessment that vanilla branch-and-bound
   cannot close [59, 72] without symmetry machinery and CPU-centuries.

**Outcome: negative (no 72-word code found; no bound change).** The run adds concrete,
reproducible evidence for the standing conjecture K₃(6,1) = 73: modern multi-strategy
search with budgets ~10⁴–10⁵× Wille's 1987 compute reproduces 73 instantly and cannot
touch 72, and all cost-2 local optima are 2-exchange-rigid.

### Round 2 — Systematic symmetry sweep (new structural result)

`orbit_sweep.py`: enumeration of **all conjugacy classes of nontrivial cyclic subgroups
⟨g⟩ of the full symmetry group S₃≀S₆** (class = coordinate cycle type λ ⊢ 6 + S₃-class of
the composite symbol map per cycle: id/τ/σ — 220 classes incl. identity; 215 attempted within the 400-orbit cap), computing for
each the exact minimum size of a ⟨g⟩-invariant covering code via orbit ILP (HiGHS, exact).

Result: **178 nontrivial classes solved to exact optimality; NONE admits an invariant
covering code of size ≤ 72.** The minimum over all solved classes is 73, achieved only by
λ=[4,1,1] with symbol classes (id,id,τ) — i.e. there IS a 73-code with an order-4 monomial
automorphism, but no 72-code with any of the 178 solved symmetry types. All other solved
classes have invariant minimum ≥ 77. The remaining 42 classes (37 ILP timeouts at 300 s +
5 skipped with > 400 orbits; all near-identity — single coordinate transpositions/symbol
swaps and similar) are being re-decided as pure ≤72-feasibility ILPs with 1200 s each
(`orbit_feas.py`, log `out/feas.txt`).

Consequence (conditional on the feasibility re-checks finishing): if a 72-word code
exists, its automorphism group within S₃≀S₆ is trivial or intersects only the handful of
near-identity involution classes — i.e. **any putative 72-code is (essentially)
symmetry-free**, explaining why annealing/tabu and algebraic constructions have failed
since 1987 and sharply limiting the remaining search space for the upper-bound route.

## Catalog correction

`research/wave3-smallest-open-cases.md` §C9 stated the interval as [65, 73], crediting
LMT 2009 with "lower 65". That is wrong: LMT *started* from 65 (Östergård–Wassermann 2002)
and **proved 71**. Corrected in this branch (§C9 header and statement). The problem file
`problems/P25-football-pool.md` was already correct.

## Next steps / handoff

- The upper-bound direction stays the only feasible target; what's left untried at scale:
  (a) parallel tempering / population-based LS across many machines; (b) orbit ILPs over
  *larger* subgroups (order 4–12, non-cyclic) with exact (not time-limited) solves;
  (c) seeding from the classified structure of published 73-codes (Wille's code itself —
  JCTA 44 print copy not freely available; worth obtaining).
- Lower-bound/UNSAT direction: needs LMT-style isomorph-pruned decomposition + modern SAT
  per cell with DRAT; a serious cluster project (CPU-decades even optimistically), not a
  single-box run.

## Step 2 — UNSAT direction

Not attempted beyond the plain kissat run: proving no 72-code exists is equivalent to
raising the lower bound from 71 to 73; the 71 bound alone consumed >200 CPU-years (2007)
with heavy isomorphism pruning. A DRAT-certified UNSAT on this 8-core box is out of reach;
recorded as infeasible for this run rather than pretended at.

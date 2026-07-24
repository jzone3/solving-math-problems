# P15 — V5 (literature-first) run notes

Session: https://app.devin.ai/sessions/63d681e694694b4fb0b4f846eca6da53
Branch: runs/P15-v5

## 1. Statement re-verification against original sources (2026-07-22)

- **Owens 2014 thesis** (scholarsarchive.byu.edu/etd/4329, PDF fetched, `papers/owens-thesis.pdf`):
  confirmed — constructs a covering system with distinct moduli, minimum modulus **42**,
  using all primes up to 89 (plus a large finitizing prime). Built entirely by hand,
  prime-by-prime hole-filling in Nielsen's up-arrow notation.
- **Nielsen 2009** (J. Number Theory 129, `papers/nielsen40.pdf`): min modulus **40**, primes up to 103.
- **Hough 2015** (Annals 181): every distinct covering system has min modulus ≤ 10^16.
- **BBMST** ("On the Erdős Covering Problem: the density of the uncovered set",
  arXiv:1811.03547, Invent. Math. 2022, `papers/bbmst-uncovered.*`): Theorem 8.1 —
  min modulus ≤ **616,000**.
- Literature check for anything > 42 (Exa searches, July 2026): nothing found beating 42.
  Recent related work (Klein–Koukoulopoulos–Lemieux j-th smallest modulus 2022; squarefree-moduli
  bounds 2025; function-field analogues 2024–26) — none touches the constructive record.
  **Problem confirmed open as stated.**

## 2. KEY LITERATURE FINDING — the V5 premise as written is misdirected

The problem file suggests BBMST's machinery is "EXISTENCE machinery … semi-constructive;
extract an explicit construction from their proof at any min modulus > 42".

**This is backwards.** BBMST Theorem 8.1 (verified directly in the paper text) states:
*if all moduli are distinct and ≥ 616,000, the system does NOT cover Z.* Their distortion
method bounds the density of the UNCOVERED set from below — it is a **nonexistence
(obstruction) theorem**, exactly like Hough's. There is no covering system anywhere in
their proof to extract; the number 616,000 is where their obstruction stops working, not
where a construction lives. The same holds for Hough 2015. Nothing in the
Hough/BBMST line can produce a witness for min modulus ≥ 43.

Consequence: the only known constructive technology is the
Erdős → Krukenberg (18) → Choi (20) → Morikawa (24) → Gibson (25) → Nielsen (40) → Owens (42)
lineage: prime-by-prime hole-filling over a smooth modulus tree. V5 therefore pivots to:
digest that lineage quantitatively, then compute with it (per V5's "…and only then compute").

## 3. Digest of the constructive method (Nielsen/Owens)

Structure of Owens's 42 construction (full read of thesis):
- Universe is a tree of prime-power branches: 2^6 · 3^4 · 5^3 · 7^2 · (higher primes)^1, with
  p↑ notation = one class mod p^k for every k ≥ 1 (finitized at the end by one unused large prime).
- Start with 2↑(1); delete moduli 2,4,8,16,32 (< 42) leaving holes = classes 2^k mod 2^{k+1},
  k=1..5 (density 31/32 minus the 64↑ tail).
- Prime 3 works inside branch 1 mod 2 (3↑(2,4↑) minus moduli 6..36); primes 5,7 fill the
  2-power holes; each later prime p fills one specific residual hole by assembling p−1 (or fewer,
  using inherited coverage) "sets" from products of unused smaller-prime moduli ≥ 42.
- Bookkeeping is purely combinatorial: at each hole, count assemblable sets vs inputs needed.
  Owens: primes ≤ 89 suffice for 42 (Nielsen needed ≤ 103 for 40); the improvement came from
  relocating the prime 5 and a trick with 19.
- Owens's own conclusion: pushing past 42 "would likely need … a similar dramatic change early
  on" (placement of 3/81↑, of 5) and "would likely require even more large primes".

## 4. Budget analysis (machine-verified, `budget.py`, exact rationals)

Necessary condition sum 1/m_i ≥ 1 over distinct p-smooth moduli ≥ N:
- N=42, primes ≤ 89 (Owens's palette): available budget 3.92 (excess +2.92)
- N=43, primes ≤ 89: 3.90 (+2.90); ≤ 103: 4.15; ≤ 127: 4.46
- Crossing point is already at primes ≤ 13 for N=43.

So the naive reciprocal-sum budget is NOT the obstruction — the constructions run out of
*alignment efficiency* (each class only covers what remains uncovered in its branch), not of
raw density. The binding constraint is the per-hole set-assembly count (each prime p consumes
p−1 sets of its own). This motivates a computational search where the machine optimizes the
alignment — which no published work has done.

## 5. Computational plan (this run)

Engine A (`greedy_cover.py`): exact direct search over a smooth universe N
(profile mirrors the literature: 2^a 3^b 5^c 7^d 11 13 …). Universe residues held as a
numpy uint8 array; usable moduli = divisors of N that are ≥ target minimum modulus, each
usable once; greedy (with variants: ascending-modulus, max-gain, randomized restarts +
hole-repair) picks (modulus, residue) to maximize newly covered residues via
reshape-sum counting. Any complete cover is re-verified independently (`verify_cover.py`,
different code path: CRT-free direct sweep). Escalate N and the target min modulus as far
as memory/time allow; record the max min-modulus achieved fully automatically.

(Notes below are appended as runs complete.)

## 6. Engine A results (direct greedy over smooth Z_N, exact & verified)

| universe N | factors | L | outcome |
|---|---|---|---|
| 5040 | 2^4 3^2 5 7 | 3 | **COVER** (24 classes, verified PASS) |
| 151200 | 2^5 3^3 5^2 7 | 6 | **COVER** (verified PASS) |
| 21621600 | 2^5 3^3 5^2 7 11 13 | 9 | **COVER** (205 classes, verified PASS) |
| 21621600 | same | 12 | **COVER** (405 classes, verified PASS) |
| 21621600 | same | 14 | FAIL, best 88792/21621600 uncovered (4.1e-3) over 8 restarts |
| 129729600 | 2^6 3^4 5^2 7 11 13 | 14 | FAIL, best 63090 uncovered (4.9e-4) |
| 129729600 | same | 16 | FAIL, best 447416 (3.4e-3) |
| 129729600 | same | 18 | FAIL, best 1.3e6 (1.0e-2) |

Local-search repair (repair.py, reassign one class at a time, 300 s) moves ~1% of the
uncovered mass — hopeless: the failure is structural misalignment, not local.

Diagnosis (literature-informed): pure per-class greedy cannot discover the nested
q↑-chain alignment that all record constructions use ("keep the partial cover as densely
packed as possible", Nielsen §2 Example 2 remark). Also note the Mirsky–Newman constraint:
a perfectly disjoint (zero-overlap) distinct-moduli cover cannot exist, so the necessary
overlap has to be placed intelligently — exactly what the q↑ tail-filling trick
(j mod p ∩ 0 mod q^{K-j}) does. Next: Engine B implements that machinery directly.

## 7. Engine B / Engine C — mechanizing the arrow calculus, and why naive versions fail

**Engine B** (`engine_b.py`): per-cell recursive chains (cover cell a mod M by a q-chain,
children covered recursively, tail finitized with prime p via
CRT(j mod p, chain-ancestor), the generalization of Nielsen's Example 1 trick).
Works at L=3 (25 congruences, verify_tree PASS) with a prime-diversification order,
but thrashes exponentially from modulus-registry conflicts at L >= 6:
each child cover is derived independently, so the (q-1)·K children per chain
each burn a disjoint set of moduli — combinatorial starvation.

**Engine C** (`engine_c.py`): proper arrow semantics — an input recipe R_j is built ONCE
and reused at every chain level k (moduli s^k·m all distinct along the chain "for free").
This is the actual mechanism of q↑ notation. Still fails, and the failure is instructive:
with strictly coprime layering (recipe moduli coprime to all ancestor chain primes),
the s-1 sibling inputs of a chain need pairwise-disjoint covers of Z, and below the
first two inputs ("1" and "2↑") the palette of small primes is exhausted — costs explode
as p·s^{p-1} for ever larger fresh primes.

**Finding:** the power of the Nielsen/Owens calculus is *not* just level-reuse; it is
essentially the **inherited-coverage mechanism** (the "x" entries in their tables):
recipes whose moduli are NOT coprime to the ambient branch, sound only because the
overlapping part is already covered by earlier congruences. Inheritance is not an
optimization — without it the recursion starves at L as low as 6. Any real mechanization
(the V1 program) must implement partial-cover-aware recursion; that is exactly where all
of Owens's hand-bookkeeping ("only thirteen inputs needed on this branch") lives.

## 8. Engine A at scale — automated record so far

Deeper 2-adic tail matters enormously (as the literature's 64↑ suggests):
- 2^7·3^4·5^2·7·11·13 (N=259,459,200): **L=14 COVER FOUND** (916 congruences,
  restart 1 of 12; both verifiers PASS: verify_cover.py direct sweep over lcm and
  verify_tree.py CRT-structured DFS). `witness_L14_N259459200.json`.
- Same profile with 3^5 (N=389M): restart 0 uncovered 90206 — worse than 2^7 bump.

L=15/16 sweeps running (2^7 and 2^8 profiles).

## 9. Escalation: L=15 success, L=16 near-miss

- **L=15**: 2^7·3^4·5^2·7·11·13 universe, restart 4 → **COVER, 743 congruences**
  (`witness_L15_N259459200.json`); PASS on both independent verifiers.
  Artifacts copied to `solutions/P15/` (with README-v5.md explicitly stating this is an
  automated-search frontier datapoint, NOT a claim on the >= 43 problem).
- **L=16**: three exponent profiles tried:
  - 2^7·3^4·5^2·7·11·13 (N=2.6e8): best 307,204 uncovered over 15 restarts (1.2e-3)
  - 2^7·3^4·5^3·7·11·13 (N=1.3e9): best 665,636 over 6 restarts (5.1e-4)
  - 2^7·3^4·5^2·7^2·11·13 (N=1.8e9): best **11,605 uncovered (6.4e-6)** — near-miss;
    high restart variance (next restarts 1.8e6, 1.3e5). More seeds running.
  The 7^2 profile (moduli 21, 28, 49, 63, ... available) is clearly the right direction
  for L=16, mirroring Owens's use of 7^2 in his prime-7 section.
- One earlier parallel batch of five 1.8 GB runs was OOM-killed (dmesg confirms);
  re-ran at 3-way parallelism.

Compute spent (approx): ~3.5 h of single-core numpy greedy sweeps across
N up to 1.8e9, plus ~20 min local-search repair experiments, plus Engine B/C
backtracking runs (~15 min). All exact, no sampling.

## 10. L=16 SUCCESS; L=18 out of reach for this method

- **L=16**: 2^7·3^4·5^2·7^2·11·13 universe (N=1,816,214,400), seed 950 restart 1 →
  **COVER, 1327 congruences, distinct moduli, min modulus 16**
  (`witness_L16_N1816214400.json`). PASS on both independent verifiers
  (direct lcm sweep + CRT-tree DFS, 12,898,054 cells). Copied to `solutions/P15/`.
  Restart variance at L=16 was enormous: uncovered counts across 12 restarts ranged
  0, 974, 11,605, 25,801, ..., up to 1.8e6.
- **L=17** is equivalent to L=18 on any 17-free palette (17 is not a divisor), so we
  went straight to L=18.
- **L=18**: 8 restarts on the L=16-winning profile: best 3,536,368 uncovered (1.9e-3);
  bigger universe 2^7·3^5·5^2·7^2·11·13 (N=5.4e9, 59 min/restart): 16.7e6 uncovered
  (3.1e-3). The loss of modulus 16 (=2^4) is qualitative: the 2-adic tail can no longer
  be packed, and greedy cannot compensate. L=18 needs structural (arrow-calculus) search,
  not restarts.

## FINAL

Verified artifact chain: L=3, 6, 9, 12, 14, 15, **16** — all with two independent
verifiers passing. Standing hand record is 42 (Owens); target 43 not approached.
The V5 premise (extract a >42 construction from BBMST) is unfixable: BBMST's method
bounds obstructions to coverings and is intrinsically non-constructive (Section 2 of
their paper; confirmed against the original). The constructive frontier is exactly the
Nielsen/Owens arrow calculus, whose mechanization requires inherited-coverage
bookkeeping (Section 7) — recommended as the follow-up (V1-style) program.

STATUS: negative (no progress on min modulus >= 43; byproduct: verified fully-automated
coverings up to min modulus 16, plus a precise diagnosis of what a mechanized
arrow-calculus search must implement).

## 11. Continuation push: new encodings and L=17/18 frontier

Orchestrator requested a further push with different encodings. What was done:

**Engine D (`engine_d.py`) — cell-tree encoding.** Uncovered set represented as
disjoint CRT cells (a mod M), M | N, instead of a flat bit array; per-modulus
residue choice via beam search (width 48) over partial CRT constraints on the
weight tables weight[g][a mod g], g = gcd(M, d). Removes the memory wall
(N ~ 1e13 feasible). Result: NEGATIVE for greedy quality — the beam
approximation of argmax loses to the flat array's exact argmax (L=12: residual
6.1e-2 vs 0 for flat). Fragmentation also explodes (250k+ cells at N=2.2e7).
Kept as documentation; exact argmax over the divisor lattice would need
branch-and-bound (recommended follow-up).

**17-in-palette flat sweeps (new target family).** Previous L>=17 attempts had
no modulus 17 available. New palettes (2 GB - 4.4 GB bool arrays, dtype-adaptive
counting fix from Section 9's OOM diagnosis):
- 2^7·3^4·5^2·7·11·13·17 (N=4.41e9, budget 1.865 @ L=17): best restart
  L=17: 15,547,207 uncovered (3.5e-3); L=18: 10,602,192 (2.4e-3).
- 2^7·3^4·5^2·7^2·11·17 (N=2.38e9, budget 1.655): L=17 best 19.3e6 (8.1e-3).
- 2^7·3^4·5^2·7^2·13·17 (N=2.81e9, budget 1.605): L=17 best 51.7e6 (1.8e-2).
Feasible richer palettes plateau at budget ~1.69 (vs 1.725 for the L=16 win):
within the flat-array memory envelope (~5e9), the L=17 budget ceiling is
structurally below what greedy needed for L=16. The 16 -> 17 step is a cliff
for this method family, not a tuning problem: L=16's win leaned on the dense
small moduli 14, 15, 16 (all lost at 17) and on 2^4 alignment.

Compute this push: ~4 h of parallel sweeps (restarts of 20-52 min each).

### Final L=17/18 restart table (all restarts, uncovered counts)

- L=17, 2^7·3^4·5^2·7·11·13·17: 15,547,207; 15,403,075  (3.5e-3)
- L=18, same palette:            10,602,192;  9,840,338  (2.2e-3)
- L=17, 2^7·3^4·5^2·7^2·11·17:  19,331,988; 23,330,945; 14,635,762  (6.2e-3)
- L=17, 2^7·3^4·5^2·7^2·13·17:  51,653,128; 41,893,833  (1.5e-2)

No restart came within 2 orders of magnitude of the ~1e-5 near-miss densities
that preceded the L=14/15/16 successes. Combined with the budget ceiling
analysis (Section 11), we assess L=17 as out of reach for exact flat greedy
within the memory envelope, independent of restart luck.

Also analyzed (not implemented): surgery on the verified L=16 witness —
deleting its modulus-16 class and re-covering that cell in a 17-extended
universe reduces to "cover one CRT cell with fresh distinct moduli", which is
exactly the arrow-calculus core problem (any prime chain re-creates the
16-identical-sibling modulus conflict). Reinforces Section 7's conclusion.

STATUS: negative (frontier of this run: verified automated coverings at
L=14/15/16; L=17 negative across 4 palettes, 9 restarts, ~8 h compute;
mechanization of the arrow calculus with inherited coverage remains the
recommended path to approach 43).

## 12. Engine E: arrow chains + inherited coverage (executing Section 7's recommendation)

`engine_e.py` = Engine B plus the two inheritance mechanisms:
- **inherit**: cover_cell(a, M) returns free if a placed class (r, m), m | M,
  a = r (mod m), already contains the cell;
- **guided split**: if a placed class intersects the cell (compatible on
  gcd(m, M)) covering a 1/ratio fraction (ratio = m/gcd <= 256), split the cell
  along a prime of m/gcd and recurse — the aligned sub-cell then inherits;
- **tail-first ordering**: a chain's finitizing tail classes are placed BEFORE
  the children recursion, so children inherit from them (this ordering is what
  the 'x' entries in Nielsen's tables encode).

Result: **L=6 covered structurally in 0.2 s** (292 congruences, max modulus
4.5e9) where Engine B thrashed for minutes and failed — direct evidence that
inheritance is the load-bearing mechanism. But L=10 still fails across 47
restarts with widened backtracking (q_tries 10, p_tries 8, ~1e6 calls/restart):
chains still starve on sibling-modulus conflicts that inheritance alone cannot
resolve. What is still missing vs. Nielsen's hand construction: reuse of one
recipe across chain levels combined WITH inheritance (Engine C had the reuse
but not the inheritance; each alone is insufficient), plus per-branch resource
budgeting. That combination is a substantial dedicated project (the V1
program), now precisely scoped by three measured failure modes (Sections 7, 11, 12).

(witness_E_L6.json verification: verify_cover's direct sweep is inapplicable
— lcm ~ 1e40; verify_tree run in background, slow on the deep 5-chains.)

## 13. Engine F (BFS deferral) and a third verifier

`engine_f.py`: breadth-first work-queue variant of Engine E — no backtracking;
cells that cannot be based/chained are deferred by splitting. Result: L=3 ok,
**L=6 diverges** (pending cells grow to >2e6, front modulus ~7e9): without
DFS rollback, bad early chains poison the whole tree and guided splits
multiply cells faster than inheritance retires them. Negative, documented.
Conclusion pair (E vs F): inheritance + DFS rollback works to L=6; inheritance
+ BFS deferral fails even there. The rollback is load-bearing too.

`verify_subtract.py`: third independent verifier (exact cell subtraction,
ascending-modulus order). Handles witnesses with astronomically large lcm
where the flat sweep (verify_cover) and the naive CRT tree (verify_tree, >20
min CPU, killed) are infeasible. Validated: PASS on witness_E_L3 (peak 116
cells), witness_E_L6 (**PASS, 292 congruences, min modulus 6, peak 22899
cells**), and the known-good L=15 witness (peak 593345 cells); correctly
FAILs a corrupted L=15 witness with 3 classes removed.

FINAL STATUS (unchanged): negative for min modulus >= 43; frontier of this
run: verified automated coverings at L=14/15/16 (greedy), structural
inheritance-mechanized covering at L=6 (Engine E, verified), L=10 structural
still open for the mechanized calculus; three measured failure modes now
scope exactly what a full Nielsen mechanization must add (recipe reuse +
inheritance + DFS rollback + per-branch budgeting, simultaneously).

## 14. Engine G: recipe/support algebra (Owens-transcription attempt collapsed
into machinery) and the tower-packing wall

Attempted next: mechanical transcription of Owens's thesis construction.
Finding: the thesis is NOT transcribable directly — sections 3.5-3.7 import
Nielsen's prime-11/13/19 tables "up to rearrangement" and sections 3.8-3.20
are resource-counting prose ("fill three copies of 7-up ...") that do not
specify residues; making them executable requires exactly the
inheritance-aware search machinery identified in Sections 7/11/12.

Built engine_g.py instead: a clean recipe algebra
  Recipe := ONE | Split(q,[R..]) | Chain(q,[R..]; tail p, depth K),
support(R) = exact set of relative moduli, chains reuse one recipe per level
(q^k separates levels; this is Engine C's reuse done right), global registry
of absolute moduli, per-hole prime palettes, waste-aware tail selection
(large p / deep K make chains nearly lossless), and BFS deferral.

Results: L=3 SUCCESS (79 congruences, verified PASS by verify_subtract);
L=6 covers the fat hole (1 mod 2) at measure 1.375 but then cascades: every
remaining hole's recipes are blocked and deferral diverges.

Diagnosis (the crispest form of the obstruction yet): a q-chain input needs a
2-power ladder {2^a} in its support; the q-1 inputs of the same chain, and
recipes of different holes, therefore all compete for the same 2-power x
q-power towers of moduli. Without inheritance there are only ~pi(113) towers,
far fewer than Sum_i (q_i - 1) inputs needed. Tower-packing is the wall: the
literature's 'x' entries let different inputs SHARE a tower by covering only
the residues the other branch missed. Inheritance is not an optimization of
the hand constructions -- it is what makes the modulus supply sufficient.
This is consistent across five engine families (B, C, E, F, G), each removing
a different candidate cause (backtracking, reuse, ordering, deferral,
support-exactness).

STATUS: negative (no witness with min modulus >= 43; automated frontier of
this run remains L=16 greedy + L=6 structural-with-inheritance; the concrete
open engineering problem is now precisely: recipe algebra of Engine G +
partial-cover recipes with x-marks + per-tower budgeting).

## 15. Waste-aware tails + stall-abort: Engine E pushed to its limit at L=10

Executing Section 14's conclusion (inheritance is load-bearing; chains must be
nearly lossless).  Two upgrades to engine_e.py:
  - waste-aware tail selection: finitizing prime p and depth K are chosen so
    the tail's ABSOLUTE measure sum_j 1/(p q^{K+1-j}) / M is below --eps;
    fat cells get deep nearly-lossless tails, thin cells cheap ones
    (this was the fix that also revived Engine G at L=3);
  - stall-abort restarts: a restart is killed once 2e6 recursive calls pass
    without the class count improving (prevents terminal DFS thrash).

Engine H (engine_h.py) prototypes the same as a transactional planner; its
runs confirmed the sibling-modulus observation: the q-1 level cells of a
chain share the modulus M*q^k, so only one can take it directly and the rest
must chain or inherit -- restating tower-packing at the residue level.

Compute: 6 parallel L=10 searches (eps in {0.002..0.1}, max_mod 1e15..1e18,
two caps palettes up to prime 199), ~2.5 h wall each thread.  Result: still
NO complete L=10 structural cover, but penetration is far deeper than any
prior engine: partial covers now reach 12,700+ placed classes (vs instant
starvation pre-patch), always crawling at depth 12-13 where the residual
subtree's modulus supply (caps) is exhausted.  Diagnosis unchanged and now
quantified: without per-subtree budgeting the DFS spends its cheap moduli
greedily and leaves late subtrees bankrupt.

STATUS: negative (min modulus >= 43 not achieved; structural frontier
deepened at L=10 but not closed).

## 16. Fresh-prime finisher: the depth-13 crawl eliminated, L=10 frontier at 21,475 classes

Section 15 diagnosed per-subtree modulus bankruptcy at recursion depth 12–13, where
cells have astronomically large fresh moduli M (~1e15) but the capped palette
(primes <= 199, small exponent caps) is exhausted. This continuation implements a
**guaranteed finisher** for thin cells, exploiting that a fresh huge M makes the
modulus family {p * M * 2^i} essentially collision-free:

- `Builder.finisher(a, M)`: covers any cell (a mod M) with 1/M < 1e-7 by a pure
  2-chain: tail classes j mod p at moduli p*M*2^(K+1-j) (j = 1..p) plus direct takes
  of the level cells (a + M*2^(k-1) mod M*2^k). Tail prime p is drawn from a
  dedicated reserve of primes in (199, 2000] — disjoint from the mid-band palette,
  so the finisher can never bankrupt the structured search. Exponent caps do NOT
  apply (a covering system only needs finitely many distinct moduli, not smooth
  ones); moduli up to 1e80 allowed. Verified sound via verify_subtract (PASS on
  L=6 witness, now 155 congruences vs 292 before, 0.7–9s).

Config sweep findings (all logged, eL10*.log):
- generous caps (exponents ~log_p 1e30) WITHOUT finisher: thrash at 1e6–1e7-digit band;
- finisher threshold at measure 1e-5 or 1e-3: failures migrate to just below the
  threshold — the finisher must sit strictly above the structured band;
- finisher WITH small-prime tails (p >= 3): steals mid-band towers, restart 0 dies
  at 1.4M calls — direct measurement that tower supply is the shared resource;
- finisher with p > 199 reserve + default caps + max-mod 1e16–1e18: restarts now
  reach **21,475 classes** (restart 2, eps 0.02, max-mod 1e18) and **16,381**
  (eps 0.005, 1e16) in ~25 min each vs 12.7k after 2.5 h before. Fail histogram
  (new instrumentation, fail_hist by modulus digit count) shows residual failures
  spread over the 1e2–1e7 band: the remaining obstruction is genuinely mid-band
  combinatorics (which residue/tower to give each fat hole), no longer the tail.

STATUS: negative for >=43; L=10 still not closed, frontier moved 12.7k -> 21.5k
classes and per-restart wall time cut ~6x. Next lever: smarter mid-band residue
selection (exact set-cover on the fat holes) rather than more compute.

## 17. Split fallback (negative), stall knob, long L=10 sweeps: frontier 30,090 classes

- Split fallback (on chain failure, subdivide the cell so children reach the
  finisher band): measured HARMFUL at L=10 — converts deep partial covers into a
  deterministic full-tree rollback (root Fail at ~2.3–3.0M calls). Left in the code
  behind `Builder.split_fallback = False` with the measurement documented. The
  reason: splits mask local failure and re-commit the search to hopeless residue
  assignments higher in the tree, so the eventual Fail rolls back everything.
- Tail-prime reserve enlarged to all primes in (199, 50000] (5133 primes); no
  supply failures observed since.
- New `--stall` CLI knob (calls without class-count growth before a restart is
  aborted).
- Long sweeps (eps 0.02/0.05, max-mod 1e16/1e18, stall 2M/20M, ~4.5 h so far):
  best restart reached **30,090 placed classes** (eps 0.05, max-mod 1e16,
  seed 4243) before stalling; multiple independent restarts stall in the
  16k–30k band with failures spread over the 1e2–1e7 modulus band.

Interpretation: the finisher fully solved the thin-cell (deep) half of the
problem; everything now hinges on mid-band residue assignment, where random
restarts + greedy DFS have a reproducible ceiling. STATUS: negative for >=43;
L=10 open; frontier 12.7k -> 30.1k classes this continuation.

## 18. Wide parallel restart sweep at L=10: robust ~30k-class ceiling (negative)

7 concurrent sweeps (one per core), 200-restart budgets, varied hyperparameters:
eps in {0.01, 0.02, 0.05, 0.1}; max-mod in {1e16, 1e17, 1e18}; branching width
q_tries/p_tries up to 20/16 (new CLI knobs); distinct seed blocks (11000-17000).
~4 h wall x 7 processes, 55 completed restarts total (logs par0-6.log).

Result: NO complete L=10 cover. Every restart stalls; stall points concentrate in
16,385-30,457 placed classes; best 30,457. Widening the branching (qtries 16-20)
does not shift the ceiling -- it only slows restarts. Ceiling insensitivity across
eps/max-mod/width/seed strongly indicates a structural obstruction in greedy
mid-band residue assignment, not a sampling shortfall: at ~1/2^15 residual
measure the surviving fat holes need small moduli that earlier greedy commitments
have consumed, and rollback cannot repair choices that high in the tree.

Conclusion of this line: random-restart DFS over the finisher-equipped arrow
calculus is exhausted at L=10. Closing the mid band needs a global assignment
mechanism (exact set-cover / ILP over the fat-hole--tower incidence, or
literature-table-guided placement), which is the documented next project.

STATUS: negative for >=43. Frontier this session: L=10 partial covers
12.7k -> 30.5k classes; thin-cell half of the problem solved outright by the
fresh-prime finisher (Section 16).

## 19. Engine I (fattest-first priority queue, no rollback): decisive negative

Fundamentally different control flow tested: a global heap of uncovered cells
ordered fattest-first (so fat holes get first pick of scarce small moduli),
chains place tails immediately and requeue level cells, failures split-and-
requeue (termination unconditional), thin cells closed by the finisher.

Measured outcome (engine_i.py, L=6, both default and generous caps):
- chain placement dies after ~331 (default caps) / ~1,122 (generous caps)
  classes; the ENTIRE remaining band then split-cascades (350k-517k splits,
  heap ~500k cells) until the finisher's reserve of 5,133 tail primes is
  exhausted by same-modulus sibling cells. SUPPLY FAILURE, not covered.
- variant with finisher-fallback instead of splitting dies in 17 pops: a fat
  cell's finisher recursion at small M collides with the palette everywhere
  and drains the reserve.

Interpretation: fattest-first breadth order destroys the implicit budgeting
that DFS commitment provides; without rollback, early modulus consumption is
irreversible and the whole mid band goes bankrupt simultaneously. Rollback and
depth-first commitment are not conveniences — they are how the search
implicitly rations towers. This closes the "different control flow" family.

## 20. Engine E + mid-band finisher fallback: ceiling unchanged (negative)

engine_e now tries the reserve-prime finisher on any failing cell with
M >= --finfloor (1e3/1e4/1e5 tested) before raising Fail. Four sweeps at
L=10 (eps 0.02/0.05, max-mod 1e16/1e18, seeds 21000-24000, ~2 h x 4 cores,
11 completed restarts): stalls at 9,962-23,550 classes — same ceiling as
without the fallback. Rescuing individual mid-band cells does not help
because the binding constraint is the JOINT assignment of towers to the
thousands of fat holes, not any single cell's closure.

FINAL STATUS this continuation: negative for >=43. The greedy/DFS/queue
engine family (B,C,D,E,F,G,H,I + fallback variants) is exhausted at L=10.
The documented next project remains an exact global assignment mechanism
(set-cover/ILP over fat-hole--tower incidence, or a faithful mechanization of
Nielsen's Table 1/Owens' ledger allocation).

## 21. ILP post-hoc closer (closer_ilp.py): infeasible, and a sharp theorem why

Executed the named next project: closer_ilp.py takes a stalled partial cover,
extracts the exact residual by cell subtraction, coalesces sibling shards,
generates candidate covers per residual cell (direct take, divisor take,
2-chain with tail prime p over palette + reserve, ~27 candidates/cell), and
solves the joint assignment as an ILP (CBC via PuLP): one candidate per cell,
each modulus used globally at most once, minimize total classes. Also added
--dump-stall to engine_e (snapshots the best partial cover every +500 classes
so the rollback-destroyed best state is recoverable).

Test instance (L=6 witness minus its 3 largest-modulus classes, 152 classes):
residual = 1,797 cells, measure 7.7e-8, ILP 48,519 vars / 10,842 conflict
constraints -> INFEASIBLE in 8 s. A 12-class deletion (6,110 cells, 256k vars)
is likewise infeasible. Diagnosis is structural, not a budget artifact:

  The residual concentrates into a handful of modulus FAMILIES — here just 6
  distinct moduli M carrying 264-396 same-M cells each. Every 2-chain
  candidate for a cell (a mod M) consumes the level moduli M*2^k, and these
  are the SAME integers for every cell in the family regardless of the tail
  prime chosen. So at most one cell per family can be closed by a chain
  (plus one direct take of M itself); a family of size >= 3 is already
  ILP-infeasible under any candidate library whose supports are built from
  the family's own base modulus. Fresh-prime injection cannot decouple them:
  a class with modulus p*M*2^k covers only a 1/p slice of a same-M cell, and
  any covering "recipe" for a full cell must have relative-modulus support
  with reciprocal sum >= 1, forcing small support elements that collide
  across the family (disjoint covering supports are exactly the scarce
  resource the whole problem is about).

Conclusion: post-hoc independent closure of a stalled greedy state is
IMPOSSIBLE in principle whenever the residual has same-modulus families of
size > 2 — which is always, since stalls happen exactly when a fat subtree
fragments. Tower sharing must be arranged DURING construction (the
literature's inherited-x marks align sibling residues so one tower serves
many cells); it cannot be retrofitted by any assignment solver over
independent per-cell candidates. This kills the set-cover/ILP-over-stalls
route and leaves faithful mechanization of Nielsen's Table 1 joint
allocation as the only credible remaining path to >= 43.

STATUS: negative for >= 43.

## 22. Executable Nielsen arrow-notation DSL (arrow_dsl.py) + partial min-40 transcription (nielsen40.py)

Executed the named next project: mechanize Nielsen's arrow calculus directly
from the MinimumModulus40 paper.

What was built and validated:
- arrow_dsl.py: exact executable semantics for Nielsen's prime-power tree
  notation. Primitives: Split(q, inputs) (branch a CRT cell into its q
  prime-adic input windows, paper's "q(a, b, ...)" diagrams), One (take the
  cell as a congruence class), Hole (named ledger of uncovered cells), X
  (cell claimed covered elsewhere, recorded for later verification),
  Arrow(q, inputs) (Nielsen's q^arrow: per-level inputs + closing tail
  "j mod p on the level-(n+1-j) leftover"), plus CRT/subcell helpers.
- test_arrow_dsl.py: reproduces the paper's own worked examples exactly:
  2( ,2(2( ,1), )) = 6 (mod 8); 3( ,2(1, ), ) = 5 (mod 6);
  3( , ,2(2( ,1), )) = 3 (mod 12); the explicit 2^arrow with p=5, n=5
  (10 classes, verified set equality); Example-1-style
  3^arrow(1, 2^arrow) closes to a verified covering of lcm 12960 with 49
  classes. ALL DSL TESTS PASS. First machine-level confirmation that the
  branch-window and arrow-closure conventions match the paper.
- nielsen40.py: transcription of Sections 4.1-4.3 (L=40). 4.1 leaves the 5
  expected holes at measure 31/32; 4.2 (including the refined deep inputs
  3^(2(1, ),2(2^, )) that free the 2*3^n (n>=4) moduli for the extra
  81^arrow(1,_)) leaves the expected 10-hole ledger at measure 0.8252;
  4.3 fills the m8 hole per the paper's 5(8,16^,3(...),3^(8,16^),5^(...))
  expression. Hole-ledger measures agree with the paper's narrative at each
  stage.

What failed, precisely:
- Deferred arrow closure ("multipliers made explicit at a later stage") via
  any independent per-arrow closer degenerates. Measured sequence:
  (a) small shared multipliers collide with other sections' forced level
  moduli (e.g. tail 3*2^6=192 of 4.1's 2^arrow vs level 24*2^3 of 4.2);
  (b) big-reserve-prime multipliers force n >= p-1 ~ 210 levels, blowing up
  nested structural arrows exponentially;
  (c) an engine-E-style fresh-prime 2-chain finisher on each leftover cell
  exhausts the pure dyadic integer family: closures with the same odd part
  compete for the identical M*2^k integers (depth-300 recursion);
  (d) widening to q in {2..59} with per-call level/tail reservations still
  cascades: sibling windows of nested chains consume each other's low-q
  families (measured w4-cascade, 298-deep).
  This is the same-modulus-family obstruction of Section 21 reappearing
  INSIDE the paper transcription: Nielsen's closing sections (4.13-4.25,
  "The primes 41..103") are not boilerplate — they ARE the joint allocation
  that assigns each arrow's leftover portions to shared prime towers with
  residues aligned by the inherited-x marks. A faithful reproduction of
  min-40 therefore requires transcribing those closing sections too (a
  hand-ledger of ~25 subsections), not a generic closer.

Next concrete step (scoped, unfinished): transcribe 4.4-4.12 (hole fillers)
and 4.13-4.25 (the per-prime joint closure) with explicit (p, n) per arrow
taken from the paper's text, using Arrow(..., p=, n=) which the DSL already
supports and tests; then verify with verify_subtract.py and only then
attempt the 43 scale-up.

## Section 23: symbolic layer + Section 4.4 transcribed and verified (2026-07-22)

New machinery (symbolic.py + nielsen40.py additions):
- symbolic.py: symbolic finalization of pending arrows (no level
  materialization), arrow-family collision checker `collide` (moduli
  M1*prod(q_i^a_i) vs M2*prod(r_j^b_j) intersect iff stripped parts match
  and exponent windows overlap), x-cell validation by exact cell
  subtraction, and `symbolic_verify` (accepts caller-supplied covered
  regions). test_symbolic.py: 5 tests, all pass.
- nielsen40.py: `_materialize_regions(ctx, depth)` — exact covered
  regions of the partial system: placed classes, arrow levels 1..depth
  (recursively, skipping Hole/X windows), relaxed leftover chain cells
  for arrows whose inputs are all dyadically relaxed (Nielsen: the arrow
  "applies to the entire congruence class 2 (mod 2)"), plus declared
  assumed regions for infinite families.
- `ASplit(q, inputs)`: split whose window assignment is found by
  backtracking so that every inherited-x cell an input would claim lands
  on a region already covered (Nielsen's diagram-relative window order).
  This replaced the earlier positional guess, which failed.
- 4.3 extension: the paper's extra 125^*1 — bare 5-power classes 5^a
  (a>=3) covering, at each 25^ level k>=2, the window-4 cell relaxed to
  its 5-part (window 4's 3^(4,8^) applies only to 0 mod 4); family
  {5^a} registered; deep tower beyond the truncation declared as an
  assumed region justified by level-wise induction (windows 1-3 by
  relaxed 25^ inputs, window 4 by 125^*1, window 5 descends).

Result: Section 4.4 (the prime 7, filling the modulus-4 hole on branch
2 mod 4) now transcribed and SYMBOLIC VERIFY: PASS —
  after 4.4: 11 classes, 11 hole-cells (measure 0.495470),
  77 level-1 classes, 67 under-arrow families, 15 inherited x-cells all
  validated against materialized coverage; no family collisions.
Open holes carried: h44_left (7-window-1), h44_g5, h44_g15 (paper: "one
class modulo 5 and another modulo 5*3"), plus the m6..m36 holes of 4.2.

Caveats (honest scope): x-window routing is coverage-aligned rather than
read off Nielsen's diagrams pixel-by-pixel; the 125^*1 deep-tower region
is an assumed-by-induction region, checked structurally (family
registered in the collision checker) but not yet closed into concrete
tail classes. Full closure with explicit (p,n) multipliers remains to be
done in the 4.13-4.25 transcription step.

Next: transcribe 4.5 (prime 11) .. 4.12, then the per-prime closure.

STATUS: negative for >= 43.

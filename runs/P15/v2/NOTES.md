# P15 V2 — ILP/set-cover, CRT-layered — run notes

Session: devin-290f12edb31a48feb78042038ffd568e (V2 of 5 parallel runs)
Branch: runs/P15-v2

## 0. Statement re-verification (2026-07-22)

- Original sources checked directly:
  - Owens, "A Covering System with Minimum Modulus 42", BYU MSc thesis 2014,
    scholarsarchive.byu.edu/etd/4329 (PDF downloaded, text extracted to owens42.txt).
    Confirms: covering system = finite set of congruence classes with **distinct moduli > 1**
    covering Z; record min modulus = 42, built by hand prime-by-prime on Nielsen's framework.
  - Nielsen, "A covering system whose smallest modulus is 40", JNT 129 (2009) 640-666
    (PDF downloaded, nielsen40.txt). His covering has > 10^50 congruences after finitization
    of the p-up-arrow notation.
  - Hough, Annals 181 (2015): min modulus <= 10^16. Balister-Bollobás-Morris-Sahasrabudhe-Tiba:
    min modulus <= 616,000.
- Openness check (Exa search, July 2026): no construction with min modulus > 42 found in any
  indexed literature; recent covering-system arXiv items (2506.11359, 2402.03810, 2607.19029)
  do not touch the constructive record. Problem confirmed open.
- Statement attacked (exact): find a finite set {a_i mod n_i} with distinct n_i, all n_i >= 43,
  covering Z.

## 1. V2 framing

Fix a smooth lcm N (prime pool + exponent caps). Covering Z with distinct divisors >= 43 of N
is a structured set-cover over the CRT tree of Z_N. Because N is astronomically large the cover
is built CRT-layered: maintain a worklist of uncovered *cells* (residue classes r mod m, m | N),
close a cell with the congruence (r mod m) when the modulus value m >= T is still unused,
otherwise split the cell along a chosen prime into p subcells. Each modulus value of N is a
globally scarce resource (usable once) — this is the set-cover/assignment structure; column
generation = on-demand cell splitting.

Key structural observations recorded before computing:
- Global reciprocal-sum feasibility (sum 1/d over usable divisors >= 1) is NOT the binding
  constraint (it is trivially satisfiable with enough primes); the binding constraint is the
  tree-structured scarcity that Hough's proof exploits: within a chain of cells sharing modulus
  m, only one cell can consume each divisor value.
- The pure p-power chain never terminates (2-chain closes 1 cell per level but spawns 1);
  termination requires exponent caps forcing prime switches — this reproduces exactly the
  p-up-arrow finitization of Morikawa/Gibson/Nielsen.

## 2. Log

(chronological; checkpointed as the run proceeds)

### 2026-07-22 ~20:30 — verifier + first engine, and a structural dead end

- Wrote solutions/P15/verify.py (CRT-tree cover checker, stdlib only). Sanity-checked on the
  classic {0/2, 0/3, 1/4, 5/6, 7/12} cover (PASS) and a corrupted variant (FAIL with witness).
- engine.py (v1): recursive cell model where every congruence covers exactly ONE leaf cell of
  the CRT tree (close cell (r mod m) with value m, else split by a prime). All strategies blow
  up (open cells -> 2M) even at T=3.
- **Dead end explained, then proved**: the no-spillover model forces the congruences to tile Z
  exactly (disjointly) with distinct moduli. By Mirsky–Newman / Davenport–Rado (Erdős's "exact
  covering systems" theorem), a disjoint cover of Z with distinct moduli > 1 is IMPOSSIBLE —
  the two largest moduli of an exact cover must coincide. So engine v1's search space is empty
  for every T and every pool; the blowup was structural, not heuristic. Overlap (congruences
  with modulus v coarser than the cell they finish, spilling into other branches) is mandatory.
  This is precisely Nielsen's cross-branch "input sets" / x-notation.
- Consequence for V2 framing: the correct layered model is stage-based. Maintain U_i =
  uncovered residues mod M_i for a tower 1 = M_0 | M_1 | ... (each step one prime). At each
  step, congruences (a mod v), v | M_{i+1}, v >= T, each modulus VALUE globally single-use,
  kill all u in U_{i+1} with u ≡ a (mod v) — one coarse value can kill many branches at once
  (this is the overlap). Set-cover per stage; greedy argmax-residue placement first, ILP later.
- Growth law: |U_{i+1}| = p·|U_i| − (kills at stage i+1). Kills bounded by the supply of fresh
  divisor values of M_{i+1} in [T, Vmax] and by placement efficiency. The Hough-style scarcity
  at the 2-3-adic top of the tree is what makes large T hard.

### 2026-07-22 ~21:30 — engine2 (explicit U, global tower) & engine3 (cells), both supercritical

- engine2 (explicit uncovered set U mod M_i, CRT-coordinate numpy columns, greedy argmax-residue
  placement per fresh divisor value): correct (T=3: 18 congs PASS; T=6: 119 congs PASS via
  verify.py). But for T=12 the density |U|/M falls too slowly relative to M growth: |U| hits
  ~3.5M around M~10^8 and keeps growing under both planners (simulate-all and supply-reciprocal
  heuristic). Peak |U| ≈ (peak uncovered measure)·M is the wall: explicit-per-integer tracking
  is memory-bound long before the supply of fresh values catches up. Densities observed:
  0.88 at M=2^10, 0.117 at M≈8.7e6 (T=12).
- engine3 (disjoint cells with per-branch local towers + coarse closures + clean spillover
  kills): cells explode (>4M cells, <200 congs at T=6/12). Diagnosis: coarse fresh divisors of
  a cell modulus get exhausted tree-wide quickly, and clean spillover (r' ≡ a mod v with v|m')
  almost never fires because residues across branches are not aligned. Nielsen's by-hand
  construction engineers this alignment (his "x" inputs); a greedy without alignment planning
  gets essentially zero cross-branch reuse.
- **LP-duality observation (kills the naive V4-ish idea, worth recording)**: for fixed smooth N,
  the natural LP relaxation of "cover Z_N with distinct divisor moduli >= T" collapses by
  translation-symmetry to the reciprocal-sum condition sum_{v | N, v >= T} 1/v >= 1: averaging
  any feasible x over translations gives x_{v,a} = y_v/v, and the point constraint becomes
  sum_v y_v/v >= 1, y_v <= 1. So the LP bound = reciprocal-sum bound; ALL the difficulty of the
  minimum-modulus problem lives in the integrality gap (this is exactly what Hough's/BBMST's
  arguments quantify). Plain LP duality certificates cannot rule out T=43 for any interesting N.
- Pivot: engine4 = the purest V2 model. Fix a smooth N that FITS IN RAM as a bitmask over Z_N;
  covering Z with moduli dividing N == covering Z_N. Greedy multi-sweep over divisor values
  (argmax residue class, efficiency-gated), then endgame assignment. Then determine empirically
  the maximal achievable T as a function of N, with exact ILP polish for small N.

### 2026-07-22 ~23:00 — engine4 (dense bitmask over Z_N) + local search + exact ILP

- engine4.py: fix factored smooth N; greedy multi-sweep over all divisor values v >= T of N
  (accept the argmax residue class of v when its uncovered count >= gate * (N/v); descending
  gates 0.99,0.9,0.7,0.4,0.15,0,0). Then two local-search layers:
  - repair(): ruin-and-recreate with incremental coverage counts (drop random ~6% of
    placements, re-place greedily on current uncovered set, accept non-worsening);
  - one_opt(): exact 1-opt — re-place value v elsewhere when new kills > exclusive coverage
    (points covered only by v), iterated to fixpoint, with 10% neutral-move shuffling.
- scan.py ladder results (greedy+repair(+one_opt), all covers verified by verify.py):
  - N=5040  (2^4·3^2·5·7):        max T reached = 5
  - N=55440 (2^4·3^2·5·7·11):     max T reached = 6
  - N=1.66e6 (2^5·3^3·5^2·7·11):  max T reached = 8
  - N=2.16e7 (2^5·3^3·5^2·7·11·13): max T reached = 8 (T=9 near-miss: 9..514 uncovered of
    21.6M across runs; all 568 divisor values >= 9 consumed; plateau resists repair+1-opt)
  - N=1.30e8 (2^6·3^4·5^2·7·11·13): T=9 SUCCESS (T9_2e6_3e4_5e2_7_11_13.txt), scan continuing
- ilp.py: exact feasibility ILP over Z_N (HiGHS): vars x_{v,a} for every divisor v>=T of N and
  residue a; sum_a x_{v,a} <= 1 per value; coverage >= 1 per point. Zero objective (pure SAT).
  - N=5040, T=6: **SAT in seconds** — 55 congruences, verified PASS (ilp5040_6). Greedy stack
    only reached T=5: measurable integrality/heuristic gap already at N=5040.
  - N=5040, T=7: undecided after 250s; long run (2h limit) in progress. recip budget 1.388,
    so UNSAT here would be a genuine scarcity certificate beyond the LP bound.
  - N=55440, T=7/8 queued behind it.
- polish.py: targeted-column ILP repair of INCOMPLETE dense covers (liberate the S placements
  with least exclusive coverage, targets = holes + their exclusive points, columns only
  (v, t mod v) for targets t). On the T=9/21.6M plateau: infeasible for |S|<=173, ILP too slow
  by |S|~300 — the plateau needs deep multi-value restructuring, not shallow reassignment.

### 2026-07-22 ~23:40 — engine5 (segmented/sampled, N beyond RAM)

- Motivation: Krukenberg's record-18 cover used only primes <= 19 => lcm ~ 10^10-10^12 scale.
  Dense bitmask dies at N ~ 2e9; engine5 streams.
- engine5.py pipeline: (1) sample-guided greedy sweeps (class counts estimated on a uniform
  sample of Z_N, values <= vmax_sample); (2) exact hole materialization by segment streaming;
  (3) exact greedy placement of remaining values on the hole list; (4) pass-based batched
  streaming 1-opt: one full stream computes exclusive-coverage sizes of ALL placements, moves
  with (new kills > exclusive loss) are selected, a second stream collects exclusive points of
  just the movers, moves applied with exact hole updates.
- Pilot N=2.16e7, T=8: SUCCESS, 569 congs, verify.py PASS (matches dense engine4).
- Launched (bigrun.sh): N1=2.2e9 (2^6·3^4·5^2·7·11·13·17) at T=10,11,12,13 and
  N2=4.19e10 (…·19) at T=12,14,16,18. Reciprocal budgets at these T are 1.9-2.4 (ample);
  the binding constraint is placement alignment, not measure.

### 2026-07-23 ~00:30-03:00 — big-N results, two engine5 bugs found and fixed

- Bug 1 (OOM): np.bincount(minlength=v) for huge divisor values v ~ N allocated O(v) memory
  (17GB) -> OOM-killed the first N1 T=10 run (and took the concurrently running scan.py and
  ilp.py with it). Fix: best_class() uses np.unique on the residues of the hole list when
  v >> |holes| (memory O(|holes|)).
- Bug 2 (SOUNDNESS): the first "SUCCESS" T=10 cover at N=2.2e9 FAILED verify.py (class
  34647439 mod 183783600 uncovered). Root cause: in the batched 1-opt, exclusive-point
  snapshots go stale as moves are applied within a pass — two placements covering the same
  point can both be moved away, leaving an untracked hole. Fix: after every pass, holes are
  recomputed exactly by a full streaming re-materialization; incremental tracking is only used
  to guide in-pass decisions. (Independent verification catching a search-engine soundness bug
  is exactly why METHODOLOGY.md demands it.)
- With fixes + elitist restore (revert to best-known placement when a diversification pass
  doubles the holes):
  - N=2.2e9, T=10: **SUCCESS, 1671 congruences, verify.py PASS** (covers/e5_T10_2.2e9.txt).
  - N=1.3e8, T=10: SUCCESS 831 congs (dense scan, verified); T=11 fails (rem 85718).
  - N=2.2e9, T=11: plateau at 42.6k holes (density 1.9e-5) after 2400s; a second attempt with
    conservative gates + fresh seed plateaued WORSE (234k) — early-sweep conservatism starves
    mid-size values. Dense finisher (finish_dense.py: engine4 repair/one_opt on the .part) also
    cannot move the 42.6k plateau: ruin-and-recreate over 6% of 1670 placements never beats the
    1-opt fixpoint. The plateau is a deep local optimum, not a shallow one.
  - N=4.2e10, T=12: running (phase3 on 306M holes takes hours/attempt at this scale).
- ILP long-run outcomes: N=5040 T=7 INDETERMINATE after 3h (no feasible point, no
  infeasibility proof; the zero-objective feasibility MIP explores ~500 B&B nodes/3h — the
  translation symmetry that collapses the LP also makes B&B slow). N=55440 T=7 also
  INDETERMINATE at 90 min. Exact SAT/UNSAT beyond the greedy frontier needs symmetry-broken
  encodings (or SAT solvers = V3's territory).
- Plateau diagnostic (T=11, N=2.2e9, 42626 holes): the leftover holes are DIFFUSE — nonzero
  in 48/64 classes mod 64, 70/81 mod 81, 24/25 mod 25, all 7 mod 7, 10/11 mod 11, 12/13
  mod 13, 16/17 mod 17. No concentrated 2-3-adic core to attack: covering residue "dust"
  requires re-matching many already-used values one dust-point each without opening their
  exclusive sets — a global assignment, not a local move. This is the integrality gap made
  visible; the hand-built record covers avoid it by constructing the tail exactly, top-down.
- N=4.2e10, T=12 (final): sample greedy + exact hole placement left 264.9M holes (0.63%);
  the streaming 1-opt pass at this scale takes >2.5h (12.5M small numpy slice-ops per stream:
  python-loop overhead dominates), so the local-search budget buys ~1 pass — INCOMPLETE at
  budget. Scaling one_opt to N ~ 10^10.5 needs a compiled kernel; but the T=11 evidence says
  the plateau, not iteration speed, is the real wall.

## 3. Results table (all covers verified by solutions/P15/verify.py)

| N (lcm) | factorization | max T achieved | method |
|---|---|---|---|
| 5040 | 2^4·3^2·5·7 | 5 greedy / 6 ILP (SAT, 55 congs) | engine4 / ilp.py |
| 55440 | 2^4·3^2·5·7·11 | 6 (T=7 ILP indeterminate) | engine4+repair |
| 1.66e6 | 2^5·3^3·5^2·7·11 | 8 | engine4+repair |
| 2.16e7 | 2^5·3^3·5^2·7·11·13 | 8 (T=9: 514 holes) | engine4+repair+1opt |
| 1.30e8 | 2^6·3^4·5^2·7·11·13 | 10 (T=11: 86k holes) | engine4 scan |
| 2.21e9 | 2^6·3^4·5^2·7·11·13·17 | 10, 1671 congs (T=11: 42.6k holes) | engine5 |
| 4.19e10 | 2^6·3^4·5^2·7·11·13·17·19 | (T=12: 265M holes at budget) | engine5 |

Reciprocal-sum budgets were 1.9-2.6 at every failing T — measure is never the binding
constraint in this range; alignment (the integrality gap) is.

## 4. Conclusions

1. The V2 attack (fix smooth N; distinct-divisor set cover over Z_N; greedy + ILP layers)
   is sound and reproduces covering systems with min modulus up to 10 fully automatically,
   with independent verification. But the achieved min-modulus grows ~ logarithmically in N
   (5->6 needs 11x, 8->10 needs 100x, 10->11 not reached with 17x + 4h of local search).
   Reaching T=43 this way would need N far beyond any explicit representation — consistent
   with Nielsen's 40 needing lcm > 10^50 and Owens's 42 more still.
2. The LP relaxation is useless as a certificate (collapses to reciprocal sums by translation
   averaging); exact ILP feasibility stalls already at N=5040/T=7. The gap between the greedy
   frontier and the counting bound is where all the difficulty lives.
3. Failure mode is universal and structural: local search always terminates in a DIFFUSE hole
   set (dust spread over nearly all residue classes of every prime power), which no
   reassignment of already-used values can absorb. Record constructions (Krukenberg, Nielsen,
   Owens) avoid dust by building the tail exactly, top-down, with cross-branch alignment
   planned from the start — that global alignment is precisely what column generation over
   residue-class columns fails to capture at scale.
4. Honest bottom line: no covering system with min modulus >= 43 was found; nothing here
   suggests V2-style search can get anywhere near 43. The constructive record 42 stands.

STATUS: frontier-pushed (verified machine-generated covers up to min modulus 10 at N=2.2e9;
exact small-N SAT/UNSAT data; two engine soundness bugs caught by independent verification;
no progress toward 43 — negative for the stated goal).

---

# Session 2 (resumed 2026-07-22/23): SAT attack, symbolic Nielsen constructor, exact minimal-lcm ladders

## 9. SAT / cube-and-conquer attack (sat_cover.py, sat_tree.py)

Encodings tried for "cover Z_N with distinct divisor moduli >= T" as CNF:
- flat: x_{v,a} vars, one length-|divs| clause per point of Z_N, at-most-one residue per
  value (pairwise for v<=30, sequential counter above). N=5040,T=6: 38,380 vars / 64,322
  clauses.
- CRT-tree layered (sat_tree.py): cell vars c_{m,r} down a prime chain 1|2|4|...|N,
  c -> (closed by a divisor of m) OR (all p children needed); logically equivalent but gives
  CDCL hierarchical lemmas. Sanity: T=3@5040 SAT in 6 s, witness verified PASS.
- translation symmetry handled by a sound case split (cube per divisor v0 with x_{v0,0}=1:
  any solution can be translated so the class covering 0 has residue 0).

Negative findings (dead end, well-documented):
- cadical195, glucose42, minicard (via pysat) and kissat 4.0.4 (built from source, --sat)
  ALL fail to solve the *known-SAT* instance N=5040 T=6 (kissat: full 2 h budget exhausted,
  no result), an instance HiGHS ILP solves in ~30 s. LP-style global counting reasoning appears essential; clause learning
  finds nothing to grip on the flat or tree encodings.
- cube split does not rescue CDCL: cubes are individually as hard.
- Conclusion: pure CDCL SAT is the wrong tool for covering-feasibility at these sizes;
  cutting-plane / LP reasoning (ILP) dominates. (A pseudo-Boolean or MaxSAT solver with
  counting engine might close the gap; not pursued further.)

## 10. Symbolic Nielsen-style constructor (engine6.py, engine7.py, hybrid7.py)

New engine class that never materializes Z_N: state = list of uncovered residue classes
(r mod M) with M a bigint lcm; incorporating a prime-power block p^k turns each class into
p^k children, and only *new* divisors v = d*p^j (j > old exponent) can hit children without
having covered the parent. Sweep-greedy set cover on children with proportional kill
thresholds; numpy fast path while M < 2^62. This reproduces the cross-branch alignment
("x-inputs") that engines 3-5 lacked, and verified instantly at small T
(T=3: 12-18 congruences, PASS).

Frontier findings:
- growth is structural: at a tail prime p the new-divisor reciprocal sum
  sum 1/(d p) ~ (sum 1/d)/p is far below (p-1)/p, so the uncovered-class COUNT multiplies
  every step even though the uncovered FRACTION shrinks. All schedules tried for T=11-14
  (fat smooth heads 2^6..2^8, 3^4..3^5, 5^2..5^3, 7^2, interleaved re-raises, vmax up to
  4e6, budget up to 8e7 classes) blow past the class budget before the divisor lattice is
  rich enough to finish. This matches why Nielsen's 40-cover needs >10^50 congruences:
  explicit-witness covers (verifiable by listing congruences) are fundamentally capped at
  low double-digit min modulus.
- hybrid7.py (engine7 front-end to M = N = 2.2e9, then engine5 hole placement + streaming
  1-opt): T=11 run plateaued ~0.9-1.0M holes (worse than engine5's 42k plateau from a dense
  greedy start) — the symbolic front-end's leftovers are more diffuse, not less.

## 11. Exact minimal-lcm ladders (minlcm.py SAT version; minlcm_ilp.py = HiGHS)

New exact results (each N decided SAT/UNSAT; SAT witnesses verified by solutions/P15/verify.py):
the minimal possible lcm N of a covering system with distinct moduli, all >= T
(equivalently minimal N such that Z_N is coverable by distinct divisor moduli >= T;
N ascending, pruned by the necessary condition sum_{v|N, v>=T} 1/v >= 1):

- T=3: N = 120 (all smaller N UNSAT; witness 14 congruences, PASS).
- T=4: N = 360 (9 measure-feasible smaller N all UNSAT in <= 31 s total; witness 21
  congruences, PASS).
- T=5: every N < 1260 UNSAT (N=840 needed a 40-min dedicated HiGHS run; ladder default is
  900 s/N with UNDECIDED entries retried at 3-4 h). N=1260, 1680 retries running.
- T=6: all N <= 1512 UNSAT except N=1260, 1440 UNDECIDED at 900 s (ladder paused to give
  CPU to the T=5 chain; 5040 known SAT from session 1, so minimal N6 is in [1260, 5040]).

Method note: ILP >> SAT for both directions on this family; the SAT ladder (minlcm.py) was
abandoned after head-to-head comparison.

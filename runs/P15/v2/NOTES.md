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

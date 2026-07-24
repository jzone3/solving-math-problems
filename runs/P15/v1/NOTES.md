# P15 — Covering system with min modulus >= 43 — run notes (variant V1)

Variant V1: mechanize the Nielsen/Owens prime-by-prime distortion method as
code; reproduce 40/42; machine-optimize hole-covering decisions to push to 43+.

## 0. Statement re-verification (original sources)

* Owens, *A Covering System with Minimum Modulus 42*, BYU MS thesis 2014,
  https://scholarsarchive.byu.edu/etd/4329 (PDF fetched & converted).
  Title/abstract confirm: distinct-moduli covering system, min modulus 42,
  improving Nielsen's 40. Construction uses primes through 89.
* Nielsen, *A covering system whose smallest modulus is 40*, J. Number
  Theory 129 (2009). PDF fetched; confirms 40, primes through 103.
* Balister–Bollobás–Morris–Sahasrabudhe–Tiba (2022, arXiv:2211.01417):
  minimum modulus of any distinct-moduli covering system is <= 616,000.
  So the target (>= 43) is *constructive frontier*, not impossibility.
* Literature check (Exa, July 2026): no published construction beating 42
  found. Problem statement in problems/P15-covering-min-modulus.md matches
  the original sources: finite set of residue classes a_i (mod n_i), n_i
  distinct, n_i >= 43, union = Z. Record to beat: 42 (Owens 2014).

## 1. Verifier

`solutions/P15/verify.py` — standalone, stdlib-only. Checks: n_i distinct,
n_i >= claimed min modulus, min modulus >= target, exact cover of Z via
CRT-structured recursive splitting (plus 20k-sample randomized pre-check,
fixed seed). Prints PASS/FAIL. This is the sole arbiter for any claim.

## 2. Feasibility (reciprocal budget)

`feasibility.py`: with primes up to P and all moduli M <= n (n smooth),
the usable reciprocal mass sum_{n>=M, n P-smooth} 1/n = prod p/(p-1) -
sum_{d<M} 1/d. For M=43, primes <= 89: total ~3.9 vs the 1.0 needed —
measure is NOT the obstruction; the obstruction is combinatorial (the
level-1 "ban" on small moduli in each prime direction, i.e. the top of
the tree where only primes 2,3,5,7 provide cheap structure).

## 3. Small-M ground truth (finite-LCM exact search)

`finite_cover.py`: exact backtracking cover of Z_N with distinct divisors
of N that are >= M (max-gain residue choice, reciprocal-sum prune).
Verified witnesses (runs/P15/v1/witnesses_small/, all PASS verify.py):

| M | N     | congruences | nodes | time |
|---|-------|-------------|-------|------|
| 3 | 120   | 14          | 15    | 0.0s |
| 4 | 2520  | 29          | 30    | 0.1s |
| 5 | 10080 | 46          | 47    | 0.5s |
| 6 | 10080 | 64          | 65    | 0.5s |

M=7 at N=10080: no cover found in 600s (645,866 nodes) — fixed-N search
stops scaling immediately; N must grow with M and the search space
explodes. Dead end for reaching 40+; kept as ground-truth generator.

## 4. Mechanized construction engines (the main V1 effort)

Three generations, all under runs/P15/v1/:

* `engine.py` — direct recursive up-arrow engine (emit / finitize /
  split-by-prime). Too slow, uncontrolled recursion. Dead end.
* `greedy.py` — global priority-queue hole filling with generalized
  divisor-chain finitization. CPU-bound in divisor-chain search; did not
  complete. Dead end (profiling data in session logs).
* `builder.py` — the serious attempt: explicit congruence emitter with a
  global distinct-modulus registry. cover_class(r,m) either (a) emits a
  divisor modulus d | m, d >= M (with budgeted measure overshoot beta),
  (b) runs a q^-chain: at level k the q-1 sibling slots mod m*q^k are
  covered recursively, one class descends; chain bottoms are closed by
  Nielsen-style finitization (fresh prime Q, divisor chain d_1..d_Q of
  the bottom modulus, budgeted waste), or (c) closes deep slots directly
  by finitization. Factorizations are threaded through the recursion so
  divisor sets of astronomically deep chain bottoms remain computable.

Iterations & fixes logged: float overflow at m>1e308 (integerized waste
checks); duplicate-radical chain contention (2^k vs 2^k collisions);
primorial-drift (nested trees accumulating all small primes, killing
finitization); sibling contention (all q-1 siblings at a level sharing
modulus m*q^k, only one can take the exact divisor). Each fix moved the
failure deeper but the systemic issue remains: contention is resolved by
escalation (bigger tree primes, deeper nesting) rather than global
optimization, which inflates congruence counts multiplicatively.

FINAL builder outcome: even M=6 does not converge (3M-congruence cap,
~620k direct emits + 290k finitizations, 4.4k trees, 900s). The
registry-greedy recursive design is a NEGATIVE result: without
Owens-style cross-hole set sharing (one set description covering slots
in several holes at once), per-slot contention makes the congruence
count blow up long before the measure or reciprocal budget is at risk.
Any follow-up should implement set descriptions as first-class shared
objects (the pool/ledger model of Section 5) rather than per-slot
emission.

## 5. The 42 -> 43 surgery plan (worked out, not executed)

Analysis of Owens's thesis (done by hand against the PDF): the ONLY
modulus < 43 in his system is a single congruence with modulus exactly
42 = 2*3*7 (the "2" component of the set 3(2,4,3^(1,2)) in the third
input of the 7^ filling the 8- and 16-holes, at 7-level 1). Its removal
uncovers exactly one class R (mod 42). All later "x"-reductions in the
thesis that cite this set cite subsets of R, so re-covering R exactly
keeps every downstream ledger valid. Owens used only primes <= 89, so
97, 101, 103 (and everything above) are entirely fresh: every modulus in
a 97-adic tree over R (d * p^j * 97^k, d | 42, p <= 89) is unused and
>= 97. A pool/ledger estimate (atoms = 8 divisors of 42; gadget primes
2..89 with costs c_p ~ p-1, each usable once per direction with disjoint
inputs) gives a pool of ~57-95 sets vs the 96 needed for a single 97^;
splitting R into two subholes (97-tree + 101-tree) or cascading a second
fresh prime over the shortfall slots clears the bar in the estimate.
STATUS of this line: promising, unproven. It requires a full transcription
of Owens Ch. 3 (plus the Nielsen tables it inherits) into explicit
congruences to make the witness explicit and machine-verifiable; that
transcription (hundreds of set descriptions, residues only partially
pinned down by the prose) did not fit in this session.

## 5b. Second push (session resumed): new encodings past the M=6 stop

Instruction: try fundamentally different encodings and push the frontier
past where we stopped (our machine frontier was M=6; literature is 42).

* `sat_cover.py` — SAT encoding (vars x_{n,a}, coverage clauses per cell of
  Z_N, at-most-one per modulus, CaDiCaL 1.9.5). DEAD END: even M=6 at
  N=10080 (78k vars / 128k clauses), which greedy solves in 0.5 s, did not
  finish in 300 s; M=7 at N=1680/2520 got neither SAT nor UNSAT in 900 s.
  Covering/counting structure with massive symmetry is hostile to CDCL.
* `finite_cover_np.py` — numpy-accelerated deterministic backtracker,
  scanning candidate LCMs N (2^a 3^b 5^c 7^d 11^e 13^f <= 3e7). M=7
  exhausted/timed out on all N <= 15120 at branch width 3.
* `fc_restart.py` — the breakthrough for mid-M: randomized-restart
  backtracking (choose modulus randomly among near-best gain-density
  within a jitter band, shuffle residue order, short per-restart budget)
  on RICH LCMs (recip sum ~1.7-2.1, N up to 5e6). Results, all PASS by
  solutions/P15/verify.py and stored in witnesses_small/:
  - M=7: N=831600, 197 congruences (24 restarts, ~8 min).
  - M=8: N=1663200, 205 congruences (90 s/restart, jitter 0.3: 3 restarts,
    ~4 min; the 20 s/0.15 config also found one at N=831600, 210 congs,
    108 restarts). Larger per-restart budget + more jitter wins.
  - M=9: N=3326400, 268 congs (150 s/restart, jitter 0.1; 2 restarts).
* `fc_anneal.py` — ruin-and-recreate local search (the strongest engine):
  state = partial assignment n->a with coverage-multiplicity array; recreate
  = LAZY greedy (max-heap of stale gain-densities, rescore on pop — valid
  since gains only decrease; jitter = random residue among near-max ones);
  ruin = drop the k lowest-unique-coverage classes plus k random. Seed
  variance is huge (initial uncovered 8k-600k at the same M,N), so running
  several seeds in parallel and keeping the lucky ones is part of the
  method. Verified witnesses (all PASS verify.py, in witnesses_small/):
  - M=10: N=4989600,   165 congs (first recreate already complete).
  - M=11: N=9979200,   402 congs (1 iteration).
  - M=12: N=23284800,  477 congs (329 iterations, ~25 min).
  - M=13: N=129729600, 610 congs (lucky seed, 1 iteration, 70 s).
  - M=14: N=129729600, 616 congs (lucky seed, 1 iteration, 111 s).
  - M=15/16 via anneal alone: NOT reached; every seed plateaus at ~23,000
    uncovered cells at N=129729600 (structural, seed-independent).
* `fc_walk.py` / `fc_walk2.py` — third push, WalkSAT-style repair: every
    modulus always assigned; move = pick uncovered cell x, reassign some
    modulus n to the class through x (a := x mod n); delta evaluated
    incrementally via the multiplicity array; fc_walk2 adds an exact
    finisher (vectorized gain over ALL moduli vs the uncovered set, with
    cached unique-coverage costs) below a threshold. This BREAKS the
    anneal plateau (23k -> ~8k at N=129729600) but saturates there.
    The decisive factor is again slack: at N=518918400 (recip 1.71) the
    jittered lazy-greedy init already converges and M=15 fell in minutes:
  - M=15: N=518918400, 1066 congs (PASS verify.py, witnesses_small/).
  - M=16: NOT reached. Best greedy init 258k uncovered at N=518918400
    (walk closed only ~40k in ~5 h); N=1102701600 (recip 1.87, includes
    prime 17) has ~2-3h init cost per seed at 1.1e9 cells and inits came
    out at 3.2-5.3M uncovered (near-max jitter sets are huge at big N, so
    early residue choices are nearly random); init_frac sweep
    (0.85/0.9/0.95/0.98/0.99) gave 0.5M-9.7M — all hopeless for walk
    closure at ~10-30 cells/min. The array-based LS family effectively
    tops out at M=15 on 32 GB; beyond that a CRT/tree-structured
    representation (Krukenberg/Nielsen-style layered construction) is
    required, not more seeds.
  Key lesson vs the 600s M=7 failure at N=10080: feasibility needs SLACK
  (recip >= ~1.7), i.e. much larger N than minimal — the earlier fixed
  small-N attempts were starved, not the search algorithm.

## 5c. Fourth push: M=16 hypothesis sweep and tree builder (all negative)

* Hypothesis 1 (init jitter is the culprit): pure-greedy init
  (init_frac=1.0) is WORSE, not better — 963k initial uncovered at
  N=518918400 vs 258k for jittered seed 29. Deterministic argmax ties
  create systematic overlap. REFUTED.
* Hypothesis 2 (more reciprocal slack fixes it): N=735134400
  (recip 1.864, prime 17) inits at 0.9-1.6M uncovered — much worse than
  deeper-2-power N with LOWER recip. Slack is not sufficient; DEPTH of
  small prime powers is what greedy chains exploit (Krukenberg's
  observation, rediscovered empirically). M=15's success N=518918400 is
  2^8*3^4*5^2*7*11*13 — deep in 2.
* Hypothesis 3 (deep-2 rich N): best M=16 candidate N=1816214400 =
  2^7*3^4*5^2*7^2*11*13 (recip 1.725 vs 1.71 that sufficed for M=15).
  3-seed fleet OOM-killed (each proc peaks ~15 GB in init at N=1.8e9);
  solo rerun inits in ~2h42m at 660k uncovered (0.036% — proportionally
  the best M=16 init seen, but absolutely hopeless for walk closure at
  10-60 cells/min). NEGATIVE.
* `fc_tree.py`: CRT/tree-structured sparse greedy builder — fragments
  (r, m) with m | N refined lazily, no cell arrays, N unbounded by
  memory. Gain-density greedy with fragment-sampled residue scoring:
  M=3, M=6, M=8 PASS witnesses generated without any array (M=8 at
  N=2^5*3^3*5^2*7*11 in ~7 min, 116 congs). At M=10 fragmentation blows
  up (2.8M fragments) and the top-K sample no longer sees where the
  remaining mass lives, so gain estimates go blind and the run exhausts
  moduli at mass ~0.015. A production version would need exact
  per-modulus gain aggregation over the fragment tree (CRT convolution),
  not sampling. Documented dead end at current engineering depth.

Conclusion: the constructive frontier of this session's array/LS family
is M=15. M=16 requires either the exact-tree greedy or a faithful
Krukenberg-style layered design; M>=43 (the actual target) requires the
Owens Ch.3 transcription + fresh-prime surgery (Section 5).

## 6. Compute spent (approx)

* finite_cover: ~25 min CPU total (M=3..7).
* engine/greedy: ~1 h CPU (terminated, no output artifacts).
* builder iterations: ~2.5 h CPU across ~8 runs (cong-cap 3M hit twice,
  depth-cap hit twice, several 600s timeouts).
* second push: SAT ~30 min; fc_restart fleets (M=7-9) ~6 h CPU across up
  to 6 parallel processes; fc_anneal fleets (M=10-16) ~20 h CPU across
  up to 10 parallel processes over ~5 h wall.
* third push (walk engines): ~40 h CPU across up to 8 parallel processes
  over ~8 h wall (M=15 success at N=518918400; M=16 seed/jitter sweeps
  negative; two ~2h+ inits at N=1.1e9 negative).
* fourth push: ~25 h CPU over ~9 h wall (M=16 hypothesis sweeps at
  N=518M/735M/1.04G/1.82G incl. one OOM-killed fleet and one 2h42m solo
  init; fc_tree builder runs M=3..10).

## 7. STATUS

STATUS: negative (for min modulus >= 43); machine frontier pushed from
min modulus 6 to min modulus 15: verified explicit covers (PASS by
solutions/P15/verify.py) for every M in 3..15, culminating in M=15 with
1066 congruences over N=518918400 via WalkSAT-style reassignment local
search (fc_walk2) on top of jittered lazy-greedy initialization. The
walk engine breaks the fc_anneal 23k plateau at N=129729600 (down to
~8k) but M=15 ultimately fell via a richer-slack N. M=16 documented
negative for the whole array-based LS family (init quality collapses at
big N; hypothesis sweeps and OOM data in 5c) and for the new sparse
CRT/tree greedy (fc_tree, PASS to M=8, sampling-blind at M=10, see 5c);
SAT encoding documented dead end; recursive
registry-greedy builder documented dead end; best path to 43 remains the
Owens-42-class surgery with fresh primes 97/101 (Section 5), which needs
a faithful Owens Ch.3 transcription as its remaining step.

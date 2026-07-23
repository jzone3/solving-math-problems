# P15 V4 — greedy + local repair at scale — run notes

Session: https://app.devin.ai/sessions/da7ba5bd517c40518a9c80f1714c0433
Variant: V4 (randomized greedy over huge modulus pools + alignment/repair).

## 0. Statement re-verification (2026-07-22)

- Original sources checked: Owens, "A Covering System with Minimum Modulus 42",
  BYU MSc thesis 2014 (scholarsarchive.byu.edu/etd/4329); Nielsen, JNT 129 (2009)
  640–666 ("A covering system whose smallest modulus is 40"); Hough, Annals 181
  (2015) (min modulus ≤ 10^16); BBMST 2022 (≤ 616,000).
- Wikipedia "Covering system" (rev. 2026-05-28) still lists 42 (Owens) as the
  constructive record; targeted Exa searches for 2024–2026 improvements found
  none. Problem confirmed open as stated: construct distinct-moduli cover with
  min modulus ≥ 43.
- KEY STRUCTURAL FACT recovered from the sources: Nielsen's min-mod-40 system
  has > 10^50 congruences and Owens's 42 system > 10^86 — these are *implicit*
  (recursive recipe) constructions, not explicit lists. Any ≥43 witness will
  almost certainly need a compressed/recursive witness format, not a literal
  congruence list.

## 1. Encoding

CRT-layered level framework (`cover.py`):
- Process prime powers p^e ("levels") in increasing order; state = holes
  (uncovered residues mod M, M = product of processed levels).
- At level p^e each hole splits into q = p^e cells; usable moduli are d·p^j
  (d | M, j = 0..e, d·p^j ≥ T, each numeric modulus used at most once =
  distinct-moduli constraint). Congruence (a mod d, b mod p^j) covers cells
  t ≡ b (mod p^j) in every hole r ≡ a (mod d).
- Lazy submodular greedy over (d, j) candidates (gains only decrease → lazy
  heap is exact), randomized tie-breaks, numpy bincount scoring.
- Verifier `solutions/P15/verify.py`: independent, stdlib-only, recursive CRT
  split, never materializes lcm; checks distinct moduli + full cover.

## 2. What was tried, in order

1. **Plain gain-greedy** (max newly covered cells per congruence):
   solves T=2,3 on small configs; stalls at T=4+ (e.g. T=10 config with
   reciprocal slack 2.21 left 296k uncovered cells). Diagnosis: hole
   fragmentation — scattered holes make each congruence's density land mostly
   on already-covered ground (>55% waste).
2. **Efficiency-greedy** (max gain·m/(Mq), i.e. least wasted density):
   worse in practice — fragments even faster (T=3 left 4 holes where
   gain-greedy left 1).
3. **Forced-alignment slot builder** (`cover2.py`, Nielsen-style fixed
   survivor cell 0 per level, per-slot set covers): solves T=3 only; too
   rigid (no j=0 whole-hole kills, whole subtrees kept on slot failure).
4. **Two-phase survivor-aligned greedy** (`cover.py --survivor`): phase 1
   covers only cells outside a random survivor class s0 (mod p), phase 2
   mops up survivor columns. Keeps holes CRT-aligned so residue classes
   stay dense. THIS is the winning V4 ingredient:
   - T=10 SOLVED first try: 1002 congruences, lcm = 2^7·3^4·5^2·7^2·11·13,
     verified PASS. (Plain greedy on same config: 296k leftover cells.)

## 3. Verified explicit covers produced so far (all PASS verify.py)

| T | levels | #congs | witness |
|---|---|---|---|
| 2 | 2^2,3 | 5 | (smoke test) |
| 3 | 2^3,3^2,5 | 17 | (smoke test) |
| 4 | 2^5,3^3,5,7 | 38 | /tmp (gain-greedy) |
| 6 | 2^5,3^3,5^2,7 | 93 | /tmp (gain-greedy) |
| 8 | 2^6,3^4,5^2,7,11,13 | 625 | /tmp (gain-greedy) |
| 10 | 2^7,3^4,5^2,7^2,11,13 | 1002 | witness_T10.json (survivor) |
| 12 | 2^7,3^4,5^3,7^2,11,13,17 | 2064 | witness_T12.json (survivor) |

## 4. Scaling analysis (why explicit lists cap out)

Hole growth per level is intrinsic: at the first level 2^e only moduli
2^j ≥ T are usable, total density 2^{floor(log2 T)-e+1}-ish << 1, so almost
all 2^e cells survive as holes; the construction only wins because hole
*density* shrinks while hole *count* multiplies. Observed (T=14 run,
levels 2^8,3^5,5^3,7^2,11,...): holes 225 → 36k → 1.8M → 22M. This is the
same explosion that makes Nielsen's T=40 system >10^50 congruences and
Owens's T=42 >10^86. An explicit machine-verifiable congruence list is
therefore fundamentally limited to T ≈ mid-teens on a 32 GB machine;
T=43 REQUIRES a compressed recursive witness format + a verifier that
checks the recipe (hole-class counting), not a list. That compressed-
witness pipeline is the real frontier for machine work on this problem.

Engineering notes:
- OOM bug fixed: np.bincount(minlength=d) allocated O(d) for divisors up to
  ~7·10^8; replaced with np.unique grouping (bounded by #holes).
- Perf: cache active-cell matrix per phase instead of recomputing per score;
  LRU-bounded residue caches (10 GB); relaxed lazy greedy (accept within 20%
  of stale upper bound) to avoid 20M-element re-sorts per heap ping-pong.
- Bottleneck at 20M+ holes: np.unique sort per divisor (~650 divisors/level).

## 5. Escalation runs (compute log)

- T=13, levels 2^7,3^4,5^3,7^2,11,13,17,19 (slack 2.55): KILLED at 8 h
  timeout mid-17-level. Hole trajectory: 4.2M (11) → 13.6M (13, used 960
  moduli) → 36.2M holes entering the 17-level (~5 h there without
  finishing). Same wall as T=14: compute-bound, not density-bound.
- T=14, levels 2^8,3^5,5^3,7^2,11,13,17,19 (slack 2.75): KILLED at 8 h
  wall-clock timeout mid-13-level. Hole trajectory: 225 → 36k → 1.8M →
  22.2M (11-level, ~2 h) → 69.5M holes entering the 13-level; the 13-level
  alone needed >5 h (69.5M-element np.unique per divisor, ~1300 divisors).
  NEGATIVE: T=14 explicit is beyond this machine/day budget with the
  current per-level greedy — compute-bound, not density-bound (slack 2.75).

## 6. Ideas not exhausted (for follow-up runs)

- Parallelize per-divisor scoring across cores (np.unique is the bottleneck;
  embarrassingly parallel over ~10^3 divisors) — likely unlocks T=14–16.
- Hole-CLASS compression: group holes by coverage-isomorphism and track
  counts, not individuals (this is exactly how Nielsen/Owens scale to
  10^50/10^86 congruences). Witness becomes a recursive recipe; verifier
  checks per-class branch accounting + modulus-usage counting instead of an
  explicit list. This is the only credible route to T≥43 and meshes V4 with V5.
- Simulated-annealing reassignment of (a, b) choices at the last two levels
  (planned repair phase) was never needed below the compute wall — greedy +
  survivor alignment already fully covered whenever the level completed.

## 7. Final summary

STATUS: negative (frontier-pushed on the tooling side; no new record).

- Re-verified problem statement + openness (record still 42, July 2026).
- Built a fully automated pipeline (build + independent verify) for
  distinct-moduli covering systems with min modulus ≥ T; key algorithmic
  finding: survivor-class alignment beats both plain max-gain greedy and
  max-efficiency greedy by a wide margin (T=10 config: 296k uncovered cells
  for plain greedy vs 0 with alignment).
- Verified explicit covers produced for T = 2,3,4,6,8,10,12 (largest:
  2064 congruences, lcm 2^7·3^4·5^3·7^2·11·13·17). T=13/14 attempts hit an
  8 h compute wall at 36–70M holes, density slack unused (2.5–2.75).
- Distance to record remains enormous: T=42 needs >10^86 congruences —
  explicit-list search cannot reach it on any hardware; compressed
  recursive witnesses (hole-class counting) are the mandatory next step.

---

# PHASE 2 (resumed session): compressed hole-class counting + kill pool

Executed the "next step" above in depth: replaced explicit hole lists with
exact big-int per-class counting, plus the counting endgame that is the
actual scaling mechanism of Nielsen (2009) / Owens (2014).

## 8. The kill-pool formulation (new machinery)

Key observation that removes the explicit-list wall entirely:

- A hole (uncovered residue r mod M_l at level l) can be covered outright by
  the single congruence r mod d for ANY divisor d | M_l with d >= T —
  overlaps with other congruences are free; only DISTINCTNESS of moduli
  constrains us. So leftover holes can be assigned distinct unused divisors
  by pure counting (an injection suffices; any hole accepts any divisor).
- Validity is a Hall-type matching condition; the usable divisor sets are
  nested over levels (d | M_l => d | M_{l'}, l' > l), so Hall's theorem
  reduces to prefix inequalities
      kills(<= l) <= #{d | M_l : d >= T} - #{structured moduli dividing M_l}.
- Witness = structured recipe + per-level kill counts; verifier replays the
  exact counting semantics and checks the prefix inequalities. This makes
  Nielsen/Owens-scale systems (10^50+ congruences) certifiable with
  kilobyte-size witnesses.

Sustainability lemma (why the mechanism is right): if at some level the
hole count h and pool P satisfy h <= P/(q-1) for the next prime q, then
killing all but one child of each hole keeps h constant while P roughly
doubles per new prime — the construction then completes greedily. The
entire difficulty is the BOOTSTRAP: reaching h <= P/(q-1) at all, which
requires a near-exact aligned "core" cover over the smooth part of N (the
hand-crafted heart of Krukenberg 1971 / Nielsen 2009 / Owens 2014).

## 9. Implementations

- runs/P15/v4/cover3.py — counting builder, single residue window mod C
  (int64-bounded); found the int64 window ceiling destroys alignment.
- runs/P15/v4/cover4.py — CRT-COMPONENT representation (class = vector of
  residues mod p^e per window prime): no magnitude ceiling, exact counts,
  survivor-branch alignment, pool kills with Hall headroom; JSON recipes.
- solutions/P15/verify3.py, verify4.py — standalone stdlib verifiers that
  REPLAY the recipes exactly (split/cover/truncate/kill), independently
  recompute all counts, and check the Hall prefix inequalities; print PASS.
- runs/P15/v4/feas2.py — optimistic trajectory model. Its key (initially
  surprising) output: with UNALIGNED (density-random) coverage, even
  perfect greedy diverges for every T >= 13 and every config tried — proof
  that ALIGNMENT (holes concentrated in sparse sublattices where moduli
  cover far more than their 1/m density) is not an optimization but the
  load-bearing mechanism.

## 10. Phase-2 results (all machine-verified)

- End-to-end compressed pipeline validated: cover4 + verify4 PASS on
  T=3 (N = 2^2·3^2·5·7, 22 structured congruences + 3 pool kills — kills
  exercised and verified), T=6 (N = 2^3·3^2·5^2·7^2·11·13, 185 congruences),
  T=8 (N = 2^4·3^3·5^3·7^2·11^2·13^2, 714 congruences; the last 19,626
  aligned classes were wiped by 10 congruences — alignment leverage
  in action).
- T=10/12/13 counting attempts: hole growth still outruns the pool
  (holes ~1e7 vs pool ~1e3 mid-run) — the single-prime level decomposition
  is measurably weaker than the prime-power levels + survivor cleanup of
  the phase-1 explicit builder, which solved T=10/12 outright.
- Conclusion sharpened: the bottleneck is not representation (solved by
  counting) nor endgame (solved by kills) but CORE ALIGNMENT QUALITY.
  Beating 42 needs an Owens-style machine-optimized exact core (per-level
  ILP/DP over aligned residue trees), then the kill pool scales it to any
  divisor-rich N. That is a well-posed, promising follow-up.

## 11. Phase-2 escalation attempts (negative, quantified)

- cover4 counting runs at T=10/12/13 (interleaved single-prime levels,
  survivor alignment, hcap 2M classes): holes reached 1e7–1e9 with pools
  stuck at ~1e3 — pool growth (x2 per new prime) cannot chase hole growth
  (x(q - covered)) without a near-exact core. Two runs OOMed at ~26 GB.
- cover5 = phase-1 explicit prime-power builder + explicit kill mop-up
  (kills recorded as ordinary congruences r mod d, verifiable by the
  original verify.py). T=13 attempts (3 configs, survivor): trajectories
  113 -> 300k -> 4.2M -> 14–17M holes entering the 11/13-levels while the
  free-divisor pool stayed ~2e3. Kill capacity is 4 orders of magnitude
  short; aborted.
- Quantified bootstrap gap for T=13 with configs of the class
  2^7·3^4·5^3·7^2·...: need holes <= pool/(q-1) ~ 200 at mid-run where the
  aligned-greedy core leaves ~1e6-1e7 — i.e. core alignment must improve by
  ~4-5 orders of magnitude, which is an exact-cover optimization problem
  (per-level ILP / Owens-style hand structure), not a scale problem.

STATUS: negative (no >= 43; compressed-witness machinery built, validated,
and pushed as the new tooling frontier).

## 12. Phase 3 (2026-07-23): structure-guided attack from the extremal family

New attack (per coordinator: fundamentally different, literature-guided).
Downloaded and fully read Owens's thesis (etd/4329); also re-confirmed via a
July-2026 arXiv paper (2607.19029, min-mod-7 minimal-lcm) that 42 is *still*
the cited record — problem open as of this week.

### 12a. Machine replay of the Owens set-counting calculus (`branchgame.py`)

Formalized the Krukenberg/Nielsen/Owens "branch game": per hole, a pool of
*sets* (partial covers of the branch); ops = MUL (mint sets via free residues
of a small prime) and FILL(p, copies, need) (each p-up-arrow copy consumes
`need` distinct pool sets — sets reusable across different primes but not
across copies of the same prime — and yields 1 new set). Transcribed all 12
counting sections 3.8–3.20 of the thesis. Result: **ALL 12 ledgers replay
PASS at T=42**, faithfully reproducing every stated tally (two sections need
the thesis's fractional-input refinements: 11-up-arrow effective cost 7 in
§3.11; six 3-input copies of 7-up-arrow in §3.12). This is, to our knowledge,
the first machine-checked replay of the Owens ledger arithmetic.

### 12b. Where T=43 breaks (`branchgame.py` part 2)

At T=43 the single modulus-42 congruence (the '2' at level 7·3 in §3.4's
third 7-input, 7·3·2 = 42) is forbidden. Its removal kills the "third-entry
needs only one 3-input" saving used throughout: already in §3.8 the three
7-up-arrow copies cost 6 sets instead of 5 and the ledger fails by exactly
ONE set (18 needed > 17 pooled). Owens's ledgers have slack ≤ 3 everywhere
and slack 0 in §§3.8, 3.15–3.17, 3.19–3.20 — the scheme is *rigid*, matching
his Conclusion ("similar lack of freedom... would be difficult to fill").

### 12c. The hole-42 reduction (`hole42.py`)

Reduction theorem (elementary, but sharpens the target): O has distinct
moduli with min exactly 42, hence exactly one congruence a* mod 42. A ≥43
cover exists iff the class a* + 42Z (minus its overlap with O \ {c*}; in
Owens's tight scheme: none) can be covered by distinct moduli ≥ 43 unused in
O. Inside the hole, modulus m acts as inner modulus n = m/gcd(m,42); each n
has ≤ 8 realizations m = n·g (g | 42). Computed availability: inner n = 2, 3,
4, 6 are fully BLOCKED by Owens's own 7-layer moduli (84; 63,126; 56,168;
252) — the cheap doubling route is closed. Restricting to certainly-unused
moduli (prime factor ≥ 97) with multiplicity 8, the raw density budget needs
inner moduli out to ~10^7 and reproduces the multiplicity-8 analogue of the
minimum modulus problem: the wall shifts but does not fall. Conclusion: any
43 must re-derive the small-prime layers (Owens's own diagnosis), i.e. a new
§3.2–3.4 with one extra unit of slack — the branch-game formalization in
`branchgame.py` is now the right search space for that (finite, ledger-
checkable), and is the concrete next frontier.

Artifacts: `owens42.pdf/.txt` (source), `branchgame.py` (+`branchgame_out.txt`),
`hole42.py` (+`hole42_out.txt`).

STATUS: negative (no >= 43). Frontier-pushed: first machine replay of the
Owens 42 ledger calculus; exact single-set deficit located at T=43; hole-42
reduction + modulus-availability tables computed.

### 12d. Model-level repair search for the S3.8 deficit

Within the branch-game model the one-set deficit at S3.8/T=43 CAN be closed:
after 13^ and 17^ the pool holds 7 sets unused by the first five 3-up-arrow
copies; 1-3 extra 3-up-arrow copies (2 disjoint sets each, +1 set each) lift
the usable count to >= 18 before the three cost-6 7-up-arrow copies. CAVEAT
(unverified semantics): Owens stopped at five 3-copies — extra copies inject
moduli 3^k*m that must not collide with the global 3-layer (S3.2) or the
five originals; a real repair requires the full modulus-collision check,
plus propagating the cost-6 penalty through ALL later sections (S3.10-3.20
each reuse 7-up-arrow savings and have slack <= 3, several with slack 0).
Next session: implement explicit modulus-set tracking in branchgame.py
(replace counts by actual modulus multisets) and re-run the repair search
end-to-end across all 12 ledgers simultaneously.

## 13. Phase 4 (2026-07-23): the complete 43-patch reduction chain (`reduce43.py`)

Pushed the hole-42 idea to its logical end. Chain (R1-R4, details in file):
remove Owens's unique modulus-42 congruence -> cover one class mod 42 with
distinct unused moduli >= 43 -> provably-safe moduli = those with a prime
factor >= 97 (O is 89-smooth) -> inner modulus n has mu(n) = 2^(3-w) safe
realizations (w = #{2,3,7} dividing n) -> build the patch as a p-tower
(p >= 97): budgets refresh every level; mu(p^k) = 8 inputs come free (bare
realizations); every other input needs a full budget-packed cover of Z.

CRISP KERNEL:  patch closes  <=>  S >= p - 9  (>= 88 at p = 97), where
S = max number of pairwise budget-disjoint covers of Z with modulus t used
<= mu(t) times. Small tower primes give no bare inputs and circularity
(their flat inputs need >= 97-divisible t = the original problem).

MEASURED: LP upper bound sum mu(t)/t = 18.9 (t<=100), 29.5 (10^3), 40.2
(10^4), 50.9 (10^5): even PERFECT covers with all moduli <= 10^5 cannot
exceed S = 51 < 88; perfect efficiency needs moduli out to ~1.1e8. Exact
greedy packing over smooth windows: S >= 8 (L=5040), S >= 9 (L=30240,
302400) - real covers plateau near 9 while the bound climbs, the familiar
efficiency decay of thin-density covering (BBMST regime).

CONSEQUENCE (citable): patching Owens-42 to 43 with *provably-unused*
moduli requires a budget-packing of ~88 disjoint covers, which is
LP-infeasible below modulus 10^5 and efficiency-infeasible in practice far
beyond; therefore any minimum-modulus-43 system must either (i) reconstruct
Owens's exact modulus ledger to unlock sub-97-prime unused moduli (a finite
but 10^86-scale bookkeeping problem - the compressed-witness machinery of
Sections 8-10 is the right tool), or (ii) redesign the small-prime layers
for +1 slack (Section 12's branch game is the right search space). These
two now-precise subproblems replace the vague target "build a 43 system".

STATUS: negative (no >= 43). Frontier-pushed: exact reduction chain +
quantified infeasibility of the safe-patch route (S = 9 measured vs 88
required, LP cap 51 at moduli <= 10^5).

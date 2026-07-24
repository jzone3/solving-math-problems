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

## 14. Phase 5 (2026-07-23): full T=43 counting-level blueprint (`blueprint43.py`)

Executed option (ii) end-to-end at the counting level. Key new structural
fact: in the 7-up-arrow, the third-input content 3(2,4,3^(1,2)) recurs at
every level k with moduli 7^k*3*m, and ONLY the k=1 instance of the '2'
entry has modulus 42 < 43 (42 is the unique 89-smooth integer in [42,43)).
Hence (a) the 42-hole is one flat class mod 42 with deeper 2-, 3-, 5- AND
7-structure free inside it, and (b) the T=43 penalty is exactly +1 set per
7-up-arrow copy that cited the third-input saving (its k=1 cell needs one
replacement set at modulus 42*s >= 43... i.e. level-42 substructure).

Blueprint: all 12 Owens ledgers re-derived at T=43 with the penalty applied
(3.11/3.15 unaffected - their savings sit at levels 252/175), each deficit
repaired by extra 3^/25^/125^ tower copies (fresh support) and/or trading a
7^ copy for cheaper sets; plus a NEW 13th section covering the 42-hole,
which closes with a single new prime 97 (pool: seeds + free 3/7/5 minting +
towers 11..89 + extra 11^/13^ copies = 96 sets exactly).

RESULT: **ALL 13 LEDGERS PASS at the counting level** - the first complete
T=43 blueprint in the Owens calculus. Extra primes needed: just {97}
(Owens's own conjecture said "likely require even more large primes").

CAVEATS (why this is a near-miss, not a SOLVED): the counting model
abstracts (1) explicit modulus collisions of repair copies (extra 3^/25^
copies inject moduli 3^k*m / 25^k*m whose global uniqueness is unchecked),
(2) content semantics: trading 7^ copies for other sets preserves set
COUNT but the cross-section pre-cover claims ("19^ needs only thirteen
inputs") must be re-derived for the repaired contents, and (3) the +1
penalty placement. Validation = explicit-modulus witness tracking (the
compressed verify4-style format of phase 2 is the right target: emit each
ledger's actual congruences and machine-check global distinctness + cover).

STATUS: near-miss (counting-level T=43 blueprint passes all 13 ledgers;
explicit-modulus validation outstanding).

## 15. Phase 6 — faithful §3.1–3.4 modulus enumeration; hole-patch corrected (2026-07-23)

Goal: begin explicit-modulus validation of the T=43 blueprint, starting with
the one self-contained piece — the 42-hole patch ("cover one class mod 42
with distinct unused moduli ≥ 43").

### 15a. A first explicit patch — and its refutation

`emit42hole.py` builds an explicit 14-congruence cover of the class 2 mod 42
(machine-verified over lcm 5880: coverage, distinctness, min modulus 49 —
prints PASS on the *internal* checks). Realization rule: inner class
k≡r (mod n) ↔ actual modulus M=n·g, g|42, gcd(M,42)=g, M≥43.

But clearance vs Owens's own moduli exposed that `hole42.py`'s
OWENS_SMALL_MODULI list (7-layer values only) was badly incomplete.
`owens_smooth.py` now enumerates, faithfully from the thesis text, the full
{2,3,5,7}-smooth modulus set of sections 3.1–3.4 (conservatively marking ALL
{2,3,5}-smooth numbers used; the 7-layer entries e1..e6 + 125^8^ + 9^4
transcribed exactly). Key soundness fact: every congruence of sections
3.5–3.20 (incl. Nielsen imports for 11,13,17,23) has modulus divisible by
its prime ≥ 11, so a 7-smooth patch modulus can only collide with 3.1–3.4.

Result: **11 of the 14 patch moduli collide with Owens's own system**
(60, 70, 105, 140, 210, 294, 420, 980, 1960, 2940, 5880 are all used —
e.g. 70 = 7·5·2 is the fourth entry of e4, 294 = 49·6 is e3 at level 2).
The 14-congruence patch is INVALID as a T=43 completion. Negative result,
machine-derived; it also invalidates the "free lists" used in §12–13.

### 15b. The corrected free-modulus budget

From the faithful enumeration, the only free 7-smooth moduli ≥43 are

    M = 7^k · t,  t ∈ {1,2,3,4,5},  k ≥ 2      (49, 98, 147, 196, 245, 343, …)

giving inner budgets per 7-level j = k−1 ≥ 1: n=7^j ×3, n=2·7^j ×1,
n=5·7^j ×1. Total free 7-adic density: Σ_j 3.7/7^j = 3.7/6 = 0.6167 < 1.
So the patch CANNOT close on 7-smooth moduli alone; it must draw on safe
new-prime moduli (any M with a prime factor ≥ 97 — Owens is 89-smooth —
with μ(n) ≤ 8 realizations by the gcd rule). Moduli with largest prime in
[11,89] have UNKNOWN clearance (needs the Nielsen-import reconstruction;
Nielsen's paper downloaded to nielsen40.pdf/.txt for that future step).

### 15c. Reduction and feasibility calculus (patch43.py)

The patch route now reads: cover Z (inner coords) with
  (A) the 7-adic freebies (≤ 0.6167 density, remainder ≥ (33/70)-type
      factors per level: after J levels remainder ∈ [(33/70)^J, (4/7)^J]);
  (B) inner moduli n = d·q (q prime ≥ 97, d 7-smooth) with multiplicity
      μ(n) ∈ {1,2,4,8} — μ collapses to 2 when 2·7 | n, which is the binding
      constraint inside deep cells.

Per-cell relative density from one prime q inside a cell mod 7:
Σ_d μ(7dq)/(dq) ≈ 9.5/q; remainder after level 1 ≈ 4 cells mod 7 (measure
4/7). Needed: Σ_q 9.5/q ≥ 4 → all primes 97…~1100 at perfect efficiency;
with realistic 2–3× overhead, primes up to 10^4–10^5 (Σ 1/q ≈ 0.92 from 97
to 10^5 → ≈ 2.2× margin). So the corrected patch is *density-feasible but
structurally deep*: each cell is itself a covering problem with effective
min modulus 97 and multiplicity 2–4 — comparable in difficulty to the
Krukenberg-era records, i.e. a genuine construction project, not a greedy
run (patchcover.py, a budgeted counting-greedy, stalls exactly as the
budget analysis predicts: 1.7M hole classes after the small levels).

### 15d. Where this leaves T=43

The blueprint's 13th section (NEW 42-hole via 97) survives at the counting
level but §15a shows its concrete tower supports (11^…89^ inside the hole)
carry unknown-clearance moduli, and §15b shows the known-free budget is
0.6167 + safe-prime structure. Two precise routes remain, in order of
promise:
 1. Reconstruct the Nielsen-import ledger (nielsen40.txt, sections for
    11,13,17,23) to unlock the [11,89]-prime moduli inside the hole — the
    blueprint's own section then becomes checkable.
 2. Build the min-modulus-97/multiplicity-≤8 inner cover directly from the
    (B)-budget (density margin ≈ 2.2× with primes to 10^5).

STATUS: near-miss (T=43 counting blueprint stands; first explicit patch
REFUTED by faithful clearance — corrected free-modulus budget derived and
density-feasible; explicit construction of the hole cover outstanding).

## 16. Phase 6b — route-1 yield quantified: Nielsen 11/13 reconstruction (setexpr.py)

Built `setexpr.py`, a set-expression engine for the up-arrow calculus
(C/T/Tow/Lev/Sum nodes -> modulus value multisets; Owens's residue
permutations never change moduli, so Nielsen's 4.5/4.6 value sets equal
Owens's 3.5/3.6). Transcribed Nielsen's full prime-11 section (all ten
inputs of 11^, incl. the composite tenth input) and the prime-13 section
(same ten sets + two modified 11^s, over-approximated safely).

Result: 483 moduli <= 1e5 in the 11-section, 625 in the 13-section, and
the FREED {2,3,5,7,11,13}-smooth patch moduli >= 43 are essentially only
second powers and cross products Nielsen had no reason to touch:

    121, 169, 242, 338, 363, 429, 507, 1331, 2197, 2662  (M < 3000)

Total inner density gain: **0.0515**. Nielsen consumes practically every
first-power 11/13 multiplier (44,55,66,77,88,99,110,132,154,165,176,198,
...), so route 1 (unlock [11,89] moduli) yields ~0.05/prime-pair — an
order of magnitude too little. Extrapolating over primes to 89 gives at
most ~0.2-0.3 extra inner density (and the ledger table shows sections
3.10+ fill towers over nearly all smaller primes, so cross-pair moduli
p*q with 11 <= q < p <= 89 are mostly used too).

CONCLUSION: the 42-hole patch budget is, definitively,
  0.6167 (7-adic free) + ~0.05-0.3 ([11,89] scraps) + safe primes >= 97
    (mu <= 8 per modulus, unbounded prime supply, density divergent).
Safe primes are unavoidable, and the binding problem is the route-2
construction: an inner covering system with effective min modulus ~97 and
multiplicity 2-8, feasible by density (~2.2x margin with primes to 1e5)
but a Krukenberg-scale design project. That - not ledger accounting - is
the true remaining wall between the counting-level blueprint and a T=43
witness.

STATUS: near-miss (T=43 counting blueprint stands; patch budget now fully
quantified; explicit hole-cover construction is the single remaining gap).

## 17. Phase 6c — synthesis: why the patch route (and the 13th ledger) is blocked

Reconciling phases 4-6: density was never the obstruction — FINISHING is.
Every covering system terminates through towers (infinite descending
chains where p-1 of p children are covered at each level). The patch's
free budget supplies only ~9.5 class-equivalents per safe prime q (and 3.7
per 7-level), while a q-tower needs q-1 ~ 96 full covers per level;
phase 4 measured exactly this (exact packing S = 9 budget-disjoint covers
vs S >= 88 required; LP <= 51 even with perfect covers on all moduli
<= 1e5). The 7-adic freebies cannot finish either: 3 classes per level
globally vs 4^j remaining branches.

So: the 42-hole CANNOT be closed by moduli that are provably free
(7^k*{1..5} + safe primes >= 97), rigorously below modulus 1e5 and
decisively in practice; and section 15/16 showed the [11,89] scraps add
only ~0.05-0.3 density with the same finishing defect (squares/cross
products, no tower structure). The counting-level 13th ledger of the
blueprint PASSes only because ledger arithmetic abstracts realizability -
its "96 sets for the 97^" are set counts, not clearance-checked towers.

DECISIVE FINDING of this campaign: minimal patching of Owens's system
cannot reach T=43. Any minimum-modulus-43 covering system requires
redesigning the small-prime (2/3/5/7) layers themselves so that the
42-slot saving is never needed - which is precisely Owens's own closing
conjecture, now backed by machine-checked budget arithmetic (owens_smooth
+ reduce43 + setexpr) rather than intuition. The repaired 12 Owens ledgers
(blueprint43.py sections 3.8-3.20) remain valid counting-level building
blocks for such a redesign.

STATUS: frontier-pushed (patch route to T=43 refuted at explicit-modulus
level below 1e5; T=43 reduced to a small-prime-layer redesign with the
12 repaired ledgers as reusable components).

## 18. Phase 7 — skeleton measurement + the re-aim lemma (2026-07-23)

### 18a. Skeleton experiment (skeleton43.py)

Measured on the 2^7*3^4*5^2*7^2 window and on the faithful used-set:
  * density ceiling of distinct 7-smooth moduli >= 42: 0.6263 (window),
    Owens's faithful skeleton achieves 0.6292 (cap 1e7) — he is
    DENSITY-PERFECT: essentially every 7-smooth modulus >= 42 is consumed
    with disjoint classes. No redesign can free 7-smooth density without
    handing exactly that density to the primes >= 11.
  * T=43 ceiling is exactly 1/42 lower (42 is the unique 7-smooth value
    in [42,43)); greedy packing reproduces the gap (0.5977 vs 0.5728).
  * So ANY T=43 system delegates residual >= 0.3946 to primes >= 11
    (Owens delegates 0.3708). The extra 1/42 is the entire problem.

### 18b. The re-aim lemma (blueprint43b.py — machine-verified PASS)

The 42-cell is EXACTLY covered by re-aiming five of Owens's own moduli,
the multiples of 42 = {84,126,168,252,504}, via the classic distinct
cover 0(2),0(3),1(4),5(6),7(12) scaled by 42. Verified over lcm 504:
coverage, distinctness, containment. Consequence: a T=43 completion does
NOT require any Owens-free modulus — it can steal used ones, replacing
the refuted free-modulus 13th section entirely.

Cost (the obstruction that remains): stealing relocates the hole to the
five cells those moduli previously covered — total measure 2/63, a 4/3
growth over 1/42, because every distinct-moduli cover of Z costs density
>= 4/3 in this cascade. Pure 7-smooth relocation therefore diverges; the
five relocated cells must be absorbed by the >= 11 sections. Unlike the
flat 42-cell, they carry 2/3-adic structure at depths 84–504 inside the
7-layer's e2/e3 entries — the same burden class as the 12 repaired
ledgers' fresh-support assumptions (extra 3^/25^/125^ copies), i.e. the
validation frontier is now UNIFORM: one kind of outstanding check
(fresh-support modulus tracking across sections), no impossible tower
construction left in the blueprint.

STATUS: frontier-pushed / near-miss (T=43 blueprint v2 = 12 repaired
ledgers + re-aim lemma; single remaining validation class:
explicit fresh-support modulus tracking, for which owens_smooth.py +
setexpr.py are the working tools).

## 19. Phase 8: transcription bug fix, corrected free budget (0.94), fuel-conservation law, and geometric decay with safe primes

### 19a. The e3 over-approximation bug (owens_smooth.py, FIXED)

The phase-6 transcription of Owens entry e3 = 3(2,4,3^(1,2)) used
`_mults(18,(3,2))`, i.e. it closed {18} under multiplication by BOTH 3
and 2.  The faithful modulus set of that entry is only
{6, 12} ∪ {3^j, 2·3^j : j >= 2} — the generator 2 was spurious, and it
wrongly marked 4·3^j (36, 108, 324, ...) as used 7-tower entries.
No other entry produces 4·3^j (e2 gives 3^j·8 and 3^j·16·2^i; the 9^·4
structure is a separate non-7 congruence set).  Fix committed; re-run of
the free-multiplier scan now gives primitive free multipliers

    t in {1, 2, 3, 4, 5, 36, 108, 324, 480, 960, 972, 1000, 1920, 2000, ...}

(previously only {1,...,5}).  In particular M = 252 = 7·36 is FREE in
Owens's system — machine-checked (owens_smooth.used_smooth).

Two immediate consequences, both machine-checked:

1. blueprint43b re-aim improves: the 42-cell is covered by four STOLEN
   moduli {84, 126, 168, 504} plus the FREE modulus 252.  Relocated
   measure drops from 2/63 (growth 4/3) to 1/36 (growth 7/6).
2. freefuel.py: corrected total free 7-smooth inner density of the
   42-cell patch problem is 0.93615 (was 0.6167).  Largest new family:
   t = 36 alone contributes 7/36 = 0.19444 (inner moduli 6·3^i·7^k,
   including inner n = 6 at k=1 — the first FREE small inner modulus).

### 19b. Fuel-conservation law (supersedes the section-17 'refuted' verdict)

Measure bookkeeping for the cascade: covering a hole cell (normalized
measure 1) by congruences with multipliers D creates new burden
(stolen old holes + uncovered remainder) of exactly 1 − (free measure
applied).  Stealing is measure-neutral; only FREE moduli make progress.
Hence the 42-cell patch closes measure-wise iff total free inner density
(with alignment) reaches 1.  Section 17's impossibility argument
implicitly required per-level FULL tower covers (the S >= 88 packing);
that architecture is sufficient but NOT necessary — a cascade whose
burden goes to 0 with per-tower trapped-chain patches (one congruence
per tower, standard Krukenberg/Nielsen device, and free moduli are
infinite in number) is also a valid finite closure PROVIDED the endgame
reaches exactly zero via the kill pool.  So section 17 is downgraded
from 'refuted' to 'open, fuel-limited': the corrected fuel is
0.936 (7-smooth) + unbounded safe-prime fuel (sum over q >= 97 of
~Sum_d mu(qd)/(qd) diverges like sum 1/q).

### 19c. Empirical geometric decay (patchcover.py, extended)

patchcover.py upgraded: (i) free budget now uses the corrected
enumeration, (ii) new `process_prime_virtual(q)` processes a safe prime
q >= 97 WITHOUT window blow-up — each free modulus q·d·g kills one
q-child of one cell mod d; choosing distinct residues mod q for all
kills of one prime (total kills < q), counts update exactly as
counts_i *= (q − K_i), den *= q.  Exact big-int arithmetic throughout.

Trajectory (smooth levels 2^3·3^4·5·7^5 then safe primes 97, 101, ...):

    after smooth levels:  measure 0.238269   (2.16M hole classes)
    prime  97: kills= 96  measure 0.209849
    prime 101: kills=100  measure 0.185134   (approx; see patchrun.log)
    prime 103: kills=102  measure 0.164862
    prime 107: kills=106  measure 0.146952
    prime 109: kills=108  measure 0.131266
    prime 113: kills=112  measure 0.117713
    prime 127: kills=126  measure 0.106811
    prime 131: kills=130  measure 0.097208
    prime 137: kills=136  measure 0.088837

Contraction ~x0.89-0.91 per prime, roughly q-independent so far —
consistent with the divergent-fuel prediction, NOT with a stall.  Run
continuing (patchrun.log); with 250 primes the projected measure is
~1e-12.

### 19d. What is and is NOT established

Established (machine-checked): corrected free budget incl. 252 free;
improved re-aim (growth 7/6); fuel 0.936 + divergent safe-prime
reservoir; empirical geometric measure decay under exact counting.

NOT established: a finite closure.  The virtual-prime cascade thins
holes geometrically but never reaches exactly zero: hole CLASS count
stays at 2.16M while counts shrink, and a finite covering system needs
holes = 0 exactly.  The missing device is Owens's fill(q, copies, need)
move — covering q−1 FULL children of a cell at prime q using complete
pool covers, which kills classes outright.  Bridging the measured
geometric decay to an exact zero (pool covers from the free families
{7^k·t} + safe primes, plus trapped-chain patches) is the concrete
remaining construction problem, now with quantified fuel slack.

STATUS: frontier-pushed / near-miss (fuel obstruction of section 17
removed; corrected budget 0.936 + divergent safe primes; exact-zero
endgame is the single remaining constructive gap).

### 19e. Phase 8b: refutation of the fresh-prime full-split closure (patchtest.py)

The tempting endgame — per residual class B, pick a fresh prime q >= 97
and cover B's q children by q congruences with distinct Owens-free
moduli D*q, D | window — is SOUND per child (inclusion machine-checked)
but has an architecture-independent capacity flaw: each class needs
q <= tau(42C) distinct divisors, distinct classes need distinct primes,
so patchable classes ~ pi(tau(42C)) = O(log C) while classes = C.
Table (patchtest.py): C = 61,261,200 gives only 245 usable primes.  It
never closes — reassuringly consistent with Hough's theorem (otherwise
T -> T+1 would iterate unboundedly).

Sharper synthesis of the true remaining gap: the virtual safe-prime
cascade drives MEASURE to 0 geometrically (patchrun.log reached 0.051
by prime 173, still ~x0.93/prime) but leaves hole CLASS COUNT at 2.16M;
exact closure requires class-count concentration (Owens's towers confine
each remainder to ONE chain), and that concentration is precisely what
the corrected 0.936 < 1 smooth fuel cannot buy on its own.  The open
constructive problem is therefore: a smooth-core design whose residual
after the 0.936 fuel is confined to O(pool) classes — not more measure.

STATUS: frontier-pushed / near-miss (phase 8: corrected budget 0.936,
252 free, re-aim growth improved to 7/6, fuel-conservation law, virtual
safe-prime cascade = measure->0 but class-count wall; fresh-prime
full-split closure refuted consistently with Hough).

## 20. Phase 9: explicit modulus-multiset validation of section 3.8 - repair REFUTED as written

Semantics pinned down from the sources (Nielsen sec.2, Owens sec.3.8):
towers are finite, closed by a per-tower fresh large prime chosen to
avoid duplication, so only the smooth/structured parts q^j*(inputs) can
collide; a section's twenty "sets" have concrete relative modulus
multisets (transcribed in ledger38.py: s1..s4 = 1,2,4,8^; s5..s8 = 5x;
s9 = 25^; s10 = 11^; s11..s15 = five 3^ copies over (s1,s2)..(s9,s10);
s16 = 13^; s17 = 17^; s18..s20 = structured 7^ copies).

Machine check (ledger38.py, cap 10^6):
  * baseline sanity: Owens's own sets 1-18 are pairwise modulus-disjoint
    -> PASS (validates the multiset model);
  * the blueprint43 T=43 repair (two extra 3^ copies over sets 11-14,
    flagged "needs explicit check" in phase 5): for EVERY input pair
    (a,b) from the section's sets, the extra 3^ copy collides with
    existing moduli (min collisions > 0 over all 136 pairs; worst
    (s10,s17) = 965).  Root cause: sets 11-15 are already 3^-scalings,
    and 13^/17^/11^ sets contain 3-scaled inputs, so any further
    3-scaling reproduces existing values 3^(i+j)*m.

VERDICT: the phase-5 counting-level repair of section 3.8 is NOT
realizable with fresh moduli inside the section.  A valid T=43 repair
of 3.8 must import supports from outside the section's 3-scalable pool
(e.g. new 2/5-adic structure, or cross-branch imports whose smooth
parts avoid 3^j*{1,2,4,5,8*2^i,...}) - or the deficit must be closed by
a genuinely different small-prime design, as Owens conjectured.

Combined phase 8-9 picture: (i) corrected free fuel 0.936 < 1 (smooth)
with divergent safe-prime reservoir but a class-count wall (sec.19);
(ii) fresh-prime full-split closure refuted (sec.19e); (iii) the
counting-level blueprint's binding repair refuted at explicit modulus
level (this section).  All three walls are now machine-checked and
quantified.

STATUS: frontier-pushed (T>=43 remains open in this session; the
counting-level near-miss of phase 5 is downgraded for section 3.8 by
explicit modulus tracking; remaining routes are cross-section support
imports or a small-prime redesign).

## 21. Phase 9b: the section-3.8 deficit is UNFIXABLE by any local tower mint (exhaustive)

Extending ledger38.py: after including the section's own 19-tower
(moduli 19^k * set-moduli) in the used pool, an extra tower copy of
base q over even the minimal input {1} collides for EVERY base:

  q in {3,9,27}: collides with the five 3^ copies (3^j*m);
  q in {5,25,125}: collides with the 5/25^ structure (125^2 = 25^3);
  q in {7,49}: collides with the 7^ copies (49^j = 7^2j * 1);
  q in {11,121}: collides with s10 = 11^;  q in {13,169}: s16 = 13^;
  q = 17: s17;  q = 19: the section's own 19^ tower;
  q = 23: collides cross-section with 3.9 (Nielsen's 23-section inputs
      include the set 1, so 23^j*1 is used there - thesis text);
  q >= 97 fresh primes: q^ needs q-1 >= 96 inputs, pool has ~18
      (counting-infeasible);
  non-tower support: the only 3-scalable fresh smooth values are
      {125k} with total density 0.0206 (machine-enumerated) - far short
      of the density ~1 a covering set requires.

CONCLUSION (machine-checked at cap 10^6): the +1 set deficit of section
3.8 at T=43 cannot be repaired by ANY additional tower copy or support
importable into the section.  Together with section 20 this closes the
entire 'patch Owens locally' program: T >= 43 requires a genuinely
different global design of the small-prime layers, exactly as Owens
conjectured - now with a machine-verified, exhaustive local argument.

STATUS: frontier-pushed (local-patch program closed exhaustively;
open routes: global small-prime redesign only).

## 22. Phase 10: the ODD-5-POWER loophole - phase-9 refutation REPAIRED (blueprint v3)

Phase 9's refutation of the section-3.8 repair was complete for tower
bases over the sections' 3-scalable pool - but a systematic valuation
scan found the loophole: every modulus in the universal set-building
pattern has 5-adic valuation in {0, 1, even >= 2} (the single 5-scaling
gives exactly 1; 25^ gives even).  The stratum of ODD 5-adic valuation
>= 3 is COMPLETELY UNUSED.  Hence extra 25^ towers over 5-SCALED inputs
mint sets whose moduli 5^(2j+1)*m are all fresh:

    mint1 = 25^(s5,s6,s7,s8):  moduli 25^j*5*{1,2,4,8*2^i}
    mint2 = 25^(s13,s14):      moduli 25^j*3^a*5*{1,2,4,8*2^i}

blueprint43c.py machine-checks (cap 10^6): zero collisions against the
FULL section-3.8 pool including its own 19-tower, zero cross-collisions
between the mints, valuations {3,5,7} all odd.  This restores exactly
the +2 sets the T=43 ledger of 3.8 needs - with modulus-fresh support,
replacing the refuted 3^ repair.  15 fresh 25^ input pairs exist vs the
universal core, enough options for the other penalized sections.

Slack accounting from the T=43 ledgers (blueprint43.py finishes):
12 spare covering sets (19:+2, 29:+2, 31:+1, 41:+1, 43:+1, 53:+1,
59:+1, 61:+3); only 4 are needed to absorb the cells relocated by the
re-aim {84,126,168,504} (with 252 free after the phase-8 correction).

BLUEPRINT v3 = 12 T=43 ledgers with odd-5-power repairs + re-aim of the
42-cell + spare-set absorption of the 4 relocated cells.  All counting
arithmetic and the binding section's modulus freshness are now
machine-verified.  Remaining validation burdens (open, not claimed):
  (a) per-section freshness replay for the other six penalized sections
      (same mechanism, 15 input-pair options each);
  (b) freshness of spare-set instantiations on the relocated branches;
  (c) residue-level emission + independent end-to-end verifier.

STATUS: near-miss / frontier-pushed (strongest state of the session:
the binding section 3.8 is repaired with machine-verified fresh moduli;
no exhaustive obstruction remains - burdens (a)-(c) are finite,
mechanical, and have multiple options each).

## 23. Phase 11: burden (a) discharged - global stratum assignment (blueprint v4)

Re-read Owens's text for every penalized section and extracted the 5-adic /
3-adic strata each section's own sets occupy:

    3.8(19), 3.12(37), 3.14(43), 3.17(59), 3.19(71/73), 3.20(79/83):
        only 5, 25^ usage -> v5 in {0,1,even}; odd v5>=3 FREE.
    3.16(53): fills TWO copies of 125^ (thesis p.15) -> odd v5=3j present,
        so the odd-5 stratum is NOT free there; but 3.16 uses only a single
        3-conjunction (no 3^/9^/27^ towers) -> the v3>=2 stratum IS free.

Mint choices (sections43.py, all checks PASS):
    * six sections: 25^ towers over 5-scaled inputs (odd-5 stratum), as
      machine-verified fresh for 3.8 in blueprint43c;
    * 3.16: 9^ towers over 5-scaled inputs (v5=1, v3>=2 stratum).

Cross-section (global) freshness: a mint lives at P^k * (stratum) where P
is the section's final prime and mints feed only the final tower.  The only
ways another section can reproduce such values are enumerated by
sections43.py, yielding 5 finite ROUTING side conditions (input assignments
the thesis text leaves free):
    S1: 3.16's 125^ sets must not feed its 19^/37^/43^ copies
        (route them into 29^/31^/7^/11^/13^/41^/47^ or the final 53^);
    S2: 3.19's and 3.20's 5*9^-type sets must not feed their 53^ copies.

Ledger arithmetic re-checked at TRUE mint costs (blueprint43d.py): all
3^-based repairs replaced by 25^ (cost 4), 3.16's 125^ repairs by 9^
(cost 2), 3.17's 25^ cost corrected 1 -> 4.  ALL 13 LEDGERS PASS.

BLUEPRINT v4 = blueprint v3 with all seven penalized sections' mints in
machine-checked fresh strata + 5 explicit routing side conditions + true
mint costs.  Burden (a) is discharged at the stratum level; burden (b)
(spare-set instantiation on relocated branches) inherits the same odd-5
mechanism; burden (c) (residue-level emission + end-to-end verifier)
remains the final open step.

STATUS: near-miss / frontier-pushed

## 24. Phase 12: burden (b) discharged - spare-set instantiation freshness

spares43.py (all checks PASS): donate 4 spare covering sets from sections
with slack avoiding 3.16 (donors 19, 29, 61, 61), instantiate each as an
odd-5-stratum mint, and aim it at a relocated cell c in {84,126,168,504}.
Absolute spare moduli are c * P^k * 5^(2j+1) * m.  Machine-checked facts:
  F1 all four cells are 5-free (so spare v5 stays odd >= 3);
  F2 spare moduli have odd v5 >= 3 and no factor 53;
  F3 zero collisions vs Owens's only odd-v5 families (the 3.3/3.4
     125-structures, which have no prime factor >= 11, and the 53-scaled
     125^ values of 3.16) up to 10^7;
  F4 donor slack suffices: need {19:1, 29:1, 61:2} vs slack
     {19:2, 29:2, 61:3} (avoiding 53 entirely).
The spare moduli are also distinct from the donor sections' own repair
mints (v7 = 1 from the cell factor vs 0).

BLUEPRINT v4 status: burdens (a) and (b) are both discharged at the
machine-checked stratum level with explicit routing side conditions.
The single remaining burden is (c): residue-level emission of the entire
integrated system + independent end-to-end verifier - i.e. a full explicit
reconstruction of Owens's ~10^86-congruence system in compressed form with
the v4 modifications.  That is the precise, finite frontier this session
leaves open.

STATUS: near-miss / frontier-pushed

## 25. Consolidated blueprint replay

verify_blueprint4.py independently re-executes all five machine-checked
components of blueprint v4 from a single entry point (ledgers at true
mint costs, re-aim lemma, sec-3.8 mint freshness, global stratum
assignment, spare-set freshness) and prints PASS only if all succeed.
Current output: BLUEPRINT v4 REPLAY: PASS.

FINAL STATUS: near-miss / frontier-pushed.  No T>=43 covering system is
claimed; the counting- and stratum-level blueprint is fully machine-
verified, and the sole remaining burden is residue-level emission of the
integrated ~10^86-congruence system plus end-to-end coverage
verification.

## 26. Phase 13: geometric-alignment gap in the spare-set absorption (correction)

Attempting residue-level emission of the spare sets exposed a gap in the
phase-12 discharge of burden (b).  spares43.py verified MODULUS freshness of
mint-type spare instantiations, but implicitly assumed a ledger spare set can
be "aimed" at an arbitrary relocated cell.  It cannot: a ledger set is a
covering object of its section's WORKING BRANCH (a fixed cell of the 2-3-5-7
core); its absolute moduli are branch-scale * relative moduli.  A relocated
cell c in {84,126,168,504} has modulus with no 5-part and a fixed position in
the smooth core; a section set on a different branch cannot cover it, and
force-scaling by c (as spares43.py modeled) is not the calculus's semantics.

Two further explicit findings from this phase:
  * a no-84/126 re-aim is measure-infeasible: with only quotients {4,12}
    stolen, the safe free quotient pool (7-smooth free t, sum 1/t = 0.321,
    plus stolen 1/4+1/12) reaches only 0.654 < 1 - so cells 84 and 126
    genuinely relocate;
  * sec 3.10's pool CONTAINS relative modulus 84 (7-combo inputs 3*4), and
    sec 3.8's pool contains 49 values divisible by 84 and 82 divisible by
    126 - so cross-scaled instantiations are not automatically fresh either.

CORRECTED absorption mechanism (counting-consistent, geometry-aware): a
relocated cell increases the INPUT COUNT of whichever section's final tower
covers the branch containing it; the extra input is filled by an unused pool
set of that same section (slack).  Moduli stay within the section's own
semantics - no new freshness burden - but this requires locating each
relocated cell inside the branch geography of a section with slack, i.e.
transcribing the smooth core's Figure 3.9 hole map.  That geometric check
supersedes spares43.py's F1-F3 and is the sharpened form of burden (b).

STATUS: near-miss / frontier-pushed (burden (a) discharged at stratum level;
burden (b) reduced to a finite branch-containment check on the core map;
burden (c) unchanged).

## 27. Phase 14: tower-semantics correction - freshness models were over-approximations

Re-reading Nielsen sec. 2 precisely: (q^m)^ = q^(m-1) * q^, with the j-th
input contributing classes a + j*q^(k-1) - q^(m-1) (mod q^k) for ALL k >= m.
So a 25^ contributes moduli 5^k * m for every k >= 2 (both parities of v5),
not 25^j * m.  semfix.py re-runs the sec 3.8 model under the correct
semantics:
  * the phase-10 "odd-5-power" mints COLLIDE (46 collisions) - phase 10/11's
    stratum freshness proofs are INVALID as stated;
  * moreover the corrected pool consumes EVERY 2-3-5-smooth value <= 10^6,
    so no smooth-stratum mint for sec 3.8 exists in the plain value-set
    model at all.

But the same re-reading also invalidates the phase-9 REFUTATION and the
baseline disjointness "PASS" of ledger38.py: Owens's own sets, modeled as
plain value sets under correct semantics, would collide with each other too.
The construction avoids this via Nielsen's "artificially increase n"
mechanism: any tower can be pushed to deeper 2-adic (or other) levels,
shifting its moduli off used values.  Owens: "whenever we use this arrow
notation, we will artificially increase n when needed to avoid repeating
moduli."  Freshness is therefore NOT decidable in the value-set model in
either direction; it is a resource question about deepening room, which the
plain multiset models (phases 9-12) cannot see.

Net state after this correction:
  * the T=43 counting blueprint (blueprint43d.py, 13 ledgers, true costs)
    remains valid - counting is semantics-robust;
  * all phase-9..13 modulus-level refutations AND freshness proofs are
    withdrawn as over-approximations (kept in the log as bounds on the
    plain model);
  * the single sound remaining question is burden (c): residue-level
    emission with explicit n-increase bookkeeping, verified end-to-end.
    This is now provably the ONLY sound validation route.

STATUS: near-miss / frontier-pushed (counting blueprint intact; all
value-set-level freshness arguments, positive and negative, withdrawn).

## 28. Phase 15: residue-level emitter validated against Nielsen's worked examples

emit.py implements the arrow calculus at RESIDUE level (the sound route):
placement of Z-covering systems on classes, q^(inputs) at depth n with
auxiliary p finitization (CRT-merged), exact Nielsen semantics.  Validated
against the paper's own worked examples:
    2^ (p=5, n=5):     10 cosets - matches Nielsen's set (1) exactly;
    3^(1,2^) (p=5,n=4): 49 cosets - matches "forty-nine cosets in S";
both verified to cover Z by the independent recursive-CRT checker
(solutions/P15/verify.py) with all moduli distinct.

This gives, for the first time in the session, machinery in which
freshness/collision questions are DECIDABLE (exact moduli, exact residues,
n-increase expressible as the depth parameter).  Burden (c) roadmap:
  1. emit Owens's smooth core (secs. 3.1-3.4) - the 2/3-skeleton, 5-layer,
     7-layer with the T=43 modification (drop modulus-42 congruence,
     re-aim per blueprint43b);
  2. emit each prime section's sets and towers with per-tower (n, p)
     bookkeeping, auto-increasing n on modulus collision;
  3. run the whole system through verify.py (recursive CRT, feasible since
     coverage factorizes by branch).
Each step is finite and now mechanically checkable.

STATUS: near-miss / frontier-pushed

## 29. Phase 15b: residue emission of the 2/3-skeleton - distinct moduli confirmed

emitcore.py emits Owens's secs. 3.1-3.2 (2^(1) T=42-truncated + 3^(2,4^) on
the odd branch, minus moduli {6,12,18,24,36}, + 81^(1,_) on 21 mod 27) as
explicit congruences and machine-checks them.  With the input-1 model
corrected to a single congruence (not a 2^ tower):
    123 congruences, ZERO duplicate moduli, min modulus 48 (>=42).
Residual holes (density 0.863) are exactly the cells later sections fill:
the even cells {2(4),4(8),8(16),16(32)}, the 4^-input relative-odd "grey"
cells, and the odd 5*3^i / 3^j line (holes 5,15,45,63,... - the input to
sec 3.3, the prime 5).  This is the first residue-level, distinct-modulus
reconstruction of the skeleton and confirms the emitter (phase 15) scales
to real Owens sections.

Remaining work for a full witness is emission of secs. 3.3-3.20 with
per-tower depth bookkeeping - a large but finite engineering task; the
2/3-skeleton demonstrates the method is sound and the moduli come out
distinct without any freshness "proof", because the depth parameter (n) is
chosen large enough per tower exactly as Nielsen/Owens prescribe.

STATUS: near-miss / frontier-pushed

## 30. Phase 16: general arrow->residue compiler (emitgram.py) - distinctness is decidable and exposes the true constraint

Built a GENERAL compiler from the full arrow grammar (C, Two, Arrow, Lev,
Sum) to explicit Z-covering congruence systems, with placement/composition.
Validated against Nielsen's worked examples: 2^ (p=5,n=5) -> exactly 10
cosets; 3^(1,2^) (p=5,n=4) -> exactly 49 cosets; both cover Z with distinct
moduli (independent recursive-CRT verifier).

Crucially, on a deep nested Owens-style fragment the compiler makes the
DISTINCTNESS constraint concrete and decidable:
  * coverage always holds (the calculus is coverage-correct by construction);
  * modulus distinctness FAILS exactly when two inputs of a tower share
    structure - e.g. two plain-C() inputs of a 5^ both yield modulus 5^k at
    every level k (duplicate pure powers of 5).  This is precisely Nielsen's
    "repeating moduli" obstruction: real inputs must carry distinct 2-adic
    (or other) scalings so the level moduli differ, and towers must go to
    deep enough n / distinct aux primes.

This is the sharpest and most honest characterization of what a T>=43
witness requires and why value-set shortcuts (phases 9-12) were unsound: a
full witness is an assignment, across all ~20 sections, of (input structure,
aux prime, depth n) to every tower such that simultaneously (i) coverage
holds, (ii) ALL moduli are globally distinct, and (iii) min modulus >= 43.
emitgram.py can DECIDE (ii)+(iii) for any concrete candidate assignment, but
producing the assignment for the T=43-modified skeleton is the open research
problem - the same one Owens flags in his conclusion.

STATUS: near-miss / frontier-pushed.  Deliverables this session: a validated
residue-level compiler/verifier for the calculus; a machine-checked T=43
counting blueprint (blueprint43d.py); a residue-emitted distinct-modulus
2/3-skeleton (emitcore.py); and a precise, corrected account of why the
value-set freshness arguments (both positive and negative) do not settle the
question.  No T>=43 covering system was constructed or verified; the record
remains 42 (Owens 2014) and the problem is open.

## 31. Phase 17: repeat literature re-check (2015-2026)

Re-queried arXiv (math.NT, "covering system", sorted by date) and web search
for any post-Owens construction with minimum modulus >= 43.  The arXiv API
was rate-limited/intermittent this session, but combined with the earlier
July-2026 check (sec. 1; arXiv:2607.19029's introduction still cites Owens's
42 as the constructive record, and Hough's 2015 Annals result proves the
minimum modulus is bounded, i.e. arbitrary T is IMPOSSIBLE), the evidence is
consistent: no known covering system has minimum modulus >= 43.  I found no
reference contradicting this, so I will not manufacture an unverified witness.

FINAL STATUS: near-miss / frontier-pushed.  Record remains 42 (Owens 2014);
minimum-modulus 43 is open.  All machinery, blueprints, and the corrected
analysis are on branch runs/P15-v4.

## 32. Regression check (session close)

Re-ran the independent explicit verifier on all committed witnesses:
  T=4  PASS  (38 congruences, min 4)
  T=6  PASS  (93, min 6)
  T=8  PASS  (625, min 8)
  T=10 PASS  (1002, min 10)
  T=12 PASS  (2064, min 12)
All verified covering systems remain valid.  The emitgram.py compiler
additionally reproduces Nielsen's two worked examples exactly (10 and 49
cosets) with coverage + distinctness.

These are the honest, machine-verified constructive results of the session.
No T>=43 witness exists.  FINAL STATUS: near-miss / frontier-pushed.

## 33. Phase 18: exact-skeleton-seeded kill machinery (skelkill.py)

Executed the experiment phase 2 flagged as the mandatory next step: seed
the compressed kill-pool endgame with the EXACT Owens 2/3 skeleton
(emitcore.py residue emission, 123 congs, distinct moduli, min 48) instead
of greedy layers, and measure hole-class concentration by exact recursive
coset coalescing over M = 2^13 * 3^7.

Results (skelkill.py):
  raw holes 15,454,616 (density 0.8626) -> coalesced to 58,386 minimal
  cosets.  Structure: the four even cells 2(4),4(8),8(16),16(32) are single
  classes (Owens covers these with secs. 3.3-3.4, not the kill pool); the
  bulk (58k classes) sits at moduli 24576..17915904, i.e. finite-depth
  tower tails plus the grey 4^-input odd lines.
  Kill pools at T=43: window M gives 5 unused divisors; xM*5^2*7 gives 552;
  xM*5^3*7^2 gives 1224.  58,386 >> 1224: INFEASIBLE.

Interpretation: the exact core improves the holes/pool ratio by ~2 orders
of magnitude over greedy (greedy at T=13: ~1e6 classes vs ~1e2 pool;
exact skeleton: 5.8e4 vs 1.2e3), but the endgame remains ~50x short.  The
gap is exactly the 5/7-layer problem: the structured cells (density
0.47 in the even branch alone) must be absorbed by full Owens-style 5^/7^
sections BEFORE any kill pool applies -- i.e. the residue-level emission
of secs. 3.3-3.20 with globally coordinated depths, which remains the open
research problem (secs. 29-30).  Consistent with everything above: no
shortcut around the full construction exists.

STATUS: near-miss / frontier-pushed (unchanged).

## 34. Phase 19: faithful residue emission of Owens sec. 3.3 (emit33.py)

Emitted the prime-5 section onto the even-branch holes 2(4),4(8),8(16),
16(32) with explicit branch classes (window 2^9*3^4*5^3 = 5,184,000):
outer plain 5-split on classes j=0..4 (mod 5) of the even branch, with
  j=0: 16+32;
  j=1: 3( , ,3^(4+8, )+3^(16,32^|16br)) + 64^|32br;
  j=2: 3(64^|32br, 4+8+16+32, 3^(1,2));
  j=3: blank + the 125^ patch (see below);
  j=4: 5(2, 4+8+16+32, 3^(1,2), 3^(32^|16br,4+8+16)+64^|32br,
        5^(1,2,3^(1,2),4^)).

Results: 217 congruences, min modulus 45 (>= 42 OK), ZERO duplicate
moduli, ZERO modulus overlap with the emitted 2/3 skeleton (all sec-3.3
moduli are divisible by 5; the skeleton's never are).  Residual census
MATCHES Owens's diagram (thesis p.6) exactly up to finite-depth tails:
  hole 4:  j=0 blank (1.0), j=1 5/6 (0.8355 obs), j=2 1/3 (0.3375),
           j=3 blank, j=4 1/10 (0.1059);
  hole 8:  same profile as hole 4;
  hole 16: j=0 covered (0), j=1 2/3 (0.676), j=2 1/3 (0.3375),
           j=3 blank, j=4 tails only (663/64800);
  hole 32: j=0 covered, j=1 tails (2025 = 32400/16 2-tail), j=2 tails
           (808 = 675+133), j=3 blank, j=4 tails (558).

Key finding on the 125^ patch (p.6 line "125^(3^(4,x),3^(8,x),
3^(16^,x),3^( ,x))"): the labels 4/8/16^ must be RELATIVE 2-adic sets
inside the 8 hole (matching sec. 3.4's reuse of the modulus families
"125 3^ 4" etc.), but its "x" slots are unspecified sets Owens accounts
only at the counting level -- the measure-level "almost complete"
coverage of the 8-hole's input 4 is NOT derivable from the thesis text
alone; it requires choices resolved elsewhere in his ledger.  Emitting
only the specified parts covers a negligible sliver (307/129600).
This concretely documents, at the first nontrivial section, why
promoting the thesis text to a residue-level witness is a research task:
the text is a counting-level certificate with free residue choices.

STATUS: near-miss / frontier-pushed (unchanged).

## 35. Phase 20: canonical p-adic digits + faithful emission of sec. 3.4
(canon.py, emit34.py; emit33.py upgraded to v2)

Two results:

(1) SEMANTIC DISCOVERY (canon.py).  The tower/split slot labels in the
Nielsen/Owens diagrams are ABSOLUTE p-adic digit positions on the
p-adic tree of Z, shared across sections.  Emitting towers by naive
relative placement (c + m*cls mod m*p^k) permutes digits depending on
the context-modulus unit, so the cross-section "x" bookkeeping ("this
cell is already covered elsewhere") silently breaks: with relative
placement, sec 3.4's x-cells missed sec 3.3's coverage by 10-19% per
cell; with canonical digits (canon.ext) the residuals collapse to
finite-depth tails.  This is the precise mechanical content of the
"geometric alignment" gap flagged in phase 13 -- now solved.

(2) SEC 3.4 EMITTED AND VALIDATED (emit34.py).  Full 7^ tower with
Owens's six inputs incl. the composite set A, over window
2^8*3^3*5^4*7^2 (and a deeper 3^4 run): 266 congruences, min modulus
42, ZERO duplicate moduli, ZERO overlap with sec 3.3 and the 2/3
skeleton (all sec-3.4 moduli contain 7).  The three 125^.3^.m sets are
injected as separately-verified relative covers of the hole-8 sliver
(their moduli need 5-exponent 5, beyond the window).  Residual census
converges to Owens's target diagram as depths increase (E3 3->4):
  hole 8:  j=1 4.6%->2.9%, j=2 4.5%->2.0%, j=3 3.8%->2.9%,
           j=4 1.7%->1.0%  (floor = 1/49 = 2.04% 7-recursion tail
           + shrinking 3-tails); j=0 = the one hole Owens leaves open
           ("5( ,x,x,x,x)", filled by later sections);
  hole 16: all five classes -> tails only;
  holes 4, 32: unchanged from sec 3.3, as the thesis states.

Combined system so far (skeleton + 3.3 + 3.4): 606 congruences, all
moduli pairwise distinct, min modulus 42.  This is now a residue-level
reconstruction of Owens secs. 3.1-3.4 -- the deepest machine-verified
replica of the record construction.  Remaining: secs. 3.5-3.20 (the
primes 11..89), each of which cites Nielsen's sets wholesale; their
faithful emission needs Nielsen's full section data plus the same
canonical-digit discipline.

## 36. Phase 21: sec 3.5 (the prime 11) emitted; two new reconstruction
## obstructions identified and quantified

(0) 81^(1,_) PLACEMENT CANONICALIZED (emitcore.py).  Nielsen 4.2's
extra tower uses moduli 3^n, n>=4 (pure powers of 3, no factor 2).
Canonical reading consistent with "one input in a 27 and one input in
a 27^" leftover: the tower sits over the 18-hole 3 (mod 9) and covers
the digit-1 chain from level 2 on (30 mod 81, 84 mod 243, ...).  The
level-1 digit-1 cell 12 (mod 27) cannot be covered (27 = 3^3 < 3^4)
and is exactly Nielsen's "one input in a 27"; the digit-2 chain
21 (mod 27), 57 (mod 81), ... is the "one input in a 27^".  Machine
census (2^7*3^7 window) confirms: 18-hole residual = 12 (mod 27)
u {21 (mod 27), 57 (mod 81), ...} u 3-adic tail, exactly.

(1) SEC 3.5 EMITTED (emit35.py) = Nielsen 4.5 with Owens's
permutation (class mod 11*5 moved to 4 (mod 5), realized as the swap
1<->4 on the first 5-adic digit of every 5^ tower cited in the
section).  Branch B = [1 (mod 12)] u [1 (mod 4) n 3 (mod 9)]; all ten
Nielsen input sets transcribed with canonical digits (S1: 4; S2: 8^;
S3: 3*2+27*1+27^*2; S4: 3*4+27*4+27^*8^; S5: 3*8^+9*8^; S6-S8 the 5^
sets; S9 the 7^ set; S10 the two-summand set).  1326 congruences over
depths (D2,D3,E5,E7,E11)=(6,5,2,2,2), min modulus 44, ZERO modulus
overlap with the skeleton / sec 3.3 / sec 3.4 (every sec-3.5 modulus
contains 11).  Coverage census per input over 2^7*3^6*5^2*7^2: S1
covers B exactly; S2-S5, S8 miss only finite-depth tails.

(2) OBSTRUCTION A -- REPEATED MODULUS FAMILIES INSIDE NIELSEN'S OWN
SETS: 48 internal duplicate moduli, all from the family
72*2^j*5^m*7^l*11^k.  Root cause is textual, not a transcription slip:
Nielsen's tenth input contains 5^(3*3(x,x,8^), 3*2, 3*4, 3*8^+9*8^),
whose first slot (3*3(x,x,8^): 9*8*2^j...) and fourth slot (9*8^:
9*8*2^j...) generate the SAME modulus values at different residues.
In Nielsen's finite system these are disambiguated by the "artificially
increase n" depth mechanism (truncate one family earlier and close it
with a different auxiliary prime) -- a choice the text does not
specify.  This is the same repeating-moduli phenomenon documented in
phase 16, now located inside a concrete cited set.

(3) OBSTRUCTION B -- THE CROSS-SECTION x-SLOTS NEED THE "COVERS MORE
THAN NEEDED" PURE-MODULUS CONVENTION: the uncovered cells of S6, S7,
S9, S10 concentrate exactly on (3 mod 9) n (5-digit-3 cells) n B --
the slots Nielsen marks as already covered by sec 4.3 ("the third
input in 5^ ... already has 3 (mod 9) covered", the property Owens
explicitly preserves in his sec 3.3 remark).  Nielsen 4.3 (lines
436-458) states that several entries of the prime-5 sets apply "to the
entire congruence class 2 (mod 2)" or larger -- i.e. those contents
are emitted with PURE moduli (no 2-adic context factor), so they cover
the odd branch too, with moduli like 9*5^m = 45, 225, ... >= 42.  Our
emit33.py placed every content inside the 2-adic hole context, so its
coverage is even-only and the odd-branch x of sec 3.5 fails (machine
census: no 5-class has (3 mod 9) n (1 mod 4) covered by secs 3.1-3.4
as currently emitted).  FIX REQUIRED (next phase): re-emit the flagged
slot-3 contents of sec 3.3 with pure moduli per the convention,
re-checking min modulus (>=42) and global distinctness, then re-run
the sec-3.5 census.

## 37. Phase 22: canonical slot->digit convention discovered and
## validated; obstruction B RESOLVED; combined 3.1-3.5 replica

(1) THE SLOT->DIGIT CONVENTION.  For every p-split / p-tower in the
Nielsen/Owens diagrams, slot t sits on the canonical p-adic digit t
for t < p, and slot p sits on the recursion digit 0.  Independent
textual confirmation: Nielsen 4.3's "lowest gray circle represents the
class 20 (mod 25)" -- the fifth-slot-then-fourth-slot cell is digits
(0,4), i.e. 0 + 4*5 = 20 (mod 25), exactly.  emit33.py and emit34.py
were remapped accordingly (previously slots were placed on digits
t-1); emit35.py already used this convention.

(2) OBSTRUCTION B RESOLVED.  With the remap, sec 3.3's third
hole-input (5-digit 3) places 3^(1,2) on the 3-split's recursion
digit, and its ONE-cells have PURE moduli 45, 135, ... (no 2-adic
context factor) -- these cover (3 mod 9) n (3 mod 5) on BOTH parities,
which is precisely the "covers more than needed" property Nielsen
states in 4.3 and Owens preserves in his 3.3 remark.  Machine check:
sec 3.5's input S6 = 5^(1,2,3*1,4) now covers its branch with ZERO
uncovered cells (was 639,744 under the old mapping), and S7's 3 mod 45
gap disappears likewise.  The sec 3.4 residual census keeps Owens's
target diagram shape under the remap (hole 8 open only on 5-slot 1,
hole 16 tails only).

(3) COMBINED 3.1-3.5 STATE: skeleton 123 + sec3.3 217 + sec3.4 266 +
sec3.5 1326 congruences; pairwise modulus overlap between sections =
0 everywhere; min modulus 42 (sec3.4), 44 (sec3.5), 45 (sec3.3),
48 (skeleton).  Explicit witnesses T=4..12 still PASS (regression).

(4) REMAINING GAPS (quantified, honest):
  a. Obstruction A (48 duplicate moduli inside Nielsen's own tenth
     input, family 72*2^j*5^m*7^l*11^k) still needs the unspecified
     depth/auxiliary-prime disambiguation;
  b. S9/S10 residuals are now dominated by finite-depth window
     artifacts (7-digit-0 recursion cells), EXCEPT one genuine slot:
     S10's 7-digit-6 set leaves (reduced 18-part) n (5-digit sigma(1))
     uncovered -- the covering source of this x in Owens's rearranged
     system is not yet identified from the text;
  c. secs 3.6-3.20 remain to be emitted.

## 38. Phase 23: sec 3.6 (the prime 13) emitted

emit36.py: Nielsen 4.6 with Owens's permutation (class mod 13*5 moved
to 2 (mod 5)), on the complementary branch B' = 3 (mod 4) side of the
6/18 holes.  Contents are built from TAGGED atoms (tag = which 2-adic
symbol the atom depends on), so branch, 5-adic permutation, and the
keep/x filter are parameters:
 - first ten 13^ inputs = the ten 4.5 sets with 4 / 8^ -> 3 (mod 4);
 - input 11 = modified 11^ copy keeping only 4/8^-dependent atoms
   (Nielsen's "replace each 20 and 21 by an x": the 2-adically
   unrestricted entries are already covered on this branch by sec 3.5,
   confirmed by the census with secs 3.1-3.5 in the base);
 - input 12 = same skeleton with 4 -> 1 and 8^ -> 2 (fresh classes,
   moduli carry 11*13 >= 143 so the min-modulus bound is safe).

Results: 2338 congruences, min modulus 52; modulus overlap with
skeleton / 3.3 / 3.4 / 3.5 all ZERO.  Census (two windows, base =
secs 3.1-3.5): first-ten inputs 1.5% uncovered (concentrated on the
8^-input's beyond-window 2-tails, dropped measure 9.3e-2); inputs
11/12 6.4% uncovered (reduced window 2^5*3^5*5^2*7*11*13, dropped
4.9e-2) -- residuals sit in the known artifact locations plus the
same S10 open slot as sec 3.5.  Internal duplicate moduli: 104, all
the 2520*13-family -- the SAME obstruction-A repeating-moduli family
(tenth-input slot 1 vs slot 4), doubled by the two 11^ copies.

Cumulative residue replica: secs 3.1-3.6, ~4900 congruences, zero
cross-section modulus collisions, min modulus >= 42 throughout.
Remaining: obstruction A disambiguation, S10's unidentified x-source,
secs 3.7-3.20.

## 39. Phase 24: obstruction A settled symbolically (collide35.py)

Question: can Nielsen's own depth mechanism ("artificially increase
n", sec 2) disambiguate the repeated-modulus family in the tenth
input's second summand, 5^(3*3(x,x,8^), 3*2, 3*4, 3*8^+9*8^)?

Method: exponent-vector families (a,b,c,e) = (2,3,5,11)-adic
valuations, checked for intersection symbolically -- depth- and
window-independent.

Machine-checked results:
 - literal reading: slot 1 (8^ on 1 (mod 9)) and slot 4 (9*8^ on
   3 (mod 9)) both realize 2^a 3^2 5^c 11^e with a>=3, c>=1: COLLIDE
   (e.g. modulus 3960 appears twice);
 - R1 stagger the 2-chain: still collide (and by Nielsen's own arrow
   definition the pure-2 part {2^m..2^n} always contains a=3);
 - R2 move slot 1 one 3-level deeper: collides with the 27^*8^
   chains of S4/S8/slot-5;
 - R3 widen to all of 1 (mod 3): collides with 3*8^ (S7 slot 4);
 - R4 drop the 5-part: collides with S5 = 3*8^+9*8^.

CONCLUSION: the repeated modulus in Nielsen 4.5's tenth input cannot
be removed by any of the local mechanisms the paper describes; since
Nielsen asserts global distinctness, the actual construction must use
an unstated NON-LOCAL re-aim (e.g. per-level auxiliary-prime closures
absorbing one family), whose residue-level data the paper does not
provide.  Reconstructing the record system residue-exactly therefore
requires solving a small research problem the source leaves open --
consistent with phase 19's finding on the thesis "x" slots.  This is
the sharpest form of obstruction A and applies verbatim to the copies
in sec 3.6.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 40. Phase 25: constructive re-aim search -- total divisor saturation

Goal: fix obstruction A constructively, by re-aiming the slot-1
family of Nielsen 4.5's tenth input onto genuinely unused moduli.
A single-congruence re-aim of a cell (c, M) can only use DIVISOR
moduli of M (one cannot add primes: covering all classes of a new
prime needs p-1 congruences of the SAME modulus, which is illegal).
So candidate rescues are exactly the divisor exponent vectors
(a, b, c, d, e) <= (j, 2, m, l, k).

Machine scan (collide35.py saturation_scan) against the concrete
emitted moduli of secs 3.1-3.6 (~4900 congruences):

 - a=0 (whole 1(9)-cell, 3465-family): USED (S10 slot4's 3*3(x,x,1))
 - a=1 (9*2-family): USED (S10 slot4's +9*2)
 - a=2 (9*4-family): USED (S10 inner slot4's 9*4)
 - a=3 (start of any 2-chain): USED (the colliding 9*8^ itself)
 - b=3 shifts (27-cell, 27*4): USED (the 27^* chains)
 - c=2 shift (using 25^ for the inner tower, i.e. Nielsen's
   "artificially increase n" applied to the 5-arrow): shifts BOTH
   colliding slots together, so the internal pair persists at every
   c; and the c=2 stratum is itself used by S6/S7 level-2 families.

CONCLUSION (sharpest form of obstruction A): the divisor-vector
space around the tenth input is TOTALLY SATURATED -- Owens's
density-perfect smooth core leaves no unused divisor family, and
every depth shift (2-adic, 3-adic, 5-adic) either self-collides or
lands on an occupied stratum.  A residue-exact repair of Nielsen
4.5/Owens 3.5 therefore requires restructuring the input sets
themselves (redistributing which cells each slot covers), i.e. the
same open redesign problem as the T=43 attempt.  This closes the
local-repair program at residue level, mirroring the counting-level
closure of phases 6-9b.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 41. Phase 26: exact-cover restructuring search (search10.py)

New attack after phase 25 closed local repair: treat the tenth
input's colliding region R = (1 mod 9 u 3 mod 9) n {v2>=3} inside a
fixed (5,7,11)-context as a finite exact-cover problem over the
dyadic-triadic cell tree, searching for ANY packing of R by free
divisor vectors (a,b) = (v2,v3), including binary/ternary depth
cascades (split cell (a,b) -> (a+1,b)x2 or (a,b+1)x3).

Machine result: the used-vector census of the concrete secs 3.1-3.6
emission (~4900 congruences) shows the ENTIRE box a<=8, b<=7 is
occupied -- 72 of 72 vectors used in the context (c,d,e>=1, f=0).
The vectors "free" beyond the box (a>=9 or b>=8) are artifacts of
finite emission depth: symbolically every used family is an infinite
ray ({a>=a0} chains, {b>=b0} 27^-type chains), so no (a,b) vector is
free at ANY depth.  The packer accordingly fails at the very first
chain cell, and depth cascades only push the demand into the next
saturated stratum (c+1 levels are occupied by the same towers'
level-(m+1) families).

CONCLUSION: obstruction A cannot be repaired by any redistribution
of the tenth input's coverage within its own (5,7,11)-context --
saturation is total, a direct consequence of the density-perfect
smooth core (phase 7).  Any valid fix must re-balance coverage
ACROSS the 5/7/11 sections (change which context cells each section
covers), i.e. the global redesign that is precisely the open T=43
problem.  The counting-level (phases 6-9b), divisor-vector (phase
25), and exact-cover (this phase) closures now form a three-level
machine-checked proof that the record construction admits no local
modification path to 43.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 42. Phase 27: sec 3.7 (the prime 17) emitted (emit37.py)

Owens 3.7 = a 17^ on the 12-hole (the single coset 13 (mod 24)
reopened by removing the modulus-12 congruence of the 3-tower),
filled with sixteen of the seventeen sets Nielsen constructs in his
prime-19 section (4.8), dropping the one set that is itself a 17^.

Transcription decisions (canonical, phase-20/22 semantics):
 - contents are absolute cells CONTAINING the branch (13 mod 24 is
   inside 1 (mod 4), 1 (mod 12), 4 (mod 9), 5 (mod 8)); moduli are
   content * 17^k with no 24-factor, matching Nielsen's dropped
   moduli 19/38 for the bare sets 1 and 2;
 - 9^(a,b) towers anchored at the hole's mod-9 cell 4 (mod 9);
 - the composite sixteenth set (reserve 5^ + 7^ + 11^ + big 13^)
   transcribed with blank/tail placeholders where Nielsen's
   "save room" 11^-with-three-inputs notation under-determines
   slots; "5^*c" = content on the 5^ chain cells 5^(k-1) (mod 5^k).

Machine-checked results:
  sec3.7: 2576 congruences, 369 placeholders
  min modulus: 51
  dups within sec3.7: 0
  overlap w/ skeleton, secs 3.3/3.4/3.5/3.6: 0, 0, 0, 0, 0
Census (census37.py, window 2^6 3^5 5^2 7*11*17): 12-hole residual
2.8%, concentrated in the recursion tail (class 0 mod 17), the
T13/T14 x-slots (classes 7/8; they cite prime-11 partial covers at
depths beyond this section's E11=1), and the dropped-measure strata
(13-moduli outside the window).  Same structure in the w13 window.
Residuals are finite-depth/window artifacts plus the documented
x-slot citations -- NOT claimed covered.

Cumulative replica: secs 3.1-3.7, ~7500 congruences, all moduli
pairwise distinct across sections.  Notably sec 3.7 avoids
obstruction A (no repeated-modulus family): Nielsen's 4.8 sets are
collision-free under the canonical reading.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 43. Phase 28: sec 3.8 (the prime 19) emitted (emit38.py)

Owens 3.8: branch 2 (mod 4); a 19^ completely fills the first input
in the 5 on the 4 hole (cell 6 mod 20).  Twenty sets built exactly
per the text: 1, 2, 4, 8^; the 5-conjunctions 5*1, 5*2, 5*4, 5*8^,
25^(1,2,4,8^); an 11^ copy with slot 6 = x ("already covered on this
branch"); five 3^ copies over the ten sets in sequence; a 13^ over
the first twelve; a 17^ over the first sixteen; and three 7^ copies
including the prescribed 7^(1,2,3(x,1,x),4,8^,3^(2,4)).  Sets 1 and
2 dropped as 19^-inputs (moduli 19, 38 < 42), leaving the eighteen
needed inputs.

Reconstruction choices (Owens does not write out the other two 7^
layouts): U19 = 7^(5*1,5*2,45-cell,5*4,5*8^,25^) and
U20 = 7^(11^,13^,9-cell,3^(5*2,5*4),17^,3^(5*8^,25^)).  Finding a
collision-free assignment required three iterations -- the first two
natural choices produced 60 and 4 repeated moduli respectively
(e.g. 1995 = 3*5*7*19 minted by both a bare 3-input in one 7^ and a
5-scaled 3^ level in another), a small live instance of exactly the
repeated-moduli discipline Nielsen describes.  The final assignment
is machine-verified collision-free.

Machine-checked results:
  sec3.8: 4124 congruences, 37 placeholders
  min modulus: 57
  dups within sec3.8: 0
  overlap w/ skeleton and secs 3.3-3.7: all 0
Census (window 2^7 3^4 5^2 7*19): residual concentrated in the
19-classes hosting the 11^/13^/17^ sets (their moduli fall outside
the window) plus recursion tails -- structural window artifacts;
the 2/3/5/7-smooth classes are covered.

Cumulative replica: secs 3.1-3.8, ~11,600 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 46. Phase 29 (sec 3.9, prime 23) + a 9^-anchor bugfix (2026-07-22)

Bugfix found while emitting sec 3.9: my 9^ towers in emit37.py were
anchored at the hole's mod-9 residue (4 mod 9), but the 12-hole
13 mod 24 fixes only mod 3 = 1 -- a 9^(a,b) must be a tower over the
mod-3 cell (level m modulus 9*3^(m-1)), else two thirds of the branch
is silently missed.  Fixed in emit37.py (nineup anchored at (1,3)):
sec 3.7 residual dropped 5,146,880 -> 2,914,944 cells with the
remainder now confined to classes 0/15 (tail + the dropped composite
set 16's out-of-window 11/13 moduli) and small tails at 12/13/14.
Same convention applied in emit39.py (anchor (2,3)).

emit39.py -- Owens sec 3.9 = Nielsen 4.9 on the 24-hole (17 mod 24,
reopened modulus-24 congruence), with Owens's swap 5^(1,2,4,8) ->
5^(2,1,4,8).  Twenty-two 23^ inputs: atoms 2,4,8,16^ and their
3-conjunctions, 9^(1,2), 9^(4,8), three 5^ sets, two 7^ sets, the
reserve set 9^(16^,_) + 7^(9^(x,*) five ways, 5^(9^(x,*) four ways)),
one each of 13^/17^/19^ over previous sets (padded with 1), and two
11^ copies over the twenty 11-free sets (V1-V10 and V11-V20).

Machine-checked results:
  sec3.9: 3108 congruences, 87 placeholders
  min modulus: 46
  dups within sec3.9: 0
  overlap w/ skeleton and secs 3.3-3.8: all 0
Census (window 2^7 3^4 5^2 7*23): classes 18-22 (the 13^/17^/19^/11^
sets, moduli outside the window) plus tails account for the residual;
all 2/3/5/7-smooth classes covered.

Cumulative replica: secs 3.1-3.9, ~14,700 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 47. Phase 30 (sec 3.10, prime 29) (2026-07-22)

emit310.py -- Owens sec 3.10: prime 29 fills TWO holes at once (the
third and fifth empty holes of Fig 3.9): branch 2 (mod 4), first
input of a 3 (1 mod 3), second and third inputs of the 5 -- target
cells (2,5) and (3,5).  Twenty-nine sets built per the text:
atoms 1..8^ + 3-conjunctions + 9^(1,2)/9^(4,8^); five 5-conjunction
sets each covering both 5-inputs (pairing the ten sets in sequence --
reconstruction choice); the double 25^ set; a 17^ over the first
sixteen; Owens's four combined 7^ sets written out explicitly
(slots 1,2 bare covering both 5-inputs, slot 3 x, slots 4-6 5-scaled
at (3,5), set 21 carrying the reserve 25^(9^,9^,_,_)@(2,5)); two 11^
copies; a 23^ (last input count under-determined -> placeholder);
two 13^ copies; two 19^ copies at 13 inputs each (five inputs apply
to the whole 4 hole per sec 3.8 -> 5 x-slots); and the final
7^(9^,9^,x,5*9^,5*9^,B) with B = 17^ over the first sixteen sets.
Set 1 dropped (29 < 42); 29^ filled with the twenty-eight.

Machine-checked results:
  sec3.10: 12414 congruences, 133 placeholders
  min modulus: 58
  dups within sec3.10: 0
  overlap w/ skeleton and secs 3.3-3.9: all 0
Census (window 2^7 3^4 5^2 7*29): residual confined to the 29-classes
hosting 11/13/17/19/23-towers (moduli outside the window) plus
recursion tails; all 2/3/5/7-smooth classes covered.

Cumulative replica: secs 3.1-3.10, ~27,100 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 48. Phase 31 (sec 3.11, prime 31) (2026-07-22)

emit311.py -- Owens sec 3.11: the 36-hole (33 mod 36, i.e. 1 mod 4 n
6 mod 9).  Thirty-one sets per the text: atoms 1..8^ with 3-, 9-
conjunctions; 27^(1,2)/27^(4,8^) over (6,9); three 5^ copies with the
prescribed 5^(2,4,8^,1) (reserved for sec 3.16); three 7^ copies at
five entries each; the composite set C + 7^(five 5^(x,x,*,*)
wrappers); three 11^ copies at eight entries (the text's two
partial-5^ entries are under-determined -> placeholders); two 13^,
two 17^ (thirteen entries), one each 19^/23^/29^.  Set 1 dropped
(31 < 42); 31^ filled with the thirty.

Key distinctness mechanism confirmed again: every intermediate tower
lives inside a 31-cell, so all section moduli carry 31 and
cross-section overlap is structurally zero; within-section reuse of
the same set across towers of different primes is safe (the tower
prime enters the modulus), while same-prime copies get disjoint set
lists.

Machine-checked results:
  sec3.11: 16814 congruences, 151 placeholders
  min modulus: 62
  dups within sec3.11: 0
  overlap w/ skeleton and secs 3.3-3.10: all 0
Census (window 2^7 3^4 5^2 7*31): residual confined to classes
hosting the 11/13/17/19/23/29 towers (out-of-window moduli) + tails.

Cumulative replica: secs 3.1-3.11, ~43,900 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 49. Phase 32 (sec 3.12, prime 37) (2026-07-22)

emit312.py -- Owens sec 3.12: first input of the 5 on the 8 hole
(36 mod 40), restricted to the first two 3-inputs (third deferred to
sec 3.16 / prime 53).  Thirty-seven sets: atoms 1,2,4,8,16^; the four
3-conjunction sets incl. 3(3^(1,2),3^(4,8)) and the split set
3(16^,_)+5*3(_,16^); 5*copies of the first eight; two 25^ copies
anchored at (1,5); six 7^ copies at three inputs each (sec 3.4 covers
the rest); two 13^; two 19^ at thirteen inputs (sec 3.8); one 29^,
one 31^; three 11^; two 17^; one 23^.  Set 1 dropped (37 < 42); 37^
filled with the thirty-six.

Machine-checked results:
  sec3.12: 13410 congruences, 153 placeholders
  min modulus: 74
  dups within sec3.12: 0
  overlap w/ skeleton and secs 3.3-3.11: all 0
Census (window 2^7 3^4 5^2 37): residual confined to the classes
hosting 7/11/13/17/19/23/29/31 towers (out-of-window moduli) + tails.

Cumulative replica: secs 3.1-3.12, ~57,300 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 50. Phase 33 (sec 3.13, prime 41) (2026-07-22)

emit313.py -- Owens sec 3.13: second 3-input of the second 5-input on
the 4 hole (2 mod 4 n 2 mod 5 n 2 mod 3).  Sets per the text: atoms
1,2,4,8^ + 3-conjunctions + 9^(1,2)/9^(4,8^); an 11^ and a 13^
(eleven inputs); twelve 5*copies; three 25^; two 19^ at thirteen
inputs; a 29^; six 7^ at five inputs; a 31^; two 17^; a 37^; two 23^
at nineteen inputs (using sec 3.9's 5^(2,1,4,8) swap).  Owens's ledger
says forty-one sets; the sequential reconstruction yields forty-two,
so the second 23^ copy is spare (noted).  41^ filled with forty sets
after dropping 1.

Machine-checked results:
  sec3.13: 32834 congruences, 117 placeholders
  min modulus: 82
  dups within sec3.13: 0
  overlap w/ skeleton and secs 3.3-3.12: all 0
Census (window 2^7 3^4 5^2 41): residual = out-of-window tower
classes + tails, as in previous sections.

Cumulative replica: secs 3.1-3.13, ~90,100 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 51. Phase 34 (sec 3.14, prime 43) (2026-07-22)

emit314.py -- Owens sec 3.14: middle 3-input of the fourth 5-input on
the 4 hole (2 mod 4 n 4 mod 5 n 2 mod 3).  Forty-two sets exactly per
the text: atoms + 5-conjunctions + 25^; an 11^ with one covered
input; 3*copies of the first ten; five 9^ pairs (incl. 9^(25^,11^));
five 7^ copies at five inputs; 31^, 29^, two 17^, 23^, a partially
filled 37^; three 13^; three 19^ at thirteen inputs.  Since 43 >= 42
NO set is dropped -- the bare set 1 gives the minimum modulus 43 and
all forty-two sets fill the 43^.

Machine-checked results:
  sec3.14: 88624 congruences, 117 placeholders
  min modulus: 43
  dups within sec3.14: 0
  overlap w/ skeleton and secs 3.3-3.13: all 0
Census (window 2^7 3^4 5^2 43): residual = out-of-window tower
classes + tails, as before.

Cumulative replica: secs 3.1-3.14, ~178,700 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 52. Phase 35 (sec 3.15, prime 47) (2026-07-22)

emit315.py -- Owens sec 3.15: first 3-input of the fourth 5-input on
the 4 hole (2 mod 4 n 4 mod 5 n 1 mod 3).  Same twenty-five sets as
sec 3.14 with 3/9^ over 1 mod 3; the 25^ broken into five pieces
(four level-1 25*c congruences + the deeper tower) to feed seven 7^
copies at four inputs each (slot 4 = the input needing only a 25);
then two 17^, 29^, 31^, three 13^, three 19^ at thirteen inputs,
41^, 43^, two 23^ -- forty-six sets, 47^ filled with all of them
(47 >= 42, nothing dropped).

Machine-checked results:
  sec3.15: 123172 congruences, 159 placeholders
  min modulus: 47
  dups within sec3.15: 0
  overlap w/ skeleton and secs 3.3-3.14: all 0
Census (window 2^7 3^4 5^2 47): residual = out-of-window tower
classes + tails, as before.

Cumulative replica: secs 3.1-3.15, ~301,900 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 53. Phase 36 (sec 3.16, prime 53) (2026-07-22)

emit316.py -- Owens sec 3.16: last (fifth) 5-input on the 4 hole,
branch (2 mod 4) n one hole mod 25 (the printed "mod 25*3^*4" is
OCR-garbled; reconstruction uses the 25-cell (5,25), marked as a
choice).  Fifty-two sets: atoms + 3-conjunctions; 5* and 25* copies;
two 125^ towers over (5,25); two 19^ at thirteen; 29^; 31^ at
twenty-nine (sec 3.11's reserved 5^(2,4,8^,1) carries over); six 7^
with the third input covered; three 13^; 37^; four 11^; 41^; 43^;
47^; two 23^; three 17^.  53^ filled with all fifty-two.

Machine-checked results:
  sec3.16: 175414 congruences, 115 placeholders
  min modulus: 53
  dups within sec3.16: 0
  overlap w/ skeleton and secs 3.3-3.15: all 0
Census (window 2^7 3^4 5^3 53): target cell FULLY covered in-window
(0 uncovered of 686880; dropped measure 0.11 from out-of-window
moduli).

Cumulative replica: secs 3.1-3.16, ~477,300 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 54. Phase 37 (sec 3.17, prime 59) (2026-07-22)

emit317.py -- Owens sec 3.17: last (third) 3-input in the first
5-input on the 8 hole (4 mod 8 n 1 mod 5 n 0 mod 3).  Fifty-eight
sets per the text, incl. the half-filled reserve 9^ device (set 25 =
5*9^(16^,_)+9^(_,16^)), three 25^, ten 7^ copies at three inputs,
four 11^, four 13^, three 17^, three 19^ at thirteen, plus singles
23/29/37/41/43/47.  59^ filled with all fifty-eight.

Machine-checked results:
  sec3.17: 72700 congruences, 249 placeholders
  min modulus: 59
  dups within sec3.17: 0
  overlap w/ skeleton and secs 3.3-3.16: all 0
Census (window 2^7 3^4 5^2 59): residual = out-of-window tower
classes + tails.

Cumulative replica: secs 3.1-3.17, ~550,000 congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 55. Phase 38 (sec 3.18, primes 61/67/89) (2026-07-22)

emit318.py -- Owens sec 3.18: third 3-input of the fourth 5-input on
the 4 hole, split mod 8: 61^ on (2 mod 8), 67^ on (6 mod 8) with two
of the 67-entries supplied by depth-shifted 61^ towers (levels 3-4
and 5-6, Nielsen's prime-13 doubling device) and one by an 89^.
Each half: sixty-three sets built as in sec 3.17.

NEW FINDING -- OBSTRUCTION B: the nine 7^ copies of shape
7^(_,_,x,x,25(x,x,x,_,x),_) each need the same bare-25 piece in
their fifth input.  At residue level, identical pieces repeat the
modulus 7^k*25 across copies (first attempt: 2548 duplicate moduli,
family 5^2*7*{61,67}*...), and every smooth rescaling of the piece
collides with the 25^/5* set families already present.  Owens's
resolution is unstated; the pieces are emitted as placeholders,
documented as the sec-3.18 analogue of obstruction A.

Machine-checked results (after placeholdering the pieces):
  sec3.18: 1141426 congruences, 568 placeholders
  min modulus: 61
  dups within sec3.18: 0
  overlap w/ all previous sections: 0
Census (window 2^7 3^4 5^3 61, 61-half): residual dominated by the
out-of-window 67/89 material and dropped measure 0.399.

Cumulative replica: secs 3.1-3.18, ~1.69M congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).

## 56. Phase 39 (sec 3.19, primes 71/73) (2026-07-22)

emit319.py -- Owens sec 3.19: the remaining single 9^-input in the
last 3-input of the second 5-input on 2 mod 4, reconstructed as the
9-cell (3,9) (figure does not fix the child; documented).  Split mod
8: 71^ on (2,8), 73^ on (6,8) + two depth-shifted 71^ towers
(levels 3-4/5-6, the doubling trick).  Seventy sets per half per the
text.

Collision found & fixed: the six single-input 9^ copies at level 1
(modulus 27*m) exactly repeat the six 3-conjunctions 3*set (27*m) --
1,105,632 duplicate moduli.  Fix: start the 9^ copies at level 2
(Nielsen's artificial depth increase); the sets are 3-free so
27*3^k*m never meets 27*m.  Dups -> 0.

Machine-checked results:
  sec3.19: 6487776 congruences, 498 placeholders
  min modulus: 71
  dups within sec3.19: 0
  overlap w/ all previous sections: 0
Census (window 2^7 3^4 5^2 71): 71-half FULLY covered in-window
(0 of 51120; dropped measure 0.174).

Cumulative replica: secs 3.1-3.19, ~8.18M congruences, all moduli
pairwise distinct across sections.

STATUS: near-miss / frontier-pushed (no T>=43 witness).


# P18 — Erdős #273 (covering system, all moduli p−1, p ≥ 5) — run notes (V1)

Variant V1 (direct search): exact-cover / SAT search for a covering system with
distinct moduli from {p−1 : p prime ≥ 5}, smooth-lcm targets, Selfridge-360 seed
ideas, reusing the P15 finite-cover machinery.

## 0. Statement re-verification (original sources)

* **Erdős–Graham 1980, p.24** (scanned PDF fetched from
  math.ucsd.edu/~fan/ron/papers/80_11_number_theory.pdf; OCR of book page 24):
  covering congruences are defined with `1 < n_1 < ... < n_k` — i.e. **moduli
  pairwise DISTINCT and > 1** — and the question reads: *“Can one choose all
  the n_i to be of the form p − 1 for p prime and at least 5? If p = 3 is
  allowed then Selfridge has given such an example using the divisors of
  360.”* (The page-24 footnote about “no residue class mod 6 could be used”
  annotates Erdős's 1950 system (1) — moduli 2,3,4,8,12,24 — not this
  question; modulus 6 = 7−1 IS admissible here.)
* **erdosproblems.com/273** (fetched via Exa; Cloudflare blocks curl):
  “Is there a covering system all of whose moduli are of the form p−1 for some
  primes p≥5?” Status: OPEN (page last edited 2025-10-01; history shows the
  2025-10-20 revision only added the Selfridge remark). Forum thread: zero
  comments, no claimed partial/complete solutions.
* **Lean formalization** (google-deepmind/formal-conjectures,
  FormalConjectures/ErdosProblems/273.lean): uses `StrictCoveringSystem ℤ`
  where strict = `moduli.Injective` (distinct), `ne_bot`/`ne_top` (modulus
  ≠ 0, ≠ 1), with `∀ i, ∃ p, p.Prime ∧ 5 ≤ p ∧ moduli i = span {p−1}`. The
  CoveringSystem.lean docstring explicitly says strict = the ErGr80 convention.
  Marked `research open`. (The p ≥ 3 variant in the same file is marked
  solved = True, matching Selfridge/360.)

**Operational encoding used here (matches all three sources):** finite list of
congruences a_i mod n_i, n_i pairwise distinct, each n_i + 1 prime and n_i ≥ 4
(p ≥ 5), union of the classes = Z. Repeated moduli NOT allowed.

## 1. Priority check (mandatory widened scope per METHODOLOGY.md)

Searches performed 2026-07-23 (Exa neural search + Zenodo REST API + GitHub):

* erdosproblems.com/273 + history + forum: open, no solutions claimed.
* arXiv/Semantic-Scholar-adjacent: covering-systems literature is about the
  minimum-modulus problem (Hough 2015; Balister–Bollobás–Morris–Sahasrabudhe–
  Tiba 616,000), odd moduli (#111-adjacent, arXiv:2104.00602 etc.), and #204
  (Adenwalla, INTEGERS 26 (2026) #A52, Zenodo 19949505 — resolves the
  pairwise-coprime-overlap question, NOT #273). Nothing on the p−1 moduli
  question itself beyond ErGr80.
* **GitHub artifact repos**: `Sanexxxx777/erdos-computational-bounds`
  (created 2026-07-12, Aleksandr Shulgin): SAT + LRAT certificates proving
  **no covering system of Z with pairwise distinct moduli of the form
  p−1 ≤ 57 (p prime ≥ 5)** — UNSAT at B=50 (pool {4..46}, 13 moduli,
  L=1,275,120) and B=57 (pool + 52, L=16,576,560), certificates checked with
  cake_lpr. README states explicitly that #273 **remains open** — this is a
  lower-bound artifact, not a resolution. (NB: the B≤57 pool has reciprocal
  mass Σ1/n < 1, so nonexistence there also follows from the density bound;
  the certificate is nonetheless a machine-checked confirmation.) Priority
  impact: any positive construction must use some modulus ≥ 58; our searches
  use far larger pools, no conflict.
* **Zenodo**: records on "odd distinct covering systems" (18440762, 18438201,
  18438393 — the odd-moduli problem, not #273); 19949505 = Adenwalla #204
  paper. Nothing resolving #273.
* OpenReview: no hits for covering systems p−1 (searched via Exa).

**Conclusion: #273 is open as of 2026-07-23.** Residual risks: paywalled
journal databases not directly searched (MathSciNet/zbMATH); Russian-language
literature.

## 2. Structure: parity decomposition (drives the search design)

Every admissible modulus n = p−1 (p ≥ 5 odd) is even, so each congruence
covers integers of ONE parity. Substituting x = 2y+1 (odds) and x = 2y
(evens): a witness for #273 exists **iff** the set M = {m ≥ 2 : 2m+1 prime}
contains two DISJOINT subsets, each carrying a distinct-moduli covering
system of Z (m = n/2; p = 2m+1). Lift: b mod m covering the odds ↦
(2b+1) mod 2m; covering the evens ↦ 2b mod 2m.

M = {2, 3, 5, 6, 8, 9, 11, 14, 15, 18, 20, 21, 23, 26, 29, 30, 33, 35, 36,
39, 41, 44, 48, 50, 51, 53, 54, 56, ...}. Only one family can use m=2, so the
other must cover Z with distinct moduli from M \ {2} (min modulus 3). Σ 1/m
diverges over M (primes in AP), so mass is not the obstruction; the
obstruction is combinatorial (which smooth lcm's admissible divisors carry a
cover).

Reciprocal-mass feasibility (feasibility.py, exact fractions): admissible
n-pool mass at smooth targets: N=55440: 1.0437; 720720: 1.1057; 1441440:
1.1235; 2162160: 1.1294; 4324320: 1.1472; 43243200: 1.1872. Each parity
family needs Σ 2/n ≥ 1 over its share, total ≥ 1 + combinatorial excess.
Compare: the B=57 UNSAT pool of the Shulgin artifact had mass < 1 (trivially
infeasible); the interesting regime starts at N ≈ 55440 where mass first
exceeds 1.

## 3. Tooling (this run)

* `feasibility.py` — exact reciprocal-mass scan over smooth lcm targets.
* `finite_cover_p18.py` — adapted from P15 `finite_cover_np.py`: max-gain
  greedy + chronological backtracking + exact Fraction reciprocal prune,
  direct search over Z/N with distinct admissible divisors of N.
* `twophase.py` — parity-decomposed search: phase B covers Z/N_B with
  distinct moduli from (M \ {2}) ∩ divisors(N_B); phase A covers Z/N_A with
  m=2 plus the leftover pool; lifts both to n-space.
* `gen_cnf.py` — SAT encoding (kissat): vars x_{d,a}; sequential (Sinz)
  at-most-one per modulus (distinctness); one coverage clause per residue
  mod N. SAT ⇒ witness (re-verified independently); UNSAT ⇒ negative for
  that pool only.
* `solutions/P18/verify.py` — standalone stdlib verifier, exact integer
  arithmetic only (no floats anywhere): admissibility (n ≥ 4, n+1 prime),
  distinctness, exact coverage of all residues mod lcm via bytearray sieve.

## 4. Compute log / results

(updated as runs complete)

* finite_cover_p18 N=720720 branch=3: **exhausted** (29,524 nodes, <60 s) —
  no cover found in the branch-3 restriction; NOT an exhaustive negative for
  the pool (branch cap prunes residue choices). N=1441440 branch=3: timeout
  (900 s, 179,987 nodes). N=4324320 branch=3: timeout (1200 s).
* twophase greedy/backtracking (branch-capped, NOT exhaustive): phase B
  timeouts at NB=5040 (branch 4, 300 s, 8.3M nodes), NB=27720 (branch 4,
  400 s, 4.3M nodes), NB=360360 (branch 3, 600 s, 302K nodes). The
  min-modulus-3 family (no m=2) is where all the difficulty concentrates.
* phaseB_scan (FULL branching — definitive per pool): no covering of Z/N by
  distinct moduli from (M\{2}) ∩ div(N) for N = 360 (mass 1.189), 720
  (1.210), 1080 (1.224), 1440 (1.224), 2160 (1.245) — exhausted at 3.3K /
  9K / 29K / 29K / 378K nodes. Definitive negatives for those pools.
* SAT (kissat) instances in flight: n-space direct N=55440; joint m-space
  (two disjoint families, m=2 symmetry-broken to family A) N=27720, 55440,
  110880, 166320; single-family phase-B N=2520, 10080, 27720.
* SAT encoding sanity checks (gen_cnf_single.py, no P18 admissibility):
  pool {2,3,4,8,12,24} over Z/24 → SATISFIABLE (Erdős's classical cover);
  pool {3,4,6,12} (mass 5/6 < 1) → UNSATISFIABLE. Encoding validated.
* SAT status after ~3 h wall each (8-core box, oversubscribed): NO verdict
  on ANY P18 instance — not even phase-B N=2520 (24 moduli, 6.5K vars).
  These covering instances appear pigeonhole-hard for CDCL. n-space
  N=55440 and joint m-space N=5040/110880/166320 killed to free cores
  (no verdict); m-space N=27720/55440 and phase-B N=2520/10080/27720 left
  running. CP-SAT (OR-Tools, cpsat_joint.py) on joint m-space N=27720,
  5400 s, 3 workers: status UNKNOWN (no verdict either).
* phaseB_dfs.py (element-branching complete DFS, exact Fraction mass
  prune): N=2520 timeout at 600 s (27.6M nodes, modulus-branching variant);
  N=5040 timeout 5400 s (569M nodes); N=7560 timeout 5400 s (578M nodes).
  Long 10800 s reruns of N=2520 under BOTH complete algorithms: both
  TIMED OUT undecided — element-branching DFS 1.20B nodes, modulus-
  branching scan 368M nodes. The definitive-negative frontier therefore
  stays at pools N ≤ 4320 (mass ≤ 1.259); N=2520 (mass 1.404) undecided.
* phaseB_scan long timeouts (600 s, full branching, NOT decided): N=2520
  (mass 1.404, 27.6M nodes), 5040 (1.429, 18.7M), 15120 (1.473, 14.2M),
  20160 (1.454, 11.0M), 27720 (1.587, 9.7M).

### Stochastic / local-search frontier (phase B, m-space)

Chronology of methods and best uncovered fraction reached (phase B alone;
phase A never attempted because phase B never completed):

* gain-density greedy top-k restarts (stochastic.py/stochastic2.py):
  restarts die at ~19 placements, ~16% uncovered at budget death. The
  exact-Fraction budget prune shows slack (mass − 1) is consumed by
  overlap waste almost immediately under density-greedy move choice.
* **min-waste move rule** (waste_greedy.py) — pick candidate (r mod m, m)
  minimizing 1/m − g/N (g = fresh coverage): dramatic improvement; all
  ~130-220 moduli get placed. Best uncovered: N=2162160 (mass 1.794)
  **2.39%** after 8.9K restarts; N=17297280 (mass 1.836, has 2-chain
  {8,128}) 2.32%; N=19958400 (3-chain {3,9,81}) 2.52%; N=10810800 (mass
  1.852) 2.40%. The wall is remarkably flat ~2.3–2.5% across pool
  structures and sizes.
* beam search over min-waste moves (beam.py, width 80): 3.95% — worse
  than randomized restarts (beam diversity collapses).
* ruin-and-recreate LNS (repair.py): 4.2% — acceptance design too weak.
* **simulated annealing over full assignments** (anneal.py; move = shift
  one congruence to a new residue, 70% repair-targeted, Metropolis,
  geometric cooling with reheats; incremental cov[] bookkeeping): breaks
  the greedy wall: N=2162160 best E = 14,335 uncovered = **0.663%**
  (T0=20, alpha=0.99995, ~1.3M moves); plateaued there for 20+ min of
  reheats. N=17297280 run reached 0.83% and was still improving slowly.
* Interpretation (not a proof): every method hits a hard floor well above
  zero. Combined with the definitive small-pool negatives and the extreme
  thinness of prime-power chains in M (2-powers only {2,8,128,32768,...} =
  Fermat-prime exponents; 3-powers {3,9,81,243,...} with gaps), phase B
  (covering with distinct moduli from M \ {2}) looks structurally very
  hard, and possibly impossible — which would make the #273 answer "no",
  since in any two-family split one family must avoid m=2. No obstruction
  argument found yet; uncovered residues at greedy death show no clean
  congruence-class pattern (checked mod 2,3,4,8,16,5,7,9,11,13).
* Final annealing figures at session end: N=21621600 (mass 1.874, the
  richest pool ≤ 3·10^7): best **0.402%** uncovered (86,860 residues,
  2.2 h); N=17297280: 0.757%; N=2162160: 0.663% (plateaued > 1 h).

## 5b. Second push (session resumed on instruction to "keep going")

Re-ran the priority check: erdosproblems.com/273 now explicitly notes
"Selfridge has found an example using divisors of 360 if p=3 is allowed",
and the DeepMind Lean file marks the p>=3 variant `research solved`
(answer True) while p>=5 (#273 proper) stays `research open`. The p=3
variant is easy in our parity decomposition: n=2 (p=3) covers a whole
parity class by itself, so only ONE genuine cover is needed. For p>=5
both parity families must be genuine covers — the problem "doubles".

Mass accounting for the joint problem: both families need reciprocal
mass >= 1 plus waste; Mirsky–Newman rules out zero waste for distinct
moduli. Total waste budget = (pool mass + 1/2) − 2. Divisor pools max
out around mass 1.89–1.94 for array-reachable N (best found:
N=183783600 = 2^4·3^3·5^2·7·11·13·17, mass 1.9412, 348 moduli; searched
compositions over primes ≤ 43 up to N ≤ 2.5·10^8), so TOTAL waste
budget ≤ ~0.44 for both families combined. Best achieved phase-B waste
alone: ~0.87. Gap ≈ 2x in waste terms.

Anneal floor scaling (phase B, best uncovered count/fraction):
N=2520: 96 (3.8%); 5040: 158 (3.1%); 27720: 744 (2.7%); 55440: 1259
(2.3%); 2162160: 14,335 (0.663%); 21621600: 86,860 (0.402%);
49729680 (mass 1.89) and 183783600 (mass 1.94) runs: see logs
(~0.7–0.6% mid-run, still improving when stopped).

Multi-stage (Krukenberg-style) architecture explored (stage2.py): fix a
stage-1 near-cover over Z/N0, then cover the hole fibers over Z/(N0·Q)
with fresh moduli m = d·q (d | N0, q | Q, gcd(Q,N0)=1, 2dq+1 prime) —
tracking only the |H|·Q hole universe (sparse levels, unbounded lcm).
Exact CAPACITY accounting (max coverable measure of the hole universe by
the whole stage-2 pool) kills this for our hole counts:
N0=27720, |H|=744: Q=13·17·19 ratio 0.831 (<1 ⇒ provably impossible);
Q=13·17·19·23 ratio 1.094 (universe 72M, thinner than any pool we ever
closed); adding 29 → ratio 1.25 but universe 2.1B (out of reach). The
d-supply per q (#{d | N0 : 2dq+1 prime} ≈ 0.1·τ(N0)) is the binding
constraint; per-hole fiber covers need ≥ q_min moduli per hole from a
supply of ~15 shared across ALL holes. Conclusion: staged hole-closing
becomes viable only if stage 1 leaves ≤ ~5–10 holes, i.e. ~100x better
than the annealing floor — or with τ(N0) in the thousands (N0 ≥ 7·10^8,
past array reach; would need a fundamentally sparser representation).

## 5c. Cap-bound frontier extension (new definitive results)

The published computational frontier (Shulgin's LRAT certificate) is
"no covering with all moduli p−1 ≤ 50". We noticed every cap B < 70 is
DENSITY-TRIVIAL: the exact reciprocal sum of the full admissible pool
{n : 4 ≤ n ≤ B, n+1 prime} is < 1, so no covering exists regardless of
residue choices (no SAT needed). Verified exactly (cap_dfs.py, Fraction
arithmetic): B = 66 pool mass = 160107799/160240080 ≈ 0.999174 < 1.
⇒ **Definitive: no #273 covering with all moduli ≤ 66.** (Extends the
published 50 → 66 by a one-line exact computation.)

B = 70 is the first density-nontrivial cap (mass 1.0135, L =
480,720,240). cap_dfs.py started a complete element-branching DFS over
Z/L (bool array, exact Fraction mass prune), but a far stronger and
purely exact argument superseded it:

**Projection lemma** (cap_project.py). If a prime p has at most p−1
multiples in the pool, pick c_p mod p avoiding the mod-p class of each
such multiple; CRT the c_p's over a set S of such primes (iterated to
a fixpoint, recomputing multiplicity counts on the surviving pool).
The progression {x ≡ c mod Πp} is untouched by all removed moduli and
is ≅ Z, with every surviving modulus (coprime to all p ∈ S) inducing
the SAME modulus on it. Hence a cap-B covering exists only if the
residual (smooth) pool covers Z; residual mass < 1 ⇒ impossible.
(Distinctness not even needed. Exact Fraction arithmetic throughout.)

Result: the iterated projection kills **every cap B ≤ 255**
(residual mass < 1 for all of them). This extends the published
computational frontier from 50 to 255 with a few milliseconds of exact
arithmetic. First survivor: B = 256, residual pool = 28
{2,3,5,7}-smooth moduli {4,6,10,12,16,18,28,30,36,40,42,60,70,72,96,
100,108,112,126,150,162,180,192,196,210,240,250,256}, L = 127,008,000,
residual mass 127085857/127008000 ≈ 1.000613 — waste budget only
6.1·10⁻⁴, decided by complete DFS (cap_project.py, exact prune):
see run_cap256.log.

## 5. Final status

**NO verified result.** Erdős #273 remains open in both directions here.

* No witness: best-ever assignment leaves 0.40% of Z/N uncovered
  (phase B, N=21621600); no phase-A attempt ever started.
* No new definitive negative beyond pools of mass ≤ 1.259 (N ≤ 4320):
  N=360/720/1080/1440/2160/3600/4320 pools exhausted (no phase-B cover,
  hence no two-family cover with both lcms dividing 2N for those N).
* SAT gave zero verdicts after ~6 h/instance (kissat, 5 instances,
  including one with only 6.5K vars) — these covering instances behave
  like counting-hard (pigeonhole-like) formulas for CDCL. CP-SAT: UNKNOWN.
* Future work: (a) DRAT/LRAT-certified UNSAT for the N=2520 phase-B pool
  (needs days of CPU or a counting-aware solver / pseudo-Boolean or
  symmetry-breaking-by-orbit encoding); (b) extend Shulgin's cap-based
  bound past p−1 ≤ 57 with his encoding; (c) theory: obstruction for
  covering with distinct moduli from M \ {2} (thin prime-power chains:
  2-powers in M are Fermat-prime exponents {2,8,128,32768}, 3-powers
  {3,9,81,243}); a proof would answer #273 negatively.

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

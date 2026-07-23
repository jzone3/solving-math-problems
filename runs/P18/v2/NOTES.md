# P18 — Erdős #273 — run v2 (SAT encoding over Z/L + obstructions + Lean fidelity)

Session: solve run v2, branch `runs/P18-v2`. Date: 2026-07-23.

## 1. Statement re-verification (primary sources)

- **erdosproblems.com/273** (viewed 2026-07-23, page last edited 2025-10-01, status **OPEN**,
  0 claimed proofs): "Is there a covering system all of whose moduli are of the form p−1 for
  some primes p ≥ 5?" Remark: "Selfridge has found an example using divisors of 360 if p = 3
  is allowed." Source cited: [ErGr80, p.24].
- **Erdős–Graham 1980, p.24** (OCR of the UCSD scan `math.ucsd.edu/~ronspubs/80_11_number_theory.pdf`,
  printed page 24 = PDF page 20): defines "a family of residue classes aᵢ (mod nᵢ) with
  **1 < n₁ < … < n_k**" as a system of covering congruences — i.e. **moduli distinct and all > 1** —
  and asks: "Can one choose all the nᵢ to be of the form p − 1 for p prime and at least 5? If
  p = 3 is allowed then Selfridge has given such an example using the divisors of 360."
- **Convention settled:** distinct moduli, every modulus > 1, finite system. This is what all
  encodings below use.

## 2. Lean formalization fidelity check (DeepMind Formal Conjectures)

File: `FormalConjectures/ErdosProblems/273.lean` (github.com/google-deepmind/formal-conjectures,
main @ 2026-07-23), definition in `FormalConjecturesForMathlib/NumberTheory/CoveringSystem.lean`.

- `CoveringSystem R`: finite index type; cosets `residue i + moduli i` (ideals) cover `Set.univ`;
  `ne_bot` (ideal ≠ 0 ⇔ modulus finite/nonzero) and `ne_top` (ideal ≠ ℤ ⇔ modulus ≠ 1). Matches
  "finite, every modulus > 1".
- `StrictCoveringSystem` adds `injective_moduli` — in ℤ ideals are `(n)` with n ≥ 0 determined
  by |n|, so injectivity = pairwise distinct moduli. Matches ErGr80's `1 < n₁ < … < n_k`.
  The docstring itself cites ErGr80.
- `erdos_273 : answer(sorry) ↔ ∃ c : StrictCoveringSystem ℤ, ∀ i, ∃ p, p.Prime ∧ 5 ≤ p ∧
  c.moduli i = Ideal.span {↑(p-1)}` — faithful to the source statement. `↑(p-1)` uses ℕ
  subtraction, harmless since p ≥ 5.
- Minor observations (logged, not blockers): the solved p ≥ 3 variant
  `erdos_273.variants.three` is stated over **ℕ** (not ℤ) — a covering of ℕ by residue classes;
  for periodic congruence systems covering ℕ ⇔ covering ℤ, so content is equivalent, but the
  inconsistency of ambient ring between the two statements is a (cosmetic) fidelity remark.
  Its `answer(True)` is justified by Selfridge's divisors-of-360 example (re-verified below,
  §5 sanity check).

**Verdict: the Lean statement is faithful.** Operational encoding used here (distinct moduli
m = p−1, p prime ≥ 5, finite, covering all of ℤ) agrees with both the original source and the
Lean statement.

## 3. Priority check (mandatory, incl. artifact repos)

Searches performed 2026-07-23:

- **erdosproblems.com/273**: OPEN; 0 claimed proofs; 1 forum comment (see below).
- **Web/arXiv/Semantic-Scholar-style searches**: "Erdős problem 273 covering system moduli p-1",
  "covering system all moduli of form p-1 primes". No resolution found. Related active work:
  - Adenwalla, *A Question of Erdős and Graham on Covering Systems*, INTEGERS 26 (2026) #A52
    (Zenodo DOI 10.5281/zenodo.19949505) — resolves **#204** (CD covering n does not exist),
    NOT #273. Downloaded and checked: only #204.
  - Hough–Nielsen (Duke 2019): every distinct covering system has a modulus divisible by 2 or 3
    (does not obstruct #273: all moduli p−1 here are even).
  - Balister–Bollobás–Morris–Sahasrabudhe–Tiba (arXiv:1811.03547) distortion sieve;
    Filaseta–Kalogirou (arXiv:2407.15280) budget bounds; Krukenberg-type min-modulus results
    (arXiv:2508.18062); 2/3/5-smooth covering classification (arXiv:2605.18644). All partial /
    adjacent, none touch existence for the {p−1, p ≥ 5} pool.
- **GitHub artifact-repo search** (per the P07-scoop lesson):
  1. `idealombrer/erdos-273-covering-pm1` (linked from the erdosproblems forum comment,
     posted by user ideal_ombrer): paper + scripts + certificates claiming
     **Theorem A**: any #273 covering must contain a modulus p−1 with p > 877 (the 149 moduli
     with 5 ≤ p ≤ 877 cannot cover ℤ; BBMST sieve, exact rationals, η(U_877)=0.99991772<1);
     **Theorem B**: Σ1/(p−1) ≥ 1 + exp(−3.36×10²¹) for any such covering; sieve-certified
     non-covering for all moduli dividing L ∈ {55440, 110880, 166320(parity), 720720};
     a Lean-verified parity reduction. Repo states **status OPEN, "probably YES"**.
     → NOT a resolution; partial results only. Their two headline certificates were
     **independently re-run in this session** (bit-identical verdicts):
     `theoremA_certify_exact.py` → η(U_877)=0.99991772 < 1 CERTIFIED;
     `unsat_lemmas_sieve.py` → all six instances η<1 (see `/tmp` logs; verdicts copied §5).
  2. `Sanexxxx777/erdos-computational-bounds`: SAT + LRAT (cake_lpr-checked) UNSAT certificate:
     no covering with distinct moduli of the form p−1 ≤ 50 (pool lcm L=1,275,120).
     Explicitly "machine-checked partial bounds, not solutions".
- **Zenodo**: only the #204 Adenwalla record above. **OpenReview**: nothing relevant found for
  "Erdős 273"/"covering system p-1".
- **DeepMind formal-conjectures issue #465**: statement formalization only, category
  `research open`.

**Conclusion: #273 is open as of 2026-07-23. No scoop.** Residual risks: paywalled journals not
searched exhaustively; the idealombrer PAPER_273 is a self-published artifact (its Theorem A
certificate reproduced here, but the sieve's mathematical correctness rests on BBMST which we
did not re-derive).

## 4. Encodings

### 4.1 SAT set-cover over Z/L (`sat_cover.py`)

For a covering whose moduli all divide L (equivalently: any covering whose lcm divides L):
- pool(L) = {m : m | L, m > 1, m+1 prime ≥ 5};
- var y[m][a] ⇔ congruence a (mod m) selected; at-most-one residue per modulus
  (sequential-counter AMO — pairwise AMO OOMs at m ≈ 5·10⁴: first attempt was OOM-killed
  at 32 GB, logged as a dead end);
- coverage clause ∨_m y[m][x mod m] for every x ∈ Z/L;
- sound translation symmetry breaking: residue of modulus 4 fixed to 0 (deleting y[4][a], a≠0:
  any covering using 4 translates to one with a₄=0; coverings not using 4 unaffected);
  residual translations are multiples of 4, whose action mod 6 has orbit representatives {0,1},
  so y[6][a] restricted to a ∈ {0,1}.
- Encoding sanity check (`sanity_p3.py`): with pool relaxed to p ≥ 3 over L=360 the CNF is SAT
  and the extracted witness is a valid 12-congruence Selfridge-type covering
  (independently re-verified in pure integers): PASS.

### 4.2 Exact density prefilter (`pool_density.py`)

Fraction-exact Σ1/m over pool(L); Σ<1 trivially forbids a covering with moduli | L.
L=360 (p≥5 pool): Σ = 7/9 < 1 ⇒ trivially impossible. All larger candidate L pass the
density test (Σ up to ≈1.18 for L=21621600), so SAT is needed there.

### 4.3 Verifier (`verify.py`)

Standalone exact acceptor (no floats on any path): reads `a m` lines; checks m>1, m+1 prime ≥ 5
(deterministic trial division), moduli pairwise distinct, and full coverage of Z/lcm.
Prints PASS only on a genuine witness. Unit-tested on the p≥3 Selfridge witness
(correctly rejected: modulus 2) and on primality edge cases (877 prime, 878 not, 881 prime).

## 5. Compute log & results

Machine: 8-core, 32 GB RAM (Devin box). Solvers: CaDiCaL 1.5.3 (pysat), OR-Tools CP-SAT 9.x,
kissat 4.0.4 (built from source, DRAT proof logging), drat-trim (built, for proof checking).

| instance | engine | encoding size | outcome |
|---|---|---|---|
| L=360 (p≥5 pool) | exact density | Σ1/m = 7/9 | **UNSAT trivially** (density < 1) |
| L=360 (p≥3 pool, sanity) | CaDiCaL | 838 vars | **SAT < 0.1s**, witness re-verified (12 congruences) |
| L=55440 | CaDiCaL (pysat) | 106,313 vars / 374,207 clauses | no verdict after ~55 min (killed; superseded by kissat) |
| L=55440 | kissat 4.0.4 + DRAT | same CNF (DIMACS) | **timeout at 14,000 s (3.9 h)**, no verdict; partial DRAT grew to 49 GB (discarded) |
| L=55440 | CP-SAT, 5 workers | AddAtMostOne + BoolOr model | **timeout at 11,800 s (3.3 h)**, status UNKNOWN |
| L=166320 | kissat 4.0.4 (no proof logging, disk budget) | 383,639 vars / 741,635 clauses | **timeout at 12,000 s (3.3 h)**, no verdict |
| first pairwise-AMO attempt | CaDiCaL | AMO on m≈5·10⁴ → 10⁹ clauses | **OOM-killed at 32 GB** (dead end; fixed with seqcounter AMO) |

These instances are exactly the family on which the idealombrer repo reports "SAT solvers only
time out" — their exact-rational sieve certificates (reproduced here, `external-repro/`) already
prove non-covering for L ∈ {55440, 110880, 166320, 720720}; our SAT runs are an *independent*
confirmation attempt with a checkable DRAT artifact, budget-capped at ~4 h each.

Bonus: the p≥3 sanity run yields a machine-verified witness for the Lean
`erdos_273.variants.three` (`answer(True)`, currently marked "TODO: find reference"):
(0 mod 2), (1 mod 4), (1 mod 6), (7 mod 10), (3 mod 12), (11 mod 18), (11 mod 30),
(23 mod 36), (3 mod 40), (35 mod 60), (71 mod 72), (179 mod 180) — distinct moduli, all p−1
with p prime ≥ 3, covers ℤ (verified exhaustively mod 360).

## 6. Obstruction / nonexistence heuristics

See OBSTRUCTIONS.md (parity reduction re-derived; Mirsky–Newman forced overlap; density
prefilters; external Theorem A/B partial bounds with reproduced certificates).

## 7. Round 2 (same session, resumed): independent distortion sieve + strengthened encodings

Direction (a) from §8 of round 1 was executed: `bbmst_independent.py` is a from-first-principles
implementation of the BBMST distortion sieve (Balister–Bollobás–Morris–Sahasrabudhe–Tiba,
arXiv:1811.03547), written directly from the statements of **Theorem 3.1** (η < 1 ⇒ no covering)
and **Theorem 3.2** (computable moment bounds M_i^(1) ≤ Σ_{d=m·p_i^j∈N_i} p_i^{-j}ν(m)/m and
M_i^(2) ≤ Σ_{pairs in N_i} p_i^{-(j1+j2)}ν(lcm(m1,m2))/lcm(m1,m2)), NOT ported from the
idealombrer code. Soundness for pools: every η-term is a monotone sum over (pairs of) pool
moduli, so η(pool) < 1 excludes every distinct-moduli subcollection with arbitrary residues.
Accept path is exact `Fraction` arithmetic; floats only steer the δ-search (coordinate descent,
δ snapped to k/5040 before exact certification).

### 7.1 Independently certified negative results (exact rationals)

| pool | \|pool\| | Σ1/m | exact η | verdict |
|---|---|---|---|---|
| m \| 55440 | 43 | 1.0437 | 185060815/221875038 ≈ 0.83408 | **no covering** |
| m \| 166320 | 58 | 1.0666 | ≈ 0.87598 | **no covering** |
| m \| 720720 | 79 | 1.1057 | ≈ 0.87262 | **no covering** |
| m \| 1441440 | 96 | 1.1235 | ≈ 0.90028 | **no covering** |
| m \| 2162160 | 107 | 1.1294 | ≈ 0.91652 | **no covering** |
| m \| 4324320 | 132 | 1.1472 | ≈ 0.94594 | **no covering** |
| m \| 8648640 | 149 | 1.1575 | ≈ 0.96199 | **no covering** |
| m \| 12252240 | 146 | 1.1470 | ≈ 0.89764 | **no covering** |
| m \| 36756720 | 200 | 1.1728 | ≈ 0.94639 | **no covering** |
| m \| 61261200 | 212 | 1.1763 | ≈ 0.95891 | **no covering** |
| m \| 73513440 | 243 | 1.1909 | ≈ 0.97699 | **no covering** |
| m \| 122522400 | 257 | 1.1944 | ≈ 0.98912 | **no covering** |
| m \| 232792560 = lcm(1..22) | 250 | 1.1716 | ≈ 0.91180 | **no covering** |
| m \| 465585120 | 304 | 1.1904 | ≈ 0.94221 | **no covering** |
| m \| 698377680 | 348 | 1.1986 | ≈ 0.96264 | **no covering** |
| m \| 5354228880 = lcm(1..23) | 395 | 1.2058 | ≈ 0.93326 | **no covering** |
| m \| 26771144400 = lcm(1..25) | 483 | — | ≈ 0.99928 | **no covering** |
| {p−1 : 5 ≤ p ≤ 877} | 149 | 1.4530 | ≈ 0.9999091 | **no covering** (Theorem A re-derived) |

(pool always = {m : m+1 prime ≥ 5} within the stated divisor set; logs:
`sieve_independent.log`, `sieve_bigL.log`, `sieve_bigL2.log`.)

Notable: the external artifact repo's certificates stopped at L ≤ 720720; the rows with
L ∈ {1441440, …, 232792560} are **new period exclusions produced this session** (sound by
Theorems 3.1+3.2; exact-rational certification of η < 1). The p ≤ 877 row independently
re-derives the artifact repo's Theorem A — this supplies the "second independent verifier"
the methodology asks for. η(p ≤ 877) ≈ 0.9999091 is razor-thin; p ≤ 881 gives η ≈ 1.0015 and
did not certify even with multi-start δ optimization (consistent with 877 being the method's
saturation point for this pool family). L=21621600 (η ≈ 1.0075) and L=2327925600 (η ≈ 1.0061) fail to certify while
their multiples/relatives 36756720, 73513440 and 5354228880 certify — the min(M1, M2/4δ(1−δ)) trade-off is not monotone in L.

### 7.2 Strengthened SAT/CP-SAT encodings (round 2)

Provably sound additions (union-bound density: any covering's used moduli satisfy Σ 1/m ≥ 1;
pool slack = Σ_pool 1/m − 1 = 269/6160 for L=55440):
- `sat_cover2.py`: used-modulus indicators u_m; **forced-use unit clauses** for every m with
  1/m > slack (forces 4, 6, 10, 12, 16, 18, 22); **pair clauses** (u_m1 ∨ u_m2) when
  1/m1 + 1/m2 > slack; same symmetry breaking. 212,625 vars / 480,592 clauses.
- `sat_parity.py`: parity-reduced formulation over H = L/2 (all pool moduli even ⇒ a covering
  splits into two disjoint-subpool coverings of Z/H with moduli m/2); swap-symmetry broken via
  modulus 4 pinned to class 0, residue 0. Same forced-use/pair clauses.
- `cpsat_cover2.py`: single exact linear density cut Σ u_m·(L/m) ≥ L added to the CP-SAT model.

Outcome: kissat 4.0.4 on both round-2 CNFs and CP-SAT with the density cut were still running
at ~5.5 h budgets without a verdict when the sieve certifications above mathematically settled
L = 55440 (and far beyond), so the SAT runs are logged as engine-limitation data points, not
results (`kissat2_55440.log`, `kissat_parity_55440.log`, `cpsat2_55440.log`).

## 8. Round 3 (same session, resumed again): positive-direction attempts + frontier map

- **Witness search on undecided periods** (`greedy_cover.py`): randomized greedy max-coverage +
  patching on L=21621600 (the richest sieve-undecided pool) leaves ≥ 8.8% uncovered — far from
  a cover; consistent with P18-v1's independent findings (their annealer's hard floor at the
  same period was 0.402% uncovered after 2.2 h; all their methods plateau well above zero).
- **Frame constructions are structurally blocked** for p ≥ 5 (OBSTRUCTIONS.md §O6): the known
  flexible covering family (Morris et al., arXiv:1904.04806) needs modulus 2 = 3−1 at its first
  layer; any p ≥ 5 witness must deviate from the tree/frame shape at layer 1.
- **Sieve frontier map** (`scan_undecided.py`, float-only δ-optimized η over 219 smooth pools
  with density ≥ 1, L < 3·10^8): 207 EXCLUDED, only 12 UNDECIDED —
  L ∈ {19958400, 21621600, 32432400, 33264000, 43243200, 49896000, 64864800, 86486400,
  99792000, 108108000, 144144000, 162162000} (all with high powers of 2/3 and 5²; η between
  1.0002 and 1.034). Any covering whose lcm is ≤3·10^8-smooth of the scanned shapes must have
  its lcm-divisor pool among these. Heavy-restart exact certification attempts on the
  borderline cases (32432400 η≈1.00020, 33264000, 144144000, 21621600 with 40 restarts) all
  stay ≥ 1 — genuine saturation of the Thm 3.2 bound, not an optimizer artifact
  (`sieve_borderline.log`, `sieve_21621600_hard.log`).
- Round-2's kissat/CP-SAT reruns were killed by two infrastructure restarts before their
  budgets elapsed (logs empty; no verdict either way — consistent with all previous attempts).
- Cross-check with sibling run P18-v1 (branch `runs/P18-v1`): they proved definitive
  small-pool negatives (phase-B pools N ≤ 4320), hit the same CDCL wall (no verdict even at
  N=2520), and their stochastic frontier stalls at 0.4–0.7% uncovered. Both directions remain
  blocked by fundamentally new mathematics, not compute.

## 9. Bottom line of run v2

- **The problem itself (Erdős #273) remains OPEN in both directions** — no p≥5 covering
  witness found, and no full impossibility proof exists.
- **New verified partial results (round 2, exact-rational certificates):** no covering system
  with distinct p−1 moduli (p ≥ 5) has all moduli dividing any of
  L ∈ {55440, 166320, 720720, 1441440, 2162160, 4324320, 8648640, 12252240, 36756720,
  61261200, 73513440, 122522400, 232792560 = lcm(1..22), 465585120, 698377680,
  5354228880 = lcm(1..23), 26771144400 = lcm(1..25)} — extending the known excluded
  periods (previously ≤ 720720) by over four orders of magnitude — and the p > 877 lower bound
  (Theorem A) was independently re-derived from first principles, satisfying the methodology's
  second-verifier requirement.
- Verified deliverables of this run: statement/convention re-verification against ErGr80 p.24
  (distinct moduli > 1); Lean formal-conjectures fidelity check (faithful); a widened priority
  check (still open; two artifact repos with partial results found and logged, one reproduced
  bit-identically); an exact standalone verifier (`verify.py`, integer-only accept path); a
  validated SAT encoding (sanity-SAT on the p≥3 pool with machine-verified Selfridge-type
  witness); exact density prefilters; and negative compute results: CDCL/CP-SAT cannot decide
  L ∈ {55440, 166320} within ~4 h budgets (consistent with the artifact repo's report), while
  the reproduced exact-rational sieve certificates already settle those periods as non-covering.
- Most promising directions for future runs: (a) independent from-first-principles
  implementation of the BBMST distortion sieve to *independently* certify the L-period lemmas
  and Theorem A; (b) structured constructions on periods with several primes p > 877 (tree/frame
  methods), guided by the parity reduction; (c) formalizing the p≥3 witness for the Lean
  `variants.three` TODO.

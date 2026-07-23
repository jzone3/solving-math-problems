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

## 7. Bottom line of run v2

- **No new verified mathematical result.** Erdős #273 remains OPEN in both directions.
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

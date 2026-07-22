# P15 V3 — SAT layered attack on min-modulus covering systems

Session: https://app.devin.ai/sessions/0ad9a586fd2a4844851a6a7b4d2a20a6
Variant: V3 (SAT encoding, layered over prime factorization, incremental escalation)

## Statement re-verification (2026-07-22)
- Owens, "A Covering System with Minimum Modulus 42", BYU MSc thesis 2014
  (scholarsarchive.byu.edu/etd/4329) — confirmed: record 42, distinct moduli.
- Nielsen, "A covering system whose smallest modulus is 40" — confirmed; NOTE: Nielsen's
  min-mod-40 system has MORE THAN 10^50 congruences (recursive tree construction). The
  problem file's guess of 10^3–10^6 congruences for a 43-witness is almost certainly a
  large underestimate.
- Hough (Annals 2015): min modulus ≤ 10^16; BBMST 2022: ≤ 616,000. Literature search
  (Exa, 2026-07) found no construction beating 42. Problem confirmed open.

## Encoding
Fix a smooth lcm candidate N. Variables x[n][a] for each divisor n ≥ m of N (n > 1) and
residue a mod n. Constraints:
1. At-most-one residue per modulus (distinct moduli ⇒ each modulus used ≤ once).
2. Coverage: for every t in Z_N, OR over divisors n ≥ m of x[n][t mod n].
Symmetry breaking: translation symmetry of Z_N — smallest divisor d1 ≥ m, if used, is
forced to residue 0.
Necessary feasibility screen: Σ_{n|N, n≥m} 1/n ≥ 1 (each class covers density 1/n).

## Key literature calibration (found mid-session, crucial)
- Dalton–Trifonov, "Extreme Covering Systems", J. Integer Seq. 25 (2022): minimal lcm
  L(m=3)=120, L(m=4)=360 (proved optimal).
- Klein, arXiv:2508.18062 (Aug 2025): L(m=5)=1440, L(m=6)=5040 proved optimal
  (Krukenberg's constructions); L(m=7)=15120 conjectured optimal. Max modulus for m=5
  is ≥108. Historical m records: Swift 4/6, Churchhouse 9, Krukenberg 18, Choi 20,
  Morikawa 24, Gibson 25, Nielsen 40 (recursive, >10^50 congruences), Owens 42.
- Consequence: my early SAT targets m=5 with N ∈ {360, 720} were provably UNSAT
  (N < 1440 or wrong divisor structure) — explains hours of kissat grinding without
  answers. UNSAT proofs of these set-cover instances appear exponentially hard for CDCL.

## Tooling log
- cover_sat.py / cover_kissat.py: direct full-N encoding. pysat Glucose4/Cadical too weak;
  kissat 4.0.4 (built from source) solves m=4/N=2520 in 14 s (45 congruences, verified).
- GOTCHA: pysat's C-level solve holds the GIL — threading.Timer-based timeouts never fire.
  Replaced with conflict-budget chunks (cover_sat.py) / kissat --time (subprocess).
- AMO encoding bug caught by verifier: sequential-counter final clause used s[-2] instead
  of s[-1], silently allowing two residues on one modulus. Machine verification caught it
  (methodology rule 4 vindicated). Fixed; layered.py results before the fix discarded.
- layered.py: per-prime-power-layer MaxSAT (holes-only clauses) — works but pysat RC2 /
  anytime linear search too slow >~3k holes; greedy layer variant loses hole alignment
  (locally optimal hole counts pick unliftable hole sets — m=3 test failed at final layer).
- layered2.py: hybrid — interior layers MaxSAT (small) or greedy (large), FINAL WINDOW of
  ladder factors solved jointly and exactly with kissat over the lifted holes. Reproduces
  m=3 (lcm 120, 14 congr) and m=4 (lcm 2520, 45 congr) instantly; both verify PASS.

## Run log
- SAT+verified: m=3 N=120 (14 congr), m=4 N=2520 (45 congr, kissat 14s), layered2 m=4.
- TIMEOUT (≥900s, now known misguided): m=5 N∈{360,720,2520} direct; layered2 m=5
  final at N=2520 (provably requires lcm ≥1440 with different structure).
- Running: kissat direct on literature-calibrated targets:
  (m=5,N=1440) (m=6,N=5040) (m=7,N=15120) (m=8,N=30240) (m=9,N=55440) (m=10,N=110880).

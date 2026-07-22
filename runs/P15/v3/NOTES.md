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

## Log
(appended as runs complete)

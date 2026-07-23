# P18 / Erdős #273 — nonexistence obstructions & heuristics (run v2)

Statement: does a finite covering system of ℤ with distinct moduli, all of the form p−1
(p prime ≥ 5), exist? All observations below are elementary and self-contained unless cited.

## O1. No global density obstruction

A covering needs Σ 1/mᵢ ≥ 1. Over the whole pool {p−1 : p ≥ 5} the series Σ 1/(p−1)
diverges (comparison with Σ 1/p), so density never rules out the problem globally — only
per-period pools (see `pool_density.py`: e.g. the divisors-of-360 pool sums to 7/9 < 1,
so Selfridge's 360 trick cannot survive the removal of modulus 2).

## O2. Parity reduction (all moduli are even)

Every pool modulus is even (p ≥ 5 odd ⇒ p−1 even). A congruence a (mod m) with m even only
meets integers of parity a mod 2. Hence a covering splits into a sub-family covering the even
integers and one covering the odd integers, and via x = 2y + r these become two coverings of ℤ
with moduli {(p−1)/2}, which must use **disjoint** modulus sets (distinctness upstairs).
Consequences:
- the effective budget must be ≥ 2 in the halved pool, i.e. Σ 1/(p−1) ≥ 1 over each parity class
  separately — this is why near-critical pools (density barely above 1) cannot work: the pool
  restricted to either parity class alone must already carry density ≥ 1/2 ... precisely,
  Σ_{covering} 1/m = Σ_even-part 1/m + Σ_odd-part 1/m with each part ≥ 1/2 (each part covers a
  set of density 1/2 in ℤ).
  (This matches the parity reduction in the idealombrer artifact repo, which is Lean-verified
  there; re-derived independently here.)

## O3. Overlap is forced (Mirsky–Newman)

By Mirsky–Newman / Davenport–Rado (Erdős's favorite proof via generating functions), an *exact*
(disjoint) covering with distinct moduli > 1 does not exist. So any #273 covering has
Σ 1/mᵢ > 1 strictly, with overlap; combined with near-critical pool densities for smooth L
(1.04–1.18, §pool_density) the required "overlap tax" quickly exceeds the available budget on
small periods — quantified exactly by the SAT/CP-SAT UNSAT results in NOTES.md §5.

## O4. Known partial structural bounds (external, artifact repo, reproduced)

- Theorem A (idealombrer, BBMST sieve, exact-rational certificate **reproduced this session**):
  every #273 covering uses a modulus p−1 with p > 877. Hence any SAT search over a period L
  whose pool only contains p ≤ 877 is doomed; conversely periods containing large-p moduli have
  L too large for exhaustive residue-level SAT (coverage clauses = L). This is the fundamental
  compute barrier for the positive direction.
- Theorem B (idealombrer, via Filaseta–Kalogirou arXiv:2407.15280): Σ 1/(p−1) ≥ 1 + exp(−3.36·10²¹)
  for any #273 covering. Not reproduced from first principles here (depends on FK's theorem);
  logged as external.

## O5. Why "probably YES" (heuristic, informal)

Σ 1/(p−1) over usable moduli diverges; Selfridge's p ≥ 3 example shows the mechanism works when
one density-1/2 modulus is available; the p ≥ 5 pool has plenty of aggregate density, only the
*small* moduli are scarce (4, 6, 10, 12, 16, 18, 22, 28, ... sum slowly). The obstruction is
combinatorial (integrality/overlap on smooth periods), not density. A construction, if it
exists, likely lives on a period with several large primes p > 877 — beyond residue-level
exhaustive search; a structured (tree/frame-based, à la BBMST constructions) approach is the
plausible route. Left open in this run.

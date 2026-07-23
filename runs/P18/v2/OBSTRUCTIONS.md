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

## O6. Frame constructions are structurally blocked at level 1 (round 3)

The flexible "frame" family behind the known lower-bound constructions (Morris et al.,
arXiv:1904.04806 §1/§5: progressions a·Q_{i−1} (mod m) with p_i | m | Q_i covering the classes
a·Q_{i−1} + Q_i·Z level by level, closed by 0 (mod Q_r)) cannot produce a p ≥ 5 witness
directly: the first layer must cover q_1 − 1 nonzero classes with distinct moduli dividing q_1
(a prime), so q_1 = 2 and the only available modulus is 2 = 3 − 1 — inadmissible for p ≥ 5.
Equivalently (parity reduction): one of the two halved subsystems must cover Z with distinct
moduli from M \ {2} = {3, 5, 6, 8, 9, 11, 14, ...} (2m+1 prime), i.e. with minimum modulus 3 and
no density-1/2 congruence. Any positive construction must therefore deviate from the greedy
tree/frame shape at the very first layer — covering the m=2-side classes with several deferred
congruences instead of one. This is where P18-v1's phase-B searches also localized all the
difficulty (their exhaustive per-pool scans failed for all N tried).

## O7. Sieve frontier map (round 3)

`scan_undecided.py` (float-only δ-optimized η over smooth L with pool density ≥ 1) maps which
smooth periods are excluded by the distortion sieve vs undecided (η ≥ 1). Undecided pools —
e.g. L = 21621600 = 2^5·3^3·5^2·7·11·13 (η ≈ 1.0075) and L = 2327925600 (η ≈ 1.0061) — are the
only smooth-period shapes where a covering could still hide; see `scan_undecided.log`.

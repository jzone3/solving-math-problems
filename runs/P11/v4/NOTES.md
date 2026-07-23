# P11 / V4 — annealing + DFT pruning (circulant weighing matrices)

Session: https://app.devin.ai/sessions/63aee44f35f5482db3b0b30b77783bb2
Variant: V4 (local search on ternary vectors, energy = sum of squared nontrivial
periodic autocorrelations; DFT/fold pruning; polish near-solutions).

## 0. Statement re-verification (against original source)

- Source of truth: github.com/dmgordo/circulant-weighing-matrices (`cwm.json`,
  dataset last updated **2026-04-24**), the data behind the La Jolla CWM repository.
  (The URL in the problem file, ljcr.dmgordon.org/cwm/, 404s; the GitHub dataset is live.)
- Repo indexes cells as CW(n, s) with weight k = s^2. The six target cells map to
  keys CW(96,6), CW(105,6), CW(112,6), CW(117,6), CW(120,7), CW(132,9) — **all six
  confirmed status "Open"** in the 2026-04-24 dataset. Problem statement matches:
  ternary first row of length n, weight k, all n-1 nontrivial periodic
  autocorrelations zero (equivalent to W W^T = k I for the circulant W).

## 1. Encoding / theory used

- DFT view: power spectrum |A(j)|^2 = k for all j. j=0 gives
  (n_+ - n_-)^2 = k, so n_+ = (k+s)/2, n_- = (k-s)/2 (negation symmetry fixes the sign).
  For k=36: 21 plus, 15 minus; k=49: 28/21; k=81: 45/36.
- Energy E = sum_{t=1}^{n-1} R(t)^2, R(t) = periodic autocorrelation. E is even and
  E ≡ 0 (mod 4) contributions come in pairs R(t)=R(n-t). Solution iff E=0.
- Fold pruning: for d | n, the fold b_j = sum_t a_{j+td} in Z^d must satisfy
  PAF_d(b) = k*delta, sum b_j = ±s, |b_j| <= n/d, sum|b_j| <= k with parity.
  Stage A (fold.c) anneals valid folds; stage B (lift.c) anneals ternary lifts with
  fold-preserving moves (pair transfer within residue classes). If all nontrivial
  PAFs vanish, R(0)=k is automatic from the fold identity.

## 2. Code

- `anneal.c` — free simulated annealing, fixed composition, O(n) incremental
  autocorrelation updates, geometric cooling + reheats + restarts.
- `pt.c` — parallel tempering variant (24 replicas, geometric ladder).
- `fold.c` — stage-A fold candidate generator.
- `lift.c` — stage-B fold-constrained annealer.
- `verify.py` — standalone witness verifier (also mirrored to solutions/ if a
  witness is ever found).

## 3. Calibration (sanity on cells with known witnesses)

- CW(13,9), CW(26,9), CW(21,16): anneal.c finds witnesses in < 2 s; verify.py PASS.
- lift.c: lifted a CW(13,9) row to a verified CW(26,9) witness in < 1 s.
- **CW(48,36) (known to exist, "Yes")**: plain annealing reached only E=28 after
  484M moves / 5 min; PT reached E=34 in 5 min. The k=36 landscape is already hard
  for unstructured local search at n=48 — known witnesses are algebraically
  structured. This calibrates expectations for the open cells (n >= 96).

## 4. Search log

### Phase 1 — plain annealing / PT / ILS (negative calibration)
- anneal.c, pt.c, ils.c all stall on the *known* cell CW(48,36):
  bestE 28 (anneal, 484M moves), 34 (PT), 32 (ILS) in ~5 min each.
  Conclusion: unstructured single-site/swap local search cannot reach E=0 at
  weight 36 even where witnesses exist. 4h baseline anneal runs on all six open
  cells produced nothing below the report threshold (E<=60) before being retired.
- Fold pruning (fold.c + lift.c): valid folds found for
  d=16 (k=36, m up to 7), d=21 (m=5), d=24 (m=4); none found within 2-20 min for
  d=28,33,35,39,40,44 (inconclusive — annealer, not exhaustive). Lifting the known
  CW(48,36) row to n=96 stalled at E=52; other lifts similar. Fold-constrained
  moves shrink the space but do not fix the landscape ruggedness.

### Phase 2 — RRR / difference-map (Fourier-side projections) — the V4 winner
- rrr.py: RRR iteration x += beta*(P_A(2 P_B(x) - x) - P_B(x)) with
  P_A = flat-spectrum projection (magnitudes := s, DC := +s),
  P_B = nearest ternary with composition (21+,15-) for k=36.
- **Solved the known cell CW(48,36) in 117 s / 4.85M iterations** (verified PASS
  by verify.py) — the cell that all Phase-1 local searches failed on.
  Also solves CW(13,9) instantly. RRR is qualitatively stronger here.
- Calibration on larger known cells CW(91,36), CW(104,36) (30 min each) and
  6-hour RRR runs on all six open cells launched (8 cores, random beta in
  [0.3,0.9] per restart).

### Phase 3 — RRR scaling wall and multiplier-symmetric RRR
- Beta sweep on CW(48,36) (rrr_batch, 3 seeds x beta in {0.3,0.5,0.7,0.9,-0.5}):
  all positive betas solve in <=2 min (11/12); negative beta fails badly.
  Kept beta ~ U[0.3, 0.9].
- Batched RRR (64 replicas/process, ~700k replica-iters/s) does NOT solve the
  *known* cells CW(91,36), CW(104,36) in 15 min (~370M replica-iters each;
  bestE 64 / 80). Random-start RRR hits a scaling wall by n~90.
- rrr_sym.py: RRR restricted to the fixed space of a multiplier i -> t*i
  (variables = orbits of <t> on Z_n; P_A evaluated on full expansion then
  orbit-averaged; weight forced via DC bin + exact integer check).
  **Found the known CW(104,36) with t=3 in < 20 s** (verified PASS) after plain
  RRR failed for 15 min — validating symmetry pruning as the decisive lever.
- sym_driver.py: per cell, enumerate all distinct cyclic multiplier subgroups
  <t> of Z_n^* (deduped by orbit partition), round-robin rrr_sym over them with
  escalating time slices. Launched on all six open cells (6 cores) alongside
  2 continuing plain-RRR runs (96, 105).

### Phase 4 — CW(96,36) witness (with caveat)
- sym_driver on n=96 round 1, multiplier t=41 (m=40 orbits):
  **SOLUTION found, verify.py PASS** —
  `00-0+0+0+00000+0+0+0-0+0-00000-0+0+0+0+0+0-000-000+0-0+0+00000-0+0+0+0-0-00000-0+0-0-0-0+0-000+0`
  (copied to solutions/P11/cw96_36.txt).
- Caveat: support lies on even residues; the 2-decimation verifies as a
  CW(48,36). Since the dataset has CW(48,6)="Yes" but CW(96,6)="Open", the cell
  follows from the classical padding implication CW(n,k) => CW(mn,k). So this
  closes the repository cell but is a propagation, not a new existence theorem.
  The other five cells have no divisor shortcut (CW(39,6)/CW(56,6)/CW(60,7) are
  "No"; k > n excludes the rest) — they remain the real targets.

### Phase 5 — exact multiplier-subgroup exhaustion + ball polish
- sym_exhaust.py / exhaust.c: exact DFS over orbit-constant ternary sequences
  for each cyclic multiplier subgroup <t> (orbit subset-sum to weight k, DC
  window prune, negation symmetry, incremental autocorrelation via precomputed
  orbit cross-correlation tables). C port ~100x Python; validated by (a)
  agreement with the Python exhauster on 7 decided subgroups, (b) re-finding
  known witnesses CW(13,9) (t=3) and CW(104,36) (t=3, 3.6 s).
- exhaust_all.sh sweeping ALL distinct multiplier subgroups per open cell,
  cheapest first (7200 s/subgroup timeout). Definitive EXHAUSTED results so far:
  n=105: 9 subgroups (m <= 27), n=112: 9 (m <= 27), n=117: 18 (m <= 27),
  n=132: 6 (m <= 24), n=120: none yet (smallest subgroup already m=37).
  => No CW witness for these cells is fixed by any exhausted multiplier group.
- Ball polish (ball.py): the persistent rrr_sym near-miss for CW(112,36) with
  t=43 (m=49, E=14) is an isolated deep local optimum — exhaustive orbit-space
  Hamming-ball search to radius 4 (3.39M candidates) finds nothing below E=14.
- SAT polish idea from the variant prompt: superseded — ball search IS an exact
  neighbourhood exhaustion (stronger than SAT within the same radius), and the
  full-space SAT encoding is V1's lane.

### Phase 6 — orbit-reduction SAT (Kramer–Mesner style), session resumed
- orbit_sat.py: same orbit space as exhaust.c, but encoded to CNF and decided
  by CaDiCaL. Vars P_o/M_o per orbit (at-most-one), Tseitin AND product vars
  per orbit pair; weight / DC(+s) / every R(t)=0 (t=1..n/2) as pseudo-Boolean
  equalities via pblib **adder** encoding (BDD encoding blows up — do not use).
  UNSAT is a definitive proof that no H-fixed CW(n,k) exists.
- Validation both directions: re-finds CW(13,9) (t=3, 0.1 s) and CW(104,36)
  (t=3, 23 s adder / 3.6 min bdd), and reproduces DFS UNSAT on n=105 gens=(8,52).
- sat_driver.py swept ALL subgroups per cell (m <= 45), skipping the 186
  DFS-decided ones (parsed from asub_*/cexh_* logs), 3600 s/subgroup.
- **All three DFS-timeout subgroups from Phase 5 are now decided UNSAT**:
  n=105 gens=(11) m=30, n=112 gens=(27,29) m=29, n=132 gens=(31) m=27.
- 48+ additional subgroups decided UNSAT, extending the frontier well past the
  DFS limits — e.g. n=117 to m<=39 complete (plus m=33,35,36 non-cyclic),
  n=120 through m<=36 largely complete, n=112 m<=32 plus m=36..44 partial.
  Full per-subgroup records in logs/satdrv_*.log, logs/sat_*.log.
- Remaining hard instances (multi-hour CaDiCaL runs, still open at session
  checkpoints): n=105 m=35..45 (4), n=112 m=36..44 (4), n=117 m=41,41,45,
  n=120 gens=(23) m=37, n=132 m=36..42 (3); subgroups with m>45 not attempted.

## 5. Final results (after ~8 h wall / 8 cores)

### Witness found
- **CW(96,36): verified witness** (solutions/P11/cw96_36.txt, verify.py PASS)
  found by rrr_sym (t=41). Caveat: it is a zero-interleaved lift of a CW(48,36),
  so it closes the "Open" repository cell via the classical CW(n,k) => CW(mn,k)
  implication rather than a new theorem. Recommend reporting to the dataset
  maintainer either way (the cell should not be listed Open).

### Definitive exhaustions (no multiplier-symmetric witness exists)
Exact, machine-verified exhaustion of ALL ternary sequences fixed by each
multiplier subgroup H <= Z_n^* (cyclic and non-cyclic, exhaust.c), per cell —
counts of distinct subgroups fully exhausted, with orbit-count (m) frontier:

| cell        | subgroups exhausted | orbit counts m covered | timeouts |
|-------------|--------------------:|------------------------|----------|
| CW(105,36)  | 41 | all subgroups with m <= 28, plus m=30 in progress | none |
| CW(112,36)  | 38 | all with m <= 28 (m=29 in progress) | none |
| CW(117,36)  | 53 | all with m <= 32 (m=33 in progress) | none |
| CW(120,49)  | 34 | all with m <= 26 | (23, m=37) cyclic |
| CW(132,81)  | 20 | all with m <= 24 | (31, m=27) |

Interpretation: if any of these five cells has a witness, it is fixed by NO
multiplier subgroup with orbit count below the per-cell frontier — i.e. any
solution has (at most) very small multiplier symmetry. Combined with the known
multiplier theorems this is structured negative evidence; the raw logs
(runs/P11/v4/logs/asub_*.log, cexh_*.log) list every exhausted subgroup with
generators, m, and leaf counts.

### Near-miss inventory (best energies reached, E = sum R(t)^2 (+weight dev))
- CW(105,36): E=24 (rrr_sym t=16, m=45)
- CW(112,36): E=14 (rrr_sym t=43, m=49) — isolated: exhaustive orbit-space
  Hamming ball to radius 4 (3.39M candidates) contains nothing better
- CW(117,36): E=32 (t=40, m=65)
- CW(120,49): E=32 (t=13, m=42)
- CW(132,81): E=34 (t=25, m=36)
- plain (non-symmetric) RRR best: n=96 E=70, n=105 E=72, n=112 E=104,
  n=117 E=96, n=120 E=140, n=132 E=268

### Compute spent (approx)
- ~8 h x 8 cores: ~2 h plain annealing/PT/ILS baselines, ~3 h plain+symmetric
  RRR (~10^10 replica-iterations total), ~4 h exact subgroup exhaustion
  (~10^9-10^10 DFS leaves machine-checked), overlapping.

### Dead ends
- Plain annealing / parallel tempering / ILS: cannot reach E=0 at k=36 even for
  n=48 where witnesses exist; useless at n >= 96.
- Fold(stage-A)/lift(stage-B) two-level annealing: folds easy to find for
  m = n/d >= 3, lifts stall (E >= 50).
- Negative-beta RRR diverges; ILS polish of RRR near-misses does not help.

## STATUS: near-miss / frontier-pushed
(One repository cell CW(96,36) closed with a verified witness, but via a
classical padding implication — not a genuinely new existence result. The five
hard cells remain open; contributed: exact exhaustion of all small-orbit-count
multiplier subgroups + best-known local-search near-misses + a validated
RRR/difference-map toolchain that rediscovers known witnesses at n <= 104.)

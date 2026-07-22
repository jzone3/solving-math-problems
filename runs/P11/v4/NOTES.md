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

## STATUS: running

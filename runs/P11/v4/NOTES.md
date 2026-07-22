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

(checkpointed as runs progress)

## STATUS: running

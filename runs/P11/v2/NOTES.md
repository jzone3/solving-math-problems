# P11 V2 — multiplier-orbit exhaustion (runs/P11-v2)

## Problem re-verification (2026-07-22)
- Cloned github.com/dmgordo/circulant-weighing-matrices (La Jolla CWM repo data).
- NOTE: cwm.json keys use **s, not k=s²** (comment in cwm_code.py line 12). So the six
  target cells are keys CW(96,6), CW(105,6), CW(112,6), CW(117,6), CW(120,7), CW(132,9).
- All six confirmed `"status": "Open"` in current cwm.json (fetched 2026-07-22). Statement
  in problems/P11-circulant-weighing.md matches the repository definition (circulant {0,±1}
  matrix W, W·Wᵀ = kI ⇔ ternary first row, weight k, all nontrivial periodic
  autocorrelations zero).

## Encoding (V2 premise)
If a CW(n,k) has numerical multiplier subgroup H ≤ Z_n^*, some translate of its first row
is constant on the orbits of H acting on Z_n by multiplication. Search:
1. Enumerate ALL subgroups H of Z_n^* (closure over ≤3 cyclic generators; Z_n^* here has
   rank ≤ 3), skip trivial H.
2. Orbits of H on Z_n; assign each orbit a value in {0,+1,−1}.
3. DFS over orbit subsets with size-sum exactly k, then all sign patterns (first orbit
   fixed +1 by negation symmetry); exact integer O(n²) autocorrelation check at leaves,
   plus (Σa)² = k prune.
4. Optional `--signed` mode: a_{t·i} = χ(t)·a_i for each character χ: H → {±1}
   (multiplier-with-sign); orbits whose stabilizer meets ker χ nontrivially forced to 0.

Code: runs/P11/v2/orbit_search.py (pure python, exact integer arithmetic).

## Validation
Search rediscovers known witnesses: CW(7,4) (2 found), CW(13,9) (8), CW(21,16) (22).

## Implementation history
1. First pure-python DFS (orbit_search.py) validated on CW(7,4)/CW(13,9)/CW(21,16),
   launched on all 6 cells with max-orbits 40, 900s/case budget. Several |H|∈{6,8,10}
   cases with r=24–39 orbits EXCEEDED the python budget.
2. Rewrote the DFS core in C (orbit_dfs.c, ~50–100× faster; O(k²) difference-table leaf
   check) with python case-enumeration driver (drive_c.py). Validated: identical witness
   counts (2/8/22) on the three known control cells. Relaunched all 6 cells with
   max-orbits 48, 3600s/case.

Note: for CW(120,49), s=7 with gcd(7,120)=1 — 7 is (by the classical multiplier theorem
for CW with prime p | k, p ∤ n) essentially forced as a multiplier, so exhausting the
⟨7⟩-invariant case carries real nonexistence weight for that cell.

## Runs
(see below, appended as they complete)

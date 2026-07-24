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

### Unsigned C exhaustion (max-orbits 48, 3600s/case, ~14h wall, 6 cells parallel)
Logs: c_<n>_<k>_plain.log. Zero witnesses everywhere. "exceeded" = cases hitting the
1h/case budget (all with small |H| ∈ {2,3,4,5,6,8} and 26–48 orbits — these approach the
unrestricted search and are V1/V3 territory).

| cell | cases complete | exceeded | wall time |
|---|---|---|---|
| CW(96,36)  | 19 | 11 | 49699s |
| CW(105,36) | 37 |  9 | 38881s |
| CW(112,36) | 30 | 13 | 48298s |
| CW(117,36) | 37 |  6 | 23252s |
| CW(120,49) | (running, 118 subgroups) | ≥11 | — |
| CW(132,81) | 14 |  7 | 27923s |

Several huge cases completed with leaves=0, e.g. CW(117,36) |H|=4 r=35: 174·10⁹ nodes,
0 leaves — the (Σa)²=k + subset-sum prunes alone kill them.

### Signed (multiplier-with-sign) runs — mathematically vacuous, confirmed empirically
All signed cases (nontrivial character χ: H→{±1}) die at node 1: χ-twisted invariance
forces every orbit entry-sum to cancel, so Σa = 0, contradicting the necessary
(Σa)² = k. Hence "multiplier with sign −1" can never produce a CW — the trivial-character
(unsigned) search already covers everything. Logs c_<n>_<k>_signed.log
(35–99 cases/cell, all complete, 0 witnesses, <1s each).

### Dedicated attack: CW(120,49), forced multiplier 7
k = 49 = 7², gcd(7,120)=1 ⇒ 7 is a multiplier of ANY putative CW(120,49)
(Theorem 2.4 in Arasu–Gordon–Zhang, arXiv:1908.08447: k = p^{2r} prime power,
gcd(n,k)=1 ⇒ p is a multiplier and fixes a translate; citing Arasu–Seberry 1996).
So exhausting the ⟨7⟩-invariant case (⟨7⟩ = {1,7,49,103} mod 120, |⟨7⟩|=4, r=39
orbits) resolves the cell outright. First split attempt (no fold prune, 1094 depth-7
prefixes, 1h/job): first 6 jobs all EXCEEDED — abandoned in favor of the fold prune.

### BREAKTHROUGH: quotient-fold prune (2026-07-23)
For d | n fold the first row to b_j = Σ_{i≡j (mod d)} a_i. Zero autocorrelation over
Z_n implies zero folded autocorrelation over Z_d, Σ_j b_j² = k and Σ_j b_j = ±√k.
Enumerate ALL valid folded images b (fold_targets() in drive_c.py; e.g. d=8,k=49: only
16 targets = ±7 concentrated in a single residue class!). DFS maintains the partial fold
vector and prunes when no target is reachable within per-class remaining capacity
(fRsuf). Implemented in orbit_dfs.c (FOLD input section) + drive_c.py/split_case.py.
- Soundness: prune is a necessary condition only; exact leaf check unchanged. Control
  cells still give 2/8/22 (and 6/8 in split mode) witnesses.
- Power: benchmark CW(120,49) |H|=8 r=28 case: 10.7·10⁹ nodes / 2858s without fold →
  223,196 nodes / 0.03s with fold-8 (≈50,000× reduction).
Fold moduli used: d=8 (n=96,112,120: 192/192/16 targets), d=7 (n=105: 42), d=9 (n=117:
108), d=6 (n=132: 48).

### Fold-pruned full reruns (max-orbits 64 ⇒ ALL nontrivial subgroups, 3600s/case)
Logs f_<n>_<k>.log. CW(117,36): all 45 subgroup cases processed, 39 complete,
6 EXCEEDED (all |H|≤4, r≥41), 0 witnesses. CW(132,81): 23 cases, 1h-exceeded tail only,
0 witnesses. Others still running; every completed case 0 witnesses.

### CW(120,49) ⟨7⟩ exhaust with fold-8 (the decisive case)
split_case.py resumable prefix split (depth 6, 365 jobs, done_pfx.txt skip list),
logs split_120_49_m7_fold8.log + split2_120_49.log, unlimited time/job, 5 workers.
Individual prefix jobs now complete in minutes–tens of minutes (vs >1h timeout before).

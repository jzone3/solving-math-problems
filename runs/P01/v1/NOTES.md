# P01 Sheehan — V1 (direct annealed counterexample search)

Session: https://app.devin.ai/sessions/89c804aff3e8446ba044c5bfcd5651f6
Date: 2026-07-22

## Problem statement re-verification

- Statement checked against Open Problem Garden ("r-regular graphs are not uniquely
  hamiltonian", Sheehan) and problem file: **every Hamiltonian 4-regular simple graph has
  ≥ 2 Hamiltonian cycles**; witness = 4-regular simple graph with exactly one HC.
- Openness re-confirmed (July 2026): Open Problem Garden still lists it open; Brinkmann–De
  Pauw (DMTCS 2024, "Uniquely hamiltonian graphs for many sets of degrees") treats the
  4-regular case as open; no announcement of a resolution found via web search.
- Known frontier: exhaustively verified for n ≤ 21 (Goedgebeur–Meersman–Zamfirescu), so all
  searches here use n ≥ 22.

## Encoding / algorithm (search.c)

- State: Hamiltonian 4-regular simple graph on n vertices, adjacency matrix + degree-4
  neighbor lists.
- Seed states: cycle 0..n-1 plus a random second Hamiltonian 2-factor (random permutation
  cycle) avoiding duplicate edges ⇒ guaranteed 4-regular + Hamiltonian.
- Move: 2-opt edge swap — pick edges (a,b),(c,d), replace with (a,c),(b,d) or (a,d),(b,c)
  when simple; preserves 4-regularity (may lose Hamiltonicity; count 0 ⇒ objective 1e6).
- Objective: log(#HC), minimized; #HC counted exactly by DFS from vertex 0 (directed count
  / 2) with a safe degree-availability pruning rule and an early cutoff (dynamic cap
  = 2·current+8) so evaluations get cheaper as the count drops.
- Annealing: Metropolis, T = 0.30·exp(−5·it/iters) + 0.02, random restarts each `iters`
  moves; `./search n seed iters cap tlimit`.

## Counter validation

- `crosscheck.py`: C counter vs. brute-force permutation counter — K5 = 12 HCs, plus 20
  random 4-regular graphs n ∈ {8,10,11,12}: all match (ALL PASS).
- Timing (full exact count of random 4-regular): n=22: 6633 HCs in 0.02 s; n=26: 20560 in
  0.10 s; n=30: 103935 in 0.70 s; n=34: 418570 in 3.4 s.

## Runs

### Pilot (n=22)
- Fixed cap 64, flat T≈1 schedule: no gradient (all counts hit cap) — dead end, fixed by
  dynamic cap + cooler schedule.
- 180 s pilot (seed 2, iters 20000): descended 6633 → **240** HCs at n=22.

### Batch 1 (in progress)
- 8 parallel workers, 4 h each (tlimit 14400 s, iters 200000/restart, cap 100000):
  n ∈ {22,24,24,26,28,28,30,32}, logs in `logs/n*-s*.log`.
- Results: (checkpointed below as they come in)

### Batch 1 outcome (dead end → fix)
- iters=200000/restart was far too long a schedule: workers stayed in high-T random-walk
  phase for hours (n=22 stuck at 1674, n=28 at ~27000). Killed after ~20 min.
- Basin-hopping mode added (`hop`): restart = copy best graph + 8 random swaps, short
  schedule iters=30000. Much better: n=22 → 144, n=24 → 144, n=26 → 192 within ~20 min.

### Batch 2 (basin-hopping, in progress)
- 8 workers `./search2 n seed 30000 100000 13500 1`, n ∈ {22,22,24,24,26,28,30,32}.

## Literature context for near-misses (Haythorpe arXiv:1608.00713)

Exhaustive minima of #HC over 4-regular Hamiltonian graphs: n=12: 60, n=13–16: 72,
n=17: 96, n=18: 108 (n≥17 restricted to connectivity-2). Minimal graphs are essentially
always vertex-connectivity 2. Extrapolating, the true minimum at n=22 is plausibly
~130–190, so our annealer hitting 144 at n=22 suggests it reaches (near-)optimal graphs —
and that the global minimum curve is far above 1, consistent with the conjecture.

### Grow mode & seeded runs
- Added `grow` mode: insert a new vertex on the pair of disjoint edges minimizing the exact
  HC count (4-regularity preserved). Growing the annealed 144-HC n=22 graph keeps the count
  at exactly **144 for every n = 23..32** — a constant-count chain, the same phenomenon
  Thomassen–Zamfirescu (arXiv:2104.06347) used to refute Haythorpe's Conjecture 4.2.
- Reproduced Haythorpe's G*_{16,4} (72 HCs, verified with our counter; matching labeling
  (1,4),(2,5),(3,6)). Greedy growing from it degrades: 96, 120, 144, 180, 240, 288, ... —
  the tight 72 structure does not survive naive insertions.
- Seeded anneal at n=22 from grown h22 (288 HCs) reached only 192; fresh basin-hopping
  reaches 144 (n=22, 23, 24) — 144 appears to be a hard floor for this move set at n≥22.

### Calibration against known exhaustive minima (Haythorpe Table 1)
- Basin-hopping anneal at n=16/17/18 found **72 / 96 / 108** — exactly the published
  exhaustive minima. The move set + schedule reaches global minima at sizes where ground
  truth is known, so the 144 plateau at n=22 is plausibly the true minimum there
  (= 36·2^(n+2-16... ) i.e. G*_{22,4} count 36·2^2 = 144).

## Near-misses / observations

- Best counts found cluster on highly divisible values (144, 192, 288) — suggests
  convergence to structured (likely low-connectivity, gadget-chain) graphs, same family
  shape as Haythorpe/Thomassen–Zamfirescu minimal examples.

## STATUS: running

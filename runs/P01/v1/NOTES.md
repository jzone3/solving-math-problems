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

## Near-misses / observations

(TBD)

## STATUS: running

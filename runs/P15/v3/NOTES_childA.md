# P15 V3 — child A compute sweep (breakout min-conflicts, m=13)

Session: https://app.devin.ai/sessions/1c0d0f3daa9c4e76b4e7160bce455b37
Parent: https://app.devin.ai/sessions/0ad9a586fd2a4844851a6a7b4d2a20a6
Hardware: 8 cores, 31 GB RAM. Engine: cover_mc.c built with gcc -O2.

Plan per parent instructions: multi-seed sweep m=13 at N=367567200
(slack 2.038, ~10.3 GB) and N=183783600 (slack 1.957, ~5 GB), 7 h
budgets (25200 s), distinct seeds; restart any seed whose best= stalls
for >1 h. Every witness must PASS solutions/P15/verify.py.

A stall monitor kills any run whose best= is unchanged for >1 h and
restarts it with a fresh seed (same N, fresh 25200 s budget).

## Run log
| N | m | seed | budget (s) | outcome |
|---|---|------|------------|---------|
| 367567200 | 13 | 101 | 25200 | stalled at best=205375 holes (t=1547s); killed after 1h no improvement, restarted as seed 201 |
| 183783600 | 13 | 102 | 25200 | stalled at best=149167 (t=8830s, sweep-best); restarted as 205 |
| 183783600 | 13 | 103 | 25200 | stalled at best=161075 (t=3823s); killed, restarted as seed 202 |
| 183783600 | 13 | 104 | 25200 | stalled at best=311355 (t=4568s); killed, restarted as seed 203 |
| 367567200 | 13 | 201 | 25200 | stalled at best=222151 (t=9s, greedy init then no MC gain); killed, restarted as seed 204 |
| 183783600 | 13 | 202 | 25200 | stalled at best=193440 (t=5328s); restarted as 207 |
| 183783600 | 13 | 203 | 25200 | stalled at best=149203 (t=10479s); restarted as 210 |
| 367567200 | 13 | 204 | 25200 | stalled at best=220439 (t=2s, greedy init only); restarted as 206 |
| 183783600 | 13 | 205 | 25200 | stalled at best=198193 (t=4903s); restarted as 208 |
| 367567200 | 13 | 206 | 25200 | reached best=212086 (t=4016s) then stalled; restarted as 209 |
| 183783600 | 13 | 207 | 25200 | broke the plateau: best=95367 at t=13506s, then stalled; restarted as 214 |
| 183783600 | 13 | 208 | 25200 | best=95227 at t=11910s (best of the cover_mc phase); killed at engine switch |
| 367567200 | 13 | 209 | 25200 | stalled at best=214355 (t=40s); restarted as 211 |
| 183783600 | 13 | 210 | 25200 | stalled at best=366157 (t=803s); restarted as 212 |
| 367567200 | 13 | 211 | 25200 | stalled at best=228149 (t=5s); restarted as 213 |
| 183783600 | 13 | 212 | 25200 | best=317195 (t=2465s); killed at engine switch |
| 367567200 | 13 | 213 | 25200 | best=199856 (t=4048s); killed at engine switch |
| 183783600 | 13 | 214 | 25200 | best=300954 (t=1097s); killed at engine switch |
| 183783600 | 13 | 215 | 25200 | best=542911 (t=674s); killed at engine switch |

Early observation: at N=3.7e8 the MC loop is extremely slow (~0.1 it/s after
init; per-move cost O(holes + N/n)); best barely moves past greedy init
(~2.2e5 holes). At N=1.8e8 the loop sustains ~40 it/s and descends steadily
(5.4e5 -> 1.5e5 holes on seed 102).

Mid-sweep pattern (~7 h in): every N=1.8e8 seed follows the same curve —
staircase descent to ~1.5e5-1.9e5 holes over 1-3 h, then a hard plateau the
breakout kicks never escape; monitor recycles the seed. Best hole counts:
149167 (s102), 149203 (s203), 161075 (s103), 162977 (s207, running). The
plateau floor ~1.5e5 holes (~0.08% of N) looks structural at this slack for
m=13, matching the parent's note that per-move cost at N~10^8 collapses
throughput at high hole counts. Two seeds later escaped it (s207 95367,
s208 95227) but descent below ~9.5e4 was <10 holes/min.

## Phase 2: cover_mc3 (childB engine, ~20x faster)
Parent redirected to the sibling engine (branch runs/P15-v3-childB,
cover_mc3.c: sampled-candidate moves, OpenMP, uint16 cnt). Built with
gcc -O2 -fopenmp -march=native. Killed all cover_mc runs, dropped
N=367567200 per instructions (RAM/throughput-bound), launched 2 parallel
cold runs (4 threads each) at N=183783600 m=13, 5400 s budgets:

| N | m | seed | engine | outcome |
|---|---|------|--------|---------|
| 183783600 | 13 | 301 | cover_mc3 | best=33555 holes at kill (~500 it/s sustained) |
| 183783600 | 13 | 302 | cover_mc3 | best=37633 holes at kill |

cover_mc3 confirmed ~10-13x faster wall-clock convergence here: 5.4e5 ->
3.4e4 holes in ~90 min vs. best 9.5e4 after 4-7 h with cover_mc. Runs were
killed by a coordinator-wide PAUSE before the planned squeeze.sh
(warm-restart + repair_mc) cycles could start. Best warm-restart state dumps
kept in witnesses/: mc3_m13_N183783600_s301.json.state (best=33555) and
mc3_m13_N183783600_s302.json.state (best=37633) — resumable via cover_mc3
arg8 or squeeze.sh.

## Final status (coordinator PAUSE, 2026-07-24 ~15:40 UTC)
- No m=13 witness found; nothing verified (no JSON produced, so no
  verify.py run was applicable).
- Best hole counts: N=183783600: 33555 (mc3 s301), 37633 (mc3 s302),
  95227 (cover_mc s208); N=367567200: 199856 (cover_mc s213).
- All computations stopped; branch runs/P15-v3-childA holds notes + states.

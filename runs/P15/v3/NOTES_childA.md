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
| 183783600 | 13 | 102 | 25200 | running; best=149167 at t=8830s, still improving |
| 183783600 | 13 | 103 | 25200 | stalled at best=161075 (t=3823s); killed, restarted as seed 202 |
| 183783600 | 13 | 104 | 25200 | stalled at best=311355 (t=4568s); killed, restarted as seed 203 |
| 367567200 | 13 | 201 | 25200 | stalled at best=222151 (t=9s, greedy init then no MC gain); killed, restarted as seed 204 |
| 183783600 | 13 | 202 | 25200 | running; best=217978 at t=1978s |
| 183783600 | 13 | 203 | 25200 | running; best=305001 at t=1816s |
| 367567200 | 13 | 204 | 25200 | running; best=220439 at init |

Early observation: at N=3.7e8 the MC loop is extremely slow (~0.1 it/s after
init; per-move cost O(holes + N/n)); best barely moves past greedy init
(~2.2e5 holes). At N=1.8e8 the loop sustains ~40 it/s and descends steadily
(5.4e5 -> 1.5e5 holes on seed 102).

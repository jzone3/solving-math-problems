# P15 V3 — child A compute sweep (breakout min-conflicts, m=13)

Session: https://app.devin.ai/sessions/1c0d0f3daa9c4e76b4e7160bce455b37
Parent: https://app.devin.ai/sessions/0ad9a586fd2a4844851a6a7b4d2a20a6
Hardware: 8 cores, 31 GB RAM. Engine: cover_mc.c built with gcc -O2.

Plan per parent instructions: multi-seed sweep m=13 at N=367567200
(slack 2.038, ~10.3 GB) and N=183783600 (slack 1.957, ~5 GB), 7 h
budgets (25200 s), distinct seeds; restart any seed whose best= stalls
for >1 h. Every witness must PASS solutions/P15/verify.py.

## Run log
| N | m | seed | budget (s) | outcome |
|---|---|------|------------|---------|
| 367567200 | 13 | 101 | 25200 | running |
| 183783600 | 13 | 102 | 25200 | running |
| 183783600 | 13 | 103 | 25200 | running |
| 183783600 | 13 | 104 | 25200 | running |

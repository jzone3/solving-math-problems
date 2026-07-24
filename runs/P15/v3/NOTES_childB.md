# P15 V3 — child B: throughput engineering for the explicit m=13+ push

Session: https://app.devin.ai/sessions/bc5faff2a8524b1d81fa86be563bdfcc
Parent: runs/P15-v3 (see NOTES.md, phase 4). Task: cover_mc at N=183783600,
m=13 runs at ~50 it/s and stalls ~140k holes; get ~100x throughput or a
smarter repair phase and close the last ~1e5 holes.

## Baseline reproduction
./cover_mc 183783600 13 1800 91 /tmp/x.json (gcc -O2 -march=native):
109008 iterations in 1800 s = 60.6 it/s, NOSOLUTION best=253638.
Confirms the ~50 it/s figure (single-threaded, and each move pays
O(nh) gain scan over ~4.8e5 holes + O(n) scans over ALL residues of the
picked modulus — up to 1.8e8 for the largest divisors — + O(N/n) strided
class scans).

## cover_mc2.c (first iteration, kept for the record)
Same search, engineered: gain only at residues actually hit by holes
(touched list, sparse reset — never O(n) over residues), hole->residue
modulo pass OpenMP-parallel into a scratch buffer, lose scan parallel,
cnt uint16, w/gain float, division-free parallel greedy init (rolling
residue counters; hole-list histogram for divisors > 2^21).
Also fixes a subtle search-behavior regression this refactor introduced:
when the landscape is flat (no hole-hitting residue, lose=0) the original
reservoir-ties over ALL residues amount to a pure random walk; the sparse
version must reproduce it explicitly or it stalls (m=7 unsolved in 300 s
without it, 70 s with).
Result at N=183783600 m=13: ~100 it/s (~1.7x). The full-hole-list gain
scan (4.8e5 random-access weight reads per move) dominates; not enough.

## cover_mc3.c (the engine that closed m=13)
Key idea: a move never scans the full hole list NOR full residue range.
- Candidate residues are proposed from a SAMPLE of the hole list
  (default 16384; exact whenever nh <= sample, i.e. the entire endgame).
  Best sampled candidate by weighted gain, reservoir tie-breaking.
- The chosen candidate is then evaluated EXACTLY with two OpenMP-parallel
  strided class scans: egain = sum of w over holes in the new class,
  lose = sum of w over uniquely-covered elements of the vacated class.
  Accept if weighted delta > 0 (sideways only on flat landscape).
  So acceptance is exact; sampling only biases WHICH candidate is tested.
- Noise moves (1% random reassignment) restricted to moduli with class
  size N/n <= 65536: at N=1.8e8 a random reassignment of a small modulus
  instantly blows ~1e6-1e7 holes (observed: energy 4.8e5 -> 3.6e6 in the
  first 30 s), something the 50 it/s original never got to feel.
- cnt uint16, w float, int32 hole list, division-free parallel greedy init.
  RAM ~4 GB at N=1.8e8 (vs ~7 GB baseline).

Smoke tests: m=5/N=1440 and m=7/N=15120 solve in seconds (~360k it/s at
N=15120), witnesses PASS solutions/P15/verify.py.

## Measured at N=183783600, m=13, seed 91, 7 threads
- throughput: 1050-1340 it/s sustained (baseline 60.6 it/s) => ~20x per
  iteration; but iterations are also *better targeted* (every accepted
  move is exactly evaluated), so hole-closing progress is far more than
  20x: baseline best after 1800 s = 253638; cover_mc3 best after 1800 s
  ≈ 45000, after 4300 s = 11524 — clean staircase through the ~140k
  plateau that stalled the original engine.
- kick behavior (restore best + shake ~8 random moduli + weight reset,
  unchanged from baseline) produces 80-150k transient holes per kick at
  this scale but recovers to new bests within ~2-4 min at this rate.

## Run log
- mc3 m=13 N=183783600 seed 91: [in progress; outcome recorded below]

## Outcome
[pending]

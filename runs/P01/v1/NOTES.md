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
  (144 = Haythorpe's G*_{22,4} count 36·2^2).

### Ground-truth match extended (GMZ arXiv:1812.05650, Table 3)
- GMZ computed exhaustive minima of #HC over ALL 4-regular Hamiltonian graphs up to n=21:
  n=19: 144 (21 graphs), n=20: 144 (18), n=21: 144 (13); n ≥ 22 left as "?".
- Our anneal independently reproduced 144 at n=19, 20, 21 (and 72/96/108 at 16/17/18) —
  i.e. it matches the exhaustive ground truth at EVERY order where it is known.
- At n=22..32 (incl. odd n=23) every configuration floors at exactly 144; nothing below
  144 was ever seen for n ≥ 19 across ~4.5 h × 8 cores of annealing.

## Near-misses / observations

- Best counts found cluster on highly divisible values (144, 192, 288) — convergence to
  structured gadget-chain graphs (2-cuts, triangle-rich), same family shape as
  Haythorpe / Thomassen–Zamfirescu minimal examples.
- Side result (possibly record-tying/record-beating upper bounds): grow-chain graphs
  `seed/g22.txt` … `seed/g32.txt` each have EXACTLY 144 Hamiltonian cycles
  (independently verified with `verify_nearmiss.py` at n=22, 25, 28, 30, 32: PASS).
  Published constructions give 36·2^{⌊n/5⌋−2} (GMZ Obs. 3.10; = 288 at n=25, 576 at n=30)
  and a constant-216 family (Thomassen–Zamfirescu arXiv:2104.06347 Fig. 1). Our constant
  144 = the n=19–21 exhaustive minimum, extended flat through n=32, is below both for
  n ≥ 25. Suggests min #HC for 4-regular graphs is exactly 144 for all n ≥ 19 — a
  natural conjecture from this data (and a very strong quantitative form of Sheehan).

## Final run totals (all workers hit their time limits, none found < 144 for n ≥ 19)

| n  | best #HC | anneal iterations | mode |
|----|----------|-------------------|------|
| 16 | 72 (= known min)  | short calib | hop |
| 17 | 96 (= known min)  | short calib | hop |
| 18 | 108 (= known min) | short calib | hop |
| 19 | 144 (= known min) | 4,206,939 | hop |
| 20 | 144 (= known min) | 2,865,354 | hop |
| 21 | 144 (= known min) | 1,980,241 | hop |
| 22 | 144 | 2,401,191 | hop (3.75 h) |
| 23 | 144 | 1,021,488 | hop (3 h) |
| 24 | 144 | ~1 h runs | hop |
| 26 | 192 | ~1 h runs | hop |
| 28 | 144 | 93,426 | seeded (3 h) |
| 30 | 144 | 33,932 | seeded (3 h) |
| 32 | 144 | 12,226 | seeded (3 h) |

Total compute: ≈ 4 h wall × 8 cores of annealing + grow/verification runs.

## Conclusion for Sheehan's conjecture (V1 framing)

Direct annealed search finds no uniquely Hamiltonian 4-regular graph; the empirical
minimum-#HC landscape is flat at 144 for n ≥ 19 and the search provably reaches the true
minimum at every order where exhaustive data exists. Nothing remotely close to a
counterexample (would need count 1; nothing below 144 observed). Strongly consistent with
the conjecture being TRUE.

---

# Continuation run (frontier push, 2026-07-23)

## New encoding: multigraph relaxation (msearch.c)

- State space enlarged to 4-regular loopless MULTIgraphs (multiplicity ≤ 2). Weighted HC
  count (product of multiplicities of used edges — the convention under which Fleischner's
  uniquely hamiltonian 4-regular multigraphs have exactly one HC). Counter validated:
  doubled triangle = 8 HCs; agrees with the simple counter on best22/h16.
- Objective log(#HC) + λ·(#extra parallel copies), λ ramped 0.1 → 2.0 within each anneal
  round: search descends in the relaxed multigraph space, then is pressed toward simple
  graphs. A simple state with #HC = 1 would be a Sheehan counterexample.
- Rationale: uniquely hamiltonian 4-regular multigraphs EXIST (Fleischner 1994), so the
  relaxed space contains count-1 states; the question is whether annealing can carry
  low counts back into simple territory.
- Results (4 h × 6 workers, exact re-verification of final states with `msearch count`):
  - n=14: multigraph with **16 HCs** using 3 extra parallel copies (multigraph/m14-s71-best.txt)
  - n=16: multigraph with **16 HCs** using 4 extra copies (m16-s72-best.txt)
  - n=22: multigraph with **96 HCs** using ONE doubled edge (m22-s74-best.txt) — a single
    parallel edge already beats the simple minimum 144; the doubled edge is 9–21.
  - λ=0 floor probes (n=10, 12): never below 16 HCs even with unrestricted parallel edges;
    the anneal NEVER approached count 1 anywhere in multigraph space (consistent with
    Fleischner's examples being large/very rigid — his simple min-degree-4 versions have
    338+ vertices).
  - Caveat logged: the in-run `best_simple_hc` counters (68 at n=14/16) are artifacts of
    the dynamic counting cap and were NOT confirmed by exact recounts (the recorded value
    can be a capped undercount); only exactly re-verified numbers are reported above.

## Frontier push: constant-144 family extended to n = 45, floor checks to n = 44

- Grow chain extended g33…g45: greedy min-count vertex insertion keeps the HC count at
  EXACTLY 144 for every n = 33…45 (seed/g33.txt … g45.txt). Insertion pattern stabilizes
  into a ladder between two hub vertices (new vertex takes over an edge at hub 0 and one
  at hub 12).
- Double-verified with the independent weighted counter (`msearch count`): g36, g40, g44,
  g45 all give exactly 144 (python verifier confirms g36; it times out beyond n≈36).
- Seeded anneals at n = 36 / 40 / 44 (2.5 h each, basin-hopping from the 144-HC seeds):
  best_ever remained 144 (6749 / 5361 / 3729 accepted-move evaluations — counting cost
  grows steeply with n) — no descent below 144 anywhere up to n=44.
- Beyond n=45 the exact-count-per-candidate grow step becomes expensive (~2 h/vertex);
  stopped at n=45. Restricting insertions to hub-incident edge pairs fails past n=45
  (min over that subset jumps to 432), so a smarter incremental counter would be needed
  to push further.

## Continuation 2 (2026-07-23): bitmask counter, deeper floors, mult-3 relaxation, n=46+

- New counter `fastcount.c`/`fastlib.c` (independent 3rd implementation): uint64 bitmask
  adjacency + availability pruning; exact count of g45 in 16 s (was minutes). Validated
  against previous counters on best22/h16/g32/g40/g45 (144/72/144/144/144 all match).
- `search5.c` = annealer driven by the fast counter (~10–50× more move evaluations/h).
  6-h random-seed anneals: the **144 floor was re-hit independently from random seeds** at
  n = 22 (3.37M its), 24 (1.27M), 28 (120k), and 40 (seeded); n=26 stalled at 192.
  Nothing below 144 at any order; nothing remotely near count 1.
- Grow chain (fast counter): g46 found with exactly **144 HCs** (seed/g46.txt), verified
  144 by the independent weighted counter (`msearch count`). Naive extrapolation of the
  insertion pattern (new x adj {0,12,x−3,x−1}) FAILS at n=46 (gives 432) — the greedy
  min-count pair is genuinely non-stationary; full grow costs ~2.5–4 h/vertex at n≥46.
- Multiplicity-3 multigraph anneals (`msearch3.c`, 6 h × 2): best exact-verified states
  **25 weighted HCs at n=18 with 5 extra parallel copies** (multigraph/m18-mult3-best.txt)
  and **72 HCs at n=22 with 2 extra copies** (m22-mult3-best.txt); still nothing below 16.
- Structural note: g45 has only 8 two-vertex cuts, all isolating 3–5-vertex gadgets in the
  original n=19 core; the growing chain region is 3-connected, so a constant-144 proof
  would need a width-4 boundary DP ({0,12,last two chain vertices}), left as a direction.
- Delegated two child sessions with fundamentally different encodings: incremental-SAT
  CEGAR (branch runs/P01-v1-sat) and girth-5/4-connected structure-targeted search
  (branch runs/P01-v1-struct); their notes live under runs/P01/v1/child-*/.

## STATUS: negative (no counterexample; frontier pushed: constant-144-HC simple family
   verified for all n = 19–46 (n=46 double-verified with two independent counters), the
   144 floor independently reproduced from random seeds at n=22/24/28 with a 10× faster
   bitmask counter, beating published few-HC constructions [GMZ 36·2^⌊n/5⌋−2, TZ
   constant-216] for n ≥ 25; multigraph relaxations (mult ≤ 2 and ≤ 3) reach 25 weighted
   HCs @ n=18 but never below 16 HCs in any space searched; SAT-CEGAR and structure-
   targeted child searches spawned on branches runs/P01-v1-sat / runs/P01-v1-struct)

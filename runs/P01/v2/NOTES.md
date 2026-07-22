# P01 Sheehan — V2 structured construction — run notes

Session: https://app.devin.ai/sessions/fd8f5201312a48f193ac2401d115edc1
Variant: V2 (structured construction: build from Fleischner multigraphs /
Entringer–Swart-type near-4-regular seeds; gadget/completion moves that preserve
HC-uniqueness; verify every step exactly).

## 0. Statement re-verification & open-status check (2026-07-22)

- Original statement (Sheehan 1975, via Bondy–Murty GTM 244 unsolved problem list and
  openproblemgarden.org/op/uniquely_hamiltonian_graphs): **no 4-regular simple graph has
  exactly one Hamiltonian cycle.** Matches problems/P01-sheehan.md.
- Open-status check via web search (July 2026): Open Problem Garden still lists it open;
  Goedgebeur–Jooken–Lo–Seamone–Zamfirescu ("Few hamiltonian cycles in graphs with one or
  two vertex degrees", arXiv:2211.08105) treats it as open ("h(4) unknown"); GMZ
  (arXiv:1812.05650, Math. Comp. 2020) verified it up to n ≤ 21. No 2024–2026 result
  claiming resolution found. **Still open.**
- ⚠ Paraphrase fix: problems/P01-sheehan.md says Entringer–Swart built "uniquely
  Hamiltonian graphs with all degrees 4 except two of degree 3". The actual
  Entringer–Swart 1980 result (J. Comb. Theory B 29, 303–309) is the *dual*: **nearly
  cubic** uniquely hamiltonian graphs — exactly two vertices of degree **4**, all others
  degree **3** (h(3,4)=1). GMZ Thm 3.2: these exist iff n even, n ≥ 18 (Royle's 18-vertex
  girth-5 graph is the smallest). This changes the gadget geometry V2 should use (we
  cannot "pair up two degree-3 vertices" of an ES graph to get 4-regularity; instead the
  natural composition adds a perfect matching on the degree-3 vertices).

## 1. Infrastructure (all machine-verified)

- `hc.c` — exact HC counter with cutoff, multigraph-aware (parallel edges = distinct
  cycles). Cross-checked against a permanent brute-force reference on 300 random
  multigraphs (`test_hc.py`, PASS) + K8 = 2520 HCs sanity check.
- `dfs.c` — C completion-DFS (attack 3 below) with a hamiltonian-u,v-path existence
  test; the path test cross-checked against brute force on 400 random instances
  (`test_hp.py`, PASS).
- `hcutil.py` — subprocess wrapper + brute reference.

## 2. Attacks

### Attack 1 — matching completions of nearly cubic 1H seeds (compose_matching.py)
Idea: nearly cubic 1H seeds (2 deg-4 + (n−2) deg-3 vertices), found by simulated
annealing over degree-preserving 2-opt swaps (`search_nearly_cubic.py`; seeds verified
HC-count = 1 exactly).
- *pair mode*: two seed copies + perfect matching across their deg-3 vertices → 4-regular
  on n1+n2 ≥ 36 vertices. Anneal over matchings, objective = capped exact HC count.
- *self mode*: one n ≥ 22 seed + perfect matching on its own 20+ deg-3 vertices →
  4-regular at n = 22–24, just past the exhausted n ≤ 21 frontier.
Early result: pair mode on 18+18 stalls at ≥ 40 HCs (cap); self mode at ≥ 400 (cap).
The matching forces many cross/chord edges simultaneously; landscape flat far from 1.
De-prioritized in favor of Attack 3 (which subsumes it with incremental uniqueness).

### Attack 2 — 4-regular 1H multigraph seeds + gadget replacement (in progress)
Fleischner (JGT 1994) proved loopless 4-regular 1H **multigraphs** exist. Observation:
in such a multigraph the unique HC cannot use either copy of a parallel pair (else
copy-swap gives a 2nd HC), so double edges are always chords. Plan: find small such
multigraphs by annealing (`search_multigraph_seeds.py`, n = 8–14), then enumerate small
4-regular-boundary gadgets replacing a double edge and verify HC count of composition.
Status: annealing running; no small seeds found yet (their minimum order may be large —
Fleischner's constructions are big).

### Attack 3 (main) — completion DFS in chord space (dfs.c)
Normal form: any 4-regular 1H graph = C_n (its unique HC) + a chord set where every
vertex has exactly 2 chords. Adding edges never destroys HCs ⇒ every intermediate
subgraph containing C_n also has HC count exactly 1 ⇒ chord (u,v) is addable iff the
current graph has **no hamiltonian u–v path**. DFS over chord additions with this exact
test is therefore sound AND complete (up to move ordering) for finding any witness at a
given n, with randomized restarts + per-restart node caps.
- Python prototype (n=22): stalls at 16/44 stubs. C version: reaches 8 stubs remaining
  (18/22 chords) within seconds at n=22.
- Sweep launched: n ∈ {22,24,26,28,30,32,36,40}, 4h each, node cap 3e6/restart.

### Attack 3 upgrades
- `dfs.c` v2: monotonicity memo (a hamiltonian u–v path persists under edge additions, so
  a failed pair is dead for the whole DFS subtree — huge cut in repeated path tests), MRV
  branching, multigraph mode (doubled chords; a 2nd parallel copy adds no new vertex
  sequence so only the 1st copy needs the path test), seeded mode, near-miss dumping.
- ham-path tester re-cross-checked after every change (test_hp.py, 400 instances, PASS).

### Attack 3b — exhaustive runs (complete search, no symmetry breaking beyond fixing the HC)
- **Multigraph mode: EXHAUSTED n = 5..14 — no 4-regular uniquely hamiltonian multigraph
  with ≤ 14 vertices exists.** (Fleischner 1994 proved existence; our result bounds the
  minimum order ≥ 15. Node counts ~7× per vertex: n=14 took 2.05e7 nodes.) n=15,16,17
  exhaustions running.
- Simple mode (Sheehan proper, reproduces part of GMZ frontier independently):
  EXHAUSTED n = 10, 12 (no witness); n = 14, 16, 18 running.

### Attack 4 — rotation-symmetric chord completions (symmetric.py)
Chord sets invariant under i→i+k map C_n to itself, hence consistent with uniqueness.
DFS over chord orbits with exact HC-count ≤ 2 checks. Results (all exhausted = "done"):
n=22 k=2 (best_rem 22), n=24 k=2,3,4(timeout best 12), n=26..32 k∈{2,..}: every completed
family exhausted with large best_rem. **Empirical: nontrivial rotation symmetry appears
strongly incompatible with unique hamiltonicity** — orbits add many chords at once and
immediately create second HCs. Sweep to n=60 running.

### Attack 5 — gadget rings (gadget_ring.py)
Ring of m copies of a k-vertex gadget with 4 boundary stubs (2 left, 2 right), straight or
crossed junctions → 4-regular on km vertices. Exhaustive over simple gadgets k ≤ 6 (iso-
deduped), m = 3..7, exact HC count. k=3: no gadgets; k=4: 1 gadget (K4-based), no hits;
k=5: 5 gadgets, 50 rings, no count-1; k=6 running.

### Negative structural findings (machine-verified)
- All nearly cubic 1H seeds tested (n=18: 2, n=22: 9) are **completion-saturated**: not a
  single extra chord (simple or doubled) can be added without creating a 2nd HC — every
  deficient pair (u,v) already has a hamiltonian u–v path. Seeded completion dies at the
  root (nodes=1–3). Nearly cubic 1H graphs are locally maximal; they cannot be grown
  toward 4-regularity by edge additions alone. Gadget/vertex surgery would be required.

## 3. Compute log

- 2026-07-22 20:40 UTC: 8× dfs sweep v1 (retired), nc-seed gen, multigraph anneal (retired).
- 2026-07-22 21:1x: dfs3 exhaustions (multi 15/16/17, simple 12..18), symm sweep n=22..60.
- 2026-07-22 21:4x: dfs4 sweep n=22..32 (12h, nearmiss dumping), gadget rings k=5,6.

## 4. Results so far

- Seeds found & verified 1H: nearly cubic n=18 (2), n=22 (9), n=24 (1); all saturated.
- New exhaustive bound: minimum order of a 4-regular 1H multigraph ≥ 15.
- No witness. Best near-miss (Attack 3): 8 unfilled chord-stubs at n=22.

STATUS: running

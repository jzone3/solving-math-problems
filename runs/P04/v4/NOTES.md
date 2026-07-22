# P04 — Hajós cycle-decomposition conjecture — Variant V4 (extremal families / perturbation)

Session: https://app.devin.ai/sessions/2b4567ec32f343ed852ee39ad5cdecb9
Branch: `runs/P04-v4`

## 0. Statement re-verification & openness check

- Statement checked against Heinrich–Natale–Streicher, arXiv:1705.08724 ("Hajós' cycle
  conjecture for small graphs"): *every simple Eulerian graph on n vertices decomposes into
  at most ⌊(n−1)/2⌋ edge-disjoint cycles*. Matches the problem file. This is the
  Lovász-1968-attributed Hajós conjecture, NOT the topological-K5 one.
- Openness (checked via Exa web/arXiv search, July 2026): only partial results found —
  Girão–Granet–Kühn–Osthus (dense/linear-min-degree asymptotic), Fuchs–Gellert–Heinrich
  (min-counterexample structure), exhaustive verification to n=12 (HNS 2017), 2025 preprints
  on Erdős–Gallai relatives (Bucić–Montgomery; arXiv:2509.01901) do not resolve Hajós.
  No claim of resolution found. Treated as open.
- Consequence of prior work: any counterexample has n ≥ 13, is 3-connected, δ ≥ 6.

## 1. Toolchain

- `mincyc.py`: exact oracle. CP-SAT model with k color classes; each class forced to be a
  single (possibly empty) cycle via `AddCircuit` with self-loop literals; each undirected
  edge assigned exactly one (class, direction). `decomposable_within(n, E, k)` decides
  "∃ decomposition into ≤ k cycles". Includes first-use symmetry breaking between classes.
  Sanity: K_5, K_7, ..., K_13 all feasible at K=⌊(n−1)/2⌋ and infeasible at K−1 (< 1s each).
- `search.py`: perturbation hill-climb. Moves: (a) vertex splits (odd n → n+1 keeps
  K=⌊(n−1)/2⌋ constant — key V4 lever), (b) toggling closed edge-pair sets (flip pairs along
  a vertex cycle; preserves all degree parities). Pool retains tight instances
  (mincyc = K exactly); density-biased selection.

## 2. Tight (equality) families confirmed by machine

All verified feasible at K and infeasible at K−1:
- K_{2k+1} for 2k+1 ∈ {5,7,9,11,13} (and K_15 seeds used in search).
- K_{2k} − perfect matching, n ∈ {14, 16}: m = K·n exactly, all cycles forced Hamiltonian
  — the unique edge-maximal Eulerian graphs; both decompose (feasible@K, infeasible@K−1).
- Clique bouquets (cliques sharing one common vertex): (7,7), (5,5,5), (9,5), (7,5,3) at
  n=13; (9,7), (7,7,3), (5,5,5,3), (11,5), (13,3) at n=15. All tight.

Observation: every tight instance found so far is *degree-forced* (a vertex of degree 2K,
so the ⌈Δ/2⌉ lower bound already gives K). No "structurally tight" instance (Δ < 2K,
tightness from global structure) seen yet — hunting those explicitly (§4).

## 3. Systematic perturbations (exhaustive where possible)

- All 5 non-isomorphic single vertex-splits of K_13 (move a ∈ {2,4,6,8,10} edges to the new
  vertex; by symmetry only a matters): n=14, K=6 — ALL feasible@6 (≤0.2s each). No witness.
- All 6 single splits of K_15: n=16, K=7 — ALL feasible@7. No witness.
- Randomized searches (running, see search logs `log_*.txt`): seeds K14−PM, K13-split,
  K16−PM, K15-split; thousands of parity-preserving perturbations at n=14–16;
  every checked instance so far decomposes within K (status TIGHT or LOOSE, no WITNESS,
  no TIMEOUT; solve times ~0.1–0.3 s per instance).

## 4. Next: structurally-tight hunt

Target: n=14, Eulerian, Δ ≤ 10 (degree bound gives only 5 < K=6). Question: does any such
graph need 6 cycles? If yes → prime perturbation seed; if provably rare/absent in large
samples, that is itself an informative negative.

## STATUS (running)

STATUS: negative (so far) — searches in progress, checkpoint to be updated.

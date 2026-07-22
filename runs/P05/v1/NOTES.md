# P05 V1 — hypotraceable seeds, mutation/annealing search

Session: https://app.devin.ai/sessions/094c48c3c4c7439883a0a78c619b717d
Branch: `runs/P05-v1` (off `devin/1784749757-context-plan`)

## 0. Statement re-verification (2026-07-22)

- Original source: T. Gallai, Problem 6, *Theory of Graphs* (Tihany 1966 colloquium
  proceedings), Academic Press 1968, p. 362. Cross-checked against Open Problem Garden page
  (openproblemgarden.org/op/do_any_three_longest_paths_...): statement matches the problem
  file — "any three longest paths in a connected graph have a common vertex?" (3-path case;
  the all-paths version was refuted by Walther 1969).
- Openness check: the only claimed proof found (arXiv:2006.16245, Sarkar) was **withdrawn by
  the author** (v3, May 2024). No 2025–2026 resolution found. Treated as open.

## 1. Attack framing (V1)

Mutate/hybridize hypotraceable and near-hypotraceable graphs; objective = the minimum over
triples of longest paths of |P1 ∩ P2 ∩ P3| ("t"), driven to 0 by simulated annealing over
graph mutations. t = 0 with three genuinely distinct longest paths = counterexample.

## 2. Seeds (all fetched from House of Graphs by id, stored in `seeds.jsonl`)

- HoG 1353 **Thomassen Graph 34** (smallest known hypotraceable graph, n=34, cubic-ish).
  Machine-verified hypotraceable by `core.is_hypotraceable` (61 s): no Ham path; G−v
  traceable for all 34 v.
- HoG 1435 **Zamfirescu Graph 36** (n=36).
- HoG 51493 **Van Cleemput–Zamfirescu Graph 13** (n=13, longest-path pathology seed).
- Petersen graph (piece factory for hybridization).

## 3. Machinery (this directory)

- `core.py` — bitmask longest-path enumerator (DFS + reachability-bound pruning),
  triple-intersection scorer, hypotraceability checker, connectivity utils.
- `search.py` — simulated-annealing mutation search. Moves: edge add/del, rewire,
  subdivide, pendant, smooth (deg-2 removal), vertex split (hub-breaking). Score =
  min-triple-intersection t (heuristic scan, exact for small path counts).
- `hybridize.py` — Thomassen-style hybrids: delete a cubic vertex from a
  hypohamiltonian/hypotraceable seed (3 stubs), take 2–4 pieces, wire stubs by random
  matchings (optionally via hub vertices), score hybrids; t ≤ 2 candidates are logged to
  `hybrids.jsonl` as annealing seeds.

Calibration measurements:
- Thomassen34: L = 33 vertices, 22 528 longest paths (14 s to enumerate), min triple
  intersection = **31** — as forced: in a hypotraceable graph every longest path misses
  exactly one vertex, so any 3 longest paths meet in ≥ n−3 vertices. Hypotraceable graphs
  themselves are maximally far from a 3-path counterexample; the value of the seeds is in
  their *pieces* and *mutations* (long-path rigidity), not the intact graphs.
- Random n≤16 graphs reach the trivial plateau t = 1 (e.g. spider-like graphs, three
  longest paths through one cut vertex) within a few hundred annealing steps. The entire
  difficulty is the 1 → 0 gap (this *is* the conjecture).

## 4. Runs

(checkpointed below as they complete)

- `rnd20`, `rnd26`, `rnd20b`: annealing from random connected seeds, n ≤ 20/26, 60
  restarts × 20 000 iters each.
- `vcz13`: annealing from Van Cleemput–Zamfirescu 13, n ≤ 22, 30 restarts × 20 000.
- `zam36`, `thom34`: annealing from the big hypotraceable seeds, 24 ≤ n ≤ 40, 10 restarts
  × 1 500 iters (expensive evals, capped at 30 000 stored paths / 3 M DFS nodes).
- `hybrid`: 5 000 random Thomassen-style hybrids of Petersen/VCZ13/Thomassen34 pieces,
  n ≤ 30.

## STATUS: (running)

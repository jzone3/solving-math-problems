# P04 V2 — Frontier push: exhaustive verification of Hajós' conjecture at n = 13 (→ 14)

Session: variant V2 of P04 (Hajós' conjecture, cycle-decomposition version).
Goal per problem file: extend the Heinrich–Natale–Streicher (HNS, arXiv:1705.08724)
exhaustive verification from n = 12 to n = 13 (and n = 14 if compute permits).

## 0. Statement re-verification & openness check (2026-07-22)

- Fetched the original source abstract (arXiv:1705.08724): "Hajós' conjecture states
  that an Eulerian graph of order n can be decomposed into at most (n-1)/2 edge-disjoint
  cycles. We ... verify Hajós' conjecture for all Eulerian graphs with up to twelve nodes."
  Matches problem file exactly (bound ⌊(n−1)/2⌋; this is the Lovász-1968-attributed cycle
  version, not topological-K5).
- Literature check (Exa search, July 2026): no proof or refutation found. Best general
  results remain asymptotic/dense (Girão–Granet–Kühn–Osthus; Montgomery et al. on
  Erdős–Gallai). Exhaustive verification frontier still n = 12. Problem still open.

## 1. Reduction: what must be enumerated at n = 13

Bound at n = 13: ⌊12/2⌋ = 6 cycles.

Let G be a counterexample of order 13 of minimum size (n ≤ 12 verified by HNS).
Facts used (each argued below, minimizing reliance on unverified literature):

(a) **G is 2-connected.** If G has a cutvertex (or is disconnected), its blocks B_i are
    even graphs of order n_i ≤ 12, so each decomposes into ≤ ⌊(n_i−1)/2⌋ cycles (HNS).
    Since Σ(n_i − 1) ≤ 12 over blocks, the total is ≤ ⌊12/2⌋ = 6. Contradiction.

(b) **G has no vertex of degree 2.** Let deg(v)=2, N(v)={x,y}.
    - If xy ∉ E(G): suppress v (G' = G − v + xy) — a simple even graph of order 12,
      decomposes into ≤ 5 cycles (HNS); re-expanding the cycle through xy gives ≤ 5
      cycles for G. Contradiction.
    - If xy ∈ E(G): remove triangle vxy; G' = G − v − {xy} is an even graph of order
      ≤ 12, decomposes into ≤ 5 cycles; plus the triangle gives ≤ 6. Contradiction.

(c) **G has at most one vertex of degree 4** (Fan–Xu / Granville–Moisiadis, as cited in
    HNS Theorem 2(i): a minimum counterexample has at most one node of degree 2 or 4).
    NOTE: we use this published lemma only to restrict the enumeration class; everything
    else is explicit computation.

So: G is 2-connected, all degrees even, and all vertices have degree ≥ 6 except at
most one vertex of degree exactly 4.

**Enumeration trick.** Delete from G the degree-4 vertex if present, else any vertex.
The result H = G − w is a connected (since G is 2-connected) graph on 12 vertices with
δ(H) ≥ 5 (every remaining vertex had degree ≥ 6 and lost ≤ 1). Conversely G is uniquely
recovered from H by adding a new vertex w joined to exactly the odd-degree vertices of H.
Hence: enumerating all connected 12-vertex graphs with δ ≥ 5 (nauty geng -c -d5 12) and
extending each by a new vertex on its odd-degree set covers **every** candidate G, up to
isomorphism (with harmless duplication ≤ 13×). Extensions with deg(w) = 0 are
disconnected (skip), deg(w) = 2 impossible by (b) — skip #odd(H) < 4; also skip
extensions that are not 2-connected, by (a).

## 2. Pipeline

`hajos_check.c` (this directory):
- reads graph6 H (n=12) from geng, filters #odd ≥ 4, builds G = H + w,
- checks 2-connectivity (brute-force vertex deletion + BFS, bitsets),
- randomized long-cycle peeling (HNS-style "random long cycle" heuristic), up to 300
  attempts, to find a decomposition into ≤ 6 edge-disjoint cycles,
- **every found decomposition is exactly re-verified** in `verify_decomposition`
  (partition of E(G) into vertex-simple cycles) — program aborts on any inconsistency,
- graphs where the heuristic fails within budget are emitted (graph6, n=13) as "hard"
  for exact ILP treatment.

Validation performed:
- decode/extend/filter logic cross-checked against an independent networkx
  implementation on a 5,880-graph geng sample: candidate sets identical (5,781/5,781).
- K13 (via H = K12): heuristic finds a 6-Hamiltonian-cycle decomposition (the extreme
  tight case m = 78 = 6·13) and it verifies.

Timing probes: geng -c -d5 12 shard r/4096 ≈ 1.4–2.9M graphs, ~4–7 s per shard single
core (geng + checker), 0 hard graphs in probes (res 0, 1, 1000, 2345, 4095; ~10M graphs
total). Estimated total class size ≈ 8–9 × 10^9 graphs; ≈ 7 core-hours; ~1 h on 8 cores.

## 3. Run log

### n = 13: COMPLETE — Hajós' conjecture VERIFIED for all Eulerian graphs of order ≤ 13

Full run: 4096 geng shards (`geng -c -d5 12 r/4096`), 8 cores, ~2.2 h wall.
Totals (per-shard details in `out13_summary.txt`):

- read (all connected 12-vertex graphs with δ ≥ 5): **8,573,140,092**
- candidate extensions G (13 vertices, even, 2-connected, ≤1 vertex of deg 4):
  **8,439,421,188**
- decomposed into ≤ 6 edge-disjoint cycles, decomposition machine-re-verified:
  **8,439,421,188 (100%)** — heuristic never failed (hard = 0, so the ILP fallback
  was never needed)
- skipped as not 2-connected: 1 graph (graph6 `LQhTQiiTTT^~TT`: even, connected,
  cutvertex 11, blocks of order 7+7 → ≤ 3+3 = 6 cycles by HNS n ≤ 12; legitimately
  excluded by the block argument (a)).

Non-candidates (read − candidates − 1 ≈ 133.7M) are the H with #odd(H) < 4
(deg(w) ∈ {0, 2}: disconnected or excluded by suppression argument (b)).

Together with HNS (n ≤ 12) and reductions (a),(b),(c) of §1 this proves:
**every Eulerian graph on at most 13 vertices decomposes into ≤ ⌊(n−1)/2⌋ cycles.**
This extends the exhaustive-verification frontier from n = 12 to n = 13.

Independent spot check: `second_verifier.py` (different decomposition method:
Eulerian-circuit splitting + exact ILP fallback, networkx-based independent graph6
decoding) run on random samples of shards — see `spot_result.txt`.

### n = 14: sharded run (in progress)

Bound at n = 14 is still ⌊13/2⌋ = 6. Class (see §1, adapted): H = geng -c -d5 13,
#odd(H) ≥ 2; #odd = 2 requires the odd pair adjacent (deg-2 vertex with non-adjacent
neighbours is excluded by suppression + n ≤ 13 now verified; the triangle case
survives since the bound does not grow from 13 to 14 — see hajos_check14.c).
Class size ≈ 1.2 × 10^12 graphs ≈ 850 core-hours → split into 1024 geng shards:
- residues 0–703: 11 child Devin sessions (64 shards each, K = 0..10), branches
  runs/P04-v2-child<K>; see CHILD_TASK.md. (5 further children hit the org's
  concurrent-session limit.)
- residues 704–1023: running locally (run14_local.sh).

### n = 14 child sessions (all 16 spawned; K → shards 64K..64K+63)

| K | session |
|---|---|
| 0 | devin-a9ffdf5b378d493c8479ba61f6139810 |
| 1 | devin-ee2421ae80914810a5959e166103b45a |
| 2 | devin-b86f587859454da9a5c30b34bec067db |
| 3 | devin-bda602e797b6425895fd61e8f8e71329 |
| 4 | devin-8814b637ddf544f988f2d0ff6283095a |
| 5 | devin-d297bbf88a3542cabbf6ccca4573bbb6 |
| 6 | devin-b12e39f8f18e44fda9ca4def8ccbb06b |
| 7 | devin-133d052ad48540f78ec5c98fb4734990 |
| 8 | devin-847adceec08b4b4b8884760bfd803526 |
| 9 | devin-b4721c039eee45f08228f53763a8d4c9 |
| 10 | devin-0d0aea1fe32f41da87e43e1c81908026 |
| 11 | devin-bec57fb535b240989fe7f0b86244f176 |
| 12 | devin-ce007eb6293148eb946647a93e7da1ce |
| 13 | devin-5aedb07075634375a216d9b4600a3168 |
| 14 | devin-49b5232960534fe6abdae94a0d2a334f |
| 15 | devin-b652ae58d3ca427cb47a900926de84a0 |

(K=14,15 spawned late after concurrency-limit retries; local run on 896–1023 kept
running in parallel as redundant cross-validation.)

### n = 14 checkpoint (parent session wrap-up, 2026-07-23 ~21:00 UTC)

Scale correction: the class `geng -c -d5 13` turned out ≈ 3–4× larger than the
mod-10^6 probes suggested — completed shards average ≈ 4.7 × 10^9 graphs each, so the
full class is ≈ 4.5–5 × 10^12 graphs ≈ 3,000+ core-hours. All 1024 shards are
assigned and running: 16 child sessions (8–16/64 shards done each at wrap-up, all
alive and checkpointing to their branches) + this machine (residues 896–1023,
16/128 done).

Local partial results (16 shards done, `out14_local_partial_summary.txt`):
- read 74,071,457,037; candidates 73,709,392,876; ok 73,709,392,832; hard 44;
  bicon_skip 0.
- 52 unique heuristic-hard order-14 graphs collected so far (incl. from running
  shards, `hard14_all_local.g6`); **all 52 verified SAT by the exact ILP**
  (`hard14_local_ilp_SAT.txt`) — each decomposes into ≤ 6 cycles. Zero
  counterexample candidates so far across ~2 × 10^11 graphs checked fleet-wide.

Hard graphs are overwhelmingly the near-extremal dense cases (m close to 6·13 = 78),
as expected since the bound does not grow from n = 13 to n = 14.

Fold-back procedure for the orchestrator: collect branches runs/P04-v2-child0..15
(each contains runs/P04/v2/child<K>/{log_*.txt, hard_*.g6, ilp_results.txt,
SUMMARY.md}), confirm every residue 0..1023 has a log with ok+hard = candidates and
every hard graph is ILP-SAT. If all shards complete with no UNSAT, Hajós' conjecture
is verified for all Eulerian graphs of order ≤ 14.

## STATUS

**STATUS: frontier-pushed.**
- n = 13: exhaustive verification COMPLETE — Hajós' conjecture holds for all Eulerian
  graphs of order ≤ 13 (previous frontier n = 12, HNS 2017). 8,439,421,188 candidate
  graphs, every decomposition found and machine-re-verified; independent
  second-verifier spot check PASS; no counterexample.
- n = 14: full enumeration (~4.5–5 × 10^12 graphs) in flight across 16 child sessions
  + local; ~20% done at parent wrap-up; 0 counterexample candidates so far (all
  heuristic-hard graphs proved decomposable by exact ILP).
- No witness claimed, hence no solutions/P04/verify.py; the negative-result
  verification chain is: hajos_check*.c internal exact re-verification + ILP
  (exact_min_decomp.py) + independent second_verifier.py spot checks.

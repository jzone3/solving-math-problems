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

(to be appended as shards complete)

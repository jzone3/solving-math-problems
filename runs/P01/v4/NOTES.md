# P01 Sheehan — V4 constraint-driven exhaustive generation

Session: https://app.devin.ai/sessions/92f2c8440e37424cb4c072fab3b61aa6
Variant: **V4** — exploit structure of minimum counterexamples to prune generation and push
the exhaustive frontier past the published limits.

## 0. Statement & openness re-verification (2026-07-22)

- Original source checked: Open Problem Garden `op/uniquely_hamiltonian_graphs` (Sheehan 1975,
  "The multiplicity of Hamiltonian circuits in a graph", Prague 1974 proceedings). Statement:
  no finite 4-regular **simple** graph is uniquely hamiltonian. Matches `problems/P01-sheehan.md`.
  OPG comment thread (2022) explicitly notes the Bondy/Häggkvist-style multigraph
  "counterexamples" (doi:10.1002/jgt.3190180503) have parallel edges and the simple-graph
  conjecture remains open.
- Literature sweep (Exa, July 2026): Goedgebeur–Jooken–Lo–Seamone–Zamfirescu, "Few hamiltonian
  cycles in graphs with one or two vertex degrees" (Math. Comp., 2023/24) still cites Sheehan
  as open; Brinkmann–De Pauw (DMTCS 2024) same. No solution found.
- Published exhaustive frontier (Goedgebeur–Meersman–Zamfirescu, "Graphs with few Hamiltonian
  Cycles", Math. Comp. 2020, arXiv:1812.05650, Observation 3.9):
  - Sheehan true for **all 4-regular graphs up to n = 21**;
  - true for 4-regular graphs of **girth ≥ 5 up to n = 26**.
  Their Table 3 gives min #HC among hamiltonian 4-regular graphs per order/girth
  (girth ≥3: 12,16,23,29,36,36,48,60,72,72,72,72,96,108,144,144,144 for n=5..21;
  girth ≥5, n=19..26: 2688,2716,3657,5589,8382,12412,18906,25299).
- Girão–Kittipassorn–Narayanan: second-cycle asymptotics ⇒ counterexample must be
  small-to-medium; every extra exhausted order genuinely shrinks the window.

## 1. Encoding (constraint-driven generation)

Every hamiltonian 4-regular graph on n vertices is, up to isomorphism, the cycle
C_n = (0,1,...,n-1) **plus a set of n chords forming a 2-regular graph** on the same vertex
set (chords ≠ cycle edges). So instead of generating all 4-regular graphs (genreg-style,
~2.9·10^13 connected 4-regular graphs at n=22) we do DFS over chord 2-factors with a
uniqueness-driven prune:

- **Second-HC prune (the workhorse):** after adding chord (v,u), search for a hamiltonian
  cycle through (v,u) in the current partial graph. Any HC ≠ base cycle survives in every
  supergraph, so the subtree dies. This is the same monotonicity idea as GMZ's 1H generator.
- **Rotation canonicity:** vertex 0 must carry the lexicographically minimal sorted
  chord-length pair (cycle distances, 2..n/2) among all vertices; any completed vertex with a
  smaller pair prunes. (Reflections not broken — only costs ≤2×, never correctness.)
- **Ordered chord choice** per vertex (partners increasing) removes intra-vertex duplicates.
- **Girth modes** `-g4`/`-g5`: forbid short chords and any new 3-/4-cycle at chord-insertion
  time (checks paths of length 2 and 3 between endpoints — complete since every cycle is
  detected when its last edge is inserted).
- HC existence test: bitmask DFS with per-node availability-degree pruning (every unvisited
  vertex needs ≥2 available neighbours; available-degree-2 neighbours of the head are forced
  moves). ~7× speedup over the naive DFS at n=15–16.
- `-mod M -res R` splits the DFS at the vertex-0 second-chord level (counter over
  (first,second)-chord pairs of vertex 0) for embarrassingly parallel runs; every worker
  enumerates the identical counter sequence, so residues partition the space exactly.
- Any leaf (all chords placed, no second HC ever seen) is re-verified inside the program by an
  independent exact HC count, and would then go through `solutions/P01/verify.py`.

Code: `search1h.c` (standalone C, no deps). Brute cross-checker: `brute_min_hc.py`.

## 2. Validation (all machine-verified)

- `-count` mode (pruning off, exact min #HC over all leaves) reproduces GMZ Table 3 girth≥3
  minima exactly for n=5..12: 12,16,23,29,36,36,48,60. ✔
- Independent Python brute force (`brute_min_hc.py`, different enumeration + different HC
  counter) agrees for n=8,9: min HC 29/36, zero uniquely hamiltonian graphs,
  2072/24692 labeled chord 2-factors. ✔
- Node counts invariant under the HC-search optimization (same tree, faster tests). ✔
- Full search leaves=0 for all n ≤ 17 girth≥3 (consistent with GMZ n≤21). ✔ (n=18/19 below)
- girth≥5 `-count` at n=19 targets GMZ's 2688 (Robertson graph order) — see log.

## 3. Runs & compute log

Machine: 8 cores, 31 GB RAM. Timings single-core unless noted.

| run | result | time |
|---|---|---|
| full n=8..17 | leaves=0 | ≤ ~90 s each |
| g5 n=19,21,23 | leaves=0 | 0.009 s / 0.44 s / 51 s |
| g5 n=24 | (running) | |
| g5 count n=19 | (running, expect min=2688) | |

Growth ≈ ×7–11 per vertex. Projections: full n=22 ≈ 2+ days on 8 cores (partial coverage
planned via mod-split); g5 n=26 ≈ 2–3 h on 8 cores (re-confirms GMZ), g5 n=27 ≈ ~1 day on
8 cores (**new frontier target**), g5 n=28 out of reach this session.

## 4. Status

STATUS: running

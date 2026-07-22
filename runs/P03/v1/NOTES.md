# P03 V1 — Direct counterexample search (Woodall's conjecture)

Session: https://app.devin.ai/sessions/d4cbcbc2be0d49e59cd58b01946b4d3d
Branch: runs/P03-v1

## Statement re-verification (done first)

Checked against Open Problem Garden ("Woodall's Conjecture", $5000 Cornuéjols prize),
Wikipedia, and Feofiloff's 2025 survey (ime.usp.br/~pf/dijoins): in every digraph, the
minimum size of a nonempty dicut equals the maximum number of pairwise disjoint dijoins.
Matches problems/P03-woodall-dijoins.md. Still open as of mid-2026: the June 2025
Combinatorica paper "Approximately Packing Dijoins via Nowhere-Zero Flows" (Abdi,
Cornuéjols, Liu, Ravi) proves only *approximate* packing (~ tau/6 dijoins) and states the
conjecture (even tau=3) is open. No claimed proof/counterexample found in a literature
sweep.

## Encoding / harness (runs/P03/v1/search.py)

- Digraphs as multiset of arcs on n labeled vertices (loops excluded; parallel arcs
  allowed in random modes — they simulate weights, cf. Schrijver's weighted CE).
- Dicuts: enumerate all 2^n-2 vertex subsets U with delta^-(U) = 0; dicut = delta^+(U).
  Keep inclusion-minimal dicuts only (others' constraints are implied). tau = min size.
  Skip graphs that are weakly disconnected or strongly connected (no dicut).
- KEY REDUCTION: dijoins are upward-closed (superset of a dijoin is a dijoin), so
  "tau pairwise disjoint dijoins exist" <=> "arc set partitions into tau dijoins".
- Packing test: SAT (CaDiCaL via pysat). Vars x[a,c] (arc a gets color c), exactly-one
  per arc; for every minimal dicut and every color c, clause OR_{a in cut} x[a,c].
  Symmetry breaking: the tau arcs of one fixed minimum dicut are pinned to distinct
  colors (valid: disjoint dijoins each use exactly one arc of a minimum dicut).
- UNSAT => counterexample. Sanity-checked on paths, parallel arcs, cycles.

## Searches run (checkpointed; all counts machine-generated, see *.log)

1. **Exhaustive, all labeled simple digraphs**, n = 3, 4, 5:
   - n=3: 36 instances with a dicut, all pack. n=4: 2228, all pack.
   - n=5: 462,000 instances with a dicut (tau up to 6), ALL pack. ~33 s.
2. **Exhaustive, all non-isomorphic digraphs on 6 vertices** (nauty-geng -c | directg,
   digraph6 stream, 1,530,843 digraphs, 6-way parallel): in progress / see below.
3. **Random multi-digraph sampling** (4 workers x 2 h): n in 4..9, m in 6..30 arcs
   i.i.d.; millions of instances, tau observed up to 17.
4. **Annealing on SAT hardness** (2 workers x 2 h): hill-climb at n=8, m<=~47 keeping
   tau>=3, score = CaDiCaL conflicts (hunt for hard/fragile packing instances).

## Near-misses / observations

- Zero UNSAT instances so far; virtually all instances pack with 0 SAT conflicts —
  packing constraints are extremely slack at these sizes (consistent with the
  literature: unweighted CE, if any, is expected to need special structure).
- SAT-hardness annealing mostly inflates tau via parallel arcs; conflicts stay tiny.

## STATUS (updated at end of run)

STATUS: running

# P04 — Hajós' Conjecture (cycle decompositions of Eulerian graphs)

**Statement.** Every simple Eulerian graph on n vertices decomposes into at most ⌊(n−1)/2⌋
edge-disjoint cycles. (Hajós, stated in Lovász 1968. NOT the topological-K5 Hajós conjecture.)

**Why it matters.** Eulerian analogue of Erdős–Gallai path decomposition; implies SCDC for
Eulerian graphs; active partial-results community (Fan–Xu; Girão–Granet–Kühn–Osthus O(n) bound).

**Status.** Proved for Δ ≤ 4, planar, projective-planar, K6-minor-free, pathwidth ≤ 6.
**Exhaustively verified only to n = 12** (Heinrich–Natale–Streicher, arXiv:1705.08724, 2017).
A minimum counterexample is 3-connected with δ ≥ 6 and constraints on degree-4 vertices
(Fuchs–Gellert–Heinrich) — strong pruning available.

**Witness & verifier.** An Eulerian graph whose minimum cycle decomposition exceeds ⌊(n−1)/2⌋.
Verify: minimum-cycle-decomposition ILP (edge-disjoint cycle cover, minimize count) — minutes
for n ≤ 20.

**Prompt variants:**
1. **V1 gap search**: generator of dense Eulerian graphs with δ ≥ 6 + annealing; score =
   ILP(min decomposition) − ⌊(n−1)/2⌋; column-generation ILP oracle for speed.
2. **V2 frontier push**: extend the 2017 exhaustive verification from n = 12 to n = 14 using
   their reduction lemmas + modern ILP/SAT — a publishable negative result on its own.
3. **V3 SAT encoding**: encode "Eulerian ∧ every cycle decomposition uses ≥ ⌊(n−1)/2⌋+1 cycles"
   via incremental SAT (enumerate-and-block decompositions is infeasible; instead bound cycle
   count by cardinality constraints on a cycle-selection encoding) at n = 13–16.
4. **V4 extremal families**: analyze families achieving the bound with equality (K_{2k+1},
   triangle-dense graphs); perturb tight instances (vertex splits, edge complementation on
   Eulerian-parity-preserving sets) hunting instances exceeding the bound.
5. **V5 literature-first**: digest Fuchs–Gellert–Heinrich structural lemmas on minimum
   counterexamples and the Girão et al. asymptotic proof; identify the size window where neither
   applies; search there specifically.

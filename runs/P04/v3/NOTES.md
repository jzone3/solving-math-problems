# P04 V3 run notes — SAT encoding attack on Hajós' cycle-decomposition conjecture

Session: https://app.devin.ai/sessions/38bad722a5aa466695abfbf7e6bb63d5
Branch: `runs/P04-v3` (off `devin/1784749757-context-plan`)

## 0. Statement re-verification and openness check (2026-07-22)

- Original source check: arXiv:1705.08724 (Heinrich–Natale–Streicher) abstract states
  exactly the problem-file statement: "Hajós' conjecture states that an Eulerian graph of
  order n can be decomposed into at most (n-1)/2 edge-disjoint cycles", attributed via
  Lovász 1968 ("On covering of graphs"). Matches `problems/P04-hajos-cycle-decomposition.md`.
  (This is the cycle-decomposition Hajós, NOT the topological-K5 one.) ✔
- Openness: Exa + arXiv sweep (July 2026) found no proof/disproof. Newest adjacent work is
  on Gallai path decompositions of Eulerian graphs (arXiv:2510.12806, Oct 2025) and the
  Erdős–Gallai cycle decomposition line (Montgomery et al., arXiv:2211.07689); neither
  claims Hajós. Exhaustive verification still stands at n ≤ 12 (arXiv:1705.08724). ✔

## 1. Encoding (the V3 core)

Deciding "G decomposes into ≤ k edge-disjoint cycles" as SAT (`sat_decider.py`):

- Variables `x[e][c]`, e ∈ E(G), c ∈ {0..k−1}: edge e assigned to cycle-slot c.
  Exactly-one color per edge (pairwise AMO).
- Per vertex v and color c: #(c-colored edges at v) ∈ {0, 2}:
  sequential-counter AtMost-2 + "not exactly one" clauses
  (x[e][c] → ∨_{e'∋v, e'≠e} x[e'][c]). ⇒ each color class is a disjoint union of cycles.
- Single-cycle-per-class via connectivity: support vars `r[c][v]` (v touches class c,
  both implication directions), root = minimum-index support vertex, BFS-level ladder
  `a[c][v][d]` (d ≤ n−1) with justification clauses
  a[c][v][d] → a[c][v][d−1] ∨ ∃u∼v (x[uv][c] ∧ a[c][u][d−1]) (aux y-vars),
  and the hard constraint r[c][v] → a[c][v][n−1].
- Symmetry breaking between interchangeable color classes: edge i restricted to colors
  ≤ i, and x[e_i][c] → ∨_{j<i} x[e_j][c−1] (first edge of color c after first of c−1).
- Solver: CaDiCaL 1.5.3 via python-sat.

G is a Hajós counterexample ⇔ formula UNSAT at k = ⌊(n−1)/2⌋.
(Enumerate-and-block over decompositions is infeasible, per the problem file; this
cardinality-free "cycle-slot" encoding bounds the cycle count structurally.)

## 2. Validation of the decider

`crosscheck.py` (log: `crosscheck.log`):
- K5/K7/K9: SAT-min = 2/3/4 = ⌊(n−1)/2⌋, matches independent brute-force
  branch-and-bound (`brute_min_decomp.py`, exhaustive cycle enumeration) for K5, K7.
- 30 random Eulerian graphs (n=5..9, m≤22): SAT-min == brute-force-min on all 30;
  every SAT model's coloring independently re-verified (each class 2-regular + connected)
  with networkx. ALL CROSSCHECKS PASS.

Timing: K13 at k=6 SAT 0.3 s, k=5 UNSAT 0.1 s; K15 k=7 SAT 1.2 s, k=6 UNSAT 0.2 s.
Random dense n=13 candidates ≈ 0.1 s/graph.

## 3. Search campaigns (n = 13–16)

Decision per candidate: SAT at k = ⌊(n−1)/2⌋ (UNSAT ⇒ counterexample). Periodically also
test k−1 to detect TIGHT graphs (min = bound), which are recycled as perturbation seeds.

Pools (biased toward min-counterexample structure: connected, all degrees even, δ ≥ 6,
dense — Fuchs–Gellert–Heinrich pruning):
- `random`: G(n,p) with p ~ U(0.55, 0.95), odd-degree vertices paired and toggled, δ≥6
  filter. 20000 graphs at n=13,14; 10000 at n=15,16.
- `circulant`: ALL connected Eulerian circulants C_n(S) at n=13..16 (exhaustive over
  connection sets).
- `perturb-tight`: random walks from K_n and discovered TIGHT graphs by toggling
  edge sets of 3–6-cycles of the ambient K_n (parity-preserving), re-testing each step.

(Results appended below as campaigns finish.)

## STATUS: (running)

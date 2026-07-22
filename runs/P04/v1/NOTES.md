# P04 V1 — Direct counterexample gap search (annealed)

Session: https://app.devin.ai/sessions/2dceb8f9358d4f9da583e6848c6e06ff
Variant: **V1 gap search** — generator of dense Eulerian graphs with δ ≥ 6 + simulated
annealing; candidate detection by heuristic min-decomposition upper bound; exact
arbitration by CP-SAT.

## Statement re-verification (before deep work)

- Problem: every simple Eulerian (connected, all degrees even) graph on n vertices
  decomposes into at most ⌊(n−1)/2⌋ edge-disjoint cycles (Hajós, per Lovász 1968).
  Confirmed this is the *cycle-decomposition* Hajós conjecture, not the topological-K5 one.
- Checked arXiv:1705.08724 (Heinrich–Natale–Streicher, "Hajós' cycle conjecture for small
  graphs") — title/abstract confirms exhaustive verification to n = 12 and the statement
  as given in problems/P04-hajos-cycle-decomposition.md.
- Quick literature scan (Exa + arXiv API, 2026-07-22): no resolution found; latest
  relevant results remain partial (pathwidth-6 2019, Girão–Granet–Kühn–Osthus dense/
  asymptotic bounds 2021, Erdős–Gallai progress by Bucić–Montgomery). Treating as OPEN.

## Encoding / tooling

- `exact.py` — exact decision "G decomposes into ≤ k cycles" via OR-Tools CP-SAT:
  k `AddCircuit` slots over all n vertices with optional self-loops (self-loop = vertex
  skipped); edge {u,v} covered iff arc (u,v) or (v,u) chosen in exactly one slot.
  Empty slots allowed ⇒ feasibility(k) ⇔ min decomposition ≤ k.
  Symmetry breaking: slot-used monotone chain + strictly increasing min-edge-index per slot.
  **Sanity check passed**: K7 feasible at k=3, INFEASIBLE at k=2 (K7 is tight: (7−1)/2=3).
- `search.py` — simulated annealing over simple connected Eulerian graphs with δ ≥ 6
  (minimum-counterexample constraints, Fuchs–Gellert–Heinrich).
  - State space moves: toggle the 3 (or 4) edges of a random triangle/C4 in K_n —
    preserves all-even parity; reject if δ < 6 or disconnected.
  - Score (to maximize): heuristic min-decomposition **upper bound** =
    min over restarts of (a) random-Euler-circuit stack-splitting, (b) greedy peel of
    long cycles (randomized Pósa-rotation longest-cycle, remove, repeat).
    Anneal objective = min + 0.02·avg (avg is a hardness tie-break on the plateau).
  - Candidate: quick-restart min > k = ⌊(n−1)/2⌋ → re-test with 400 deep restarts →
    if still > k, exact CP-SAT decision at k (600 s limit). INFEASIBLE ⇒ counterexample.

Lesson learned early: Euler-split alone is a very weak upper bound on dense graphs
(constantly 7–9 at n=13 where true min ≤ 6 — dozens of false candidates, all exact-refuted
FEASIBLE in seconds). Adding the greedy long-cycle peel collapses the false-positive rate
to ~0: the heuristic then sits exactly on the k plateau.

## Runs

(checkpointed below as they complete)

### Pilot runs (2026-07-22)
- n=13, 60 s, weak heuristic: ~340 candidates, **all exact-checked FEASIBLE at k=6** —
  i.e. hundreds of distinct dense δ≥6 Eulerian 13-vertex graphs each decompose into ≤ 6
  cycles. No near-miss.
- n=13, 60 s, strong heuristic: 12 975 anneal iterations, heuristic best = 6 = k (never
  exceeded the bound).
- n=15, 80 s: 8 270 iterations, heuristic best = 7 = k.

## STATUS

STATUS: running (long runs in progress; will update)

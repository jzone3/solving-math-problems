# P01 Sheehan — V1 child-struct (structure-targeted constrained-family search)

Session: https://app.devin.ai/sessions/38bd1cad166d43c3b79a62e85987044c
Parent: runs/P01/v1 (branch runs/P01-v1); this work: branch runs/P01-v1-struct
Date: 2026-07-23

## Task

Search over CONSTRAINED families the parent's generic anneal did not target:
(a) 4-regular girth >= 5, (b) 4-regular 4-connected — minimize exact #HC at
n = 20..40. Anything below the parent's 144 floor (n >= 19) would be a record;
count 1 solves Sheehan.

## Tooling (searchstruct.c, reuses ../fastlib.c bitmask exact HC counter)

- Same 2-opt regularity-preserving move set + Metropolis anneal + basin-hopping
  as ../search5.c, with a **family penalty** added to the objective
  (strict per-move constraint enforcement was tried first and stalls: the
  constrained space is nearly disconnected under 2-opt at small n):
  - girth: 0.25 * (10*#triangles + #C4-pairs) — smooth, 0 iff girth >= 5;
  - 4-connectivity: +3.0 iff some cutset of size <= 3 exists.
  Best-ever is only updated at penalty 0 (i.e. genuinely inside the family).
- 4-connectivity checked by brute force over all <= 3-subsets with bitmask BFS
  (obviously correct; ~1 ms at n = 30). Girth by per-vertex truncated BFS.
- Constraint checks cross-validated against networkx (`node_connectivity`,
  girth) on the Robertson graph (girth 5, conn 4) and the parent's g22.txt
  (girth 3, conn 2): agree.
- `g6min` mode: stream graph6 (geng output), exact-count each 4-regular graph,
  track the argmin — used for EXHAUSTIVE small-n scans.
- Seeds: `nauty-geng -c -t -f -d4 -D4 n 2n:2n` = all connected 4-regular
  girth->=5 graphs (the caagt.ugent.be/uhg GenerateUHG download needs nauty
  sources to build; geng gives the same girth-5 quartic family directly, and
  HoG's meta-directory is JS-only — geng route used instead).

## Exhaustive results, family (a) girth >= 5 (complete geng enumeration)

| n  | #girth-5 quartic graphs | min #HC | notes |
|----|------------------------|---------|-------|
| 19 | 1 (Robertson graph)    | 2688    | conn4 |
| 20 | 2                      | 2716    | conn4 |
| 21 | 8                      | 3657    | conn4 |
| 22 | 131                    | 5589    | all minima seen were 4-connected |

These are EXACT constrained minima (every graph in the family counted).
Striking: the girth-5 minima are 20-40x ABOVE the unconstrained minimum 144 and
INCREASE with n — high girth forces MANY Hamiltonian cycles in the 4-regular
setting, the opposite direction from a Sheehan counterexample. (The GMZ
few-HC/high-girth phenomenon lives in min-degree-3 graphs, not 4-regular ones;
the 4-regular few-HC extremal graphs are girth-3, connectivity-2 — exactly what
the parent's anneal converged to.)

## Anneal results (3.5 h x 7 workers, penalty method, exact counts)

(to be filled in when workers finish)

## STATUS: (pending)

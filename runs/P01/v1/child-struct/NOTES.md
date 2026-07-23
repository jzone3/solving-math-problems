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
| 23 | 3917                   | 8382    | argmin 4-connected |

These are EXACT constrained minima (every graph in the family counted;
argmin edge lists in exhaustive-girth5-argmin-n{22,23}.txt, full n=22 family
in girth5-n22-all.g6; geng n=23 took ~2.5 h, n=24 was out of reach).
Striking: the girth-5 minima are 20-40x ABOVE the unconstrained minimum 144 and
INCREASE with n — high girth forces MANY Hamiltonian cycles in the 4-regular
setting, the opposite direction from a Sheehan counterexample. (The GMZ
few-HC/high-girth phenomenon lives in min-degree-3 graphs, not 4-regular ones;
the 4-regular few-HC extremal graphs are girth-3, connectivity-2 — exactly what
the parent's anneal converged to.)

## Anneal results (3.5 h x 7 workers, penalty method, exact counts)

Best-ever recorded only at penalty 0 (graph verified inside the family);
final bests re-verified with TWO independent counters: ../verify_nearmiss.py
(iterative Python, n <= 26 — all PASS) and the parent's independently written
weighted counter msearch.c `count` (n = 28, 30 — both match).

| n  | family        | min #HC found | anneal iters | graph file |
|----|---------------|---------------|--------------|------------|
| 24 | girth >= 5    | 12968         | 155,352      | best-f1-n24.txt |
| 25 | girth >= 5    | 20423         | 110,183      | best-f1-n25.txt |
| 28 | girth >= 5    | 67350         | 19,799       | best-f1-n28.txt |
| 32 | girth >= 5    | (>= 200000 = cap; no gradient, aborted) | — | — |
| 22 | 4-connected   | 1512          | 1,394,190    | best-f2-n22.txt |
| 26 | 4-connected   | 4896          | 161,864      | best-f2-n26.txt |
| 30 | 4-connected   | 40708         | 11,723       | best-f2-n30.txt |
| 24 | girth5 + 4conn| 12968         | 187,918      | best-f3-n24.txt |

- The n=24 girth-5 anneal best (12968) equals the girth5+4-connected best and
  is 4-connected — consistent with the exhaustive data where every girth-5
  few-HC argmin is automatically 4-connected.
- The n=32 girth-5 run is a logged dead end: random girth-5 graphs at n=32
  have > 200000 HCs, so the capped objective was flat and never descended
  (same failure mode as the parent's Batch-1; not worth pursuing given the
  monotone-increasing exact minima at n = 19..23).
- 4-connected minima also blow up fast (1512 @ 22 -> 40708 @ 30), an order of
  magnitude above the unconstrained 144 floor already at n = 22 — matching
  Haythorpe/GMZ: few-HC extremal 4-regular graphs have connectivity 2.

## Conclusion

Neither constrained family contains few-HC graphs: both girth >= 5 and
4-connectivity push #HC far ABOVE the unconstrained 144 floor and the minima
grow with n. Nothing below 144 for n >= 19 was found (nothing below 1512 in
these families, and the girth-5 minima for n <= 23 are EXACT, 2688..8382);
no uniquely Hamiltonian candidate, no new record. Structure-targeting in these
directions is anti-productive for Sheehan: counterexample hunting should stay
in the low-connectivity girth-3 regime the parent already floors at 144.
The exhaustive girth-5 constrained minima (n = 19..23) appear to be new data
not in GMZ (their tables cover all 4-regular graphs, not the girth-5 slice).

## STATUS: negative (no counterexample, no sub-144 record; exact girth-5
   constrained minima computed for n = 19..23 [2688, 2716, 3657, 5589, 8382,
   monotone increasing], anneal floors girth-5 @ n=24/25/28 and 4-connected
   @ n=22/26/30 all >= 1512 >> 144; both constrained families are HC-rich —
   independent double verification passed on every reported minimum)

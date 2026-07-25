## Phase 3 reduced-universe scope

The phase-3 core search extracts an induced subgraph of `wt_r3.pkl` and
certifies each iteration with Kissat plus drat-trim.  The current materialized
universe is `wt_r3_core5751.pkl`: 5,751 vertices and 46,732 induced edges.
Its independent check is recorded in `logs/core5751_check.log` and ends with
`s VERIFIED`.

**All phase-3 hitting-set, hyperedge, LP, and infeasibility conclusions are
scoped only to this 5,751-vertex reduced universe.  They do not establish
the corresponding claim for the full 27,265-vertex `wt_r3.pkl` universe or
for the original 77,485-vertex construction.  Banks from different
universes must never be mixed.**

The old full-universe bank had 320 hyperedges of sizes 8,472--9,090
(median 8,878), approximately 31% of the universe, and was rejected as
search-quality input.  On `wt_r3_core5751.pkl`, the maximum-colourable
subset optimizer is warm-started by the sound tabu colouring path and uses
CP-SAT to improve the retained coloured subset.  A quality gate rejects
`|D| > 5%|U|`; rejected attempts are logged but not banked.

The initial reduced-universe optimizer bank accepted 14 diverse hyperedges:
sizes 107--287, median 218 (8 attempts were rejected at sizes 289--437).
The CEGAR run then added 13 sound fallback hyperedges, yielding a final bank
of 27 with sizes 107--382, median 234.  Eight independent Kissat checks of
the final bank all returned SAT for `U \ D`.

The fractional LP bound of the final 27-clause bank was 3.75, far below 509.
This confirms that the bank remains too small to support a meaningful
near-509 lower bound.

The reduced-universe outer trajectory reached a 9-vertex incumbent.  One
iteration was `OPTIMAL` with CP-SAT bound 9; subsequent CEGAR iterations were
time-limited (`FEASIBLE`) with bounds 6--8 and incumbents 9--12.  No 508, 450,
or 400 infeasibility claim is made: those bounds are irrelevant to this
5,751-vertex scoped run and were not proven by the partial bank.
# P23 hitset16 phase 2 notes

## Soundness invariant

For every banked set `D`, the generator retains a four-colouring of every
vertex in the complete universe and asserts both coverage and
`colour[u] != colour[v]` for every edge whose two endpoints are outside `D`.
Thus `D` is a genuine whole-universe hyperedge: `U \ D` is four-colourable.
The CEGAR driver repeats the same assertion immediately before adding every
outer clause. It also independently asks Kissat to colour random bank
complements periodically.

The outer selection `S` is coloured first. Tabu then colours `U \ S`; the
resulting conflict vertex cover `D` is contained in `U \ S`, so the new clause
is disjoint from the current selection and soundly excludes it.

## Minimum-degree-4 strengthening

A minimum non-4-colourable induced subgraph can be assumed vertex-critical.
If one of its vertices has induced degree at most three, colour the remaining
graph first and assign that vertex a colour not used by its at most three
neighbours. Removing it would preserve non-4-colourability, contradicting
minimality. Consequently every selected vertex in a minimum witness has at
least four selected universe-neighbours. The CP-SAT outer model encodes this
condition. Any infeasibility statement is scoped to the current bank and
support-restricted outer model; it becomes a complete universe negative only
after the CEGAR loop has generated no further hyperedge for the relevant
returned selections.

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

# P20 — Grünbaum's problem: 4-regular 4-chromatic graph of girth ≥ 6

**Statement.** Does there exist a 4-regular graph with chromatic number ≥ 4 and girth ≥ 6?
(The surviving small case of Grünbaum's 1970 conjecture; the asymptotic form died with Johansson's
O(Δ/log Δ) bound.) Source: Grünbaum, Amer. Math. Monthly 77 (1970) 1088–1092; Open Problem Garden
"high girth low degree 4 chromatic graphs". VERIFY the exact quantifiers against the original.

**Why it matters.** The girth-5 examples (Chvátal graph, Grünbaum graph, Brinkmann graph) are famous
named small graphs; the first girth-6 example would join them. A "no example with ≤ N vertices"
exhaustive result is also a citable frontier.

**Witness.** One graph: 4-regularity + girth ≥ 6 are trivial checks; χ ≥ 4 is certified by a DRAT
UNSAT proof of 3-colorability — fully machine-verifiable and a clean Lean/`decide` target for a
small witness.

**Attack.** (a) genreg/geng generation of 4-regular girth-6 graphs by increasing n with incremental
3-colorability filtering; (b) structured candidates: Cayley graphs, vertex-transitive census
(4-valent girth-6 starts ~26 vertices), incidence-geometry constructions, generalized-Petersen-like
graphs; (c) annealing on fractional chromatic number over the girth-6 4-regular space. Prior compute:
only the girth-5 minimal-graph enumeration (MOLGEN) — girth 6 is virgin.

**Priority.** Widened check (GitHub/Zenodo/OpenReview + MathWorld/OPG + 2024–26 papers) per
context/METHODOLOGY.md before claiming.

Obs 4 / Tract 4 / Headline 4.

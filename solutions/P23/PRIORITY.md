# P23 — Priority check & current-record pin (Hadwiger–Nelson, smaller 5-chromatic UDG)

Session: https://app.devin.ai/sessions/8c6eba9abd204ecf9e216e61f6b8dbe4
Date: 2026-07-23.

## STEP 0 result — the current world record is UNCHANGED: 509 vertices (Jaan Parts, 2020)

**Record: a 5-chromatic unit-distance graph on 509 vertices and 2442 edges**, discovered by
Jaan Parts, "Graph minimization, focusing on the example of 5-chromatic unit-distance graphs
in the plane", *Geombinatorics* **XXIX** no. 4 (2020) 137–166 (arXiv:2010.12665). The graph
arose from the Polymath16 project (the collaborative follow-up to de Grey's 2018 proof that
χ(plane) ≥ 5, arXiv:1804.02385).

Chain of records for the smallest known 5-chromatic UDG (all "M-type"):
| vertices | edges | who / when |
|---|---|---|
| 1581 | — | de Grey 2018 (original) |
| 1585 → 826 → 803 → 633 → 610 | — | Polymath16 shrinking, 2018 |
| 553 | 2840 | Heule / Parts, Jul 2019 (Heule arXiv:1805.12181 gave 553) |
| 529 | 2630 | Parts, Jul 2019 |
| 525 | 2605 | Parts, Jul 2019 |
| 510 | 2508 → 2502 | Parts / Heule, Aug 2019 – Mar 2020 |
| **509** | **2442** | **Parts, before Mar 2020 — CURRENT RECORD** |

Lower bound: every 5-chromatic UDG has **≥ 26 vertices** (de Grey & Parts,
"On lower bounds of the order of k-chromatic unit distance graphs", arXiv:2303.14714, 2023).
So the true minimum lies in [26, 509]; the gap is wide and 509 is the standing upper record.

## Priority search performed (2026-07-23), scope beyond published literature

Per METHODOLOGY §"MANDATORY scope beyond the published literature", I searched arXiv, the
Polymath16 wiki + all blog threads, GitHub, Zenodo, and general web:

- **MathWorld "Parts Graphs"** (updated, cites Soifer 2024): lists exactly the record chain
  above; 509/2442 is the smallest. No smaller graph listed.
- **Soifer, *The New Mathematical Coloring Book*, 2nd ed. (Springer, 2024), Ch. 56
  "Jaan Parts' Current World Record"** — a 2024 book chapter still titled *Current* World
  Record for the 509 graph. Strong evidence the record was unbeaten as of 2024.
- **arXiv full-text / listing sweep** (chromatic number of the plane; 5-chromatic
  unit-distance; k-chromatic UDG order) through 2026: later works are about *lower* bounds
  (arXiv:2303.14714 ≥26), spheres/hyperbolic variants (Exoo–Ismailescu 2023; Voronov 2022),
  two-distance 6-chromatic graphs (Parts 2020b, arXiv:2010.12656, 31 vertices — different
  problem), and the Erdős unit-distance-*count* problem (Alexeev–Mixon–Parshall 2024). **None
  improves the 509 plane record.**
- **GitHub**: `vsvor/dist-graphs` (Voronov, R²/S² search — S² and larger-plane graphs, none
  < 509 in the plane), `vasnesterov/HadwigerNelson` (Lean formalization tooling for
  4-colorability, not a smaller graph), `pmckenne/chromatic` (MCTS for *3*-chromatic, 2026 —
  different regime). No repo claims a < 509 plane graph.
- **Zenodo / OpenReview / general web**: no artifact claiming a smaller-than-509 5-chromatic
  unit-distance graph in the plane.

**Conclusion:** as of 2026-07-23 the record to beat is **509 vertices, 2442 edges** (Parts
2020). No public improvement found. Residual risk: Geombinatorics is not fully open-access
and a very recent unpublished improvement cannot be fully excluded, but the 2024 Soifer book
chapter labelling it the *current* record makes this unlikely.

## Data / tooling obtained (STEP 1)

- All 43 of Parts' graphs (the record 509 plus its L/S subgraphs and mono/non-mono families)
  were downloaded from the **Polymath16 dropbox** folder Parts posted in the 15th research
  thread (`.../JP/Large`, `graphs.txt` index). Exact Mathematica-format coordinates.
- SAT solver **kissat** (built from source) + **drat-trim** for certified UNSAT; **sympy**
  for exact algebraic-number arithmetic.

# P23 — Smaller 5-chromatic unit-distance graphs (Hadwiger–Nelson)

**Statement.** The chromatic number of the plane satisfies 5 ≤ χ ≤ 7 (de Grey 2018,
arXiv:1804.02385). The smallest known 5-chromatic unit-distance graph has **509 vertices**
(Jaan Parts, "Graph minimization, focusing on the example of 5-chromatic unit-distance graphs",
Geombinatorics XXIX (2020); via Polymath16). Target: a smaller 5-chromatic UDG — or, stretch
goal, any 6-chromatic UDG (which would be a major result).

**Approach.** Polymath16 tooling is public (Parts' reduction methods, SAT-based 4-colorability
checks with exact algebraic coordinates over ℚ(√3,√11,...)). Attack: new spindle/Minkowski-sum
constructions + SAT minimization with exact arithmetic verification of unit distances.

**Verification gate:** vertices must have EXACT algebraic coordinates (no floating point);
unit distances verified in exact arithmetic; non-4-colorability by DRAT-certified UNSAT;
independent verifier script; widened priority check (Polymath16 threads, Parts' later papers,
arXiv, GitHub/Zenodo) — the 509 record may have been improved; pin the current record first.
Lean: 4-colorability UNSAT via LRAT replay; exact-distance arithmetic feasible with norm_num
extensions.

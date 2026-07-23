# P21 — Hoffman–Singleton decomposition of K₅₀

**Statement.** Does K₅₀ decompose into 7 edge-disjoint copies of the Hoffman–Singleton graph?
(HoSi = unique (7,5)-cage: 7-regular, girth 5, 50 vertices, 175 edges; 7·175 = C(50,2) = 1225.)
Source: Douglas West's open problem pages, dwest.web.illinois.edu/openp/hoffsing.html. VERIFY the
statement there and the best-known partial result.

**Why it matters.** The analogue for K₁₆ into 3 Clebsch graphs is a Ramsey-theory gem. Best known:
**5** edge-disjoint HoSi copies in K₅₀ (Meszka–Šiagiová, J. Combin. Des. 2003) — even a 6th copy is
a new record and a publishable frontier push.

**Witness.** 7 edge lists (or 7 permutations of a fixed HoSi copy). Verifier: each copy 7-regular
with girth 5 (forces HoSi), union partitions E(K₅₀). Milliseconds; trivially Lean-checkable
(`decide` on a finite structure, or BFS certificates).

**Attack.** Prescribed-automorphism search: assume the decomposition is invariant under a subgroup
of Aut(HoSi) = PSU(3,5):2 (order 252000) — orders 5, 7, 25 are natural; this collapses the search
to a small exact-cover/SAT instance. Also voltage-graph liftings extending Meszka–Šiagiová.
Intermediate deliverable: 6 disjoint copies (beat the 2003 record). Nonexistence is out of reach —
treat purely as a construction hunt.

**Priority.** Widened check (GitHub/Zenodo/OpenReview + design-theory literature 2003–2026) per
context/METHODOLOGY.md.

Obs 4 / Tract 3 / Headline 5 (textbook-worthy if it exists).

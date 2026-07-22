# P12 — Tuscan-2 Squares T2(11) and T2(13)

**Statement.** Does an n×n array (n = 11, 13) exist, each row a permutation of n symbols, such
that every ordered pair (a,b) appears with b immediately right of a in exactly one row, and with
b two steps right of a in at most one row? (Golomb–Taylor 1985, IEEE Trans. IT; Handbook of
Combinatorial Designs ch. VI.62; open instances per CPro1 repo tuscan-2-square/problem_def.py.)

**Why it matters.** Tuscan-k squares interpolate between row-complete Latin squares and Vatican
squares; sequencing designs for interference-free communication. Open since 1985 at size 11×11.

**Status.** The whole design type resisted CPro1 (LLM-generated heuristics × 48h, both 2025
papers). No complete-search (SAT/exhaustive) attack on record despite the tiny size.

**Witness & verifier.** An 11×11 (or 13×13) array; verification is O(n³), instant.
Nonexistence for n = 11 may be exhaustible — either outcome closes a 40-year-old cell.

**Prompt variants:**
1. **V1 SAT**: direct SAT encoding (adjacency-pair exactly-once = exact cover; 2-step at-most-once);
   fix row 1 = identity; row-permutation symmetry breaking; run modern solvers (kissat/cadical)
   long on T2(11).
2. **V2 exhaustive DFS**: row-by-row backtracking with pair-availability pruning and isomorph
   rejection (column rotation classes); estimate and, if feasible, exhaust T2(11) completely.
3. **V3 algebraic**: T2(n) exists when n+1 is prime (Vatican); try near-field / relative
   difference set / terrace-based constructions for n = 11, 13 (Bailey's terraces, Z_11 directed
   terraces); LLM-guided algebraic pattern search.
4. **V4 CP/hybrid**: OR-Tools CP-SAT model + large-neighborhood search; anneal on near-solutions
   (minimize violated pair constraints), seed SAT with high-quality partials.
5. **V5 literature + reformulation**: verify the exact definition against Golomb–Taylor 1985 and
   the Handbook (avoid paraphrase drift); reformulate as edge-decomposition of a doubled complete
   digraph into Hamiltonian paths with constraints; try known path-decomposition machinery.

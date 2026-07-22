# P13 — Perfect Mendelsohn Designs with Block Size 6

**Statement.** A (v,k)-PMD is a set of cyclically ordered k-tuples of a v-set such that every
ordered pair (x,y) appears at cyclic distance i in exactly one block, for every i = 1..k−1.
Open: k = 6 with v ∈ {9, 10, 12, 15, 16, 18} (and k = 7 with v ∈ {14, 15}).
(Handbook ch. VI.35; CPro1 repo perfect-mendelsohn-design/problem_def.py.)

**Why it matters.** The k = 5 spectrum was completed only in 2020 (Griggs–Kozlik, J. Combin.
Des. 28) — the community actively closes these tables; k = 6 is the live frontier.

**Status.** Whole type resisted CPro1's heuristics. (9,6)-PMD has only v(v−1)/k = 12 blocks —
possibly fully exhaustible; no complete-search records found.

**Witness & verifier.** A b×6 array of cyclic blocks; verification trivial.

**Prompt variants:**
1. **V1 SAT smallest-first**: encode (9,6)-PMD (12 blocks, 72 cells) in SAT with block and
   symbol symmetry breaking; aim for full resolution (SAT model or UNSAT proof with DRAT).
2. **V2 prescribed automorphisms**: assume cyclic/rotational automorphism group (Z_v or Z_{v−1}
   with fixed point); search base blocks only (difference-method); classic and never applied here
   by generic heuristics; sweep all v in the open list.
3. **V3 CP + LNS**: CP-SAT model over all open v; large-neighborhood search; seed from partial
   designs; escalate the smallest unresolved v to complete search.
4. **V4 exhaustive backtracking**: orderly generation of (9,6) and (10,6) with canonical-form
   pruning (nauty on the block-incidence structure); settle existence either way.
5. **V5 recursive constructions**: PMD product/filling constructions from the literature (Zhang,
   Bennett, Zhu et al. surveys); check whether any open v is reachable from known PMDs via
   standard recursions the tables may have missed; verify candidates exactly.

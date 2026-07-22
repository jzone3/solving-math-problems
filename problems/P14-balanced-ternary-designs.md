# P14 — Balanced Ternary Designs: 4 surviving open instances

**Statement.** Does a BTD(V,B; ρ1,ρ2,R; K,Λ) exist for
(14,18; 7,1,9; 7,4), (12,15; 6,2,10; 8,6), (12,20; 4,3,10; 6,4), (14,28; 8,3,14; 7,6)?
(V elements, B blocks of size K with element multiplicities ≤ 2; each element in ρ1 blocks once
and ρ2 blocks twice; every unordered pair covered Λ times.)
(Handbook ch. VI.2; CPro1 repo balanced-ternary-design instances; Greig 2002 progress notes.)

**Why it matters.** Standing Handbook table cells; 7 sibling instances fell quickly to CPro1's
LLM heuristics in 2025, and one was proved nonexistent (Greig) — these 4 are the survivors.

**Status.** First three survived CPro1 (48h × top heuristics × 2 papers); (14,28;…) apparently
never attempted. **Nobody appears to have ever run a MIP solver on these.**

**Witness & verifier.** A V×B matrix over {0,1,2}; verify row/column sums and pairwise
inner-product conditions. Instant.

**Prompt variants:**
1. **V1 ILP**: exact integer program (expand multiplicity indicators; all constraints linear);
   Gurobi-free stack: OR-Tools CP-SAT / HiGHS; symmetry breaking on rows/columns; run all 4.
2. **V2 SAT**: direct SAT with cardinality networks for sums and pairwise-Λ constraints;
   cube-and-conquer for the hardest instance.
3. **V3 prescribed automorphisms**: Kramer–Mesner reduction under small groups (Z_2, Z_3, Z_7 on
   V = 14); orbit-matrix ILP — the classical method never tried here.
4. **V4 annealing++**: CPro1-style local search but with multi-objective energy (violations of
   each constraint class weighted adaptively) and restarts from V1's LP-relaxation roundings.
5. **V5 nonexistence**: attempt counting/divisibility/linear-algebra nonexistence proofs
   (generalized Fisher-type inequalities for BTDs, Greig's methods) on each cell; a proof of
   nonexistence closes the cell just as well as a construction.

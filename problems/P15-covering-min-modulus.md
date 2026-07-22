# P15 — Covering System with Minimum Modulus ≥ 43

**Statement.** Construct a covering system of the integers (finite residue classes a_i mod n_i,
distinct moduli, union = Z) with minimum modulus ≥ 43 — beating the standing record of 42.
(Erdős's minimum modulus problem, constructive side. Record: 42, T. Owens, BYU MSc thesis 2014,
scholarsarchive.byu.edu/etd/4329, improving Nielsen's 40. Upper bound: min modulus ≤ 616,000,
Balister–Bollobás–Morris–Sahasrabudhe–Tiba 2022; earlier Hough, Annals 2015.)

**Why it matters.** THE covering-system question for 60 years. The gap 42 ↔ 616,000 is the
community's standing quantitative challenge. Any min modulus ≥ 43 construction is publishable.

**Status.** The 42 record was built BY HAND in 2014 (prime-by-prime greedy with hole-filling).
No published computational optimization (ILP/SAT/column generation) has ever been applied to the
constructive side.

**Witness & verifier.** Finite list of congruences; verify: every residue mod lcm covered
(CRT-structured check, avoids materializing lcm). Instant relative to size (likely 10³–10⁶
congruences).

**Prompt variants:**
1. **V1 mechanize Owens**: reimplement Nielsen/Owens's prime-by-prime distortion method as code;
   reproduce 40 and 42; then let the machine optimize the choices (branch-and-bound over
   hole-covering decisions) to push to 43+.
2. **V2 ILP/set-cover**: fix a smooth lcm N (chosen via the reciprocal-sum feasibility
   heuristics); covering with distinct divisors ≥ 43 of N is a structured set-cover — ILP with
   column generation over residue-class columns, CRT-layered.
3. **V3 SAT layered**: encode covering layer-by-layer over the prime factorization (tree
   structure of residues); incremental SAT adding primes until cover completes.
4. **V4 greedy + local repair at scale**: randomized greedy over huge modulus pools with
   simulated-annealing hole repair; the 2014 record used tiny hand-managed pools — scale is the
   unexplored dimension.
5. **V5 literature-first**: digest BBMST 2022's distortion method (their EXISTENCE machinery
   bounds min modulus ≤ 616,000 — it is semi-constructive); extract an explicit construction from
   their proof at ANY min modulus > 42; even min modulus 50 via their method, made explicit and
   verified, would be a result.

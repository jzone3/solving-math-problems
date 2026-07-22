# P08 — Graffiti 39/40: distance-matrix deviation vs inertia

**Statement.** For every connected graph G: (39) the standard deviation of the n² entries of the
distance matrix satisfies dev(D) ≤ n⁺(G) (number of positive adjacency eigenvalues);
(40) dev(D) ≤ n⁻(G). (WoW conj. 39, 40; open rows in Roucairol–Cazenave 2025 Table 1;
worked manually by Favaron–Mahéo–Saclé, Discrete Math. 111 (1993), left open.)

**Why it matters.** Classic Graffiti "metric vs spectral" pairing surviving 30+ years with no
dedicated literature.

**Status.** Exhaustive n ≤ 10 (1995); MCTS n ≤ 50 (2025). dev(D) grows with diameter while
inertia of structured trees can be controlled — **the n > 50 tree regime was never searched**.

**Witness & verifier.** One connected graph with large distance-variance and few positive
(resp. negative) adjacency eigenvalues; one BFS-APSP + eigensolve.

**Prompt variants:**
1. **V1 tree exhaustive + annealing**: trees have cheap D (BFS) — exhaust trees to n ≈ 24, then
   anneal on trees to n = 1000; score = dev(D) − n⁺ (resp. n⁻).
2. **V2 parameterized near-paths**: paths maximize dev(D) but have n⁺ ≈ n/2; hunt spectrally
   degenerate long-diameter families — brooms, caterpillars with periodic legs, subdivided stars
   (closed-form/recursive spectra); optimize parameters.
3. **V3 spectral design**: build graphs with forced small n⁺ (complete multipartite has n⁺ = k−1;
   graph products/joins control inertia) then stretch diameter with pendant paths; balance the
   trade-off systematically.
4. **V4 asymptotic analysis**: derive growth rates of dev(D) vs n⁺/n⁻ on candidate families; if
   any family wins asymptotically, find the concrete crossover instance and verify exactly.
5. **V5 both-conjectures harness**: unified search treating (39) and (40) simultaneously
   (n⁺ + n⁻ ≤ n bounds mean at least one side is ≤ n/2 — exploit); include non-tree sparse
   graphs; exact-verify all near-misses with rational/interval arithmetic.

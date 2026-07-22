# P01 — Sheehan's Conjecture (uniquely Hamiltonian 4-regular graphs)

**Statement.** Every Hamiltonian 4-regular simple graph has at least two Hamiltonian cycles.
Equivalently: no 4-regular simple graph is uniquely Hamiltonian.
(Sheehan 1975; Bondy–Murty GTM 244 appendix; openproblemgarden.org/op/uniquely_hamiltonian_graphs)

**Why it matters.** r=4 is THE remaining case of "no r-regular graph (r>2) is uniquely
Hamiltonian" (Thomassen: odd r; Haxell–Seamone–Verstraëte: even r > 22).

**Status.** Verified exhaustively for n ≤ 21 (Goedgebeur–Meersman–Zamfirescu 2020/2022).
Girão–Kittipassorn–Narayanan: asymptotically true (second cycle length ≥ n − cn^{4/5}), so any
counterexample is small-to-medium (n ≈ 22–50). Uniquely Hamiltonian 4-regular MULTIGRAPHS exist
(Fleischner); Entringer–Swart built uniquely Hamiltonian graphs with all degrees 4 except two of
degree 3.

**Witness & verifier.** A 4-regular simple graph with exactly one Hamiltonian cycle.
Verify: exact HC count via DP over path states / #SAT / ILP enumeration — seconds for n ≤ 40.

**Prompt variants (5 solve runs):**
1. **V1 direct search**: annealed local search over 4-regular graphs (2-opt style edge swaps
   preserving regularity), objective = number of Hamiltonian cycles (count with early cutoff at
   2); seed from random 4-regular graphs, n = 22–40.
2. **V2 structured construction**: start from Fleischner's uniquely Hamiltonian 4-regular
   multigraphs and Entringer–Swart near-4-regular graphs; design gadget replacements of
   multi-edges/degree-3 vertices that preserve HC-uniqueness; verify each construction exactly.
3. **V3 SAT/SMS**: encode "4-regular ∧ Hamiltonian ∧ no second HC" with SAT-modulo-symmetries or
   incremental SAT (find HC, block it, assert UNSAT of second HC) for n = 22–28; exhaust or find.
4. **V4 constraint-driven**: exploit known structure of minimum counterexamples from the
   Goedgebeur et al. papers (girth, connectivity constraints) to prune generation (genreg/snarkhunter
   style) and push the exhaustive frontier past n = 21; publishable either way.
5. **V5 literature-first**: digest Fleischner/Thomassen/GKN proofs to identify exactly where
   4-regular simple escapes the proof techniques; derive structural necessary conditions of a
   counterexample; then targeted search in that residual family.

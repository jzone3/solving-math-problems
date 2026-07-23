# Curated Problem Catalog

25 problems selected from `research/` (see `context/PLAN.md` for criteria). Each file contains
the statement, status, attack plan, and 5 prompt variants for parallel ultra-mode solve runs
(see `context/METHODOLOGY.md`).

| ID | Problem | Domain | Obs | Tract | Witness |
|----|---------|--------|-----|-------|---------|
| P01 | Sheehan's conjecture (uniquely Hamiltonian 4-regular) | graph theory | 4 | 4 | one 4-regular graph, unique HC |
| P02 | Brandt's regular supergraph conjecture | graph theory | 5 | 4 | maximal triangle-free graph + ILP infeasibility |
| P03 | Woodall's dijoin packing conjecture | comb. optimization | 3 | 4 | small digraph, dicut/dijoin gap |
| P04 | Hajós' Eulerian cycle decomposition conjecture | graph theory | 4 | 3 | Eulerian graph needing > ⌊(n−1)/2⌋ cycles |
| P05 | Gallai's three longest paths | graph theory | 3 | 3 | graph + 3 disjoint-intersection longest paths |
| P06 | Graffiti 129/698 (Laplacian deviation vs Randić) | spectral | 5 | 5 | one graph, eigensolve check |
| P07 | Graffiti 154 (2m·μ(D)² ≤ n³) | spectral | 5 | 5 | one connected graph |
| P08 | Graffiti 39/40 (distance deviation vs inertia) | spectral | 5 | 4 | one connected graph, n>50 regime |
| P09 | Bollobás–Nikiforov (λ₁²+λ₂² ≤ 2m(1−1/ω)) | spectral | 2 | 5 | one graph |
| P10 | Brouwer's Laplacian partial-sum conjecture | spectral | 2 | 5 | one graph + index t |
| P11 | Circulant weighing matrices CW(96,36) etc. | designs | 4 | 5 | one ternary vector |
| P12 | Tuscan-2 squares T2(11), T2(13) | designs | 5 | 4 | one 11×11 array |
| P13 | Perfect Mendelsohn designs, block size 6 | designs | 4 | 5 | tiny block array |
| P14 | Balanced ternary designs, 4 open instances | designs | 5 | 4 | small {0,1,2} matrix |
| P15 | Covering system with min modulus ≥ 43 | number theory | 5 | 4 | finite congruence list |
| P16 | BHS Laplacian bounds #44/#46 (last 2 of 68) | spectral | 4 | 5 | one graph, eigensolve |
| P17 | WoW 20/21 (inertia ≤ energy/2) | spectral | 4 | 5 | one graph, eigensolve |
| P18 | Erdős #273 (covering, moduli p−1, p≥5) | number theory | 4 | 4 | finite congruence list |
| P19 | Wide Partition Conjecture (Chow–Taylor) | comb. designs | 4 | 4 | partition + UNSAT tableau cert |
| P20 | Grünbaum 4-regular 4-chromatic girth ≥ 6 | graph theory | 4 | 4 | one graph + DRAT 3-col UNSAT |
| P21 | Hoffman–Singleton decomposition of K₅₀ | designs | 4 | 3 | 7 edge-disjoint HoSi copies |
| P22 | Folkman Fe(3,3;4) — Graham's $100 (H₃/G₁₂₇ arrowing) | Ramsey | 5 | 4 | one SAT/DRAT arrowing cert |
| P23 | 5-chromatic unit-distance graph < 509 vertices | geometry | 5 | 4 | exact-coordinate UDG + DRAT |
| P24 | Biplane 2-(121,16,2): automorphism-cell eliminations | designs | 4 | 4 | per-cell DRAT certs |
| P25 | Football pool K₃(6,1) ∈ [71,73] | covering codes | 4 | 4 | size-72 code or UNSAT |

Wave-2 additions (2026-07-23) sourced from research/wave2-*.md.
Wave-3 additions (2026-07-23, named/notable problems, no more automated-conjecture lists)
sourced from research/wave3-*.md.

Notable exclusions (researched, rejected): Costas 32/33 (decades of prior compute), Hadamard-668
(active dedicated project), S(2,6,46) (picked-over), lonely runner k=9 / no-three-in-line D(61) /
u(n) (active specialist compute races), SRG(69,20,7,5) (kept as reserve), rational Diophantine
septuple (reserve — near-misses known but witness heights may be huge).

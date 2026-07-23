# P22-v2 — Statement fidelity & priority check (G₁₂₇ arrowing)

Run date: 2026-07-23. Target: decide whether G₁₂₇ → (3,3)ᵉ, where
G₁₂₇ = (Z₁₂₇, {{x,y} : x−y ≡ α³ (mod 127)}). UNSAT of the arrowing CNF would
give Fe(3,3;4) ≤ 127; a valid zero-mono-triangle 2-coloring would refute
Exoo's conjecture (and kill the classic ≤127 candidate).

## Statement fidelity

Checked word-by-word against Radziszowski–Xu, "On the Most Wanted Folkman
Graph", Geombinatorics XVI (2007) (paper53.pdf), Section 7:

- Definition of G₁₂₇ matches: vertices Z₁₂₇, x~y iff x−y is a nonzero cubic
  residue mod 127. Symmetry requires −1 to be a cubic residue; verified
  (126 ∈ C). The cubic residues form the index-3 subgroup C of Z₁₂₇^*, |C|=42.
- All invariants stated in RX07 §7 reproduced independently
  (`verify_props.py`, exact computations, PASS):
  2667 edges, 9779 triangles, 42-regular, K₄-free, independence number 11,
  vertex- and edge-transitive, automorphisms x ↦ ax+b (a ∈ C, b ∈ Z₁₂₇),
  order 127·42 = 5334 (matches RX07's "5334 (=127∗42) automorphisms").
  NOTE: the task prompt said Aut order "divisible by 127·63" — that is
  incorrect; the correct order is 127·42 = 5334 (RX07). Symmetry breaking here
  uses only verified automorphisms, so the discrepancy does not affect
  soundness.
- SAT encoding matches RX07 §7's reduction: one boolean per edge, two clauses
  (x∨y∨z), (¬x∨¬y∨¬z) per triangle; SAT ⇔ G₁₂₇ ↛ (3,3)ᵉ. Encoding self-test
  on R(3,3)=6: K₅ SAT / K₆ UNSAT (`selftest_encoding.py`, PASS).

## Priority check (widened, per METHODOLOGY formalization gate)

Searches performed (Exa, 2026-07-23): arXiv/Semantic-Scholar-indexed queries
for "Folkman Fe(3,3;4) G127 arrowing SAT", "G(127, cubic residues) arrows",
"Folkman 786 upper bound 2024 2025 2026", "arrowing triangle SAT DRAT Folkman
github", Zenodo/GitHub-oriented queries, Heule talk archives.

Prior work found on THIS exact instance (all leave it open):

1. Radziszowski–Xu 2007 (Geombinatorics XVI, paper53): conjecture
   G₁₂₇ → (3,3)ᵉ (attributed to Exoo); tried SAT solvers **zChaff** and
   **march_eq** on the exact 2667-var/19558-clause CNF — "these solvers seem
   to be far from being able to decide φG". Also note the NAE-3-SAT halving.
2. Lange–Radziszowski–Xu 2012 (arXiv:1207.3750, fe334mc12): MAX-CUT SDP
   relaxation on L(127,5)=G₁₂₇; bounds insufficient to prove arrowing;
   established Fe(3,3;4) ≤ 786 via G₇₈₆ instead. States "The question of
   whether G127 → (3,3) is still open".
3. Xu–Liang–Radziszowski 2018 (kwr18): reiterates the conjecture, still open.
4. Bikov–Nenov, AJC 77 (2020) "On the independence number of (3,3)-Ramsey
   graphs and the Folkman number Fe(3,3;4)" (arXiv:1904.01937): "It is still
   unknown whether G127 → (3,3)" — most recent peer-reviewed status.
5. Mulrenin–Van Overberghe 2025 (arXiv:2506.14942): H₃ (63-vertex Hermitian
   unital) candidate; does not address G₁₂₇ (0 mentions of 127).
6. Hassan–Radziszowski–Van Overberghe 2026 (arXiv:2605.16542, May 2026):
   newest Folkman-number paper; does not address G₁₂₇ arrowing.
7. Hassan, RIT MS thesis 2022 "Graph Arrowing: Constructions and Complexity":
   complexity-focused; no G₁₂₇ resolution claimed.

GitHub/Zenodo/OpenReview/general-web searches surfaced NO artifact repo
claiming a resolution of G₁₂₇ → (3,3)ᵉ or any Fe(3,3;4) upper bound below
786. Best published bounds remain 20 ≤ Fe(3,3;4) ≤ 786 (LB: Bikov–Nenov
arXiv:1609.03468).

Residual risks: paywalled Geombinatorics issues not fully checked; possible
unindexed private SAT-competition benchmark results on φ(G₁₂₇).

## Survey of prior attacks (bonus)

- SAT (zChaff, march_eq, 2007): hopeless at the time; no published modern
  CDCL/CnC attempt found — this run (kissat 4.0.4 + cube-and-conquer) appears
  to be the first documented modern attempt.
- MAX-CUT SDP / minimum-eigenvalue (Dudek–Rödl 2008; LRX 2012): proves
  arrowing for G₉₄₁, G₈₆₀, G₇₈₆; bounds too weak for G₁₂₇.
- Heuristic colorings (LRX 2012): MAX-CUT heuristics found colorings of
  H_G with large cuts but never a zero-mono-triangle coloring of G₁₂₇.

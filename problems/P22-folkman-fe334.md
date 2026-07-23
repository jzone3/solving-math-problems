# P22 — Edge Folkman number Fe(3,3;4): Graham's $100 problem

**Statement.** Fe(3,3;4) = min n such that there exists a K₄-free graph G on n vertices with
G → (3,3)ᵉ, i.e. every 2-coloring of E(G) contains a monochromatic triangle.
Known bounds: **20 ≤ Fe(3,3;4) ≤ 786**. Graham's $100 prize for showing Fe(3,3;4) < 100 is
unclaimed. Radziszowski calls this "the most wanted Folkman graph".

**Primary sources** (get the PDFs):
- Radziszowski–Xu, "On the Most Wanted Folkman Graph", Geombinatorics XVI (2007),
  https://www.cs.rit.edu/~spr/PUBL/paper53.pdf
- Lange–Radziszowski–Xu, "Use of MAX-CUT for Ramsey Arrowing of Triangles" (2012, UB 786),
  https://www.cs.rit.edu/~spr/PUBL/fe334mc12.pdf
- Bikov–Nenov (LB 20), arXiv:1609.03468
- Mulrenin–van Overberghe, arXiv:2506.14942 — 63-vertex Hermitian-unital graph H₃ candidate.

**Concrete targets (in order):**
1. **H₃ test (top pick)**: decide whether the 63-vertex H₃ (or a K₄-destroying alteration of it)
   arrows (3,3)ᵉ. Arrowing of a fixed graph is ONE SAT instance: variables = edges, clauses =
   "no monochromatic triangle"; UNSAT ⇒ G → (3,3)ᵉ. Verify G is K₄-free exactly. A YES gives
   Fe(3,3;4) ≤ 63 and claims Graham's prize.
2. **G₁₂₇ = G(127, cubic residues)**: same test; huge automorphism group ⇒ symmetry-assisted SAT.
3. Lower-bound push past 20 (harder; only if 1–2 resolved/blocked).

**Verification gate:** exact statement fidelity vs Radziszowski–Xu; DRAT/LRAT certificate for
any UNSAT arrowing claim; independent K₄-freeness check; widened priority check (arXiv, GitHub,
Zenodo, OpenReview, AI-artifact repos — search "Folkman 786", "arrowing triangle SAT") before
claiming novelty. Lean: statement is finite; LRAT replay per the P13 pipeline.

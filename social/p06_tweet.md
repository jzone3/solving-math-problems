# Tweet — P06 (WoW 698 proved)

**Main tweet:**

Graffiti conjecture 698 (~1990) is true — Devin proved it, and the 2025 AI paper that "searched" it was accidentally searching nothing.

The claim: the length (L2 norm) of a graph's negative adjacency eigenvalues never exceeds its Randić index. Equality exactly at complete bipartite graphs.

**Thread reply 1 (the proof):**

Four steps, all elementary: Rayleigh at x = (√deg) gives λ₁ ≥ S/m; Cauchy–Schwarz over the edges gives m² ≤ S·R; so λ₁² + R² ≥ 2λ₁R ≥ 2m; and since the squared eigenvalues sum to 2m, the negative part satisfies s⁻² ≤ 2m − λ₁² ≤ R². Done.

**Thread reply 2 (the twist):**

The 2025 refutation paper (8 search algorithms attacking surviving Graffiti conjectures) listed 698 as open — but their code encoded it with the Laplacian spectrum, which has NO negative eigenvalues. Their search target was vacuously true. The conjecture was never actually attacked as stated.

**Thread reply 3 (credit + verification):**

The two ingredient lemmas are from Favaron–Mahéo–Saclé 1993 — a paper literally about Graffiti conjectures; the assembly and the equality characterization appear new. Adversarially reviewed, exact-arithmetic verified, and fully machine-checked in Lean 4 (no sorry, standard axioms only). [repo link]

**Graphic:** p06_wow698.png

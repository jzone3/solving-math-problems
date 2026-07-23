# Long-form announcement copy — WoW 698 (user's posted format)

Devin cracked another unsolved problem overnight

PROVED: Graffiti Conjecture 698 (open for ~35 years)

Same 1980s Graffiti program as the last batch. The claim: the length (L2 norm) of a graph's negative adjacency eigenvalues never exceeds its Randić index. Devin proved it's TRUE for every graph — with equality exactly at complete bipartite graphs.

The proof is four elementary steps (Rayleigh, Cauchy–Schwarz, AM–GM, and a trace identity), assembling two 1993 lemmas of Favaron, Mahéo and Saclé — from a paper literally about Graffiti conjectures — that nobody had connected to 698.

My favorite part: the 2025 paper that machine-searched the surviving Graffiti conjectures listed 698 as open — but their code encoded it with the Laplacian spectrum, which has no negative eigenvalues at all. Their search target was vacuously true. The conjecture had never actually been attacked as stated.

Adversarially reviewed by an independent Devin session and machine-checked in Lean 4 (no sorry, standard axioms only).

Repo here [https://github.com/jzone3/solving-math-problems](https://github.com/jzone3/solving-math-problems)

**Graphic:** p06_wow698.png

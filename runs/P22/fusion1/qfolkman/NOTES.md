# P22-fusion1 — certified reproductions of the paper's small quasi-Folkman systems

Mulrenin–Van Overberghe (arXiv:2506.14942), appendix. A triangle system 𝒯 on
vertex set V is **quasi-Folkman** if (a) 𝒯 ⊉ K₄ (no 4-subset of V contains all
4 of its triples in 𝒯) and (b) the graph G = (edges appearing in 𝒯's triples)
arrows 𝒯: every 2-colouring of E(G) has a monochromatic triple in 𝒯. Encoded as
SAT (one var per edge, two NAE clauses per triple); **UNSAT ⇔ arrows**. All
results below are independently reconstructed and certified (kissat/CaDiCaL UNSAT
+ drat-trim/lrat-check VERIFIED). Note: quasi-Folkman is *weaker* than genuine
edge-Folkman — G itself is not required K₄-free — so these do **not** bound
f(2,3,4); they are faithful, checkable reproductions of the paper's stated
computations ("been done before").

## 11-vertex circulant (`qf11.py`, `verify_qf11_independent.py`)
Vertices {1..11}; 𝒯 = all 11 cyclic rotations (mod 11) of the 8 base triples
{1,2,3},{1,2,4},{1,2,6},{1,2,7},{1,3,5},{1,3,8},{1,4,7},{1,4,8} — exactly the
example in the paper. |𝒯| = 88, G = K₁₁ (55 edges), CNF 55 vars / 176 clauses,
property (a) checked over all C(11,4)=330 quads. kissat + CaDiCaL `s
UNSATISFIABLE`; drat-trim + lrat-check `VERIFIED`; independent verifier PASS.

## 39-vertex H₃ reduction (`h3_39.py`)
Remove the vertices of three pairwise-vertex-disjoint maximal K₉ cliques of H₃
(clique indices (0,1,4), union 24 vertices). Result reproduces the paper's stated
counts **exactly**: 39 vertices, 411 edges, 1488 triangles, 898 non-degenerate.
Its non-degenerate-triangle arrowing CNF (1796 clauses) is kissat `s
UNSATISFIABLE`, drat-trim `s VERIFIED` — the 39-vertex graph is still
quasi-Folkman, as claimed.

## 12-vertex example (`qf12.py`)
The paper states a 12-vertex quasi-Folkman graph exists but does not print it; the
explicit 120-triple set is taken from the authors' repository
(github.com/Steven-VO/quasiFolkman, `quasi_folkman.ipynb` cell 62) and matched
exactly. 12 vertices, 66 edges (K₁₂), 120 triples, CNF 240 clauses. kissat `s
UNSATISFIABLE`, drat-trim `s VERIFIED`.

Large/regenerable proofs (`*.drat`, `*.lrat`) are git-ignored; `.py`, `.cnf`,
`.edges`, and solver `.out` logs are tracked.

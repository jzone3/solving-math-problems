# P22-fusion1 / H₃ — the 63-vertex Hermitian-unital route to Fe(3,3;4)

Session 2026-07-24, branch `runs/P22-fusion1`. This is a **different target** from
the G₁₂₇ work in `../NOTES.md`: the problem file's *top-pick* candidate for
pushing Fe(3,3;4)=f(2,3,4) far below 786 is the 63-vertex graph **H₃** of
Mulrenin–Van Overberghe, "Some remarks on Folkman graphs for triangles"
(arXiv:2506.14942, 2025-06-17). We independently reconstruct H₃, reproduce and
**fully certify** their q=3 computational result, and probe the open frontier
toward `f(2,3,4) ≤ 63`.

## The construction (paper §2), all independently verified

Work in `PG(2,q²)` with `q=3`, i.e. over `GF(9)`.
- Hermitian unital `U = {⟨X,Y,Z⟩ : X^{q+1}+Y^{q+1}+Z^{q+1}=0}`, here `X⁴+Y⁴+Z⁴=0`;
  `|U| = q³+1 = 28`.
- **Secants** = lines meeting `U` in exactly `q+1 = 4` points; there are
  `q⁴−q³+q² = 63` of them.
- **H₃** = intersection graph of secants: vertices = secants, `v_ℓ ~ v_m` iff
  `ℓ ∩ m ∈ U` (they cross at a unital point).
- **Maximal cliques `C_q`**: for each unital point, the `q²=9` secants through it
  form a clique of order 9; there are `q³+1 = 28`, and every edge lies in
  **exactly one** (its crossing point).
- A triangle (3 pairwise-adjacent secants) is **degenerate** if all three pass
  through one common unital point (lives inside one clique), **non-degenerate**
  otherwise (three *distinct* crossing points). `T₃` := the non-degenerate
  triangles.

`build_h3.py` builds all of this over `GF(3)[i]/(i²+1)` and checks, with hard
asserts, every statistic in Propositions 2.1/2.2/2.3:

```
H_3: n=63 vertices, 1008 edges, 32-regular   d=(q+1)(q²−1)=32   [OK]
|U|=28, secants=63                                              [OK]
triangles total=5376, non-degenerate |T_3|=3024  (paper eq (3)) [OK]
Prop 2.3: #K4 with all four faces non-degenerate = 0            [OK]
```

`verify_h3.py` is an **independent second verifier** (methodology gate): it
rebuilds H₃ from scratch over a *different* field model `GF(3)[t]/(t²+2t+2)`
(so the arithmetic/geometry code shares nothing with `build_h3.py`), and
re-derives 63 vtx / 1008 edges / 32-regular / **srg(63,32,16,16)** (adjacent and
non-adjacent vertices both have 16 common neighbours) / 28 order-9 maximal
cliques with unique edge membership / 5376 triangles / |T₃|=3024 / Prop 2.3.
It then reads `h3.edges` and `h3.cnf` and checks (order-independent, via clause
multiset) that the CNF is *exactly* the NAE encoding of T₃ over the
independently-built graph. Output: all `PASS`.

## Certified result: H₃ → (K₃)_{T₃}

Encoding (`h3.cnf`): one Boolean per edge (1008 vars); for each non-degenerate
triangle `{a,b,c}` two clauses `(a∨b∨c)`, `(¬a∨¬b∨¬c)` — total 6048 clauses.
SAT ⇔ a 2-colouring of E(H₃) with **no monochromatic non-degenerate triangle**;
UNSAT ⇔ `H₃ → (K₃)_{T₃}`.

```
kissat  h3.cnf → s UNSATISFIABLE (exit 20)   ~3.3 s
cadical h3.cnf → s UNSATISFIABLE (exit 20)   (second, independent solver)
drat-trim h3.cnf h3.drat → s VERIFIED        (backward-checked DRAT)
lrat-check h3.cnf h3.lrat → c VERIFIED       (LRAT emitted by drat-trim -L)
```

So **every 2-colouring of E(H₃) contains a monochromatic non-degenerate
triangle**, and since `T₃ ⊉ K₄` (Prop 2.3, re-verified), this reproduces —
independently and with a checked UNSAT certificate — the q=3 case of Theorem 1.1
that the paper attributes to "recent adjacent computational work" [ref 22].
Two solvers agree UNSAT; two independent checkers verify the proof.

## Why this is NOT yet a Folkman bound (honest scope)

H₃ is **not** K₄-free: it contains **9576** K₄'s (each order-9 clique alone
contributes many). A graph with `T ⊉ K₄` and `H → (K₃)_T` need not be Folkman,
because it can carry "accidental" K₄'s using a triangle outside `T` (paper §1).
So `H₃ → (K₃)_{T₃}` does **not** by itself give `f(2,3,4) ≤ 63`. Closing that
gap is the paper's **open conjecture**: does H₃ contain a genuine K₄-free
Folkman subgraph?

## Frontier probe: block constructions (open conjecture) — negative

By Prop 2.2(4), every K₄ has ≥3 vertices in one maximal clique, so making every
maximal clique triangle-free destroys **all** K₄'s. Max-edge way: replace each
`K₉` clique by a balanced complete bipartite `K_{4,5}` ("random block
construction"); an edge survives iff its two secants land on opposite sides of
their clique's bipartition. The 28 bipartitions are independent. Surviving
triangles are exactly the non-degenerate triangles all three of whose edges
survive. `block_search.py` builds the surviving subgraph `G` (always K₄-free,
asserted `#K4 == 0`), encodes arrowing over `G`'s own triangles, and runs kissat
(`--time=300`). UNSAT would mean `G → (3,3)ᵉ` on ≤63 vertices ⇒ `f(2,3,4) ≤ 63`.

Result over 250 constructions (200 random balanced + 50 triangle-count-maximizing
local search):

| strategy | #constructions | surviving edges (min/med/max) | surviving triangles (min/med/max) | SAT | UNSAT | TIMEOUT |
|---|---:|---:|---:|---:|---:|---:|
| random balanced | 200 | 560/560/560 | 465/519/555 | 200 | 0 | 0 |
| greedy/local-search | 50 | 560/560/560 | 570/596/619 | 50 | 0 | 0 |
| **total** | **250** | 560 | 465/524/619 | **250** | **0** | **0** |

Every construction is satisfiable (each solved in <0.01 s), i.e. **none arrows**.
Even the triangle-maximizing constructions (≈560 edges, ≈600 surviving
triangles) leave far too sparse a triangle hypergraph to force a monochromatic
triangle — consistent with the paper only *conjecturing* the q=3 case and its
Theorem 1.2 needing `q → ∞` (bound ≈ 2^280). So **balanced block constructions
of H₃ do not yield an f(2,3,4) ≤ 63 Folkman graph**; a positive answer, if one
exists, needs edge deletions outside this natural family (open).

## Files
- `build_h3.py` — constructor + property checks + CNF/edge emit.
- `verify_h3.py` — independent second verifier (different field model). PASS.
- `h3.edges`, `h3.cnf` — the graph (1008 edges) and arrowing CNF (1008 var / 6048 cl).
- `h3.drat`, `h3.lrat` — UNSAT proofs; `*.verify.out` — solver/checker logs.
- `block_search.py`, `block_results.json`, `blocks/` — frontier probe (all SAT).

## Bottom line
Independently reconstructed H₃, and reproduced + **certified** (DRAT & LRAT,
two solvers, two checkers) `H₃ → (K₃)_{T₃}`. This is solid new verified content
for P22, but is *not* a Folkman bound. The natural K₄-eliminating family (block
constructions) provably fails to arrow for q=3 over 250 tries, so
`f(2,3,4) ≤ 63` via H₃ remains **open**; `21 ≤ f(2,3,4) ≤ 786` stands.

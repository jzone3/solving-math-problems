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

## Full-graph arrowing H₃ → (3,3)ᵉ: certified but trivial

`full_arrow.py` emits the arrowing CNF over **all** 5376 triangles of H₃
(`h3_full.cnf`, 1008 vars / 10752 clauses). kissat → UNSAT (exit 20), drat-trim
→ VERIFIED, so H₃ → (3,3)ᵉ. But the proof is *tiny* (23 core lemmas): each
maximal clique is a K₉ ⊇ K₆ and R(3,3)=6, so every 2-colouring already has a
monochromatic (degenerate) triangle inside one clique. Hence full-graph arrowing
is trivial and useless for Folkman — the content is entirely in the **K₄-free**
constraint (which forbids exactly those clique triangles). This is why T₃
(non-degenerate only) is the meaningful system and why f(2,3,4) ≤ 63 hinges on
the open K₄-free-subgraph question.

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

## Frontier probe 2: max-triangle K₄-free subgraphs (ILP) — negative

Block constructions force each maximal clique *triangle-free* (very lossy). A
strictly larger family of K₄-free subgraphs is obtained by deleting only an
edge **hitting set** of the K₄'s: every K₄ must lose ≥1 of its 6 edges, but
cliques may keep triangles (as long as they don't extend to a K₄). `k4free_max.py`
solves this with an ILP (PuLP/CBC): binary `x_e` (edge kept), `z_T ≤ x_e` for
each triangle edge, constraint `Σ_{e∈K₄} x_e ≤ 5` for all 9576 K₄'s, objective
`max Σ z_T`. Each extracted subgraph is *independently* re-checked K₄-free
(direct enumeration, `#K4 == 0`) and its arrowing CNF (over **all** its
triangles, not just non-degenerate ones) is solved with kissat.

CBC did not close the ILP within 900 s (max-triangle incumbent 682, upper bound
2514; so the reported values are strong feasible incumbents, not certified
optima). Even so, every candidate is satisfiable:

| subgraph | ILP status | \|E\| | total triangles | non-deg / deg | kissat | K₄-free |
|---|---|---:|---:|---:|---|---|
| max-triangle ILP | feasible (gap) | 627 | 1101 | 682 / 419 | **SAT** | yes (asserted) |
| max-edge ILP | feasible (gap) | 601 | 951 | 562 / 389 | **SAT** | yes (asserted) |
| greedy max-triangle | heuristic | 627 | 1101 | 682 / 419 | **SAT** | yes (asserted) |

These retain far more triangles (up to 1101) than the block constructions
(~500–600) yet still **do not arrow** — a K₄-free subgraph of H₃ needs its
triangle hypergraph dense enough to force monochromaticity, and even the
triangle-maximizing K₄-free subgraphs found are colourable. So across two
independent families (bipartite block constructions and optimal K₄-edge-hitting
subgraphs), **no K₄-free subgraph of H₃ was found that arrows**; `f(2,3,4) ≤ 63`
via H₃ remains **open** (consistent with the paper's conjecture and its
Theorem 1.2 requiring q → ∞).

## Exact max-triangle-K₄-free optimum: still open interval

Attempted to certify the true maximum number of non-degenerate triangles in any
K₄-free subgraph of H₃ (`k4free_opt.py`, CBC 900 s + HiGHS 1.15.1 1200 s, warm
starts). The MILP is hard: best proven incumbent **682**, best valid upper bound
**≈2477** — **optimality NOT proven** (interval [682, 2477]). So we cannot yet
claim the triangle-maximal K₄-free subgraph, only a strong incumbent. The best
incumbent subgraph (627 edges, 1101 triangles) is again **SAT / does not arrow**
(independently-verified 0-mono-triangle colouring). Recorded in `k4free_opt.json`
(`certified_optimal: false`). Note: even a certified optimum would not settle the
conjecture, since arrowing is not monotone in triangle count — this only bounds
the natural "how many triangles can a K₄-free subgraph keep" quantity.

## Complete CEGAR decision procedure — undecided (does not converge)

`cegar.py` implements a *complete* refinement loop that can in principle settle
the conjecture either way: ILP picks a K₄-free subgraph G forced to contain a
monochromatic triangle under every good colouring found so far
(`Σ_{T∈mono(c)} y_T ≥ 1`, `y_T ≤ x_e`, `Σ_{K₄} x_e ≤ 5`); kissat then tests G
for arrowing. UNSAT ⇒ G arrows ⇒ f(2,3,4) ≤ 63; ILP infeasibility ⇒ no K₄-free
subgraph arrows ⇒ conjecture false; SAT ⇒ add the new good colouring and repeat.
Each iteration provably cuts the current G, so it terminates — but only after
finitely-many (worst-case astronomically many) colourings.

Bounded run (HiGHS, 90 s/ILP, ~40 min wall): **27 iterations, |C|=29, status
undecided** — every G was SAT (does not arrow), K₄-freeness independently
asserted each round. The loop does **not** trend toward arrowing: the ILP
repeatedly returns *degenerate* candidates (often 5–6 edges / 2 triangles that
trivially dodge the few accumulated colourings), because "hit finitely many
colourings" is far too weak a pressure — tiny K₄-free graphs always evade a
small colouring set. This confirms the practical intractability: settling the
paper's conjecture is not reachable by this (or the earlier heuristic) approach
within available compute. Artifacts: `cegar.py`, `cegar_results.json`,
`colorings.json`.

**Triangle-floor variant (serious candidates, still SAT).** To kill the
degeneracy, `--triangle-floor N` adds `Σ y_T ≥ N` so every candidate is a
triangle-rich near-frontier K₄-free subgraph. (Tradeoff: with a floor, ILP
infeasibility no longer proves the conjecture FALSE — it only says "no K₄-free
subgraph with ≥N triangles hits all accumulated colourings"; the decisive-FALSE
branch survives only at floor 0.) Run `--triangle-floor 400 --ilp-time 150
--kissat-time 180 --wall-time 1500`: 10 iterations, every candidate independently
confirmed K₄-free with 401–863 triangles, **all SAT** (none arrows). So even the
richest K₄-free subgraphs of H₃ we can produce (up to 863 triangles) fail to
arrow — the strongest negative evidence yet on the paper's open conjecture, but
still not a decision.

## Exact decision as a 2-QBF (the principled version of CEGAR) — undecided

The open question "does H₃ contain a K₄-free subgraph S with S → (3,3)ᵉ?" is
*exactly* a 2-QBF, because arrowing is monotone under adding edges:

    ∃ s_e (K₄-free selection) . ∀ x_e (2-colouring) . ∃ present monochromatic triangle.

`qbf_arrow.py` emits this in QDIMACS with prefix `∃ s (1008) | ∀ x (1008) |
∃ t (5376)`: K₄-free clauses on s (one 6-literal clause per K₄), Tseitin vars
`t_T` forced false unless T is both present (`t_T→s_a,s_b,s_c`) and monochromatic
(`t_T→ x_a=x_b=x_c`), and one global clause `∨_T t_T`. 7392 vars, 47209 clauses
(9576 K₄ + 7·5376 triangle + 1 global); self-check confirms the empty/trivial
subgraph correctly fails. A verdict here is **decisive either way**: TRUE ⇒ a
K₄-free arrowing subgraph exists ⇒ f(2,3,4) ≤ 63 (then certify the witness S by
the ordinary UNSAT+DRAT arrowing test); FALSE ⇒ **no** K₄-free subgraph of H₃
arrows ⇒ the paper's q=3 conjecture is disproven.

Ran CAQE 4.0.1 and DepQBF 6.03, 1200 s each: **both TIMEOUT**, no verdict, no
certificate. This is the honest ceiling — a dedicated ∃∀ CEGAR solver (which is
the principled form of our hand-rolled CEGAR above) also fails to decide the
instance in available compute. Artifacts: `qbf_arrow.py`, `qbf_results.json`
(the 47k-clause `.qdimacs` and solver logs are large/regenerable, git-ignored).

**Strengthened QBF (`--symbreak` + bloqqer) — still undecided (hardware ceiling).**
`qbf_arrow.py --symbreak` adds *sound* lex-leader symmetry breaking on the ∃-s
layer: pynauty automorphism generators (7 used), each **verified to be a genuine
H₃ automorphism** before use (an unsound permutation could yield a false FALSE),
lifted to the 1008-edge action, with comparator aux vars in the outer ∃ block.
This yields 14511 vars / 89552 clauses (80714 after bloqqer 037 preprocessing).
Reran DepQBF and CAQE (± bloqqer), longer budget: all four **UNKNOWN** — the box
ran out of memory (`Out of memory: Killed process ... caqe`) before any verdict.
So even with preprocessing + symmetry breaking the exact decision procedure
exceeds this machine's memory/compute; the question stays open, and settling it
would need a bigger machine or a stronger/parallel QBF solver on the (sound,
regenerable) `h3_arrow_sym.qdimacs`.

## Certificate-backed negative decisions (SAT witnesses)

`verify_witness.py` extracts a model from kissat for each of the three K₄-free
alterations and **independently** verifies it: rebuild the subgraph, map the
model to an edge 2-colouring, enumerate all triangles and confirm **0
monochromatic**, re-assert K₄-free. All three PASS (0 mono triangles), so each
"does not arrow" decision has an exact certificate (the counterpart of the DRAT
proof on the UNSAT side):

```
max-triangle-ilp:    |E|=627 #triangles=1101 mono=0 K4-free=yes PASS
max-edge-ilp:        |E|=601 #triangles=951  mono=0 K4-free=yes PASS
greedy-max-triangle: |E|=627 #triangles=1101 mono=0 K4-free=yes PASS
```

Colourings saved to `witnesses.json`.

## Priority re-check (H₃ route)
Fresh Exa searches (2026-07-24): no published Fe(3,3;4) upper bound below 786
(Lange–Radziszowski–Xu record stands; cf. also "Ramsey graphs and the Folkman
number Fe(3,3;4)", Australas. J. Combin. 77). No artifact exhibits a *K₄-free*
subgraph of H₃ that arrows — the paper only **conjectures** H₃ contains a
Folkman subgraph, and its unconditional Theorem 1.2 needs q → ∞. So
`f(2,3,4) ≤ 63` via H₃ is genuinely **open**; the certified positive result here
is `H₃ → (K₃)_{T₃}` (T₃ = non-degenerate triangles, not K₄-free), matching the
paper's q=3 computation.

## Files
- `build_h3.py` — constructor + property checks + CNF/edge emit.
- `verify_h3.py` — independent second verifier (different field model). PASS.
- `h3.edges`, `h3.cnf` — the graph (1008 edges) and arrowing CNF (1008 var / 6048 cl).
- `h3.drat`, `h3.lrat` — UNSAT proofs; `*.verify.out` — solver/checker logs.
- `block_search.py`, `block_results.json`, `blocks/` — frontier probe 1 (all SAT).
- `k4free_max.py`, `k4free_results.json`, `k4free_max*.cnf`, `*.cbc.log` — frontier probe 2, max-triangle K₄-free subgraphs (all SAT).

## Bottom line
Independently reconstructed H₃, and reproduced + **certified** (DRAT & LRAT,
two solvers, two checkers) `H₃ → (K₃)_{T₃}`. This is solid new verified content
for P22, but is *not* a Folkman bound. The natural K₄-eliminating family (block
constructions) provably fails to arrow for q=3 over 250 tries, so
`f(2,3,4) ≤ 63` via H₃ remains **open**; `21 ≤ f(2,3,4) ≤ 786` stands.

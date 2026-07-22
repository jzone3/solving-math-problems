# P02 Lean formalization notes

Machine-checked (Lean 4 + mathlib) refutation of the statement on West's
open-problem page (dwest.web.illinois.edu/openp/regsup.html):

> "If G is a maximal triangle-free graph and has minimum degree at least
> n(G)/3, then G has a regular supergraph obtainable by vertex
> multiplications."

Witness: the 9-vertex graph `W` (graph6 `H?q`qjo`, edges
{04, 05, 08, 14, 17, 18, 25, 26, 28, 36, 37, 38, 46, 57}), the minimal
counterexample from `runs/P02/v4` / `solutions/P02/verify.py`.

## Project

`formalization/P02/` — Lean 4 (`leanprover/lean4:v4.32.0`) + mathlib
(`v4.32.0`), same toolchain as `formalization/P08`.

| File | Contents |
|---|---|
| `P02/Multiplication.lean` | General defs: `SimpleGraph.mult` (vertex multiplication), `multEmbedding` (supergraph embedding for x ≥ 1), `mult_degree`, `mult_isRegularOfDegree_iff` (regularity ⇔ linear system), `farkas_no_solution` (certificate-checking lemma) |
| `P02/Witness.lean` | `W`, plus `decide`-proved facts: `W_cliqueFree`, `W_common_neighbor`, `W_maximal`, `W_degree`, `W_minDegree` |
| `P02/Main.lean` | Farkas certificate `y`, `W_linear_system_infeasible`, `W_no_regular_mult_supergraph`, `WestStatement`, `west_statement_false` |

## Main theorems

```lean
-- W satisfies the hypotheses
theorem W_cliqueFree : W.CliqueFree 3
theorem W_maximal   : Maximal (fun H => H.CliqueFree 3) W
theorem W_degree    : ∀ v : Fin 9, 9 ≤ 3 * W.degree v   -- δ ≥ n/3, exact form
theorem W_minDegree : W.minDegree = 3                    -- = 9/3 exactly

-- ... but has NO regular multiplication supergraph
theorem W_no_regular_mult_supergraph
    (x : Fin 9 → ℕ) (hx : ∀ v, 1 ≤ x v) (d : ℕ) :
    ¬(W.mult x).IsRegularOfDegree d

-- and hence West's recorded statement is false
def WestStatement : Prop :=
  ∀ (n : ℕ) (G : SimpleGraph (Fin n)) (_ : DecidableRel G.Adj),
    Maximal (fun H => H.CliqueFree 3) G →
    (∀ v, n ≤ 3 * G.degree v) →
    ∃ (x : Fin n → ℕ) (d : ℕ), (∀ v, 1 ≤ x v) ∧ (G.mult x).IsRegularOfDegree d

theorem west_statement_false : ¬WestStatement
```

## Proof structure

1. **Finite decidable facts** (`Witness.lean`): triangle-freeness, the
   common-neighbour property of every non-adjacent pair, and the degree
   bounds are all proved by plain `decide` (kernel reduction; `maxRecDepth`
   raised to 4000 for the `CliqueFree` check — still plain `decide`, **no
   `native_decide` anywhere**). Maximality (`Maximal (·.CliqueFree 3) W`,
   mathlib's order-theoretic maximality among triangle-free graphs on the
   same vertex set) is derived honestly from `W_common_neighbor`: any
   strictly larger graph has an edge uv ∉ W, and the common neighbour w of
   u, v yields the triangle {u, w, v} via `is3Clique_triple_iff`.

2. **Vertex multiplication, honestly** (`Multiplication.lean`):
   `G.mult x` lives on `Σ v, Fin (x v)` — each vertex `v` is replaced by an
   independent set of `x v` twin copies, with copies adjacent iff the
   originals are (the standard definition). For `x ≥ 1`, `multEmbedding`
   exhibits `G` as an induced subgraph (adjacency preserved AND reflected),
   justifying "supergraph obtainable by vertex multiplications".
   `mult_degree` computes `deg(v, i) = ∑_{u ∈ N(v)} x u` (via
   `Finset.card_sigma`), giving the honest equivalence
   `mult_isRegularOfDegree_iff`: the multiplication graph is d-regular iff
   `∑_{u ∈ N(v)} x u = d` for every v.

3. **Farkas certificate** (`Multiplication.lean` + `Main.lean`): the general
   lemma `farkas_no_solution` proves that any integer vector y with
   `∑ y = 0`, `(A y)ᵤ ≥ 0` for all u, and `∑ᵤ (A y)ᵤ > 0` refutes
   `{x ≥ 1, A x = d·1}` for **every** d simultaneously, by the symmetry
   chain `0 = d·∑y = ∑ᵥ yᵥ (Ax)ᵥ = ∑ᵤ (Ay)ᵤ xᵤ ≥ ∑ᵤ (Ay)ᵤ > 0`
   (double counting over the symmetric adjacency relation:
   `sum_neighborFinset_comm`, an instance of `Finset.sum_comm'`).
   The concrete certificate is `y = (2, -1, -1, 2, -1, -1, -1, -1, 2) : ℤ⁹`
   — exactly **twice** the rational vector `(1, -½, -½, 1, -½, -½, -½, -½, 1)`
   from `solutions/P02/verify.py` (cleared denominators; ℤ suffices, no ℚ
   needed). Its three defining properties (`y_sum`, `y_Ay_nonneg`,
   `y_Ay_sum_pos`; in fact A y = 2·e₈) are checked by `decide`.

## Verification record

- `lake build`: **succeeds** (Lean `v4.32.0`, mathlib `v4.32.0`), no `sorry`,
  no added axioms, no `native_decide`.
- `#print axioms` (2026-07-22, this commit):

```
'P02.west_statement_false' depends on axioms: [propext, Classical.choice, Quot.sound]
'P02.W_no_regular_mult_supergraph' depends on axioms: [propext, Classical.choice, Quot.sound]
'P02.W_maximal' depends on axioms: [propext, Classical.choice, Quot.sound]
'P02.W_cliqueFree' depends on axioms: [propext, Classical.choice, Quot.sound]
'P02.W_minDegree' depends on axioms: [propext, Classical.choice, Quot.sound]
'P02.W_degree' depends on axioms: [propext, Classical.choice, Quot.sound]
'SimpleGraph.mult_isRegularOfDegree_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'SimpleGraph.farkas_no_solution' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Exactly the three standard axioms; in particular no `sorryAx` and no
`Lean.ofReduceBool`/`Lean.trustCompiler` (which would indicate
`native_decide`).

## Fidelity review: formal statement vs. West's wording

West: *"If G is a maximal triangle-free graph and has minimum degree at least
n(G)/3, then G has a regular supergraph obtainable by vertex multiplications."*

- **"maximal triangle-free"** → `Maximal (fun H => H.CliqueFree 3) G`:
  G is triangle-free and no proper supergraph on the same vertex set is.
  This is the standard reading (adding any edge creates a triangle) and is
  proved for W from the common-neighbour property, not merely asserted.
- **"minimum degree at least n(G)/3"** → `∀ v, n ≤ 3 * G.degree v`, an exact
  integer form of δ(G) ≥ n/3 with no rounding or division; for W we
  additionally record `W.minDegree = 3` with `n = 9`, so W sits exactly on
  the δ = n/3 boundary (the open zone; δ > n/3 is the Brandt–Thomassé
  theorem).
- **"regular supergraph obtainable by vertex multiplications"** →
  `∃ x ≥ 1, ∃ d, (G.mult x).IsRegularOfDegree d`. `G.mult x` replaces each
  vertex by `x v ≥ 1` independent twin copies (the definition of vertex
  multiplication); `multEmbedding` proves it is genuinely a supergraph of G
  (G embeds as an induced subgraph). `IsRegularOfDegree d` is mathlib's
  "every vertex has degree d". The equivalence with the linear system is
  proved (`mult_isRegularOfDegree_iff`), not assumed.
- **Quantification**: `WestStatement` quantifies over graphs on `Fin n`.
  Since every finite graph is isomorphic to one on `Fin n` and all notions
  used are isomorphism-invariant, this loses no generality for the purpose
  of refutation: `west_statement_false` exhibits a concrete counterexample,
  which is the logically relevant direction.
- **Multiplicities**: x ranges over positive integers. Zero multiplicities
  (vertex deletion) are excluded — matching the "supergraph" requirement,
  West's wording, and `verify.py`. The `d` is existential, as in the
  statement; the Farkas certificate kills all d at once.

## Relation to `verify.py`

The Lean development formalizes the n = 9 witness (the minimal
counterexample) with the same edge list and (up to scaling by 2) the same
Farkas certificate as the first entry of `WITNESSES` in
`solutions/P02/verify.py`. The larger witnesses (n = 12, 15, 18) and the
infinite-family argument are not formalized here; n = 9 suffices to refute
the statement.

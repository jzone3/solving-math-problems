# Brandt's regular-supergraph problem (West's version) — REFUTED at n = 9

Self-contained verification package for a math researcher.

## The claim (false as recorded)

From Douglas West's *Open Problems — Graph Theory and Combinatorics* page
(`west_regsup.html`, dwest.web.illinois.edu/openp/regsup.html):

> If G is a maximal triangle-free graph and has minimum degree at least n(G)/3, then G has a
> regular supergraph obtainable by vertex multiplications.

Vertex multiplication: replace each vertex v by an independent set of x_v ≥ 1 twins (same
neighborhoods). A d-regular multiplication supergraph exists iff the integer system
Σ_{u∼v} x_u = d, x ≥ 1 is solvable — equivalently (by scaling) iff {x ≥ 1, Ax = c·1} is
feasible over ℚ.

## The witness

9-vertex graph, graph6 `H?q`qjo`, edges
{04,05,08,14,17,18,25,26,28,36,37,38,46,57}: maximal triangle-free, δ = 3 = n/3.
Infeasibility of the LP is certified by an explicit rational Farkas vector — a
machine-checkable impossibility proof, no search required to verify. Also included: a twin-free
n = 12 witness, a 4-chromatic n = 15 witness, and the infinite family n = 9t (blow-ups).

## How to verify

- `python3 verify.py` — re-derives maximality/degree conditions and checks the Farkas
  certificates with exact `fractions.Fraction` arithmetic. Expect PASS (all witnesses).
- Full run notes incl. exhaustive sweep (this is the MINIMUM counterexample: all maximal
  triangle-free graphs with δ ≥ n/3 for n < 9 admit regular multiplication supergraphs):
  `RUN-NOTES.md`.

## Lean formalization

`lean/` — the refutation is machine-checked in Lean 4 + mathlib
(`P02.west_statement_false`): W's maximal triangle-freeness and δ = 3 = 9/3 by kernel
`decide`; vertex multiplication defined honestly (blow-up graph on `Σ v, Fin (x v)`) with a
proven regularity ⇔ linear-system equivalence; infeasibility via an explicit integer Farkas
certificate. No `sorry`, no `native_decide`, no added axioms (`#print axioms` =
[propext, Classical.choice, Quot.sound]). Build: `cd lean && lake exe cache get && lake build`.

## Important nuance (statement provenance)

Brandt's original paper (`brandt2002.pdf`, Discrete Math. 251 (2002) 33–46, Conjecture 4.1)
requires minimum degree **strictly greater than** n/3; that version is now a THEOREM
(Brandt–Thomassé, regular weight functions). What is refuted here is precisely the ≥ n/3
version recorded on West's page — the boundary δ = n/3 — which is the statement the community
has been tracking as open. Brandt's in-paper Conjecture 5.1 (d_f < 3 ⇒ Ax = 1 has a rational
solution x ≥ 0) is untouched: our witnesses have d_f = 3 exactly.

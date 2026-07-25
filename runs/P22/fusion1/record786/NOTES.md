# Record graph \(G_{786}\)

This directory contains two structural reconstructions of the record
quasi-Folkman graph behind the known bound

\[
F_e(3,3;4) \le 786.
\]

The source is A. Lange, S. Radziszowski, and X. Xu, *Use of MAX-CUT for
Ramsey Arrowing of Triangles*, arXiv:1207.3750, Theorem `th:786`.

## Exact construction

The graph is

```text
G_786 = L(785,53) plus one extra vertex
```

where \(L(785,53)\) is the circulant graph on \(\mathbb Z_{785}\) with
connection set

\[
S = \{53^i \bmod 785 : i \ge 0\}.
\]

The subgroup has size 156 and contains \(-1\bmod 785\), so the circulant
part is undirected and 156-regular. The extra vertex, indexed 785, is joined
to the 60 vertices listed in the paper and hard-coded in both reconstruction
scripts.

## Independently verified structural facts

Both scripts independently obtain:

```text
vertices = 786
edges    = 61290
triangles= 428881
2*t_tri = 857762
K4-free = True
```

`build_g786.py` checks K4-freeness through triangle-freeness of every
neighborhood. `verify_g786_independent.py` uses a different test: it
enumerates all triangles and checks that no triangle has a common neighbor
adjacent to all three of its vertices. The latter is equivalent to the
absence of a 4-clique.

The independent verifier also reconstructs the edge set locally and compares
it with a freshly rebuilt edge set from `build_g786.build()`. Both verifiers
agree on the full graph.

## Arrowing caveat

The implication

\[
G_{786} \longrightarrow (3,3)
\]

is **not** re-certified here by SAT, DRAT, or another independent proof
system. In the cited paper it follows from a MAX-CUT SDP upper bound:

```text
857753 < 857762 = 2*t_tri.
```

Thus these artifacts reproduce and certify the machine-checkable structural
claims only. They reconfirm the known bound
\(F_e(3,3;4)\le 786\) as a reproducible artifact; they do not establish a
new or improved bound.

For comparison, the same paper's Table 1 gives \(G_{127}=L(127,5)\), where
the MAX-CUT upper bound is

```text
20181 > 19558 = 2*t_tri.
```

Consequently that method does not prove that \(G_{127}\) arrows
\((3,3)\). The paper explicitly states that whether
\(G_{127}\to(3,3)\) is still open, consistent with the undecided
`G_127` status in this project.

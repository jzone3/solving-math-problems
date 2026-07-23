# P22 / v1 — H₃ arrowing test (Folkman Fe(3,3;4), Graham's $100 problem)

Session: Devin ultra run, 2026-07-23. Branch `runs/P22-v1`. **Result: NEGATIVE (no Folkman
graph found; bound Fe(3,3;4) ≤ 786 unimproved).** All paper-suggested K₄-destroying
alterations of H₃ were tested at ~4× the authors' reported scale; every K₄-free candidate
admits a good 2-coloring (SAT), each independently re-verified in Python.

## 1. Construction of H₃ (exact, per arXiv:2506.14942 §2)

`h3.py` builds, from scratch:
- GF(9) = GF(3)[x]/(x²+1); PG(2,9) with 91 points/lines.
- Hermitian unital U₃ = {⟨X,Y,Z⟩ : X⁴+Y⁴+Z⁴ = 0}: **28 points** (= q³+1). ✓
- Secant lines (meet U₃ in exactly q+1 = 4 points): **63**; tangents: 28. ✓
- H₃ = intersection graph of secants (adjacent iff their intersection point ∈ U₃).

Independently verified properties (vs paper's Prop 2.2, q=3):
| property | computed | paper |
|---|---|---|
| n | 63 | q⁴−q³+q² = 63 |
| regularity | 32 | q³+q²−q−1 = 32 |
| edges | 1008 | (SAT vars: 1008) |
| maximal cliques C₃ | 28 cliques of order 9 | q³+1 = 28, order q² = 9 |
| SRG λ / μ | 16 / 16 | 2q²−2 = 16, (q+1)² = 16 |
| triangles / non-degenerate | 5376 / 3024 | \|T₃\| = 3024 (eq. (3)) |
| K₄ count | **9576** | H₃ is NOT K₄-free |

Since H₃ contains K₄s (indeed 28 K₉s), the direct branch "(1) if K₄-free" of the task does
not apply; per the paper's Problem 5.1 the question is whether H₃ has a **K₄-free subgraph**
H with H → (3,3)ᵉ. We therefore (a) reproduced the quasi-Folkman certificates, and
(b) ran the paper's K₄-destroying alterations (Appendix A, experiments 1–5).

## 2. Certified reproductions (DRAT, verified with drat-trim)

- `out/h3_quasi.cnf` (1008 vars, 6048 clauses — exactly the paper's instance):
  2-color E(H₃) with no monochromatic **non-degenerate** triangle → **UNSAT**;
  DRAT cert `out/h3_quasi.drat.gz`, drat-trim: `s VERIFIED`. Reproduces Theorem 1.1 (q=3):
  H₃ →_{T₃} (K₃), i.e. H₃ is quasi-Folkman.
- `out/h3_full_arrow.cnf` (all 5376 triangles): H₃ → (3,3)ᵉ → **UNSAT** (implied by the
  above; cert `out/h3_full_arrow.drat`, `s VERIFIED`). Not a Folkman graph since H₃ ⊇ K₄.

## 3. K₄-destroying alterations (paper's experiments 1–5) + SAT arrowing

`alterations.py`; every candidate: (i) exact K₄-freeness check, (ii) SAT test of
"∃ 2-coloring with no mono triangle" via kissat, (iii) if SAT, the coloring witness is
re-verified independently in Python (verify_coloring; zero failures).

| experiment | description | candidates | outcome |
|---|---|---|---|
| exp1 | each K₉ of C₃ → random K_{4,5} | 7,005 | all SAT (colorable) |
| exp2 | each K₉ → random maximal triangle-free graph | 7,000 | all SAT |
| exp3 | remove random K₄-edges until K₄-free | 5,003 | all SAT |
| exp4 | greedily remove edge in most K₄s | 330 | all SAT |
| exp5 | add random non-degenerate triangles keeping K₄-free | 12,000 | all SAT |

Total: **31,338 K₄-free candidates, none arrows (3,3)ᵉ.** Consistent with the authors'
"thousands of repeats, none succeeded" (Appendix A); our sample is several times larger.

`core_analysis.py` reproduces the paper's simplification observation (remove edges in ≤1
triangle + K₄-free vertices of degree < 8, iterate): exp3 candidates mostly collapse to the
empty graph (trivially colorable), while exp4/exp5 candidates keep essentially all 63
vertices (~575–655 edges) yet remain colorable — the same near-miss profile the authors saw.

## 4. Statement fidelity (vs primary literature)

Radziszowski–Xu, "On the Most Wanted Folkman Graph" (paper53.pdf): Fe(3,3;4) = smallest
order N of a K₄-free graph for which any 2-coloring of its edges contains a monochromatic
triangle ("equivalent to … the smallest K₄-free graph which is not a union of two
triangle-free graphs"). Our encoding is literally this: vars = edges, per triangle the two
clauses (x_e∨x_f∨x_g), (¬x_e∨¬x_f∨¬x_g); UNSAT ⇔ G → (3,3)ᵉ. K₄-freeness checked exactly
(exhaustive), not via the triangle system. Matches the paper's Appendix A encoding
(1008 vars / 6048 clauses for the quasi instance — exact agreement).

Note: the problem file's lower bound "20" is stale; Bikov–Nenov 2020 give 21 ≤ Fe(3,3;4)
(confirmed current in arXiv:2605.16542, May 2026).

## 5. Priority check (widened, per METHODOLOGY.md) — see PRIORITY.md

Clean: no artifact claiming Fe(3,3;4) < 786 or resolution of Problem 5.1 found
(arXiv, GitHub, Zenodo, OpenReview, Exa web search; details in PRIORITY.md).
The May-2026 survey-adjacent paper arXiv:2605.16542 still cites 21 ≤ Fe(3,3;4) ≤ 786.

## 6. Dead ends / observations

- H₃ itself trivially arrows (3,3)ᵉ (even restricted to non-degenerate triangles), but the
  arrowing evaporates under every K₄-destroying alteration tried. The obstruction: the
  quasi-Folkman UNSAT relies on the degenerate structure (K₉s) staying intact; once cliques
  are bipartized/thinned, good colorings reappear.
- The random block construction replaces each K₉ by a triangle-free graph; the paper's own
  Theorem 1.2 needs q large (bound ≈ 2^280), so failure at q=3 is expected but was worth
  the direct test.
- Next escalations (not done here): (a) exhaustive/SAT-guided search over *structured*
  clique replacements (e.g. all inequivalent K_{4,5} alignments simultaneously, as one
  2-level SAT/QBF instance rather than random sampling), (b) G₁₂₇ = G(127, cubic residues)
  arrowing with symmetry breaking (problem file target 2), (c) MaxSAT over subgraphs of H₃
  maximizing unavoidable mono triangles.

## Files

- `h3.py` — construction + property verification (run: prints all checks)
- `step1_verify.py` — quasi-Folkman + full arrowing UNSAT with DRAT certs
- `arrow.py` — SAT encoding, kissat/drat-trim drivers, K₄ checks, witness verifier
- `alterations.py` — experiments 1–5 (usage: `python3 alterations.py exp<k> <iters> [seed]`)
- `core_analysis.py` — simplification/core analysis of candidates
- `logs/` — per-experiment run logs; `out/` — CNFs, DRAT certs, JSON candidate logs
- Toolchain: kissat (arminbiere/kissat master), drat-trim (marijnheule/drat-trim master)

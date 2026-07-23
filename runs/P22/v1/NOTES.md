# P22 / v1 — H₃ arrowing test (Folkman Fe(3,3;4), Graham's $100 problem)

**Catalog correction:** the current lower bound is **21 ≤ Fe(3,3;4)** (Bikov–Nenov 2017/2020,
reconfirmed in arXiv:2605.16542, May 2026), not 20 as stated in `problems/P22-folkman-fe334.md`.

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

## 7. Escalation (1): structured 2-level CEGAR search (this session, phase 2)

`cegar.py` + `aut.py`: instead of random sampling, we attack **Problem 5.1 in full
generality** as a Σ₂ (∃∀) problem over ALL spanning subgraphs of H₃ (1008 edge booleans):

- Synthesis SAT (incremental CaDiCaL via pysat): K₄-freeness exact (9576 clauses over the
  K₄s of H₃); triangle indicator vars t_T ↔ "all 3 edges kept" (5376 triangles); WLOG core
  conditions, sound by the removability arguments in Appendix A / Bikov–Nenov (each kept
  edge in ≥2 kept triangles; every vertex degree 0 or ≥8; ≥1 triangle).
- CEGAR loop: synthesis model → K₄-free candidate → kissat arrowing check. Colorable ⇒
  the coloring (extended to E(H₃)) yields the blocking clause "some triangle monochromatic
  under Δ must be kept", added for the whole 192-element orbit of Δ under a computed
  subgroup of Aut(H₃) (`aut.py`: coordinate permutations × admissible diagonals × Frobenius,
  acting on secants; graph-automorphism property asserted). UNSAT ⇒ Folkman graph found.
- Synthesis-UNSAT terminates the loop with a PROOF that H₃ has no K₄-free arrowing subgraph
  (negative resolution of Problem 5.1); counterexamples persisted (`out/cegar_cex.txt`)
  so runs are resumable.

Note this space strictly contains the clique-replacement space of experiments 1–2 (any
K₄-free subgraph is admitted, incl. those with triangles inside C₃-cliques).

Two CEGAR strata were run for ~2h each (both still negative at wrap-up):

- **core-conditions stratum** (`cegar.py`): 2,176 counterexample colorings accumulated
  (each blocked as a full 192-orbit ⇒ ~418k colorings excluded); candidates drift to small
  sparse graphs (~130–250 edges), all colorable.
- **maximality stratum** (`cegar_max.py`): WLOG restriction to MAXIMAL K₄-free subgraphs
  (sound: any K₄-free arrowing subgraph extends to a maximal one, and arrowing is
  edge-monotone). Candidates are dense (~525–540 edges, ~600–670 kept triangles); 3,040
  counterexamples accumulated (~584k colorings excluded with orbits). All colorable.
- **Direct 2QBF** (`qbf_gen.py` → `out/p51.qdimacs`, 75,600 vars / 409,081 clauses,
  ∃ subgraph ∀ coloring ∃ witness): DepQBF 6.03 ran >1.5h without deciding; left as an
  artifact for a longer dedicated run (TRUE ⇒ Folkman graph ≤63 / Graham prize;
  FALSE ⇒ Problem 5.1 answered NO).

Counterexample pools are persisted (`out/cegar_cex.txt.gz`, `out/cegar_max_cex.txt.gz`)
and both loops resume from them, so a follow-up session can continue where this stopped.
No Folkman graph found; no synthesis-UNSAT proof reached either — Problem 5.1 remains open,
but the maximality stratum + orbit blocking is a substantially stronger attack than the
paper's random sampling and is the recommended continuation (possibly with the full
12,096-element PΓU(3,3) instead of the 192-element subgroup in `aut.py`).

## 8. Phase 3 (this session): full PΓU(3,3), parallel CEGAR — and a NEW exact result

### 8a. H₃ search upgrades (still negative)

- `aut_full.py` constructs the **full automorphism group** acting on the 63 secants:
  the 192-element monomial subgroup extended by randomly-found non-monomial unitary
  matrices (M with Mᵀ·M^(3) = λI), closed under composition → exactly **12,096 = |PΓU(3,3)|**
  permutations (verified as graph automorphisms of H₃).
- `cegar_max2.py`: maximality-stratum CEGAR with (i) new counterexamples blocked over
  random samples of the full 12,096 group, (ii) **partial lex-leader symmetry breaking**
  on the candidate edge vector (s ≤_lex s∘g for 48 random g ∈ PΓU(3,3); sound since
  maximality/K₄-freeness/arrowing are Aut-invariant), (iii) multiple parallel workers
  sharing the persisted pool. >45,000 further iterations across workers; every maximal
  K₄-free candidate (~515–550 edges) remains colorable. Pool grown to >46,000
  counterexample colorings (orbit-expanded: hundreds of millions excluded).

### 8b. NEW exact result: minimum order of quasi-Folkman triangle systems

Appendix A of arXiv:2506.14942 defines the **quasi-Folkman property** for (G,T):
T ⊉ K₄ (no 4 triples of T spanning only 4 vertices) and G →_T (K₃); the authors found
examples on 12, then 11 vertices (circulant, |T|=88) and left the minimum order open.
We DECIDED the small cases exactly:

- `enum_mono.c`: exhaustively enumerates ALL 2-colorings of E(K_n) (first edge fixed by
  complement symmetry) and outputs every distinct set ("mask") of monochromatic triples
  with ≤ thresh elements. n=7: 2²⁰ colorings (t6: 99,575 masks); n=8: 2²⁷ (t7: zero
  masks ⇒ every K₈-coloring has ≥8 mono triples; t8: 579,005); n=9: 2³⁵ (t13: 36.5M).
  Cross-validated for n=7 against an independent pure-Python brute force (exact match),
  and the paper's 11-vertex circulant example is confirmed quasi-Folkman by our checker.
- `quasi_exact.py`: a quasi-Folkman T must hit every coloring's mono-mask (a subset of
  these constraints being UNSAT is therefore a sound impossibility proof) + the 4-set
  face constraints; SAT models are checked exactly by one kissat arrowing call and,
  if colorable, refuted via CEGAR with S_n-orbit blocking.

Results (logs `logs/quasi7.log`, `logs/quasi8.log`):

- **n=7: NO quasi-Folkman system exists** (synthesis UNSAT immediately from the t6 masks).
- **n=8: NO quasi-Folkman system exists** (UNSAT after 1 CEGAR iteration).
- (Monotone in n via embedding, so none exists on ≤ 8 vertices.)
- n=9: the 36.5M-clause instance was still being decided at wrap-up (`logs/quasi9b.log`);
  n=10 open. Hence the minimum order of a quasi-Folkman system is in **{9,10,11}**,
  improving on the paper's "≤ 11, minimum unknown".

This is (per §5-style priority check: no artifact deciding small quasi-Folkman orders was
found) a small but genuinely new exact result directly answering a question left open in
the paper's appendix.

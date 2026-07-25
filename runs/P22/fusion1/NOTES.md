# P22-fusion1 — G₁₂₇ → (3,3)ᵉ ? (continuation: new attacks)

Session: 2026-07-24 (fusion continuation). Branch `runs/P22-fusion1`, built on
`runs/P22-v2`. Goal unchanged: decide whether G₁₂₇ = G(127, cubic residues mod
127) arrows (3,3)ᵉ. UNSAT of φ(G₁₂₇) ⇒ Fe(3,3;4) ≤ 127 (from 786) and claims
Graham's $100 prize; a zero-mono-triangle 2-coloring ⇒ refutes Exoo's
conjecture.

**This wave does NOT redo v2.** v2 already established (all machine-verified):
any witness coloring must have trivial automorphism stabilizer (circulant
exhaustive + orders 2/3/7 UNSAT, DRAT-certified); SAT-side floor 204 mono
triangles (needs 0); CDCL (kissat/gimsatul), lex/BreakID/SBVA, march_cu +
star-edge cube-and-conquer, orbit collapse, walk/NuWLS/RC2-LNS all fail to
decide. See `runs/P22/v2/NOTES.md`.

Per the instructions we tried **fundamentally different attacks**:
(A) a fractional/counting lower-bound argument, and (B) structure-aware cubing
with better (triangle-dense) cubing variables — which doubles as the RX07
dense-subgraph "enumerate colorings + extend" strategy. Both come with exact
verification; no UNSAT of the full instance is claimed, so no full-instance
DRAT certificate is produced (none exists — the instance did not close).

Outcome (honest): **G₁₂₇ → (3,3)ᵉ remains UNDECIDED.** Two new documented
results below sharpen *why* the standard attacks stall.

**Separate, more promising target — H₃ (63 vertices):** see
[`h3/NOTES.md`](h3/NOTES.md). We independently reconstruct the Hermitian-unital
graph H₃ of Mulrenin–Van Overberghe (arXiv:2506.14942) and reproduce + **fully
certify** (DRAT+LRAT, two solvers, two checkers) their q=3 result
`H₃ → (K₃)_{T₃}` (T₃ = non-degenerate triangles, T₃ ⊉ K₄). H₃ is not itself
K₄-free (9576 K₄'s), so this is not yet a Folkman bound; a 250-construction
balanced-block-construction search toward `f(2,3,4) ≤ 63` was all-SAT (none
arrows), quantifying the gap to the paper's open conjecture.

---

## Priority re-check (methodology formalization gate)

Fresh searches 2026-07-24 (Exa web + contents). The problem is **still open**:

- **Erdős Problem #582** (= Graham's $100 problem, the existence form of this
  exact Folkman number N = Fe(3,3;4)), erdosproblems.com/582, *last edited
  2026-02-08*: "The current best bounds known are **21 ≤ N ≤ 786**." Lower
  bound Bikov–Nenov [BiNe20]; upper bound Lange–Radziszowski–Xu [LRX14].
  RX07 "speculate N ≤ 127" (Exoo's conjecture, i.e. G₁₂₇ → (3,3)ᵉ). No
  resolution recorded.
  - Note: the current published **lower bound is 21** (Bikov–Nenov, AJC 2020),
    slightly stronger than the "≥ 20" in `problems/P22-folkman-fe334.md` and
    v2's PRIORITY.md. Does not affect the G₁₂₇ question.
- No new arXiv / GitHub / Zenodo / OpenReview artifact claims a decision of
  G₁₂₇ → (3,3)ᵉ or any Fe(3,3;4) upper bound below 786. The July 2026
  Resonance article "A Combinatorial Puzzle From Arithmetic" is an unrelated
  recreational (24-game / Polish-notation) piece — a false hit.
- Most recent Folkman-number papers (Hassan–Radziszowski–Van Overberghe
  arXiv:2605.16542; Mulrenin–Van Overberghe arXiv:2506.14942) do not address
  G₁₂₇ arrowing, consistent with v2's finding.

Residual risk unchanged from v2: paywalled Geombinatorics issues; possible
unindexed private SAT-competition results.

---

## Attack A — fractional / counting lower bound (rigorous NEW negative result)

**Question reframed.** G₁₂₇ → (3,3)ᵉ ⇔ min over 2-edge-colorings of
(# monochromatic triangles) ≥ 1. Any convex relaxation gives a *valid lower
bound* on that minimum; a relaxation value ≥ 1 would settle arrowing. This is
the analytic core of the LRX 2012 MAX-CUT SDP approach (too weak for G₁₂₇), and
is exactly the "fractional/counting argument" class requested.

**Result (proved, `fractional_lp.py`, PASS).** The *triangle-local LP
relaxation* — the Sherali–Adams level-2 / local-consistency LP over the
triangle hypergraph — has optimum value **exactly 0**:

- LP: per-triangle distributions p_T(s) ≥ 0 over the 8 colorings s ∈ {0,1}³ of
  its edges, with ∑ₛ p_T(s)=1 and edge-marginal consistency
  ∑_{s:s_j=1} p_T(s)=m_e across triangles sharing edge e; minimize
  ∑_T (p_T(000)+p_T(111)). Every genuine 2-coloring is a feasible point whose
  objective equals its mono-triangle count ⇒ LP_opt ≤ true min (valid bound).
- **Certificate that LP_opt = 0:** objective ≥ 0 always; and the explicit
  point m_e = ½ (all e) with every triangle taking the *uniform distribution
  over its 6 bichromatic patterns* {001,010,100,011,101,110} is feasible (each
  single-edge marginal is 3·⅙ = ½, identical for all triangles, so consistency
  holds globally) with objective 0. Hence LP_opt = 0 exactly. Confirmed
  numerically with scipy/HiGHS on a subgraph (optimum 0).
- The certificate uses only that G₁₂₇ is **K₄-free** (triangles pairwise share
  ≤ 1 edge, checked in the script), so it holds for *any* K₄-free triangle
  hypergraph.

**Meaning.** No counting/fractional argument that only couples triangles
through shared single-edge marginals (SA level ≤ 2) can prove arrowing of
G₁₂₇ — a clean explanation of why the LRX low-order MAX-CUT relaxation is too
weak. Strengthening requires higher SA/Lasserre levels (frustration around
odd cycles of triangles), which are SDPs at the (2667 choose 2) scale —
infeasible here and already found too weak by LRX at the tractable level.

Run: `python3 runs/P22/fusion1/fractional_lp.py` (add `--full-lp` for the
9779-triangle LP; the certificate is solver-free).

---

## Attack B — structure-aware / better cubing (triangle-dense region), measured

**Motivation.** v2's cube-and-conquer cubed the 42 **star edges** at vertex 0.
Fixing star edges forces some N(0)-internal edges by UP, but v2 measured that
even fixing 25–41 star edges leaves instances kissat can't refute in 240–300 s
(and a UP-only star DFS hit 176M nodes, 0 conflicts). Hypothesis: cubing on a
**connected, triangle-dense region** of edges (many *internal* triangles fully
determined by the cube) should create deeper propagation cascades and might
decompose better. This is simultaneously the classic RX07 "enumerate colorings
of a dense subgraph, then extend" strategy.

**Method (`dense_cube.py`, `conquer_dense.py`, `measure_up.py`).** Greedily
grow a vertex set W maximizing induced triangles; cube on S = edges induced on
W. Enumerate assignments to S, dropping any that make an induced triangle
monochromatic (sound: such an assignment already contains a mono triangle, so
φ(G₁₂₇) refutes it by one clause). Sample surviving cubes, add their literals
(mapped to the canonical global gen_cnf.py edge-variable numbering) as units to
`plain.cnf`, and conquer with kissat (120 s/cube, 8 workers). Compare against a
matched-|S| **star-edge baseline**.

> Correctness note: an initial version emitted cube literals in region-*local*
> edge order and fed them to `plain.cnf` (which numbers vertex-0 star edges
> 1..42 first), so it accidentally re-ran star cubing. Fixed by mapping every
> cube literal to the global edge-variable id before solving; results below are
> from the corrected runs.

**Results (corrected).** 50 samples per |S|, 120 s/cube, dense vs matched
star baseline (same # fixed vars).

*Cube structure.* Dropping internally-mono assignments compresses the dense
cube space substantially (dense regions have induced triangles; star regions
have none since N(0) is triangle-free):

| \|S\| | induced △ | surviving dense cubes | compression | surviving star cubes |
|---:|---:|---:|---:|---:|
| 16 | 12 | 1,283 (exact) | 51× | 32,768 |
| 20 | 16 | 7,305 (exact) | 143× | 524,288 |
| 30 | 27 | 463,497 (exact) | 2,317× | 5.37e8 |
| 42 | 42 | ≈4.86e7 (est., 2e7 samples) | ≈90,500× | 2.20e12 |

*Unit propagation (extra vars fixed beyond the cube, min/median/max; 0
conflicts throughout):*

| \|S\| | dense region | star baseline |
|---:|---:|---:|
| 16 | 0 / 0 / 0 | 12 / 19 / 23 |
| 20 | 0 / 0 / 0 | 15 / 26.5 / 34 |
| 30 | 0 / 0 / 0 | 52 / 62 / 73 |
| 42 | 0 / 0 / 0 | 96 / 115 / 128 |

*Conquer (kissat, 120 s):* **every one of the 400 sampled cubes (200 dense +
200 star) timed out** — 0 SAT, 0 UNSAT, at all |S| for both families. Median
solve time 120.003 s across the board.

**Read.** The corrected experiment *refutes* the dense-cubing hypothesis, and
informatively so. Triangle-dense induced regions are **self-contained**:
triangles inside W are fully assigned (and non-mono) by the cube, while every
boundary triangle keeps ≥ 2 free edges, so a dense cube triggers **zero**
full-CNF unit propagation — it communicates almost nothing to the rest of
φ(G₁₂₇). Star cubes propagate much more (fixing star edges forces
N(0)-internal edges, ~115 vars at |S|=42). Yet **both conquer identically
badly**: all cubes time out at 120 s regardless of |S| or propagation depth.
So the barrier is *not* a lack of shallow propagation (v2's implicit read);
even the high-propagation star cubes don't crack, and the low-propagation
dense cubes are no worse. G₁₂₇'s hardness lives in deep CDCL search after
propagation — no shallow structural decomposition tried here (star, march_cu,
or triangle-dense) unlocks it. This is a cleaner diagnosis than v2's and
quantitatively closes the "better cubing variables" avenue on this hardware.

---

## Artifacts (this wave)

- `fractional_lp.py` — Attack A: local-LP certificate + numerical check (PASS).
- `dense_cube.py`, `conquer_dense.py`, `measure_up.py` — Attack B tooling.
- `dense_table.json`, `dense_up.json`, `dense_results.json` (+ star-baseline
  counterparts) — Attack B measurements.
- Toolchain: kissat 4.0.4, cadical 3.0.1, march_cu, drat-trim, lrat-check
  built under `/home/ubuntu/sat-tools` (see blueprint update).

## Bottom line

G₁₂₇ → (3,3)ᵉ remains undecided. New this wave: (A) a rigorous proof that the
triangle-local (SA level-2) fractional relaxation is worthless (optimum 0),
bounding what counting arguments can achieve; (B) a measured comparison showing
triangle-dense cubing triggers zero cross-CNF propagation and conquers no
faster than star cubing (all 400 sampled cubes time out), so "better cubing
variables" does not help. The problem's hardness is concentrated in deep CDCL
reasoning that no shallow structural decomposition on this hardware unlocks —
consistent with 20 years of the problem staying open.

## Fresh post-restart datapoint (2026-07-25T15:48Z)
- kissat 4.0.4 on `runs/P22/v2/sb.cnf` (symmetry-broken G127 arrowing, 10884 vars / 68860 clauses), 590s wall, 64 MB RSS -> `s UNKNOWN` (no verdict). Reconfirms non-termination; G127 arrowing remains undecided on this hardware.

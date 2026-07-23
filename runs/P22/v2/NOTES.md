# P22-v2 — G₁₂₇ → (3,3)ᵉ ? (SAT attack with symmetry breaking)

Session: 2026-07-23, Devin ultra run (8 cores, 32 GB).
Goal: decide whether G₁₂₇ = G(127, cubic residues mod 127) arrows (3,3)ᵉ.
UNSAT ⇒ Fe(3,3;4) ≤ 127 (from 786). SAT ⇒ refutes Exoo's conjecture.

**Outcome: UNDECIDED (negative result documented).** No solver came close to
deciding the instance; all structured/heuristic SAT-side searches strongly
support the arrowing conjecture (no coloring below ~240 mono triangles found;
no circulant coloring works). Details below.

## 1. Statement fidelity & priority

See `PRIORITY.md`. Statement checked against Radziszowski–Xu 2007 §7; all
graph invariants reproduced exactly (`verify_props.py` PASS: 2667 edges,
9779 triangles, 42-regular, K₄-free, α = 11, |Aut| ≥ 5334 = 127·42).
Question confirmed open through Bikov–Nenov (AJC 77, 2020) and the two most
recent Folkman papers (arXiv:2506.14942, arXiv:2605.16542). Note: the task
prompt's "Aut order divisible by 127·63" is incorrect — RX07 and our
computation give 127·42 = 5334.

## 2. Encoding

`gen_cnf.py`: one variable per edge (red/blue), per triangle two clauses
(x∨y∨z) ∧ (¬x∨¬y∨¬z). SAT ⇔ G₁₂₇ ↛ (3,3)ᵉ. Identical to RX07 §7's φG:
2667 vars, 19558 clauses. Self-test (`selftest_encoding.py`): K₅ SAT,
K₆ UNSAT (R(3,3)=6) — PASS.

- `plain.cnf`: + unit clause fixing edge {0,1} red. Sound by global color
  swap alone (no automorphism needed).
- `sb.cnf`: + lex-leader constraints X ≤_lex σ(X) for the 84 symmetries
  {σ_a, σ_a∘flip : a ∈ C} where σ_a : x ↦ ax is the stabilizer of vertex 0
  (42 verified graph automorphisms), flip = global color swap; lex prefix =
  100 edge variables (the 42 star edges of vertex 0 first). Soundness:
  standard lex-leader (Crawford et al.) w.r.t. any subset of the formula's
  symmetry group — only graph automorphisms + color swap are used, exactly
  as required. 10884 vars, 68860 clauses.

Symmetry-breaking honesty note: |Aut × flip| = 10668 ≪ 2^2667, so symmetry
breaking cannot make this instance tractable by itself; it only removes a
~10⁴ factor. Confirmed empirically (§4).

## 3. SAT-side searches (looking for a good coloring — would kill the candidate)

- **Circulant colorings, exhaustive** (`circulant_colorings.py`): every
  translation-invariant coloring is determined by a color per difference
  class {c, 127−c}, 21 classes ⇒ 2²¹ = 2,097,152 colorings, all checked
  exhaustively: **none avoids a monochromatic triangle.** So any witness of
  G₁₂₇ ↛ (3,3)ᵉ, if it exists, is non-circulant. (Fast, exact, deterministic.)
- **Focused random walk** (`walk.c`, WalkSAT-style on mono-triangle count,
  6 seeds × noise ∈ {8,12,15,20,25,40}%, ~10⁹ flips total): best found
  **243 monochromatic triangles** (random baseline ≈ 9779/4 ≈ 2445).
  Plateau ~243–301 across all seeds; no downward trend after the first
  minutes. Simulated annealing (`anneal.c`) was weaker (best 655).
- Consistent with LRX 2012's MAX-CUT heuristics never finding a good cut:
  the SAT side looks empty; evidence for the arrowing conjecture.

## 3b. Symmetric-coloring exclusion (new partial results, machine-verified)

nauty (dreadnaut) confirms |Aut(G₁₂₇)| = **exactly 5334**, so
Aut = Z₁₂₇ ⋊ Z₄₂ (translations ⋊ Stab(0), Stab(0) = mults by cubic residues,
cyclic of order 42). Classification of nontrivial subgroups H ≤ Aut:
- If H contains a nontrivial translation, it contains all of Z₁₂₇ (127
  prime), so an H-invariant coloring is circulant — **excluded exhaustively**
  (§3, all 2²¹ circulant colorings hit a mono triangle).
- Otherwise gcd(|H|,127)=1, and by Schur–Zassenhaus conjugacy H is conjugate
  to a subgroup of Stab(0) ≅ Z₄₂; conjugating the subgroup is equivalent to
  translating the coloring, so the restricted problems are isomorphic. Any
  such H contains an element of prime order q ∈ {2,3,7}.

Restricted instances (`invariant_colorings.py`: collapse edge variables to
H-orbits; SAT ⇔ an H-invariant good coloring exists):
- **order 3** (also 6, 21, 42): some triangle lies inside a single edge-orbit
  ⇒ trivially UNSAT (no invariant coloring can 2-color it non-mono).
- **order 7** (381 orbit-vars, 2794 clauses): kissat UNSAT in 0.04 s;
  DRAT certificate checked by drat-trim: VERIFIED (`inv_7.drat`).
  Order 14 likewise UNSAT+VERIFIED (implied by 7, checked independently).
- **order 2** (⟨x ↦ −x⟩, 1344 orbit-vars, 9800 clauses): the hard case —
  see run log `kissat_inv2.log` (status recorded below).

Consequence if order-2 resolves UNSAT: **every 2-coloring of E(G₁₂₇)
avoiding monochromatic triangles (if one exists) has trivial stabilizer in
Aut(G₁₂₇)** — i.e. a counterexample to Exoo's conjecture must be completely
asymmetric. Already unconditionally: no witness coloring is invariant under
any automorphism of order 3, 6, 7, 14, 21, 42, or 127 (or any subgroup
containing such).

## 4. UNSAT-side solver runs

- **kissat 4.0.4** on `plain.cnf` and `sb.cnf`, single-threaded, DRAT logging
  on, multi-hour runs: no termination and no meaningful progress signal
  (remaining-variables gauge stayed at 2666/2667 resp. ~39–100%; conflict
  rate ~30k/s). RX07 observed the same with zChaff/march_eq in 2007;
  modern CDCL alone still cannot touch φ(G₁₂₇).
- **Cube-and-conquer** (march_cu from marijnheule/CnC, built with -fcommon):
  - depth 10: 1024 cubes, 0 refuted leaves; average cube "weight" 2646
    (out of 2667 free vars) — lookahead fixes essentially nothing: the
    instance has no easily-refutable branches near the top.
  - depth 16: 65536 cubes, 0 refuted leaves, average weight 2631.
  - Sampled conquering with kissat: 30/30 depth-10 cubes TIMEOUT at 60 s;
    200-cube depth-16 sample: see `cnc_d16_sample.log` (essentially all
    TIMEOUT at 30 s). Cubing on ~16 of 2667 edge variables does not
    decompose the problem; march_cu's lookahead heuristic finds no leverage.
- Estimated hardness: with ~10–16 assumed literals producing no measurable
  simplification, a full CnC tree would need depth ≫ 40 (≫ 10¹² cubes) —
  far beyond a single machine. This is consistent with the problem having
  been open for ~20 years despite explicit SAT formulations.

## 5. What would move the needle (recommendations)

1. **H₃ first** (P22 target 1): 63 vertices — the Mulrenin–Van Overberghe
   candidate is a much smaller instance and per arXiv:2506.14942 has real
   structural evidence; the K₄-destroying alterations of H₃ should be
   SAT-tested before pouring more compute into G₁₂₇.
2. For G₁₂₇: SAT-modulo-symmetries or an orbit-based encoding (color
   variables per edge-orbit of chosen subgroups) rather than plain lex; or
   the RX07 extension strategy (enumerate colorings of a dense subgraph, then
   extend) with modern hardware; or massive distributed CnC (10⁶ CPU-h scale).
3. The circulant exclusion (§3) suggests trying to prove arrowing restricted
   to structured coloring families as partial results (e.g. colorings
   invariant under any nontrivial automorphism — the remaining subgroup types
   are the 42 conjugates of Stab(0) subgroups; a mult-invariant analysis is a
   finite, feasible follow-up).

## 6. Artifacts

- `build_g127.py`, `verify_props.py` — construction + independent property
  verification (PASS).
- `gen_cnf.py`, `selftest_encoding.py` — CNF generation + encoding self-test.
- `plain.cnf`, `sb.cnf` not committed (regenerable, ~1–3 MB); DRAT logs not
  kept (no UNSAT result).
- `walk.c`, `anneal.c`, `circulant_colorings.py`, `cnc_run.py` — search tools.
- `verify_coloring.py` — independent witness checker (unused: no witness).
- Logs: `kissat_plain.log`, `kissat_sb.log`, `walk_*.log`,
  `cnc_d16_sample.log`.

## 7. Compute spent

~8 cores for ~4 h: 2 × kissat CDCL (plain, sb), 6→2 × walk local search,
march_cu cubing (d10/d16/d20 attempt), 230 sampled cube-conquer kissat runs.

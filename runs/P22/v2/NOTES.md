# P22-v2 — G₁₂₇ → (3,3)ᵉ ? (SAT attack with symmetry breaking)

Session: 2026-07-23, Devin ultra run (8 cores, 32 GB).
Goal: decide whether G₁₂₇ = G(127, cubic residues mod 127) arrows (3,3)ᵉ.
UNSAT ⇒ Fe(3,3;4) ≤ 127 (from 786). SAT ⇒ refutes Exoo's conjecture.

**Outcome: main question UNDECIDED, but a new machine-verified partial
theorem was established:**

> **Theorem (symmetric-coloring exclusion).** Every 2-coloring of E(G₁₂₇)
> without a monochromatic triangle — if one exists — has trivial stabilizer
> in Aut(G₁₂₇). Equivalently: any witness that G₁₂₇ ↛ (3,3)ᵉ must be
> completely asymmetric (invariant under no nontrivial automorphism).

Proof: exhaustive + DRAT-certified case analysis over the subgroup lattice of
Aut(G₁₂₇) = Z₁₂₇ ⋊ Z₄₂ (order 5334, confirmed exactly by nauty) — see §3b.
All heuristic/structured SAT-side searches support Exoo's arrowing conjecture
(no coloring below 242 mono triangles found). The unrestricted SAT instance
remains far beyond current solvers (§4).

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
  8 seeds × noise ∈ {8,12,15,20,25,40}%, ~5×10⁹ flips total): best found
  **242 monochromatic triangles** (random baseline ≈ 9779/4 ≈ 2445).
  Plateau ~242–301 across all seeds; no downward trend after the first
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
- **order 2** (⟨x ↦ −x⟩, 1344 orbit-vars, 9800 clauses): too hard for plain
  CDCL (kissat: no progress in 20+ min, `kissat_inv2.log`), but solved by
  **cube-and-conquer with full certification**:
  - march_cu depth-12 cubing: 4096 cubes (`inv2_cubes_d12.icnf.gz`).
  - Cube-cover completeness PROVED: the CNF {¬cubeᵢ} is UNSAT, DRAT checked
    by drat-trim (`check_cover.py`: "COVER VERIFIED").
  - All **4096/4096 cubes UNSAT, each with its own DRAT certificate checked
    by drat-trim** (`cnc_prove.py`; ledger `inv2_d12_status.txt`: 4096
    distinct indices 0–4095, all VERIFIED; logs `cnc_inv2.log`,
    `cnc_inv2b.log`). Per-cube times mostly < 20 s, none hit the 300 s
    limit; total ≈ 2.5 h on 6–8 workers.

This completes the theorem stated at the top: combined with the circulant
exclusion (order 127) and orders 3 and 7, **no good coloring of E(G₁₂₇) is
invariant under any nontrivial automorphism**. Independent re-verifier:
`solutions/P22/verify_symmetric_exclusion.py` (PASS).

## 4. UNSAT-side solver runs

- **kissat 4.0.4** on `plain.cnf` and `sb.cnf`, single-threaded, DRAT logging
  on: 68 min resp. 63 min CPU in the first runs (~40M conflicts each) plus
  follow-up runs, no termination and no meaningful progress signal
  (remaining-variables gauge stayed at 2666/2667 resp. ~38–100%). RX07
  observed the same with zChaff/march_eq in 2007; modern CDCL alone still
  cannot touch φ(G₁₂₇). Symmetry breaking gave no observable advantage,
  as predicted.
- **Cube-and-conquer** (march_cu from marijnheule/CnC, built with -fcommon):
  - depth 10: 1024 cubes, 0 refuted leaves; average cube "weight" 2646
    (out of 2667 free vars) — lookahead fixes essentially nothing: the
    instance has no easily-refutable branches near the top.
  - depth 16: 65536 cubes, 0 refuted leaves, average weight 2631.
  - Sampled conquering with kissat: 30/30 depth-10 cubes TIMEOUT at 60 s;
    depth-16 sample: 152/152 TIMEOUT at 30 s (`cnc_d16_sample.log`).
    Cubing on ~16 of 2667 edge variables does not decompose the problem;
    march_cu's lookahead finds no leverage (contrast with the
    order-2-invariant instance, where depth-12 CnC succeeded fully).
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
- `plain.cnf`, `sb.cnf` not committed (regenerable via `gen_cnf.py`); their
  DRAT logs not kept (no UNSAT result).
- `invariant_colorings.py`, `inv_2.cnf`, `inv_7.cnf/.drat`, `inv_14.cnf/.drat`
  — orbit-collapsed instances + certificates.
- `inv2_cubes_d12.icnf.gz`, `inv2_d12_status.txt`, `cover.cnf`,
  `cnc_prove.py`, `check_cover.py` — the certified order-2 CnC proof
  (per-cube DRATs regenerable; each was drat-trim-checked before deletion).
- `walk.c`, `anneal.c`, `circulant_colorings.py`, `cnc_run.py` — search tools.
- `verify_coloring.py` — independent witness checker (unused: no witness).
- `solutions/P22/verify_symmetric_exclusion.py` — standalone re-verifier of
  the theorem (PASS, < 1 s + optional kissat re-solve).
- Logs: `kissat_plain.log`, `kissat_sb.log`, `walk_*.log`,
  `cnc_d16_sample.log`, `cnc_inv2*.log`, `kissat_inv2.log`.

## 6b. Resumed run (second wave)

The session was resumed with instructions to push harder. Additional work:

- **Priority re-check** (fresh Exa searches, incl. "solved/certificate/2026"
  angles): still no resolution of G₁₂₇ → (3,3)ᵉ anywhere. The strongest
  related results remain LRX 2012 (Fe(3,3;4) ≤ 786 via G₇₈₆ MAX-CUT) and the
  2025/26 papers; none touch the G₁₂₇ decision.
- **Star-branching hardness measurement** (`scaling.py`): fix the colors of
  k of the 42 star edges at vertex 0 uniformly at random and run kissat.
  Result: k = 25, 30, 35 (3/3 each TIMEOUT at 240 s), k = 38 (4/4 at 300 s)
  and even k = 41 — all free star edges fixed — (6/6 at 300 s, 3/3 at 240 s)
  all give instances kissat cannot refute within the limit. So a
  cube-and-conquer tree over the full star (the natural "orbit
  representative" cube set, 2⁴¹/84 classes after Stab(0)×flip reduction)
  would cost ≳ 2⁴¹/84 · 300 s ≈ 8·10¹² core-seconds ≈ 2.5·10⁵ core-years.
  Star-edge cubing is quantitatively hopeless, matching the march_cu picture.
  - Cautionary bug note: a first version of this experiment (and of
    `star_tree.py`) produced spurious instant "UNSAT" because random cubes on
    var 1 clashed with the unit clause `1 0` already in `plain.cnf`, and
    (in `star_tree.py`) because a red-unit clause contradicted the flip
    lex-leader constraint, which forces var(0,1)=False. Both are fixed in the
    committed versions; no claim was based on the buggy runs.
- **UP-only star DFS** (`star_dfs.c`): unit propagation over the triangle
  clauses can never refute a star-only assignment — triangles inside N(0)
  would be K₄s through 0, and G₁₂₇ is K₄-free, so the forced N(0)-internal
  edges never interact. 176M nodes, 0 conflicts. This explains *why* the
  instance resists top-level cubing: all shallow pruning must come from deep
  CDCL reasoning, not propagation.
- **BreakID + parallel CDCL**: BreakID (krr/breakid) on the unit-free base
  formula detects 6 generators (the full 2·5334 group incl. flip) and adds
  6084 sound lex-leader clauses (`breakid_out.cnf`, 2917 vars, 25642
  clauses). gimsatul 1.1.3 (4 threads each) ran on `sb.cnf` and
  `breakid_out.cnf` for hours: no termination, no progress signal. Consistent
  with everything above.
- **SAT-side improvement**: continued focused-walk runs improved the best
  known coloring from 242 to **232 monochromatic triangles** (out of 9779) —
  i.e. ≥ 9547 triangles simultaneously bichromatic, still 232 short of a
  counterexample. The plateau structure (many restarts stuck at ~232–245)
  continues to support the arrowing conjecture.

Bottom line unchanged: G₁₂₇ → (3,3)ᵉ remains undecided; the quantitative
hardness estimates above are now measured, not guessed.

## 7. Compute spent

~8 cores for ~4.5 h: 2 × kissat CDCL on the main instance (68/63 min + extra),
6→2 × walk local search (~10⁹ flips), march_cu cubing (d10/d16/d20 on main;
d12/d18 on inv_2), ~230 sampled cube-conquer runs on the main instance, and
the full certified 4096-cube CnC proof of the order-2 case (~2.5 h).

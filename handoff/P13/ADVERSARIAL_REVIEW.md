# Adversarial review: nonexistence of a (9,6,1)-PMD (runs/P13-v3)

Reviewer: independent Devin session (adversarial, per `context/METHODOLOGY.md`).
Claim under review: **no (9,6,1)-perfect Mendelsohn design exists** (`solutions/P13/NONEXISTENCE.md`).

## VERDICT: CONFIRMED

The claimed nonexistence is correct as far as machine verification can establish it, and
v=9 was genuinely open in the literature we could access. Details and residual risks below.

---

## 1. Statement fidelity

Primary-source definition checked against Abel & Bennett, *The existence of (v,6,λ)-perfect
Mendelsohn designs with λ>1*, Des. Codes Cryptogr. 40 (2006) 211–224 (full text retrieved),
and Bennett–Zwicker–Chang, Discrete Math. 309 (2009) 4772–4783 (full text retrieved):
a (v,k,λ)-PMD is a collection of cyclically ordered k-tuples (blocks of k *distinct* points)
of a v-set such that for every t = 1..k−1 every ordered pair of distinct points is t-apart
in exactly λ blocks; b = λv(v−1)/k. For (9,6,1): b = 12, necessary condition
v ≡ 0,1,3,4 (mod 6) satisfied (9 ≡ 3).

All four programs in this run encode exactly this object:

- `solutions/P13/verify.py` — checks distinctness within blocks, b = v(v−1)/k, and
  exact-once coverage of every ordered pair at every distance t = 1..5. Faithful.
- `runs/P13/v3/gen_cnf.py` — cells one-hot, symbol at-most-once per block, and for every
  (t, ordered pair) an exactly-one over Tseitin product vars e ↔ x[b][p][u] ∧ x[b][(p+t)%6][w].
  Faithful. (Block count fixed at b = 12 is forced by the definition: 6b distance-1 slots
  must equal v(v−1) = 72.)
- `runs/P13/v3/pmd_cpsat.py` — same constraints in CP-SAT plus a redundant (implied)
  global count of v−1 occurrences per symbol. Faithful.
- `runs/P13/v3/pmd_dfs.py` — exact cover of the 5·v² (pair, distance) slot universe by
  canonical blocks. Faithful.

### Symmetry-breaking soundness (gen_cnf.py, the DRAT-certified encoding)

1. **Block 0 = (0,1,2,3,4,5)** — sound WLOG: any putative design has ≥1 block; relabel
   its points along the cyclic order. Pure point-relabeling, no interaction with other
   constraints.
2. **Rotation-canonical blocks** (position 0 = block minimum; clauses forbid
   x[b][0][s] ∧ x[b][p][s′] for s′ < s) — sound: blocks are cyclic tuples, so each block
   has exactly one rotation with its (unique) minimum first. Block 0 is consistent with this.
3. **Blocks 0..7 are exactly the blocks containing point 0, with 0 at position 0** — sound:
   every point lies in exactly v−1 = 8 blocks (v−1 occurrences, at most one per block);
   in any 0-containing block the minimum is 0, so rotation-canonicity puts 0 at position 0;
   a set of blocks can be listed with the 0-blocks first.
4. **0-blocks strictly ordered by position-1 symbol** — sound: the distance-1 successors of
   0 across the 8 zero-blocks are exactly {1,...,8}, each once (definition, t=1), so the
   keys are distinct and some ordering is strictly increasing. Consistency with block 0
   fixed: block 0's successor of 0 is 1, the minimum possible, so block 0 may sit first. ✔
5. **Remaining blocks ordered non-strictly by position-0 (minimum) symbol** — sound: any
   set can be sorted non-strictly.

Each rule maps an arbitrary design to a relabeled/reordered design satisfying all rules
simultaneously (relabel → rotate each block → sort), so UNSAT of the constrained instance
implies nonexistence. No unsound interaction found. The CP-SAT model's optional
first-occurrence rule (flagged "potentially unsound" in NOTES.md) was correctly excluded
from the headline runs, and I reproduced UNSAT with it off (12.2 s on this machine).

The DFS uses only rule 1 (weakest assumption) and is exhaustive on the quotient.

## 2. Priority — was (9,6,1) genuinely open?

- **Abel–Bennett 2006, Thm 1.4** (full text): for λ=1, k=6 the necessary conditions are
  sufficient *except v = 6, 10* and possibly for listed exceptions including, for
  v ≡ 3 (mod 6), **the interval [9, 135]** — i.e. v = 9 explicitly among the possible
  exceptions (open), and v = 10 already settled nonexistent (their Thm 1.3, via the
  nonexistence of a (10,6,5)-BIBD nested with a (10,3,2)-BIBD, Hishida et al.). The run's
  correction of the problem file (v=10 wrongly listed open) is right; CPro1's
  `OPEN_INSTANCES` (which includes [10,6,15]) is the evident source of the error.
- **Bennett–Zwicker–Chang 2009 (Discrete Math. 309), Thm 1.3** — same status: v ≡ 3 (mod 6)
  open interval [9,135]. This is the latest comprehensive PMD summary found.
- **Citation sweep**: Semantic Scholar citations of Abel–Bennett 2006 (3, none on k=6 λ=1),
  of Abel–Bennett–Zhang 2000 (27, none resolving k=6 λ=1 cases after 2009), and of
  Bennett–Zwicker–Chang 2009 (1, on K={5,8}). Griggs–Kozlik 2020 closed k=5 only.
- **Artifact search**: GitHub code search for "perfect mendelsohn" finds only CPro1
  (heuristic search, v=9 unsolved there) and this repo; Zenodo: no hits. No competing claim
  of existence or nonexistence for (9,6,1) found.
- The CRC Handbook of Combinatorial Designs (2nd ed., 2007) table VI.35 derives from the
  same Abel–Bennett/Miao–Zhu results; no independent access to the printed table was
  possible in this session (see residual risks).

Conclusion: v = 9 was a genuine possible exception (open) in every accessible source, and
this result is the first recorded resolution.

## 3. Independent hostile verification

All artifacts in `/tmp` were regenerated on this reviewer's machine (kissat and drat-trim
built from source, current masters).

1. **Shipped proof re-checked**: `pmd9_unsat.cnf.gz`/`pmd9_unsat.drat.gz` decompressed;
   `drat-trim pmd9_unsat.cnf pmd9_unsat.drat` → **`s VERIFIED`** (45.7 s, 15211 RAT lemmas
   in core — matches NOTES.md).
2. **CNF provenance confirmed**: `gen_cnf.py 9` regenerated on this machine is
   **byte-identical** (`cmp`) to the shipped `pmd9_unsat.cnf`, so the audited encoding is
   exactly what the proof refutes.
3. **Reviewer's own CNF** (`my_pmd.py cnf`, written from the definition alone, with a
   *different* symmetry-breaking scheme: block0 fixed + rotation-min + strict lexicographic
   block order on (pos0,pos1) encoded as quartic forbidden patterns — no zero-block
   partitioning): 26,568 vars / 1,033,458 clauses; kissat → **UNSAT**; fresh DRAT proof
   (39 MB) checked by drat-trim → **`s VERIFIED`** (153 s).
4. **Reviewer's own exhaustive DFS** (`my_pmd.py dfs`, written independently; only WLOG
   block (0..5) assumed): exhausts in **581,650 nodes → no design**. (Node count coincides
   with the run's `pmd_dfs.py` because both use the same natural branching rule —
   lexicographically-first uncovered distance-1 pair over canonical blocks — a deterministic
   quotient; this is replication, not code sharing: sanity v=7 → SAT with witness PASSing
   my own verifier, v=6 → UNSAT.)
5. **Run's CP-SAT model re-run** (`pmd_cpsat.py 9 240 8 --no-firstocc`): **UNSAT, 12.2 s**.

Four mechanically independent refutations (two with checked DRAT certificates, one of them
from an encoding written by a hostile reviewer) plus an exhaustive combinatorial search.

## Residual risks

1. **Common-mode definition error** — mitigated to near zero: the definition was re-read
   from two primary papers and CPro1's independent problem_def; all encodings agree with it.
2. **Literature coverage**: I could not access the printed CRC Handbook table VI.35 nor the
   full text of Hantao Zhang's "Combinatorial Designs by SAT Solvers" (Handbook of
   Satisfiability, 2009 ch. 17 / 2021 ch. 21), which reports SAT attacks on Mendelsohn
   designs. Its abstract-level description and the 2009/2020-era design-theory surveys give
   no indication that (9,6,1) was resolved there, but this remains the largest (still small)
   priority risk. A pre-announcement email to R.J.R. Abel / F.E. Bennett or a check of the
   printed Handbook table is recommended.
3. **Toolchain trust**: kissat/drat-trim are independent, widely trusted tools; both proofs
   were checked with drat-trim only. Paranoia option: re-check certificates with a verified
   checker (cake_lpr / GRAT). Not done here.
4. Unpublished/in-press resolutions cannot be excluded by any search.

## Verdict

**CONFIRMED** — (9,6,1)-PMD nonexistence is sound (encodings faithful, symmetry breaking
sound, proof certificates verified, independently re-derived), and the case was open per
Abel–Bennett 2006 and all later accessible literature. v=10 correction also confirmed.

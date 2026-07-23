# Adversarial review: P14 nonexistence claims (runs/P14-v1)

Reviewer: independent Devin session (adversarial, per `context/METHODOLOGY.md`).
Claims under review (`solutions/P14/NONEXISTENCE.md`, `runs/P14/v1/NOTES.md`): no BTD exists
for **(14,18; 7,1,9; 7,4)**, **(12,15; 6,2,10; 8,6)**, **(12,20; 4,3,10; 6,4)** — each via
CP-SAT INFEASIBLE + independent CNF, kissat UNSAT, drat-trim-verified DRAT certificates.

## VERDICT: CONFIRMED (all three instances)

All three nonexistence claims reproduce end-to-end on this machine, including from a CNF
encoding written from scratch by this reviewer (different variable scheme, different
cardinality encoding, opposite lex orientation), and the instances were genuinely open.
Details and residual risks below.

---

## 1. Statement fidelity

**Definition pinned against three primary sources (all retrieved in full):**

- **Kunkle & Sarvate, "Balanced (Part) Ternary Designs"** (CRC Handbook of Combinatorial
  Designs section, source text at kunklet.people.charleston.edu/section.pdf): a
  BTD(V,B; ρ1,ρ2,R; K,Λ) arranges V elements into B multisets (blocks) of cardinality K
  (K ≤ V) with (1) each element appearing R = ρ1+2ρ2 times, multiplicity one in exactly ρ1
  blocks and two in exactly ρ2 blocks; (2) for every pair of distinct elements v,w,
  Σ_b m_vb·m_wb = Λ.
- **CPro1 `problem_def.py`** (cloned github.com/Constructive-Codes/CPro1,
  `CPro1/design_definitions/balanced-ternary-design/problem_def.py`): identical, with the
  V×B incidence-matrix formulation (entries in {0,1,2}, row sums R, column sums K), and its
  verifier `v()` checks exactly rows/columns/ρ-counts/pair inner products.
- **Rosin, arXiv:2501.17725 (CPro1 paper), Table 1**: verbatim the same definition and the
  parameter convention (V,B; p1,p2,R; K,L).

The repo's `problems/P14-balanced-ternary-designs.md`, `solutions/P14/verify.py`, and all
three encodings in this run implement exactly this object. Parameter convention
(v,b; ρ1,ρ2,r; k,λ) = (V,B; p1,p2,R; K,L) is consistent everywhere. Necessary counting
identities V·R = B·K and B·K² − V·(p1+4·p2) = Λ·V·(V−1) re-derived and machine-checked:
hold for all three instances (so no cheap counting refutation of the *encodings* exists —
the instances are admissible and nonexistence is genuinely combinatorial).

**Encoding audit (hard, machine-checked).** I model-counted both the run's CNF encoder
(`encode_sat.py`) and my own independent encoder against brute-force enumeration of ALL
{0,1,2}-matrices on tiny admissible instances (`review_validate.py` alongside this file):

| instance | brute: all valid | brute: doubly-lex-sorted (dec) | encode_sat.py (with lex) | review_encode.py (no lex) | review_encode.py (with lex) |
|---|---|---|---|---|---|
| (3,3;1,1,3;3,2) | 12 | 1 | 1 | 12 | 1 |
| (3,4;2,1,4;3,3) | 48 | 1 | 1 | 48 | 1 |
| (4,4;0,2,4;4,4) | 0 | 0 | 0 | 0 | 0 |

(Reproduce: `python3 review_validate.py`.)

Exact agreement in every cell — the constraint encodings (row ρ-counts, column sums via
literal duplication in seqcounter, AND-product pair sums) are exactly right, not just
satisfiability-equivalent.

**Weighted-cardinality-by-literal-duplication** (the one exotic device in `encode_sat.py`):
independently re-tested — 200 random weighted exactly-k constraints (weights 1–3, n ≤ 6)
encoded by literal duplication in pysat seqcounter, model counts compared to brute force:
all 200 exact. PASS.

**Double-lex symmetry breaking** (the only solution-removing device):
- Theory: Flener–Frisch–Hnich–Kiziltan–Miguel–Pearson–Walsh, *Breaking Row and Column
  Symmetries in Matrix Models*, CP 2002 — every matrix class under row×column permutation
  contains a doubly-lex-ordered member. This applies to arbitrary totally ordered entry
  domains, including {0,1,2}. Row and column permutations map BTDs to BTDs (elements are
  interchangeable; blocks are an unordered multiset), so UNSAT under double-lex ⇒ UNSAT.
- Implementation: I isolated the lex clauses of BOTH CNF encoders (constraints stubbed out)
  and model-counted all 3×3 {0,1,2} matrices: `encode_sat.py`'s non-increasing double-lex
  admits exactly the 1169 doubly-non-increasing matrices (brute force: 1169), and
  `review_encode.py`'s independent implementation admits exactly the same 1169. Both exact.
- The CP-SAT model's `add_lex_ge` was read line-by-line: standard prefix-equality chain,
  correct.

No statement-fidelity or encoding-soundness problems found.

## 2. Priority — were the instances genuinely open?

- **Kunkle–Sarvate Handbook table** (rows 43, 76, 79 = design-list rows (43),(76),(79) of
  Billington–Robinson's list): (14,18;7,1,9;7,4), (12,15;6,2,10;8,6), (12,20;4,3,10;6,4)
  all have **known b2's: none** — no BTD with these parameters known for ANY b2, i.e.
  existence open as of the Handbook.
- **Kaski–Östergård, *Enumeration of Balanced Ternary Designs*, Discrete Appl. Math. 138
  (2004)** (results page users.ics.aalto.fi/pkaski/btd.html retrieved): their classification
  covers the small-R classes; row 43 = (14,18;7,1,9;7,4) appears in their table **with no
  Nd/Ns entries** (not classified — too large), and the two R=10 instances are beyond the
  classified range. Not resolved there.
- **CPro1 papers**: arXiv:2501.17725 Table 1 lists all three with "?" and no literature
  progress (the [Greig, 2002] column resolves only (12,26;3,5,13;6,5) as nonexistent);
  its Appendix/repo shows constructions for the 7 solved siblings only. arXiv:2505.23881
  (May 2025, reasoning models) adds (16,22;9,1,11;8,5) and (21,21;12,1,14;14,9) but not
  these three. Cloned CPro1 repo confirms: `OPEN_INSTANCES` still contains all three;
  `designs/balanced-ternary-design/` has result files only for the solved siblings.
- **Citation sweep**: Semantic Scholar lists only two citing works for Kaski–Östergård 2004
  (Kaski–Östergård 2005 classification-algorithms book chapter; Greig 2003 constructions
  chapter) — nothing later resolving these cells.
- **Artifact sweep** (2026-07-23): GitHub code search for the parameter strings (e.g.
  "12,15;6,2,10;8,6") hits only this repo; repo search for "balanced ternary design" finds
  nothing relevant; Exa web/scholar searches for BTD nonexistence/SAT/DRAT 2025–2026 find
  nothing touching these cells; Zenodo/OpenReview: nothing beyond the two CPro1 papers.

I found **no prior resolution and no competing claim**. Priority stands. (Caveat: I could
not access the printed 2nd-edition Handbook ch. VI.2 tables directly, only the
Kunkle–Sarvate source text they derive from, plus CPro1's Handbook-derived instance list.)

## 3. Independent verification (this machine, 2026-07-23)

**(a) Shipped-pipeline re-run.** DRAT proofs are not committed (1 GB+); per NOTES.md they
are regenerated deterministically. I regenerated all three CNFs with the run's
`encode_sat.py` and re-ran kissat 4.0.4 + drat-trim from clean upstream clones:

| instance | CNF (vars/clauses, = NOTES.md where reported) | kissat | proof | drat-trim |
|---|---|---|---|---|
| (12,20;4,3,10;6,4) | 109,544 / 227,650 | s UNSATISFIABLE (exit 20) | 881,275,914 B (matches reported 881 MB) | **s VERIFIED** (841 s) |
| (12,15;6,2,10;8,6) | 115,794 / 237,980 (= NOTES.md) | s UNSATISFIABLE (exit 20) | 1.19 GB | **s VERIFIED** (1197 s) |
| (14,18;7,1,9;7,4)  | 134,238 / 278,728 (= NOTES.md) | s UNSATISFIABLE (exit 20) | 1.27 GB | **s VERIFIED** (1443 s) |

**(b) Reviewer's own encoding, written from the definition alone**
(`runs/P14/v1/review_encode.py`, committed with this review). Deliberately different at
every design point except the lex orientation: order-encoding variables t1 = (m≥1),
t2 = (m≥2) instead of one-hot x1/x2; column sums and pair products expressed WITHOUT
literal duplication (m = t1+t2 makes all weights 1); totalizer cardinality encoding
instead of seqcounter; independently implemented prefix-chain lex over order-encoded
comparisons. Sanity: SAT on dev instance BTD(4,8;2,3,8;4,6) with witness PASSing
`solutions/P14/verify.py`; exact brute-force model-count agreement on the tiny instances
above (with and without lex).

| instance | reviewer CNF (vars/clauses) | kissat | proof | drat-trim |
|---|---|---|---|---|
| (12,20;4,3,10;6,4) | 82,884 / 534,914 | s UNSATISFIABLE (exit 20), ~9 min | 0.73 GB | **s VERIFIED** (860 s) |
| (12,15;6,2,10;8,6) | 58,120 / 316,135 | s UNSATISFIABLE (exit 20), ~9 min | 0.74 GB | **s VERIFIED** (876 s) |
| (14,18;7,1,9;7,4)  | 97,564 / 600,366 | s UNSATISFIABLE (exit 20), ~10 min | 0.87 GB | **s VERIFIED** (1086 s) |

Orientation note: my first variant used lex non-DEcreasing (the mirror canonical form —
equally sound, and its 3×3 lex-only model count is exactly the 1169 doubly-non-decreasing
matrices). kissat made no visible progress on it in >5 h per instance (proofs >20 GB),
while the non-increasing orientation of the SAME encoder finishes in ~10 min. So the
certified runs above share the lex orientation with the reviewed encodings — a performance
necessity, not a soundness one; independence is retained in variables, constraint
encodings, cardinality machinery, and lex implementation.

**(c) CP-SAT reproduction.** `solve_cpsat.py 12 20 4 3 10 6 4` re-run on this machine
(8 workers): INFEASIBLE in 676 s, agreeing with the reported 684 s result.

So each instance now has: CP-SAT INFEASIBLE (original run; for (12,20) two CP-SAT models
and a reviewer re-run) + a DRAT-certified UNSAT on the run's CNF (reproduced here) + a
DRAT-certified UNSAT on an adversarially-written CNF (this review) — three (four for
(12,20)) independent encodings per instance, two of them proof-checked.

## 4. Residual risks

1. **Common-mode error in the double-lex idea itself** — all encodings rely on the same
   Flener et al. 2002 theorem. The theorem is standard, and the group used (full S_V × S_B)
   is genuinely a symmetry group of the constraint set (verified from the definition), but
   no lex-free nonexistence proof exists yet, and (see §3b) the certified runs all use the
   same non-increasing orientation — the mirror orientation appears computationally out of
   reach. Both encoders' lex clauses were proven exactly correct by exhaustive model
   counting, so the residual risk is the theorem's applicability, which was re-derived
   here from the definition. A Kramer–Mesner / orbit-based verification without lex would
   remove this entirely.
2. **Toolchain trust**: kissat + drat-trim share no code, but drat-trim itself is unverified
   C. A formally verified checker (cake_lpr / GRAT) pass would upgrade the certificates.
   Proofs are large (0.9–13 GB) but regenerate deterministically in ~10–20 min each.
3. **Handbook access**: openness was established from the Kunkle–Sarvate source text,
   Kaski–Östergård 2004, and the CPro1 papers/repo, not the printed 2nd-edition Handbook
   itself. The risk that the printed tables contain a resolution missing from all of the
   above is judged very low.
4. `NOTES.md`'s alt-CP-SAT confirmations for (14,18) and (12,15) timed out (correctly
   disclosed there); the independent-confirmation burden is carried by the CNF/DRAT route,
   which this review re-established twice over.

## 5. Reviewer artifacts

- `runs/P14/v1/review_encode.py` — the independent encoder used in §3(b).
- `runs/P14/v1/review_validate.py` — exhaustive model-count validation harness (§1).
- Logs on the review machine: kissat/drat-trim outputs for all six certified runs
  (regen-* = shipped encoder, mine3-* = reviewer encoder), plus the abandoned
  mirror-orientation runs (mine-*, mine2-*).

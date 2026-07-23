# Nonexistence of three balanced ternary designs

Self-contained verification package for a math researcher.

## Result

**No BTD exists for any of:**
- BTD(14,18; 7,1,9; 7,4)
- BTD(12,15; 6,2,10; 8,6)
- BTD(12,20; 4,3,10; 6,4)

These were the three balanced-ternary-design instances left unresolved by the CPro1
computational campaigns (arXiv:2501.17725, arXiv:2505.23881), themselves the survivors of
the classical existence tables (Billington's surveys; Handbook of Combinatorial Designs).
A fourth instance, BTD(14,28; 8,3,14; 7,6), remains **undecided** (~19 h of solver time,
no verdict; cube-and-conquer recommended).

## Definition

A BTD(V,B; p1,p2,R; K,L) is a V×B incidence matrix with entries in {0,1,2}: every column
sums to K, every row contains the entry 1 exactly p1 times and the entry 2 exactly p2
times (so row sum R = p1 + 2·p2), and every unordered pair of distinct rows has inner
product exactly L.

## Evidence (per instance)

1. **CP-SAT**: OR-Tools model `runs/P14/v1/solve_cpsat.py` INFEASIBLE
   (684 s / 1482 s / 2007 s). For (12,20) a second independently written model
   (`solve_cpsat_alt.py`) is also INFEASIBLE.
2. **DRAT-certified SAT proof**: independent CNF encoding (`runs/P14/v1/encode_sat.py`),
   kissat `s UNSATISFIABLE`, proof checked by drat-trim `s VERIFIED` — for all three.
   Proofs are 1–40 GB and are not shipped; they regenerate deterministically:
   ```
   python3 encode_sat.py V B p1 p2 R K L f.cnf   # e.g. 12 20 4 3 10 6 4
   kissat -q f.cnf f.proof
   drat-trim f.cnf f.proof                        # prints "s VERIFIED"
   ```
3. **Soundness of symmetry breaking**: the only solution-removing device is double-lex
   ordering of rows and columns, sound for the full row/column permutation group
   (Flener et al., CP 2002). Positive controls: the same encoders reproduce known designs
   on dev instances, validated by `solutions/P14/verify.py`.
4. **Adversarial review**: see `runs/P14/v1/ADVERSARIAL_REVIEW.md` — independent reviewer
   pinned the definition against the primary literature, validated encodings by exhaustive
   model counting on small instances, confirmed the instances were genuinely open
   (Handbook tables, Kaski–Östergård 2004, CPro1 repo/papers, artifact sweeps), re-ran the
   full shipped pipeline, and ran its own independently written encoding
   (order-encoding + totalizer + its own lex): kissat UNSAT + drat-trim VERIFIED on all
   three instances. **Verdict (2026-07-23): CONFIRMED.** Documented residual risks: all
   certified runs share one lex orientation (mirror orientation computationally
   intractable); drat-trim is unverified C (a cake_lpr pass would upgrade the trust base).

## Priority

Checked per this project's widened gate: primary literature + Handbook + arXiv +
GitHub/Zenodo/OpenReview artifact search — no prior resolution found for any of the three.

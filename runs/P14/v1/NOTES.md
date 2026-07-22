# P14 V1 (exact ILP / CP-SAT) — run notes

Session: devin-a3c4bd5a99684570aaff53cdb0582cba (2026-07-22). Variant V1: exact integer
program via OR-Tools CP-SAT (Gurobi-free stack), symmetry breaking, all 4 instances.

## Problem statement re-verification (against original source)
- Cloned CPro1 repo (github.com/Constructive-Codes/CPro1); read
  `CPro1/design_definitions/balanced-ternary-design/problem_def.py`. Definition matches the
  problem file exactly: V×B matrix over {0,1,2}; row sum R with exactly p1 ones and p2 twos;
  column sum K; every distinct pair i<k has sum_j m_ij*m_kj = L.
- Openness cross-check: CPro1 `OPEN_INSTANCES` contains (14,18,7,1,9,7,4), (12,15,6,2,10,8,6),
  (12,20,4,3,10,6,4); `designs/balanced-ternary-design/` has result-*.txt files ONLY for the 7
  solved siblings — none for these three. (14,28,8,3,14,7,6) not in CPro1's list (Handbook-open,
  apparently unattempted). Exa literature search (2026-07-22) found nothing newer than the 2025
  CPro1 papers touching these cells. Treating all 4 as open as of July 2026.
- Necessary counting identities machine-checkable and hold for all 4:
  V*R = B*K and B*K^2 − V*(p1+4*p2) = L*V*(V−1).

## Encoding (runs/P14/v1/solve_cpsat.py)
- Booleans x1[i][j], x2[i][j] (mult 1 / mult 2), x1+x2 ≤ 1; int m = x1+2*x2.
- Row: Σ x1 = p1, Σ x2 = p2. Column: Σ m = K.
- Pair inner products linearized: m_i*m_k = AND(x1,x1') + 2AND(x1,x2') + 2AND(x2,x1') + 4AND(x2,x2'),
  AND via standard aux boolean; Σ_j = L for each of C(V,2) pairs.
- Symmetry breaking: double-lex (rows lex non-increasing AND columns lex non-increasing) —
  sound for the full S_V × S_B symmetry group, so UNSAT ⇒ genuine nonexistence.
- Sanity: solved dev instances BTD(4,8;2,3,8;4,6) instantly and BTD(18,18;2,6,14;14,10)
  in ~30 s; both witnesses verified PASS by solutions/P14/verify.py.

## Instances & runs

### Pass 1 — 900 s each, 8 workers, model solve_cpsat.py (double-lex on)
| instance | status | wall |
|---|---|---|
| (14,18;7,1,9;7,4)  | UNKNOWN | 900 s |
| (12,15;6,2,10;8,6) | UNKNOWN | 900 s |
| (12,20;4,3,10;6,4) | **INFEASIBLE** | 684 s |
| (14,28;8,3,14;7,6) | UNKNOWN | 900 s |

**Candidate nonexistence result: BTD(12,20;4,3,10;6,4) does not exist** (CP-SAT proves
INFEASIBLE in 684 s). Double-lex is a sound symmetry-breaking scheme (Flener et al., CP 2002:
every row/col-permutation class contains a double-lex-sorted matrix), so INFEASIBLE with it
implies genuine nonexistence — modulo solver correctness. Per methodology, launched an
independent confirmation with a differently-written model (solve_cpsat_alt.py: IntVar domain
encoding + AddMultiplicationEquality + independently implemented lex, sanity-checked on a dev
instance) — running in background.

### Confirmations for (12,20;4,3,10;6,4) nonexistence
1. solve_cpsat_alt.py (independent 2nd CP-SAT model): **INFEASIBLE in 575 s**. Agrees.
2. Third, fully independent check: CNF encoding (runs/P14/v1/encode_sat.py — pysat seqcounter
   cardinalities; weighted sums by literal duplication, exhaustively validated on small cases;
   AND-aux for pair products; independently implemented double-lex) run through **kissat**:
   **s UNSATISFIABLE** (exit 20), 881 MB DRAT proof; drat-trim verification in progress.
   Encoder end-to-end sanity-checked on dev instance BTD(4,8;2,3,8;4,6): kissat found a
   solution which verify.py PASSed.

### Pass 2 — 3600 s each, 4 workers, model solve_cpsat.py
| instance | status | wall |
|---|---|---|
| (14,18;7,1,9;7,4)  | **INFEASIBLE** | 1482 s |
| (12,15;6,2,10;8,6) | running |  |
| (14,28;8,3,14;7,6) | queued |  |

**Second nonexistence result: BTD(14,18;7,1,9;7,4) does not exist** (CP-SAT INFEASIBLE,
1482 s, double-lex sound). Confirmations launched: solve_cpsat_alt.py (running) and
kissat on encode_sat.py CNF (134238 vars / 278728 clauses, running).

### Pass-2 completion + confirmations (running log)
- (12,20;4,3,10;6,4): kissat UNSAT proof **DRAT-VERIFIED by drat-trim** ("s VERIFIED",
  872 s check, 881 MB proof). Nonexistence now triple-confirmed (2 CP-SAT models + certified SAT).
- (14,18;7,1,9;7,4): kissat also reports **s UNSATISFIABLE**; drat-trim verifying.
  solve_cpsat_alt confirmation still running.
- **(12,15;6,2,10;8,6): INFEASIBLE (solve_cpsat.py, 2007 s)** — third nonexistence result!
  Confirmations launched: solve_cpsat_alt + kissat CNF (115794 vars / 237980 clauses).
- (14,28;8,3,14;7,6): pass-2 3600 s run in progress.

Note: DRAT proofs are ~1 GB each — not committed; regenerate deterministically via
`python3 encode_sat.py V B p1 p2 R K L f.cnf && kissat -q f.cnf f.proof && drat-trim f.cnf f.proof`.

(log continues)

# P23 exact verification of public sub-509 candidates and controls

**Date:** 2026-07-24 UTC. **Arithmetic:** exact SymPy algebraic expressions for all rows; files accepted by fusion1 `mfield.py` are additionally labelled with their multiquadratic field. High-precision (260 decimal digits) values were used only to conservatively select candidate pairs; every pair with `|d²-1| < 1e-40` was decided symbolically. The reported numeric margin is the closest non-edge `|d²-1|` after exact unit edges were removed.

| file | claimed order | exact order parsed | field / method | exact unit edges | SAT/UNSAT | certificate status | margin |
|---|---:|---:|---|---:|---|---|---|
| `runs/P23-priority2/data/g409c.vtx` | 409 | 409 | SymPy exact algebraic expressions (outside mfield supported multiquadratic field) | 2046 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.0024166 |
| `runs/P23-priority2/data/g469.vtx` | 469 | 469 | mfield Q(3,5,11) | 2436 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.0024166 |
| `runs/P23-priority2/data/v433d.vtx` | 433 | 433 | mfield Q(3,5,11) | 2292 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.0024166 |
| `runs/P23-priority2/data/v387.vtx` | 387 | 387 | SymPy exact algebraic expressions (outside mfield supported multiquadratic field) | 1904 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.0024166 |
| `runs/P23-priority2/data/v379.vtx` | 379 | 379 | mfield Q(3,5,11) | 1944 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.0024166 |
| `runs/P23-priority2/sources/code-evidence/509_parts.vtx` | 509 | 509 | mfield Q(3,5,11) | 2442 | UNSAT | s VERIFIED | 0.000160218 |
| `runs/P23-priority2/data/v16_56.vtx` | 16 | 16 | SymPy exact algebraic expressions (outside mfield supported multiquadratic field) | 28 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.381966 |
| `runs/P23-priority2/data/v30z.vtx` | 30 | 30 | mfield Q(3,5,11) | 48 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.108695 |
| `runs/P23-priority2/data/v31_115.vtx` | 31 | 31 | SymPy exact algebraic expressions (outside mfield supported multiquadratic field) | 59 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.381966 |
| `runs/P23-priority2/data/v38w.vtx` | 38 | 38 | mfield Q(3,5,11) | 123 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.163042 |
| `runs/P23-priority2/data/mos_10.vtx` | 10 | 10 | mfield Q(3,5,11) | 19 | SAT | valid 4-coloring independently rechecked against exact edge list | 0.457427 |
| `runs/P23-priority2/data/g568.vtx` | 568 | 568 | mfield Q(3,5,11) | 2922 | UNSAT | s VERIFIED | 0.000160218 |

## Interpretation

- Every sub-509 file that parsed exactly was SAT for the 4-coloring CNF, and its emitted model is saved as `verify-out/<label>.coloring.txt` and independently rechecked against the exact edge list.
- `g409c.vtx` had one extra closing brace on its final coordinate line; the parser removed only that wrapper artifact. It still parsed exactly 409 records.
- `v16_56.vtx` and `v31_115.vtx` use nested radicals outside fusion1's multiquadratic representation; they were handled by the exact SymPy algebraic pipeline rather than being silently dropped.
- The 509 control produced 2442 exact edges, Kissat `s UNSATISFIABLE`, and drat-trim `s VERIFIED`. The proof itself was temporary and deleted after verification; raw compact solver/drat-trim output is in `verify-out/record509.log`.
- `g568.vtx` independently produced 2922 exact edges, UNSAT, and drat-trim `s VERIFIED`.
- Solver logs contain the 260-digit scan summary, exact edge count, SAT/UNSAT status, and certificate output. No multi-hundred-MB proof files are retained.

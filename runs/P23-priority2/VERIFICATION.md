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

## 509-edge-deletion reconstruction

The reconstruction started from `data/v509e2442.vtx` and its exactly
recomputed 2442-edge set.  A proof-core experiment was attempted, but
drat-trim's `-c` output contains derived clauses and therefore cannot be used
as an original-edge dependency list without dependency tracking; deleting the
516 edges whose original clauses were absent from that output incorrectly
produced a SAT instance and was discarded.

The first uncapped tests found three individually removable edges (original
edge indices 10, 46, and 54).  A greedy sequential pass was then run from the
2431-edge witness, testing candidates one at a time against the current graph
and accepting only deletions followed by a fresh UNSAT certificate.  The final
bounded result has **2406 edges**, i.e. 36 confirmed deletions.  Its compact
certificate is in `verify-out/v509e2406.log` and contains:

```text
s UNSATISFIABLE
s VERIFIED
```

The final witness files are:

- `data/v509e2406.edges`
- `data/v509e2406.cnf`
- coordinates: `data/v509e2442.vtx` (the same 509 exact coordinates)

The accepted original edge indices are:

```text
2 5 10 13 18 21 42 46 54 55 56 59 62 63 67 70 71 73
74 79 82 93 96 104 117 118 120 130 137 141 146 147 150
154 155 160
```

The 2406 retained edges were checked explicitly against the exact 2442-edge
set; all are exact unit edges.  Thus this independently reconstructed witness
matches the 509/2406 edge count reported by de Grey--Parts, although it is not
claimed to be their exact edge-deletion set.

The greedy pass used a 5-hour wall-clock budget and stopped after 13,068.7
seconds (about 3 h 38 min), immediately after certifying the 2406-edge
witness.  It tested candidates in rotating batches of four parallel Kissat
instances against the same current graph, applying at most one accepted
deletion per round.  The remaining candidate list was not exhausted; this was
a bounded reconstruction, not a minimality proof.

For auditability, the partial 120-second sweep completed 883 of 2442 edge
instances before being redirected: 633 were SAT and 250 timed out. A longer
900-second-capped follow-up was then run on the available timeout candidates;
in the snapshot used for the reconstruction, 112 were UNSAT and 5 were SAT.
The candidate tests were deliberately not treated as a proof of global
edge-minimality. Every accepted intermediate graph was re-solved and
drat-trim-checked before the next round; the final accepted graph has the
certificate cited above.

The provenance audit and public-data verdict are in
`runs/P23-priority2/OBTAIN-2406.md`.

## Additional Parts Dropbox files

The Dropbox archive was downloaded as a ZIP export of the public folder. The
following files were parsed with exact `mfield.py` arithmetic over
Q(sqrt(3),sqrt(5),sqrt(11)); every filename edge count matched the exact
recomputed count. SAT models were independently checked against the exact
edge sets.

| file | order | exact order | filename edges | exact edges | 4-colorability | certificate |
|---|---:|---:|---:|---:|---|---|
| `v136e564.vtx` | 136 | 136 | 564 | 564 | SAT | valid coloring |
| `v141e594.vtx` | 141 | 141 | 594 | 594 | SAT | valid coloring |
| `v150e639.vtx` | 150 | 150 | 639 | 639 | SAT | valid coloring |
| `v159e646.vtx` | 159 | 159 | 646 | 646 | SAT | valid coloring |
| `v166e774.vtx` | 166 | 166 | 774 | 774 | SAT | valid coloring |
| `v167e772.vtx` | 167 | 167 | 772 | 772 | SAT | valid coloring |
| `v172e804.vtx` | 172 | 172 | 804 | 804 | SAT | valid coloring |
| `v180e778.vtx` | 180 | 180 | 778 | 778 | SAT | valid coloring |
| `v214e977.vtx` | 214 | 214 | 977 | 977 | SAT | valid coloring |
| `v221e1006.vtx` | 221 | 221 | 1006 | 1006 | SAT | valid coloring |
| `v226e1037.vtx` | 226 | 226 | 1037 | 1037 | SAT | valid coloring |
| `v238e1131.vtx` | 238 | 238 | 1131 | 1131 | SAT | valid coloring |
| `v250e1116.vtx` | 250 | 250 | 1116 | 1116 | SAT | valid coloring |
| `v265e1246.vtx` | 265 | 265 | 1246 | 1246 | SAT | valid coloring |
| `v265e1293.vtx` | 265 | 265 | 1293 | 1293 | SAT | valid coloring |
| `v289e1389.vtx` | 289 | 289 | 1389 | 1389 | SAT | valid coloring |
| `v308e1522.vtx` | 308 | 308 | 1522 | 1522 | SAT | valid coloring |
| `v310e1536.vtx` | 310 | 310 | 1536 | 1536 | SAT | valid coloring |
| `v312e1502.vtx` | 312 | 312 | 1502 | 1502 | SAT | valid coloring |
| `v315e1498.vtx` | 315 | 315 | 1498 | 1498 | SAT | valid coloring |
| `v319e1524.vtx` | 319 | 319 | 1524 | 1524 | SAT | valid coloring |
| `v335e1638.vtx` | 335 | 335 | 1638 | 1638 | SAT | valid coloring |
| `v343e1688.vtx` | 343 | 343 | 1688 | 1688 | SAT | valid coloring |
| `v367e1822.vtx` | 367 | 367 | 1822 | 1822 | SAT | valid coloring |
| `v374e1860.vtx` | 374 | 374 | 1860 | 1860 | SAT | valid coloring |
| `v374e1864.vtx` | 374 | 374 | 1864 | 1864 | SAT | valid coloring |
| `v374e1868.vtx` | 374 | 374 | 1868 | 1868 | SAT | valid coloring |
| `v374e1872.vtx` | 374 | 374 | 1872 | 1872 | SAT | valid coloring |
| `v375e1862.vtx` | 375 | 375 | 1862 | 1862 | SAT | valid coloring |
| `v375e1916.vtx` | 375 | 375 | 1916 | 1916 | SAT | valid coloring |
| `v375e1920.vtx` | 375 | 375 | 1920 | 1920 | SAT | valid coloring |
| `v376e1890.vtx` | 376 | 376 | 1890 | 1890 | SAT | valid coloring |
| `v400e2034.vtx` | 400 | 400 | 2034 | 2034 | SAT | valid coloring |
| `v403e2106.vtx` | 403 | 403 | 2106 | 2106 | SAT | valid coloring |
| `v403e2112.vtx` | 403 | 403 | 2112 | 2112 | SAT | valid coloring |
| `v406e2076.vtx` | 406 | 406 | 2076 | 2076 | SAT | valid coloring |
| `v406e2082.vtx` | 406 | 406 | 2082 | 2082 | SAT | valid coloring |
| `v412e2106.vtx` | 412 | 412 | 2106 | 2106 | SAT | valid coloring |
| `v421e2094.vtx` | 421 | 421 | 2094 | 2094 | SAT | valid coloring |
| `v433e2186.vtx` | 433 | 433 | 2186 | 2186 | SAT | valid coloring |
| `v451e2400.vtx` | 451 | 451 | 2400 | 2400 | SAT | valid coloring |
| `v510e2502.vtx` | 510 | 510 | 2502 | 2502 | UNSAT | `s VERIFIED` |
| `v525e2605.vtx` | 525 | 525 | 2605 | 2605 | UNSAT | `s VERIFIED` |

The two UNSAT rows are above the 509-vertex record and were independently
checked with drat-trim; their compact logs are `verify-out/v510e2502-drat.log`
and `verify-out/v525e2605-drat.log`. No sub-509 file in this expanded set was
UNSAT.

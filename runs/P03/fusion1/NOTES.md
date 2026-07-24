# Woodall P03 — fusion1

## Environment

- Branch: `runs/P03-fusion1`
- Python: Python 3.10.12
- PySAT: `python-sat 1.9.dev7` (Glucose3 smoke test passed)
- NetworkX: `3.4.2`
- PyPy: PyPy 7.3.9 / Python 3.8.13
- nauty: 2.7r3; binaries are `/usr/bin/nauty-geng` and
  `/usr/bin/nauty-directg` (the unprefixed `geng`/`directg` names are absent)

## Port

The v5 phase-2 scripts were copied from `origin/runs/P03-v5`:
`orient_exhaust.py`, `prep_graphs.py`, `enum_pypy.py`, `harness.py`,
`crosscheck.py`, `sat_check.py`, and the supporting search/exhaustion and test
scripts.

## Checker validations

All validations below passed on 2026-07-24:

- `test_harness.py`: all sanity tests passed.
- `crosscheck.py`: independent brute-force checker agreed with the PySAT
  harness on 40/40 random tau=3 instances.
- `test_exact_pack.py`: pure-Python exact packer agreed with PySAT on 300
  n=14 candidates; random-DAG cross-check agreed on 21 instances (0
  non-packing instances in that sample).
- `test_cegar.py`: CEGAR packer agreed with pure exact backtracking on 400/400
  n=14 candidates and with PySAT on 60/60 random tau>=3 DAGs.
- `test_dicut_filter.py`: reduced-dicut filter agreed with brute force on
  500/500 candidates.

The fixture files used by the v5 tests were regenerated in `/tmp` from the
tracked v5 `kept14.jsonl`; they are not part of the repository.

## n=16 exhaustion

The fresh nauty generation produced 4,060 connected cubic graphs on 16
vertices. `prep_graphs.py` retained 2,595 non-planar, 3-edge-connected
graphs, dropping 681 planar and 784 not-3-edge-connected graphs. Eight PyPy
shards are running over these 2,595 retained graphs:

```
0:325  325:650  650:975  975:1300
1300:1625  1625:1950  1950:2273  2273:2595
```

Each shard uses `enum_pypy.py` with profile, DAG, source-sink, CEGAR exact
packing, reduced-dicut, and exact backtracking filters. Candidate output is
written to a separate `.cand.jsonl` file and stderr progress to a `.log`
file. At the latest checkpoint (about 12 minutes wall time), seven shards had
completed their first graph and one shard had completed two. Per-graph totals
ranged from 5.10M to 8.23M DAG leaves, 4.48M to 6.72M profile leaves, and
1.12M to 2.60M CEGAR packing checks; all reported zero candidates. One shard
was still processing its first graph. All eight candidate files remained
empty.

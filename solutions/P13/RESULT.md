# P13 results (V4 run): nonexistence of (9,6)- and (10,6)-PMDs

**Claim 1. No (9,6)-PMD exists.**
**Claim 2. No (10,6)-PMD exists.**

Both settled by complete exhaustive backtracking search (V4,
`runs/P13/v4/pmd6_search.c` and `pmd6_search2.c`), each verified by at least
three independent complete traversals with different branching orders /
implementations, including (for v=9) a fully unrestricted run with no symmetry
assumption at all. Details, node counts, and completeness argument:
`runs/P13/v4/NOTES.md`.

These are nonexistence results, so there is no finite witness for `verify.py`;
reproduction is by re-running the searchers (v=9 takes < 1 s with the fixed
first block, ~4 min unrestricted; v=10 ~10 min single-core).

Bonus exact result: the maximum partial (9,6)-PMD packing has **10 blocks**
(of the 12 a perfect design needs). Witness:
`runs/P13/v4/witness_v9_maxpack10.txt`, verified by
`python3 solutions/P13/verify.py --packing`.

Impact: the open list for (v,6)-PMDs (Handbook VI.35 / Abel–Bennett–Zhang 2000)
shrinks from {9,10,12,15,16,18} to {12,15,16,18}, with v=9,10 now proven
nonexistent (joining v=6).

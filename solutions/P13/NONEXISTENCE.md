# P13 claimed result: no (9,6)-PMD exists (and confirmation that no (10,6)-PMD exists)

Claim type: nonexistence by complete exhaustive search (no witness array; the certificate is
replication of the search). Produced by the V2 run (branch `runs/P13-v2`,
code in `runs/P13/v2/`).

## Claim 1 — There is no (9,6,1)-perfect Mendelsohn design.  [believed NEW]

Three independent programs agree:

1. `runs/P13/v2/pmd_dlx.c` (exact-cover / dancing-links, min-column heuristic):
   `./pmd_dlx 9 6 1 9 0 0 0` — full search, **zero symmetry assumptions**, all 10,080
   cyclic blocks as candidates: SOLUTIONS 0.
2. Same program with the WLOG relabelling that the block covering (0,1) at distance 1 is
   (0,1,2,3,4,5): `./pmd_dlx 9 6 1 9 0 0 1`: SOLUTIONS 0 (62,383 nodes).
3. `runs/P13/v2/exhaust_indep.c` (independently written plain backtracker, no DLX,
   branches on smallest uncovered distance-1 pair): `./exhaust_indep 9 6 1`:
   solutions=0 (97,066,584 nodes). The Python re-implementation
   `runs/P13/v2/exhaust_indep.py 9 6 --first-block` also reports 0.

All three implementations were validated against known values before use:
MTS(6)=0, MTS(7)=480 labeled solutions, (7,6)-PMD count 240, (4,4)-PMD nonexistence,
(5,4)/(10,3)/(13,6)/(8,7) existence (witnesses PASS `solutions/P13/verify.py`).

Reproduction: `gcc -O2 -o pmd_dlx pmd_dlx.c && ./pmd_dlx 9 6 1 9 0 0 0` (seconds–minutes);
`gcc -O2 -o exhaust_indep exhaust_indep.c && ./exhaust_indep 9 6 1` (~1 minute).

## Claim 2 — There is no (10,6,1)-PMD (independent computational confirmation).

Known in the literature (Abel & Bennett 2006, Des. Codes Cryptogr. 40, Thm 1.3), though
listed as open in the CPro1 instance list. Confirmed here by two independent programs:
`./pmd_dlx 10 6 1 10 0 0 1` → SOLUTIONS 0, and `./exhaust_indep 10 6 1` → solutions=0
(226,078,254,824 nodes, ~1.5 h).

`solutions/P13/verify.py` remains the witness verifier for any positive (existence) claim;
no witness exists for v=9,10 by the above.

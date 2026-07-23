# P13 — Perfect Mendelsohn Designs, V2 run (prescribed automorphisms / difference method)

Session: https://app.devin.ai/sessions/d0105a2e11c94006bd318ac1a1566207
Variant: V2 — prescribe cyclic automorphism groups, search base blocks (Kramer–Mesner
orbit exact cover), sweep all open v.

## 0. Statement re-verification & openness check (2026-07-22)

- Statement checked against CPro1 repo `CPro1/design_definitions/perfect-mendelsohn-design/problem_def.py`
  (cloned from github.com/Constructive-Codes/CPro1): matches the problem file exactly.
  OPEN_INSTANCES = [[9,6,12],[10,6,15],[12,6,22],[15,6,35],[16,6,40],[18,6,51],[14,7,26],[15,7,30]].
- **Literature discrepancy found**: Abel & Bennett, *The existence of (v,6,λ)-perfect
  Mendelsohn designs with λ>1*, Des. Codes Cryptogr. 40 (2006) 211–224
  (DOI 10.1007/s10623-006-0008-4), **Theorem 1.3: "There is no (10,6,1)-PMD"** (proved by a
  counting argument breaking blocks into 2-(10,?,?) structure). So (10,6) in the CPro1 open
  list is actually *settled (nonexistent)* in the literature. The same paper's Theorem 1.4
  summary of λ=1 open cases: v≡0 (mod 6): {12,18,24,...}; v≡3 (mod 6): [9,135] ∪ ...;
  v≡4 (mod 6): {16,22,34} ∪ [52,148]. Note **10 is absent** — consistent with Thm 1.3.
- (9,6), (12,6), (15,6), (16,6), (18,6), (14,7), (15,7) confirmed open: no later resolution
  found (Exa + Crossref search, ≥2006 publications; k=5 was closed in 2020 by Griggs–Kozlik
  but nothing new for k=6/7 λ=1 small v).

## 1. Method / encoding

Exact cover formulation. Universe: all triples (i, x, y), i ∈ 1..k−1, ordered pairs x≠y —
(k−1)·v(v−1) columns. Each block (cyclic k-tuple of distinct points) covers k pairs at each
distance; a PMD = exact cover by b = v(v−1)/k blocks.

Prescribed automorphism σ with c cycles of length n plus f fixed points (v = nc+f), in
standard form (0 1 … n−1)(n … 2n−1)… . Rows of the cover matrix = σ-orbits of blocks
(orbits with an internal (i,pair) collision are discarded). DLX / Algorithm X with
min-column heuristic exhausts each prescription completely (`pmd_dlx.c`).

Key reduction: if a PMD admits any nontrivial automorphism, it admits one of **prime**
order p, whose cycle type is (p-cycles)^c + fixed^f. So sweeping all (p, c, f) with p prime
covers *all* possible nontrivial automorphism groups; all-UNSAT ⇒ every (v,k)-PMD is rigid.

With n=1 (identity, one orbit per block) the same code is a plain full exhaustive exact-cover
search. Symmetry breaking for full exhaust (`fixfirst`): any PMD can be relabelled so the
block covering pair (0,1) at distance 1 is exactly (0,1,…,k−1); forcing that row is WLOG.

Correctness validation against known results:
- (7,3): Z_7 gives SAT (MTS(7) exists) ✓; full exhaust counts 480 solutions.
- (6,3): full exhaust, 0 solutions (MTS(6) does not exist) ✓ (335 nodes).
- (4,4): full exhaust, 0 solutions ((4,4)-PMD does not exist) ✓.
- (5,4), (10,3), (7,6), (13,6), (8,7) (via Z_7 + fixed point): SAT, all witnesses PASS
  the independent verifier `solutions/P13/verify.py` ✓.
- (8,7) has no Z_8-invariant solution but a Z_7+fix one — matches classical difference
  construction.

Second, independently written checker `exhaust_indep.py` (pure Python, no DLX; branches on
the lexicographically smallest uncovered distance-1 pair): agrees on (6,3)=0, (7,3)=480,
(7,6)=240.

## 2. Results

### (9,6)-PMD: DOES NOT EXIST (full exhaustive search, two independent programs)

- `pmd_dlx 9 6 1 9 0 0 0` — trivial group, **no symmetry assumption at all**, exhaust
  the full exact-cover tree over all 10080 cyclic blocks: **SOLUTIONS 0**.
- `pmd_dlx 9 6 1 9 0 0 1` — with WLOG first block (0,1,2,3,4,5): SOLUTIONS 0 (62,383 nodes,
  seconds).
- `exhaust_indep 9 6 1` — independently written C backtracker (no DLX, pair-driven
  branching): **solutions=0**, 97,066,584 nodes.
- Python `exhaust_indep.py` (third implementation) running as an additional check.

Modulo replication, this settles the smallest open case: **there is no (9,6,1)-PMD**.

### (10,6)-PMD: DOES NOT EXIST (confirms Abel–Bennett 2006 Thm 1.3 computationally)

- `pmd_dlx 10 6 1 10 0 0 1` (WLOG first block): SOLUTIONS 0.
- `exhaust_indep 10 6 1` (independent C backtracker, WLOG first block): **solutions=0**,
  226,078,254,824 nodes (~1.5 h).

### Prescribed-automorphism sweeps (see sweep_results.tsv)

For v = 9, 10, 12 (k=6): **every** cycle type (n,c,f), n ≥ 2, is UNSAT-exhausted —
no (v,6)-PMD with any nontrivial automorphism exists for these v (for 9, 10 subsumed by
full nonexistence above). In particular for v=12 this means any (12,6)-PMD must be rigid.
Sweeps for (15,6), (16,6), (18,6), (14,7), (15,7) in progress.

## STATUS: (running — see final line when complete)

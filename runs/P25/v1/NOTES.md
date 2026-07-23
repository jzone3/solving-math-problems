# P25 v1 — Football pool problem K₃(6,1) ∈ [71,73]

Session: ultra solve run, 2026-07-23. Target: find a 72-word ternary covering code of
length 6, radius 1 (new record ⇒ K₃(6,1) ≤ 72), or prove size 72 impossible (⇒ K₃(6,1)=73).

## Step 0 — Bounds re-verification (COMPLETE)

**Confirmed current interval: 71 ≤ K₃(6,1) ≤ 73.** The problem file's [71,73] is correct;
`research/wave3-smallest-open-cases.md` §C9's "[65,73]" is OUTDATED (it cites the lower
bound 65 that Linderoth–Margot–Thain themselves superseded).

Pinned sources:
- **Lower bound 71**: Linderoth–Margot–Thain, *Improving Bounds on the Football Pool
  Problem by Integer Programming and High-Throughput Computing*, INFORMS J. Computing 21
  (2009), doi:10.1287/ijoc.1090.0334. TR PDF (fetched, quote verified):
  https://jlinderoth.github.io/papers/Linderoth-Margot-Thain-07-TR-2.pdf — "our computations
  have been improve the lower bound on |C∗₆| from 65 to 71, and a total of more than two CPU
  centuries total have gone into the computation". Prior lower bound 65: Östergård–Wassermann,
  JCTA 99 (2002), doi:10.1006/jcta.2002.3260.
- **Upper bound 73**: L.T. Wille, *The football pool problem for 6 matches: a new upper
  bound obtained by simulated annealing*, JCTA 44 (1987) 171–177 (per Kéri's tables and the
  LMT TR: "the best known feasible solution has value 73 (found by Wille (1987))").
- **Kéri's covering-code tables** (Östergård's tables' successor, the standard reference):
  https://old.sztaki.hu/~keri/codes/3_tables.pdf — row n=6, R=1: "t 71–73 v", t = LMT 2007,
  v = Laarhoven–Aarts–van Lint–Wille 1989. PDF archived in this run.
- **OEIS A004044** (classic football pool problem): data ends at n=5 (a(5)=27); n=6 open.

## Widened priority check (COMPLETE, clean)

- **arXiv:2504.01932** (Gijswijt–Polak 2025, *Semidefinite lower bounds for covering codes*):
  audited the full new-bounds tables — their q=3, R=1 improvements start at n=13. No change
  at n=6 (their method reproduces ≤ the known 71 there; asterisked table cells confirm).
- **GitHub** `Slavov88/football-pool-problem` (updated 2025-12, "paper by Slavov and
  Mavrodiev"): cloned — repository contains ONLY a README, no code, data or claims. No
  associated paper found via search. Not a threat, but worth re-checking at write-up time.
- **Zenodo**: search "football pool covering code" — nothing relevant.
- **MaRDI/OEIS/Kéri**: all still list 71–73 as of 2026-07.

## Step 1 — Search for a 72-word code

Hardware: 8 cores, 32 GB. Tooling built this run (in `~/p25`, key files committed here):
- `ls.c` — incremental local search (fixed-temperature Metropolis, focused moves: pick an
  uncovered word u, move a random codeword into B(u); O(1) incremental cover counts).
  Calibration: K=81 instant; K=74 seconds; **K=73 (Wille's 40-year record) reproduced in
  < 1 second of CPU time** (352k iterations, T=0.35) and by 7/8 independent workers.
  A fresh 73-code found this run: `code73_example.txt` (verify.py → PASS).
- `gen_sat.py` — CNF: 729 indicator vars, 729 cover clauses (13-ary), totalizer ≤72,
  symmetry breaking x[000000]=1 (per-coordinate symbol translations act transitively).
  7,724 vars / 273,082 clauses. Solver: kissat 4.0.4.
- `ilp.py` — HiGHS ILP: min Σx, cover constraints; LP relaxation ≈ 56.6 at root (matches
  LMT's reported root bound ~56.6 → the 140-CPU-year gap; UNSAT-at-72 via vanilla MIP is
  hopeless, as expected).

Status of K=72 runs: local search (5 workers, T ∈ [0.40,0.55], random + 73-seeded starts)
reaches 1–2 uncovered words within seconds and then plateaus — exactly the landscape
behavior reported since 1987. Long budgets (2×10¹⁰ iterations/worker) in progress.

(Results section updated at end of run — see below.)

## Step 2 — UNSAT direction

Not attempted beyond the plain kissat run: proving no 72-code exists is equivalent to
raising the lower bound from 71 to 73; the 71 bound alone consumed >200 CPU-years (2007)
with heavy isomorphism pruning. A DRAT-certified UNSAT on this 8-core box is out of reach;
recorded as infeasible for this run rather than pretended at.

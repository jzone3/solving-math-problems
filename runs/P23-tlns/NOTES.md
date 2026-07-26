# P23 — exact large-neighbourhood descent in the *translated-placement* universe

Child run of `runs/P23-fusion1` (E43–E50).  Goal: a 5-chromatic unit-distance
graph with fewer than 509 vertices (Parts' record) inside the translated
placement `A u (T + omega*A)` that E43–E45 discovered, using the exact
region-trade machinery of E23–E27.

**Result of this run: a certified 1112-vertex 5-chromatic unit-distance graph**
(`witness_1112.pkl`, `verify.py` prints PASS, drat-trim `s VERIFIED`).  That is
far above 509 — the translated universe was *not* shown to beat Parts here, and
the honest conclusion is in T6: the obstruction is the minimiser, not the
universe.

Everything is exact: floats only ever prefilter, and every accepted unit edge
satisfies `dx^2 + dy^2 = 1` in `Q(sqrt3, sqrt5, sqrt11)`.

## T1 — the universe, rebuilt from the lattice decomposition (`tuniv.py`)

`runs/P23-fusion1/tscan2.pkl` (the float scan that produced the working
translation) is **not in the repository** — the branch has `tscan.py`/`tasym.py`
but not the pickle they write, so the exact translation could not be read from
it.  Rather than re-run a float scan, the universe is rebuilt from the *exact*
decomposition recorded in E43, which is better anyway — no float search enters
the pipeline at any point:

```
omega = w[15] = (7 + i sqrt15)/8          (rotation about the origin)
T     = a + omega*b,   12a = (0,0,4,0),   12b = (6,0,-6,0)
A(r)  = 3 Minkowski layers of the 30 unit vectors of Parts' ring
        (lattice.build_base), clipped at radius r
universe(rA, rB) = A(rA)  u  (T + omega*A(rB))
```

with the asymmetric radii of E45, `rA = 1.6`, `rB = 1.3`:

```
2545 vertices, 14316 exact unit edges   (1441 in the A half, 1104 in the B half)
kissat: s UNSATISFIABLE for 4 colours   (206 s)
verify_universe.py: PASS                (edge list recomputed from scratch)
```

That is **2545 vertices against the 2581 of E45** — same placement, slightly
different Minkowski base — and it is the smallest exactly-verified
non-4-colorable universe in this family so far.

## T2 — the asymmetric-radius frontier for this base (`tasym.py`)

E45's frontier had to be re-measured for this base.  Each universe is built
exactly and then handed to kissat:

| rA | rB | vertices | edges | verdict |
|---|---|---|---|---|
| 1.6 | 1.35 | 2557 | 14388 | UNSAT |
| **1.6** | **1.3** | **2545** | **14316** | **UNSAT** |
| 1.65 | 1.25 | 2473 | 13871 | SAT |
| 1.55 | 1.3 | 2461 | 13547 | SAT |
| 1.6 | 1.25 | 2425 | 13451 | SAT |
| 1.5 | 1.3 | 2401 | 13000 | SAT |
| 1.6 | 1.2 | 2365 | 12989 | SAT |
| 1.7 | 1.2 | 2503 | 14088 | SAT |
| 1.7 | 1.1 | 2317 | 12741 | SAT |
| 1.6 | 1.15 | 2275 | 12320 | SAT |

1.6/1.3 sits exactly on the frontier here too, and the asymmetry is again real
rather than a size effect: 1.7/1.2 has 2503 vertices and *is* 4-colorable while
1.6/1.35 has 2557 and is not.  So the E45 recipe transfers, and there is no
cheaper obstructing universe to be had by shrinking the radii.

## T3 — greedy to the floor (`coremin.py`, `greedy8.py`, `chain.sh`, `best.py`)

Pipeline of E27: DRAT-core minimisation first, then batched (8-4-2-1) greedy
deletion in which every accepted deletion is re-certified by kissat and
drat-trim and the UNSAT core is used as a free jump.

* five independent DRAT-core chains from the whole 2545-vertex universe reach
  1725 / 1757 / 1772 / 1784 / 1814 (≈ 30 iterations of ≈ 35 s each);
* batched greedy from those cores, then *chained*: `chain.sh` restarts every
  worker from the smallest witness any worker has produced (`best.py`), which
  keeps 8 cores on one descent instead of 8 parallel copies of the same one.

Trajectory of the shared descent (every intermediate is a certified
non-4-colorable subset):

```
2545 -> 1725 (cores) -> 1527 -> 1465 -> 1422 -> 1399 -> 1333 -> 1265
     -> 1233 -> 1198 -> 1168 -> 1138 -> 1121 -> 1112
```

It never actually stops: 12 h of 8-core descent was still shedding ~2 vertices
per core-hour at 1112, and not one greedy *pass* had completed (a pass over 1100
vertices at ≈ 40 s per certified batch is itself ~4 h).  1112 is where this run
was cut, not a floor.  For calibration, E13's greedy floors at ~1850 on Parts'
own universe, which provably contains a 509 — the same ~3.5x overshoot would put
the optimum of this universe near 300, so nothing here contradicts a sub-509
witness existing; the search simply cannot get near it.

## T4 — exact region trades (`tlns.py`)

Port of `lnsdescend.py`/`hlns.py`/`cegar4.py` to the field-coordinate universe,
with the E23–E27 calibration baked in:

* drop `H` vertices — a random scatter (`BALL=0`) or a contiguous geometric ball
  (`BALL=1`, the `H` nearest vertices to a random centre);
* candidates are the pool vertices within `HOPS` unit steps of the hole;
* solve *completely* for a refill of at most `H - DROPK` of them: a Cadical
  cardinality-constrained outer solver over the candidate set, with a hyperedge
  (CEGAR) clause added for every 4-colouring found, so the search ends either in
  a strictly smaller certified witness or in `OUTER UNSAT` = a proof that this
  hole cannot be refilled that cheaply;
* every other iteration proposes a subset of the hole directly instead of asking
  the outer solver (E24: the outer solver is a poor proposer);
* accepted trades are re-checked through `coremin.solve_core`, so each descent
  step carries a kissat UNSAT plus a drat-trim-verified proof, and the extracted
  core is a free extra jump;
* temp CNFs are `/tmp/tl_{tag}_{pid}.cnf` etc., so parallel workers never
  collide.

**Symmetry breaking is what makes any of this affordable.**  The first LNS
workers spent 6+ minutes per 4-colorability call and produced two descents in an
hour.  Fixing the colours of one triangle (WLOG — colour classes are
interchangeable; the triangle is checked against the exact edge list) drops the
same calls to seconds and the drat proof of the final witness from **1.5 GB and
still running after 30 min** to a few MB in seconds.  `coremin.py` had this,
the ported LNS did not; both now do.

Results over ~4 h of 4–6 LNS workers at hole sizes 20/25/30/45/60/80:

* 22 accepted trades (6 of which were improved further by the core jump),
  typically −1 or −2 vertices each;
* 26 neighbourhoods hit their time limit (1200–3600 s) after 250–600 CEGAR
  iterations / 500–1200 hyperedges;
* **0 `OUTER UNSAT` certificates.**  That is the expected outcome so far above
  the optimum: at 1100+ vertices the witness is still so redundant that cheaper
  refills usually exist, so neighbourhoods end in descents or timeouts rather
  than in rigidity proofs.  Hole rigidity only becomes provable near the true
  minimum, which is why E23 could close holes on the 509-witness pool.

Head-to-head at this scale, chained greedy is still the better minimiser
(≈ 20 vertices/hour against ≈ 2 for LNS), so the run kept 3–4 cores on greedy
throughout.

## T5 — certification (`emit.py`, `verify.py`)

`emit.py` turns a subset of the pool into a self-contained witness — exact
coordinates, and an edge list *recomputed* from those coordinates rather than
copied from the pool.  `verify.py` shares no code with the rest of the
directory: it re-implements the field, recomputes the exact unit-distance graph
(floats only prune, with a generous radius, so no unit pair can be missed),
compares it with the claimed edge list, and then runs kissat + drat-trim.

```
$ python3 verify.py witness_1112.pkl
1112 vertices with exact coordinates in Q(sqrt3, sqrt5, sqrt11)
5474 unit edges, each with dx^2 + dy^2 = 1 exactly, and no unit pair missing
not 4-colorable: kissat UNSAT, drat-trim s VERIFIED
5-colorable: chromatic number is exactly 5
PASS: 1112-vertex 5-chromatic unit-distance graph
```

(`witness_1121.pkl` / `verify_1121.log` is the previous certified snapshot,
kept because it was verified with the pre-symmetry-breaking encoding as well.)

## T6 — what this says about the goal

* The translated universe is real, reproducible from exact data alone, and 36
  vertices smaller than the one E45 reported (2545 vs 2581).
* Its radius frontier is tight: no smaller obstructing (rA, rB) exists for this
  base, so the ~2500-vertex scale of the universe is not the thing to attack.
* Descent from 2545 to a certified 1112 is a factor 2.3, and the descent was
  still moving when the run ended.  Getting under 509 needs another factor 2.2
  on top of that — well beyond what deletion plus 20–80-vertex region trades
  achieve at ~2 vertices/core-hour.
* The measured obstacle is precise: exact region trades only pay off once the
  witness is close to optimal (they then prove hole rigidity), but *reaching*
  that regime is exactly what greedy cannot do.  The gap between them —
  1100 down to ~500 — is where a different idea is needed: a constructive
  design in this placement (a Parts-style spindle assembly using the translated
  copy), or an exact minimiser that works on the *structure* rather than on
  vertex neighbourhoods.

## Files

| file | what |
|---|---|
| `tuniv.py` | exact rebuild of `A u (T + omega*A)`; writes `tuniv_1.6_1.3.pkl` |
| `tasym.py` | asymmetric-radius frontier scan (T2) |
| `check.py` | 4-colorability of a universe or a subset (kissat) |
| `coremin.py`, `greedy8.py` | DRAT-core minimisation and batched greedy (ported) |
| `tlns.py` | exact large-neighbourhood region trades (T4) |
| `chain.sh`, `launch.sh`, `best.py`, `monitor.sh` | worker chaining on the shared best witness |
| `emit.py` | subset -> self-contained witness with recomputed exact edges |
| `verify.py` | standalone verifier (prints PASS) |
| `best_1112.pkl`, `witness_1112.pkl`, `verify_1112.log` | the certified result |

## Reproduce

```
python3 tuniv.py                                  # exact universe
python3 verify_universe.py tuniv_1.6_1.3.pkl 3 5 11
python3 check.py tuniv_1.6_1.3.pkl                # kissat: UNSAT
POOL=tuniv_1.6_1.3.pkl python3 coremin.py 1
POOL=tuniv_1.6_1.3.pkl python3 greedy8.py 1 coremin_seed1.pkl g1
MODE=greedy SEED=51 ./chain.sh                    # chained descent
MODE=lns SEED=54 H=20 BALL=0 DROPK=1 ./chain.sh   # exact region trades
python3 emit.py tuniv_1.6_1.3.pkl best_1112.pkl witness_1112.pkl
python3 verify.py witness_1112.pkl                # PASS
```

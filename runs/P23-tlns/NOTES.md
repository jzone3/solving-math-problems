# P23 — exact large-neighbourhood descent in the *translated-placement* universe

Child run of `runs/P23-fusion1` (E43–E50).  Goal: a 5-chromatic unit-distance
graph with fewer than 509 vertices (Parts' record) inside the translated
placement `A u (T + omega*A)` that E43–E45 discovered, using the exact
region-trade machinery of E23–E27.

Everything here is exact: floats only ever prefilter, and every accepted unit
edge satisfies `dx^2 + dy^2 = 1` in `Q(sqrt3, sqrt5, sqrt11)`.

## T1 — the universe, rebuilt from the lattice decomposition (`tuniv.py`)

`runs/P23-fusion1/tscan2.pkl` (the float scan that produced the working
translation) was never committed, so the universe is rebuilt from the *exact*
decomposition recorded in E43 instead, which is better anyway — no float scan is
involved at any point:

```
omega = w[15] = (7 + i sqrt15)/8         (rotation about the origin)
T     = a + omega*b,  12a = (0,0,4,0),  12b = (6,0,-6,0)
A     = 3 Minkowski layers of the 30 unit vectors of Parts' ring
        (lattice.build_base(3, r)), clipped at radius r
universe(rA, rB) = A(rA)  u  (T + omega*A(rB))
```

with `rA = 1.6`, `rB = 1.3` (the asymmetry of E45):

```
2545 vertices, 14316 exact unit edges (1441 A-half / 1104 B-half)
kissat: s UNSATISFIABLE for 4 colours  (206 s)
verify_universe.py: 2545 vertices, 14796 exact edges: PASS  (edges recomputed
                    independently from the coordinates)
```

That is **2545 vertices against the 2581 of E45** — the same placement, a
slightly different Minkowski base, and the smallest exactly-verified
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

So 1.6/1.3 is on the frontier here exactly as in E45, and the asymmetry is again
real rather than a size effect (1.7/1.2 has 2503 vertices and is 4-colorable,
1.6/1.35 has 2557 and is not).

## T3 — greedy to the floor (`coremin.py`, `greedy8.py`, `chain.sh`)

Pipeline of E27: DRAT-core minimisation first, then batched (8-4-2-1) greedy
deletion where every accepted deletion is re-certified by kissat + drat-trim and
the proof core is used as a free jump.

* 5 independent DRAT-core chains from the whole 2545-vertex universe:
  1757, 1772, 1784, 1814, 1725 (each ~30 iterations of ~35 s).
* batched greedy from those cores, then chained (every worker restarts from the
  smallest witness any worker has produced).

Progress of the chained descent (all intermediates certified non-4-colorable):

```
2545 -> 1725 (core chains) -> 1527 -> 1465 -> 1422 -> 1399 ...
```

(continued below)

## Reproduce

```
python3 tuniv.py                       # rebuild the universe exactly
python3 verify_universe.py tuniv_1.6_1.3.pkl 3 5 11
python3 check.py tuniv_1.6_1.3.pkl     # kissat: UNSAT
POOL=tuniv_1.6_1.3.pkl python3 coremin.py 1
POOL=tuniv_1.6_1.3.pkl python3 greedy8.py 1 coremin_seed1.pkl g1
POOL=tuniv_1.6_1.3.pkl START=greedy_g1.pkl H=40 DROPK=2 SEED=1 python3 tlns.py
python3 emit.py tuniv_1.6_1.3.pkl <witness>.pkl witness.pkl
python3 verify.py witness.pkl          # standalone: prints PASS
```

# P11 — V5 run notes (character-theory / mechanized nonexistence)

Session: variant V5 of P11 (circulant weighing matrices, open Strassler cells).
Goal per problem file: mechanize the standard nonexistence toolbox (multiplier
theorems, self-conjugacy/Lander, field descent) over all open cells n<=200.

## 1. Statement & openness re-verification (source check)

- Source of truth: github.com/dmgordo/circulant-weighing-matrices `cwm.json`
  (La Jolla CWM repository export). HEAD = commit 5b3d729 (2026-04-24).
- Current dataset has **28** cells with status "Open" in Strassler's range
  (n<=200, k=s^2<=100), not 22 as the problem file says. The 6 cells named in
  the problem file are all "Open" in the current dataset.
- Reconciliation vs AGZ 2021 Table 10 (22 open): dataset additionally lists
  as Open the 5 regression cells below, plus CW(132,81) and CW(182,64)
  (AGZ Props 4.2/5.1 claim these are dead but the dataset has never credited
  those two propositions -- see Finding B); conversely dataset marks
  CW(116,49) No (AGZ) though it appears in the paper's open table.
  22 + 7 - 1 = 28: consistent.

### Finding A (data regression in the source repository — witnesses recovered)

Comparing dataset history: commit 1113578 (2024-03-03) vs the 2025-01-24
re-upload (a58ff99) shows several cells were silently demoted from
Yes-with-witness to Open. The old witnesses **machine-verify** as valid CWMs:

| cell        | status now | witness source                    | verified |
|-------------|-----------|------------------------------------|----------|
| CW(96,36)   | Open      | cwm.json @ 1113578                 | PASS     |
| CW(146,64)  | Open      | cwm.json @ 1113578                 | PASS     |
| CW(155,25)  | Open      | cwm.json @ 1113578                 | PASS     |
| CW(165,25)  | Open      | cwm.json @ 1113578                 | PASS     |
| CW(186,25)  | Open      | cwm.json @ 1113578                 | PASS     |
| CW(228,49)  | Open      | lift x2 of CW(114,49) (Yes now)    | PASS     |
| CW(242,81)  | Open      | lift x2 of CW(121,81) (Yes now)    | PASS     |

Witnesses + standalone verifier: `solutions/P11/witnesses.json`,
`solutions/P11/verify.py` (prints PASS). Note CW(96,36) is also implied by
CW(48,36)="Yes" in the *current* dataset (padding A(X)->A(X^2)), so the
current "Open" marking is internally inconsistent — clearly a data
regression, not a mathematical reopening. These cells are absent from Tan's
2018 open list and from AGZ 2021's Table 10 of remaining open cases, i.e.
they were considered settled (Yes) in the literature. **So: not new
mathematics, but the problem file's cell CW(96,36) is not actually open, and
the live repository data should be reported/fixed upstream.**

### Finding B (dataset vs AGZ paper discrepancy)

arXiv:1908.08447v3 (= Cryptogr. Commun. 2021) Prop 4.2 claims no CW(132,81)
and Prop 5.1 claims no CW(182,64), both via McFarland d-multipliers
(Theorem 4.1) applied to contracted ICWs. The dataset (maintained by
coauthor Gordon) has listed BOTH cells as "Open" in every commit
(2024-2026), while crediting the paper's other 11 kills ("Arasu, Gordon and
Zhang (Preprint 2020)"). No erratum found (Crossref/Exa search). Exactly the
two results that rely on Theorem 4.1 are excluded — consistent with the
known subtlety that classical multiplier-theorem proofs use nonnegativity
of coefficients, which fails for ternary/integer group-ring elements.
Treated here as genuinely open; our ICW exhausts below re-verify the
*computational core* of those propositions (conditional on Thm 4.1).

## 2. Toolbox mechanized (`cwm_tools.py`, `battery.py`)

- Theorem 2.4 (prime-power multiplier) and Theorem 4.1 (McFarland
  d-multiplier for the contraction ICW_d(m,k), m=n/d, d=gcd(n,k),
  needs gcd(m,k)=1): multiplier set = intersection of <p_i> in Z_m^*.
- Fixed-translate reduction: if t is a multiplier and gcd(s,m)=1 then some
  translate of B is fixed by t (weighted-sum argument); checked per cell.
- Lander/self-conjugacy (Thm 2.2): p self-conjugate mod m' => folded image
  mod m' is == 0 (mod p^a); with sum=s, sum of squares=k this forces the
  trivial folding s*delta_j at a fixed-point residue j.
- Orbit exhaust (Algorithm 1 equivalent): DFS over multiplier orbits,
  coefficients in [-d,d], moment pruning, full autocorrelation check at
  leaves.

## 3. Results

Engine: `exhaust_cw.c` (compiled as `exhaust_icw`; args `m s d t [q:j ...]`).
Validation of engine: reproduces AGZ Table 9 solution counts (up to
equivalence-counting conventions) on (105,36),(117,36),(140,36),(180,36),
(140,64),(180,64),(196,64),(156,81),(198,81),(112,100),(120,100),
(156,100),(165,100),(195,100); positive control: finds the classical
CW(57,49) (72 fixed solutions) and CW(63,16) (8 fixed solutions).

### 3a. ICW_d(m,k) exhausts over all open cells (icw_*.out)

| cell        | m  | d  | t  | #ICW fixed sols | verdict |
|-------------|----|----|----|-----------------|---------|
| CW(105,36)  | 35 | 3  | 4  | 2  | survives (ICWs exist) |
| CW(112,36)  | 7  | 16 | 2  | 3  | survives |
| CW(117,36)  | 13 | 9  | 3  | 9  | survives |
| CW(140,36)  | 35 | 4  | 4  | 2  | survives |
| CW(180,36)  | 5  | 36 | 2  | 1  | survives |
| CW(195,36)  | 65 | 3  | 16 | 8 (fold 5:0) | survives |
| CW(140,64)  | 35 | 4  | 2  | 4  | survives |
| CW(180,64)  | 45 | 4  | 2  | 2  | survives |
| CW(182,64)  | 91 | 2  | 2  | **0** | killed, conditional on Thm 4.1 (= AGZ Prop 5.1); independently re-verified by icw_recheck.py (FFT-based, 0 sols) |
| CW(196,64)  | 49 | 4  | 2  | 4  | survives |
| CW(132,81)  | 44 | 3  | 3  | **0** | killed, conditional on Thm 4.1 (= AGZ Prop 4.2); independently re-verified by icw_recheck.py (FFT-based, 0 sols) |
| CW(156,81)  | 52 | 3  | 3  | 264 | survives |
| CW(195,81)  | 65 | 3  | 3  | 8 (fold 5:0) | survives |
| CW(198,81)  | 22 | 9  | 3  | 18 | survives |
| CW(112,100) | 7  | 16 | 2  | 3  | survives |
| CW(120,100) | 3  | 40 | 2  | 1  | survives |
| CW(155,100) | 31 | 5  | -  | -  | multiplier group trivial; method inapplicable |
| CW(156,100) | 39 | 4  | 5  | 12 | survives |
| CW(165,100) | 33 | 5  | 4  | 12 | survives |
| CW(182,100) | 91 | 2  | 64 | (running) | |
| CW(195,100) | 39 | 5  | 5  | 12 | survives |

Notes: counts are raw fixed-by-t solutions with B(1)=+s (no dedup by
decimation/translation), hence larger than AGZ's equivalence-class counts.
Fold 5:0 justifications: see section on fold normalization below.
Cross-implementation controls: icw_recheck.py (independent Python DFS +
FFT flat-power check) reproduces 9 sols for ICW9(13,36), 2 for ICW3(35,36),
8 for CW(63,16), and 0/0 for the two killed cells.

### 3b. CW(120,49): UNCONDITIONAL NONEXISTENCE (new result, pending
independent confirmation)

k=49=7^2, gcd(120,49)=1: by Theorem 2.4 (Arasu et al., standard), 7 is a
multiplier and (since gcd(7,120)=1, weighted-sum argument) some translate
of any CW(120,49) is fixed by x->7x; wlog A(1)=+7 (negation). Orbits of <7>
on Z_120: 39 (6 fixed pts, 9 of size 2, 24 of size 4). Fold constraints
proved above (mod 8 = 7*delta_0 after X^20-shift normalization; mod 5 and
mod 10 = 7*delta_0 forced). Exhaust:

    ./exhaust_cw 120 8:0 5:0 10:0
    n=120 done: solutions=0 nodes=21574791268 leaves=800338644

**Zero solutions** => no CW(120,49) exists.  This cell is listed as open in
Strassler's table (Tan 2018, AGZ 2021 Table 10, current La Jolla dataset).
Chain of reasoning is entirely classical (Thm 2.4 + Lander self-conjugacy +
exhaust); the only trust point is the search code, so an independent
differently-written re-verification is REQUIRED before claiming solved
(recheck run with the rewritten engine + a Python reimplementation in
progress; also positive control CW(57,49) passes).

### 3c. CW(192,49): decision run in progress

Same setup (7 multiplier, ord(7 mod 192)=8, 51 orbits); 7 self-conjugate
only mod 8 among useful divisors; residual translations are X^{32j} == 0
(mod 8), so the two fold cases 8:0 and 8:4 cannot be merged and both are
being run (`exhaust192_f0.out`, `exhaust192_f4.out`).

### Fold-normalization proofs

n=120, s=7: 7 is self-conjugate mod 8 (7=-1), mod 5 (7=2, 2^2=-1), mod 10
(7^2=49=-1). Lander Thm 2.2 applied to the folded image (an ICW_{120/q}(q,49)
with B B^(-1) = 49 * identity in Z[Z_q]) forces B == 0 (mod 7); with
sum b = 7 and sum b^2 = 49 that means B = 7*delta_j. Since A is fixed by 7,
so is B, so j is a fixed point of x->7x mod q. Mod 8: j in {0,4}; the
residual translations preserving fixedness are X^a, 6a==0 (mod 120), i.e.
a in 20Z; X^20 shifts j by 4 mod 8 (and by 0 mod 5), so wlog j=0 mod 8.
Mod 5: 7x==x forces j=0. Mod 10: j in {0,5}; j=5 puts mass 7 on odd
residues, contradicting the mod-8 fold (all mass at 0 mod 8, i.e. even
positions have total 7, odd positions total 0 via the mod-2 coarsening);
so j=0 mod 10.

n=195 cells (fold 5:0): for k=36, both 2 and 3 are self-conjugate mod 5
(2^2=4=-1, 3^2=9=-1), so the mod-5 fold is == 0 mod 6, hence = 6*delta_j;
for k=81, 3 self-conjugate mod 5 and 3^4||81 gives fold == 0 mod 9, hence
= 9*delta_j. Residual translations X^{13a} generate all shifts mod 5
(13=3 mod 5 is a unit), so wlog j=0.

## 4. Dead ends / limitations

- CW(155,100): largest coprime contraction m=31 has trivial McFarland
  multiplier group (<2> and <5> in Z_31^* intersect trivially), so the
  entire multiplier machinery is inapplicable. Same reason AGZ left it out
  of Table 9. No new handle found.
- Cells with #ICW>0 would need a lift-exhaust over Z_n without a full-group
  multiplier -- the search space has no orbit compression and is infeasible
  (this is exactly why these cells are still open).
- Field descent (Schmidt) bounds are vacuous at these sizes (n<=200,
  k<=100); self-conjugacy fails in the surviving cells for the relevant
  moduli, which is why Lander's theorem cannot be pushed further.

## 5. Compute summary (8-core VM, gcc -O3)

- ICW battery (21 cells): seconds to ~1 h each; largest ICW3(52,81):
  4.8B nodes. Total ~2 h CPU.
- CW(120,49) decision: 21.6B nodes, ~65 min (run twice: original + rewritten
  engine, identical zero-solution outcome and node count).
- Positive control CW(57,49): 1.9B nodes, found 72 fixed solutions.
- CW(192,49): two fold cases split 3-way each (deterministic node-counter
  partition, validated on CW(63,16) and CW(57,49) splits); hundreds of
  billions of nodes searched, still running at session close.
- SAT independent checks: CaDiCaL/kissat on 13.8M-clause (no-fold) and
  ~14M-clause (with-fold) encodings of "CW(120,49) fixed by 7 exists";
  running (UNSAT expected). SAT encoding validated SAT-side on CW(57,49)
  (returns a witness that machine-verifies) and CW(63,16)+fold.
- ICW zero cells re-verified by a second, independently written Python/FFT
  exhaust (icw_recheck.py): 0 solutions for both, and exact count agreement
  on three nonzero controls.

STATUS: see end of file.

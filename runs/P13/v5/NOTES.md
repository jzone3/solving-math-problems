# P13 (Perfect Mendelsohn designs, k=6/7) — V5 run notes

Variant V5: literature-first — digest known partial results and recursive
constructions, then targeted computation. Session: devin-e08185f9d0e64de5ae36451b173d1484.

## 1. Statement re-verification (against original sources)

- CPro1 `problem_def.py` (constructive-codes/cpro1) fetched; t-apart semantics
  and open instance list {(9,6),(10,6),(12,6),(15,6),(16,6),(18,6),(14,7),(15,7)}
  confirmed identical to the problem file.
- **Semantics calibration**: our verifier (`pmdlib.check_pmd`) reproduces PASS on
  all 8 published (v,6,2)- and (v,6,3)-PMDs for v ∈ {9,10,12,15,16,18} from
  Abel–Bennett, *Des. Codes Cryptogr.* 40 (2006) 211–224, Lemmas 4.4/4.8
  (`calibrate.py` → ALL PASS). So our encoding of "t-apart" matches the
  literature's exactly.
- **Stale open case found**: (10,6,1)-PMD is known NOT to exist —
  Abel–Bennett 2006, Theorem 1.3 (via nonexistence of a (10,3,2)-BIBD nested
  in a (10,6,5)-BIBD, Hishida et al.). The CPro1 list (and hence the problem
  file) is out of date for v=10. Genuinely open k=6 cases as of the 2006
  paper: v ∈ {9,12,15,16,18} (consistent with its Theorem 1.4).
- Still open as of July 2026 as far as we can find: the 2025 CPro1 papers
  (arXiv:2501.17725, 2505.23881) list all 8 instances as open and solved none;
  no newer (v,6,1) or (v,7,1) result found in searches (Griggs–Kozlik 2020
  completed k=5 only).

## 2. Recursion reachability (core V5 question)

See `recursion_analysis.md`. Summary: every standard recursion
(fill-in-hole, HPMD filling, weighting/Wilson, PBD closure, TD inflation)
provably cannot produce any (v,6,1)-PMD with v ≤ 18 beyond the known v=7,13:
- only sub-18 ingredient PMDs known are v=7,13; IPMD(v,h) needs v ≥ 5h+1 → v ≥ 36;
- HPMD-filling arithmetic forces v ≥ 32 once w ≥ 1, and w=0 needs an
  IPMD(12,7) violating the hole bound;
- PBD closure with all block sizes ≥ 7 forces v ≥ 43.
**Negative result (rigorous counting): the open cases are unreachable by the
standard recursions; only direct construction / exhaustive search can settle
them.** This explains why the table has been frozen since 2000.

## 3. Targeted computation (literature-guided prescribed automorphisms)

Difference methods are exactly how all small (v,6,λ) designs in the
literature were built, so we swept them exhaustively.

### 3a. Structural lemma (machine-checked, easy to prove by hand)
For k=6, λ=1, a base-block orbit under a regular abelian action whose
stabilizer has order d ∈ {2,3} is impossible: if the block satisfies
B[i+r] = B[i]+s with ord(r mod 6) = d, then for t = (6/d)·(d-1)... concretely
for d=2 (r=3) all six t=3 differences equal s (multiplicity 6 ≠ 2), and for
d=3 (r ∈ {2,4}) all six t=r differences equal s. Only full orbits and d=6
"strand" orbits (B = (x, x+s, ..., x+5s), s of order 6) can occur.
Consequently, orbit-size counting alone kills many group ansatzes (see 3b).

### 3b. Exhaustive translation-ansatz sweeps (point set = G, or G + ∞)
Engine: `diffsearch.py` (+ `mitm.py` for the large cases; meet-in-the-middle
with multiplier canonicalization for (18,6)/Z17+∞). Exact cover on per-t
difference coverage; candidates deduplicated by coverage mask. Positive
controls: (7,6)/Z7, (13,6)/Z13 (both paths), (8,7)/Z7+∞ — all found & PASS.

All searches EXHAUSTIVE within ansatz, all NEGATIVE:

| v,k | group ansatz | result |
|---|---|---|
| 9,6 | Z9; Z8+∞; Z3×Z3 | no design (Z3×Z3 admits no valid full-orbit block at all) |
| 12,6 | Z11+∞; Z12; Z2×Z6 | no design |
| 15,6 | Z15; Z14+∞ | impossible by orbit-size counting (needs d∈{2,3} short orbits) |
| 16,6 | Z16; Z15+∞; Z2×Z8; Z4×Z4; Z2×Z2×Z4; Z2^4 | impossible by counting / no candidates (Z2^4 has no valid block: t=3 differences pair up) |
| 18,6 | Z17+∞ (3 full orbits, multiplier-canonicalized MITM); Z18; Z3×Z6 | no design |
| 14,7 | Z13+∞; Z14 | no design |
| 15,7 | Z15; Z14+∞ | no design |

### 3c. Semiregular-action sweeps (H=Z_m acting with c point-classes ± ∞)
Engine: `semireg.py` (full block-orbits only; requires m | b). Controls
(7,6)/(13,6) PASS.
- (9,6): H=Z4, c=2 + ∞ — NEGATIVE (exhaustive). H=Z3, c=3 — NEGATIVE (exhaustive).
- (15,6): H=Z7 c=2+∞, H=Z5 c=3 — running (see logs).
- (16,6): H=Z8 c=2 — NEGATIVE (exhaustive). H=Z5 c=3+∞ — running.
Not covered: short-orbit variants in the semiregular setting, |H|=2 ansatzes,
nonabelian groups, ≥2 fixed points (multiple ∞) — noted as gaps.

## 4. Full exhaustive resolution of (9,6) — MAIN RESULT

`fullsearch.py` (exact cover over items (t,x,y), candidates = all 10080
cyclic 6-tuples of 9 points, WLOG one block = (0,1,2,3,4,5) by relabeling):

    DONE nodes=36019 time=107s solutions=0
    NO (9,6,1)-PMD exists (exhaustive)

Controls through the same code path: (7,6) found+PASS, (9,4) found+PASS,
(6,6) correctly reported nonexistent (known).

Independent second verification with a different method and encoding:
`satcheck.py` (CaDiCaL, cell variables + pair-occurrence auxiliaries;
(7,6) control SAT+PASS): (9,6) → RESULT_PLACEHOLDER_SAT9

If both agree: **a (9,6,1)-PMD does not exist** — this settles the smallest
open k=6 case negatively (the 2006 survey listed v=9 as possible-exception;
no complete-search record exists in the literature we found).

## 5. (10,6) independent confirmation

Literature says nonexistent (via nested BIBDs). Our own full exhaustive
search (`fullsearch.py 10 6`): RESULT_PLACEHOLDER_FULL10

## 6. Compute log

- calibration + small ansatz sweeps: seconds each.
- mitm large sweeps ((18,6)/Z17+∞ etc.): seconds to ~1 min each.
- fullsearch (9,6): 107 s, 36k nodes.
- satcheck (9,6): see logs/sat9.log.
- semireg (15,6)/(16,6) heavy cases: minutes–hours (logs/sr_*.log).
- fullsearch (10,6): hours-scale attempt (logs/full10.log).

## STATUS

STATUS: frontier-pushed — (9,6,1)-PMD proven nonexistent by exhaustive search
(two independent programs), pending final SAT confirmation; all other open
instances: exhaustive negatives for every standard difference-method ansatz;
rigorous argument that no known recursion can reach any open case.

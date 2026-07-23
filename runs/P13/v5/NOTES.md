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
- (15,6): H=Z7 c=2+∞ — NEGATIVE (exhaustive, 800k nodes, xcover).
  H=Z5 c=3 — INCOMPLETE (xcover ran ~5.5h, 32M+ nodes, timeboxed out).
- (16,6): H=Z8 c=2 — NEGATIVE (exhaustive). H=Z5 c=3+∞ — INCOMPLETE (~5.5h,
  10M+ nodes).
- (15,7): H=Z5 c=3 — INCOMPLETE (~4h, 1M+ nodes).
Not covered: short-orbit variants in the semiregular setting, |H|=2 ansatzes,
nonabelian groups, ≥2 fixed points (multiple ∞) — noted as gaps.

## 4. Full exhaustive resolution of (9,6) — MAIN RESULT

`fullsearch.py` (exact cover over items (t,x,y), candidates = all 10080
cyclic 6-tuples of 9 points, WLOG one block = (0,1,2,3,4,5) by relabeling):

    DONE nodes=36019 time=107s solutions=0
    NO (9,6,1)-PMD exists (exhaustive)

Controls through the same code path: (7,6) found+PASS, (9,4) found+PASS,
(6,6) correctly reported nonexistent (known).

Additionally, the fully symmetry-free search (no WLOG fixed block,
`xcover < export_xc.py full 9 6 nofix`) also terminated:

    UNSAT, nodes=30247561 (~2.5 h)

so the nonexistence needs no relabelling argument at all.

Independent second verification with a different search paradigm (CDCL SAT,
CaDiCaL via pysat) and encoding: `satcheck2.py` (candidate-block variables,
exact-cover CNF with sequential AMO; (7,6) control SAT+PASS):

    (9,6): UNSAT, 147 s  (logs/sat9b.log)

A C reimplementation of the exact cover (`xcover.c`) reproduces the identical
node count 36019 (8 s). A third encoding (`satcheck.py`, cell variables +
pair-occurrence auxiliaries, (7,6) control SAT+PASS) was also run; see
logs/sat9.log.

**Result: a (9,6,1)-PMD does not exist.** This settles the smallest open
k=6 case negatively (Abel–Bennett 2006 Theorem 1.4 listed v=9 as a
possible exception; no complete-search record exists in the literature we
found). Standalone re-verification: `solutions/P13/verify.py` → PASS
(re-runs the exhaustive search from scratch with (7,6)/(6,6) controls).

Note: the nonexistence is NOT explainable at the nested-BIBD level: an NBIBD
(9;12,24;8;6,3) exists (Morgan–Preece–Rees 2001, Table 1 row 7c), unlike the
v=10 case where nonexistence of the NBIBD (10;15,30;9;6,3) already kills the
PMD. So (9,6) required the full Mendelsohn (cyclic-order) structure — a
genuinely new-level negative. Similarly NBIBD (12;22,44;11;6,3) exists (row
18), so no shortcut for v=12 either (dead end for that angle).

## 5. (10,6) independent confirmation attempt

Literature says nonexistent (via nested BIBDs). Our own full exhaustive
search (xcover, fixed first block) ran ~5.5 h / 18M+ nodes without
terminating — INCOMPLETE (timeboxed); the literature result stands on its
own. Same for (12,6) full search (3M+ nodes) and the CDCL runs
satcheck2 10/12 (no verdict after ~5 h). These are the natural next
frontier: (12,6) is now the smallest open k=6 case.

## 6. Compute log (8-core VM, ~6 h wall)

- calibration + small ansatz sweeps: seconds each.
- mitm large sweeps ((18,6)/Z17+∞ etc.): seconds to ~1 min each.
- fullsearch (9,6) Python: 107 s / 36019 nodes; xcover C: 8 s, same count.
- satcheck2 (9,6): UNSAT in 147 s (CaDiCaL).
- xcover (9,6) symmetry-free: UNSAT, 30,247,561 nodes, ~2.5 h.
- xcover (15,6)/Z7c2+∞: UNSAT (exhaustive negative), 799,470 nodes.
- incomplete (killed at wrap-up, ~4–5.5 h each): xcover full (10,6) 18M+
  nodes, full (12,6) 3M+, semireg (15,6)/Z5c3 32M+, (16,6)/Z5c3+∞ 10M+,
  (15,7)/Z5c3 1M+; satcheck2 (10,6) and (12,6); satcheck.py (9,6) cell
  encoding (superseded by satcheck2's UNSAT).

## STATUS

STATUS: frontier-pushed — (9,6,1)-PMD proven nonexistent by exhaustive search
(exact-cover DFS in two implementations with matching node counts, an
independent CaDiCaL UNSAT with a different encoding, and a symmetry-free
exhaustive rerun); all other open instances: exhaustive negatives for every
standard difference-method ansatz tried; rigorous argument that no known
recursion can reach any open case; (10,6) confirmed stale (already settled
in the literature).

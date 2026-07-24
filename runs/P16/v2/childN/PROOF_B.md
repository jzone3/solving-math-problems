# P16 childN — Inequality (B) is FALSE; Conjecture J is FALSE; Conjecture H is FALSE

**Status: DISPROOF COMPLETE.** The goal of this session was to prove
inequality (B) (and boundary case (W=)), the last missing pieces of
Conjecture J.  Instead we found **explicit counterexamples**: (B) fails, clause
(b) of Conjecture J fails, and — much more importantly — **Conjecture H itself
is false**, on an explicit 40-vertex tree, while Bound 44 remains true there
(λ² ≈ 19.36 vs R = 197/8 = 24.625).  The entire certificate program
"Bound 44 ⇐ H ⇐ J ⇐ (B)+(W=)+(a)" is dead as stated: the certificate family
v = s + c·1 is not rich enough to witness Bound 44 on all graphs.

Everything below is verified in exact rational arithmetic by the
self-contained, dependency-light script `verify_counterexamples.py`
(no shared library code; line graph, 2-walks, ρ₀, the H-interval and the
clause-(b) pairwise test are all recomputed from scratch), and independently
by `exp15_realize.py`/`exp16_independent_verify.py` (which use childL's
`common.py` and a from-scratch implementation, respectively).

## 1. The counterexample T40 (n = 40 tree)

Rooted description (i–j is the special edge):

- `i` (degree 4) — joined to `j` and to three branch vertices `k₁,k₂,k₃` of
  degree 4; each `k` has three children of degrees (2,2,3); every child of
  degree c carries c−1 leaves.
- `j` (degree 3) — joined to `i`, one pendant leaf, and one branch vertex
  `l` of degree 4 whose three children have degrees (4,4,4); again each child
  of degree c carries c−1 leaves.

Total: 2 + 3 + 9 + 15 + 2 + 3 + 9 − 3 = 40 vertices (see `build_T40()`).

Exact data at e = ij:

| quantity | value |
|---|---|
| s_e | 7 |
| z1_e = (A_L²1)_e | 25 |
| zs_e = (A_L²s)_e | 175 |
| w_e = zs_e − s_e·z1_e | **0** |
| arg44_e | 49/2 |
| ρ₀(e) (2-ball max arg44) | 197/8 |
| global R = max_g arg44_g | **197/8** (= ρ₀(e)!) |

- **Heavy:** z1_e = 25 > 197/8 = ρ₀(e).
- **(B) violated:** D_e = ρ₀(e)(s_e−3) + 3z1_e − zs_e = (197/8)·4 + 75 − 175
  = **−3/2 ≤ 0.**
- **Clause (b) of Conjecture J violated:** with f any edge of degree-sum
  s_f ≤ 6 (33 admissible violating pairs), e.g. at ρ = 197/8:
  ρ·s_e − zs_e + s_f(z1_e − ρ) = (3s_f − 21)/8 < 0.  Hence **Conjecture J is
  false.**
- **Conjecture H violated:** here ρ₀(e) equals the *global* R, so the heavy
  edge survives globally.  The interval of Corollary H3 requires
  c ≤ (R·s_e − zs_e)/(z1_e − R) = −(21/8)/(3/8) = **−7** from edge e, while the
  lower bounds give c ≥ −76/39 ≈ −1.95 and positivity requires c > −min s = −3.
  The interval is **empty**: no c > −min s_e with (A_L²(s+c1)) ≤ R(s+c1).
  **Conjecture H is false.**
- **Bound 44 is still true** on T40: λ(A_L)² ≈ 19.3617 ≤ 24.625 = R, with
  large slack.  (So T40 does not threaten Bound 44 — it kills the
  *certificate*, not the *bound*.)

Why verification never saw it: H was verified exhaustively for all connected
n ≤ 10 and all trees n ≤ 18 (childH), (B) for n ≤ 9, trees ≤ 16 and ~400
random graphs n ≤ 60.  T40 has 40 vertices and its structure (three identical
degree-4 branches tuned so that arg44_{ik} = 197/8 sits 3/8 below z1_e = 25,
plus a j-side branch inflating zs) has essentially zero probability of being
hit by uniform random tree sampling (a dedicated 60k random-tree search in
`exp20_random_H.py` finds nothing).

## 2. The counterexample T52 (n = 52 tree) — (B)/clause (b) with strict slack

`build_T52()`: i of degree 5 with four degree-5 branches (each: four children
of degree 2, each carrying one leaf); j of degree 3 with a pendant and one
degree-3 branch with two degree-6 children (each carrying five leaves).

At e = ij: s = 8, z1 = 38, zs = 308, **w_e = +4 > 0**, arg44_e = 188/5,
ρ₀(e) = 948/25 < 38 = z1 (heavy), D_e = **−22/5 < 0**.  Here the global
R = 54 > z1 (third-shell spikes), so H is untouched (interval nonempty) —
T52 shows the *2-ball-local* statements (B)/(b) are false even when the global
certificate exists.  It also refutes the margin conjecture (D_e ≥ 1) in the
strongest possible way and shows w_e > 0 is possible on heavy edges.

Bonus: `exp13_w1b_counterexample.py` gives an n = 35 tree where the (weaker
premise) statement W1B — "z1_e ≥ ρ₁(e) ⇒ w_e ≤ 0" — fails with w_e = 4
(z1 = 27, ρ₁ = 238/9 ≈ 26.4), refuting the 1-ball form of childJ's V1 as well.

## 3. How the counterexamples were found (the adversary method)

Write everything at e = ij in *star data*: x = d_i, y = d_j, the degree
multisets {d_k} (k ∼ i, k ≠ j), {d_l} (l ∼ j, l ≠ i), and the branch averages
m_k.  Then (identities I6–I8 of childL):

- z1_e = (s−2)² + x·m_i + y·m_j − 2xy,
- w_e = Σ_k (d_k−y)(d_k+y−4) + Σ_{k∼i} d_k(m_k−y) + (symmetric in j) with the
  cross terms x(m_i−x) + y(m_j−y),
- D_e = (s_e−3)(ρ₀−z1_e) − w_e, so a **heavy edge with w_e ≥ 0 close enough to
  the window edge violates (B)**.

The adversary maximizes w_e ≥ 0 subject to *every 2-ball edge having
arg44 < z1_e* (which forces ρ₀ < z1, i.e. heaviness).  Constraints per branch
k of degree t: (C1) arg44_{ik} < z1, i.e. m_k < (z1/2 − (x−1)² − (t−1)² + xt)/m_i,
integrality t·m_k ∈ ℤ; (C2) each second-shell child of degree c must satisfy
arg44_{ku} < z1 with m_u = (t+c−1)/c after minimal leaf padding — the leaves
sit at line-graph distance 3, *outside* B₂(e), so their own arg44 (which can be
huge) never enters ρ₀(e).  This "pad just beyond the horizon" trick is exactly
why every fixed-radius localization fails: for T40 even the 3-ball max equals
197/8 (the spikes are absent entirely because R itself is small — this is what
also kills H).

Search pipeline: `exp12_Wstar.py` (1-ball adversary → first abstract w > 0
configs), `exp14_W2star.py` (full 2-shell adversary with exact per-child
feasibility → config (x,y) = (5,3), dk = (5,5,5,5), dl = (1,3) with w = 4 →
T52), `exp17_minimal.py` (exact minimization of realization size over the
tree family → T40, the smallest member found, with w = 0).

Minimality status: connected n ≤ 10 and trees n ≤ 18 are clean for H
(childH's exhaustive runs), and n ≤ 9/trees ≤ 16 for (B) (childL).  So the
minimal counterexamples live in 11…40 (graphs) / 19…40 (trees); T40 is the
smallest we found (best over the portion of the tree-family search space
x,y ≤ 6, branch degrees ≤ 9, child degrees ≤ 12 covered by
`exp17_minimal.py` within this session).

## 4. What survives, what dies

| statement | status |
|---|---|
| Inequality (B) | **FALSE** (T40: D = −3/2; T52: D = −22/5) |
| Margin conjecture D_e ≥ 1 | **FALSE** |
| (W=) boundary case | untested by T40/T52 (both are strictly heavy); the same adversary at exact equality produced no realized violation in this session — open, but moot for J |
| Clause (b) of Conjecture J | **FALSE** (T40, T52) |
| Conjecture J | **FALSE** |
| Conjecture H (childH PROOF44 §5) | **FALSE** (T40: needs c ≤ −7 < −3 = −min s) |
| Bound 44 | **still true on every graph tested**, incl. T40/T52 (λ² = 19.36 vs 24.63, resp. 30.45 vs 54) |
| childH's reduction "H ⇒ Bound 44" (Lemmas H1–H3) | still valid — but its hypothesis is now known to be unsatisfiable in general |
| childL Theorem L1, L2, Lemma X | still valid as implications; vacuous for proving J |

## 5. Consequences and recommended next steps

1. **Stop trying to prove (B)/(W=)/J/H.** All the "resisting configurations"
   catalogued by childJ/childL were real obstructions, not artifacts.
2. Bound 44 itself still stands (n ≤ 10 exhaustive + all hard sets + T40/T52
   here).  Since λ² ≤ R ⇔ ∃ v > 0 with A_L²v ≤ Rv (second-order
   Collatz–Wielandt, childH Lemma H1), Bound 44 is *equivalent* to the
   existence of SOME positive certificate vector — the failure is specifically
   that v = s + c·1 is too rigid.  On T40 the certificate must give the heavy
   edge e = ij a *larger* weight relative to its 2-ball than any affine
   function of s can (v_e must exceed (A_L²v)_e/R even though z1_e > R).
3. Natural richer families to try next (all still 2-local, exact-checkable):
   v = s + c·1 + β·(R·1 − arg44) (slack-weighted); v_e = max(s_e + c, γ·z1_e/R);
   or two-parameter v = α s + β z1 + c·1.  A quick sanity requirement: on T40
   the working v must satisfy v_e ≥ (A_L²v)_e/R at e while v stays positive on
   the s = 3 leaf edges — check any candidate on T40/T52 first, they are now
   the sharpest known tests.
4. If a structured certificate family again fails, the fallback is a genuinely
   different proof route for Bound 44 (e.g. quadratic-form/trace arguments on
   A_L², or interlacing), since localized linear certificates have now been
   pushed to their limit.

## 6. File inventory

- `verify_counterexamples.py` — **the** self-contained exact verification
  (run: `python3 verify_counterexamples.py`).
- `exp12_Wstar.py`, `exp14_W2star.py` — abstract 1-/2-shell adversaries.
- `exp13_w1b_counterexample.py` — n = 35 W1B counterexample.
- `exp15_realize.py`, `exp16_independent_verify.py` — T52 construction +
  independent verification; `exp18_n40.py` — T40 + r-ball scan.
- `exp17_minimal.py` — minimal-realization search (→ T40).
- `exp20_random_H.py` — random-tree H search (finds nothing; the structure is
  too delicate for random sampling).
- `exp1–exp11` — the (failed) proof attempts that led to the adversary:
  baseline scans, η-contraction bounds, multiplier certificates and their
  symbolic cancellation (`exp9_symbolic.py`), and the float 2-shell relaxation
  (`exp11b_fast.py`) whose "false positives" turned out to be real.

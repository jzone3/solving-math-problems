# P16 childE — session notes (Bound 44)

**Bottom line: PROOF INCOMPLETE.** Major new machinery + corrections to childB.
Rigorous content is in `PROOF44.md`; this file is the experimental log.

## Headline results

1. **NEW Lemma E1 (shifted-sum weights)** — exact, Jensen-free:
   ρ(Q) ≤ max_e (M_e + c·s_e)/(s_e + c) for any c > −min s_e, where
   s_e = dᵢ+dⱼ, M_e = dᵢ(dᵢ+mᵢ)+dⱼ(dⱼ+mⱼ). A homotopy between the Das-type
   edge bound (c=0) and Anderson–Morley (c→∞). **This one-parameter family
   certifies Bound 44 for 273,183 of the 273,191 connected graphs n ≤ 9** and
   all but ≈200 of the 11.7M graphs at n = 10. Feasibility in c is an exact
   interval intersection (`exp15_exact.py`).
2. **sum ∪ affine-product covers ALL n ≤ 9** (the 8 sum-failures, all δ=1:
   GCOfBc, H?`@fBP, H?`@f@h, H?`@db`, H?`aeRS, HCOcbQp, HCOfBej, HCOefDf,
   are covered by φ(x)=x+b product weights). At n = 10 exactly **190 graphs**
   (`n10_fails.txt`) escape both; all 190 pass the **second-order** test
   λ² ≤ max (A_L²y)/y with the same affine weights, and all tested ones pass
   first-order with a general ψ (Lemma E3).
3. **Correction to childB finding 2**: product weights φ(dᵢ)φ(dⱼ) with the BEST
   concave φ FAIL at n = 9 (36 graphs, e.g. H?`reQF, slack −0.039, exp7). The
   right generalization is ψ(dᵢ,dⱼ) concave in each variable (Lemma E3), which
   numerically succeeds on every hard graph tried (n ≤ 10 hard sets + trees).
4. Route 2 (Perron-edge) is dead as stated: S_{e*} ≤ max arg44 fails on
   5,616/12,111 graphs n ≤ 8 (exp14).
5. Trees: sum ∪ prod covers all trees n ≤ 14 except 6 spider-like trees
   (first at n = 10, e.g. IhOK?E??G); these also defeat every additive
   f(x)+f(y) family but pass general-ψ and the second-order test.

## Experiment log (all scripts runnable from this dir; Python + numpy/scipy/sympy, nauty)

- `common.py` — graph6/degrees/m/line-graph utilities.
- `exp1–exp5` — certificate mining: power weights fail (453 @ord1 n≤8);
  affine φ(x)=x+b product covers n≤8 but 36 fail @n=9; ord4 power covers n≤8.
- `exp7` — SLSQP over ALL concave φ (product form): infeasible on n=9 hard set
  ⇒ product family dead (correction to childB).
- `exp8/exp9/exp11` — bivariate ψ families; general ψ (concave per variable,
  SLSQP) feasible with positive slack on every hard graph tested; optimal ψ
  near-rank-1 but not exactly; additive ψ=f(x)+f(y) often works ⇒ led to E1.
- `exp12/exp13` — grid scans of sum/product families: 0 failures n ≤ 9.
- `exp14` — Perron-edge route fails (Route 2 dead).
- `exp15_exact.py` — EXACT interval feasibility for sum (linear in c) and prod
  (quadratic in b; coefficients machine-verified). n ≤ 9: sum alone 273,183 /
  273,191, union 100%. n = 10 (16 shards): union covers all but 190.
- `exp16` — the 8 n≤9 sum-failures all have δ=1; c-window analysis.
- `exp17` — the 190 n=10 hard graphs: second-order affine test covers 190/190;
  bilinear ψ = xy + c(x+y) + e covers 0/190.
- `exp18` — additive family with general concave f: covers 191/204 hard graphs;
  the 13 exceptions (7 leaf-heavy + 6 trees) need general ψ or ord2.
  (NB early buggy run of exp18 compared against τ+2 instead of τ; fixed.)
- `verify_identities.py` — sympy + random-graph machine verification of every
  identity used in PROOF44.md (L1 algebra, L2 quadratic coefficients, exact
  line-graph neighbor-sum telescoping, CW validity vs true ρ(Q)).

## Pitfalls / caveats for successors

- CW normalization: certificates bound λ = ρ(Q) − 2; always compare CW value
  against τ = RHS44 − 2, NOT against RHS44 (two separate off-by-2 bugs caught).
- In `prod_feasible` the quadratic must use T = τ+2 in all three coefficients.
- Positivity for Lemma E1 is c > −min_e s_e (NOT c > −2δ); with the weaker
  (wrong) constraint 225 spurious failures appear at n ≤ 9.
- geng shards: `nauty-geng -cq n res/mod`; trees: `nauty-gentreeg | nauty-copyg -g`.
- The n=10 scan logs (`exp15_n10_*.log`) were produced with the conservative
  (pre-fix) code: they over-count failures; the 202 logged graphs were recheck
  ed with corrected code, leaving the definitive 190 (`n10_fails.txt`).

## Status vs dispatch routes

- Route 1 (learn φ shapes → closed-form rule): executed; discovery is that the
  right family is additive/shifted-sum, not product. Rule "f affine" covers all
  but a thin residue; no universal closed-form rule yet.
- Route 2 (global counting at max-degree-sum edge): the naive version is dead
  (exp14), but the counting identity Σdᵢmᵢ = Σ_e s_e is precisely what a proof
  of E1-feasibility needs; see PROOF44.md §5.
- Route 3 (structural restriction): subsumed — the resisting classes are now
  characterized exactly (leaf-heavy small graphs, 6 spider trees, 190 profile
  (δ,Δ) ∈ {(2,5),(2,6),(3,6),(3,7)} graphs).

**PROOF NOT COMPLETE. No counterexample. Sharpest known path: PROOF44.md §5.**

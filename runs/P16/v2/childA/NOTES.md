# P16 childA — symbolic perturbation analysis around the bipartite-regular equality manifold

Child session of runs/P16-v2. Task: exact (sympy, rational) perturbation analysis of
gap = RHS − mu for Bounds 44/46 on structured parametric families near the equality
manifold (bipartite regular graphs), expansion in eps = 1/d; report any family with
negative gap (counterexample) or leading-order positivity.

**Headline result: NO counterexample found. Every family analyzed has RHS − mu
(the max-edge gap) with POSITIVE leading coefficient in 1/d (or exactly positive in
closed form), for both bounds. However, individual edges with exactly negative gap
series exist (see F2c) — the obstruction to a counterexample is confirmed to be
global rescue by high-term edges, quantified here to third order.**

## Machinery (perturb.py)

For a quotient matrix B(d) (entries polynomial in d, bipartite pattern, row sums
d + O(1)), mu(L_B) = 2d + O(1) is the top branch; we expand it as an exact series in
eps = 1/d by Newton iteration on the characteristic polynomial over formal series
(exact rational/symbolic coefficients; convergence asserted via the Newton
correction vanishing to the requested order). Edge terms 2 + sqrt(arg) are expanded
exactly; gap per edge = term − mu; RHS − mu = max over edges (compared
lexicographically on exact coefficients). Symmetric integer quotient matrices are
realizable with equal large even cell sizes (DHS Lemma 2.3), and the specific
non-symmetric families used (F2, F4) have manifest positive integer cell sizes, so
any negative max-edge gap would have been a genuine counterexample.

Limitation found: the formal-Newton branch expansion only terminates when the O(1)
branch correction c0 is rational (true for all families below). For generic
multi-parameter 4/6-cell perturbations c0 is algebraic (root of the leading branch
polynomial) and the pure-series route stalls; those cases were covered instead by a
wide exact instance sweep (scan_exact.py, below).

## Families and exact results (families.log, families2.log)

### F1/F3 — (d, d+c)-biregular bipartite (includes K_{d,d+c}); 2-cell
Closed form, no series needed: mu = 2d + c and for the (unique) edge type,
  arg44 − (mu−2)^2 = c^2,  arg46 − (mu−2)^2 = c^2 (c + 2d + 4)/(c + 2d).
So gap > 0 for every c ≠ 0 and ALL d — **exact global positivity, both bounds**;
gap = 0 iff c = 0 (equality manifold). Perturbation order: gap ~ c^2/(2d) for both.

### F2 — K_{d,d} minus a matching of size t; 4-cell (ML(t), UL(d−t), MR, UR)
mu = 2d − 2t/d + 4t/d^2 − (4t^2+8t)/d^3 + O(d^-4). Max edge is always the
unmatched–unmatched edge (UL,UR), with exact gap series (t symbolic):
  Bound 44: gap = t·eps − 5t·eps^2 + t(17t+28)/4·eps^3 + O(eps^4)
  Bound 46: gap = 2t·eps − 6t·eps^2 + 2t(2t+3)·eps^3 + O(eps^4)
Positive leading order for every t ≥ 1 — **no violation**; fixed t = 1,2,3,5 checked
with fully rational coefficients (t=1 reproduces the known K_{d,d}−e Θ(1/d) gap:
gap44 = eps − 5eps^2 + ..., gap46 = 2eps − 6eps^2 + ...).

### F2c — K_{d,d} minus a near-perfect matching (u unmatched pairs, t = d−u)
mu = 2d − 2 + 2u/d + 4u/d^2 + O(d^-3). Notable: the matched–matched edge has gap
  Bound 44: −u·eps − 2u·eps^2 + O(eps^3);  Bound 46: −2u·eps − 2u·eps^2 + O(eps^3)
i.e. **a genuinely NEGATIVE edge-gap series** (that edge's term lies strictly below
mu, to leading order — not float noise). But the max edge (unmatched–unmatched:
degrees d, m ≈ d−1) has gap +1 (44: 1/2 for mixed, 1 for UU; 46: 2) at O(1) —
positive at order eps^0 — so RHS − mu > 0. **No violation**; this isolates exactly
which local data would beat the bounds (d_i = d_j = d−1 with m_i, m_j > d−1) and
shows the rescue comes from edges at vertices of full degree d whose m is BELOW
their degree. A counterexample must avoid any such "degree-max, m-depressed" edge
globally, which conflicts with sum rules (Σ d_i m_i = Σ_{ij∈E}(d_i+d_j)).

### F4 — 3-cell bipartite: left cells with degrees d+p, d+q, right cell degree d
B = [[0,0,d+p],[0,0,d+q],[d−h,h,0]], p,q,h symbolic. mu = 2d + p − h(p−q)/d + O(d^-2)
(branch through the larger left degree; scan restricted p ≥ q wlog by symmetry).
Exact coefficient polynomials in (p,q,h) computed to eps^2 (families2.log). Exact
integer scan p,q ∈ [−4,4], h ∈ [1,8]: max-edge gap has **nonnegative leading
coefficient in every case** (positive unless p=q=0); no violation.

### Wide exact instance sweep — general 4-cell and 6-cell perturbations (scan_exact.py)
Because the symbolic route needs rational branch constants, generic perturbations
were swept as exact integer instances at d ∈ {50, 200, 1000}:
- 4-cell symmetric: blocks [[d−w+p11, w+p12],[w+p21, d−w+p22]], w ∈ 1..6,
  p ∈ {−3..3}^4 (75,558 bound-evaluations);
- 6-cell symmetric (3+3): base rows (d−u−v, u, v | u, d−u−v, v | v, v, d−2v),
  u,v ∈ 1..4, all single-entry perturbations ±1, ±2 plus 30,000 random integer
  perturbation matrices in {−2..2}^{3×3} (143,646 bound-evaluations).
Screen: float gap < −1e−9 ⇒ exact rational Sturm confirmation (charpoly root
bisection with rational endpoints; edge comparison via (lam−2)^2 vs rational arg —
no floats on the accept path). Result: **zero candidates**; minimum observed gap
−6.8e−13 (float noise, attained only at exactly-regular = equality configurations,
e.g. w=2, p=(−1,3,3,−1), which is (d+2)-regular bipartite).

## Interpretation / suggestions

1. First- and second-order positivity around the equality manifold holds in every
   structured direction tested; the leading gap coefficient is a square (c^2-type)
   or degree-difference-driven positive term. The bounds look locally TRUE near
   bipartite regular to the orders computed.
2. The F2c negative-edge phenomenon gives a precise target for any future search:
   all edges must have both endpoints at degree < Δ(G) with elevated m — impossible
   at a maximum-degree-sum edge (m_i ≤ d_j there), matching the §3.1 obstruction in
   ../NOTES.md. A global counting argument bounding the term deficit at the
   max-degree-sum edge by the surplus forced elsewhere looks like the most promising
   PROOF route (Bound 46 already has the conditional criterion in ../NOTES.md §3).
3. If more search is wanted: perturbations at scale d^{1/2} (fractional-power
   ansatz) and non-bipartite quotients with odd structure were NOT covered here.

## Files
- perturb.py — series machinery (Newton-on-charpoly over exact series).
- families.py / families.log — F1, F2, F2b, F2c, F3.
- families2.py / families2.log — F4 3-cell symbolic + exact integer scan.
- enum4.py, enum6.py — fully-symbolic 4/6-cell attempts (stall on algebraic branch
  constants; kept for reference).
- scan_exact.py / scan_exact.log — wide exact instance sweep + Sturm confirmer.

**Conclusion: no verified counterexample; leading-order positivity of RHS − mu
established (exactly) for every family analyzed, both Bound 44 and Bound 46.**

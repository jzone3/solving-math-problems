# P16 childB — proof attempt for BHS Bounds 44 & 46 (edge Collatz–Wielandt via the line graph)

Child session of runs/P16-v2. Task: attempt a complete proof of

- **Bound 44**: μ(G) ≤ max_{ij∈E} [ 2 + √( 2((dᵢ−1)² + (dⱼ−1)² + mᵢmⱼ − dᵢdⱼ) ) ]
- **Bound 46**: μ(G) ≤ max_{ij∈E} [ 2 + √( 2(dᵢ² + dⱼ²) − 16dᵢdⱼ/(mᵢ+mⱼ) + 4 ) ]

(statements per DHS arXiv:2606.14550 Table 2, as fixed in runs/P16/v2/NOTES.md §1).

**OUTCOME: no complete proof and no counterexample. Substantial new PARTIAL RESULTS**,
centered on a new *edge-type Collatz–Wielandt lemma* on the line graph, which (i) yields a
new one-parameter family of valid edge bounds interpolating from Anderson–Morley, (ii) gives
new checkable sufficient conditions for 44/46, (iii) empirically *certifies both bounds on every
connected graph with n ≤ 8 via an adapted concave weight*, and (iv) reduces Bound 46 on
minimum-degree-≥2 graphs (verified n ≤ 9) to choosing a single exponent per graph.

All numerical claims below were verified exhaustively (nauty-geng, float64, tol 1e-9);
scripts in this directory. Notation: s = dᵢ+dⱼ, p = dᵢdⱼ, Q = D+A (signless Laplacian),
λ = λ_max(A(L(G))) the adjacency spectral radius of the line graph, arg44/arg46 = the
square-root arguments above, t44/t46 = the edge terms, RHS = max over edges.

## 1. Rigorous new results (proofs complete, numerically cross-checked)

### Lemma B1 (line-graph identity)
For any graph G with at least one edge, ρ(Q) = 2 + λ_max(A(L(G))).
*Proof.* Q = RRᵀ with R the unoriented incidence matrix, and RᵀR = 2I + A(L(G)).
RRᵀ and RᵀR have the same nonzero eigenvalues, and both top eigenvalues are ≥ 2 > 0. ∎

### Lemma B2 (edge Collatz–Wielandt)
Let G have no isolated vertices and let φ: (0,∞) → (0,∞) be concave. Then

  μ(G) ≤ ρ(Q) ≤ max_{ij∈E} [ dᵢφ(mᵢ)/φ(dⱼ) + dⱼφ(mⱼ)/φ(dᵢ) ].

*Proof.* Apply Collatz–Wielandt (DHS Lemma 2.5) to A(L(G)) with the positive test vector
y_{ij} = φ(dᵢ)φ(dⱼ). For an edge e = ij,
(A_{L(G)} y)_e = φ(dᵢ)(Σ_{k∼i} φ(d_k) − φ(dⱼ)) + φ(dⱼ)(Σ_{k∼j} φ(d_k) − φ(dᵢ)).
By Jensen (φ concave), Σ_{k∼i} φ(d_k) ≤ dᵢφ(mᵢ). Hence
(A y)_e / y_e ≤ dᵢφ(mᵢ)/φ(dⱼ) + dⱼφ(mⱼ)/φ(dᵢ) − 2. Conclude with Lemma B1 and μ ≤ ρ(Q). ∎

This is the exact edge-type analog of DHS Lemma 3.6 (which is vertex-type); to our knowledge
it is new, and it is the natural tool for the two remaining edge-type bounds.

### Corollary B3 (new valid bound family, sharp on bipartite regular)
For every a ∈ [0,1]:  μ(G) ≤ max_{ij∈E} [ dᵢmᵢᵃ/dⱼᵃ + dⱼmⱼᵃ/dᵢᵃ ]  =: 2 + F_a(G).
At a = 0 this is Anderson–Morley (max dᵢ+dⱼ); a = 1 needs no concavity (Jensen is exact).
For every a, equality holds on bipartite regular graphs (value 2d) — i.e. the family is tight
exactly on the equality manifold of Bounds 44/46. (Sanity-verified: F_a + 2 ≥ λ+2 = ρ(Q) for
a ∈ {0,…,1}, all connected n ≤ 8.)

### Lemma B4 (second-order Perron localization on the line graph)
Let z be the Perron vector of A(L(G)) and e* = ij an edge maximizing z. Then
λ² ≤ S_{e*}, where S_e := Σ_{f∼e in L(G)} (line-degree of f)
     = (dᵢ−1)(dᵢ−2) + (dⱼ−1)(dⱼ−2) + dᵢmᵢ + dⱼmⱼ − dᵢ − dⱼ.
*Proof.* λ²z_{e*} = (A²z)_{e*} ≤ z_{e*}·(A²·1)_{e*} = z_{e*}S_{e*} since all z_f ≤ z_{e*}. ∎

Key identities (exact algebra, machine-checked):
- arg44(e) − S_e = (dᵢ−dⱼ)² + 2mᵢmⱼ − dᵢmᵢ − dⱼmⱼ
- arg46(e) − S_e = dᵢ² + dⱼ² + 4s − 16p/(mᵢ+mⱼ) − dᵢmᵢ − dⱼmⱼ
(both vanish identically on regular data dᵢ=dⱼ=mᵢ=mⱼ, matching the equality manifold).

### Proposition B5 (checkable sufficient conditions)
If every edge of G satisfies
  C44: (dᵢ−dⱼ)² + 2mᵢmⱼ ≥ dᵢmᵢ + dⱼmⱼ
then Bound 44 holds for G; if every edge satisfies
  C46: dᵢ² + dⱼ² + 4(dᵢ+dⱼ) ≥ 16dᵢdⱼ/(mᵢ+mⱼ) + dᵢmᵢ + dⱼmⱼ
then Bound 46 holds for G.
*Proof.* Apply Lemma B4 at the Perron edge e*: λ² ≤ S_{e*} ≤ arg(e*) ≤ max arg; then
ρ(Q) = 2+λ ≤ 2+√(max arg). ∎
(In fact the condition is only needed at the Perron edge e*.) Note mᵢ ≥ dⱼ and mⱼ ≥ dᵢ imply
C44. Coverage on connected n ≤ 8 (12,112 graphs): C44 all-edges 314, C46 all-edges 1,432;
at the actual Perron edge: 613 / 6,882 graphs.

### Proposition B6 (both bounds hold for semiregular bipartite graphs)
If G is (r,s)-semiregular bipartite, every edge has (dᵢ,dⱼ,mᵢ,mⱼ) = (r,s,s,r); then
- arg44 = 2((r−1)²+(s−1)²) ≥ (r+s−2)², so RHS44 ≥ r+s ≥ μ (Anderson–Morley);
- arg46 − (s−2)² = (r−s)² + 4((r+s)² − 4rs)/(r+s) = (r−s)²(1 + 4/(r+s)) ≥ 0, so RHS46 ≥ r+s ≥ μ.
(Regular graphs are trivial: both RHS equal 2d ≥ μ.)
The general identity arg46 − (s−2)² = (dᵢ−dⱼ)² + 4(s(mᵢ+mⱼ) − 4p)/(mᵢ+mⱼ) recovers the
parent run's conditional criterion (NOTES.md §3 item 1).

## 2. New empirical findings (exhaustive, scripts + logs here)

1. **ρ(Q)-strengthening holds**: ρ(Q) ≤ RHS44 and ≤ RHS46 for ALL connected graphs
   2 ≤ n ≤ 9 (12,112 for n ≤ 8 plus 261,080 for n = 9; `n9_check.py rho`, logs n9_rho_*).
   Minimum gap 0 (equality, e.g. HFzf~z{, H~~~~~~ = K9 has gap 0 too at float noise), never
   negative. So the Q-based machinery is *not* doomed: no small graph separates μ from ρ(Q)
   relative to these bounds.
2. **Per-graph adapted concave φ always certifies both bounds (n ≤ 8)**: for every connected
   graph n ≤ 8 there exists a concave φ (optimized over values at the graph's {d,m}-points with
   concavity as linear constraints, SLSQP, `opt_phi.py`) such that the Lemma-B2 bound is
   ≤ RHS44 and ≤ RHS46. Zero failures / 12,112. Hence a proof of either bound "only" requires a
   *rule* G ↦ φ_G plus a max-vs-max comparison — the edge-CW family is rich enough.
3. **Power family suffices for Bound 46 when δ(G) ≥ 2**: some a ∈ {0, 0.05, …, 1} gives
   2 + F_a ≤ RHS46 for every connected graph with min degree ≥ 2, n ≤ 9 (197,772 graphs at
   n = 9; zero failures; `n9_check.py pow46`). With leaves allowed, the only n ≤ 8 exceptions
   are FCOf? and G?bnS{ (deficits 0.011, 0.009), both fixed by a general concave φ.
   For Bound 44 the power family fails on 270 δ≥2 graphs (n ≤ 8) — 44 genuinely needs richer φ.
4. **No universal exponent**: bipartite-semiregular-like graphs (EEz_, FCZb_, …) force
   a ≈ 0.6 while dense graphs force a ≤ 0.425; the working-a intervals have empty common
   intersection. Moreover NO universal φ can work *pointwise* (per-edge-data): the P4
   middle-edge data (d=2, m=1.5) has t46 = −∞ and t44 ≈ 2.71 < any CW value there; P4 is saved
   only by its leaf edges. Any proof must exploit the max-vs-max slack / global structure.
5. **Dominance failures** (why the problem is hard): max t44/t46 does NOT dominate any of:
   Anderson–Morley, Merris, Guo–Das edge quadratic (dᵢ+dⱼ+√((dᵢ−dⱼ)²+4mᵢmⱼ))/2, Li–Zhang,
   √(2d(d+m)) (Lemma 2.9), Bound 42, nor their pointwise minimum (min gap −0.149 @ EEj_ for 46,
   −0.310 @ FCZbg for 44; `dominance.py`, `dominance_min.py`); nor the line-graph second-order
   bound max_e S_e, nor max √(D_e D_f) (`linegraph.py`). So on some graphs Bounds 44/46 are
   strictly sharper than every classical bound tried — they cannot be proved by dominance over
   any of them.
6. **Perron-critical-edge argument fails on actual graphs**: with i the Perron vertex of
   B = P⁻¹QP and j its best neighbor (DHS Prop 3.5 setup), min over n ≤ 8 of t44(i,j) − ρ is
   −0.707 (P4); even taking the best edge incident to the Perron vertex fails (−0.204 @ DQo).
   (`perron_edge.py`)

## 3. Assessment and suggested next steps

Both bounds look TRUE (now verified beyond μ up to the stronger ρ(Q) statement, n ≤ 9).
The most promising proof program uncovered here:

(a) **Bound 46, δ ≥ 2 case**: find an explicit rule a(G) (empirically a ∈ [0.6] for
    bipartite-semiregular-like graphs, smaller for dense graphs; perhaps a = a(Δ/δ) or a
    two-piece φ as in DHS's proof of Bound 43) and prove max_e CW_a(e) ≤ max_e t46(e) by a
    case analysis on the CW-maximizing edge. The pointwise obstruction disappears for δ ≥ 2
    on many data regions; the identity arg46 − S_e above pinpoints exactly the deficient
    region dᵢmᵢ + dⱼmⱼ + 16p/(mᵢ+mⱼ) − dᵢ² − dⱼ² − 4s ∈ (0, ·).
(b) **Leaves**: handle pendant vertices by a separate direct argument (leaf edges have large
    terms: t44(leaf) = 2+√(2((dᵢ−1)² + dᵢ(mᵢ−1))); the two power-family exceptions found are
    tiny-deficit and leaf-driven).
(c) **Bound 44**: needs the full concave-φ freedom. Since per-graph feasibility holds
    (finding 2), formulate the choice of φ as the solution of the finite concave-feasibility
    program and look for a closed-form (e.g. piecewise-linear with one breakpoint at m̄ or Δ/2).
(d) Extend the exhaustive ρ(Q) check to n = 10 and the δ≥2/pow46 check to n = 10 for more
    confidence before investing in the case analysis.

## 4. Files

- `harness.py` — g6 parsing, edge terms, base scan (min gaps vs μ and Merris)
- `perron_edge.py` — Perron-critical-edge tests (finding 6)
- `dominance.py`, `dominance_min.py` — dominance failures (finding 5)
- `linegraph.py` — line-graph identities/sanity, S_e, D_eD_f (Lemmas B1/B4 checks)
- `cw_edge.py` — power-family CW bounds F_a, sanity F_a ≥ λ (Corollary B3 check)
- `opt_phi.py` — per-graph optimal concave φ feasibility (finding 2)
- `twocase46.py` — max-degree-sum-edge case analysis coverage (small)
- `n9_check.py`, `n9_rho_*.log`, `n9_pow_*.log` — n = 9 exhaustive verification (findings 1, 3)

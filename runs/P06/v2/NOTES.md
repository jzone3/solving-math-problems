# P06 V2 — annealed / structured search on Graffiti 129 (dev(Laplacian) ≤ Randić)

Session: https://app.devin.ai/sessions/925ab3b6622842418603b730a198be53
Variant: V2 (annealed edge-flip search from star seeds; extended with structured
constructions once a key identity was found).

## 0. Statement re-verification (against source code)

Cloned github.com/RoucairolMilo/refutationGBR and read
`src/models/conjectures/GenerateGraph.rs` (CONJECTURE == 129) and
`invariants.rs`:

- **dev** = *population* standard deviation (divide by n, then sqrt) of the
  eigenvalues of L = D − A.
- **R** = Σ_{uv∈E} 1/√(d_u d_v) (standard Randić index); edges only, so
  isolated vertices contribute 0 to R but do count in n for dev.
- Conjecture 129: dev(G) ≤ R(G) for every simple graph (refutation trigger in
  the Rust code is `dev - R > 0.0001`). No connectivity restriction in the code.
- Conjecture 698 as coded in refutationGBR is **trivially true / buggy**: it
  computes the ℓ2-norm of the *negative* Laplacian eigenvalues, which is always
  0 since L ⪰ 0. So the only meaningful target here is 129. (Definitional
  ambiguity of 698 noted for V5.)

Literature check (July 2026): no dedicated paper on WoW 129/698; still listed
as open in Roucairol–Cazenave 2025 Table 1. Proceeded.

## 1. KEY IDENTITY — dev depends only on the degree sequence

trace(L²) = Σ_i d_i² + 2m, hence

    dev(G)² = (Σd² + 2m)/n − (2m/n)²  .

Machine-verified on 200 random graphs (`explore2.py`, prints PASS).
Consequences:

- Scoring f(G) = dev − R needs **no eigensolve**; edge flips update f exactly in
  O(d_u + d_v). This let the anneal run at n up to ~500 cheaply.
- Conjecture 129 is equivalent to a purely degree/edge-local statement:
  √((Σd²+2m)/n − 4m²/n²) ≤ Σ_e (d_u d_v)^{−1/2}.

## 2. EXACT EQUALITY FAMILY (new, as far as we know)

For every q ≥ 3, the graph **G_q = K_q ∪ (q−2)K_1** (clique plus q−2 isolated
vertices, n = 2q−2) satisfies dev = R = q/2 **exactly**:
R(K_q) = q/2 and dev² = q²(q−1)(k+1)/n² with k = q−2 gives 4(q−1)² = (2q−2)². ✓
(Numerically confirmed for q up to 100, `explore3.py`; exhaustively these are the
*only* nonempty equality graphs for n ≤ 10, see §4.)

So the conjectured inequality is **tight on an infinite family** — any proof
must be sharp, and any counterexample search should orbit this manifold.
The stars (the near-miss family from the problem file) are only
*asymptotically* tight: f(K_{1,n−1}) = √(n−1) − √(dev²) → 0⁻ like −Θ(1/√n)
(`explore.py`: f = −0.0141 at n = 5000).

## 3. Small theorems proved along the way (paper-ready remarks)

- **Unconditional envelope**: maximizing dev² over n (real) gives
  dev ≤ (Σd²+2m)/(4m) for every graph. Hence a *sufficient* condition for 129 on
  a graph is 4mR ≥ Σd² + 2m, i.e. Σ_e [4m/√(d_ud_v) − d_u − d_v − 2] ≥ 0.
- **129 holds for all regular graphs**: d-regular ⇒ R = n/2 and the envelope is
  (d+1)/2 ≤ n/2, equality iff G = K_n (and then only at the padded size
  n = 2q−2). One-paragraph proof.
- **Unions of cliques never violate**: for G = ∪K_{a_i} + kK_1, positivity would
  require Σa_i²(a_i−1) > (Σa_i)(Σa_i(a_i−1)), impossible (termwise); equality iff
  a single clique, and then only at k = q−2. So the equality family is the unique
  optimum among clique unions.
- Stars violate the *envelope* condition for n ≥ 10 (4mR < Σd²+2m) yet satisfy
  129 because their n is far above the maximizing n* = 8m²/(Σd²+2m) ≈ 8; any
  counterexample must live where n is near n* AND the envelope condition fails.

## 4. Exhaustive verification n ≤ 10 (re-derivation of the 1995 frontier)

`exhaust.py` + nauty-geng: **all** graphs n = 4..10 (12,005,168 graphs at
n = 10; 8-way parallel). Max f = 0 at every order; the only graphs with f = 0
are the empty graphs and G_q = K_q ∪ (q−2)K_1 (q = 3..6, i.e. graph6 CT, ECeW,
G?aK[[, I?ACKMF`w). No positives; matches Brewster–Dinneen–Faber.

## 5. Local exhaustive perturbation of the equality family (symmetry-reduced)

Aut(G_q) = S_q × S_{q−2} ⇒ any ≤t edge flips are WLOG inside a window of 2t
clique + 2t isolated vertices. `local_flips.py`:

- **t = 2 (all 1- and 2-flip perturbations), q = 4..200: all strictly negative.**
  Best is a single clique-edge deletion with deficit ≈ −1/q (e.g. −0.00497 at
  q = 200). Deficit shrinks like Θ(1/q) but never crosses 0.
- t = 3 at q ∈ {6,10,20,50,120}: all strictly negative (same optimum).
  [results in local3.log]

So G_q is a strict local maximum of f at every size tested; no crossing
direction of ≤3 flips exists at any scale.

## 6. Annealed edge-flip search (the V2 mandate)

`search.py`: simulated annealing, moves = single edge flips, score = f computed
incrementally (exact formula, no eigensolve), periodic drift re-sync, seeds =
star K_{1,n−1} and clique+iso G_{(n+2)/2}, geometric cooling 0.05 → 1e−6.

- Run 1: n ∈ {14,18,22,26,30,38,46,62,78,98,150,198,302,498}, 2M iters × 4
  restarts × 2 seeds each. Result: best found at each even n=2q−2 is exactly
  G_q with f = 0 (float 0 up to 1e−12); at other n, strictly negative optima.
  No f > 0 ever observed. [anneal_run1.log]

## 7. Wide parameterized family scans

`family_scan.py` (clique±apex/matching/pendants/subdivision/split + isolated
padding, thousands of parameter combos): max f = 0, attained only at
degenerate reductions to K_q + (q−2)K_1; all genuine deformations negative.
`family_scan_wide.py`: complete split graphs K_q ∨ sK_1 + kK_1 with q ≤ 200,
s ≤ 4000, optimal padding k ≈ n*−(q+s); star-with-clique-center q ≤ 120,
s ≤ 800. [family_wide.log]

## STATUS: negative (no counterexample; conjecture tight on K_q ∪ (q−2)K_1)

Summary: re-verified the exact WoW-129 definition from refutationGBR source;
discovered dev² is a pure degree-sequence invariant (trace(L²) identity),
found the exact equality family K_q ∪ (q−2)K_1 (dev = R = q/2 for all q), proved
129 for regular graphs and clique unions, re-exhausted n ≤ 10 (equality graphs
are exactly this family), exhausted all ≤3-flip perturbations of the family up
to symmetry (all strictly negative, deficit Θ(1/q)), and ran long incremental
annealing at n up to 498 from star and clique seeds — global optimum always
f = 0 on the equality family, never positive. Strong evidence 129 is TRUE and
sharp; recommended follow-up: prove 129 via the degree-sequence reformulation
(§1) with the envelope + slack analysis of §3.

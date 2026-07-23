# P16 childC — extended counterexample search for BHS Bounds 44 & 46

Child session C of runs/P16-v2. Task: push the search into regimes not covered by
the parent run (exhaustive n ≤ 10, trees n ≤ 17, quotient annealing k ≤ 5 entries
≤ 500, continuous relaxation k ≤ 3). Statements as in ../NOTES.md §1 (verified
against arXiv:2606.14550v1 Table 2):

- Bound 44: μ(G) ≤ max_{ij∈E} [2 + √(2((dᵢ−1)² + (dⱼ−1)² + mᵢmⱼ − dᵢdⱼ))]
- Bound 46: μ(G) ≤ max_{ij∈E} [2 + √(2(dᵢ² + dⱼ²) − 16dᵢdⱼ/(mᵢ+mⱼ) + 4)]

## RESULT: no counterexample found. Both bounds survive all new regimes.

## 1. CP-SAT quotient search with eigenvector certificate, k = 4..10 (cpsat_quotient.py)

New encoding. Restrict to quotient matrices B whose support is a TREE on k cells
(zero diagonal): realizability (DHS Lemma 2.3) is then automatic and the quotient
graph is bipartite, so L_B = diag(s) − B is sign-similar to the nonnegative matrix
Q_B = diag(s) + B and Collatz–Wielandt gives lam_max(L_B) = lam_max(Q_B) ≥
min_i (Q_B x)_i / x_i for any positive integer vector x. The violation condition
is cleared of denominators into integer polynomial constraints
(P_i = s_i·m_i = Σ_j B_ij s_j):

- 44: (T−2W)²·sᵢsⱼ > 2W²·(((sᵢ−1)²+(sⱼ−1)²−sᵢsⱼ)·sᵢsⱼ + PᵢPⱼ) for every support edge
- 46: (T−2W)²·(Pᵢsⱼ+Pⱼsᵢ) > W²·((2(sᵢ²+sⱼ²)+4)(Pᵢsⱼ+Pⱼsᵢ) − 16(sᵢsⱼ)²)

together with W·(Q_B x)ᵢ ≥ T·xᵢ and T > 2W (W = 32). A FEASIBLE solution is a
counterexample certificate (then re-checked by ../verify_p16.py). Encoding
validated against the float formulas on 20k random tuples and the CW/bipartite
similarity on 2k random tree quotients (test_encoding.py).

Runs (cpsat44.log, cpsat46.log): all nonisomorphic tree supports for each
k = 4..10, entry bound E = max(600/k, 30) (products kept < 2^62), x ≤ 2000,
T ≤ (2s_max+4)·W, 500 s per k per bound, 8 workers. Every instance returned
UNKNOWN or INFEASIBLE within budget — **0 candidates** for either bound.
(UNKNOWN = no violating quotient found within budget, not a proof.)

## 2. Exhaustive n = 11 sweeps (geng_screen.py, n11_*.log)

Fast float screener (skip eigensolve when both RHS ≥ Anderson–Morley max(dᵢ+dⱼ);
candidate threshold gap < 1e-6, none triggered). Reproduces parent's n ≤ 10
minimum gap (0.0221 for bound 44 at n = 8).

| family (connected, n = 11)        | graphs      | min gap44 | min gap46 |
|-----------------------------------|-------------|-----------|-----------|
| all bipartite (geng -b)           | 25,598      | 0.0461    | 0.1239    |
| degrees in [1,5] (geng -d1 -D5)   | 21,503,340  | 0.0461    | 0.1229    |
| degrees in [2,5] (geng -d2 -D5)   | 14,661,872  | 0.0461    | 0.1229    |
| degrees in [3,6] (geng -d3 -D6)   | 64,434,315  | 0.1125    | 0.2710    |

≈ 86.4M new graphs (union ≈ 78M distinct), **no violation**; tightest n = 11
graphs are the expected near-bipartite-biregular ones (e.g. J?`CPbGL@g?).
Not covered at n = 11: max degree ≥ 7 with min degree ≤ 2 (145M+ graphs for
d1–d6 alone); these are far from the equality manifold (leaf edges inflate the
max), so low priority.

## 3. Non-equitable overlays of bipartite near-regular graphs (overlay_search.py)

- Circulant overlays: Z_n (n even ≤ 120), layer 1 = odd offsets (bipartite
  regular), layer 2 = arbitrary offsets (breaks bipartiteness/equitability at
  vertex-transitive regularity): min gap −3.2e-14 = equality (all-odd unions,
  bipartite regular), otherwise positive. No violation.
- Random overlays: union of a random dX-biregular bipartite graph and a second
  one on a rotated bipartition, n ≤ 120, plus one-edge-deleted variants (4,000
  draws): min gap 0 (equality only), no violation.

## 4. Continuous quotient relaxation k = 4..8 (continuous_quotient.py)

Extends parent's k ≤ 3 analysis. B = diag(n)^{-1}S, S symmetric ≥ 0 on a support
pattern (all nonisomorphic trees on k nodes, all tree+even-cycle unicyclic
patterns, complete bipartite patterns; 5/9/27/67/155 supports for k = 4..8),
penalty-enforced B_ij ≥ 1 on support, Nelder-Mead multistart (30 restarts per
support per bound). Integer quotients are a subset, so a nonnegative infimum
covers all entry sizes for these supports.

Result: minima ≈ 0 for every k and both bounds; 18 reported "negative" points
(down to float gap −47.7) all occurred at entry scales e^20–e^38 (λ ~ 1e9–5e16)
and were **all rechecked at 60-digit precision (recheck_negatives.py): every one
is nonnegative — float64 cancellation noise**, consistent with the parent run's
k=3 warning. Genuine minima are the bipartite-regular equality configurations.

## 5. Conclusion

**Negative result (no counterexample; verified counterexample: NOT FOUND).**
New coverage beyond the parent run: (i) certificate-driven CP-SAT search over
all tree-support quotients k = 4..10 with entries up to 150 (0 candidates);
(ii) ~86M connected n = 11 graphs in near-regular / bipartite degree regimes
(min gap 0.046); (iii) overlay constructions escaping small equitable
partitions (equality only); (iv) continuous quotient infimum ≈ 0 for k ≤ 8 over
tree/unicyclic/complete-bipartite supports — numerically no quotient
certificate with ≤ 8 cells on those supports can refute either bound, for ANY
entry size. Everything continues to point to both bounds being true, with the
bipartite-regular manifold as the unique tight locus.

Files: cpsat_quotient.py, geng_screen.py, overlay_search.py,
continuous_quotient.py, recheck_negatives.py, test_encoding.py, run_queue.sh;
logs: cpsat44.log, cpsat46.log, n11_*.log, overlay.log, cont44.log, cont46.log,
queue.log.

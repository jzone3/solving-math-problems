# P07 — Graffiti 154: 2m·μ(D)² ≤ n³

**Statement.** For every connected graph G with n vertices, m edges, and average inter-vertex
distance μ(D): the standard deviation of the adjacency eigenvalues (= √(2m/n)) is at most
n/μ(D). Equivalently: **2m·μ(D)² ≤ n³**. (WoW conj. 154; open in Roucairol–Cazenave 2025
Table 1, searched only to n = 50. Sibling conj. 143: Var(positive adjacency eigenvalues) ≤ m/μ(D),
searched to n = 100 — attack both.)

**Why it matters.** The reformulation 2m·μ(D)² ≤ n³ is a crisp extremal statement that appears
nowhere in the literature — the community has never seen it in this form.

**Status.** Exhaustive n ≤ 10 (1995); MCTS n ≤ 50/100 (2025). The natural extremal family
(dumbbells: two cliques joined by a path) is fully parameterized and was inexpressible in the
edge-by-edge MCTS at n > 50 — the unexplored regime is exactly where a counterexample would live.

**Witness & verifier.** One connected graph; verify with BFS all-pairs distances + edge count
(no eigensolve needed in the reformulated form).

**Prompt variants:**
1. **V1 dumbbell optimization**: closed-form 2m·μ² for dumbbell(a, ℓ, b) (cliques sizes a,b, path
   length ℓ) and lollipops/kites; optimize the 3-parameter family exactly over all n; verify any
   violation with exact rational arithmetic.
2. **V2 broad structured families**: theta graphs, cliques with multiple pendant paths, joins of
   cliques and paths; symbolic optimization (sympy) of 2mμ²/n³ over each family.
3. **V3 annealed search at n = 100–2000**: sparse graph representation, incremental BFS scoring,
   score = 2mμ²/n³; seeds from V1 near-optima.
4. **V4 proof attempt**: try to prove 2m·μ(D)² ≤ n³ (it may be an easy unnoticed theorem —
   settle it either way); relate μ(D) bounds (Erdős-type average distance vs m) and check
   tightness constants; if a proof gap appears, extract the extremal structure and search it.
5. **V5 conj-143 twin**: same machinery for Var(positive adjacency eigenvalues) ≤ m/μ(D)
   (needs eigensolve); structured families with few large positive eigenvalues and large diameter.

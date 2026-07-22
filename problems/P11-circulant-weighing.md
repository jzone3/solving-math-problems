# P11 — Circulant Weighing Matrices: open cells CW(96,36), CW(105,36), CW(112,36), CW(117,36), CW(120,49), CW(132,81)

**Statement.** Does an n×n circulant {0,±1} matrix W with W·Wᵀ = kI exist for the open (n,k)
cells? Equivalently: a ternary first-row vector of length n with all nontrivial periodic
autocorrelations zero and weight k. (La Jolla CWM Repository, https://ljcr.dmgordon.org/cwm/;
data github.com/dmgordo/circulant-weighing-matrices; Arasu–Gordon–Zhang 2021 settled 12 of Tan's
34 open cases ≤ (200,100) — 22 remain.)

**Why it matters.** CWMs = perfect ternary sequences with two-level autocorrelation (radar,
spread spectrum); an actively maintained repository tracks every cell.

**Status.** Nonexistence results come from multiplier/field-descent theory; existence side has
never (visibly) seen modern SAT/ILP. Witness is a single vector — the smallest witness of any
problem in this catalog.

**Witness & verifier.** First row (ternary vector); verify all n−1 autocorrelations = 0 and
weight = k. Milliseconds.

**Prompt variants:**
1. **V1 SAT direct**: encode entries as 2-bit variables, autocorrelation-zero as pseudo-Boolean
   constraints, weight cardinality constraint; symmetry-break by cyclic shift + multiplier group;
   attack CW(96,36) and CW(105,36) first.
2. **V2 multiplier-orbit exhaustion**: assume the solution is fixed by a multiplier subgroup of
   Z_n^* — variables become orbit choices (often < 30 orbits); exhaust all subgroups and orbit
   assignments; may fully RESOLVE several cells (either way).
3. **V3 algebraic construction**: known CWM families (Galois-ring, q-ary sequence, composition
   theorems CW(n1,k1)⊗CW(n2,k2)); systematically test all composition routes into the open
   cells and near-cell parameters; LLM-guided identity search.
4. **V4 annealing + DFT pruning**: local search on ternary vectors, energy = Σ|autocorrelation|²
   (Fourier-side: power spectrum flatness); polish near-solutions with SAT.
5. **V5 character-theory nonexistence**: attempt to KILL cells with field descent /
   self-conjugacy / multiplier theorems (Arasu et al. toolbox, arXiv:1908.08447) — mechanize the
   standard nonexistence tests over all 22 open cells; any newly killed cell is publishable.

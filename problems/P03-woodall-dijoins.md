# P03 — Woodall's Conjecture (packing dijoins)

**Statement.** In every finite digraph, the minimum size of a nonempty dicut equals the maximum
number of pairwise disjoint dijoins. (Woodall 1978, LNM 642, 620–635.)

**Why it matters.** Central open min-max in combinatorial optimization (dual of Lucchesi–Younger).
The weighted version (Edmonds–Giles) is FALSE (Schrijver 1980) with a tiny counterexample —
exactly the DGG shape: an LP-flavored min-max that might fail on a small concrete instance.
Cornuéjols has offered money for the τ = 3 case.

**Status.** Open even for τ = 3 in general digraphs. True for source-sink connected digraphs
(Schrijver) and planar digraphs. Known weighted counterexamples ≤ 10 arcs. No published
large-scale ILP search for unweighted counterexamples.

**Witness & verifier.** A digraph with min dicut τ but max dijoin packing ≤ τ − 1.
Verify: min dicut via flow; max disjoint dijoins via ILP (partition arcs into τ dijoins).
Witness likely ≤ 30 arcs if it exists.

**Prompt variants:**
1. **V1 DGG playbook**: build the exact harness — random/annealed small digraphs, score =
   τ(min dicut) − ILP(max dijoin packing); run at 8–30 arcs with isomorph rejection.
2. **V2 subdivision seeds**: take Schrijver's and Cornuéjols–Guenin weighted counterexamples,
   replace weights by parallel/subdivided arcs in all combinatorially distinct ways (subdivision
   changes dicut structure); test each and anneal around them.
3. **V3 τ=3 targeted**: restrict to digraphs with min dicut exactly 3; use the known
   Abdi–Cornuéjols–Zlatin partial results to identify structural conditions a counterexample must
   satisfy; enumerate within that class.
4. **V4 LP integrality gap**: study the fractional dijoin-packing LP (exact by LY duality
   considerations); search instances maximizing the integrality gap of the packing ILP —
   any instance with gap ≥ 1 after rounding analysis is a candidate; certify with exact ILP.
5. **V5 literature-first**: digest Schrijver 1980, Cornuéjols–Guenin 2002, Abdi et al. 2023–25;
   map exactly which digraph classes are safe; design the search to live outside all safe classes
   (non-planar, not source-sink connected, τ ≥ 3) and run it.

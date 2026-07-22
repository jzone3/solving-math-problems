# P05 — Gallai's Three Longest Paths Question

**Statement.** In every connected graph, any three longest paths have a common vertex.
(Gallai 1966 asked about all longest paths — false, Walther 1969; the 3-path version is the
surviving open case. openproblemgarden.org/op/do_any_three_longest_paths_in_a_connected_graph_have_a_vertex_in_common)

**Why it matters.** Benchmark of longest-path structure theory. Known: 7 longest paths can have
empty intersection (Skupień); 2 always intersect (folklore); 3 is open.

**Status.** True for outerplanar, series-parallel, graphs with Hamiltonian blocks. Any polyhedral
counterexample needs ≥ 18 vertices (Brown, PhD thesis 2025). General exhaustive frontier low
(~n ≤ 12). No SAT attack in the literature.

**Witness & verifier.** A connected graph + three longest paths with no common vertex.
Verify: exact longest-path length (ILP/DP, fine for sparse n ≤ 60), check the 3 paths attain it
and have empty intersection.

**Prompt variants:**
1. **V1 hypotraceable seeds**: the 7-path counterexamples come from hypotraceable graphs
   (Thomassen's 34-vertex graph); mutate/hybridize hypotraceable and near-hypotraceable graphs;
   objective = min over vertices of (number of longest paths through it), minimize to 0 over
   triples.
2. **V2 SAT at fixed (n, L)**: encode "three paths of length L, pairwise-empty common
   intersection, no path of length > L" as SAT for n = 12–20; sweep L; SMS-style symmetry
   breaking.
3. **V3 block-structure construction**: the known 3-path-true classes all have well-behaved
   block trees; design graphs whose block decomposition defeats the known proof techniques
   (three long "arms" through distinct cut vertices) and search that parameterized family.
4. **V4 exhaustive frontier**: push exhaustive verification over all connected graphs to n = 13–14
   (with longest-path oracle + isomorph-free generation), and over sparse cubic graphs further;
   document the frontier.
5. **V5 literature-first**: digest the de Rezende–Fernandes–Martin–Wakabayashi survey line and
   Brown 2025; extract where proofs break; construct targeted candidates in the residual class
   before searching.

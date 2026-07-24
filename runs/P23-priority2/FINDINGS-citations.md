# Hadwiger–Nelson: is there a published plane 5-chromatic unit-distance graph with < 509 vertices?

Citation-graph forensics. All accesses: **2026-07-24** (UTC).

## VERDICT

**NO.** No published or publicly available work claims a 5-chromatic unit-distance graph **in the plane (R^2)** with fewer than 509 vertices. Parts' 509-vertex / 2442-edge graph (Geombinatorics XXIX(4) 2020, 137–166, arXiv:2010.12665) remains the smallest known, and is still cited as the record in works as recent as June 2026.

Strongest evidence (exact quotes):

1. Parts, arXiv:2010.12665 (abstract): *"We applied this method to minimize 5-chromatic unit-distance graphs and obtained a graph with 509 vertices and 2442 edges."* (Fig. 2 caption: *"5-chromatic graph with 509 vertices and 2442 edges."*)
2. **de Grey & Parts, arXiv:2303.14714 (2023)** — the two principals themselves, three years later: *"For k = 5, the finite upper bounds are v5 ≤ 509, e5 ≤ 2406, see [5]."* with footnote 2: *"In [5] the corresponding 509-vertex graph has 2442 edges, but is not edge-critical, which allows us to reduce e5. We were able to discard 36 edges…"* → **edges** were reduced to 2406; the **vertex** bound stays at 509. https://arxiv.org/abs/2303.14714
3. Oostema, Mahzoon & **Heule**, "Coloring Unit-Distance Strips using SAT", LPAR-23 (2020): *"The current record is a graph with 509 vertices and 2 442 edges, which was recently discovered by Jaan Parts [16]."* https://doi.org/10.29007/btmj (PDF: https://www.cs.cmu.edu/~mheule/publications/LPAR23-CNP.pdf)
4. Voronov, Neopryatnaya & Dergachev, Discrete Math. 345 (2022) 113106, arXiv:2106.11824: *"Then J. Parts, using a different vertex selection algorithm, found a 5-chromatic distance graph with 509 vertices, which is by far the minimal number of vertices in the case of the plane [29]."*
5. Chybowska-Sokół, Junosza-Szaniawski & Węsek, Discrete Math. (2023), arXiv:2201.04499: *"The current record of 509 vertices is held by Parts [52]."*
6. Gehér, "Note on the chromatic number of Minkowski planes", arXiv:2301.13695: *"while the distance graph published by de Grey had a total of 1581 vertices, the current known smallest example consists only 509 [18]."*
7. Exoo & Ismailescu, "A 5-chromatic same-distance graph in the hyperbolic plane", arXiv:2303.06801: *"progressively smaller 5-chromatic unit-distance graphs were found by Heule [5] and subsequently by Parts [9]; the current record is a graph of order 509."*
8. **Most recent (2026-06-15)**: A. Rosenmann, "On the chromatic number and equilateral dimension of R^n with the tropical norm", arXiv:2606.16642v2 (25 Jun 2026): *"A Polymath project was assigned to reduce the number of vertices of a graph requiring five colors and, as far as we know, the current minimal example is a graph of 509 vertices constructed by Parts in 2020 [23]."*
9. Aggarwal, "Computer-aided discovery of extremal unit-distance graphs & quantum contextuality", MIT PRIMES 2025: *"In 2022, Jaan Parts discovered the current record, a unit-distance graph with chromatic number 5 on only 509 vertices [23]."* https://math.mit.edu/research/highschool/primes/materials/2025/Aggarwal.pdf
10. Wikipedia, Hadwiger–Nelson problem (accessed 2026-07-24): *"As of 2021, the smallest known unit distance graph with chromatic number 5 has 509 vertices."*
11. Polymath16 wiki (michaelnielsen.org/polymath1, accessed 2026-07-24) is **stale**: its table of non-4-colorable graphs stops at G_11 = 510 vertices / 2508 edges, and the R^2 row of its "best known bounds" table still reads "5 | 510 | 2508 | 7". Nothing below 509 anywhere on the page.

## Method / coverage

- Semantic Scholar Graph API citations: `arXiv:2010.12665` → 18; `arXiv:1804.02385` → 135; `arXiv:1805.12181` → 30; `arXiv:2303.14714` → 0.
- OpenAlex `cites:` for all four works plus the duplicate OpenAlex records of de Grey's Geombinatorics version (W2795827704, 45 citations), the Exoo–Ismailescu DCG version (W2963183679, 34) and the second Parts record (W4287634333) — this surfaced several works S2 missed (e.g. "Diverse beam search to find densest-known planar unit distance graphs", "Geoffrey Exoo and Dan Ismailescu, or 2 Men for 2 Forbidden Distances", "On chromatic numbers of 3-dimensional slices" (2026 journal version)).
- arXiv API sweep `abs:"unit-distance" AND abs:"chromatic"` (all years, newest first) and author sweeps `au:Parts`, `au:"de Grey"` — to catch any non-citing new record. Newest relevant items: 2607.19995, 2607.19946, 2606.28157, 2606.16642, 2606.12325, 2603.14581 (Parts, "The chromatic number of R^8 is at least 25" — R^8, not the plane).
- **89 + 8 arXiv PDFs downloaded and converted to text**, then grepped for `509`, `5-chromatic`, `chromatic number 5`, `smallest known`, `record`, `we improve`, and for every `<number>-vertex/vertices` token with value < 509 co-occurring with a 5-chromatic mention. Every hit was read in context (see "traps" below).
- Non-arXiv items (paywalled/journal-only) were checked via abstract + landing page (Crossref/OpenAlex/Springer/Semantic Scholar); none is a plane-construction paper (SAT proof checkers, register allocation, prime/Fibonacci distance graphs, Ramsey sets in R^n, hyperbolic plane, expository notes).
- Also checked: Polymath16 wiki, Wikipedia, Heule's CMU publication page (CNP-SAT19.pdf, LPAR23-CNP.pdf).

## The full historical chain (all above 509)

| Graph | Vertices | Source |
|---|---|---|
| de Grey original | 20425 → 1581 | arXiv:1804.02385 |
| Heule (SAT minimization) | 826 → 803 → 633 → 610 → **553** | arXiv:1805.12181 ("consisting of 553 vertices") |
| Heule, proof trimming | **529** (2670 edges) | arXiv:1907.00929 / SAT'19: *"we were able to reduce the smallest known unit-distance graph with chromatic number 5 to a graph with 529 vertices and 2670 edges (down from 553 vertices and 2720 edges)"* |
| Polymath16 G_9 / G_10 / G_11 | 525 / 517 / **510** (2508 edges) | Polymath16 wiki table; 510 also quoted in Parts arXiv:1909.13177: *"who found a 5-chromatic unit-distance graph with 510 vertices and 2508 edges."* |
| **Parts** | **509** (2442 edges) | arXiv:2010.12665 — current record |

## Traps / near-misses explicitly ruled out (numbers < 509 that are NOT plane 5-chromatic UD graphs)

| Number seen | Where | Why it is not a counterexample |
|---|---|---|
| **481** ("G481") | Parts, "The chromatic number of the plane is at least 5 — a human-verifiable proof", arXiv:2010.12661, Fig. 7: *"The 481-vertex base graph G481. Fixed root vertices are shown in color… In total, 268 vertices are used."* | G481 is a **base graph** hosting coloring trees for a human-verifiable proof of χ≥5 — it is nowhere claimed to be 5-chromatic itself, and Parts (2020 and again with de Grey in 2023) states the smallest 5-chromatic graph is 509. |
| 372 and 972 | Voronov–Neopryatnaya–Dergachev, arXiv:2106.11824, Figs. 6–7: *"5-chromatic 372-vertex unit distance graph embedded into the circumsphere of…"* | **Sphere**, not the plane. Their planar constructions in the same paper have 64513 vertices. |
| 495 | Parts, "A 6-chromatic odd-distance graph in the plane", arXiv:2206.12632: *"we got a 495-vertex graph G495"* | **Odd-distance** graph, χ=6 — not a unit-distance graph. |
| 26, 100, 103 | Exoo–Ismailescu, arXiv:1805.06055 ("Figure 9. A 26-vertex {1,2}-graph with chromatic number 5") | **Two forbidden distances**, not unit-distance. |
| 622 | Exoo–Ismailescu, arXiv:2303.06801 | **Hyperbolic plane**, same-distance graph. |
| 421, 465 | Currie/Gehér-type Minkowski work, arXiv:2108.12861 ("unit-distance graph with vertex set U30+U30 has 421 vertices") | **Minkowski (regular-polygon) norm** plane, and those graphs are not 5-chromatic Euclidean UD graphs. |
| 59 (R^3), ~400 (R^3) | Mundinger et al., ICML 2025, arXiv:2501.18527 | **R^3**, χ≥6 constructions. |
| 29 (G29) | Dúcz & Varga, arXiv:2606.28157 (June 2026), "A unit-distance graph in the plane with independence ratio below 1/4" | Plane UD graph, but the result is **independence ratio / geometric fractional chromatic number > 4**, not chromatic number 5. Its χ is 4. |
| 27 / 21 / 31 etc. | various (G27, G21, G31 gadgets) | building blocks, χ ≤ 5 gadgets or 4-chromatic; none is a standalone 5-chromatic UD graph. |
| 525/517/510/529/553 | Heule + Polymath16 | all **larger** than 509. |

Also checked and irrelevant to the record: Gliesch & Ritt, "A new heuristic for finding verifiable k-vertex-critical subgraphs", J. Heuristics 28 (2022) — abstract (Springer landing page, accessed 2026-07-24) scopes it to **DIMACS** benchmark instances ("We find new best k-VCSs for several DIMACS instances"); it cites Heule only in passing and makes no planar UD claim. Full text paywalled; no planar-geometry claim visible in the accessible text.

## Full list of citing works checked

(Column "full text checked" = arXiv PDF downloaded and text-searched; "metadata/abstract only" = paywalled or non-arXiv, checked via abstract/landing page. "mentions 509" = the string 509 appears and was read in context — in every case it refers to Parts' record, never to a smaller graph.)

| Year | Paper | URL | Full text checked | mentions 509 |
|---|---|---|---|---|
| 2026 | A unit-distance graph in the plane with independence ratio below 1/4 | https://arxiv.org/abs/2606.28157 | yes |  |
| 2026 | Exact certification of the coordinate fields of the triangle-free Exoo-Ismailescu unit-distance graphs EI17 an | https://arxiv.org/abs/2607.19995 | yes | yes |
| 2026 | Improved bounds for lines and $1$-separated sets in Euclidean Ramsey theory | https://arxiv.org/abs/2606.17194 | yes |  |
| 2026 | Neural algorithmic reasoning for approximate k-coloring with recursive warm starts | https://arxiv.org/abs/2601.05137 | yes |  |
| 2026 | On the chromatic number and equilateral dimension of $\mathbb{R}^n$ with the tropical norm | https://arxiv.org/abs/2606.16642 | yes | yes |
| 2026 | On the range of two-distance graphs | https://arxiv.org/abs/2601.07828 | yes |  |
| 2026 | The chromatic number of R^8 is at least 25 (Parts 2026) | https://arxiv.org/abs/2603.14581 | yes |  |
| 2025 | Diverse beam search to find densest-known planar unit distance graphs | https://arxiv.org/abs/2406.15317 | yes |  |
| 2025 | Fractional Chromatic Numbers and Chromatic Numbers for the Fibonacci Distance Graphs | https://doi.org/10.1080/00150517.2025.2503249 | metadata/abstract only |  |
| 2025 | Isomorphisms of unit distance graphs of layers | https://arxiv.org/abs/2505.07799 | yes |  |
| 2025 | Lower Bounds for the Independence Numbers of Distance Graphs with Vertices in \documentclass[12pt]{minimal} \u | https://doi.org/10.1134/S0032946025020048 | metadata/abstract only |  |
| 2025 | Neural Discovery in Mathematics: Do Machines Dream of Colored Planes? | https://arxiv.org/abs/2501.18527 | yes |  |
| 2025 | On the chromatic number of the plane for map-type colorings | https://arxiv.org/abs/2502.01958 | yes |  |
| 2025 | On the Chromatic Number of the Plane with Two Forbidden Distances | https://doi.org/10.1080/00029890.2025.2559554 | metadata/abstract only |  |
| 2025 | Ramsey problems for graphs in Euclidean spaces and Cartesian powers | https://arxiv.org/abs/2512.15516 | yes |  |
| 2024 | A Graph Theorist Plants a Tree | https://doi.org/10.1080/07468342.2024.2377007 | metadata/abstract only |  |
| 2024 | A Lower Bound on the Number of Colours Needed to Nicely Colour a Sphere | https://arxiv.org/abs/2404.14398 | yes |  |
| 2024 | Any Two-Coloring of the Plane Contains Monochromatic 3-Term Arithmetic Progressions | https://arxiv.org/abs/2402.14197 | yes |  |
| 2024 | Canonical theorems in geometric Ramsey theory | https://arxiv.org/abs/2404.11454 | yes |  |
| 2024 | Characterization of Colorings Obtained by a Method of Szlam | https://arxiv.org/abs/2411.04346 | yes |  |
| 2024 | Chromatic Coloring of Distance Graphs V | https://doi.org/10.61091/jcmcc122-26 | metadata/abstract only |  |
| 2024 | Extending the Continuum of Six-Colorings | https://arxiv.org/abs/2404.05509 | yes | yes |
| 2024 | On lower bounds of the density of planar periodic sets without unit distances | https://arxiv.org/abs/2411.13248 | yes |  |
| 2023 | A 5-chromatic same-distance graph in the hyperbolic plane | https://arxiv.org/abs/2303.06801 | yes | yes |
| 2023 | Chromatic number of spacetime | https://arxiv.org/abs/2308.16885 | yes | yes |
| 2023 | Chromatic numbers of Cayley graphs of abelian groups: A matrix method | https://arxiv.org/abs/2303.06262 | yes |  |
| 2023 | Cliques in representation graphs of quadratic forms | https://arxiv.org/abs/2306.07108 | yes | yes |
| 2023 | Coloring and density theorems for configurations of a given volume | https://arxiv.org/abs/2309.09973 | yes |  |
| 2023 | Decidability of modal logics of non-k-colorable graphs | https://arxiv.org/abs/2303.09934 | yes |  |
| 2023 | Monochromatic Infinite Sets in Minkowski Planes | https://arxiv.org/abs/2308.08840 | yes |  |
| 2023 | Monochromatic triangles in the max-norm plane | https://arxiv.org/abs/2302.09972 | yes |  |
| 2023 | More certainty in coloring the plane with a forbidden distance interval | https://arxiv.org/abs/2303.14722 | yes | yes |
| 2023 | Nonrepetitive colorings of Rd | https://doi.org/10.5817/cz.muni.eurocomb23-016 | metadata/abstract only |  |
| 2023 | Note on the Chromatic Number of Minkowski Planes: The Regular Polygon Case | https://arxiv.org/abs/2301.13695 | yes | yes |
| 2023 | On lower bounds of the order of $k$-chromatic unit distance graphs | https://arxiv.org/abs/2303.14714 | yes | yes |
| 2023 | Optimization of trigonometric polynomials with crystallographic symmetry and spectral bounds for set avoiding  | https://arxiv.org/abs/2303.09487 | yes | yes |
| 2023 | Prime and polynomial distances in colourings of the plane | https://arxiv.org/abs/2308.02483 | yes |  |
| 2023 | Spherical sets avoiding orthonormal bases | https://arxiv.org/abs/2310.06821 | yes |  |
| 2023 | Still Spinning: The Moser Spindle at Sixty | https://doi.org/10.1080/0025570X.2023.2176684 | metadata/abstract only |  |
| 2023 | The chromatic number of the plane with an interval of forbidden distances is at least 7 | https://arxiv.org/abs/2304.10163 | yes | yes |
| 2023 | The fractional chromatic number of the plane is at least 4 | https://arxiv.org/abs/2311.10069 | yes |  |
| 2023 | Unit and Distinct Distances in Typical Norms | https://arxiv.org/abs/2302.09058 | yes |  |
| 2022 | A 6-chromatic odd-distance graph in the plane | https://arxiv.org/abs/2206.12632 | yes | yes |
| 2022 | A conditional approach for monochromatic unit distance in a plane for four and five coloring | https://arxiv.org/abs/2210.16212 | yes |  |
| 2022 | A new heuristic for finding verifiable k-vertex-critical subgraphs | https://doi.org/10.1007/s10732-021-09487-9 | metadata/abstract only |  |
| 2022 | Clique numbers of finite unit-quadrance graphs | https://doi.org/10.1007/s10801-022-01157-8 | metadata/abstract only |  |
| 2022 | Coloring distance graphs on the plane | https://arxiv.org/abs/2201.04499 | yes | yes |
| 2022 | Cutting corners | https://arxiv.org/abs/2211.17150 | yes |  |
| 2022 | Embedding euclidean distance graphs in R n and Q n |  | metadata/abstract only |  |
| 2022 | Odd Distances in Colourings of the Plane | https://arxiv.org/abs/2209.15598 | yes |  |
| 2022 | On the Chromatic Number of 2-Dimensional Spheres | https://arxiv.org/abs/2203.08666 | yes |  |
| 2022 | On the chromatic numbers of 3-dimensional slices | https://arxiv.org/abs/2208.02230 | yes | yes |
| 2022 | On the plane and its coloring | https://arxiv.org/abs/2206.12633 | yes |  |
| 2022 | Online coloring of disk graphs | https://arxiv.org/abs/2206.14564 | yes |  |
| 2022 | Practical algebraic calculus and Nullstellensatz with the checkers Pacheck and Pastèque and Nuss-Checker | https://doi.org/10.1007/s10703-022-00391-x | metadata/abstract only |  |
| 2022 | The Chromatic Number of $\mathbb{R}^{n}$ with Multiple Forbidden Distances | https://arxiv.org/abs/2205.12312 | yes |  |
| 2022 | THE CHROMATIC NUMBER OF R n WITH MULTIPLE FORBIDDEN DISTANCES |  | metadata/abstract only |  |
| 2022 | The density of planar sets avoiding unit distances | https://arxiv.org/abs/2207.14179 | yes |  |
| 2022 | Two-Colorings of Normed Spaces with No Long Monochromatic Unit Arithmetic Progressions | https://doi.org/10.1134/S1064562422050143 | metadata/abstract only |  |
| 2022 | Two-Colorings of Normed Spaces without Long Monochromatic Unit Arithmetic Progressions | https://arxiv.org/abs/2203.04555 | yes |  |
| 2021 | A recursive Lovász theta number for simplex-avoiding sets | https://arxiv.org/abs/2106.09360 | yes | yes |
| 2021 | A solution to Ringel's circle problem | https://arxiv.org/abs/2112.05042 | yes |  |
| 2021 | A universal partition result for infinite homogeneous Kn-free and related graphs | https://doi.org/10.1016/J.DISC.2020.112153 | metadata/abstract only |  |
| 2021 | Annulus Graphs in Rd\documentclass[12pt]{minimal} \usepackage{amsmath} \usepackage{wasysym} \usepackage{amsfon | https://arxiv.org/abs/2112.09453 | yes |  |
| 2021 | Assorted musings on dimension-critical graphs | https://arxiv.org/abs/2106.05333 | yes |  |
| 2021 | C O ] 1 7 D ec 2 02 1 Annulus graphs in R d |  | metadata/abstract only |  |
| 2021 | Chromatic Coloring of Distance Graphs I | https://doi.org/10.35940/ijitee.i9291.0710921 | metadata/abstract only |  |
| 2021 | Cliques in exact distance powers of graphs of given maximum degree | https://doi.org/10.1016/j.procs.2021.11.052 | metadata/abstract only |  |
| 2021 | Constructing 5-chromatic unit distance graphs embedded in the Euclidean plane and two-dimensional spheres | https://arxiv.org/abs/2106.11824 | yes | yes |
| 2021 | Design of quantum optical experiments with logic artificial intelligence | https://arxiv.org/abs/2109.13273 | yes |  |
| 2021 | Easier variants of notorious math problems |  | metadata/abstract only |  |
| 2021 | Embedding euclidean distance graphs in $${\mathbb {R}}^n$$ and $${\mathbb {Q}}^n$$ | https://arxiv.org/abs/2108.07713 | yes |  |
| 2021 | Embedding Euclidean Distance Graphs in R and Q |  | metadata/abstract only |  |
| 2021 | Finite (cid:15) -unit distance graphs |  | metadata/abstract only |  |
| 2021 | Intersection Problems in Extremal Combinatorics: Theorems, Techniques and Questions Old and New | https://arxiv.org/abs/2107.06371 | yes |  |
| 2021 | Mathematicorum with Mathematical Mayhem |  | metadata/abstract only |  |
| 2021 | Max-norm Ramsey theory | https://arxiv.org/abs/2111.08949 | yes |  |
| 2021 | Maximum likelihood thresholds via graph rigidity | https://arxiv.org/abs/2108.02185 | yes | yes |
| 2021 | Non-local Potts model on random lattice and chromatic number of a plane | https://arxiv.org/abs/2107.08508 | yes |  |
| 2021 | On the Babai and Upper Chromatic Numbers of Graphs of Diameter 2 | https://doi.org/10.5556/J.TKJM.52.2021.3430 | metadata/abstract only |  |
| 2021 | Probabilistic formulation of the Hadwiger--Nelson problem | https://arxiv.org/abs/2112.07665 | yes | yes |
| 2021 | The chromatic number of the Minkowski plane -- the regular polygon case | https://arxiv.org/abs/2108.12861 | yes |  |
| 2021 | Upper Bounds on Chromatic Number of $\mathbb{E}^n$ in Low Dimensions | https://arxiv.org/abs/2112.13438 | yes |  |
| 2020 | A Finite Graph Approach to the Probabilistic Hadwiger-Nelson Problem. | https://arxiv.org/abs/2008.07987 | yes |  |
| 2020 | A small 6-chromatic two-distance graph in the plane | https://arxiv.org/abs/2010.12656 | yes |  |
| 2020 | All finite sets are Ramsey in the maximum norm | https://arxiv.org/abs/2008.02008 | yes |  |
| 2020 | Coloring Unit-Distance Strips using SAT | https://doi.org/10.29007/btmj | metadata/abstract only |  |
| 2020 | D M ] 2 S ep 2 02 0 Exact square coloring of subcubic planar graphs ∗ |  | metadata/abstract only |  |
| 2020 | Deep Learning-based Approximate Graph-Coloring Algorithm for Register Allocation | https://doi.org/10.1109/LLVMHPCHiPar51896.2020.00008 | metadata/abstract only |  |
| 2020 | Density Estimates of 1-Avoiding Sets via Higher Order Correlations | https://doi.org/10.1007/s00454-020-00263-3 | metadata/abstract only |  |
| 2020 | Exact square coloring of subcubic planar graphs | https://arxiv.org/abs/2009.00843 | yes |  |
| 2020 | Graph minimization, focusing on the example of 5-chromatic unit-distance graphs in the plane | https://arxiv.org/abs/2010.12665 | yes | yes |
| 2020 | Nullstellensatz-Proofs for Multiplier Verification | https://doi.org/10.1007/978-3-030-60026-6_21 | metadata/abstract only |  |
| 2020 | Odd Wheels Are Not Odd-Distance Graphs | https://arxiv.org/abs/2008.10305 | yes | yes |
| 2020 | On some problems in combinatorial geometry |  | metadata/abstract only |  |
| 2020 | On the Chromatic Numbers Corresponding to Exponentially Ramsey Sets | https://doi.org/10.1007/s10958-020-04815-z | metadata/abstract only |  |
| 2020 | Reasoning with Propositional Logic: From SAT Solvers to Knowledge Compilation | https://doi.org/10.1007/978-3-030-06167-8_5 | metadata/abstract only |  |
| 2020 | The chromatic number of the plane is at least 5 -- a human-verifiable proof | https://arxiv.org/abs/2010.12661 | yes |  |
| 2020 | The Proof Checkers Pacheck and Pastèque for the Practical Algebraic Calculus | https://doi.org/10.34727/2020/isbn.978-3-85448-042-6_34 | metadata/abstract only |  |
| 2020 | Uniquely optimal codes of low complexity are symmetric | https://arxiv.org/abs/2008.12871 | yes |  |
| 2020 | What percent of the plane can be properly 5- and 6-colored? | https://arxiv.org/abs/2010.12668 | yes | yes |
| 2019 | A $6$-chromatic two-distance graph in the plane | https://arxiv.org/abs/1909.13177 | yes |  |
| 2019 | Almost-Monochromatic Sets and the Chromatic Number of the Plane | https://arxiv.org/abs/1912.02604 | yes |  |
| 2019 | Beskonačne i konačne formulacije matematičkih rezultata |  | metadata/abstract only |  |
| 2019 | Clockface polygons and the collective joy of making mathematics together | https://doi.org/10.54870/1551-3440.1451 | metadata/abstract only |  |
| 2019 | Computing a Smaller Unit-Distance Graph with Chromatic Number 5 via Proof Trimming |  | metadata/abstract only |  |
| 2019 | Counterexamples to Borsuk’s Conjecture with Large Girth | https://doi.org/10.1134/S0001434619050249 | metadata/abstract only |  |
| 2019 | Deep Learning-based Hybrid Graph-Coloring Algorithm for Register Allocation | https://arxiv.org/abs/1912.03700 | yes |  |
| 2019 | Discrete Approximation of Coloring the Plane | https://doi.org/10.46787/pump.v2i0.227 | metadata/abstract only |  |
| 2019 | Lattice approach to plane colorings | https://arxiv.org/abs/1908.03880 | yes |  |
| 2019 | Lattice approach to plane colorings. |  | metadata/abstract only |  |
| 2019 | Monochromatic equilateral triangles in the unit distance graph | https://arxiv.org/abs/1909.09856 | yes |  |
| 2019 | On a Frankl-Wilson Theorem | https://doi.org/10.1134/S0032946019040045 | metadata/abstract only |  |
| 2019 | On periodic sets avoiding given distance on the hyperbolic plane |  | metadata/abstract only |  |
| 2019 | On the support of a non-autocorrelated function on a hyperbolic surface | https://arxiv.org/abs/1908.11613 | yes |  |
| 2019 | Problems in extremal graph theory and Euclidean Ramsey theory |  | metadata/abstract only |  |
| 2019 | Shalosh B. Ekhad: a computer credit for mathematicians | https://doi.org/10.1007/s11192-019-03305-7 | metadata/abstract only |  |
| 2019 | Small unit-distance graphs in the plane | https://arxiv.org/abs/1905.07829 | yes |  |
| 2019 | Triangle colorings require at least seven colors | https://arxiv.org/abs/1909.02708 | yes |  |
| 2019 | Trimming Graphs Using Clausal Proof Optimization | https://arxiv.org/abs/1907.00929 | yes |  |
| 2019 | Twenty Female Mathematicians | https://arxiv.org/abs/1910.01730 | yes |  |
| 2018 | Computing Small Unit-Distance Graphs with Chromatic Number 5 | https://arxiv.org/abs/1805.12181 | yes |  |
| 2018 | Exponentially Ramsey Sets | https://doi.org/10.1134/S0032946018040051 | metadata/abstract only |  |
| 2018 | Improved Frankl–Rödl Theorem and Some of Its Geometric Consequences | https://doi.org/10.1134/S0032946018020047 | metadata/abstract only |  |
| 2018 | Lower Bounds for the Measurable Chromatic Number of the Hyperbolic Plane | https://doi.org/10.1007/s00454-018-0027-8 | metadata/abstract only |  |
| 2018 | On the density of planar sets without unit distances | https://arxiv.org/abs/1809.05453 | yes |  |
| 2018 | On the density of sets of the Euclidean plane avoiding distance 1 | https://arxiv.org/abs/1810.00960 | yes |  |
| 2018 | Reinforcement Learning in Graph Theory |  | metadata/abstract only |  |
| 2018 | Solmu 3/2018 |  | metadata/abstract only |  |
| 2018 | The Chromatic Number of the Plane is At Least 5: A New Proof | https://arxiv.org/abs/1805.00157 | yes | yes |
| 2018 | The Hadwiger-Nelson problem with two forbidden distances | https://arxiv.org/abs/1805.06055 | yes |  |
| 2018 | The Namer-Claimer game | https://arxiv.org/abs/1808.10800 | yes |  |
| 2017 | Chromatic numbers of spheres | https://arxiv.org/abs/1711.03193 | yes |  |
| 2017 | Combinatorial distance geometry in normed spaces | https://arxiv.org/abs/1702.00066 | yes | yes |
| 2017 | Exact Distance Colouring in Trees | https://arxiv.org/abs/1703.06047 | yes |  |
| 2017 | Lower Bounds for the Measurable Chromatic Number of the Hyperbolic Plane | https://arxiv.org/abs/1708.01081 | yes |  |
| 2017 | Polynomial configurations in sets of positive upper density over local fields | https://arxiv.org/abs/1701.06024 | yes | yes |
| 2016 | A new proof of the Larman-Rogers upper bound for the chromatic number of the Euclidean space | https://arxiv.org/abs/1610.02846 | yes |  |
| 2008 | The mathematics of Septoku | https://arxiv.org/abs/0801.3697 | yes |  |
| ? | A 21-Vertex 4-Chromatic Unit-Distance Graph of Girth 4 |  | metadata/abstract only |  |
| ? | Comptes Rendus Mathématique |  | metadata/abstract only |  |
| ? | COMPUTER-AIDED DISCOVERY OF EXTREMAL UNIT-DISTANCE GRAPHS & QUANTUM CONTEXTUALITY |  | metadata/abstract only |  |
| ? | SAT COMPETITION 2016 Solver and Benchmark Descriptions |  | metadata/abstract only |  |
| ? | The Mathematics Enthusiast The Mathematics Enthusiast |  | metadata/abstract only |  |


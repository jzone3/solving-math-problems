# Literature forensics: 5-chromatic unit-distance graphs in the Euclidean plane

**Research cutoff/access date:** 2026-07-24.  
**Question:** Did any published or publicly available source, in the requested Russian-language or worldwide-thesis scope, report a 5-chromatic unit-distance graph embedded in the ordinary Euclidean plane with fewer than 509 vertices?

## Bottom line

I found **no published or publicly available source reporting fewer than 509 vertices for a 5-chromatic unit-distance graph in the ordinary plane**. The strongest verified plane construction found is Jaan Parts's **509 vertices / 2442 edges**. Parts's paper explicitly calls it the “record-holder.” Earlier public constructions/records are 1581 (de Grey), 553 and 529 (Heule), and 510 (Heule/competition). The Russian-school paper by Voronov–Neopryatnaya–Dergachev reports **64513 plane vertices**, while its smaller 372- and 972-vertex examples are on spheres, not in the plane.

This is a literature-search conclusion, **not a mathematical proof that no unpublished/private graph exists**. I also found no thesis in 2019–2026 that claims a plane graph below 509. One Warsaw master's thesis reports a 529-vertex graph; the ELTE master's thesis is about the probabilistic formulation/order lower bounds, not a smaller graph.

“Claims <509 in the plane?” below means: does the source itself make such a claim? `No` means it reports a count >=509 or only discusses unrelated variants; `Unclear` means relevant but no count/record claim was located.

## Primary record and comparator sources

### 1. Jaan Parts, “Graph minimization, focusing on the example of 5-chromatic unit-distance graphs in the plane” (2020)

- **URLs:** [arXiv abstract](https://arxiv.org/abs/2010.12665), [HTML full text](https://ar5iv.labs.arxiv.org/html/2010.12665), [MathWorld summary](https://mathworld.wolfram.com/PartsGraphs.html)
- **Accessed:** 2026-07-24
- **What it says:** This is the key source. It minimizes 5-chromatic unit-distance graphs in the ordinary plane and gives the 509-vertex/2442-edge graph.
- **Exact quotations:**
  > “We introduce a new graph minimization method, in which it is required to preserve some graph property and there is an effective procedure for checking this property. We applied this method to minimize 5-chromatic unit-distance graphs and obtained a graph with 509 vertices and 2442 edges.”

  > “The record-holder is a graph with 509 vertices and 2442 edges (Fig. 2) … For comparison we show the previous 510-vertex record obtained in the competition with Heule …”

  > “Together, in the course of a short competition, we brought the number of vertices down to 525, 517 (Heule) and, finally, 510 (Heule soon corrected his method and came to a similar result [8]). Later, when preparing this text, we obtained a graph with 509 vertices.”
- **Verdict:** **No** — it reports 509 as the record-holder, not <509.

### 2. Aubrey D. N. J. de Grey, “The chromatic number of the plane is at least 5” (2018)

- **URLs:** [arXiv](https://arxiv.org/abs/1804.02385), [HTML](https://ar5iv.labs.arxiv.org/html/1804.02385)
- **Accessed:** 2026-07-24
- **What it says:** First published 5-chromatic unit-distance plane construction; later text describes its 1581-vertex graph.
- **Exact quotations:**
  > “We present a family of finite unit-distance graphs in the plane that are not 4-colourable, thereby improving the lower bound of the Hadwiger-Nelson problem. The smallest such graph that we have so far discovered has 1581 vertices.”

  > “Despite the rather simplistic nature of these methods, we have so far shrunk N by a factor of nearly 13, our current record being the 1581-vertex graph G …”
- **Verdict:** **No** — 1581, not <509.

### 3. Marijn J. H. Heule et al., “Computing Smaller Unit-Distance Graphs with Chromatic Number 5” (2018)

- **URL:** [arXiv PDF/search record](https://arxiv.org/pdf/1805.12181)
- **Accessed:** 2026-07-24
- **What it says:** SAT/proof-minimization work reporting 553-vertex plane graphs, reducing the published 1581-vertex construction.
- **Exact quotation from the arXiv record:**
  > “We present a new method for reducing the size of graphs with a given property. Our method, which is based on clausal proof minimization, allowed us to compute several 553-vertex unit-distance graphs with chromatic number 5, while the smallest published unit-distance graph with chromatic number 5 has 1581 vertices.”
- **Verdict:** **No** — 553.

### 4. Marijn J. H. Heule, “Computing a Smaller Unit-Distance Graph with Chromatic Number 5 via Proof Trimming” (2019)

- **URLs:** [arXiv](https://arxiv.org/abs/1907.00929), [CMU PDF](https://www.cs.cmu.edu/~mheule/publications/CNP-SAT19.pdf), [NSF-hosted PDF](https://par.nsf.gov/servlets/purl/10120529)
- **Accessed:** 2026-07-24
- **What it says:** Reduces the then-smallest known graph from 553 to 529 vertices.
- **Exact quotation:**
  > “We applied this method to reduce the smallest known unit-distance graph with chromatic number 5 from 553 vertices and 2720 edges to 529 vertices and 2670 edges.”
- **Verdict:** **No** — 529.

### 5. Marijn J. H. Heule, “Formal Methods and the Chromatic Number of the Plane” (slides)

- **URL:** [CMU/Avigad meeting slides](https://www.andrew.cmu.edu/user/avigad/meetings/fomm2020/slides/fomm_heule.pdf)
- **Accessed:** 2026-07-24
- **What it says:** Public presentation of the SAT progress; reports a 510-vertex graph.
- **Exact quotation:**
  > “Our proof minimization techniques were able to construct a 510-vertex unit-distance graph with chromatic number 5.”
- **Verdict:** **No** — 510.

### 6. Oostema, Martins, Heule, “Coloring Unit-Distance Strips using SAT” (2023)

- **URLs:** [CMU PDF](https://www.cs.cmu.edu/~mheule/publications/LPAR23-CNP.pdf), [EasyChair PDF](https://e.easychair.org/publications/paper/69T4/download)
- **Accessed:** 2026-07-24
- **What it says:** A strip-coloring/SAT paper, not a new minimization result. Its introduction summarizes the known plane record as 509.
- **Exact quotation:**
  > “The current record is a graph with 509 vertices and 2 442 edges, which was recently discovered by Jaan Parts [16].”
- **Verdict:** **No** — explicitly says current record is 509.

### 7. Wolfram MathWorld, “Parts Graphs” (secondary source)

- **URL:** https://mathworld.wolfram.com/PartsGraphs.html
- **Accessed:** 2026-07-24
- **What it says:** Gives a chronological table: 553, 529, 525, 510, 510, 509 vertices (with corresponding edge counts and dates).
- **Relevant exact table values:** `553`, `529`, `525`, `510`, `510`, `509`; final entry `509 | 2442`.
- **Verdict:** **No** — its listed minimum is 509.

## Part A — Russian-language / Raigorodskii-school sources

### 8. Voronov, Neopryatnaya, Dergachev, “Constructing 5-Chromatic Unit Distance Graphs Embedded in the Euclidean Plane and Two-Dimensional Spheres” (2021 preprint; Discrete Mathematics 2022)

- **URLs:** [arXiv](https://arxiv.org/abs/2106.11824), [HTML](https://ar5iv.labs.arxiv.org/html/2106.11824), [Math-Net author bibliography](https://www.mathnet.ru/php/person.phtml?option_lang=rus&personid=62211)
- **Accessed:** 2026-07-24
- **What it says:** Russian-school authors develop constructions based on a 4-chromatic subgraph. The plane examples have 64513 vertices; the smaller 372- and 972-vertex graphs are embedded in two-dimensional spheres.
- **Exact quotations:**
  > “A series of 5-chromatic unit distance graphs on 64513 vertices embedded into the plane is constructed.”

  > “Namely, the 5-chromatic unit distance graph on 372 vertices embedded into the circumsphere of an icosahedron with a unit edge length, and the 5-chromatic graph on 972 vertices embedded into the circumsphere of a great icosahedron are constructed.”
- **Variant warning:** 372 and 972 are **sphere** counts, not plane counts. The plane count stated in the abstract is 64513.
- **Verdict:** **No** — plane count is 64513; sphere counts do not answer the question.

### 9. Kanel-Belov, Voronov, Cherkashin, “О хроматическом числе плоскости” / “On the chromatic number of infinitesimal plane layer” (2017/2018)

- **URLs:** [Math-Net author page](https://www.mathnet.ru/php/person.phtml?option_lang=rus&personid=62211) (the Math-Net entry identifies the 2017 Russian paper and English translation)
- **Accessed:** 2026-07-24
- **What it says:** This is about a “plane layer”/infinitesimal-layer variant, not the ordinary plane's finite 5-chromatic graph record. No <509 ordinary-plane graph claim was located.
- **Exact contextual quotation from the Math-Net indexed text:**
  > “У него рёбра — отрезки длины 1. Хроматическое число этого графа, как нетрудно видеть, равно четырем.”
  (The surrounding discussion is the 7-vertex Moser spindle and the classical lower bound 4.)
- **Variant warning:** Do not treat “infinitesimal plane layer” results as a new ordinary-plane 5-chromatic graph.
- **Verdict:** **Unclear** — relevant background/variant, but no <509 ordinary-plane claim.

### 10. Sokolov, Voronov, “On the chromatic number of the plane for map-type colorings” (2025)

- **URL:** [arXiv HTML](https://ar5iv.labs.arxiv.org/html/2502.01958)
- **Accessed:** 2026-07-24
- **What it says:** Studies map-type colorings with restrictions on region boundaries/vertices, not finite unit-distance graph minimization.
- **Exact quotation:**
  > “We consider the Hadwiger–Nelson problem on the chromatic number of the plane under conditions of coloring a map containing a finite number of vertices in any bounded region.”

  > “In the classical formulation of the problem … From [3, 5] it is known that 5 ≤ χ(R²) ≤ 7.”
- **Variant warning:** Its 6/7-color map bounds concern a strengthened coloring model; they are not claims of a smaller 5-chromatic unit-distance graph.
- **Verdict:** **Unclear** — no vertex-count claim for an ordinary-plane 5-chromatic graph.

### 11. Raigorodskii, Trukhan, “О хроматических числах некоторых дистанционных графов” (2018)

- **URL:** [Math-Net](https://www.mathnet.ru/php/archive.phtml?wshow=paper&jrnid=dan&paperid=47476&option_lang=rus)
- **Accessed:** 2026-07-24
- **What it says:** Estimates chromatic numbers of distance graphs with vertices in `{−1,0,1}^n`; this is a high-dimensional/discrete distance-graph problem, not plane graph minimization.
- **Exact indexed abstract quotation:**
  > “В работе получены новые оценки для хроматических чисел графов из различных классов дистанционных графов с вершинами в {-1; 0; 1}^n.”
- **Variant warning:** The vertex set `{−1,0,1}^n` and dimension parameter make this unrelated to a <509 plane record.
- **Verdict:** **No** — no ordinary-plane count claim.

### 12. Demekhin, Raigorodskii, Rubanov, “Дистанционные графы, имеющие большое хроматическое число и не содержащие клик или циклов заданного размера” (2013)

- **URL:** [Math-Net English full text](https://www.mathnet.ru/php/getFT.phtml?jrnid=sm&paperid=7830&what=fullteng)
- **Accessed:** 2026-07-24
- **What it says:** Existence of high-dimensional distance graphs with large chromatic number and prescribed clique/cycle avoidance.
- **Exact indexed abstract quotation:**
  > “Доказано существование последовательностей дистанционных графов G_n ⊂ R^n, хроматические числа которых растут экспоненциально, но которые в то же время не содержат клик или циклов заданного наперед размера.”
- **Variant warning:** This is asymptotic/high-dimensional and not a finite 5-chromatic plane graph record.
- **Verdict:** **No** — no ordinary-plane count claim.

### 13. Rubanov, “Хроматические числа трехмерных графов расстояний, не содержащих тетраэдров” (2007)

- **URL:** [Math-Net/DOI](https://doi.org/10.4213/mzm4091)
- **Accessed:** 2026-07-24
- **What it says:** Constructs a 5-chromatic distance graph in R^3 with no tetrahedra, using Moser-spindle ideas.
- **Exact quotation:**
  > “В пространстве R^3 существует граф расстояний, имеющий хроматическое число 5 и не содержащий тетраэдров.”
- **Variant warning:** R^3, not the plane; no vertex count relevant to the question is supplied in the indexed text.
- **Verdict:** **No** — wrong dimension.

### 14. Cherkashin and Voronov, “On the chromatic number of 2-dimensional spheres” (2023)

- **URL:** [Math-Net bibliography entry / arXiv 2203.08666](https://www.mathnet.ru/php/person.phtml?option_lang=rus&personid=62211)
- **Accessed:** 2026-07-24
- **What it says:** Sphere problem, not ordinary-plane graph minimization.
- **Verdict:** **No** — sphere variant; no <509 plane claim.

### 15. “О рациональных аналогах проблем Нелсона–Хадвигера и Борсука” (CyberLeninka)

- **URL:** https://cyberleninka.ru/article/n/o-ratsionalnyh-analogah-problem-nelsona-hadvigera-i-borsuka
- **Accessed:** 2026-07-24
- **What it says:** Rational/affine-rational analogues, including `Q^n` and rational-coordinate unit-distance graphs.
- **Exact indexed quotation:**
  > “В этой статье мы рассматриваем аффинно-рациональные аналоги задачи Нелсона-Хадвигера …”
- **Variant warning:** Rational/algebraic plane analogues cannot be silently substituted for the ordinary real plane record; the source does not report a <509 ordinary-plane graph.
- **Verdict:** **No** — no ordinary-plane <509 claim.

### 16. Pyaderkin, “Числа независимости и хроматические числа случайных дистанционных графов” (MIPT candidate dissertation, defended 2019)

- **URL:** [Istina MSU](https://istina.msu.ru/dissertations/247553156/)
- **Accessed:** 2026-07-24
- **What it says:** Dissertation on independence/chromatic numbers of random distance graphs; supervisor A. M. Raigorodskii; MIPT, 8 April 2019.
- **Exact metadata:** Istina lists the title, author, MIPT affiliation, supervisor, and defense date; no finite ordinary-plane 5-chromatic graph count was found in the public metadata.
- **Verdict:** **Unclear** — relevant school/dissertation metadata, but no <509 plane claim.

### 17. Kupavskii lecture material, “Дистанционные графы с большим обхватом и большим хроматическим числом”

- **URL:** http://kupavskii.com/wp-content/uploads/2016/07/2012-Petrozavodsk.pdf
- **Accessed:** 2026-07-24
- **What it says:** Lecture slides define distance graphs and state the classical plane bound `4 ≤ χ(R²) ≤ 7`; focus is large girth/chromatic number, not 5-chromatic graph minimization.
- **Exact indexed quotation:**
  > “Несложно показать, что 4 ≤ χ(R²) ≤ 7.”
- **Verdict:** **No** — no <509 claim.

### 18. Russian conference/program material: “Осенние математические чтения в Адыгее 2025”

- **URL:** https://amra.cmcagu.ru/programma-konferentsii/
- **Accessed:** 2026-07-24
- **What it says:** Program lists talks including “Хроматическое число плоскости при всюду плотных цветовых классах” and “Непрерывные вложения дистанционных графов.”
- **Exact program wording:**
  > “Хроматическое число плоскости при всюду плотных цветовых классах.”
- **Variant warning:** A conference-program title is not evidence of a finite graph vertex record; no <509 claim appears in the public program.
- **Verdict:** **Unclear** — relevant conference lead, no count claim.

### 19. Math-Net/Russian expository background: Soifer, “Хроматическое число плоскости: его прошлое, настоящее и будущее” (2004)

- **URL:** [Math-Net author/publication page](https://www.mathnet.ru/php/person.phtml?option_lang=eng&personid=22781)
- **Accessed:** 2026-07-24
- **What it says:** Historical exposition predating the 2018 breakthrough; useful for the classical problem but cannot contain a post-2018 <509 record.
- **Verdict:** **No** — historical/background only.

## Part B — Worldwide theses and repositories, 2019–2026

### 20. Warsaw University of Technology, “Lower bound on chromatic number of the plane” (MSc, 2021)

- **URL:** https://repo.pw.edu.pl/info/master/WUTbb7da29f360747afab3d046a7811edf0/
- **Accessed:** 2026-07-24
- **What it says:** Presents de Grey's proof, discusses Exoo–Ismailescu, verifies vertex counts with R, and gives smaller non-4-colorable subgraphs. Its smallest 5-chromatic graph is 529 vertices.
- **Exact repository description:**
  > “The smallest graph with chromatic number equal to 5 introduced in this work has 529 vertices.”
- **Verdict:** **No** — 529, not <509.

### 21. Ágoston, “Probabilistic formulation of the Hadwiger–Nelson problem” (ELTE master's thesis, 2019; public arXiv version 2021)

- **URLs:** [arXiv](https://arxiv.org/abs/2112.07665), [DOI landing page](https://doi.org/10.48550/arxiv.2112.07665), [public text mirror](https://docslib.org/doc/8125090/on-the-computational-complexity-of-degenerate-unit-distance)
- **Accessed:** 2026-07-24
- **What it says:** Master's thesis on unit-distance graphs, the plane, and the probabilistic formulation; develops lower bounds on the **order of non-k-colorable graphs**. It is not a claim of a new smaller 5-chromatic plane graph.
- **Exact thesis-structure evidence:** Chapters include “The chromatic number of the plane,” “The probabilistic formulation,” and “Related problems — Spheres / Other dimensions.”
- **Variant warning:** Lower bounds on the minimum possible order of non-4/non-5-colorable graphs are not constructions of graphs below 509.
- **Verdict:** **Unclear** — relevant thesis, but no <509 plane graph claim located.

### 22. Ágoston, “Coloring Geometric Graphs and Hypergraphs” (ELTE thesis record, 2023)

- **URL:** https://doi.org/10.15476/elte.2022.266
- **Accessed:** 2026-07-24
- **What it says:** Broad thesis on geometric graph/hypergraph coloring; mentions Hadwiger–Nelson as context but does not report a sub-509 plane graph in the public abstract/metadata.
- **Verdict:** **Unclear** — no relevant vertex-record claim.

### 23. Rudawski, “The Hadwiger–Nelson problem” (bachelor thesis, 2019; listed in CV)

- **URL:** https://jplab.github.io/pdfs/CV.pdf
- **Accessed:** 2026-07-24
- **What it says:** A CV lists a 2019 bachelor thesis with this title. The CV does not expose the thesis text or any graph count.
- **Verdict:** **Unclear** — no public count claim in the located source.

### 24. Bellitto, “Walks, Transitions and Geometric Distances in Graphs” (thesis)

- **URL:** https://perso.lip6.fr/Thomas.Bellitto/thesis.pdf
- **Accessed:** 2026-07-24
- **What it says:** Includes a chapter on geometric distances and distance-avoiding sets; discusses unit-distance graphs/Hadwiger–Nelson as background, not a smaller finite 5-chromatic plane construction.
- **Verdict:** **Unclear** — no <509 claim located.

### 25. TU Delft repository: “Complete positivity and distance-avoiding sets”

- **URL:** https://repository.tudelft.nl/record/uuid:145db990-90bc-4519-8f5c-15f31050f99f
- **Accessed:** 2026-07-24
- **What it says:** Semidefinite/convex-optimization work on distance-avoiding sets, spheres, and Euclidean spaces. It is not a finite 5-chromatic graph record.
- **Verdict:** **Unclear** — related analytic variant, no <509 plane graph claim.

### 26. TU Delft repository: “Connectedness of Unit Distance Subgraphs Induced by Closed Convex Sets”

- **URL:** https://repository.tudelft.nl/record/uuid:0742e42f-43cf-41c9-8b27-98d4fb1734e5
- **Accessed:** 2026-07-24
- **What it says:** Studies connectivity of unit-distance graphs induced by closed convex subsets; cites the plane chromatic problem as context, with no finite 5-chromatic graph minimization claim.
- **Verdict:** **Unclear** — related but not a record source.

### 27. CMU SAT/proof materials (not theses, included because the requested CMU/Heule check surfaced them)

- **URLs:** [SAT4Math CNP proofs](https://www.cs.cmu.edu/~mheule/MSS/03-CNP-proofs.pdf), [LPAR23 paper](https://www.cs.cmu.edu/~mheule/publications/LPAR23-CNP.pdf)
- **Accessed:** 2026-07-24
- **What they say:** CMU materials report the 510-vertex Heule construction and later cite the 509-vertex Parts record. No CMU thesis reporting <509 was found.
- **Verdict:** **No** — public CMU material supports 509 as the record, not a smaller graph.

## Explicit exclusions / common confusions

- **Spheres:** Voronov–Neopryatnaya–Dergachev's 372-vertex and 972-vertex graphs are on circumspheres. They do not answer the ordinary-plane question.
- **Higher dimensions:** Rubanov's 5-chromatic R^3 graph and Raigorodskii-school asymptotic distance-graph results are not plane constructions.
- **Rational/algebraic plane:** CyberLeninka's rational/affine-rational analogues concern restricted coordinate fields or rational chromatic parameters; they are not automatically graphs in the full real plane and do not report <509 here.
- **Map-type/measurable/fractional colorings:** Sokolov–Voronov map colorings and probabilistic/fractional chromatic-number work concern variants of the coloring problem, not finite ordinary-plane 5-chromatic graph vertex records.
- **6-chromatic/two-distance graphs:** Parts's separate two-distance/6-chromatic work is outside the requested 5-chromatic unit-distance scope.
- **Order lower bounds:** A theorem saying every non-k-colorable graph must have at least N vertices is a lower bound on possible order, not a construction of a graph with N vertices. Conversely, a thesis describing a 529-vertex graph does not beat 509.

## Search assessment

I searched the requested Russian terms and author cluster through Math-Net, arXiv, CyberLeninka, Istina, general web indexing, Russian conference/program pages, and repository metadata; and searched worldwide thesis/repository terms including Hadwiger–Nelson thesis, chromatic number of the plane thesis, ProQuest-like indexed results, TU Delft, DiVA, CMU/Heule, ELTE, and Warsaw. The publicly indexed Russian-school sources located either (i) concern general/high-dimensional/rational/spherical distance graphs, (ii) concern map/layer variants, or (iii) report plane examples much larger than 509. The thesis sources located report 529 or provide background/order bounds, not <509.

## Conclusion

**Answer for the stated scope: No source found claims a 5-chromatic unit-distance graph in the ordinary Euclidean plane with fewer than 509 vertices.** The best documented public result remains Parts's 509-vertex, 2442-edge graph, and the exact sentence “The record-holder is a graph with 509 vertices and 2442 edges” is the strongest direct record statement located.

## Part C

Access date for every source in this section: **2026-07-24**. This section records the targeted follow-up search on Soifer's second edition, House of Graphs, and non-journal/public web sources. “No” below means that the source does not claim a sub-509 ordinary-plane 5-chromatic unit-distance graph; it does not mean that the source proves that no unpublished graph exists.

### C1. Alexander Soifer, *The New Mathematical Coloring Book*, second edition (Springer, 2024)

#### Springer book page: metadata, description, and complete chapter list

- **URL:** https://link.springer.com/book/10.1007/978-1-0716-3597-1
- **Accessed:** 2026-07-24
- **What it says:** The Springer page identifies the book as the 2024 second edition and labels the table of contents “Table of contents (68 chapters).” The page's visible descriptive text says:

  > “(TNMCB) includes striking results of the past 15-year renaissance that produced new approaches, advances, and solutions to problems from the first edition. A large part of the new edition ‘Ask what your computer can do for you,’ presents the recent breakthrough by Aubrey de Grey and works by Marijn Heule, Jaan Parts, Geoffrey Exoo, and Dan Ismailescu.”

  The complete Springer chapter list is:

  1. A Story of Colored Polygons and Arithmetic Progressions
  2. Chromatic Number of the Plane: The Problem
  3. Chromatic Number of the Plane: A Historical Essay
  4. Polychromatic Number of the Plane and Results Near the Lower Bound
  5. De Bruijn–Erdős Reduction to Finite Sets and Results Near the Lower Bound
  6. Polychromatic Number of the Plane and Results Near the Upper Bound
  7. Continuum of 6-Colorings of the Plane
  8. Chromatic Number of the Plane in Special Circumstances
  9. Measurable Chromatic Number of the Plane
  10. Coloring in Space
  11. Rational Coloring
  12. Chromatic Number of a Graph
  13. Dimension of a Graph
  14. Embedding 4-Chromatic Graphs in the Plane
  15. Embedding World Series
  16. Exoo–Ismailescu: The Final Word on Problem 15.4
  17. Edge Chromatic Number of a Graph
  18. Carsten Thomassen’s 7-Color Theorem
  19. How the Four-Color Conjecture Was Born
  20. A Victorian Comedy of Errors and Colorful Progress
  21. Kempe–Heawood’s Five-Color Theorem and Tait’s Equivalence
  22. The Four-Color Theorem
  23. The Great Debate
  24. How Does One Color Infinite Maps? A Bagatelle
  25. Chromatic Number of the Plane Meets Map Coloring: Townsend–Woodall’s 5-Color Theorem
  26. Paul Erdős
  27. De Bruijn–Erdős’ Theorem and Its History
  28. Nicolaas Govert de Bruijn
  29. Edge-Colored Graphs: Ramsey and Folkman Numbers
  30. From Pigeonhole Principle to Ramsey Principle
  31. The Happy End Problem
  32. The Man Behind the Theory: Frank Plumpton Ramsey
  33. Ramsey Theory Before Ramsey: Hilbert’s Theorem
  34. Ramsey Theory Before Ramsey: Schur’s Coloring Solution of a Colored Problem and Its Generalizations
  35. Ramsey Theory Before Ramsey: Van der Waerden Tells the Story of Creation
  36. A Japanese Insight into Baudet–Schur–Van der Waerden’s Theorem
  37. Whose Conjecture Did Van der Waerden Prove? Two Lives Between Two Wars: Issai Schur and Pierre Joseph Henry Baudet
  38. Monochromatic Arithmetic Progressions or Life After Van der Waerden’ Proof
  39. In Search of Van der Waerden: The Early Life
  40. In Search of Van der Waerden: The Nazi Leipzig, 1933–1945
  41. In Search of Van der Waerden: Amsterdam, Year 1945
  42. In Search of Van der Waerden: The Unsettling Years, 1946–1951
  43. How the Monochromatic AP Theorem Became Classic: Khinchin and Lukomskaya
  44. Monochromatic Polygons in a 2-Colored Plane
  45. 3-Colored Plane, 2-Colored Space, and Ramsey Sets
  46. The Gallai Theorem
  47. O’Donnell Earns His Doctorate
  48. Applications of the Baudet–Schur–Van der Waerden
  49. Applications of the Bergelson–Leibman and the Mordell–Faltings Theorems
  50. Solution of an Erdős Problem: The O’Donnell Theorem
  51. Aubrey D.N.J. de Grey’s Breakthrough
  52. De Grey’s Construction
  53. Marienus Johannes Hendrikus “Marijn” Heule
  54. Can We Reach Chromatic 5 Without Mosers Spindles?
  55. Triangle-Free 5-Chromatic Unit Distance Graphs
  56. Jaan Parts’ Current World Record
  57. A Stroke of Brilliance: Matthew Huddleston’s Proof
  58. Geoffrey Exoo and Dan Ismailescu, or 2 Men for 2 Forbidden Distances
  59. Jaan Parts on Two-Distance 6-Coloring
  60. Forbidden Odds, Binaries, and Factorials
  61. 7- and 8-Chromatic Two-Distance Graphs
  62. What If We Had No Choice?
  63. AfterMath and the Shelah–Soifer Class of Graphs
  64. A Glimpse into the Future: Chromatic Number of the Plane, Theorems, and Conjectures
  65. What Do the Founding Set Theorists Think About the Foundations?
  66. So, What Does It All Mean?
  67. Imagining the Real or Realizing the Imaginary: Platonism Versus Imaginism
  68. Two Celebrated Problems

- **Plane/variant assessment:** Chapters 2–11 include the plane problem and variants such as measurable coloring, space, and rational coloring. Chapters 51–56 are the relevant finite unit-distance-graph sequence; Chapter 56 is explicitly the current-record chapter. Chapters 58–61 concern two-forbidden-distance or two-distance variants and must not be substituted for the ordinary unit-distance plane problem.
- **Verdict:** **No.** The page advertises the relevant historical and computational work but does not claim a graph below 509.

#### Chapter 56: “Jaan Parts’ Current World Record”

- **URLs:** Springer chapter DOI https://doi.org/10.1007/978-1-0716-3597-1_56; Springer chapter landing page https://link.springer.com/chapter/10.1007/978-1-0716-3597-1_56; indexed chapter abstract https://ideas.repec.org/h/spr/sprchp/978-1-0716-3597-1_56.html
- **Accessed:** 2026-07-24
- **What it says:** The indexed abstract identifies this as Chapter 56 and gives the exact record statement:

  > “Parts’ record holder (in terms of the smallest number of vertices) is a graph on 509 vertices with 2442 edges (visualized in Fig. 56.1), created using a large subgraph on 374 vertices with 1860 edges (visualized in Fig. 56.2), and a small subgraph on 136 vertices with 564 edges (visualized in Fig. 56.3).”

  The same abstract says it concerns “5-chromatic unit-distance graphs.”
- **Plane/variant assessment:** This is the ordinary finite 5-chromatic unit-distance-graph record associated with Parts’s plane construction, not the 16-/31-vertex two-distance material discussed elsewhere in the book. The 509 graph is not claimed to have fewer than 509 vertices.
- **Verdict:** **No.** This is one of the clearest post-2020 public statements confirming 509 as the smallest-by-vertices record.

#### Gasarch review of the second edition

- **URLs:** https://algoplexity.com/~ntran/SIGACT/articles/br-dec-24-soifer-gasarch.pdf; archive issue https://algoplexity.com/~ntran/SIGACT/archives/55-4.pdf; review index https://www.cs.umd.edu/~gasarch/bookrev.html
- **Accessed:** 2026-07-24
- **What it says:** William Gasarch’s SIGACT News review identifies the book and compares the editions:

  > “The New Mathematical Coloring Book: Mathematics of Coloring and the Colorful Life of its Creators Second edition by Alexander Soifer”

  > “In 2024 Alexander Soifer published The New Mathematical Coloring Book. I will refer to this book by TNMCB. TNMCB is around 900 oversized pages.”

  In its discussion of the relevant historical material, the review states:

  > “(a) In 2018 Marijn Heule had a series of results culminating in a 5-chromatic unit-distance graph on 510 vertices. (b) In 2020 Jaan Parts obtained a 5-chromatic unit-distance graph on 509 vertices.”

  It also says:

  > “The two graphs have girth 3. Soifer asks in the book for the smallest 5-chromatic unit-distance graph of girth 4.”

- **Plane/variant assessment:** The quoted 510 and 509 statements concern finite 5-chromatic unit-distance graphs used for the plane lower bound. The girth-4 question is an additional extremal question, not a claim that a smaller ordinary-plane graph exists.
- **Verdict:** **No.** Gasarch reports 509, not a sub-509 construction.

#### Errata/addenda

- **URL:** https://page.mi.fu-berlin.de/rote/Kram/soifer-errata.pdf
- **Accessed:** 2026-07-24
- **What it says:** The errata document identifies the work as:

  > “Alexander Soifer: The New Mathematical Coloring Book. Mathematics of Coloring and the Colorful Life of Its Creators, Second Edition. Springer 2024, xlvii+841 pages, doi:10.1007/978-1-0716-3597-1.”

  The errata is a correction list for the book; the publicly indexed material located contains no claim of a sub-509 5-chromatic unit-distance graph and no replacement record below 509.
- **Plane/variant assessment:** Bibliographic/correction material, not a new graph construction.
- **Verdict:** **Unclear** as a record source, but **no sub-509 claim located**.

#### Soifer conference abstracts/talk material

- **URLs:** https://www.math.fau.edu/combinatorics/abstracts/soifer55-1.pdf and https://www.math.fau.edu/combinatorics/abstracts/soifer56.pdf
- **Accessed:** 2026-07-24
- **What they say:** The abstracts describe the 2024 book and the progression from de Grey to Heule to Parts. The earlier abstract states:

  > “In 2018. Aubrey de Grey, a Cambridge-educated biologist, achieves the first breakthrough in the problem of finding chromatic number of the plane by constructing the first ever 5-chromatic unit-distance graph. He is followed by the virtuoso Dutch American computer scientist Marijn Heule, an Invited Speaker at this Conference, who substantially reduces the order of the smallest 5-chromatic unit-distance graph. The Russian microchip designer Jaan Parts further reduces the size of the smallest known 5-chromatic unit distance graph.”

  The later abstract discusses new and old plane-coloring questions and says:

  > “Much of this material – but not all – in contained in the 2024, Springer New York book ‘The New Mathematical Coloring Book: Mathematics of Coloring and the Colorful Life of Its Creators.’”

  Neither abstract supplies a number below 509; the relevant number is supplied explicitly by Chapter 56 and Gasarch above.
- **Plane/variant assessment:** The 2024/2026-style abstract material includes six-coloring and other forbidden-distance variants as well as the ordinary plane problem. It does not announce a new sub-509 ordinary-plane graph.
- **Verdict:** **No** for any claim of <509; **Unclear** as a standalone numerical record source because the abstracts do not give the count.

### C2. House of Graphs

- **URLs:** https://houseofgraphs.org/graphs/51434 (Parts Graph 16); https://houseofgraphs.org/graphs/51435 (Parts Graph 199); https://houseofgraphs.org/graphs/51436 (Parts Graph 31); site search/index evidence was cross-checked against https://mathworld.wolfram.com/PartsGraphs.html
- **Accessed:** 2026-07-24
- **What the entries say:**

  **Graph 51434 — Parts Graph 16.** The House of Graphs result identifies “Name: Parts Graph 16” and reports 16 vertices, 56 edges, chromatic number 5, and “Planar | No.” Thus it is an abstract 5-chromatic graph in the database, not an ordinary-plane unit-distance embedding. Its small order cannot answer the requested question.

  **Graph 51436 — Parts Graph 31.** The entry identifies “Name: Parts Graph 31” and reports 31 vertices, 113 edges, chromatic number 6, and “Planar | No.” This is a 6-chromatic two-distance-type Parts graph, not a 5-chromatic ordinary-plane unit-distance graph.

  **Graph 51435 — Parts Graph 199.** The entry identifies “Name: Parts Graph 199.” The associated Parts/MathWorld material places the 199-vertex graph among additional Parts graphs associated with the two-distance work, distinct from the 509-vertex 5-chromatic unit-distance record sequence. The House of Graphs page is a graph-database record, not a proof that the graph is a plane 5-chromatic unit-distance graph.

  MathWorld’s Parts Graphs summary explicitly distinguishes the record sequence from the 16/31/199 entries:

  > “The Parts graphs are a set of unit-distance graphs with chromatic number five derived by Jaan Parts in 2019-2020 (Parts 2020a).”

  It lists the 5-chromatic record sequence through 509 vertices and then says:

  > “Additional graphs on 16, 31, and 199 nodes are also associated with Parts (2020b). The 31-node graph is a small 6-chromatic graph with exactly two edge lengths (1 and the golden ratio).”

- **Plane/variant assessment:** House of Graphs stores abstract graph invariants (including chromatic number and planarity) and does not, by itself, establish an exact Euclidean unit-distance realization in the ordinary plane. In particular, the 16-vertex entry is nonplanar despite its chromatic number 5; the 31-vertex entry is 6-chromatic and two-distance. These are not sub-509 answers to the plane 5-chromatic unit-distance question. The ordinary-plane 5-chromatic record sequence remains 553, 529, 525, 510, and 509, as summarized by MathWorld and Parts’s paper.
- **Verdict:** **No.** No House of Graphs entry located is a 5-chromatic unit-distance graph embedded in the ordinary plane with fewer than 509 vertices. The apparent small numbers are abstract/nonplanar or two-distance/6-chromatic variants.

- **de Grey entry:** https://houseofgraphs.org/graphs/51366 is identified in search results as “De Grey Graph 60.” The associated MathWorld description states that the 59- and 60-vertex de Grey graphs have chromatic number 6 and are unit-distance in 3 dimensions but not 2 dimensions. Therefore they are not ordinary-plane 5-chromatic graphs. **Verdict: No.**
- **Heule search:** Searches for “Heule” on House of Graphs did not locate a qualifying named 5-chromatic ordinary-plane graph below 509. The Heule constructions are documented in the public SAT repository and papers, but the relevant 510 graph is not a smaller House of Graphs plane record. **Verdict: No qualifying sub-509 claim located.**

### C3. Public web, Polymath, GitHub, Q&A, and Wikipedia sweep

#### Polymath16 wiki and later thread

- **URLs:** https://michaelnielsen.org/polymath/index.php?title=Hadwiger-Nelson_problem; mirror https://asone.ai/polymath/index.php?title=Hadwiger-Nelson_problem; later thread https://dustingmixon.wordpress.com/2021/02/01/polymath16-seventeenth-thread-declaring-victory/
- **Accessed:** 2026-07-24
- **What they say:** The 2021 “declaring victory” thread states:

  > “The record for the smallest graph was progressively improved, including several times by Marijn Heule, and the present record is 509, achieved by Jaan Parts.”

  Earlier Polymath threads record the historical sequence, including:

  > “The smallest known 5-chromatic unit distance graph has 510 vertices and 2508 edges.”

  and:

  > “The smallest known 5-chromatic unit distance graph has 529 vertices and 2630 edges.”

- **Plane/variant assessment:** These statements concern finite 5-chromatic unit-distance graphs for the plane problem. Other Polymath material on higher-dimensional graphs, forbidden distance intervals, spheres, and two-distance graphs is not interchangeable with this record.
- **Verdict:** **No.** The later thread explicitly gives 509 as the present record.

#### Formalization GitHub repository

- **URL:** https://github.com/vasnesterov/HadwigerNelson
- **Accessed:** 2026-07-24
- **What it says:** The README says:

  > “Specifically, we verify that the 510-vertex graph constructed by Marjin Heule is not 4-colorable.”

  It also says the smallest known Parts graph is beyond the current formalization capabilities and lists as a future goal:

  > “Prove that the 509-vertex Parts graph is a non-4-colorable unit distance graph.”

- **Plane/variant assessment:** This is a formal verification of the 510-vertex Heule graph and a statement of a future formalization target, not a claim that 510 is the best available graph. The README recognizes the 509-vertex Parts graph.
- **Verdict:** **No.** No sub-509 claim.

#### MathOverflow

- **URL:** https://mathoverflow.net/questions/472444/bottleneck-for-the-search-of-a-graph-of-chromatic-number-6
- **Accessed:** 2026-07-24
- **What it says:** The question begins:

  > “Since de Grey's discovery of a planar unit distance graph of chromatic number 5 having 1581 vertices, smaller ones have been found, the smallest with 509 vertices (per wikipedia).”

  It then asks:

  > “Q1: is 509 indeed the current record?”

  The page is primarily about the bottleneck for finding a 6-chromatic graph, so the question’s wording is evidence of the public 509 understanding rather than a new construction.
- **Plane/variant assessment:** The quoted sentence explicitly says “planar unit distance graph of chromatic number 5.” The subsequent topic is chromatic number 6, which is a different target.
- **Verdict:** **No.** It reports 509 and asks for confirmation; it does not claim <509.

#### Wikipedia article and edit-history source text

- **URL:** https://en.wikipedia.org/w/index.php?title=Hadwiger%E2%80%93Nelson_problem&action=raw (article); article page https://en.wikipedia.org/wiki/Hadwiger%E2%80%93Nelson_problem
- **Accessed:** 2026-07-24
- **What it says:** The current article source states:

  > “As of 2021, the smallest known unit distance graph with chromatic number 5 has 509 vertices.”

  The article defines the relevant graph as the unit-distance graph of the plane and cites the Polymath material. The accessible article text therefore supports 509, not a sub-509 graph. The revision/history trail did not reveal a later 2023–2026 claim of a smaller ordinary-plane graph.
- **Plane/variant assessment:** The article’s surrounding discussion is the ordinary Euclidean-plane Hadwiger–Nelson problem. It should not be read as covering higher-dimensional, two-distance, measurable, or rational variants.
- **Verdict:** **No.** The exact article sentence gives 509.

#### de Grey / Heule public repositories and pages

- **URLs:** https://github.com/marijnheule/CNP-SAT; https://github.com/marijnheule; https://ar5iv.labs.arxiv.org/html/1804.02385; https://github.com/vasnesterov/HadwigerNelson
- **Accessed:** 2026-07-24
- **What they say:** The de Grey paper states:

  > “The smallest such graph that we have so far discovered has 1581 vertices.”

  Heule’s public CNP-SAT repository is a computational repository for unit-distance graphs; the formalization repository above explicitly records the 510-vertex Heule proof and the 509-vertex Parts graph as the smaller target. No 2023–2026 de Grey or Heule page located claims a 5-chromatic ordinary-plane unit-distance graph below 509.
- **Plane/variant assessment:** de Grey’s 1581 graph and Heule’s 510 graph are ordinary-plane finite unit-distance constructions; no smaller author-page claim was found. The separate 2026 de Grey 61-vertex result indexed in MathWorld is a **triangle-free** 5-chromatic graph and is not evidence of a sub-509 ordinary-plane graph unless its geometric ambient space and unit-distance realization are checked; the located public descriptions did not establish that it supersedes the 509 plane record, so it is excluded from the answer.
- **Verdict:** **No sub-509 claim located.**

#### Other public sources searched

- **Philip Gibbs / viXra/blog:** Searches for 2023–2026 material found no accessible exact sentence claiming a sub-509 ordinary-plane 5-chromatic unit-distance graph. **Verdict: Unclear/no claim located.**
- **Terence Tao blog comments:** Searches found no accessible exact 2023–2026 record statement claiming <509. **Verdict: Unclear/no claim located.**
- **Math StackExchange:** The accessible answers found discuss the 2018 de Grey 1581-vertex result or measurable-coloring variants, not a later sub-509 construction. For example, one answer says:

  > “De Grey's graph has 1581 vertices.”

  URL: https://math.stackexchange.com/questions/2514507/hadwiger-nelson-problem-5-colors-needed-if-color-sets-are-lesbeauge-measureable (accessed 2026-07-24). This is historical and not a current-record claim. **Verdict: No sub-509 claim located.**
- **MathWorld current summary:** https://mathworld.wolfram.com/deGreyGraphs.html and https://mathworld.wolfram.com/PartsGraphs.html (accessed 2026-07-24). The de Grey page says:

  > “As of 2022, the smallest of these is the 509-vertex Parts graph (Parts 2020a).”

  The Parts page lists the 509/2442 record sequence and distinguishes the 16-, 31-, and 199-node associated graphs. **Verdict: No.**

## Part C summary

Across the Springer second edition and its Chapter 56 abstract, Gasarch’s 2024 SIGACT review, the errata, Soifer conference abstracts, House of Graphs, Polymath16’s later thread, the formalization GitHub repository, MathOverflow, Wikipedia’s article source, author repositories, and the searched blog/Q&A material, **no source was found claiming a 5-chromatic unit-distance graph embedded in the ordinary Euclidean plane with fewer than 509 vertices**.

The strongest new exact record statements are:

> “Parts’ record holder (in terms of the smallest number of vertices) is a graph on 509 vertices with 2442 edges…”

> “The record for the smallest graph was progressively improved, including several times by Marijn Heule, and the present record is 509, achieved by Jaan Parts.”

> “As of 2021, the smallest known unit distance graph with chromatic number 5 has 509 vertices.”

These remain literature-search findings, not a proof that no private, unpublished, or undiscovered graph exists. The answer for the combined Part A–C scope is therefore: **No source found claims a sub-509 5-chromatic unit-distance graph in the ordinary plane.**

---

# Part D — Geombinatorics Quarterly: reconstructed tables of contents, vol. XXIX (2019/20) – XXXVI (2026)

Access date for everything in Part D: **2026-07-24**.

Two independent reconstructions were cross-checked:

1. **Publisher site (authoritative, per-issue TOCs):** https://geombina.uccs.edu/past-issues — volume pages
   https://geombina.uccs.edu/past-issues/volume-xxix … /volume-xxxvi, plus the author index
   https://geombina.uccs.edu/author-index (e.g. https://geombina.uccs.edu/author-index/jaan-parts).
2. **zbMATH Open API** (free): `https://api.zbmath.org/v1/document/_search?search_string=so:Geombinatorics & py:2019-2026`
   → 118 indexed articles, volumes 28(3)–35(4). Used to obtain review/summary texts.

The publisher's own TOCs cover **Vol. XXIX no. 1 (July 2019) through Vol. XXXVI no. 1 (July 2026)** — i.e. the journal is fully
reconstructed through the latest published issue. Vol. XXXVI no. 1 (July 2026) contains nothing on unit-distance graphs.

## D1. Every Geombinatorics article XXIX–XXXVI touching unit-distance graphs / chromatic number of the plane

| Vol (issue), date | Pages | Authors | Title | Setting | Claims a plane 5-chromatic UDG < 509? |
|---|---|---|---|---|---|
| XXIX (3), Jan 2020 | 97–103 | Exoo, Ismailescu | A 6-chromatic two-distance graph in the plane | plane, **two-distance** | No (variant) |
| XXIX (3), Jan 2020 | 111–115 | Parts | A small 6-chromatic two-distance graph in the plane | plane, **two-distance** | No (variant; this is the source of the 16-/31-vertex "Parts graphs") |
| **XXIX (4), Apr 2020** | **137–166** | **Parts** | **Graph minimization … 5-chromatic unit-distance graphs in the plane** | **plane, unit-distance** | **No — this IS the 509 record** |
| XXX (1), Jul 2020 | 5–13 | de Grey | A small 6-chromatic unit-distance graph in R^3 | **R^3** | No |
| XXX (1), Jul 2020 | 25–39 | Parts | What percent of the plane can be properly 5- and 6-colored? | plane, tilings / order lower bounds | No (gives v6>24, v7>6992 type bounds) |
| XXX (2), Oct 2020 | 77–102 | Parts | The chromatic number of the plane is at least 5 — a human-verifiable proof | plane, unit-distance | No (verifiability, not minimization) |
| XXX (3), Jan 2021 | 138–151 | Sirgedas | The surface of a sufficiently large sphere has chromatic number at most 7 | **sphere** | No |
| XXX (4), Apr 2021 | 177–189 | Parts | On upper bounds for the multi-fold chromatic numbers of the plane | plane, **multi-fold** | No |
| XXX (4), Apr 2021 | 190–201 | D.H.J. Polymath | On the chromatic number of circular disks and infinite strips in the plane | plane subsets | No |
| XXXI (2), Oct 2021 | 49–67 | Exoo, Fisher, Ismailescu | The chromatic number of the Minkowski plane — the regular polygon case | **Minkowski (non-Euclidean) plane** | No |
| XXXI (2), Oct 2021 | 68–76 | Heule | Odd-distance virtual edges in unit-distance graphs | plane, unit-distance (technique) | No count claim below 509 |
| XXXI (3), Jan 2022 | 110–115 | de Grey, Haugstrup | Two small 6-chromatic unit-distance graphs in R^3 | **R^3** | No |
| XXXI (3), Jan 2022 | 124–137 | Parts | A 6-chromatic odd-distance graph in the plane | plane, **odd-distance** | No (variant) |
| XXXI (4), Apr 2022 | 156 | Conway, de Grey, Parts, Soifer | Is there a better visualization of Coulson's 15-colouring of 3-space…? | **R^3 colouring** | No |
| XXXI (4), Apr 2022 | 189–195 | Parts | On the plane and its coloring | plane, colouring (χ=7 "in a certain sense") | No |
| XXXII (1), Jul 2022 | 5–28 | Gwyn, Stavrianos | A finite graph approach to the probabilistic Hadwiger-Nelson problem | plane, **lower bounds on order** (e5≥98, v5≥22) | No (lower bound, not a construction) |
| XXXII (1), Jul 2022 | 29–39 | Jones, Kraus | On the Babai and upper chromatic numbers of R^n with non-Euclidean distance | R^n, non-Euclidean | No |
| XXXII (2), Oct 2022 | 57–71 | de Grey, Parts | Tiling the plane with hexagons: improved separations for k-colourings | plane tilings | No |
| **XXXII (2), Oct 2022** | **72–74** | **de Grey, Parts** | **On lower bounds of the order of k-chromatic unit distance graphs** | **plane, unit-distance** | **No — explicitly restates v5 ≤ 509 as the upper bound (see quote below)** |
| XXXII (4), Apr 2023 | 145–158 | Exoo, Ismailescu | A 5-chromatic same-distance graph in the hyperbolic plane | **hyperbolic plane** | No |
| XXXII (4), Apr 2023 | 159–185 | Parts | More certainty in coloring the plane with a forbidden distance interval | plane, **forbidden interval** | No (variant) |
| XXXIII (1), Jul 2023 | 14–38 | Martinez-Figueroa | Topology and chromatic number of random ε-distance graphs on spheres | **spheres, random** | No |
| XXXIII (3), Jan 2024 | 97–106 | Fiscus, Myzelev, Zhang | A new class of geometrically defined hypergraphs arising from the Hadwiger-Nelson problem | plane, hypergraphs | No |
| XXXIV (1), Jul 2024 | 11–19 | Gasarch | Review of Soifer, *The New Mathematical Coloring Book*, 2nd ed. | review | No — states "In 2020 Jaan Parts obtained a 5-chromatic unit-distance graph on 509 vertices" |
| XXXIV (1), Jul 2024 | 20–29 | Mundinger, Pokutta, Spiegel, Zimmer | Extending the continuum of six-colorings | plane, **6-colorings / two distances** | No |
| XXXIV (1), Jul 2024 | 30–36 | Soifer | New open problems and conjectures in *The New Mathematical Coloring Book* | plane, open problems | No |
| XXXIV (3), Jan 2025 | 113–115 | Soifer | New results and new open problems and conjectures related to the chromatic number of the plane problem | plane, survey of open problems | No — zbMATH review (Zbl 1569.05108) describes only conjectures on 6-colorings, 7-chromatic two-distance graphs and χ(R^n); no new smallest-graph claim |
| XXXIV (3), Jan 2025 | 116–119 | Thürey | More than 'the chromatic number of the plane' | plane, generalisation | No |
| XXXV (3), Jan 2026 | 102–110 | Haugstrup | A tetrahedron-free 6-chromatic unit-distance graph in three-dimensional space | **R^3** | No |
| XXXV (3), Jan 2026 | 111–118 | de Grey | A 5-chromatic, triangle-free unit-distance graph in R^3 with 61 vertices | **R^3** (girth 4) | No — 61 vertices is an **R^3** result, not the plane |
| XXXV (4), Apr 2026 | 155–159 | Voloshin | Note about a gap in coloring the plane | plane, colouring note | No (zbMATH Zbl None; short note, no construction) |
| XXXVI (1), Jul 2026 | 24–37 | Soifer | Fifty years anniversary of the four-color theorem | history | No |

Everything else in volumes XXIX–XXXVI is matchstick graphs, tilings, polyiamonds/polyominoes, crossing numbers,
Ramsey-type problems, obituaries, essays and book reviews — none of which bears on the question.

**Jaan Parts' Geombinatorics author page** (https://geombina.uccs.edu/author-index/jaan-parts) lists **nothing after 2023**;
his last item is XXXII(4) 2023. So no later Parts paper in the journal supersedes the 509 graph.

## D2. The decisive Geombinatorics quote (de Grey & Parts, the two people who hold/held the record)

de Grey & Parts, *On lower bounds of the order of k-chromatic unit distance graphs*, Geombinatorics **32**/2 (2022) 72–74;
free full text at https://arxiv.org/abs/2303.14714 (PDF https://arxiv.org/pdf/2303.14714v1, accessed 2026-07-24):

> "It is known that v3 = 3 and v4 = 7 (provided by the unit triangle and the Moser graph). For k ≥ 5, exact values of vk
> are not known. Initial lower bounds v5 > 12, v7 > 6197 were obtained by Dan Pritikin [7]. **For k = 5, the finite upper
> bounds are v5 ≤ 509, e5 ≤ 2406, see [5].**"

with footnote 2:

> "In [5] the corresponding 509-vertex graph has 2442 edges, but is not edge-critical, which allows us to reduce e5.
> We were able to discard 36 edges, but we didn't perform an exhaustive search, so further improvements are possible."

Two consequences: (i) as of March 2023 the record-holders themselves state 509 as the best known upper bound on the
minimum order; (ii) the **edge** count has been improved to ≤ 2406 (36 edges removed) while the **vertex** count 509 stands.
The same note gives the best published lower bound in that line: **v5 ≥ 28** ("As a result, we get the bounds:
e5 ≥ 99, v5 ≥ 28, e6 ≥ 182, v6 ≥ 42"). Note the caveat that the prompt's "2442 edges" is Parts' original figure.

## D3. Independent arXiv / citation sweep (accessed 2026-07-24)

arXiv API queries `all:"unit distance graph"`, `all:"chromatic number of the plane"`, `all:"Hadwiger-Nelson"`
(80 most recent hits each, back to 2004) and the full citation list of arXiv:2010.12665 via the Semantic Scholar API
(https://api.semanticscholar.org/graph/v1/paper/arXiv:2010.12665/citations, 18 citing works). No hit constructs a plane
5-chromatic unit-distance graph below 509. The near-misses that must not be confused with it:

- **Voronov, Neopryatnaya, Dergachev**, arXiv:2106.11824, Discrete Math. 345(12) 113106 (2022):
  "A series of 5-chromatic unit distance graphs on **64513 vertices** embedded into the plane is constructed… the
  5-chromatic unit distance graph on **372 vertices** embedded into the **circumsphere of an icosahedron**…" — the small
  numbers are on **spheres**; the plane number is 64513 (their point is Moser-spindle-freeness, not size).
- **de Grey**, Geombinatorics 35(3) 2026: a **61-vertex** 5-chromatic triangle-free UDG **in R^3**.
- **Mundinger–Pokutta–Spiegel–Zimmer**, arXiv:2501.18527 (ICML 2025), "Neural discovery in mathematics": improves the
  **off-diagonal 6-colouring** variant, not the 5-chromatic graph size.
- **Matolcsi–Ruzsa–Varga–Zsámboki** arXiv:2311.10069 and arXiv:2606.28157 (2026): **fractional** chromatic number of the plane / independence ratio; the 27-vertex Moser-lattice graph there is a *fractional* object, not a 5-chromatic UDG.
- **Aggarwal**, MIT PRIMES 2025, *Computer-aided discovery of extremal unit-distance graphs & quantum contextuality*,
  https://math.mit.edu/research/highschool/primes/materials/2025/Aggarwal.pdf (accessed 2026-07-24) — a 2025 independent
  restatement: "In 2022, Jaan Parts discovered the current record, a unit-distance graph with chromatic number 5 on only
  **509 vertices** [23]." (That paper targets edge-density/Erdős unit-distance extremal problems, not χ.)

## D4. MathWorld cross-check (Weisstein, accessed 2026-07-24)

- https://mathworld.wolfram.com/PartsGraphs.html — record table: 553/2840, 529/2630, 525/2605, 510/2508, 510/2502,
  **509/2442** (last, "prior to Mar. 7, 2020"). And, crucially for the House of Graphs entries:
  "Additional graphs on **16, 31, and 199** nodes are also associated with Parts (2020b). The 31-node graph is a small
  **6-chromatic graph with exactly two edge lengths (1 and the golden ratio φ)**." → the tiny "Parts graphs" in
  House of Graphs are **two-distance**, not unit-distance; they are not counterexamples.
- https://mathworld.wolfram.com/MixonGraphs.html and https://mathworld.wolfram.com/deGreyGraphs.html —
  "As of 2022, the smallest of these is the **509-vertex Parts graph** (Parts 2020a)."
- https://mathworld.wolfram.com/HeuleGraphs.html — Heule sequence ending at 510/2504 (Aug. 8, 2019).

---

# Overall verdict (all scopes)

**No published or publicly available source states, or exhibits data for, a 5-chromatic unit-distance graph in the
Euclidean plane with fewer than 509 vertices.** The 509-vertex / 2442-edge graph of Jaan Parts
(Geombinatorics XXIX no. 4 (2020) 137–166; arXiv:2010.12665) remains the smallest, and is confirmed as such by
sources dated 2020 → 2026:

| Date | Source | Exact wording |
|---|---|---|
| 2021 | Polymath16 "declaring victory" thread | "the present record is 509, achieved by Jaan Parts" |
| Oct 2022 (arXiv Mar 2023) | de Grey & Parts, Geombinatorics 32/2 | "For k = 5, the finite upper bounds are v5 ≤ 509, e5 ≤ 2406" |
| 2023 | Oostema–Martins–Heule, LPAR-23 | "The current record is a graph with 509 vertices and 2 442 edges" |
| 2024 | Soifer, *The New Mathematical Coloring Book* 2nd ed., **Ch. 56 "Jaan Parts' Current World Record"** | "Parts' record holder (in terms of the smallest number of vertices) is a graph on 509 vertices with 2442 edges" |
| 2024 | Gasarch review, Geombinatorics 34(1) 11–19 | "In 2020 Jaan Parts obtained a 5-chromatic unit-distance graph on 509 vertices" |
| 2025 | Aggarwal, MIT PRIMES | "In 2022, Jaan Parts discovered the current record, a unit-distance graph with chromatic number 5 on only 509 vertices" |
| 2026 | Geombinatorics vols XXXIV–XXXVI TOCs; Parts' author page empty after 2023 | no later paper claims a smaller plane graph |

Two genuine refinements exist, neither of which reduces the vertex count:
- **edges**: 2442 → **≤ 2406** (de Grey & Parts 2022, 36 edges removed from Parts' graph; not exhaustively searched).
- **lower bound on the order**: v5 > 12 (Pritikin 1998) → v5 ≥ 22 (Gwyn–Stavrianos 2022) → **v5 ≥ 28** (de Grey–Parts 2022).
  So the true minimum order lies in [28, 509]; the interval is open.

This is a literature-search conclusion, not a proof that no unpublished graph exists.

## Things that look like counterexamples but are not

| Object | Vertices | Why it does not count |
|---|---|---|
| de Grey, Geombinatorics 35(3) (2026) | 61 | 5-chromatic, triangle-free, but in **R^3** |
| de Grey–Haugstrup / Haugstrup, R^3 6-chromatic | 47, 59, 60 | **R^3**, and 6-chromatic |
| Voronov–Neopryatnaya–Dergachev sphere graphs | 372, 972 | on **spheres** (icosahedron circumsphere), not the plane |
| Parts' two-distance graphs (Geombinatorics XXIX(3) 2020) = House of Graphs 51434/51435/51436 | 16, 31, 199 | **two distances** (1 and φ), not unit-distance |
| Matolcsi et al. Moser-lattice graph | 27 | **fractional/geometric fractional** chromatic number 4, not χ = 5 |
| Gwyn–Stavrianos, de Grey–Parts order bounds | 22, 28 | **lower bounds** on the minimum order — no such graph is exhibited |
| Warsaw MSc thesis (2021) | 529 | larger than 509 |
| Heule graphs | 510, 517, 529, … | larger than 509 |

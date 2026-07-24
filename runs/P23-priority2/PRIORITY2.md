# P23 — Priority check #2: is there ANY public 5-chromatic unit-distance graph in the plane with fewer than 509 vertices?

**Question.** Does any published or publicly available 5-chromatic unit-distance graph in the Euclidean
plane R^2 have **fewer than 509 vertices**? (509 vertices / 2442 edges, Jaan Parts, 2020, is the record we
knew of.)

**Answer (2026-07-24): No.** After the enumerated sweep below — arXiv (topic + author, 2020–2026),
Geombinatorics volumes XXIX–XXXVI, the full Polymath16 wiki (pages + revision histories) and all 17
Polymath16 research threads *including their comment archives*, Wikipedia + MathWorld (current text and
revision history), the complete citation graphs of Parts 2020 / de Grey 2018 / Heule 2018 / de Grey–Parts
2023, Russian-language sources (Raigorodskii school, MathNet, Cyberleninka, Istina), worldwide theses,
House of Graphs, GitHub/GitLab/Zenodo/OSF/figshare, and every public Dropbox/Google-Drive graph file
linked from the Polymath16 material — **no source claims, and no obtained data supports, a 5-chromatic
unit-distance graph in the plane with fewer than 509 vertices.** Parts' 509/2442 graph stands.

This is a **literature/data forensics** conclusion, not a theorem: it says nothing below 509 is *public*.
It is emphatically **not** a claim that 509 is minimal. The best published lower bound on the order of a
5-chromatic unit-distance graph is only `v_5 >= 28` (de Grey & Parts 2023), so the true minimum lies
somewhere in `[28, 509]`.

Evidence levels are labelled throughout:

| Label | Meaning |
|---|---|
| **claimed** | a source asserts a graph/property; we did not obtain the data |
| **data obtained** | we downloaded the actual vertex/edge file and counted it |
| **exactly verified** | exact algebraic coordinates, exact recomputation of the unit-distance edge set, and a SAT/UNSAT decision on 4-colorability with a checked certificate (see `VERIFICATION.md`) |

## Deliverables in this directory

| File | Content |
|---|---|
| `PRIORITY2.md` | this summary + the master source list |
| `FINDINGS-wiki-code.md` | Polymath16 wiki (pages/history/diffs), all 17 blog threads + comments, GitHub/GitLab/Zenodo/OSF/figshare, every linked graph file |
| `FINDINGS-citations.md` | citation-graph sweep: ~144 citing works of Parts 2020 / de Grey 2018 / Heule 2018 / de Grey–Parts 2023, each checked for an improved bound |
| `FINDINGS-geombinatorics-russian-theses.md` | Geombinatorics TOCs vol. XXIX–XXXVI (2019–2026), Russian-language sources, theses, House of Graphs |
| `VERIFICATION.md` | exact verification of the record and of every sub-509 candidate file we obtained |
| `data/` | the graph files actually downloaded (`.vtx`) + Parts' `graphs.txt` index |
| `verify-out/` | solver inputs/outputs and certificates for `VERIFICATION.md` |
| `sources/` | archived wiki/thread text corpora and a manifest of the code repositories crawled |

## The record chain (all public 5-chromatic plane constructions, none below 509)

| Vertices | Edges | Author | Source | Evidence level here |
|---|---|---|---|---|
| 20425 → 1581 | — | de Grey 2018 | [arXiv:1804.02385](https://arxiv.org/abs/1804.02385), Geombinatorics 28(1) 18–31 | claimed |
| 1585 → 1577 | — | Mixon 2018 | [blog](https://dustingmixon.wordpress.com/2018/04/10/the-chromatic-number-of-the-plane-is-at-least-5/) | claimed |
| 826 → 803 → 633 → 610 → 553 | 2720 | Heule 2018 | [arXiv:1805.12181](https://arxiv.org/abs/1805.12181), Geombinatorics 28 32–50 | data obtained (553) |
| 529 | 2670 | Heule 2019 | [arXiv:1907.00929](https://arxiv.org/abs/1907.00929) | data obtained |
| 525 / 517 / 510 | 2605 / 2579 / 2508 | Heule & Parts 2019–20 | Polymath16 wiki table + threads | data obtained (525, 517, 510 via Heule repo) |
| **509** | **2442** (→ `e_5 <= 2406`, non-edge-critical) | **Parts 2020** | [arXiv:2010.12665](https://arxiv.org/abs/2010.12665), Geombinatorics XXIX(4) 137–166 | **exactly verified** (see `VERIFICATION.md`) |

Post-2020 refinements found — real, but they do **not** lower the vertex count:

* de Grey & Parts, *On lower bounds of the order of k-chromatic unit distance graphs*,
  [arXiv:2303.14714](https://arxiv.org/abs/2303.14714) / Geombinatorics 32(2) 2022: *"For k = 5, the finite
  upper bounds are v5 ≤ 509, e5 ≤ 2406"*, i.e. **the two record-holders themselves, three years later, still
  give 509 vertices**; only the edge count drops (36 edges of the 509 graph are removable).
* The same paper's lower bound `v_5 >= 28`.

## Sources checked (master list; all accesses 2026-07-24 UTC)

### arXiv (topic + author sweeps, 2020–2026)

Queried through the arXiv API (`export.arxiv.org/api/query`, sorted by submission date), covering
`all:"unit distance graph"`, `all:"unit-distance"`, `all:"Hadwiger-Nelson"`, `all:"chromatic number of the
plane"`, `abs:"unit-distance" AND abs:"chromatic"`, plus author queries for Parts, de Grey, Heule, Exoo,
Ismailescu, Alexeev, Hubai, Kahle, Gibbs, Voronov, Neopryatnaya, Dergachev, Raigorodskii, Rubanov,
Neustroeva. Every result from 2020 onward was triaged; relevant PDFs were downloaded and text-searched for
`509`, `5-chromatic`, `record`, `smallest known` and for every `N-vertex` token with `N < 509` co-occurring
with a 5-chromatic mention. Full per-paper table: `FINDINGS-citations.md`.

Notable items and why none is a counterexample:

| Paper | Finding |
|---|---|
| Parts, [arXiv:2010.12665](https://arxiv.org/abs/2010.12665) | the 509 record itself |
| Parts, [arXiv:2010.12661](https://arxiv.org/abs/2010.12661) | human-verifiable χ≥5 proof; its `G481` "base graph" is **not** claimed 5-chromatic (a trap: 481 < 509) |
| de Grey & Parts, [arXiv:2303.14714](https://arxiv.org/abs/2303.14714) | `v_5 ≤ 509`, `e_5 ≤ 2406`, `v_5 ≥ 28` |
| Voronov, Neopryatnaya & Dergachev, [arXiv:2106.11824](https://arxiv.org/abs/2106.11824) | plane graphs: 3877 / 64513 vertices; the 372- and 972-vertex 5-chromatic examples are on a **sphere**, not the plane |
| Parts, [arXiv:2206.12632](https://arxiv.org/abs/2206.12632) | 495-vertex graph is **odd-distance**, χ=6 — not unit-distance |
| Exoo & Ismailescu, [arXiv:2303.06801](https://arxiv.org/abs/2303.06801) | 622 vertices, **hyperbolic** plane |
| Exoo & Ismailescu, [arXiv:1805.06055](https://arxiv.org/abs/1805.06055) | 26 vertices, **two forbidden distances** |
| Mundinger et al. (ICML 2025), [arXiv:2501.18527](https://arxiv.org/abs/2501.18527) | ML-discovered colorings; χ≥6 constructions in **R^3** |
| Dúcz & Varga, [arXiv:2606.28157](https://arxiv.org/abs/2606.28157) (2026) | 29-vertex plane UD graph, but about **independence ratio / fractional** chromatic number; its χ is 4 |
| Parts, [arXiv:2603.14581](https://arxiv.org/abs/2603.14581) (Mar 2026) | Parts' newest paper — **R^8**, χ(R^8) ≥ 25; contains no new plane record |
| Rosenmann, [arXiv:2606.16642](https://arxiv.org/abs/2606.16642) (Jun 2026) | most recent citation found: *"the current minimal example is a graph of 509 vertices constructed by Parts in 2020"* |

### Geombinatorics (Parts' and de Grey's usual venue)

TOCs reconstructed issue-by-issue for volumes **XXIX (2019–20) through XXXVI (2026)** from
<https://geombina.uccs.edu> (author and volume indexes, e.g.
<https://geombina.uccs.edu/author-index/jaan-parts>) cross-checked against the zbMATH API — see
`FINDINGS-geombinatorics-russian-theses.md`. The journal is still publishing on this exact topic, and the
2026 items are **not** plane results:

* de Grey, *A 5-Chromatic, Triangle-Free Unit-Distance Graph in R^3 With 61 Vertices*, Geombinatorics 35 (2026) — **R^3**.
* Haugstrup, *A Tetrahedron-Free 6-Chromatic Unit-Distance Graph in Three-Dimensional Space*, Geombinatorics 35 (2026) — **R^3**.
* de Grey & Haugstrup, *Two Small 6-Chromatic Unit-Distance Graphs in R^3*, Geombinatorics 33 (2022) 110–115 — **R^3**.

No Geombinatorics article in vol. XXIX–XXXVI claims a plane 5-chromatic unit-distance graph below 509.

### Polymath16 wiki, blog threads and comments

Polymath16 is where the 553 → 509 chain actually happened, so the wiki, its **revision history/diffs**, and
the **comment sections** of all 17 research threads were archived and grepped (details, URLs and dates in
`FINDINGS-wiki-code.md`). The wiki's record table is now stale — it stops at 510/2508 — and nothing in any
revision or comment claims a plane 5-chromatic graph below 509. The project's final thread is
[*Polymath16, seventeenth thread: Declaring victory*](https://dustingmixon.wordpress.com/2021/02/01/polymath16-seventeenth-thread-declaring-victory/)
(2021-02-01), i.e. the collaboration wound down after the 509 result.

### Wikipedia / MathWorld

* [Hadwiger–Nelson problem](https://en.wikipedia.org/wiki/Hadwiger%E2%80%93Nelson_problem), current text:
  *"As of 2021, the smallest known unit distance graph with chromatic number 5 has 509 vertices."* Revision
  history pulled via the MediaWiki API (`prop=revisions`, 200 revisions back) — no revision ever asserted a
  smaller plane graph, and no such edit was reverted.
* MathWorld [Parts Graphs](https://mathworld.wolfram.com/PartsGraphs.html) lists 553/529/525/510/510/**509**
  with edge counts and discovery dates; [de Grey Graphs](https://mathworld.wolfram.com/deGreyGraphs.html),
  [Heule Graphs](https://mathworld.wolfram.com/HeuleGraphs.html),
  [Mixon Graphs](https://mathworld.wolfram.com/MixonGraphs.html),
  [de Grey–Haugstrup Graphs](https://mathworld.wolfram.com/deGrey-HaugstrupGraphs.html) and
  [Hadwiger-Nelson Problem](https://mathworld.wolfram.com/Hadwiger-NelsonProblem.html) all still say the
  smallest plane example is the 509-vertex Parts graph. These pages are actively maintained (Weisstein
  computed exact coordinates for the new de Grey R^3 graphs in Dec 2025 / Jan 2026), which makes their
  silence on any sub-509 plane graph meaningful.

### Citation graphs

Semantic Scholar Graph API + OpenAlex `cites:` for Parts 2020 (18 citations), de Grey 2018 (135 + 45 on the
duplicate Geombinatorics record), Heule 2018 (30), de Grey–Parts 2023 (0), plus the Exoo–Ismailescu DCG
record (34). ~144 citing works enumerated; 97 arXiv PDFs downloaded and text-searched, the rest checked via
abstract/landing page. Every occurrence of "509" refers to Parts' record; no citing work claims an
improvement. Full table: `FINDINGS-citations.md`.

### Russian-language sources and theses

MathNet.ru, Cyberleninka, Istina (MSU), Raigorodskii-school publications, and thesis/dissertation searches
2019–2026 — details in `FINDINGS-geombinatorics-russian-theses.md`. The relevant Russian-school
construction (Voronov–Neopryatnaya–Dergachev) reports **64513** plane vertices; its small graphs are
spherical. One Warsaw master's thesis reports 529; the ELTE thesis concerns the probabilistic formulation
and order lower bounds. Nothing below 509 in the plane.

### Code/data hosting and linked graph files

`FINDINGS-wiki-code.md` has the full inventory. Highlights:

* <https://github.com/marijnheule/CNP-SAT> — real edge files for 517/529/553/510/610/633/803; nothing below 509.
* <https://github.com/vasnesterov/HadwigerNelson> (Lean formalization) — contains `vtx/509_parts.vtx` and
  `vtx/510_heule.vtx`; its verified target is Heule's 510 and it lists Parts' 509 as future work.
* <https://github.com/vsvor/dist-graphs> (Voronov) — plane DIMACS files with 3877 / 64513 vertices; the
  372-vertex files are **sphere** graphs.
* Parts' public Dropbox folder and its `graphs.txt` index (both archived here) — the sub-509 `.vtx` files it
  contains are explicitly labelled 4-chromatic graphs/subgraphs or intermediate components; see the
  verification section below, where we settle this by computation rather than by trusting the labels.
* GitLab, Zenodo, OSF and figshare searches: nothing relevant. (Note: several 2026 Zenodo preprints with
  titles like *"THE HADWIGER–NELSON PROBLEM: A RESOLUTION VIA OCTONIONIC PROJECTION"*
  (<https://doi.org/10.5281/zenodo.18452568>), *"Formal Verification of the 7-Color Chromatic Number of the
  Plane"* (<https://doi.org/10.5281/zenodo.20149766>), *"…via the Information Entropy Postulate"*
  (<https://doi.org/10.5281/zenodo.18261686>), *"…Analytical Proof of the 6-Color Chromatic Number"*
  (<https://doi.org/10.5281/zenodo.18260263>), *"A Ramanujan Partition Congruence Proof…"*
  (<https://doi.org/10.5281/zenodo.21209452>) were retrieved and inspected: all are unrefereed claims to
  *settle* χ(R^2) = 6 or 7 by analytic/algebraic arguments, none contains a unit-distance graph
  construction, none is peer-reviewed, and none bears on the sub-509 question.)
* House of Graphs entries for the Parts / de Grey / Heule graphs were checked; its public API required
  authentication for bulk queries (HTTP 401), so this source was covered via its web pages and the MathWorld
  cross-references rather than an exhaustive API sweep.

## Exact verification (the only sub-509 candidates in existence, settled by computation)

The only sub-509 *files* anywhere in the public Polymath16 corpus are Parts' component/subgraph files. Their
labels say they are 4-chromatic, but per the hard rule we did not trust the labels — we settled every one of
them by computation. Coordinates were parsed as exact algebraic numbers (fusion1's `mfield.py` where the
field is multiquadratic, an exact SymPy pipeline for the nested-radical files such as
`Sqrt[(5+Sqrt[5])/2]`), the unit-distance edge set was recomputed exactly (260-digit scan to select
candidate pairs, every pair with `|d²−1| < 1e-40` then decided symbolically), and 4-colorability was decided
with kissat. Full table, margins and certificates: `VERIFICATION.md`, `verify-out/`.

| file | order | exact unit edges | 4-colorable? | conclusion |
|---|---:|---:|---|---|
| `g409c.vtx` | 409 | 2046 | **SAT** (4-coloring rechecked exactly) | not 5-chromatic |
| `g469.vtx` | 469 | 2436 | **SAT** | not 5-chromatic |
| `v433d.vtx` | 433 | 2292 | **SAT** | not 5-chromatic |
| `v387.vtx` | 387 | 1904 | **SAT** | not 5-chromatic |
| `v379.vtx` | 379 | 1944 | **SAT** | not 5-chromatic |
| `v38w.vtx`, `v31_115.vtx`, `v30z.vtx`, `v16_56.vtx`, `mos_10.vtx` | 38, 31, 30, 16, 10 | 123, 59, 48, 28, 19 | **SAT** | gadgets, not 5-chromatic |
| `509_parts.vtx` (control) | 509 | **2442** | **UNSAT**, `drat-trim`: `s VERIFIED` | 5-chromatic — the record, independently re-verified here |
| `g568.vtx` (control) | 568 | 2922 | **UNSAT**, `drat-trim`: `s VERIFIED` | 5-chromatic, but larger than 509 |

So every sub-509 coordinate file that exists publicly is *provably* 4-colorable, i.e. **exactly verified not
to be a counterexample**, while the 509 record is **exactly verified to be 5-chromatic**.

## Residual risk

* Geombinatorics is not open access; TOCs were reconstructed from the publisher's indexes and zbMATH, and
  MathWorld's reference lists were used as a cross-check for very recent issues. A sub-509 plane result
  hiding in an issue whose TOC is not yet indexed anywhere cannot be excluded with certainty — though the
  record-holders' own 2022/2023 papers, MathWorld's Jan-2026 pages, and a June-2026 arXiv citation all still
  state 509.
* House of Graphs bulk API access and a few paywalled non-arXiv journal papers were not fully readable;
  their abstracts/landing pages were checked instead.
* Private/unpublished work is out of scope by definition.

# P23 priority-2 data forensics: Polymath16/wiki/blog/code crawl

**Access date:** 2026-07-24 (UTC)  
**Scope:** public HTML, WordPress REST post/comment archives, Polymath wiki revisions/diffs, public GitHub repositories, and linked public graph files. This is a source/data inventory, not a new construction or an assertion based only on a filename.

## Executive conclusion

No public claim or obtained graph data establishes a **5-chromatic unit-distance graph in the plane with fewer than 509 vertices**. The smallest obtained/evidenced 5-chromatic plane graph remains **509 vertices, 2442 edges**, Jaan Parts (2020). The only sub-509 coordinate files found are explicitly described as 4-chromatic subgraphs, intermediate components, or otherwise are not claimed as 5-chromatic plane graphs. In particular:

* `g409c.vtx` has 409 coordinate rows, but the author explicitly calls it a **409-vertex 4-chromatic graph** and says two copies plus an edge yield a 5-chromatic graph.
* `g469.vtx` has 469 rows and is explicitly labelled a **469-vertex 4-chromatic subgraph** of a 625-vertex 5-chromatic graph.
* `v379.vtx`, `v387.vtx`, `v433d.vtx` and related files are intermediate/reduced components or candidates; the thread does not claim any of them alone is 5-chromatic.
* `v525e2605.vtx`, `g529_2630.vtx`, `g553_2840.vtx`, and `g568.vtx` are obtained and have the claimed row counts, but all are **>= 509** (and 568 is the smallest obtained fresh claim above the record). The linked `v510e2508.vtx` Dropbox URL returned an HTML landing page rather than graph data and is not counted as obtained.

A vertex-row count in a `.vtx` file is data evidence for order only; chromaticity and exact unit-distance correctness are recorded separately as text claims unless an edge/SAT certificate is present.

## Polymath16 wiki

Main page checked: <http://michaelnielsen.org/polymath1/index.php?title=Hadwiger-Nelson_problem> (redirected by server to `/polymath/index.php`). Linked wiki pages crawled:

* <http://michaelnielsen.org/polymath/index.php?title=Hadwiger-Nelson_problem>
* <http://michaelnielsen.org/polymath/index.php?title=Probabilistic_formulation_of_Hadwiger-Nelson_problem>
* <http://michaelnielsen.org/polymath/index.php?title=Algebraic_formulation_of_Hadwiger-Nelson_problem>
* <http://michaelnielsen.org/polymath/index.php?title=Excluding_bichromatic_vertices>
* <http://michaelnielsen.org/polymath/index.php?title=Coloring_R_2>

For each page, the raw page HTML, history HTML, and history diff views were saved under `runs/P23-priority2/sources/wiki/`. The main page history/diffs include the progression 553, 529, 525, 510 and finally 509. The wiki's “Notable unit distance graphs” table describes the bold number as the current minimal order known not to be 4-colorable; the current table/revision material does not contain a number below 509 for the plane 5-chromatic target. `sources/wiki/extracted.txt` is the grep-able text corpus.

Representative evidence in the archived revision text includes the record table and history edits such as “added 529 vertex graphs”; no <509 5-chromatic claim was found. The wiki also links the 17 Mixon research threads, including the fourteenth through seventeenth threads that were not present in some older wiki revisions.

## Dustin Mixon Polymath16 research threads and comments

All 17 Dustin Mixon research threads were checked, including comment archives through the WordPress REST API (`number=100`, all pages). Raw post JSON and normalized post/comment text are in `runs/P23-priority2/sources/threads/`; `all-text.txt` is the searchable corpus. The first thread was separately fetched after correcting its canonical slug (`simplifying-de-greys-graph`). Dates and URLs checked:

1. 2018-04-14 — <https://dustingmixon.wordpress.com/2018/04/14/polymath16-first-thread-simplifying-de-greys-graph/>
2. 2018-04-22 — <https://dustingmixon.wordpress.com/2018/04/22/polymath16-second-thread-what-does-it-take-to-be-5-chromatic/>
3. 2018-05-01 — <https://dustingmixon.wordpress.com/2018/05/01/polymath16-third-thread-is-6-chromatic-within-reach/>
4. 2018-05-05 — <https://dustingmixon.wordpress.com/2018/05/05/polymath16-fourth-thread-applying-the-probabilistic-method/>
5. 2018-05-10 — <https://dustingmixon.wordpress.com/2018/05/10/polymath16-fifth-thread-human-verifiable-proofs/>
6. 2018-05-29 — <https://dustingmixon.wordpress.com/2018/05/29/polymath16-sixth-thread-wrestling-with-infinite-graphs/>
7. 2018-06-16 — <https://dustingmixon.wordpress.com/2018/06/16/polymath16-seventh-thread-upper-bounds/>
8. 2018-06-24 — <https://dustingmixon.wordpress.com/2018/06/24/polymath16-eighth-thread-more-upper-bounds/>
9. 2018-07-02 — <https://dustingmixon.wordpress.com/2018/07/02/polymath16-ninth-thread-searching-for-a-6-coloring/>
10. 2018-08-28 — <https://dustingmixon.wordpress.com/2018/08/28/polymath16-tenth-thread-open-sat-instances/>
11. 2018-09-14 — <https://dustingmixon.wordpress.com/2018/09/14/polymath16-eleventh-thread-chromatic-numbers-of-planar-sets/>
12. 2019-03-23 — <https://dustingmixon.wordpress.com/2019/03/23/polymath16-twelfth-thread-year-in-review-and-future-plans/>
13. 2019-07-08 — <https://dustingmixon.wordpress.com/2019/07/08/polymath16-thirteenth-thread-bumping-the-deadline/>
14. 2019-08-05 — <https://dustingmixon.wordpress.com/2019/08/05/polymath16-fourteenth-thread-automated-graph-minimization/>
15. 2019-12-12 — <https://dustingmixon.wordpress.com/2019/12/12/polymath16-fifteenth-thread-writing-the-paper-and-chasing-down-loose-ends/>
16. 2020-05-11 — <https://dustingmixon.wordpress.com/2020/05/11/polymath16-sixteenth-thread-writing-the-paper-and-chasing-down-loose-ends-ii/>
17. 2021-02-01 — <https://dustingmixon.wordpress.com/2021/02/01/polymath16-seventeenth-thread-declaring-victory/>

The comments contain the useful chronology: 610 (May 2018), 553/529/525, 510, and then Parts' 509 (comment 24942, 2020-03-07). They also contain the most relevant caveats: the 409 graph is 4-chromatic; the 469 graph is a 4-chromatic subgraph; the 568 graph is claimed 5-chromatic but larger than 509. No comment claims a verified plane 5-chromatic graph below 509.

Terence Tao checked: <https://terrytao.wordpress.com/2018/04/14/polymath16-now-launched-simplifying-the-lower-bound-argument-for-the-hadwiger-nelson-problem/> and the Polymath16 tag archive <https://terrytao.wordpress.com/tag/polymath16/>. Tao's material is an announcement/context thread and did not expose a smaller graph claim; the detailed research-thread corpus is Mixon's archive above.

## Linked graph files obtained

Files downloaded from public Dropbox links and one public Jixco mirror are under `runs/P23-priority2/data/`. Dropbox folder/index evidence:

* Parts folder announcement and index: <https://www.dropbox.com/sh/o5jdo163zycx5sc/AAB7ll1DfO36ILTISP4G0TX9a?dl=0>
* Index: <https://www.dropbox.com/s/0bcutukm5b99nu1/graphs.txt?dl=0>
* Parts 509/510 index says `M-graph m6a: 509 v509e2442.vtx; 510 v510e2502.vtx`; the individual 509 file was also obtained in the Vasnesterov repository below.
* 553: <https://www.dropbox.com/s/zknw7c8ckl79qgu/g553_2840.vtx?dl=0>
* 529: <https://www.dropbox.com/s/zbwjv3pj6d93fb7/g529_2630.vtx?dl=0>
* 525: <https://www.dropbox.com/s/2mcb5o7r0uewoua/v525e2605.vtx?dl=0>
* 568: <https://www.dropbox.com/s/21sly4f9lr41myl/g568.vtx?dl=0>
* 510 (link checked; Dropbox returned HTML rather than a coordinate file): <https://www.dropbox.com/s/v5lbv5adropt2l0/v510e2508.vtx?dl=0>
* 409 (explicitly 4-chromatic): <https://www.dropbox.com/s/msbtrhd5gs8ajsn/g409c.vtx?dl=0>
* 469 (explicitly 4-chromatic subgraph): <https://www.dropbox.com/s/xp7b43bnnrsqz0c/g469.vtx?dl=0>
* Additional intermediate/component files: `v379.vtx`, `v387.vtx`, `v433d.vtx`, `v799.vtx`, `v30z.vtx`, `v31_115.vtx`, `v38w.vtx`, `v16_56.vtx`, `mos_10.vtx`, `v34590.vtx`, `g607.vtx`, `g625.vtx`, `g649a.vtx`, `g655.vtx`, and `745.vtx`.

Actual downloaded coordinate-row counts (evidence from `wc -l`; `.vtx` rows): `g409c` 408 newline rows = 409 coordinate records when accounting for final-line formatting, `g469` 468 newline rows = 469 records, `v379` 378 newline rows = 379 records, `v387` 386 newline rows = 387 records, `v433d` 432 newline rows = 433 records, `v525e2605` 524 newline rows = 525 records, `g529_2630` 528 newline rows = 529 records, `g553_2840` 552 newline rows = 553 records, `g568` 567 newline rows = 568 records, and `v510e2508` 261 rows because it is a Mathematica-style compressed/structured artifact rather than one coordinate per line. The Parts `graphs.txt` index is the authoritative claimed order/edge count for its named files.

Google Drive links were enumerated from the comments and preserved in the thread corpus. They were mostly tiling images/visualizations, not graph coordinate datasets; no sub-509 5-chromatic graph data was obtained from them.

## Public code/data hosting

### GitHub: Heule

* <https://github.com/marijnheule/CNP-SAT> — shallow working clone (now removed; see `sources/REPOSITORIES.md`); last commit in clone: 2021-09-27 (`bb414955...`, “T721”). It contains actual edge files and coordinates for 517, 529, 553, 510, 610, 633, 803, etc. Example headers: `edge/517.edge` = `p edge 517 2579`; `edge/529.edge` = `p edge 529 2670`; `edge/553.edge` = `p edge 553 2722`; `edge/510.edge` = `p edge 510 2504`. No file below 509 is a claimed 5-chromatic plane record.

### GitHub: Lean formalization

* <https://github.com/vasnesterov/HadwigerNelson> — working clone (now removed; retained evidence is under `sources/code-evidence/`); last commit 2024-09-02 (`ad784354...`). It contains `vtx/509_parts.vtx` and `vtx/510_heule.vtx`. README explicitly says the verified target is Heule's 510 graph, cites the Parts 509 graph, and lists proving Parts 509 as future work. This is the cleanest obtained 509 coordinate artifact, but not a <509 claim.

### GitHub: Voronov

* <https://github.com/vsvor/dist-graphs> — working clone (now removed; see `sources/REPOSITORIES.md`); last commit 2021-12-21 (`e3714d0...`). Plane series-1 DIMACS files have headers `p edge 3877 26778`–`26814`; plane series-2 files have 64513 vertices. README/paper context describes 5-chromatic plane constructions, all far above 509. The repository also has sphere files (including 372-vertex sphere examples), which are **not plane graphs** and must not be used as a plane record.

### Other hosting searches

GitLab search (<https://gitlab.com/search?search=Hadwiger-Nelson>) produced unrelated unit-distance drawing material (e.g. Parcly Taxel/Dounreay), not a Polymath16 5-chromatic plane graph. Searches of Zenodo, OSF, and figshare for Hadwiger–Nelson/unit-distance graph terms produced no relevant sub-509 artifact. Search result pages and URLs were checked on 2026-07-24; no graph data was downloaded from those services.

## Suspicious/promising items and disposition

* **409 vertices:** promising by size only, but explicitly 4-chromatic in the source comment; not a counterexample. Data saved.
* **469 vertices:** explicitly 4-chromatic subgraph; not a counterexample. Data saved.
* **374/375/376/403/433 etc.:** Parts L/S or intermediate components; the Parts index and comments do not claim them alone to be 5-chromatic. Do not count them as records.
* **568 vertices:** explicit 5-chromatic claim with data, but larger than 509. Data saved and is the closest fresh public candidate found above the record.
* **Google Drive/Dropbox visual links:** checked/enumerated; no additional <509 5-chromatic coordinate file found.

## Archive inventory

The committable archive is intentionally trimmed to well under the original 1.3 GB working tree:

* `VERIFICATION.md` — exact-arithmetic verification table for all priority sub-509 files, the 509 control, and g568.
* `verify-out/` — compact solver logs, drat-trim `s VERIFIED` output, SAT colorings, and JSON summary. Temporary CNF/DRAT proof files were deleted after checking; no large proof is retained.
* `data/` — downloaded `.vtx` graph data and Parts `graphs.txt` index. These are retained because they are the requested data artifacts.
* `sources/code-evidence/` — tiny retained evidence files: Parts 509/Heule 510 coordinates and Heule `.edge` headers for 517/529/553/510.
* `sources/REPOSITORIES.md` — repository URLs, resolved commit SHAs/dates, and cited evidence. The three full GitHub clones were dropped after recording: `vsvor/dist-graphs` at `e3714d0a156f6ed151d4521debb2b89ce4f1075c`, `vasnesterov/HadwigerNelson` at `ad7843546da5f4db4fcf9827e0951f34295ad7cc`, and `marijnheule/CNP-SAT` at `bb414955a6ef5f49f7df2b245b1e778aa67c068a`.
* `sources/wiki/extracted.txt.gz` plus `sources/wiki/MANIFEST.md` — normalized wiki corpus and page/history/diff URL manifest. Raw HTML/history/diff files were dropped; the crawl had five page files, five history files, and 318 diff files.
* `sources/threads/all-text.txt.gz`, `first-text.txt`, `linked-files.tsv.gz`, `urls.txt`, and `MANIFEST.md` — normalized Mixon post/comment corpus and compact linked-file inventory. Raw WordPress JSON files were dropped.

The URLs, SHAs, access date, and evidence-file descriptions needed to reproduce the dropped repository/wiki/thread material remain in the manifests and this report.

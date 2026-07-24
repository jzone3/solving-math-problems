# Provenance audit for the reported 509/2406 graph

**Audit date:** 2026-07-24 UTC

## Verdict

The actual 509-vertex/2406-edge file was **not found publicly** in the sources
checked.  The public coordinate file obtained is `v509e2442.vtx`; no public
edge list or coordinate file identifying the 36 discarded edges was located.

## Sources checked

| Source | URL / identifier | Outcome |
|---|---|---|
| de Grey & Parts paper | https://arxiv.org/abs/2303.14714 | The footnote explicitly says 36 edges were discarded, but supplies no data URL or edge list. |
| arXiv source | https://arxiv.org/src/2303.14714 | Source tarball contains `main.tex` and `references.tex`; no graph data or ancillary file. |
| related arXiv sources | `/src/` and `/e-print/` for `2303.14722`, `2206.12630`, `2206.12632`, `2206.12633`, `2206.12635`, `2010.12665` | HTTP 200 source archives inspected; no 2406-edge graph data. |
| arXiv ancillary endpoint | https://arxiv.org/anc/2303.14714 and corresponding endpoints for the six related IDs | HTTP 404 for each checked identifier. |
| Parts graph index | https://www.dropbox.com/s/0bcutukm5b99nu1/graphs.txt?dl=0 | Lists `v509e2442.vtx` and `v510e2502.vtx`; no `v509e2406` or nearby 509-edge entry. |
| Parts Dropbox folder | https://www.dropbox.com/sh/o5jdo163zycx5sc/AAB7ll1DfO36ILTISP4G0TX9a?dl=0 | Folder listing includes `v509e2442.vtx`, `v451e2400.vtx`, and `v510e2502.vtx`; no 2406 file. |
| older Parts folder link | https://www.dropbox.com/sh/ufknm1v9gtbhad3/AAC6uRgySFEQfFJdqiN7DME4a/JP/Large?dl=0&subfolder_nav_tracking=1 | Listing checked; no 2406 file. |
| Dropbox filename probes | Same file-share token with `v509e2406.vtx`, `v509e2405.vtx`, `v509e2407.vtx` | Returned the `graphs.txt` HTML response rather than graph data; not evidence of sibling files. |
| Polymath corpus | Archived wiki/thread corpus under `sources/wiki/` and `sources/threads/` | Searches for `2406`, `2405`–`2410`, `-36`, `36 edges`, and `edge-critical` found discussion and the 2442 record, but no downloadable 2406 data. |
| Parts paper source | https://arxiv.org/src/2010.12665 | References the Dropbox `JP/Large` folder and `graphs.txt`; contains no reduced edge list. |
| Geombinatorics issue index | https://geombina.uccs.edu/past-issues/volume-xxxii | Confirms the article and issue (XXXII(2), October 2022); no supplementary graph-data link is listed. |
| author index | https://geombina.uccs.edu/author-index/aubrey-de-grey | Confirms the article metadata; no graph-data attachment is listed. |
| MathWorld Parts graphs summary | https://mathworld.wolfram.com/PartsGraphs.html | Lists the public record as 509/2442 and does not list a 509/2406 artifact. |
| web search: de Grey/Parts 2406 | Search results for “Aubrey de Grey 509 2406 unit distance graph” and “Jaan Parts 509 2442 2406 graph” | Returned the paper, MathWorld, and the 2442 Parts paper/data references; no downloadable 2406 data. |

The obtained `v509e2442.vtx` is retained under `data/`, and its exact
2442-edge set is in `data/v509e2442.edges`.

The Dropbox share was also downloaded as a ZIP export. It contained 43
additional `.vtx` files from the L-subgraph, S-subgraph, mono-pair,
non-mono-pair, and non-mono-triple families listed in `graphs.txt`; all were
saved under `data/` and exactly verified. The ZIP contained no
`v509e2406.vtx` or other 509/2406 file. The expanded verification results are
in the additional table in `VERIFICATION.md`.

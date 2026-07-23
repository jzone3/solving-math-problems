# P22 / v1 — Priority check (widened scope per METHODOLOGY.md)

Date: 2026-07-23. Question: has anyone already improved Fe(3,3;4) ≤ 786, resolved
Problem 5.1 of arXiv:2506.14942 (K₄-free Folkman subgraph of H₃), or claimed
Graham's $100 prize (Fe(3,3;4) < 100)?

## Searches performed

1. **arXiv** (Exa search over arxiv.org + direct abstract fetches):
   - "Folkman number upper bound improved 2026", "Hermitian unital Folkman 63 vertices SAT".
   - Newest relevant: **arXiv:2605.16542** "On Small Folkman Graphs Arrowing K₂ or K₃"
     (May 2026) — states "the best known bounds are 21 ≤ Fe(3,3;4) ≤ 786 [BN20, LRX14]";
     also proves Fe(3,3;4) ≤ Fe(3,3; complement(P₂∪P₃)). **786 still standing; LB is 21**
     (Bikov–Nenov 2017/2020), not 20 as in the catalog file.
   - Target paper arXiv:2506.14942 v-latest: Problem 5.1 posed open; authors' own
     experiments negative.
2. **GitHub** (repo search API): "Folkman 786", "arrowing triangle SAT", "Fe(3,3;4)",
   "folkman graph 63" — no relevant artifact repos. Known code: Steven-VO/quasiFolkman
   (the paper's own experiment notebook — inspected; same experiments 1–5 we reproduced)
   and Bikov's older Folkman code.
3. **Zenodo** (records API, q=Folkman): only the 2019 "QSAT Benchmark Based on
   Vertex-Folkman Problems" (doi:10.5281/zenodo.3548976) — vertex Folkman, unrelated to
   the edge bound.
4. **OpenReview / general web** (Exa): "Graham $100 Folkman prize claimed" — only
   historical coverage (Quanta 2017, Lu's f(2,3,4) page with the 2007 ≤ 9697 result);
   no claim of a sub-786 graph or prize award.

## Conclusion

No prior resolution found; the negative result recorded in this run does not conflict with
any known artifact. Residual risks: paywalled Geombinatorics issues post-2020 not checked
page-by-page; Chinese-language venues (Xu Xiaodong's group) not searched natively.

## Note

This run claims **no new result** — it is a certified reproduction (quasi-Folkman UNSAT of
H₃, DRAT-verified) plus a scaled-up negative sweep of the paper's suggested alterations —
so priority is moot for novelty claims; check recorded for completeness per methodology.

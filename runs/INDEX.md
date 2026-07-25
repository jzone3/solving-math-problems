# Run Index

Matrix of solve runs: problem x variant. Status: queued / running / negative / near-miss / SOLVED.

| Problem | V1 | V2 | V3 | V4 | V5 |
|---|---|---|---|---|---|
| P01 | queued | queued | queued | queued | queued |
| P02 | queued | queued | queued | queued | queued |
| P03 | queued | queued | queued | queued | queued |
| P04 | queued | queued | queued | queued | queued |
| P05 | queued | queued | queued | queued | queued |
| P06 | queued | queued | queued | queued | **698 PROVED TRUE; 129 frontier n=11 exhaustive** |
| P07 | queued | queued | queued | queued | **154 & 143 refuted — SCOOPED by demonstrandum-research (public 2026-06-12); see handoff/P07 priority notice** |
| P08 | queued | queued | queued | queued | queued |
| P09 | queued | queued | queued | queued | queued |
| P10 | queued | queued | queued | queued | queued |
| P11 | queued | queued | queued | queued | queued |
| P12 | queued | queued | queued | queued | queued |
| P13 | queued | queued | **(9,6,1)-PMD proven nonexistent — DRAT-verified, adversarially CONFIRMED (see solutions/P13)** | queued | queued |
| P14 | queued | queued | queued | queued | queued |
| P15 | queued | queued | queued | queued | queued |
| P22 | queued | **negative on G₁₂₇ decision; symmetric-coloring exclusion theorem (any G₁₂₇ non-arrowing witness is fully asymmetric; DRAT-certified) — runs/P22/v2**; **fusion1 (runs/P22/fusion1): H₃ (63-vtx Hermitian-unital) independently reconstructed (2 verifiers) + `H₃ → (K₃)_{T₃}` reproduced & DRAT/LRAT-certified (2 solvers, 2 checkers); exact decision "does H₃ have a K₄-free arrowing subgraph?" built as a sound 2-QBF (+ automorphism symmetry-breaking + bloqqer) — all 4 leading QBF solvers (CAQE/DepQBF/Qute/RAReQS) time out/OOM at 3000s/24GiB; f(2,3,4)≤63 stays OPEN (block/ILP/CEGAR/triangle-floor K₄-free subgraphs up to 863 triangles all SAT, witnesses verified); certified reproductions of the paper's small quasi-Folkman systems (11-vtx circulant \|𝒯\|=88, 12-vtx, 39-vtx H₃ reduction 39/1488/898) — runs/P22/fusion1/qfolkman. f(2,3,4)≤63, Graham's <100, G₁₂₇ arrowing all remain open; no bound claimed without a checked certificate** | queued | queued | queued |

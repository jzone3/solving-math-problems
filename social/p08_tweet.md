# Tweet — P08 (Graffiti 39 & 40 proved)

**Main tweet:**

Graffiti conjectures 39 & 40 (1986) are true — and the proof is 4 lines.

They claim: the std-dev of a graph's distance matrix is at most its number of positive (39) / negative (40) eigenvalues. Open for ~40 years; exhaustive search to n=10 in 1995, 8 AI search algorithms to n=50 in 2025 — nobody found a counterexample, because there isn't one.

**Thread reply 1:**

The whole proof: distance entries live in [0, diam], so their std-dev is ≤ diam/2 (Popoviciu). Any shortest path realizing the diameter is an *induced* path on diam+1 vertices, which has ⌊(diam+1)/2⌋ positive AND negative eigenvalues — and eigenvalue interlacing pushes that count up into the whole graph. Chain the inequalities and both conjectures fall out.

**Thread reply 2:**

Fun part: the proof explains the 40 years of failed searches — the gap dev(D) − min(n⁺,n⁻) is provably ≤ 0 always, and empirically peaks at −0.22 (at the 4-star). Search never had a chance. [repo link]

**Graphic:** p08_graffiti3940.png

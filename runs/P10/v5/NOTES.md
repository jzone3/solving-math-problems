# P10 — Brouwer's Conjecture — V5 (literature-first) run notes

Session: devin-9a0b5e0756804d1dade30ae429a27826 · Date: 2026-07-22 · Branch: `runs/P10-v5`

## 0. Statement re-verification (against original source)

Problem file statement — for every graph G with m edges and Laplacian eigenvalues
μ₁ ≥ … ≥ μₙ: Σ_{i≤t} μᵢ ≤ m + t(t+1)/2 for all 1 ≤ t ≤ n — matches the statement in
Brouwer–Haemers, *Spectra of Graphs* (Springer 2012), §3.2 / Conjecture 3.9.1, and the
Wikipedia article "Brouwer's conjecture" (checked 2026-07-22). No paraphrase drift.

## 1. HEADLINE FINDING: the conjecture is NO LONGER OPEN

The problem file's "Status: Open in general (July 2026)" is **stale**.

- **Kothari, P. K. & Tudose, S., "On Brouwer's Laplacian conjecture", arXiv:2606.12197v1
  (10 Jun 2026)** gives a full proof of Brouwer's conjecture, deriving it from the
  Grone–Merris–Bai (GMB) theorem restricted to split graphs, and also proves the converse
  (Brouwer ⇒ GMB), establishing equivalence of the two statements.
- Independent corroboration — three later 2026 preprints by three separate groups treat the
  conjecture as settled and build on it:
  - arXiv:2607.03388 (Cai–Chen–Yang–Zhang, SJTU): "Recently, Kothari and Tudose (2026)
    proved the conjecture" — proves the *full* (equality-case) Brouwer conjecture of Li–Guo:
    equality for some 1≤k≤n−1 iff G is a threshold graph with clique number k+1.
  - arXiv:2607.08452 (Lu–Yang, Nanjing): "…which was recently confirmed by Kothari and
    Tudose" — proves two of Lew's generalization conjectures.
  - arXiv:2607.17293 (Cui–Chen, Guangxi): "…which has been confirmed by Kothari and Tudose
    (2026) recently" — independently characterizes the equality case.
- No withdrawal, errata, or rebuttal found (arXiv still at v1; Exa searches for
  "error/flaw/retracted" return nothing adverse).

Hence the V5 mandate "verify none [of the cited papers] closes the conjecture" resolves in
the *opposite* direction: 2606.12197 closes it. Counterexample/metaheuristic search
(V1–V4 framings) is moot; a violating witness cannot exist unless the KT proof is wrong.
The bulk of this run therefore went into a line-by-line audit + machine verification of the
KT proof — the strongest V5 deliverable available.

## 2. The KT proof, digested

Forward chain (only this direction is needed; the converse is separate, so no circularity):

```
GMB for split graphs  (Bai 2011 — split graphs are Bai's hard case)
  ⇒ Lemma 3.2:  ‖L_H − |K|·C‖_* ≤ |K|·|S|   (C = I − J/n, H split with clique K, ind. set S)
  ⇒ identity (5.3) + trace duality ⇒ Lemma 5.5 (capacitated-routing inequality for M)
  ⇒ Lemma 5.3:  Σ_{i≠j}(1−|M_ij|)² ≥ (2/n)‖v‖²,  M_ij = P_ii+P_jj−2P_ij−1, v = CM1
  ⇒ (with Lemma 5.2 identity) Lemma 5.6:  Σ_{i≠j}(M_ij)_+ ≤ k(k+1)
  ⇒ (with Lemma 5.1, tr(PL) = Σ_edges ‖P(e_i−e_j)‖²) Brouwer:  Σ_{i≤k} λ_i ≤ m + C(k+1,2).
```

Manual audit of each step (all fine; details of the potential trouble spots):

1. **GMB ⇒ 3.2.** Σ_{i≤k} d'_i = Σ_i min(d_i,k) ≤ kr + E(K,S) for split H (clique degrees
   ≤ anything, min ≤ k; independent-set degrees sum to E(K,S)). With t = #{i≤n−1: λ_i>r},
   Σ_{λ_i>r}(λ_i−r) ≤ E(K,S). Then, using 2m = r(r−1) + 2E(K,S),
   ‖L−rC‖_* = Σ_{i≤n−1}|λ_i−r| = 2Σ_+(λ_i−r) − (2m − r(n−1)) = 2Σ_+ + rs − 2E ≤ rs. ✔
   (Checked the arithmetic by hand and by machine.)
2. **Lemma 5.1.** tr(PL) = Σ_{(i,j)∈E} (P_ii+P_jj−2P_ij) via L = Σ (e_i−e_j)(e_i−e_j)ᵀ. ✔
3. **Lemma 5.2 identity** ¼Σ_{i≠j}[a_ij² − (P_ii−P_jj)²] = k(k+1): verified in *exact
   rational arithmetic* on random rational projections (P²=P, P1=0). ✔
4. **Identity (5.3)** Σ_{i≤r} v_i + Σ_{i≤r<j}|M_ij| = −tr((L_{G_r} − rC)N), N = CMC:
   verified exactly for all r on random rational projections. Key steps: N=CMC ⇒ can
   replace N by M inside the trace (L1=C1=0); diag(M)=0; M_ij+|M_ij| = 2(M_ij)_+ matches
   the cut edges of G_r (added exactly where M_ij ≥ 0). ✔
5. **Trace duality step.** N = C − 2P (checked: M = d1ᵀ+1dᵀ−2P−J+I, CP=PC=P) has
   eigenvalues in {−1,0,1} so ‖N‖_op = 1; |tr(AN)| ≤ ‖A‖_*‖N‖_op is standard. G_r is a
   genuine split graph, so Lemma 3.2 gives the bound r(n−r) *independent of the cut*,
   yielding (5.4): Σ_{i≤r} v_i ≤ Σ_{i≤r<j}(1−|M_ij|). Note 1−|M_ij| ≥ 0 since
   a_ij = ‖P(e_i−e_j)‖² ∈ [0,2]. ✔
6. **Telescoping** (Abel summation with x sorted descending, Σv_i = 0) gives Lemma 5.5;
   Cauchy–Schwarz with Σ_{i<j}(v_i−v_j)² = n‖v‖² (v ⟂ 1) gives Lemma 5.3. ✔
7. **Lemma 5.6.** Uses (x−1)_+ = ¼(x² − (1−|x−1|)²), valid exactly for x ∈ [0,2] (checked
   symbolically on both branches); v_i − v_j = n(P_ii−P_jj) (exact-verified); then (5.5) ⇔
   (5.2). Finally Σ_{edges}(a_ij−1) ≤ ½Σ_{i≠j}(a_ij−1)_+ ≤ C(k+1,2), plus k=n case
   trivial (Σλ = 2m ≤ 2·C(n+1,2) — actually m + C(n+1,2) ≥ 2m since m ≤ C(n,2)). ✔

No gaps found. The proof is short, self-contained modulo Bai's theorem (published, TAMS
2011, 15 years of scrutiny), and every algebraic identity checks out exactly.

## 3. Machine verification (code in this directory)

`audit_lemmas.py` (also distilled into `solutions/P10/verify.py`, numpy-only, prints PASS):

- **Exact (Fraction arithmetic)**: Lemma 5.2 identity, v = nC·diag(P) identity, and
  identity (5.3) for *all* r — on random rational rank-k projections with P1=0
  (n ≤ 9, 6 trials each, every check exact-equality PASS).
- **Numeric**: GMB positive-part bound + Lemma 3.2 nuclear-norm bound on 400 random split
  graphs (n ≤ 30); Lemmas 5.5/5.3/5.6 on 400 random projections (n ≤ 40) with random test
  vectors; end-to-end Brouwer on 1500 random G(n,p) graphs (n ≤ 24), all k. All PASS,
  max violation ~1e-13 (numerical noise at threshold-graph equality cases).
- **Adversarial**: 60 restarts × 300 steps of gradient ascent on the Stiefel manifold
  trying to violate Lemma 5.6 (Σ(M_ij)_+ > k(k+1)). Best value found: slack 5.7e-14, i.e.
  ascent converges to the *equality* cases (projections aligned with threshold-graph
  eigenspaces) and never crosses. Consistent with the lemma being tight and true.

Compute spent: ~10 min CPU total (verification is cheap; no large-scale search is
warranted given §1).

## 4. Residual open problems in this area (post-KT frontier)

- **Full/equality Brouwer (Li–Guo)**: equality iff threshold graph with clique number k+1 —
  now also claimed proved, twice independently (2607.03388, 2607.17293).
- **Signless-Laplacian analogue** and weighted-graph analogues: still open in general
  (KT's proof uses L = Σ(e_i−e_j)(e_i−e_j)ᵀ; the signless version needs (e_i+e_j) and the
  P1=0 trick breaks).
- **Token-graph / Apte–Parekh–Sud conjecture** (λ_max of k-token graph ≤ m + k): only the
  weak version m + 4k − 2 is known (Lew, 2601.17575).
- **Simplicial (Duval–Reiner-type) Brouwer analogues**: open.

## 5. Dead ends / notes for the orchestrator

- V1–V4 (counterexample-hunting framings) for P10 should be stood down or repointed at the
  signless-Laplacian / token-graph analogues, where a witness search is still meaningful.
- No arithmetic in the KT paper was trusted: every identity was recomputed exactly, every
  inequality lemma stress-tested numerically and adversarially.
- `problems/P10-brouwer-laplacian.md` should be updated: Status → closed (Kothari–Tudose
  2026); the "2606.12197" entry in the V5 variant list *is* the closing paper.

## STATUS: closed-in-literature — Brouwer's conjecture was PROVED by Kothari–Tudose (arXiv:2606.12197, June 2026); proof audited line-by-line and machine-verified (all lemmas PASS, adversarial search finds only equality cases); no counterexample search warranted.

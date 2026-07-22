# P10 Brouwer's Conjecture — V3 (exhaustive n=11–12 frontier push)

Session: https://app.devin.ai/sessions/738e8176361f4894bc2aa550222ba4de
Variant: V3 — push Brouwer's exhaustive verification frontier (n ≤ 10, per Brouwer–Haemers)
to n = 11 and as far into n = 12 as compute allows, using nauty `geng` + optimized eigensolver.

## 0. Statement re-verification & status check (2026-07-22)

- Statement matches the original source form (Brouwer–Haemers, *Spectra of Graphs*):
  for all 1 ≤ t ≤ n, S_t(G) := Σ_{i=1}^t μ_i ≤ m + t(t+1)/2 (= m + binom(t+1,2)).
  Wikipedia + arXiv abstracts confirm the same normalization (Laplacian L = D − A,
  eigenvalues descending, m = |E|).
- **Important status finding**: arXiv:2606.12197 (submitted 2026-06-10, "On Brouwer's
  Laplacian conjecture") *claims a full proof*, via Grone–Merris–Bai restricted to split
  graphs, and claims equivalence between BC and GMB. Unrefereed as of July 2026 (0
  citations). Other 2025–26 wave papers (2503.11165, 2601.17575 approximate version,
  2607.03388, 2607.08452, 2607.17293 equality case) treat the conjecture as open.
  ⇒ We proceed with V3: an exhaustive n=11/12 verification is valuable either way
  (independent numerical support / a counterexample would refute the claimed proof).

## 1. Method

Pipeline: `nauty-geng -q n [res/mod] | brouwer_check n TMIN TMAX` (C, graph6 stdin).

Reductions (both machine-checked against brute force on small n):

1. **Proven cases skipped**: t ∈ {1, 2, n−1, n} are theorems (Haemers–Mohammadian–Tayfeh-
   Rezaie etc.); t = n is trivial (2m ≤ m + n(n+1)/2).
2. **Complement duality**: eigenvalues of L(Ḡ) are {0} ∪ {n − μ_i(G)}, giving
   S_t(Ḡ) = tn − 2m + S_{n−1−t}(G), and algebra shows
   BC(G, n−1−t) ⇔ BC(Ḡ, t) exactly ((n−1−t)(n−t)/2 = n(n−1)/2 − tn + t(t+1)/2).
   Since geng's output is complement-closed (all graphs up to iso), testing
   t ∈ {3, …, ⌊(n−1)/2⌋} over ALL graphs covers every t.
   n=11: test t ∈ {3,4,5} (covers 3–7; 8↔2 proven). n=12 full-range equivalent:
   either all graphs at t ∈ {3,4,5}, or the m ≤ 33 half at t ∈ {3..8}.
3. **Grone–Merris–Bai prune**: S_t ≤ Σ_{i≤t} d*_i (conjugate degrees, Bai 2011). If the
   conjugate partial sums already satisfy the Brouwer bound for all tested t, skip the
   eigensolve. (Prunes only ~4–5% — the Brouwer bound is much weaker than GMB pointwise,
   so most graphs fail the prune; also tried the dual prune via Bai on the complement at
   t' = n−1−t: zero additional prunes on n ≤ 10. Dead end noted.)
4. **Eigensolve**: LAPACK dsyev ('N') on the dense Laplacian (2.5× faster than a
   hand-rolled cyclic Jacobi: n=10 full run 41 s vs 104 s single-core). Margin
   = S_t − m − t(t+1)/2; anything > −1e−6 logged as NEAR (for exact high-precision
   recheck); > +1e−6 logged as VIOL. Float error for 12×12 integer Laplacians is
   ≪ 1e−9, and the observed margin gap is ~0.68, so thresholds are extremely safe.

## 2. Validation on known range (n ≤ 10)

Reproduces Brouwer's exhaustive result — zero violations:

| n  | #graphs     | eigensolved | near | viol | max float margin |
|----|-------------|-------------|------|------|------------------|
| 7  | 1,044       | 678         | 0    | 0    | −0.763932 |
| 8  | 12,346      | 9,224       | 0    | 0    | −0.726927 |
| 9  | 274,668     | 265,192     | 0    | 0    | −0.702929 |
| 10 | 12,005,168  | 11,475,350  | 0    | 0    | −0.686017 |

(max margin over the tested middle-t range t ∈ [3, ⌊(n−1)/2⌋]; slowly increasing toward 0
with n but far from a violation.)

## 3. n = 11 exhaustive run — COMPLETE, zero violations (frontier pushed)

Command: 8-way parallel `nauty-geng -q 11 r/8 | brouwer_lapack 11 3 5` (t ∈ {3,4,5} covers
all t by complement duality + proven cases). Wall time ≈ 14 min on 8 cores.

- Total graphs processed: **1,018,997,864** — exactly the known count of graphs on 11
  vertices (OEIS A000088(11)), confirming no shard loss.
- Eigensolved: 1,016,946,219 (GMB prune caught only ~0.2%). Near-misses (|margin| < 1e−6): 0.
  Violations: **0**.
- Max float margin over all *eigensolved* (non-GMB-pruned) graphs and t ∈ {3,4,5}: **−0.6734** (shard maxima: −0.673423487,
  −0.686017055, −0.702929456, −0.713784513, −0.726927137, −0.730608748, −0.817042866 ×2).
  Nothing remotely close to a violation; the closest-approach margin creeps up very slowly
  with n (−0.727 @ n=8 → −0.686 @ n=10 → −0.673 @ n=11).
  NB: exact equality S_t = m + t(t+1)/2 IS attained (split graphs, known); those graphs are
  GMB-pruned in the C pipeline (for them GMB = Brouwer bound exactly), so they never show
  up as float near-misses — maxmargin above is over the pruned-out remainder only.

⇒ **Brouwer's conjecture verified exhaustively for all graphs on 11 vertices** — extends
Brouwer's published exhaustive range (n ≤ 10).

### Independent second verifier (verify2.py)

Per methodology, a differently-written checker (Python/numpy, different graph6 parser,
numpy eigvalsh, NO pruning, NO t-range reduction — checks every t ∈ 1..n):

- n=8 full (12,346): viol=0, worst margin 0.000000000 (equality at t=7, g6 `G~~~~{`).
- n=9 full (274,668): viol=0, worst margin 0 (equality at t=6, `HEv]}~~`).
- n=10 full (12,005,168, 8-way): viol=0, worst margin 0 — equality graphs at t=4..7
  (e.g. `I??CFf~~w` at t=4). Confirms the C pipeline's prune/t-reduction is sound and
  that all equality cases are split-type graphs caught by the GMB prune or dual-proven t.

Sanity checks: (a) n=9 rerun with full t-range 3..7 (no complement-duality reduction)
gives identical results (0 viol, same global margin), validating the t-restriction;
(b) totals match A000088 for n = 7..11.

Margin-vs-density profile (n=10, t∈{3,4}): worst margins at m ≈ 16–18 of 45 (density ≈ 0.4),
but variation is mild (−0.69 to −0.94), so no edge-slice of n=12 can be safely skipped —
exhaustive sharding is required.

## 4. n = 12 push — FULL exhaustive run via 12 child sessions

Margins are too diffuse across densities to safely skip edge-slices, so we sharded the
FULL n=12 space (165,091,172,592 graphs, A000088(12)) across 12 parallel child Devin
sessions × 8 cores each = 96 geng subshards (`geng -q 12 s/96 | brouwer_lapack 12 3 5`,
t ∈ {3,4,5} covers all t by complement duality since t' = 11−t maps {3,4,5}→{8,7,6} and
t ∈ {1,2,9,10,11,12} are proven/trivial). Estimated ~3 h per child.

Child sessions (each pushes summaries to runs/P10-v3-n12-r<r>):
7272f2ac80a74ca187dae7e449d2c7d1, e27fba857c5c42b8a3fa5d11ae590b2a,
a9d51e48dbee4aad92d3a4d39efd5d00, 70df3f75f44c4b549983ed3a5b04bf95,
4f2d15aa7f6643b48c9277d080e4ae9a, 538c709dd42d417e98bb9f7631ec8b47,
89f71dbf5c6f4e16862542252b4ac1b0, c4e4312e29014af1ab88f252efc41948,
9d99c86f4d194acfb7a6a075bad07b10, f1c86115ebbc4a7d854008b1b63f6ede,
5416463bf875462a9e98271f06f2982d, b7d094c030f946ab939ef3d44de1f614

(results appended below when shards report)

## STATUS

(final line appended at end of session)

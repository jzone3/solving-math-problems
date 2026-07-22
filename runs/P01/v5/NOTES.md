# P01 — Sheehan's Conjecture — V5 (literature-first) run notes

Session: https://app.devin.ai/sessions/99dad6f2feb447aaa6c9248967c720be
Branch: runs/P01-v5. Variant V5: digest the literature, locate exactly where 4-regular simple
escapes every known proof technique, derive structural necessary conditions on a counterexample,
then run a *targeted* search in the residual family.

## 0. Statement re-verification & openness check (2026-07-22)

- Statement matches the original framing (Sheehan 1975, Prague symposium proceedings; restated
  verbatim in Girão–Kittipassorn–Narayanan arXiv:1709.04895 Conjecture 1.2 and in
  Goedgebeur–Meersman–Zamfirescu arXiv:1812.05650 §3.1.4 Conjecture (S)):
  **"There is no uniquely hamiltonian 4-regular (simple) graph."** No paraphrase drift: the
  problem file's statement is exactly (S).
- Openness: arXiv full-text searches ("uniquely hamiltonian", "Sheehan"+"hamiltonian",
  "second hamiltonian cycle", sorted by date, through 2026-06) show NO paper resolving (S).
  Latest touching work: GJLSZ "Few hamiltonian cycles in graphs with one or two vertex degrees"
  (arXiv:2211.08105, JGT), Thomassen–Zamfirescu arXiv:2104.06347. Treated as OPEN as of
  July 2026.

## 1. Literature digest — where each technique breaks at r = 4

Papers pulled and read (PDFs → text): arXiv:1812.05650 (GMZ, Math. Comp. 2020),
arXiv:2211.08105 (GJLSZ 2022), arXiv:2104.06347 (Thomassen–Zamfirescu 2021),
arXiv:1709.04895 (GKN 2017), arXiv:2008.03173 (Van Cleemput–Zamfirescu).

### 1.1 Thomason's lollipop / parity (settles all odd r)
Smith/Thomason: in a graph all of whose vertices have ODD degree, every edge lies on an even
number of hamiltonian cycles → second HC. At r = 4 every vertex has even degree and the parity
argument gives nothing. The lollipop walk on 4-regular graphs can return to the start edge
(the walk graph is no longer an odd graph), so no parity certificate exists. This is the
fundamental parity obstruction: r = 4 is even.

### 1.2 Thomassen's h-independent dominating sets (r ≥ 300 → HSV r > 22)
Thomassen (JCTB 1998, Theorem 4 as stated in GJLSZ): if G has HC h and a set S that is
independent in (V, E(h)) and dominating in (V, E(G)\E(h)) — an *h-IDS* — then G has a second
HC (lollipop + parity on the auxiliary graph H = h ∪ E(G[S])). LLL guarantees an h-IDS for
r ≥ 300 (Thomassen), improved to r > 22 even (Haxell–Seamone–Verstraëte JGT 2007).
**Break at r = 4:** K5 already has NO h-IDS; Thomassen noted infinitely many 4-regular
hamiltonian graphs without h-IDS (all known families have small girth; GJLSZ Question 3 asks
whether large girth restores h-IDS at r = 4 — open). Also GJLSZ construct 5- and 6-regular
examples without h-IDS, so the method is dead for all small even r, not just 4.
**Consequence for a counterexample G with its unique HC h: G has no h-IDS.** This is a strong,
machine-checkable necessary condition (used as a filter below).

### 1.3 GKN long-second-cycle (asymptotic Sheehan)
GKN Theorem 1.1: δ(G) ≥ 3 + hamiltonian ⇒ second cycle of length ≥ n − cn^{4/5}. Poset/rotation
machinery produces a LONG cycle, not a spanning one; the deficit cn^{4/5} is real for their
method (they cannot close the last o(n) vertices). At small n the bound is vacuous
(n − cn^{4/5} < n needs enormous n to bite as "second HC"). So: any counterexample is
small-to-medium; no effective bound extracted for n ≤ 50.

### 1.4 Fleischner multigraphs & Entringer–Swart / (3,4)-regular graphs (tightness)
- Fleischner (JGT 2014): uniquely hamiltonian SIMPLE graphs of minimum degree 4 EXIST
  (non-regular). So "min degree 4" alone is not an obstruction — regularity is essential.
- Fleischner: uniquely hamiltonian 4-regular MULTIgraphs exist — simplicity is essential.
- Entringer–Swart 1980: uniquely hamiltonian simple graphs, all degrees 4 except two
  vertices of degree 3 ("(3,4)-regular"); GJLSZ Observation 5: smallest such have n = 18.
- (S) sits exactly at the intersection: 4-regular ∧ simple.

### 1.5 Exhaustive/computational frontier (GMZ 2020, GJLSZ 2022)
- (S) verified for ALL 4-regular graphs n ≤ 21 (genreg + HC counting); for girth ≥ 5,
  n ≤ 26 (GMZ Observation 3.9).
- GMZ Table 3: min #HC among hamiltonian 4-regular graphs: 144 at n ∈ {19,20,21} (girth 3);
  girth-4 minima grow (1600 at n=21); girth-5 minima grow fast (25299 at n=26). Striking:
  girth-3 minimum is FLAT (72→144 region), consistent with bounded-HC families.
- Thomassen–Zamfirescu 2021: infinite family of 4-regular Hamiltonian graphs with exactly
  216 HCs (Fig. 1 ring construction), and 4-regular 4-CONNECTED with constant #HC (two
  Petersen-modification blocks + Meredith K3,4 expansion). Kills Haythorpe's growth
  conjecture: #HC need NOT grow with n at r = 4. So counting/averaging lower-bound
  strategies cannot prove (S).

### 1.6 Where 4-regular simple escapes everything — synthesis
1. Parity (odd degree) — unavailable.
2. h-IDS/LLL — provably unavailable (no-h-IDS 4-regular families exist).
3. Asymptotic rotation methods — leave an n^{4/5} deficit.
4. Counting lower bounds — false in general (constant-216 family).
5. Exhaustive generation — compute wall at n = 21 (girth 5: n = 26).
Residual gap: n ∈ [22, ~50], and nothing known rules out a counterexample there. The
believers' evidence is thin: minima at fixed girth grow in n for girth ≥ 4, but girth-3
minima plateau at 144 with multiplicity growing (13–21 extremal graphs), i.e. lots of
near-flat structure to exploit.

## 2. Structural necessary conditions on a minimum counterexample G (with unique HC h)

Derived from the digest; each is machine-checkable and used to prune/steer the search.

(C1) n ≥ 22; if girth(G) ≥ 5 then n ≥ 27. [GMZ Obs. 3.9]
(C2) Chord structure: G = C_n ∪ F where C_n = h and F := G − E(h) is a 2-REGULAR simple
     graph on the same vertex set, edge-disjoint from h (no chord of h-length 1).
     So F is a disjoint union of "chord cycles"; searching (S) = searching 2-factors F.
(C3) No h-IDS: no S ⊆ V independent in (V,E(h)) (no two h-consecutive) and dominating in
     (V,F) (every v ∉ S has an F-neighbour in S). [Thomassen Thm 4]
(C4) Forbidden local pattern "parallel adjacent chords": chords (i,j) and (i+1,j+1)
     (h-indices mod n) cannot both be present — swapping them against h-edges
     (i,i+1),(j,j+1) yields a second HC: i →(F) j →(h,backwards) i+1 →(F) j+1 →(h) i.
     More such 2-chord switch patterns are detected computationally (exact check subsumes).
(C5) G is nonplanar. [Bondy–Jackson: uniquely hamiltonian planar graphs have a vertex of
     degree ≤ 3 — actually of degree 2 or 3; a 4-regular planar G is excluded.]
(C6) Every edge of h lies on an odd number of HCs in each "lollipop class"? — no usable
     parity at r=4; NOT used.
(C7) Equivalent reformulation via near-4-regular graphs: G is a counterexample iff
     G = H + uv where H is uniquely hamiltonian, all degrees 4 except deg(u)=deg(v)=3,
     u,v non-adjacent, and H has NO hamiltonian u–v path. (Adding uv creates exactly the
     HCs {ham u–v paths of H} ∪ {HCs of H}.) Entringer–Swart/GJLSZ graphs realize the
     degree condition at n = 18 — the residual question is killing all ham u–v paths.
     This is the V5 "residual family": ES-shaped graphs with no ham path between the two
     cubic vertices.

## 3. Attack plan (executed below)

A. Exact HC counter (standalone python, bitset backtracking with degree/connectivity
   pruning, early cutoff) — the verifier core.
B. Targeted annealed search over chord 2-factors F on C_n (state space per (C2)), n = 22–40,
   objective = #HC (cutoff-counted), hard-pruning (C4), steering bonus for (C3)-violating
   (i.e. no-h-IDS) candidates.
C. Residual-family search per (C7): anneal over (3,4)-regular-shaped graphs
   H = C_n + (2-factor minus one chord), tracking (#HC(H) − 1) + #hamPaths(u,v).
D. Any witness → solutions/P01/verify.py (independent, dependency-light).

Checkpoints below as the run progresses.

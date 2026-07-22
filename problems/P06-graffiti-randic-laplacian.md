# P06 — Graffiti 129/698: Laplacian eigenvalue deviation vs Randić index

**Statement (129).** For every graph G, the standard deviation of the Laplacian eigenvalues is
at most R(G) = Σ_{uv∈E} (d(u)d(v))^{−1/2} (the Randić index). (698 is an L²-norm variant.)
(Fajtlowicz, Written on the Wall conj. 129, 698; open rows in Roucairol–Cazenave 2025 Table 1;
reference invariant code: github.com/RoucairolMilo/refutationGBR.)

**Why it matters.** Links Laplacian spread and the Randić index — two heavily studied chemical
graph theory invariants — with ZERO dedicated literature. A refutation lands in an active
(MATCH-journal) community.

**Status.** Exhaustive n ≤ 10 (Brewster–Dinneen–Faber 1995); MCTS to n = 50, 15 min single-core
(2025). **Near-miss family already visible**: stars have R = √(n−1) and Laplacian deviation ~√n —
an O(1) gap. Strongly suggests a counterexample among star-like graphs.

**Witness & verifier.** One graph; verify with one eigensolve + Randić sum (milliseconds).

**Prompt variants:**
1. **V1 star-like closed forms**: compute both sides in closed form for double stars, spiders,
   stars with pendant paths, complete split graphs (parameterized families at arbitrary n);
   optimize parameters analytically/numerically; verify any violation exactly (exact arithmetic).
2. **V2 annealed search**: local search (edge flips) from star seeds at n = 20–500, score =
   dev(Laplacian) − R(G); use sparse eigensolvers; exact-verify candidates.
3. **V3 large-n asymptotics**: analyze the asymptotic ratio for candidate families; if some
   family violates asymptotically, binary-search the smallest concrete n and verify.
4. **V4 exhaustive small-n**: geng-exhaust n = 11–13 (both conjectures); either a counterexample
   or a new exhaustive frontier; then trees only to n ≈ 24.
5. **V5 dual conjecture check**: first re-derive the precise WoW definitions of 129 and 698 from
   the original sources / refutationGBR Rust code (definitional ambiguity killed prior work);
   then run the harness on BOTH definitional readings across variants 1–2 machinery.

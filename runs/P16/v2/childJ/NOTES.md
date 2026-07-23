# P16 childJ — session notes (Conjecture H attack)

**Bottom line: PROOF INCOMPLETE, no counterexample.** Rigorous content in
`PROOF_H.md`. Three headline outcomes:

1. **Reduction sharpened**: Conjecture H ⇐ **Conjecture J**, a pairwise
   statement about the 2-ball data (z1, zs, s, ρ₀) of two edges, with the
   level ρ ranging over the whole ray ρ ≥ max(ρ₀(e), ρ₀(f)) — not just the
   graph's own R. Verified: all 273k connected graphs n ≤ 9 (all pairs, all
   ρ, exact quadratic minimization), all trees n ≤ 16, the childE 198 hard
   graphs, 400 random graphs n ≤ 60. Zero violations. Proof of J ⇒ H in
   PROOF_H §2 (uses clause (b) strictness for the c > −min s corner).
2. **Decoupling refuted**: there is NO rule c = φ(R) (childE/childH's failed
   closed forms are special cases): trees T₁ = `HkE?K?@` and
   T₂ = `Li_GS?@?S??@?A` both have R = 14 but exact feasible intervals
   [−21/10, ∞) and [−16/7, −11/5], which are disjoint. Found via pooled
   cross-graph envelopes (exp8–exp13); this is THE structural obstruction and
   any proof must formalize why the two configurations exclude each other
   within one graph at R = 14 (gluing experiments exp15: every path-join
   raises R to ≥ 16 or breaks a binding 2-ball; the 2-ball of a binding edge
   pins m-values ~3 steps into the graph).
3. **New identities** make everything 2-local and explicit:
   z1_e = (s_e−2)² + T_e, arg44_e = (s_e−2)² + (dᵢ−dⱼ)² + 2(mᵢmⱼ−dᵢdⱼ),
   T_e = Σ_{k∼i,k≠j}(d_k−dⱼ) + Σ_{l∼j,l≠i}(d_l−dᵢ), and the uniform ψ-form
   ψ_g(ρ) = −s_g + w_g/(ρ − z1_g) (w = zs − s·z1) for both bound types.

## Also established

- Structural facts (1-ball local, verified n ≤ 8 + trees + hard sets):
  σ ≤ 0 ⇒ κ ≤ 0; (s−2)² ≤ ρ ⇒ z1 ≤ ρ; min-U at a max-s edge (exp4, exp6).
- **Lemma P** (proved + sympy): pendant edges (leaf + degree-2 inner vertex)
  never impose positive lower bounds — sample of the general local method.
- 1-ball pairwise version of J is FALSE (`HhOK?E?` n=9 etc.) — 2-ball minimal.
- Vertex-space certificates (N = Q−2I, x = d+t) FAIL (26 graphs δ≥2 n≤8):
  the line-graph formulation is essential (exp2).
- No fixed c works for trees; c = −3/2 fails only T₂ among trees n ≤ 17.

## Pitfalls for successors

- exp10/exp11/exp16 import-guard: scripts must use `if __name__ == "__main__"`
  (exp11 imports exp10; exp14/16 import exp11's rand_graph).
- The pooled cross-graph envelope has exactly ONE conflicting gridpoint
  (ρ = 14, `combine_env.py`) — that is not a bug; it's discovery #2.
- Clause (a) q(ρ) is quadratic in ρ: check both endpoints AND the interior
  stationary point when the leading coeff (s_e − s_f) is positive.
- Strictness matters only at the −min s corner (clause b); everywhere else
  closed inequalities suffice.
- All scans float64 tol 1e−7/1e−9; T₁/T₂ interval endpoints and the hard-set
  runs are exact rational (`exp1_structure.py`, Fraction arithmetic).

## Route map (ranked)

1. Prove V1/V2 (PROOF_H §4) by the Lemma P mechanism — bounded case bash
   over 1-ball configurations; this settles clause (b) and the κ/σ signs.
2. Formalize the T₁/T₂ exclusion: given a lower-binding f with L_f(ρ) > −2−ε
   and an upper-binding e with U_e(ρ) < −2+ε in the same graph, derive a
   contradiction from the pinned m-values (both configs force degree data up
   to distance 3; their coexistence inflates some arg44 beyond ρ).
3. If stuck, ord4 with y = s + c (childH route #4) — untested, same linear
   shape, might have enough extra slack to admit a c = φ(R) rule (the ord2
   refutation here does NOT apply to ord4 a priori).

**PROOF NOT COMPLETE. Conjecture H stands, now reduced to Conjecture J.**

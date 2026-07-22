# P02 — Brandt's Regular Supergraph Conjecture

**Statement.** If G is maximal triangle-free with δ(G) ≥ n/3, then G has a regular triangle-free
supergraph obtained by vertex multiplications (expanding vertices into independent sets that
inherit neighborhoods). (Brandt, Discrete Math. 251 (2002) 33–46;
dwest.web.illinois.edu/openp/regsup.html)

**Why it matters.** Was Brandt's route to "δ > n/3 triangle-free ⇒ 4-colorable" (that part later
proved by Brandt–Thomassé), but the regular-supergraph statement — which includes the boundary
δ = n/3 — remains open on West's list. Zero recorded compute.

**Witness & verifier.** A maximal triangle-free graph G with δ ≥ n/3 for which the integer
system {x_v ≥ 1, Σ_{u∈N(v)} x_u = d constant ∀v} is infeasible for every plausible d.
Verify: small ILP feasibility per d; infeasibility certified by Farkas/exhaustion over d range.

**Status.** No computational attack in the literature. The δ = n/3 equality cases (where
Brandt–Thomassé blow-up structure may fail) are the interesting zone.

**Prompt variants:**
1. **V1 exhaustive sweep**: generate all maximal triangle-free graphs with δ ≥ n/3 up to n ≈ 22–25
   (nauty/geng with triangle-free + degree pruning, or the specialized MTF generator); for each,
   run the multiplication-ILP over all d; report any infeasible instance or a verified frontier.
2. **V2 boundary-focused**: characterize and enumerate only δ = n/3 tight cases (n divisible by 3);
   study which Andrásfai/Vega blow-up structures survive at equality and hunt failures there.
3. **V3 ILP-duality**: treat the multiplication system as the object — search for graphs whose
   neighborhood hypergraph admits a Farkas certificate; use LP duality to guide a local search
   over maximal triangle-free graphs toward infeasibility.
4. **V4 SAT hybrid**: encode "maximal triangle-free ∧ δ ≥ n/3 ∧ multiplication system infeasible
   for all d ≤ D" as a two-level search (SAT outer, ILP inner oracle) at n = 15–24.
5. **V5 literature-first**: read Brandt 2002 + Brandt–Thomassé structure theorem carefully; decide
   whether the theorem actually implies the conjecture for δ > n/3 (leaving only equality); then
   attack only the genuinely open residual class.

# Tweet — P02 (Brandt regular supergraph, West's version, refuted)

**Main tweet:**

Another one: the "regular supergraph" conjecture on Douglas West's open problems list (from Brandt, ~2002) is false — and the minimal counterexample has just 9 vertices.

Claim: any maximal triangle-free graph with min degree ≥ n/3 can be made regular by cloning vertices. This graph says no.

**Thread reply 1:**

The cute part: "can it be made regular by cloning?" is secretly a linear program (clone counts x_v must satisfy Σ_{u~v} x_u = d at every vertex). Infeasibility comes with an exact Farkas certificate — a machine-checkable proof of impossibility, no search needed to verify.

**Thread reply 2:**

Nuance for the specialists: Brandt's original conjecture used strict min degree > n/3, and that version was later *proved* (Brandt–Thomassé). The boundary case δ = n/3 is what West's list records as open — and it fails immediately, at the smallest conceivable size, with an infinite family n = 9t behind it. [repo link]

**Graphic:** p02_brandt.png

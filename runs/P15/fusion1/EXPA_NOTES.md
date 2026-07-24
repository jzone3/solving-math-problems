# Experiment A — fusion1

Date: 2026-07-24

## Engine

`fusion_cover.py` combines the exact-gain CRT/tree `fc_tree2.Builder` with
the fresh-prime 2-chain finisher from `toolkit/engine_e.py`.  Greedy residuals
are retained as exact `(residue, modulus)` cells.  The first residual cell for
a given modulus can use the ordinary bare `M*2^k` finisher ladder.  Repeated
`M` values are routed through an odd fresh-prime prefixed chain, with all
moduli tracked in the finisher's global registry.

The acceptance path remains exact: no float is used to accept a class, and
the intended output is checked by both toolkit verifiers before being called a
witness.

## Runs

No complete witness was produced in this experiment.  Therefore no
`witness_m*.json` is present and there are no verifier PASS lines to claim.
As an explicit negative check, the saved M=17 partial was rejected by the
first verifier with:

```
FAIL: integer not covered (sampling): -350831266824411604767564875161
```

It is a partial artifact, not a witness; it was not accepted or renamed as
`witness_m17.json`.  The second verifier was also started on this partial but
did not finish promptly because subtraction cells expand on the incomplete
cover.

### M=17, N=4,410,806,400

Factoring profile: `2^7,3^4,5^2,7,11,13,17`; 1,904 divisor candidates;
reciprocal sum over eligible divisors 1.865425.

With a 20-second greedy cap:

```
  chosen=88 mass=0.10346 frags=7349165 unused=1816 t=15s
TIMEOUT mass=0.06334 frags=5186258 chosen=129
GREEDY ok=False chosen=129 mass=0.0633401595228 residual=5186258 elapsed=20.0s
```

The residual closer was not attempted to completion: millions of exact cells
remain, and the per-cell fresh-prime closure is not computationally viable.
A 10-second run on the same profile reached 9,148,925 residual cells and
failed at residual #2 (`a=549, M=235620`) with the unprefixed same-M supply
path; this motivated the prefixed-chain implementation.

### M=18, N=4,410,806,400

Same factoring profile; 1,903 divisor candidates; reciprocal sum 1.806601.

With a 20-second greedy cap:

```
  chosen=141 mass=0.060238 frags=5105322 unused=1762 t=15s
TIMEOUT mass=0.03794 frags=3680718 chosen=197
GREEDY ok=False chosen=197 mass=0.0379351689523 residual=3680718 elapsed=20.0s
```

Again, the residual is far too large for independent finisher calls.

## Honest conclusion

The fusion did not push the verified frontier past m=16; it reached no
verified m=17 or m=18 witness.  The exact-gain greedy phase is substantially
better than a naive flat greedy in class scoring, but at these profiles it
stalls with millions of fragments and residual density between 0.038 and
0.063.  The fresh-prime finisher is useful for isolated thin cells, but does
not constitute a practical residual closer at this fragmentation scale.

The central remaining obstruction is not merely direct-ladder modulus
collision.  Routing a repeated-M cell through a distinct odd prefix creates
an odd-prime sibling tree; recursively closing its siblings reproduces the
same resource contention and can branch explosively.  A successful follow-up
needs shared residual-set recipes or a bounded repair phase that reduces the
number of residual cells by several orders of magnitude before invoking the
finisher.

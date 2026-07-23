"""Structure-targeted family search around known weighted extremal examples.

Weighted counterexamples (Schrijver 1980; Cornuejols-Guenin 2002) cannot be
simulated unweighted directly (weight-0 arcs have no unweighted analogue),
but we can probe the *neighborhood* of these structures unweighted:

Family A (weight scaling): weight-1 arc -> t parallel arcs, weight-0 arc -> 1
  arc, for t = 1..5. Also the subdivided variant where each of the t parallel
  copies is subdivided once (path of length 2 through a fresh vertex), which
  breaks the interchangeability of parallel copies.

Family B (generalized Schrijver rings): the Schrijver example is 3 alternating
  "solid paths" of length 3 arranged in a ring of 2k hexagon vertices with an
  inner ring + radial dashed arcs. Generalize to r solid paths (r = 3,5,7 odd)
  on an outer/inner ring of 2r vertices, same wiring pattern, then apply the
  weight-scaling of Family A for t = 1..3.

Every candidate is checked exactly: tau by dicut enumeration, nu by the exact
lazy-dicut ILP. Any nu < tau prints '!!! GAP'.
"""

import sys
import time

from woodall import all_dicuts, max_packing, condense_multi, min_dicut_flow
from schrijver_instance import N as SN, ARCS_W1, ARCS_W0


def scale_instance(n, arcs_w1, arcs_w0, t, subdivide=False):
    """w1 arc -> t parallel copies (optionally each subdivided), w0 -> 1 arc."""
    arcs = list(arcs_w0)
    nv = n
    for (u, v) in arcs_w1:
        for _ in range(t):
            if subdivide:
                arcs.append((u, nv))
                arcs.append((nv, v))
                nv += 1
            else:
                arcs.append((u, v))
    return nv, arcs


def ring_instance(r):
    """Generalized Schrijver ring with r solid paths on 2r outer + 2r inner
    vertices. Outer ring O_0..O_{2r-1}, inner ring I_0..I_{2r-1}.

    Mirrors the r=3 pattern: solid arcs O_{2j+1}->O_{2j+2}, O_{2j+1}->I_{2j},
    I_{2j+3}->I_{2j+2}(?) -- we use the direct generalization:
      solid: O_{2j+1}->O_{(2j+2)%2r}, O_{2j+1}->I_{2j}, I_{(2j+2)%2r}->I_{2j+... }
    Simpler faithful generalization: for j in range(r):
      a_j: O_{2j}->O_{2j+1 mod},  b_j: O_{2j}->I_{2j+1 mod}, c_j: I_{2j-1}->I_{2j+1}?
    To stay honest we just generalize the *dashed* wiring exactly like r=3:
      dashed outer: O_{2j}->O_{2j-1}, dashed inner: I_{2j}->I_{2j+1},
      radial: O_i -> I_i for all i;
      solid: O_{2j+1}->O_{2j+2}, O_{2j+1}->I_{2j+1}? -- see code below.
    """
    n = 4 * r
    O = list(range(2 * r))
    I = list(range(2 * r, 4 * r))
    m = 2 * r
    solid, dashed = [], []
    for j in range(r):
        a = O[(2 * j + 1) % m]
        solid.append((a, O[(2 * j + 2) % m]))          # along outer ring
        solid.append((a, I[(2 * j + 1) % m]))          # into inner ring
        solid.append((I[(2 * j) % m], I[(2 * j + 1) % m]))  # along inner ring
        dashed.append((a, O[(2 * j) % m]))             # outer back-arc
        dashed.append((I[(2 * j + 2) % m], I[(2 * j + 1) % m]))  # inner back-arc
    for i in range(m):
        dashed.append((O[i], I[i]))                    # radial
    return n, solid, dashed


def check(name, n, arcs, tau_hi=10):
    n2, arcs2 = condense_multi(n, tuple(arcs))
    try:
        cuts = all_dicuts(n2, arcs2)
        tau = min(len(c) for c in cuts) if cuts else None
    except ValueError:
        tau = min_dicut_flow(n2, arcs2)
    if tau is None:
        print(f"{name}: strongly connected after condensation, skip", flush=True)
        return
    if tau > tau_hi:
        print(f"{name}: tau={tau} > {tau_hi}, skip ILP", flush=True)
        return
    t0 = time.time()
    _, nu = max_packing(n2, arcs2, tau=tau, time_limit=600)
    dt = time.time() - t0
    tag = "!!! GAP" if nu < tau else "ok"
    print(f"{name}: n={n2} m={len(arcs2)} tau={tau} nu={nu} "
          f"[{dt:.1f}s] {tag}", flush=True)
    if nu < tau:
        print("WITNESS", n2, sorted(arcs2), flush=True)


def main():
    # Family A: scaled Schrijver
    for t in range(1, 6):
        n, arcs = scale_instance(SN, ARCS_W1, ARCS_W0, t)
        check(f"schrijver-scaled t={t}", n, arcs)
    for t in range(1, 4):
        n, arcs = scale_instance(SN, ARCS_W1, ARCS_W0, t, subdivide=True)
        check(f"schrijver-scaled-subdiv t={t}", n, arcs)
    # Family B: generalized rings, scaled
    for r in (3, 5, 7):
        n, solid, dashed = ring_instance(r)
        for t in range(1, 4):
            nn, arcs = scale_instance(n, solid, dashed, t)
            check(f"ring r={r} t={t}", nn, arcs)
        for t in range(1, 3):
            nn, arcs = scale_instance(n, solid, dashed, t, subdivide=True)
            check(f"ring-subdiv r={r} t={t}", nn, arcs)


if __name__ == "__main__":
    main()

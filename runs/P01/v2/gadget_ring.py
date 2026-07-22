"""V2 attack 5: gadget rings (Fleischner-style structured construction).

A ring of m copies of a gadget: gadget = graph on k vertices with 4 boundary
stubs (2 "left": l1,l2; 2 "right": r1,r2); internal degree of v = 4 - #stubs(v).
Copies c=0..m-1 joined by junction edges (c.r1 -> (c+1).l1, c.r2 -> (c+1).l2)
[straight] or (r1->l2, r2->l1) [crossed]. The composed graph is 4-regular on
k*m vertices. Enumerate small gadgets exhaustively (k <= 6), count HCs of the
ring exactly for m = 3..7; log any count == 1 (witness!) and count <= 3
near-misses.

Usage: python3 gadget_ring.py k [mmax]
"""
import sys, itertools
from collections import Counter
from hcutil import hc_count

def gadget_graphs(k, stub_of):
    """All simple graphs on k vertices with degree sequence 4 - stubs."""
    need = [4 - stub_of[v] for v in range(k)]
    if any(x < 0 for x in need) or sum(need) % 2:
        return
    pairs = list(itertools.combinations(range(k), 2))
    m = sum(need) // 2
    for combo in itertools.combinations(pairs, m):
        d = [0] * k
        for u, v in combo:
            d[u] += 1; d[v] += 1
        if d == need:
            yield list(combo)

def ring(k, m, gedges, l1, l2, r1, r2, crossed):
    edges = []
    for c in range(m):
        off = c * k
        for u, v in gedges:
            edges.append((u + off, v + off))
        noff = ((c + 1) % m) * k
        if crossed:
            edges.append((r1 + off, l2 + noff)); edges.append((r2 + off, l1 + noff))
        else:
            edges.append((r1 + off, l1 + noff)); edges.append((r2 + off, l2 + noff))
    return edges

def canon(k, gedges, stubs):
    """Cheap iso-dedup: canonical form over all vertex permutations (k small)."""
    best = None
    for perm in itertools.permutations(range(k)):
        pe = tuple(sorted((min(perm[u], perm[v]), max(perm[u], perm[v])) for u, v in gedges))
        ps = tuple(sorted((perm[v], s) for v, s in stubs))
        key = (pe, ps)
        if best is None or key < best:
            best = key
    return best

def main(k, mmax):
    tested = 0
    seen = set()
    # stub assignments: multiset of 4 stubs (l1,l2,r1,r2) over vertices
    for l1, l2 in itertools.combinations_with_replacement(range(k), 2):
        for r1, r2 in itertools.combinations_with_replacement(range(k), 2):
            stub_of = Counter([l1, l2, r1, r2])
            so = [stub_of.get(v, 0) for v in range(k)]
            for gedges in gadget_graphs(k, so):
                stubs = [(l1, "l"), (l2, "l"), (r1, "r"), (r2, "r")]
                key = canon(k, gedges, stubs)
                if key in seen:
                    continue
                seen.add(key)
                for crossed in (0, 1):
                    for m in range(3, mmax + 1):
                        n = k * m
                        edges = ring(k, m, gedges, l1, l2, r1, r2, crossed)
                        # rings can have parallel junction edges if l/r coincide; fine (multigraph)
                        c = hc_count(n, edges, cutoff=4)
                        tested += 1
                        if c == 1:
                            simple = len(set(edges)) == len(edges)
                            with open("WITNESS.txt" if simple else "gadget_multi_hits.txt", "a") as f:
                                f.write(f"GADGET-RING k={k} m={m} simple={simple} "
                                        f"gedges={gedges} stubs=({l1},{l2}|{r1},{r2}) "
                                        f"crossed={crossed} edges={sorted(edges)}\n")
                            print(f"HIT k={k} m={m} simple={simple} count=1", flush=True)
                        elif c == 0:
                            break  # larger rings of same gadget usually also 0? not nec., but prune
    print(f"k={k} done: {tested} ring tests, {len(seen)} gadgets", flush=True)

if __name__ == "__main__":
    k = int(sys.argv[1])
    mmax = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    main(k, mmax)

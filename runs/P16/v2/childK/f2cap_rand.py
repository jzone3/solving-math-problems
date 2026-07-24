"""Random + adversarial stress test for F2'' (capped sigma), n up to ~150.

Generators: G(n,p); random regular +/- edge perturbations; K_{a,b} minus
random matching; BA; windmill with cliques replaced; hybrid = windmill glued
to a random regular graph via one vertex; hub + mixed gadgets.
All pruned to the delta>=2 core (iteratively delete deg<=1), keep the largest
connected component.
"""
import numpy as np
import networkx as nx
from common import build
from graphs import windmill


def core(G):
    G = G.copy()
    while True:
        low = [v for v in G if G.degree(v) <= 1]
        if not low:
            break
        G.remove_nodes_from(low)
    if len(G) < 3:
        return None
    comp = max(nx.connected_components(G), key=len)
    G = G.subgraph(comp).copy()
    if len(G) < 3 or min(dict(G.degree()).values()) < 2:
        return None
    return nx.to_numpy_array(G)


def gens(rng):
    while True:
        r = rng.integers(0, 6)
        if r == 0:
            n = int(rng.integers(10, 150))
            p = rng.uniform(1.5 / n, 4.0 / n) if rng.random() < 0.5 else rng.uniform(0.05, 0.5)
            yield nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
        elif r == 1:
            n = int(rng.integers(8, 120))
            d = int(rng.integers(2, min(8, n - 1)))
            if (n * d) % 2:
                n += 1
            G = nx.random_regular_graph(d, n, seed=int(rng.integers(1 << 30)))
            for _ in range(int(rng.integers(0, 5))):
                if G.number_of_edges() > n:
                    e = list(G.edges())[int(rng.integers(G.number_of_edges()))]
                    G.remove_edge(*e)
            yield G
        elif r == 2:
            a = int(rng.integers(2, 8))
            b = int(rng.integers(a, 100))
            G = nx.complete_bipartite_graph(a, b)
            es = list(G.edges())
            for e in [es[i] for i in rng.choice(len(es), size=int(rng.integers(0, a)), replace=False)]:
                G.remove_edge(*e)
            yield G
        elif r == 3:
            n = int(rng.integers(10, 120))
            yield nx.barabasi_albert_graph(n, int(rng.integers(2, 5)), seed=int(rng.integers(1 << 30)))
        elif r == 4:  # hybrid: windmill + random regular glued at hub
            k = int(rng.integers(5, 40))
            d = int(rng.integers(3, 7))
            nr = int(rng.integers(d + 1, 40))
            if (nr * d) % 2:
                nr += 1
            W = nx.from_numpy_array(windmill(k))
            R = nx.random_regular_graph(d, nr, seed=int(rng.integers(1 << 30)))
            G = nx.disjoint_union(W, R)
            G.add_edge(0, 2 * k + 1)
            G.add_edge(0, 2 * k + 2)
            yield G
        else:  # hub + gadgets with medium m
            k = int(rng.integers(4, 25))
            c = int(rng.integers(3, 7))
            G = nx.Graph()
            G.add_node(0)
            pos = 1
            for _ in range(k):
                vs = list(range(pos, pos + c))
                pos += c
                G.add_cycle = None
                for a2 in range(c):
                    G.add_edge(vs[a2], vs[(a2 + 1) % c])
                    if rng.random() < 0.8:
                        G.add_edge(0, vs[a2])
            yield G


def main():
    rng = np.random.default_rng(7)
    tot = 0
    worst = {2: (1e18, None), 4: (1e18, None)}
    nbad = {2: 0, 4: 0}
    for G in gens(rng):
        A = core(G)
        if A is None:
            continue
        bd = build(A)
        d, m = bd["d"], bd["m"]
        for cap in (2, 4):
            s = np.maximum(d - 4 + np.minimum(m, d + cap), 0.0)
            D = np.diag(s)
            Ms = 2 * D + 4 * np.eye(bd["n"]) - bd["Q"] - D @ bd["H"] @ D
            e = np.linalg.eigvalsh(Ms)[0]
            if e < worst[cap][0]:
                worst[cap] = (e, (bd["n"], tot))
            if e < -1e-7:
                nbad[cap] += 1
        tot += 1
        if tot % 500 == 0:
            print(f"tot={tot} cap2: bad={nbad[2]} worst={worst[2]}  "
                  f"cap4: bad={nbad[4]} worst={worst[4]}", flush=True)
        if tot >= 4000:
            break
    print(f"FINAL tot={tot} cap2: bad={nbad[2]} worst={worst[2]}  "
          f"cap4: bad={nbad[4]} worst={worst[4]}")


if __name__ == "__main__":
    main()

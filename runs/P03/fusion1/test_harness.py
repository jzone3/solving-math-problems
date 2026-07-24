"""Sanity tests for harness.py on known instances."""
from harness import (tau, has_k_disjoint_dijoins, rho, is_planar,
                     is_source_sink_connected, minimal_dicuts, check_candidate)


def t_path():
    # directed path 0->1->2: tau=1, packs 1
    n, arcs = 3, [(0, 1), (1, 2)]
    assert tau(n, arcs) == 1
    assert has_k_disjoint_dijoins(n, arcs, 1)
    print("PASS path")


def t_bipartite():
    # 3-regular bipartite, all arcs from side A={0,1,2} to B={3,4,5} (K33)
    arcs = [(a, b) for a in range(3) for b in range(3, 6)]
    n = 6
    assert tau(n, arcs) == 3
    assert has_k_disjoint_dijoins(n, arcs, 3)
    assert not has_k_disjoint_dijoins(n, arcs, 4)
    print("PASS K33 orientation")


def t_two_disjoint_paths():
    # two vertex-disjoint arcs: dicut {both} at various U; tau: U={0,2} closed?
    # 0->1, 2->3 is weakly disconnected: U={0,1} is closed with empty
    # delta+, i.e. the empty dicut exists -> tau = 0.
    n, arcs = 4, [(0, 1), (2, 3)]
    assert tau(n, arcs) == 0
    print("PASS disjoint arcs")


def t_schrijver():
    # Schrijver's Edmonds-Giles counterexample digraph (unweighted version
    # must still pack tau dijoins if tau small; here we just smoke-test that
    # the routines run on a ~14-arc digraph and Woodall holds unweighted).
    # Digraph from Schrijver 1980 as commonly drawn: we use a stand-in
    # 7-vertex DAG.
    arcs = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 5), (4, 6), (5, 6),
            (3, 6), (0, 3), (3, 5), (4, 3)]
    n = 7
    t = tau(n, arcs)
    assert t is not None and t >= 1
    assert has_k_disjoint_dijoins(n, arcs, t), f"Woodall fails?! tau={t}"
    print(f"PASS smoke DAG tau={t}")


def t_check_candidate():
    arcs = [(a, b) for a in range(3) for b in range(3, 6)]
    r = check_candidate(6, arcs, 3, verbose=True)
    assert r['tau'] == 3 and r['packs'] and not r['counterexample']
    assert r['rho'] == 0  # 3-regular bipartite: excess ±3 ≡ 0 mod 3
    assert r['ss_connected']
    print("PASS check_candidate", r)


if __name__ == "__main__":
    t_path()
    t_bipartite()
    t_two_disjoint_paths()
    t_schrijver()
    t_check_candidate()
    print("ALL PASS")

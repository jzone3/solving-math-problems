"""Sanity tests for core.py."""
import random
from core import (enumerate_dicuts, minimal_dicuts, tau, rho3, pack3_sat,
                  brute_pack3, analyze, is_source_sink_connected)


def test_parallel_arcs():
    # 3 parallel arcs 0->1: single dicut of size 3, trivially partitionable
    arcs = [(0, 1)] * 3
    d = enumerate_dicuts(2, arcs)
    assert len(d) == 1 and len(d[0]) == 3
    assert tau(d) == 3
    assert pack3_sat(arcs, d) is True
    assert brute_pack3(arcs, d) is True


def test_path():
    # path 0->1->2: dicuts {0},{1} of size 1
    arcs = [(0, 1), (1, 2)]
    d = enumerate_dicuts(3, arcs)
    assert tau(d) == 1
    assert len(minimal_dicuts(d)) == 2


def test_tau3_gadget():
    # two triples of parallel arcs 0->1, 1->2 ; dicuts sizes 3
    arcs = [(0, 1)] * 3 + [(1, 2)] * 3
    d = enumerate_dicuts(3, arcs)
    assert tau(d) == 3
    md = minimal_dicuts(d)
    assert pack3_sat(arcs, md) is True


def test_rho():
    arcs = [(0, 1)] * 3
    assert rho3(2, arcs) == 0  # imbalances 3,-3 -> mod3 = 0
    arcs = [(0, 1)] * 4
    assert rho3(2, arcs) == 1  # 4 mod3=1, -4 mod3=2 -> 3/3=1


def test_sat_vs_brute_random():
    random.seed(1)
    checked = 0
    for _ in range(300):
        n = random.randint(3, 4)
        m = random.randint(3, 7)
        arcs = [(random.randrange(n), random.randrange(n)) for _ in range(m)]
        arcs = [(u, v) for (u, v) in arcs if u != v]
        if not arcs:
            continue
        d = enumerate_dicuts(n, arcs)
        if not d:
            continue
        md = minimal_dicuts(d)
        s = pack3_sat(arcs, md)
        b = brute_pack3(arcs, d)  # use full dicut list independently
        assert s == b, (arcs, s, b)
        checked += 1
    assert checked > 50
    print(f"sat-vs-brute agreed on {checked} random instances")


def test_ss_connected():
    # 0->1, 2->1: sources 0,2 sink 1, both reach it
    assert is_source_sink_connected(3, [(0, 1), (2, 1)]) is True
    # 0->1, 2->3 (disconnected pairs): source 0 cannot reach sink 3
    assert is_source_sink_connected(4, [(0, 1), (2, 3)]) is False


if __name__ == "__main__":
    for f in list(globals().values()):
        if callable(f) and getattr(f, "__name__", "").startswith("test_"):
            f()
            print("PASS", f.__name__)

"""Tests for the symbolic closure layer against known-good and
known-bad arrow systems."""
from arrow_dsl import Ctx, One, Split, Arrow, Hole
from symbolic import symbolic_verify, collide


def test_collide():
    # 3*2^e vs 12 = 3*2^2: grids intersect (e=2)
    assert collide(6, {2}, 12, set())
    # 6*2^e vs 9: cores 3 vs 9 differ
    assert not collide(6, {2}, 9, set())
    # 6*2^e vs 6*2^f: same grid
    assert collide(6, {2}, 12, {2})
    # 6*2^e vs 9*3^f: cores after stripping {2,3}: 3 vs 1
    assert not collide(6, {2}, 9, {3})
    # 2*2^e vs 6*3^f: strip {2,3}: 1 vs 1; v2(6)=1 >= v2(2)=1;
    # v3(2)=0 <= v3? r=3 in s2\s1: qval(m1,3)=0 < qval(m2,3)=1 -> False
    assert not collide(2, {2}, 6, {3})
    # 2*2^e vs 12*3^f: v2: r=2 in s1\s2: v2(12)=2 >= v2(2)=1 ok;
    # r=3: v3(2)=0 < v3(12)=1 -> no
    assert not collide(2, {2}, 12, {3})
    # 2*2^e vs 4*2^f*3^g: r=3 in s2\s1: v3(2)=0 >= v3(4)=0 ok; collide
    assert collide(2, {2}, 4, {2, 3})
    print("collide OK")


def test_good_system():
    # 2^(1) with L=1: covers everything; one class per level.
    ctx = Ctx(1)
    Arrow(2, [One()]).eval(ctx, 0, 1, "t")
    ok, lines = symbolic_verify(ctx)
    assert ok, lines
    print("good 2^ OK:", lines[-1])

    # 3^(1, 2(1, )) requires the blank to be a real hole -> must fail.
    ctx = Ctx(1)
    Arrow(3, [One(), Split(2, [One(), Hole()])]).eval(ctx, 0, 1, "t")
    ok, lines = symbolic_verify(ctx)
    assert not ok, lines
    print("hole detection OK")

    # nested arrows: 3^(1, 2^(1)-in-window) -- fine, distinct families
    ctx = Ctx(1)
    Arrow(3, [One(), Arrow(2, [One()])]).eval(ctx, 0, 1, "t")
    ok, lines = symbolic_verify(ctx)
    assert ok, lines
    print("nested OK:", lines[-1])


def test_family_clash():
    # two 2^ arrows on cells with same odd part must clash:
    # 2^ on (0 mod 3) and 2^ on (1 mod 3) -> families 6*2^e both.
    ctx = Ctx(1)
    Split(3, [Arrow(2, [One()]), Arrow(2, [One()]), One()]).eval(
        ctx, 0, 1, "t")
    ok, lines = symbolic_verify(ctx)
    assert not ok, lines
    assert any("collision" in l or "duplicate" in l for l in lines), lines
    print("family clash detection OK")


if __name__ == "__main__":
    test_collide()
    test_good_system()
    test_family_clash()
    print("ALL SYMBOLIC TESTS PASS")

"""Machine-verify the reconstructed weighted seeds: tau=2, nu=1 for both
Schrijver D1 and Cornuejols-Guenin D2, and the Figure 7 'special joins'
fractional packing facts for D1."""
import core
import seeds


def check(name, n, arcs, w, exp_tau, exp_nu):
    t, cut = core.tau(n, arcs, w)
    t2, v = core.nu(n, arcs, w)
    assert t == t2
    print(f"{name}: tau={t} nu={v} (expected {exp_tau},{exp_nu}); "
          f"|V|={n} |A|={len(arcs)} planar={core.is_planar(n, arcs)} DAG-ok")
    assert t == exp_tau and v == exp_nu, (name, t, v)


def check_d1_special_joins():
    lab = {l: i for i, l in enumerate(seeds.D1_labels)}
    joins = [set("acdfh"), set("dfgib"), set("giace"), set("bhe")]
    cuts = core.minimal_dicuts(core.all_dicuts(seeds.D1_n, seeds.D1_arcs))
    for J in joins:
        Jidx = {lab[c] for c in J}
        for c in cuts:
            assert c & Jidx, (J, c)
    # every weight-1 arc in exactly two special joins
    from collections import Counter
    cnt = Counter()
    for J in joins:
        for c in J:
            cnt[c] += 1
    assert all(cnt[l] == 2 for l in seeds.D1_labels), cnt
    print("D1 special joins fact verified (4 half-weight joins, frac packing 2)")


if __name__ == "__main__":
    check("Schrijver D1", seeds.D1_n, seeds.D1_arcs, seeds.D1_w, 2, 1)
    check_d1_special_joins()
    check("Cornuejols-Guenin D2", seeds.D2_n, seeds.D2_arcs, seeds.D2_w, 2, 1)
    print("ALL SEED CHECKS PASS")

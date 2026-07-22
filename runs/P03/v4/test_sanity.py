"""Sanity checks for woodall.py on instances with known answers."""
import sys
from woodall import (min_dicut, max_packing, all_dicuts, is_dijoin,
                     find_dicut_avoiding, pack)


def check(name, cond):
    print(("PASS" if cond else "FAIL"), name)
    if not cond:
        sys.exit(1)


# single arc: tau=1, nu=1
n, arcs = 2, [(0, 1)]
tau, nu = max_packing(n, arcs)
check("single arc tau=1", tau == 1)
check("single arc nu=1", nu == 1)

# directed path 0->1->2: dicuts {01},{12}; tau=1, nu=1 (J={01,12})
n, arcs = 3, [(0, 1), (1, 2)]
tau, nu = max_packing(n, arcs)
check("path tau=1", tau == 1)
check("path nu=1", nu == 1)

# two parallel arcs 0->1 doubled: tau=2, nu=2
n, arcs = 2, [(0, 1), (0, 1)]
tau, nu = max_packing(n, arcs)
check("parallel tau=2", tau == 2)
check("parallel nu=2", nu == 2)

# directed cycle: strongly connected -> no dicut
n, arcs = 3, [(0, 1), (1, 2), (2, 0)]
check("cycle no dicut", min_dicut(n, arcs) is None)

# complete bipartite orientation K_{2,2} all arcs from {0,1} to {2,3}:
# ideals of condensation... dicuts include all 4 arcs (U={0,1}), and
# {0}->: arcs (0,2),(0,3) size 2, similarly others; also U={0,1,2}: arcs
# from U to {3}: (0,3),(1,3) size 2. tau=2 and nu should be 2
n, arcs = 4, [(0, 2), (0, 3), (1, 2), (1, 3)]
tau, nu = max_packing(n, arcs)
check("K22 tau=2", tau == 2)
check("K22 nu=2", nu == 2)

# dijoin check: path, J={0} (arc 0->1) is not a dijoin (dicut {12} avoided)
n, arcs = 3, [(0, 1), (1, 2)]
check("not dijoin", not is_dijoin(n, arcs, [0]))
check("sep finds cut", find_dicut_avoiding(n, arcs, [0]) == frozenset({1}))
check("full dijoin", is_dijoin(n, arcs, [0, 1]))

# LY-style example: two disjoint arcs 0->1, 2->3 (weakly disconnected):
# dicuts: complicated (disconnected). tau via ideals; U={0} cut {a0};
# U={0,2} cut both; etc. tau=1... also empty dicut? U={0,1}: delta-(U)=0,
# delta+(U)=0 -> empty dicut, tau=0. Generators must keep weak connectivity.
n, arcs = 4, [(0, 1), (2, 3)]
check("disconnected gives tau=0", min_dicut(n, arcs) == 0)

print("ALL SANITY PASS")

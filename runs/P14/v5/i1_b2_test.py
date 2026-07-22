"""Test: for I1=(14,18;7,1,9;7,4), is the published restriction b2 = V*r2 = 14
(i.e. every block has at most one doubled element) derivable from the grand
two-point counting relaxation?  Force n_2 + n_3 >= 1 and check feasibility.
Also probe each instance: for each d, min/max attainable n_d at this level.
"""
import pulp
from grand_ilp import solve, INSTANCES

def probe(inst):
    name = inst[0]
    K = inst[6]
    for d in range(K//2 + 1):
        for sense, tag in [(1, "min"), (-1, "max")]:
            # re-solve with objective
            import grand_ilp
            st, n, P, prob = grand_ilp.solve(*inst)
            # instead: use solve with objective by patching after build is
            # awkward; do a fresh model with constraint-based bisection.
            break
        break

if __name__ == "__main__":
    inst = INSTANCES[0]
    # force some block with >= 2 doubles
    import grand_ilp
    # monkey-patch: add extra constraint by wrapping pulp problem creation
    orig = pulp.LpProblem.solve
    def patched_build():
        pass
    # simplest: copy solve body via extra constraint support
    st, n, P, prob = grand_ilp.solve(*inst, msg=False)
    print("I1 baseline:", st)
    # add n2+n3>=1 and resolve
    prob += n[2] + n[3] >= 1, "force_multi_double"
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=1200))
    print("I1 with n2+n3>=1:", pulp.LpStatus[prob.status])
    if pulp.LpStatus[prob.status] == "Optimal":
        print("   n_d =", {d: int(v.value()) for d, v in n.items() if v.value() and v.value() > .5})

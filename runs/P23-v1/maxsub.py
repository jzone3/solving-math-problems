"""Maximally substituted record: apply all 8 swaps simultaneously (they pairwise
compose in 26/28 cases; test the full set, backing off greedily on SAT).
Then: full criticality scan + swap scan around the new record variant."""
import pickle, random, sys
from coremin import solve_core, adj
PAIRS = [(47264,413),(620,347),(1674,300),(2731,220),(47058,415),(1666,301),(2472,217),(3452,356)]
g509 = set(range(509))
def unsat(S, tag='mx'):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=3600, tag=tag)
    return (st=='UNSAT'), keep
if __name__ == '__main__':
    sel = list(range(8))
    while True:
        W = {PAIRS[i][0] for i in sel}; V = {PAIRS[i][1] for i in sel}
        B = (g509 - V) | W
        ok,_ = unsat(B)
        print('subset', sel, len(B), 'UNSAT' if ok else 'SAT', flush=True)
        if ok:
            pickle.dump(sorted(B), open('gmax.pkl','wb'))
            print('MAX-SUBSTITUTED RECORD SAVED:', len(B), 'vertices,', len(sel), 'swaps', flush=True)
            break
        sel = sel[:-1]

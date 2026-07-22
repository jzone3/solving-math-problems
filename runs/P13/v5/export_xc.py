"""Export exact-cover instances for xcover.c, and decode its solutions.

Usage:
  python3 export_xc.py full <v> <k> [fix|nofix] > inst.txt   (prints fixed-cover
     hex mask on stderr)
  python3 export_xc.py semireg <name> > inst.txt
  python3 export_xc.py decode <mode> <args...> -- <idx...>   (verify a solution)
"""
import sys, itertools


def full_instance(V, K, fix=True):
    pts = list(range(V))
    items = {}
    for t in range(1, K):
        for x in pts:
            for y in pts:
                if x != y:
                    items[(t, x, y)] = len(items)

    def mask_of(block):
        m = 0
        for t in range(1, K):
            for i in range(K):
                m |= 1 << items[(t, block[i], block[(i + t) % K])]
        return m

    cands = []
    for sub in itertools.combinations(pts, K):
        first, rest = sub[0], sub[1:]
        for perm in itertools.permutations(rest):
            block = (first,) + perm
            cands.append((block, mask_of(block)))
    fixed = mask_of(tuple(range(K))) if fix else 0
    return len(items), cands, fixed


def semireg_instance(name):
    from semireg import SemiregEngine, CASES
    m, c, ui, k = CASES[name]
    eng = SemiregEngine(m, c, ui, k)
    cands = [(b, mk) for (b, mk) in eng.gen_candidates()]
    return eng.n_items, cands, 0, eng


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "full":
        V, K = int(sys.argv[2]), int(sys.argv[3])
        fix = (sys.argv[4] if len(sys.argv) > 4 else "fix") == "fix"
        n, cands, fixed = full_instance(V, K, fix)
        print(n, len(cands))
        for b, mk in cands:
            print(format(mk, 'x'))
        print(format(fixed, 'x') if fixed else '0', file=sys.stderr)
    elif mode == "semireg":
        n, cands, fixed, eng = semireg_instance(sys.argv[2])
        print(n, len(cands))
        for b, mk in cands:
            print(format(mk, 'x'))
        print('0', file=sys.stderr)
    elif mode == "decode":
        sub = sys.argv[2]
        sep = sys.argv.index('--')
        idxs = [int(x) for x in sys.argv[sep + 1:]]
        from pmdlib import check_pmd
        if sub == "full":
            V, K = int(sys.argv[3]), int(sys.argv[4])
            fix = (sys.argv[5] if len(sys.argv) > 5 else "fix") == "fix"
            n, cands, fixed = full_instance(V, K, fix)
            blocks = ([tuple(range(K))] if fix else []) + [cands[i][0] for i in idxs]
            print(blocks)
            print(check_pmd(blocks, V, K, 1))
        else:
            name = sys.argv[3]
            n, cands, fixed, eng = semireg_instance(name)
            blocks = []
            for i in idxs:
                blocks += eng.expand(cands[i][0])
            v = eng.m * eng.c + (1 if eng.use_inf else 0)
            print([cands[i][0] for i in idxs])
            print(check_pmd(blocks, v, eng.k, 1))

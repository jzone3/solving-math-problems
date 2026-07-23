"""Heule-style core-based minimization of a non-4-colorable subgraph."""
import pickle, random, subprocess, sys, time, os
from sat import color_cnf, write_cnf, KISSAT, DRATTRIM

POOL = os.environ.get('POOL', 'union.pkl')
allpts, E = pickle.load(open(POOL, 'rb'))
NALL = len(allpts)
adj = [set() for _ in range(NALL)]
for u, v in E:
    adj[u].add(v)
    adj[v].add(u)

def find_triangle(S):
    Sset = set(S)
    best = None
    for u in S:
        for v in adj[u] & Sset:
            if v <= u:
                continue
            for w in adj[u] & adj[v] & Sset:
                if w > v:
                    return (u, v, w)
    return None

def solve_core(S, seed=0, timeout=3600, tag='cm'):
    """Return (status, core_vertex_set or model)."""
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = find_triangle(S)
    tri2 = tuple(remap[x] for x in tri)
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    random.seed(seed)
    tmpdir = os.path.expanduser('~/p23/tmp')
    os.makedirs(tmpdir, exist_ok=True)
    base = f'{tmpdir}/{tag}_{seed}'
    cnf, drat, core = base + '.cnf', base + '.drat', base + '.core'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, '-q', f'--seed={seed}', cnf, drat],
                           capture_output=True, text=True, timeout=timeout)
        if 's UNSATISFIABLE' not in r.stdout:
            if 's SATISFIABLE' in r.stdout:
                return 'SAT', None
            return 'UNKNOWN', None
        r2 = subprocess.run([DRATTRIM, cnf, drat, '-c', core],
                            capture_output=True, text=True, timeout=timeout)
        if 's VERIFIED' not in r2.stdout:
            return 'NOVERIFY', None
        keep = set()
        with open(core) as f:
            f.readline()
            for line in f:
                for tok in line.split()[:-1]:
                    x = abs(int(tok))
                    keep.add(S[(x - 1) // 4])
    finally:
        for p in (cnf, drat, core):
            if os.path.exists(p):
                os.unlink(p)
    # triangle vertices must stay (their fixed colors are WLOG only if triangle present)
    keep |= set(tri)
    return 'UNSAT', keep

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    S = set(range(NALL))
    it = 0
    while True:
        it += 1
        t = time.time()
        st, keep = solve_core(S, seed=seed * 1000 + it, tag=f'cm{seed}')
        dt = round(time.time() - t, 1)
        if st != 'UNSAT':
            print(f'seed{seed} it{it}: {st} n={len(S)} {dt}s', flush=True)
            break
        print(f'seed{seed} it{it}: n={len(S)} -> core {len(keep)} {dt}s', flush=True)
        if len(keep) >= len(S):
            break
        S = keep
    pickle.dump(sorted(S), open(f'coremin_seed{seed}.pkl', 'wb'))
    print(f'seed{seed} FINAL {len(S)}', flush=True)

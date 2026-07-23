import pickle, time, sys
from multiprocessing import Pool
from sat import color_cnf, solve

pts, E = pickle.load(open('g509.pkl', 'rb'))
n = len(pts)
adj = [set() for _ in range(n)]
for u, v in E:
    adj[u].add(v)
    adj[v].add(u)

def find_triangle(banned):
    for u in range(n):
        if u in banned:
            continue
        for v in adj[u]:
            if v in banned or v <= u:
                continue
            common = adj[u] & adj[v] - banned
            for w in common:
                if w > v:
                    return (u, v, w)
    return None

def test_delete(dels):
    dels = set(dels) if not isinstance(dels, int) else {dels}
    keep = [x for x in range(n) if x not in dels]
    remap = {x: i for i, x in enumerate(keep)}
    E2 = [(remap[u], remap[v]) for u, v in E if u not in dels and v not in dels]
    tri = find_triangle(dels)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(keep), E2, 4, sym_clique=tri2)
    t = time.time()
    st, _ = solve(nvars, cls, timeout=600)
    return sorted(dels), st, round(time.time() - t, 1)

if __name__ == '__main__':
    with Pool(8) as p:
        for dels, st, dt in p.imap_unordered(test_delete, range(n)):
            print(dels, st, dt, flush=True)

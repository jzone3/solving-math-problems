"""Extract an induced subgraph (by vertex-index list) from a pool pickle and
save as (points, edges) in field coords for verify_m.py."""
import pickle, sys

pool_path, idx_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
allp, E = pickle.load(open(pool_path, 'rb'))
S = sorted(pickle.load(open(idx_path, 'rb')))
remap = {v: i for i, v in enumerate(S)}
pts = [allp[v] for v in S]
Es = set((min(a, b), max(a, b)) for a, b in E)
sub = [(remap[u], remap[v]) for (u, v) in Es if u in remap and v in remap]
pickle.dump((pts, sorted(sub)), open(out_path, 'wb'))
print(f'{out_path}: {len(pts)} vertices, {len(sub)} edges')

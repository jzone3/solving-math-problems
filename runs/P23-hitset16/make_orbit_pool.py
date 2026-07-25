import pickle, sys
import lattice

full_path, witness_path, out_path = sys.argv[1:4]
pts, edges = pickle.load(open(full_path,'rb'))
witness = pickle.load(open(witness_path,'rb'))
selected = {(pts[i][0], pts[i][1]) for i in witness}
closed = set()
for side,p in selected:
    for q in lattice.orbit24(p):
        if side == 'B' and q == (0,0,0,0):
            continue
        closed.add((side,q))
index = {p:i for i,p in enumerate(pts)}
ids = sorted(index[p] for p in closed)
new_index = {old:i for i,old in enumerate(ids)}
new_pts = [pts[i] for i in ids]
new_edges = [(new_index[u],new_index[v]) for u,v in edges if u in new_index and v in new_index]
with open(out_path,'wb') as f: pickle.dump((new_pts,new_edges),f)
print(f'witness={len(witness)} orbit_closed_vertices={len(new_pts)} edges={len(new_edges)}')

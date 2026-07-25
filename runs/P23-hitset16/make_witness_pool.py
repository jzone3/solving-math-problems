"""Materialize the known 2167-vertex witness as an integer-coordinate pool."""
import pickle

pts, edges = pickle.load(open("wt_16.pkl", "rb"))
keep = sorted(pickle.load(open("greedy_t16a.pkl", "rb")))
remap = {old: new for new, old in enumerate(keep)}
red_edges = [(remap[u], remap[v]) for u, v in edges
             if u in remap and v in remap]
pickle.dump(([pts[i] for i in keep], red_edges),
             open("wt_witness2167.pkl", "wb"))
print(f"vertices={len(keep)} edges={len(red_edges)}")

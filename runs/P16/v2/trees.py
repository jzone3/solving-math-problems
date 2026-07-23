import subprocess, sys
import networkx as nx
import numpy as np
from search_common import mu, rhs_graph, rhs44_edge, rhs46_edge
N=int(sys.argv[1])
worst={44:1e9,46:1e9}
for n in range(2,N+1):
    p=subprocess.Popen(["nauty-gentreeg","-q",str(n)],stdout=subprocess.PIPE,text=True)
    for line in p.stdout:
        A=nx.to_numpy_array(nx.from_sparse6_bytes(line.strip().encode())).astype(np.int8)
        lam=mu(A)
        for b,fn in ((44,rhs44_edge),(46,rhs46_edge)):
            g=rhs_graph(A,fn)-lam
            worst[b]=min(worst[b],g)
            if g<-1e-9: print("VIOLATION",b,line.strip(),flush=True)
    p.wait()
    print(f"trees n={n} done worst44={worst[44]:.4f} worst46={worst[46]:.4f}",flush=True)

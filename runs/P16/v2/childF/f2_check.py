"""Exhaustive verification of Conjecture F2 (childF):

  For every connected graph G with delta >= 2, with sigma_i := d_i + m_i - 4,
  w_e := 1/(arg46(e) - 4)  (edges with arg46 = 4 have sigma_i = sigma_j = 0 and
  are given weight 0 -- their DHD contribution vanishes),
  H := R diag(w) R^T,  D := diag(sigma),  Q := D_deg + A:

      M(G) := 2 D + 4 I - Q - D H D  >= 0  (PSD).

F2 ==> Conjecture D1 (K = diag(arg46) - A_L^2 >= 0) by the Fenchel/completion
argument: for X in range(R), X^T H^+ X >= 2(DX)^T X - (DX)^T H (DX)
                                       >= X^T (Q - 4I) X.
Usage: f2_check.py n [res mod]   (geng res/mod split)
"""
import sys
import numpy as np
import subprocess

def run(n, res=0, mod=1):
    cmd = ["nauty-geng", "-c", "-d2", str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1<<20)
    count = 0; bad = []; minmin = np.inf; minmin_g = None
    for line in p.stdout:
        g6 = line.strip()
        count += 1
        data = [ord(c)-63 for c in g6]
        nn = data[0]
        bits = []
        for v in data[1:]:
            bits += [(v>>k)&1 for k in range(5,-1,-1)]
        A = np.zeros((nn,nn))
        idx = 0
        for j in range(1,nn):
            for i in range(j):
                A[i,j]=A[j,i]=bits[idx]; idx+=1
        d = A.sum(1); m = (A@d)/d
        sig = d+m-4
        edges = [(i,j) for i in range(nn) for j in range(i+1,nn) if A[i,j]]
        E = len(edges)
        R = np.zeros((nn,E)); w = np.zeros(E)
        for k,(i,j) in enumerate(edges):
            R[i,k]=R[j,k]=1
            a4 = 2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j])
            w[k] = 1.0/a4 if a4 > 1e-9 else 0.0   # degenerate: sigma_i=sigma_j=0
        H = (R*w) @ R.T
        D = np.diag(sig)
        M = 2*D + 4*np.eye(nn) - (np.diag(d)+A) - D@H@D
        ev = np.linalg.eigvalsh(M)[0]
        if ev < minmin: minmin, minmin_g = ev, g6
        if ev < -1e-8:
            bad.append((g6, ev))
    print(f"n={n} res={res}/{mod}: {count} graphs, min eig {minmin:.3e} at {minmin_g}, FAILURES {len(bad)}")
    for b in bad[:20]: print("  BAD", b)

if __name__ == "__main__":
    n = int(sys.argv[1])
    res = int(sys.argv[2]) if len(sys.argv)>2 else 0
    mod = int(sys.argv[3]) if len(sys.argv)>3 else 1
    run(n, res, mod)

"""Machine verification of every step of the childF reduction (F2 ==> D1).

Steps verified:
  (1) [sympy, exact]  Lemma F1 algebra:
        arg46 - 4 = (2/(m_i+m_j)) * [ (d_i^2+d_j^2)(m_i+m_j) - 8 d_i d_j ]
      and the SOS-style decomposition
        (d^2+e^2)(x+y) - 8de = (x+y)(d-e)^2 + 2de(x+y-4)
      which is >= 0 for x,y >= 2, de > 0; equality iff d=e and x=y=2.
  (2) [numeric, random graphs] identity Q d = d o (d+m).
  (3) [numeric, random graphs+vectors] per-edge Young step:
        sum_e (arg-4+eps) x_e^2 - 2 X^T D X + X^T D H_eps D X
          = sum_e (arg-4+eps) (x_e - w_eps(e) (sigma_i X_i + sigma_j X_j))^2 >= 0
      hence x^T K_eps x >= X^T M_eps X  with X = Rx.
  (4) [numeric] M_eps >= M  (monotone in eps; degenerate edges contribute 0
      because sigma=0 at their endpoints).
  (5) [exhaustive n<=8] every edge with arg46 = 4 has sigma_i = sigma_j = 0
      (in fact d_i=d_j=2, m_i=m_j=2), delta>=2.
  (6) [numeric, all delta>=2 graphs n<=8] the full chain:
      min eig M >= -1e-10  implies (checked directly) min eig K >= -1e-9.
"""
import numpy as np
import sympy as sp
from vertex_cert import graphs, g6_adj
from shifted_scan import data

def step1():
    di, dj, mi, mj = sp.symbols('d_i d_j m_i m_j', positive=True)
    arg = 2*(di**2+dj**2) - 16*di*dj/(mi+mj) + 4
    lhs = sp.simplify(arg - 4 - sp.Rational(2)*((di**2+dj**2)*(mi+mj) - 8*di*dj)/(mi+mj))
    assert lhs == 0, lhs
    d, e, x, y = sp.symbols('d e x y', positive=True)
    expr = (d**2+e**2)*(x+y) - 8*d*e - ((x+y)*(d-e)**2 + 2*d*e*(x+y-4))
    assert sp.expand(expr) == 0, expr
    print("step1 OK (sympy identities exact)")

def randgraph(rng, n):
    while True:
        A = (rng.random((n,n)) < rng.uniform(0.25,0.7)).astype(float)
        A = np.triu(A,1); A = A+A.T
        d = A.sum(1)
        if d.min() >= 2:
            # connectivity check
            seen={0}; stack=[0]
            while stack:
                v=stack.pop()
                for u in np.nonzero(A[v])[0]:
                    if u not in seen: seen.add(u); stack.append(u)
            if len(seen)==n: return A

def steps234(trials=300):
    rng = np.random.default_rng(0)
    for _ in range(trials):
        n = int(rng.integers(5, 14))
        A = randgraph(rng, n)
        d,m,edges,R,arg,AL = data(A)
        sig = d+m-4
        Q = np.diag(d)+A
        assert np.allclose(Q@d, d*(d+m)), "step2 fail"
        D = np.diag(sig)
        for eps in [0.0, 1e-3, 0.7]:
            a = arg-4+eps
            if np.min(a) <= 1e-12: continue
            w = 1.0/a
            H = (R*w)@R.T
            Me = 2*D+4*np.eye(n)-Q-D@H@D
            K = np.diag(arg+eps) - AL@AL
            for _ in range(5):
                x = rng.standard_normal(len(edges))
                X = R@x
                b = R.T@(sig*X)
                lhs = a@ (x**2) - 2*X@(sig*X) + X@(D@H@D)@X
                rhs = a@((x - w*b)**2)
                assert abs(lhs-rhs) < 1e-8*max(1,abs(lhs)), "step3 identity fail"
                assert x@K@x >= X@Me@X - 1e-8, "step3 chain fail"
        # step4: M_eps monotone decreasing in w, i.e. M_eps >= M_0 (w0 with 0 on degenerate)
        w0 = np.where(arg-4 > 1e-9, 1.0/np.maximum(arg-4,1e-300), 0.0)
        H0 = (R*w0)@R.T
        M0 = 2*D+4*np.eye(n)-Q-D@H0@D
        weps = 1.0/(arg-4+0.1)
        Heps = (R*weps)@R.T
        Meps = 2*D+4*np.eye(n)-Q-D@Heps@D
        assert np.linalg.eigvalsh(Meps-M0)[0] > -1e-9, "step4 fail"
    print("step2,3,4 OK (numeric, %d random graphs)" % trials)

def step56():
    total=0; degedges=0
    for n in range(3,9):
        for g6 in graphs(n):
            total+=1
            A=g6_adj(g6); d,m,edges,R,arg,AL=data(A)
            sig=d+m-4
            nn=len(d)
            for k,(i,j) in enumerate(edges):
                if arg[k]-4 < 1e-9:
                    degedges+=1
                    assert abs(sig[i])<1e-12 and abs(sig[j])<1e-12
                    assert d[i]==2 and d[j]==2
            w0 = np.where(arg-4>1e-9, 1.0/np.maximum(arg-4,1e-300), 0.0)
            H=(R*w0)@R.T; D=np.diag(sig); Q=np.diag(d)+A
            M=2*D+4*np.eye(nn)-Q-D@H@D
            K=np.diag(arg)-AL@AL
            if np.linalg.eigvalsh(M)[0] >= -1e-10:
                assert np.linalg.eigvalsh(K)[0] >= -1e-9, ("step6 fail", g6)
    print(f"step5,6 OK ({total} graphs n<=8, {degedges} degenerate edges seen)")

if __name__ == "__main__":
    step1(); steps234(); step56()
    print("ALL REDUCTION STEPS VERIFIED")

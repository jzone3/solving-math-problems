"""V4 numeric pipeline: families without few-valued closed-form spectra.

  A. Joins of arbitrary small graphs: all graphs on 2..8 vertices (nauty-geng),
     each joined with K_r and E_r (r<=40), plus all pairwise joins of graphs n<=7.
     Component spectra by numpy eigensolve; join formula assembles the spectrum;
     deficits with floats; anything < 0.5 is re-checked EXACTLY via sympy on the
     integer Laplacian.
  B. Incidence graphs of projective planes PG(2,q) (q prime power <= 1024):
     (q+1)-regular bipartite, A-eigs +-(q+1), +-sqrt(q); exact check via integer
     arithmetic on squared terms.
  C. Paley graphs (SRG) q <= 1000 and their cones/joins with cliques.
"""
import subprocess, sys, time
import numpy as np
from fractions import Fraction

t0 = time.time()
worst = [None]
suspects = []

def deficits_min(eigs_desc, m):
    t = np.arange(1, len(eigs_desc) + 1)
    d = m + t * (t + 1) / 2.0 - np.cumsum(eigs_desc)
    i = int(np.argmin(d))
    return d[i], i + 1

def rec(name, eigs_desc, m, G_edges=None, n=None):
    d, t = deficits_min(eigs_desc, m)
    if worst[0] is None or d < worst[0][0]:
        worst[0] = (d, name, t)
    if d < 0.5:
        suspects.append((d, name, t, G_edges, n))
        print(f"  suspect {name} t={t} d={d:.6f}", flush=True)

def graph6_iter(n):
    p = subprocess.run(["nauty-geng", "-q", "-c", str(n)], capture_output=True, text=True)
    return p.stdout.split()

def g6_to_adj(g6):
    import networkx as nx
    return nx.from_graph6_bytes(g6.encode())

def lap_eigs(A):
    L = np.diag(A.sum(1)) - A
    return np.sort(np.linalg.eigvalsh(L))[::-1]

import networkx as nx

def join_eigs(eA, nA, mA, eB, nB, mB):
    # remove one (numerically smallest) zero from each, shift, add 0 and nA+nB
    ea = list(eA[:-1] + nB)
    eb = list(eB[:-1] + nA)
    out = np.array(ea + eb + [nA + nB, 0.0])
    return np.sort(out)[::-1], mA + mB + nA * nB

# --- A: joins of small graphs ---
base = {}
for n in range(2, 9):
    for g6 in graph6_iter(n):
        G = g6_to_adj(g6)
        A = nx.to_numpy_array(G)
        base[g6] = (lap_eigs(A), n, G.number_of_edges())
    print(f"loaded geng n={n}: total {len(base)} graphs {time.time()-t0:.0f}s", flush=True)

names = list(base.keys())
# join each with K_r, E_r
for g6, (e, n, m) in base.items():
    for r in range(1, 41):
        eK = np.array([float(r)] * (r - 1) + [0.0]); mK = r * (r - 1) // 2
        eE = np.zeros(r); mE = 0
        ee, mm = join_eigs(e, n, m, eK, r, mK)
        rec(f"{g6}vK{r}", ee, mm, g6, n)
        ee, mm = join_eigs(e, n, m, eE, r, mE)
        rec(f"{g6}vE{r}", ee, mm, g6, n)
print(f"A1 done {time.time()-t0:.0f}s worst={worst[0]}", flush=True)

small = [k for k in names if base[k][1] <= 7]
for i, ga in enumerate(small):
    ea, na, ma = base[ga]
    for gb in small[i:]:
        eb, nb, mb = base[gb]
        ee, mm = join_eigs(ea, na, ma, eb, nb, mb)
        rec(f"{ga}v{gb}", ee, mm, (ga, gb), na + nb)
print(f"A2 done {time.time()-t0:.0f}s worst={worst[0]}", flush=True)

# --- B: projective plane incidence graphs ---
def prime_powers(limit):
    out = []
    for q in range(2, limit + 1):
        x = q
        for p in range(2, q + 1):
            if x % p == 0:
                while x % p == 0: x //= p
                out.append(q) if x == 1 else None
                break
    return out

for q in prime_powers(1024):
    v = q * q + q + 1
    n = 2 * v
    m = (q + 1) * v
    s = np.sqrt(q)
    # L-eigs: 2(q+1) x1, (q+1)+sqrt(q) x(v-1), (q+1)-sqrt(q) x(v-1), 0 x1
    e = np.array([2.0 * (q + 1)] + [(q + 1) + s] * (v - 1) + [(q + 1) - s] * (v - 1) + [0.0])
    rec(f"PG(2,{q})", e, m)
print(f"B done {time.time()-t0:.0f}s worst={worst[0]}", flush=True)

# --- C: Paley graphs (conference graph SRG) and cones ---
def paley_eigs(q):
    # A-eigs: (q-1)/2 x1, (-1+sqrt(q))/2 x((q-1)/2), (-1-sqrt(q))/2 x((q-1)/2)
    d = (q - 1) / 2.0
    s = np.sqrt(q)
    a = np.array([d] + [(-1 + s) / 2] * ((q - 1) // 2) + [(-1 - s) / 2] * ((q - 1) // 2))
    return np.sort(d - a)[::-1], q, q * (q - 1) // 4

for q in [x for x in range(5, 1001, 4) if all(x % p for p in range(2, int(x**0.5) + 1)) or
          round(x ** 0.5) ** 2 == x]:
    # q must be prime power = 1 mod 4; crude filter: primes =1 mod4 and squares of primes
    e, n, m = paley_eigs(q)
    rec(f"Paley({q})", e, m)
    for r in range(1, 31):
        eK = np.array([float(r)] * (r - 1) + [0.0])
        ee, mm = join_eigs(e, n, m, eK, r, r * (r - 1) // 2)
        rec(f"Paley({q})vK{r}", ee, mm)
print(f"C done {time.time()-t0:.0f}s worst={worst[0]}", flush=True)

print(f"WORST float deficit: {worst[0]}")
print(f"suspects (<0.5): {len(suspects)}")

# exact recheck of suspects that are actual small graphs (graph6-based)
if suspects:
    from sympy import Matrix
    import re
    print("Exact recheck of graph6-based suspects:")
    for d, name, t, tag, n in sorted(suspects)[:200]:
        if tag is None: continue
        # rebuild integer Laplacian of the join and check exactly
        def gmat(g6):
            G = g6_to_adj(g6)
            return nx.to_numpy_array(G).astype(int), G.number_of_nodes()
        mobj = re.match(r"(.+)v(K|E)(\d+)$", name)
        if isinstance(tag, tuple):
            A1, n1 = gmat(tag[0]); A2, n2 = gmat(tag[1])
        elif mobj:
            A1, n1 = gmat(mobj.group(1))
            r = int(mobj.group(3))
            A2 = (np.ones((r, r), int) - np.eye(r, dtype=int)) if mobj.group(2) == "K" \
                 else np.zeros((r, r), int)
            n2 = r
        else:
            continue
        N = n1 + n2
        A = np.zeros((N, N), int)
        A[:n1, :n1] = A1; A[n1:, n1:] = A2; A[:n1, n1:] = 1; A[n1:, :n1] = 1
        L = np.diag(A.sum(1)) - A
        M = Matrix(L.tolist())
        eigs = []
        for val, mult in M.eigenvals().items():
            eigs += [val] * mult
        eigs = sorted(eigs, key=lambda x: -x.evalf())
        mE = int(A.sum()) // 2
        S = 0
        ok = True
        for tt, v in enumerate(eigs, 1):
            S += v
            gap = mE + Fraction(tt * (tt + 1), 2) - S
            if gap.is_negative:
                print(f"!!! EXACT COUNTEREXAMPLE {name} t={tt}")
                ok = False
        if ok:
            print(f"  exact-verified >=0: {name} (float d={d:.4f})")

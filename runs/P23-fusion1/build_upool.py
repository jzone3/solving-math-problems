"""Pool around the union of Parts' 509 and Heule's 510, plus their shared core."""
import os, pickle
import numpy as np
import mfield

RMAX = float(os.environ.get('RMAX', '2.6'))
DMIN = int(os.environ.get('DMIN', '3'))
F = mfield.MField([3, 5, 11])
h = mfield.load_vtx(F, '/home/ubuntu/p23heule/vtx/510.vtx')
p = mfield.load_vtx(F, '/home/ubuntu/solving-math-problems/solutions/P23/v509e2442.vtx')
shared = set(h) & set(p)
U = sorted(set(h) | set(p), key=lambda q: (F.to_float(q[0]), F.to_float(q[1])))
n = len(U)
Z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in U])
c = Z.mean()
E0 = []
for i in range(n):
    for k in np.nonzero(np.abs(np.abs(Z[i+1:] - Z[i]) - 1.0) < 1e-7)[0]:
        j = i + 1 + int(k)
        dx = F.sub(U[i][0], U[j][0]); dy = F.sub(U[i][1], U[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E0.append((i, j))
print(f'union {n} vertices, {len(E0)} edges, shared core {len(shared)}', flush=True)
V = []
for u, v in E0:
    for a, b in ((u, v), (v, u)):
        V.append((F.sub(U[a][0], U[b][0]), F.sub(U[a][1], U[b][1])))
zV = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in V])
seen = set(U); new = []
for i in range(n):
    W = Z[i] + zV
    ins = np.nonzero(np.abs(W - c) <= RMAX)[0]
    if not len(ins): continue
    deg = (np.abs(np.abs(W[ins][:, None] - Z[None, :]) - 1.0) < 1e-7).sum(axis=1)
    for k, dg in zip(ins, deg):
        if dg < DMIN: continue
        q = (F.add(U[i][0], V[k][0]), F.add(U[i][1], V[k][1]))
        if q in seen: continue
        seen.add(q); new.append(q)
allp = U + new
print(f'{len(new)} new candidate points -> pool {len(allp)}', flush=True)
zz = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in allp])
E = []
for i in range(len(allp)):
    for k in np.nonzero(np.abs(np.abs(zz[i+1:] - zz[i]) - 1.0) < 1e-7)[0]:
        j = i + 1 + int(k)
        dx = F.sub(allp[i][0], allp[j][0]); dy = F.sub(allp[i][1], allp[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E.append((i, j))
print(f'pool {len(allp)} vertices, {len(E)} exact edges', flush=True)
pickle.dump((allp, E), open('upool.pkl', 'wb'))
pickle.dump(sorted(i for i, q in enumerate(allp) if q in shared), open('ucore.pkl', 'wb'))
pickle.dump(sorted(i for i, q in enumerate(allp) if q in set(p)), open('uparts.pkl', 'wb'))
pickle.dump(sorted(i for i, q in enumerate(allp) if q in set(h)), open('uheule.pkl', 'wb'))

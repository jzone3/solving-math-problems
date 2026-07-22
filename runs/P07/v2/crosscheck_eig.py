"""Second, differently-written check: literal R-C style evaluation with numpy
(eigendecomposition + Floyd-Warshall), no reformulation."""
import numpy as np
a,ell=50,70; n=a+ell
A=np.zeros((n,n))
for i in range(a):
    for j in range(i+1,a): A[i,j]=A[j,i]=1
prev=0
for k in range(ell):
    v=a+k; A[prev,v]=A[v,prev]=1; prev=v
INF=10**9
D=np.where(A>0,1,INF).astype(float); np.fill_diagonal(D,0)
for k in range(n): D=np.minimum(D, D[:,k,None]+D[None,k,:])
assert D.max()<INF
eig=np.linalg.eigvalsh(A)
stdev=float(np.sqrt(((eig-eig.mean())**2).mean()))
mean_dist=float(D.sum()/(n*n))          # R-C: mean over all n^2 entries
mean_dist_std=float(D.sum()/(n*(n-1)))  # standard
print("stdev(eigs) =",stdev)
print("n/mean_dist (R-C) =",n/mean_dist," -> violated:",stdev>n/mean_dist)
print("n/mean_dist (std) =",n/mean_dist_std," -> violated:",stdev>n/mean_dist_std)
assert stdev - n/mean_dist > 1e-5 and stdev - n/mean_dist_std > 1e-5
print("CROSSCHECK PASS")

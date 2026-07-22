from families import *
import fractions
F=fractions.Fraction

def dumbbell(a,ell,b):
    # cliques K_a and K_b joined by path with ell internal vertices
    n=a+b+ell
    edges=[(i,j) for i in range(a) for j in range(i+1,a)]
    edges+= [(a+i,a+j) for i in range(b) for j in range(i+1,b)]
    prev=0
    for k in range(ell):
        edges.append((prev,a+b+k)); prev=a+b+k
    edges.append((prev,a))
    return edges,n

def broom(a,paths):
    # clique K_a with pendant paths of given lengths, all at vertex 0
    n=a+sum(paths)
    edges=[(i,j) for i in range(a) for j in range(i+1,a)]
    nxt=a
    for L in paths:
        prev=0
        for k in range(L):
            edges.append((prev,nxt)); prev=nxt; nxt+=1
    return edges,n

best=(F(0),None)
for n in range(100,131):
    for a in range(3,n-2):
        for b in range(1,n-a-1):
            ell=n-a-b
            e,nn=dumbbell(a,ell,b)
            m,S,lc,ls,n3=score(e,nn)
            r=F(lc,n3)
            if r>best[0]: best=(r,("dumbbell",n,a,ell,b))
    if best[0]>1:
        print("violation:",float(best[0]),best[1]); break
    print(n,float(best[0]),best[1])

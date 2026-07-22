"""Exact integer optimization of R = 2*m*S^2 / n^7  (since mu=S/n^2, R = 2 m mu^2/n^3)
over lollipop and dumbbell families using verified closed forms. Violation iff R > 1,
i.e. 2*m*S^2 > n^7 (all integers, m half-integer*2 handled)."""
from fractions import Fraction as F

def S_lol(a,l): return a*a + a*l*l + 3*a*l - a + (l**3 - 7*l)//3 if (l**3-7*l)%3==0 else None
def S_lol_exact(a,l): return F(3*a*a + 3*a*l*l + 9*a*l - 3*a + l**3 - 7*l, 3)
def m_lol(a,l): return F(a*(a-1),2) + l

def S_dum(a,l,b): return F(3*(a*a + 2*a*b*l + 6*a*b + a*l*l + 3*a*l - 3*a + b*b + b*l*l + 3*b*l - 3*b) + l**3 - 13*l, 3)
def m_dum(a,l,b): return F(a*(a-1),2) + F(b*(b-1),2) + l + 1

def ratio(m,S,n): return 2*m*S*S / F(n**7)

best_overall={}
minviol=None
for n in range(20,220):
    best=(F(0),None)
    for a in range(3,n):
        l=n-a
        r=ratio(m_lol(a,l), S_lol_exact(a,l), n)
        if r>best[0]: best=(r,("lollipop",a,l))
    for a in range(2,n-2):
        for b in range(2,n-a):
            l=n-a-b
            if l<1: continue
            r=ratio(m_dum(a,l,b), S_dum(a,l,b), n)
            if r>best[0]: best=(r,("dumbbell",a,l,b))
    best_overall[n]=best
    if best[0]>1 and minviol is None:
        minviol=n
        print("FIRST VIOLATION at n =",n,":",best[1],"ratio =",float(best[0]))
    if n%20==0: print(n,float(best[0]),best[1])
print("min violating n over lollipop+dumbbell:",minviol)
n=150
b=best_overall[150]; print("n=150:",float(b[0]),b[1])

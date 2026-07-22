import sys, itertools
sys.path.insert(0, '.')
from fractions import Fraction
from p02lib import *

# C5: 5-cycle, MTF, 2-regular, delta=2 >= 5/3. feasible (x=1), m* should be 1/2? Ax=1 with x=1/2 each -> m*=1/2>0
def cyc(n):
    adj=[0]*n
    for i in range(n):
        adj[i]|=1<<((i+1)%n); adj[(i+1)%n]|=1<<i
    return adj
n=5; adj=cyc(5)
assert is_triangle_free(n,adj) and is_maximal_tf(n,adj)
print('C5', exact_mstar(n,adj))  # expect ok, 1/2

# Petersen
edges=[(0,1),(1,2),(2,3),(3,4),(4,0),(5,7),(7,9),(9,6),(6,8),(8,5),(0,5),(1,6),(2,7),(3,8),(4,9)]
adj=[0]*10
for u,v in edges: adj[u]|=1<<v; adj[v]|=1<<u
assert is_triangle_free(10,adj) and is_maximal_tf(10,adj)
print('Petersen', exact_mstar(10,adj))  # 3-regular -> 1/3

# Star K_{1,3}: MTF, m* : A x = 1: center c adj to 3 leaves; leaf eq: x_c =1; center eq: sum leaves=1 -> leaves 1/3 -> m*=1/3
adj=[0b1110,1,1,1]
print('K13', exact_mstar(4,adj))

# graph with infeasible? C5 with a pendant path? try all MTF graphs n<=7 quickly via brute force check parse
# quick graph6 roundtrip test
import random
random.seed(1)
n=8; adj=[0]*n
for u in range(n):
    for v in range(u+1,n):
        if random.random()<0.4:
            adj[u]|=1<<v; adj[v]|=1<<u
n2,adj2=parse_graph6(to_graph6(n,adj))
assert adj2==adj, 'g6 roundtrip fail'
print('g6 roundtrip ok')

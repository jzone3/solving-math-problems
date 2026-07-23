/* Fast HC counter for 4-regular simple graphs on n <= 64 vertices.
 * Bitmask adjacency + availability pruning. Same counting semantics as search.c
 * (directed count from vertex 0, divided by 2), independently implemented.
 *
 * Usage: ./fastcount count < graphfile          exact count (cap 2^62)
 *        ./fastcount capcount CAP < graphfile   count with early cutoff at CAP
 * Also exposes count_hc_fast() for inclusion in search drivers (compile with -DLIB).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n;
static uint64_t adjm[64];
static long long hc_cap2, hc_cnt;

static void dfs(int v, int depth, uint64_t vis){
    if(hc_cnt >= hc_cap2) return;
    if(depth == n){
        if(adjm[v] & 1ULL) hc_cnt++;
        return;
    }
    uint64_t cand = adjm[v] & ~vis;
    while(cand){
        int w = __builtin_ctzll(cand);
        cand &= cand-1;
        uint64_t nvis = vis | (1ULL<<w);
        /* prune: every unvisited neighbor u of w must still have >=2 available
         * connections among: unvisited vertices (excl. w now visited), vertex 0
         * (closing endpoint), and w itself (the new head). */
        uint64_t check = adjm[w] & ~nvis;
        uint64_t freeset = ~nvis | 1ULL;   /* unvisited plus vertex 0 */
        int ok = 1;
        uint64_t c2 = check & ~1ULL;
        while(c2){
            int u = __builtin_ctzll(c2);
            c2 &= c2-1;
            int avail = __builtin_popcountll(adjm[u] & freeset) + ((adjm[u]>>w)&1);
            if(avail < 2){ ok=0; break; }
        }
        if(ok) dfs(w, depth+1, nvis);
        if(hc_cnt >= hc_cap2) return;
    }
}

long long count_hc_fast(long long cap){
    hc_cap2 = cap*2; hc_cnt = 0;
    dfs(0, 1, 1ULL);
    return hc_cnt/2;
}

#ifndef LIB
int main(int argc, char** argv){
    long long cap = (1LL<<61);
    int argi = 1;
    if(argc>=2 && strcmp(argv[1],"capcount")==0){ cap = atoll(argv[2]); }
    if(scanf("%d",&n)!=1) return 2;
    if(n>64){ fprintf(stderr,"n too big\n"); return 2; }
    memset(adjm,0,sizeof(adjm));
    int a,b;
    int deg[64]; memset(deg,0,sizeof(deg));
    while(scanf("%d %d",&a,&b)==2){
        adjm[a] |= 1ULL<<b; adjm[b] |= 1ULL<<a;
        deg[a]++; deg[b]++;
    }
    for(int i=0;i<n;i++) if(deg[i]!=4){ fprintf(stderr,"vertex %d deg %d != 4\n", i, deg[i]); return 2; }
    printf("%lld\n", count_hc_fast(cap));
    return 0;
}
#endif

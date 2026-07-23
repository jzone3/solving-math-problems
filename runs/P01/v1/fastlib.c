#include <stdint.h>
extern int n;
extern uint64_t adjm[64];
static long long hc_cap2, hc_cnt;
static void fdfs(int v, int depth, uint64_t vis){
    if(hc_cnt >= hc_cap2) return;
    if(depth == n){ if(adjm[v] & 1ULL) hc_cnt++; return; }
    uint64_t cand = adjm[v] & ~vis;
    while(cand){
        int w = __builtin_ctzll(cand);
        cand &= cand-1;
        uint64_t nvis = vis | (1ULL<<w);
        uint64_t check = adjm[w] & ~nvis & ~1ULL;
        uint64_t freeset = ~nvis | 1ULL;
        int ok = 1;
        while(check){
            int u = __builtin_ctzll(check);
            check &= check-1;
            int avail = __builtin_popcountll(adjm[u] & freeset) + (int)((adjm[u]>>w)&1);
            if(avail < 2){ ok=0; break; }
        }
        if(ok) fdfs(w, depth+1, nvis);
        if(hc_cnt >= hc_cap2) return;
    }
}
long long count_hc_fast(long long cap){
    hc_cap2 = cap*2; hc_cnt = 0;
    fdfs(0, 1, 1ULL);
    return hc_cnt/2;
}

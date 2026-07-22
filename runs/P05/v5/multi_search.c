/* V5 stage-2: generalized arm-structure search.
 *
 * Family: attach pendant arms (paths) at a set A of k=3..6 vertices of core H.
 * Choose 3 endpoint pairs (tips) among A, no vertex in all three pairs.
 * If there exist per-pair maximum H-paths P1,P2,P3 with empty triple
 * intersection, print a CANDIDATE line (arm-length feasibility LP is checked
 * downstream in Python; for k=3 it is always feasible).
 *
 * Output line:
 * CAND <g6> pairs=u1,v1;u2,v2;u3,v3 lens=l1,l2,l3 p1=<m> p2=<m> p3=<m> M=<full pair matrix over union>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 32

static int n;
static uint32_t adj[MAXN];

typedef struct { int len; uint32_t *masks; int cnt, cap; } PairList;
static PairList pl[MAXN][MAXN];
static long total_masks, mask_budget = 8000000;
static int overflow;

static void pl_add(int s, int t, int len, uint32_t mask){
    PairList *p = &pl[s][t];
    if (len > p->len){ p->len = len; p->cnt = 0; }
    if (len == p->len){
        if (p->cnt == p->cap){
            if (total_masks >= mask_budget){ overflow = 1; return; }
            p->cap = p->cap ? p->cap*2 : 8;
            p->masks = realloc(p->masks, p->cap*sizeof(uint32_t));
        }
        p->masks[p->cnt++] = mask; total_masks++;
    }
}

static int start;
static void dfs(int v, uint32_t mask, int len){
    uint32_t cand = adj[v] & ~mask;
    while (cand){
        int w = __builtin_ctz(cand); cand &= cand-1;
        uint32_t m2 = mask | (1u<<w);
        if (start < w) pl_add(start, w, len+1, m2);
        dfs(w, m2, len+1);
    }
}

static int parse_g6(const char *s){
    int k = 0;
    n = s[k++] - 63;
    if (n < 1 || n > MAXN) return -1;
    memset(adj, 0, sizeof(adj));
    int bitpos = 0, need = n*(n-1)/2;
    int i = 0, j = 1;
    while (bitpos < need){
        int v = s[k++] - 63;
        if (v < 0) return -1;
        for (int b = 5; b >= 0 && bitpos < need; b--, bitpos++){
            if ((v>>b)&1){ adj[i] |= 1u<<j; adj[j] |= 1u<<i; }
            if (++i == j){ i = 0; j++; }
        }
    }
    return 0;
}

static PairList *getpl(int u, int v){ return u < v ? &pl[u][v] : &pl[v][u]; }

static const char *cur_g6;
static long cands;

static void check_structure(int u1,int v1,int u2,int v2,int u3,int v3){
    /* no vertex in all three pairs */
    uint32_t q1 = (1u<<u1)|(1u<<v1), q2 = (1u<<u2)|(1u<<v2), q3 = (1u<<u3)|(1u<<v3);
    if (q1 & q2 & q3) return;
    PairList *l1 = getpl(u1,v1), *l2 = getpl(u2,v2), *l3 = getpl(u3,v3);
    if (!l1->cnt || !l2->cnt || !l3->cnt) return;
    for (int i1 = 0; i1 < l1->cnt; i1++){
        uint32_t p1 = l1->masks[i1];
        /* p1 must avoid arm vertices in q2&q3 not in q1? No: p1 may pass through
           attachment vertices; intersection test below is exact. */
        for (int i2 = 0; i2 < l2->cnt; i2++){
            uint32_t i12 = p1 & l2->masks[i2];
            if (i12 == 0) { /* still fine, need triple empty */ }
            for (int i3 = 0; i3 < l3->cnt; i3++){
                if ((i12 & l3->masks[i3]) == 0){
                    /* print candidate with M matrix over union */
                    uint32_t un = q1|q2|q3;
                    printf("CAND %s pairs=%d,%d;%d,%d;%d,%d lens=%d,%d,%d p1=%u p2=%u p3=%u M=",
                        cur_g6,u1,v1,u2,v2,u3,v3,l1->len,l2->len,l3->len,
                        p1,l2->masks[i2],l3->masks[i3]);
                    int verts[6], k=0;
                    for (int v=0; v<n; v++) if (un>>v&1) verts[k++]=v;
                    for (int x=0;x<k;x++) for(int y=x+1;y<k;y++){
                        PairList *pp = getpl(verts[x],verts[y]);
                        printf("%d,%d,%d;",verts[x],verts[y],pp->len);
                    }
                    printf("\n"); fflush(stdout);
                    cands++;
                    return; /* one candidate per structure is enough */
                }
            }
        }
    }
}

int main(void){
    char line[1024];
    long processed = 0;
    while (fgets(line, sizeof line, stdin)){
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!line[0]) continue;
        if (parse_g6(line)) { fprintf(stderr, "bad g6: %s\n", line); continue; }
        cur_g6 = line;
        for (int s = 0; s < n; s++) for (int t = 0; t < n; t++){
            pl[s][t].len = -1; pl[s][t].cnt = 0;
        }
        total_masks = 0; overflow = 0;
        for (start = 0; start < n; start++) dfs(start, 1u<<start, 0);
        if (overflow) fprintf(stderr, "OVERFLOW on %s\n", line);
        /* iterate unordered triples of distinct vertex-pairs */
        int np = n*(n-1)/2;
        for (int e1 = 0; e1 < np; e1++)
        for (int e2 = e1+1; e2 < np; e2++)
        for (int e3 = e2+1; e3 < np; e3++){
            /* decode pair indices */
            int u1,v1,u2,v2,u3,v3,t,i,j;
            t=e1; for(i=0;;i++){ int c=n-1-i; if(t<c){u1=i;v1=i+1+t;break;} t-=c; }
            t=e2; for(i=0;;i++){ int c=n-1-i; if(t<c){u2=i;v2=i+1+t;break;} t-=c; }
            t=e3; for(i=0;;i++){ int c=n-1-i; if(t<c){u3=i;v3=i+1+t;break;} t-=c; }
            (void)j;
            check_structure(u1,v1,u2,v2,u3,v3);
        }
        processed++;
        if (processed % 100000 == 0)
            fprintf(stderr, "... %ld graphs, %ld cands\n", processed, cands);
    }
    fprintf(stderr, "processed %ld graphs, %ld candidate structures\n", processed, cands);
    return 0;
}

/* V5 spider-reduction search for Gallai's 3-longest-paths question.
 *
 * For each input graph H (graph6 on stdin, n<=32), test:
 *   exist distinct a,b,c and maximum-length a-b, b-c, a-c paths P1,P2,P3
 *   (maximum per endpoint-pair) with c not in P1, a not in P2, b not in P3,
 *   and V(P1) & V(P2) & V(P3) == 0.
 * A hit yields a Gallai-3 counterexample by attaching pendant arms at a,b,c.
 *
 * Prints "HIT <graph6> a b c ..." for hits; stats to stderr.
 * Also tracks the best near-miss: minimum achievable |P1&P2&P3| over all
 * valid (endpoint-avoiding) triples, reported with -m.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 64

static int n;
static uint64_t adj[MAXN];

/* per-pair storage of maximum paths */
typedef struct { int len; uint64_t *masks; int cnt, cap; } PairList;
static PairList pl[MAXN][MAXN]; /* s<t used */
static long total_masks, mask_budget = 8000000;
static int overflow;

static int popc(uint64_t x){ return __builtin_popcountll(x); }

static void pl_add(int s, int t, int len, uint64_t mask){
    PairList *p = &pl[s][t];
    if (len > p->len){ p->len = len; p->cnt = 0; }
    if (len == p->len){
        if (p->cnt == p->cap){
            if (total_masks >= mask_budget){ overflow = 1; return; }
            p->cap = p->cap ? p->cap*2 : 8;
            p->masks = realloc(p->masks, p->cap*sizeof(uint64_t));
        }
        p->masks[p->cnt++] = mask; total_masks++;
    }
}

static int start;
static void dfs(int v, uint64_t mask, int len){
    uint64_t cand = adj[v] & ~mask;
    while (cand){
        int w = __builtin_ctzll(cand); cand &= cand-1;
        uint64_t m2 = mask | (1ull<<w);
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
            if ((v>>b)&1){ adj[i] |= 1ull<<j; adj[j] |= 1ull<<i; }
            if (++i == j){ i = 0; j++; }
        }
    }
    return 0;
}

int main(int argc, char **argv){
    int report_nearmiss = (argc > 1 && !strcmp(argv[1], "-m"));
    char line[1024];
    long processed = 0, hits = 0;
    int global_best_nm = 999;
    char global_best_g6[1024] = "";
    while (fgets(line, sizeof line, stdin)){
        char *nl = strchr(line, '\n'); if (nl) *nl = 0;
        if (!line[0]) continue;
        if (parse_g6(line)) { fprintf(stderr, "bad g6: %s\n", line); continue; }
        for (int s = 0; s < n; s++) for (int t = 0; t < n; t++){
            pl[s][t].len = -1; pl[s][t].cnt = 0;
        }
        total_masks = 0; overflow = 0;
        for (start = 0; start < n; start++) dfs(start, 1ull<<start, 0);
        if (overflow) fprintf(stderr, "OVERFLOW (budget) on %s\n", line);
        int hit = 0, best_nm = 999;
        for (int a = 0; a < n-2 && !hit; a++)
        for (int b = a+1; b < n-1 && !hit; b++)
        for (int c = b+1; c < n && !hit; c++){
            /* pairs: (a,b) avoid c ; (b,c) avoid a ; (a,c) avoid b */
            PairList *l1 = &pl[a][b], *l2 = &pl[b][c], *l3 = &pl[a][c];
            if (l1->cnt == 0 || l2->cnt == 0 || l3->cnt == 0) continue;
            /* filter in place into temp arrays */
            for (int i1 = 0; i1 < l1->cnt && !hit; i1++){
                uint64_t p1 = l1->masks[i1];
                if (p1 >> c & 1) continue;
                for (int i2 = 0; i2 < l2->cnt && !hit; i2++){
                    uint64_t p2 = l2->masks[i2];
                    if (p2 >> a & 1) continue;
                    uint64_t i12 = p1 & p2;
                    for (int i3 = 0; i3 < l3->cnt; i3++){
                        uint64_t p3 = l3->masks[i3];
                        if (p3 >> b & 1) continue;
                        int sz = popc(i12 & p3);
                        if (sz < best_nm) best_nm = sz;
                        if (sz == 0){
                            hits++;
                            printf("HIT %s abc=%d,%d,%d len=%d,%d,%d p1=%llu p2=%llu p3=%llu\n",
                                   line, a, b, c, l1->len, l2->len, l3->len, p1, p2, p3);
                            fflush(stdout);
                            hit = 1; break;
                        }
                    }
                }
            }
        }
        if (best_nm < global_best_nm && !hit){
            global_best_nm = best_nm; strcpy(global_best_g6, line);
        }
        processed++;
        if (processed % 1000000 == 0)
            fprintf(stderr, "... %ld graphs, %ld hits\n", processed, hits);
    }
    fprintf(stderr, "processed %ld graphs, %ld hits\n", processed, hits);
    if (report_nearmiss)
        fprintf(stderr, "best near-miss triple-intersection size: %d on %s\n",
                global_best_nm, global_best_g6);
    return 0;
}

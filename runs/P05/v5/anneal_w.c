/* Weighted-multigraph annealer for Gallai-3.
 *
 * Searches connected graphs on n <= 14 vertices with integer edge weights
 * 1..W for three maximum-WEIGHT paths with empty vertex intersection.
 * A weighted witness lifts to an unweighted counterexample candidate by
 * subdividing each weight-w edge into w unit edges (must then be re-verified
 * exactly on the lifted graph, including paths ending inside subdivided
 * edges — see verify_lift.py).
 *
 * dpw[mask][v] = max weight of a simple path with vertex set mask ending v.
 * Energy as in anneal.c.
 *
 * Usage: anneal_w n seed iters maxdeg W
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 14
#define SAMPLE_CAP 160

static int n, dmax = 4, W = 4;
static uint16_t adj[MAXN];
static int8_t wt[MAXN][MAXN];
static int16_t *dpw;   /* (1<<n)*n */
static uint32_t lp[SAMPLE_CAP];

static uint64_t rng;
static inline uint64_t rnd(void){
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng;
}

static int connected(void){
    uint16_t seen = 1, frontier = 1, full = (1u<<n)-1;
    while (frontier){
        uint16_t nxt = 0, f = frontier;
        while (f){ int v = __builtin_ctz(f); f &= f-1; nxt |= adj[v]; }
        frontier = nxt & ~seen; seen |= nxt;
    }
    return seen == full;
}

static long evaluate(void){
    int full = 1<<n;
    memset(dpw, -1, (size_t)full*n*sizeof(int16_t));
    for (int v = 0; v < n; v++) dpw[(1<<v)*n + v] = 0;
    int bestw = 0;
    for (int mask = 1; mask < full; mask++){
        for (int v = 0; v < n; v++){
            int16_t d = dpw[mask*n + v];
            if (d < 0) continue;
            if (d > bestw) bestw = d;
            uint16_t ext = adj[v] & ~(uint16_t)mask;
            while (ext){
                int u = __builtin_ctz(ext); ext &= ext-1;
                int nm = mask | (1<<u);
                int16_t nd = d + wt[v][u];
                if (nd > dpw[nm*n + u]) dpw[nm*n + u] = nd;
            }
        }
    }
    if (bestw == 0) return 1000000;
    int m = 0; long seen_cnt = 0;
    uint32_t andall = 0xFFFFFFFF;
    for (int mask = 1; mask < full; mask++){
        int hit = 0;
        for (int v = 0; v < n; v++)
            if (dpw[mask*n + v] == bestw){ hit = 1; break; }
        if (!hit) continue;
        andall &= (uint32_t)mask;
        seen_cnt++;
        if (m < SAMPLE_CAP) lp[m++] = (uint32_t)mask;
        else { long j = rnd() % seen_cnt; if (j < SAMPLE_CAP) lp[j] = (uint32_t)mask; }
    }
    if (m < 3) return 1000000;
    if (andall)
        return 10000 + 500L*__builtin_popcount(andall) - (m < 499 ? m : 499);
    int best = 999; long cnt = 0;
    for (int i1 = 0; i1 < m; i1++)
        for (int i2 = i1+1; i2 < m; i2++){
            uint32_t i12 = lp[i1] & lp[i2];
            for (int i3 = i2+1; i3 < m; i3++){
                int sz = __builtin_popcount(i12 & lp[i3]);
                if (sz < best){ best = sz; cnt = 1; }
                else if (sz == best) cnt++;
            }
        }
    return 10000L*best - (cnt < 9999 ? cnt : 9999);
}

static void print_state(FILE *f){
    fprintf(f, "n=%d edges:", n);
    for (int a = 0; a < n; a++)
        for (int b = a+1; b < n; b++)
            if ((adj[a]>>b)&1) fprintf(f, " %d-%d:%d", a, b, wt[a][b]);
    fprintf(f, "\n");
}

int main(int argc, char **argv){
    n = atoi(argv[1]);
    rng = strtoull(argv[2], 0, 10) * 2654435761u + 88172645463325252ull;
    long iters = atol(argv[3]);
    if (argc > 4) dmax = atoi(argv[4]);
    if (argc > 5) W = atoi(argv[5]);
    dpw = malloc((size_t)(1<<n)*n*sizeof(int16_t));
    memset(adj, 0, sizeof(adj));
    memset(wt, 0, sizeof(wt));
    for (int v = 0; v+1 < n; v++){
        adj[v] |= 1u<<(v+1); adj[v+1] |= 1u<<v;
        wt[v][v+1] = wt[v+1][v] = 1 + rnd()%W;
    }
    for (int t = 0; t < n/2; t++){
        int a = rnd()%n, b = rnd()%n;
        if (a!=b && !((adj[a]>>b)&1)){
            adj[a] |= 1u<<b; adj[b] |= 1u<<a;
            wt[a][b] = wt[b][a] = 1 + rnd()%W;
        }
    }
    long E = evaluate();
    long best_seen = E;
    for (long it = 0; it < iters; it++){
        double T = 300.0 * (1.0 - (double)it/iters) + 5.0;
        int a = rnd()%n, b = rnd()%n;
        if (a == b) continue;
        uint16_t sa = adj[a], sb = adj[b];
        int8_t sw = wt[a][b];
        int had = (adj[a]>>b)&1;
        int mv = rnd()%10;
        if (had && mv < 6){
            /* reweight */
            int nw = wt[a][b] + ((rnd()&1) ? 1 : -1);
            if (nw < 1 || nw > W) continue;
            wt[a][b] = wt[b][a] = (int8_t)nw;
        } else if (had){
            adj[a] &= ~(1u<<b); adj[b] &= ~(1u<<a); wt[a][b] = wt[b][a] = 0;
            if (!connected()){ adj[a]=sa; adj[b]=sb; wt[a][b]=wt[b][a]=sw; continue; }
        } else {
            if (__builtin_popcount(adj[a])>=dmax || __builtin_popcount(adj[b])>=dmax) continue;
            adj[a] |= 1u<<b; adj[b] |= 1u<<a;
            wt[a][b] = wt[b][a] = (int8_t)(1 + rnd()%W);
        }
        long E2 = evaluate();
        if (E2 < 10000){
            printf("HIT energy=%ld ", E2); print_state(stdout); fflush(stdout);
        }
        double dE = (double)(E2 - E);
        if (dE <= 0 || (double)(rnd()%1000000)/1000000.0 < 1.0/(1.0+dE/T)){
            E = E2;
            if (E < best_seen) best_seen = E;
        } else { adj[a]=sa; adj[b]=sb; wt[a][b]=sw; wt[b][a]=sw; }
        if (it % 100000 == 0)
            fprintf(stderr, "it=%ld T=%.1f E=%ld best=%ld\n", it, T, E, best_seen);
    }
    fprintf(stderr, "done best=%ld\n", best_seen);
    return 0;
}

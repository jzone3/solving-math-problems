/* Structure-targeted simulated annealing for a direct Gallai-3 counterexample
 * at sizes beyond exhaustive reach (n = 15..18).
 *
 * State: connected graph on n vertices (adjacency bitmask), sparse.
 * Exact evaluation via subset DP (reach[mask] = endpoint bitset), collecting
 * all longest-path vertex sets (capped at SAMPLE_CAP by reservoir sampling).
 * Energy = 10000 * (min triple intersection) - (#triples at min, capped).
 * Moves: toggle random non-bridge edge (keep connected, degree <= dmax).
 * Any energy < 10000 (i.e. empty triple) is printed as HIT with the graph6.
 *
 * Usage: anneal n seed iters [maxdeg]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 20
#define SAMPLE_CAP 160

static int n, dmax = 4;
static uint32_t adj[MAXN];
static uint32_t *reach;

static uint64_t rng;
static inline uint64_t rnd(void){
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng;
}

static int connected(void){
    uint32_t seen = 1, frontier = 1, full = (1u<<n)-1;
    while (frontier){
        uint32_t nxt = 0, f = frontier;
        while (f){ int v = __builtin_ctz(f); f &= f-1; nxt |= adj[v]; }
        frontier = nxt & ~seen; seen |= nxt;
    }
    return seen == full;
}

static uint32_t lp[1<<21]; /* longest masks buffer (big; only first m used) */

/* returns energy; fills g6 hit via caller check */
static long evaluate(void){
    int full = 1<<n;
    memset(reach, 0, full*sizeof(uint32_t));
    for (int v = 0; v < n; v++) reach[1u<<v] = 1u<<v;
    int best_pc = 1;
    for (int mask = 1; mask < full; mask++){
        uint32_t ends = reach[mask];
        if (!ends) continue;
        int pc = __builtin_popcount((uint32_t)mask);
        if (pc > best_pc) best_pc = pc;
        uint32_t e = ends;
        while (e){
            int v = __builtin_ctz(e); e &= e-1;
            uint32_t ext = adj[v] & ~(uint32_t)mask;
            while (ext){
                int w = __builtin_ctz(ext); ext &= ext-1;
                reach[mask | (1u<<w)] |= 1u<<w;
            }
        }
    }
    /* reservoir-sample longest masks */
    int m = 0; long seen_cnt = 0;
    uint32_t andall = 0xFFFFFFFF;
    for (int mask = 1; mask < full; mask++){
        if (reach[mask] && __builtin_popcount((uint32_t)mask) == best_pc){
            andall &= (uint32_t)mask;
            seen_cnt++;
            if (m < SAMPLE_CAP) lp[m++] = (uint32_t)mask;
            else { long j = rnd() % seen_cnt; if (j < SAMPLE_CAP) lp[j] = (uint32_t)mask; }
        }
    }
    if (m < 3) return 1000000; /* too few longest paths */
    if (andall) {
        /* all longest paths share pc(andall) vertices: gradient toward 0 */
        return 10000 + 500L*__builtin_popcount(andall) - (m < 499 ? m : 499);
    }
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

static void print_g6(FILE *f){
    /* graph6 for n<=20 */
    fputc(n+63, f);
    int bit = 0, acc = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++){
            acc = (acc<<1) | ((adj[i]>>j)&1);
            if (++bit == 6){ fputc(acc+63, f); bit = 0; acc = 0; }
        }
    if (bit) fputc((acc << (6-bit)) + 63, f);
    fputc('\n', f);
}

int main(int argc, char **argv){
    n = atoi(argv[1]);
    rng = strtoull(argv[2], 0, 10) * 2654435761u + 88172645463325252ull;
    long iters = atol(argv[3]);
    if (argc > 4) dmax = atoi(argv[4]);
    reach = malloc((1<<n)*sizeof(uint32_t));
    /* init: random path + a few chords */
    memset(adj, 0, sizeof(adj));
    for (int v = 0; v+1 < n; v++){ adj[v] |= 1u<<(v+1); adj[v+1] |= 1u<<v; }
    for (int t = 0; t < n/2; t++){
        int a = rnd()%n, b = rnd()%n;
        if (a!=b){ adj[a] |= 1u<<b; adj[b] |= 1u<<a; }
    }
    long E = evaluate();
    double T = 300.0;
    long best_seen = E;
    for (long it = 0; it < iters; it++){
        T = 300.0 * (1.0 - (double)it/iters) + 5.0;
        int a = rnd()%n, b = rnd()%n;
        if (a == b) continue;
        uint32_t sa = adj[a], sb = adj[b];
        int had = (adj[a]>>b)&1;
        if (had){ adj[a] &= ~(1u<<b); adj[b] &= ~(1u<<a); if(!connected()){ adj[a]=sa; adj[b]=sb; continue; } }
        else {
            if (__builtin_popcount(adj[a])>=dmax || __builtin_popcount(adj[b])>=dmax) continue;
            adj[a] |= 1u<<b; adj[b] |= 1u<<a;
        }
        long E2 = evaluate();
        if (E2 < 10000){
            printf("HIT energy=%ld ", E2); print_g6(stdout); fflush(stdout);
        }
        double dE = (double)(E2 - E);
        if (dE <= 0 || (double)(rnd()%1000000)/1000000.0 < 1.0/(1.0+dE/T)){
            E = E2;
            if (E < best_seen){ best_seen = E; }
        } else { adj[a]=sa; adj[b]=sb; }
        if (it % 20000 == 0)
            fprintf(stderr, "it=%ld T=%.1f E=%ld best=%ld\n", it, T, E, best_seen);
    }
    fprintf(stderr, "done best=%ld\n", best_seen);
    return 0;
}

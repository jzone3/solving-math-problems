/* search1h.c — constraint-driven exhaustive search for uniquely hamiltonian
 * 4-regular simple graphs (Sheehan's conjecture, P01, variant V4).
 *
 * Encoding: every hamiltonian 4-regular graph on n vertices is (up to iso)
 * the cycle C_n = (0,1,...,n-1) plus a set of n chords forming a 2-regular
 * graph on the same vertex set, chords disjoint from cycle edges.
 *
 * DFS over chord assignments, vertex by vertex. Core pruning:
 *   - after adding chord (v,u), search for a hamiltonian cycle through (v,u)
 *     in the current partial graph (cycle + chords so far). Any such cycle is
 *     a second HC (the base cycle uses no chords), and HCs persist in
 *     supergraphs, so the whole subtree is pruned.
 *   - rotation symmetry: vertex 0 must have the lexicographically minimal
 *     sorted chord-length pair among all vertices (lengths measured along the
 *     cycle, in 2..n/2). Any fully-assigned vertex with a smaller pair prunes.
 *   - reflection through vertex 0: chord pair of vertex 0 {a,b} (as vertex
 *     labels) must satisfy min(a,b) <= n - max(a,b) ... handled via length
 *     pair minimality + tie-break on labels (cheap partial break; duplicates
 *     only cost time, never correctness).
 *   - parity/feasibility of remaining chord deficiencies.
 *
 * A DFS leaf (all vertices chord-degree 2, no second HC found on any added
 * chord) is a uniquely hamiltonian 4-regular graph => counterexample.
 * Leaves are re-verified by an exact HC count before being reported.
 *
 * Options: -g4 / -g5 impose girth >= 4 / 5 (forbids short chords and
 * chord-chord triangles/squares via explicit checks).
 * -mod M -res R: split the search space by the residue of the top-level
 * branch counter for trivial parallelisation.
 *
 * gcc -O3 -march=native -o search1h search1h.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int N;
static int GIRTH = 3;
static long long MOD = 1, RES = 0;
static int COUNTMODE = 0;
static long long min_hc = -1;
static unsigned long long nodes = 0, hc_calls = 0, leaves = 0;
static long long top_counter = 0;

#define MAXN 34
static int deg[MAXN];               /* chord degree, 0..2 */
static int cadj[MAXN][2];           /* chord neighbours */
static int adj[MAXN][4];            /* full adjacency (cycle + chords) */
static int adeg[MAXN];
static uint64_t amask[MAXN];        /* adjacency bitmask */

static inline int clen(int u, int v){ int d = u>v? u-v : v-u; return d < N-d ? d : N-d; }

/* vertex 0 chord length pair (sorted), set when vertex 0 completed */
static int p0a = -1, p0b = -1;

/* ---- exact hamiltonian-cycle search through a specific edge (u,v) ----
 * returns 1 if there is a hamiltonian cycle of the current graph that uses
 * edge (u,v). Simple DFS with degree pruning. */
static int hcv_target;
static uint64_t hcv_full;

static int hc_dfs(int v, uint64_t visited){
    if (visited == hcv_full)
        return (amask[v] >> hcv_target) & 1ULL;
    /* prune: every unvisited vertex needs >=2 available nbrs (unvisited, or
       the current head v, or the target); vertices with exactly 2 that
       include v are forced moves. */
    uint64_t avail = ~visited | (1ULL << v) | (1ULL << hcv_target);
    uint64_t un = hcv_full & ~visited;
    int forced = -1;
    for (uint64_t m = un; m; m &= m - 1){
        int w = __builtin_ctzll(m);
        uint64_t a = amask[w] & avail;
        int d = __builtin_popcountll(a);
        if (d < 2) return 0;
        if (d == 2 && ((amask[w] >> v) & 1ULL) && ((visited >> w) & 1ULL) == 0)
            if ((a >> v) & 1ULL) forced = w;
    }
    if (forced >= 0)
        return hc_dfs(forced, visited | (1ULL << forced));
    for (int i = 0; i < adeg[v]; i++){
        int w = adj[v][i];
        if (!((visited >> w) & 1ULL))
            if (hc_dfs(w, visited | (1ULL << w))) return 1;
    }
    return 0;
}

static int has_hc_through(int u, int v){
    hc_calls++;
    /* hamiltonian path from v to u in G, then close with edge (u,v). Start at
       u, force first step to v: path u-v-...-u covering all. */
    hcv_target = u;
    hcv_full = (N == 64) ? ~0ULL : ((1ULL << N) - 1);
    return hc_dfs(v, (1ULL << u) | (1ULL << v));
}

/* exact HC count (undirected), for leaf re-verification */
static long long hc_count;
static void cnt_dfs(int v, uint64_t visited){
    if (visited == hcv_full){
        if (amask[v] & 1ULL) hc_count++;
        return;
    }
    for (int i = 0; i < adeg[v]; i++){
        int w = adj[v][i];
        if (!((visited >> w) & 1ULL)) cnt_dfs(w, visited | (1ULL << w));
    }
}
static long long count_hc(void){
    hc_count = 0;
    hcv_full = (1ULL << N) - 1;
    cnt_dfs(0, 1ULL);
    return hc_count / 2;
}

static void add_edge(int u, int v){
    adj[u][adeg[u]++] = v; adj[v][adeg[v]++] = u;
    amask[u] |= 1ULL << v; amask[v] |= 1ULL << u;
}
static void del_edge(int u, int v){
    adeg[u]--; adeg[v]--;
    amask[u] &= ~(1ULL << v); amask[v] &= ~(1ULL << u);
}

static int girth_ok(int u, int v){
    if (GIRTH >= 4 && clen(u, v) == 2) return 0;              /* triangle with cycle */
    if (GIRTH >= 5 && clen(u, v) <= 3) return 0;
    if (GIRTH >= 4){
        /* no common neighbour (triangle) */
        if (amask[u] & amask[v]) return 0;
    }
    if (GIRTH >= 5){
        /* no path of length 2 or 3 between u and v in current graph */
        for (int i = 0; i < adeg[u]; i++){
            int w = adj[u][i];
            if (amask[w] & amask[v]) return 0; /* u-w-x-v square */
        }
    }
    return 1;
}

static void report(void){
    long long c = count_hc();
    if (COUNTMODE){
        if (min_hc < 0 || c < min_hc) min_hc = c;
        return;
    }
    fprintf(stderr, "LEAF n=%d HCcount=%lld chords:", N, c);
    for (int v = 0; v < N; v++)
        for (int i = 0; i < deg[v]; i++)
            if (cadj[v][i] > v) fprintf(stderr, " (%d,%d)", v, cadj[v][i]);
    fprintf(stderr, "\n");
    if (c == 1){
        printf("COUNTEREXAMPLE n=%d\n", N);
        for (int v = 0; v < N; v++)
            for (int i = 0; i < deg[v]; i++)
                if (cadj[v][i] > v) printf("%d %d\n", v, cadj[v][i]);
        fflush(stdout);
    }
}

static void search(int v){
    nodes++;
    while (v < N && deg[v] == 2){
        /* rotation-canonicity: completed vertex must not beat vertex 0 */
        if (v > 0 && p0a >= 0){
            int a = clen(v, cadj[v][0]), b = clen(v, cadj[v][1]);
            int lo = a < b ? a : b, hi = a < b ? b : a;
            if (lo < p0a || (lo == p0a && hi < p0b)) return;
        }
        v++;
    }
    if (v == N){ leaves++; report(); return; }
    /* choose a partner for v's next chord: partner u > v (all earlier are full),
       u not cycle-adjacent to v, deg[u]<2, not already a chord */
    int start = v + 2;
    /* avoid unordered duplicates of the two chords chosen AT v */
    if (deg[v] == 1 && cadj[v][0] > v && cadj[v][0] + 1 > start)
        start = cadj[v][0] + 1;
    for (int u = start; u < N; u++){
        if (v == 0 && u == N - 1) continue;         /* cycle edge (0,n-1) */
        if (deg[u] >= 2) continue;
        if ((amask[v] >> u) & 1ULL) continue;       /* already chord */
        if (!girth_ok(v, u)) continue;
        if (v == 0 && deg[0] == 1){
            /* split work over the (first,second)-chord pairs of vertex 0 */
            top_counter++;
            if (MOD > 1 && (top_counter % MOD) != RES) continue;
        }
        /* tentative add */
        deg[v]++; deg[u]++;
        cadj[v][deg[v]-1] = u; cadj[u][deg[u]-1] = v;
        add_edge(v, u);
        int was_p0 = 0;
        if (v == 0 && deg[0] == 2){
            int a = clen(0, cadj[0][0]), b = clen(0, cadj[0][1]);
            p0a = a < b ? a : b; p0b = a < b ? b : a;
            was_p0 = 1;
        }
        if (COUNTMODE || !has_hc_through(v, u))
            search(v);
        if (was_p0){ p0a = p0b = -1; }
        del_edge(v, u);
        deg[v]--; deg[u]--;
    }
}

int main(int argc, char **argv){
    N = atoi(argv[1]);
    for (int i = 2; i < argc; i++){
        if (!strcmp(argv[i], "-g4")) GIRTH = 4;
        else if (!strcmp(argv[i], "-g5")) GIRTH = 5;
        else if (!strcmp(argv[i], "-mod")) MOD = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-res")) RES = atoll(argv[++i]);
        else if (!strcmp(argv[i], "-count")) COUNTMODE = 1;
    }
    for (int v = 0; v < N; v++){
        adeg[v] = 0; amask[v] = 0; deg[v] = 0;
    }
    for (int v = 0; v < N; v++) add_edge(v, (v + 1) % N);
    search(0);
    fprintf(stderr, "DONE n=%d girth>=%d mod=%lld res=%lld nodes=%llu hc_calls=%llu leaves=%llu\n",
            N, GIRTH, MOD, RES, nodes, hc_calls, leaves);
    if (COUNTMODE) fprintf(stderr, "MINHC n=%d girth>=%d min=%lld over %llu labeled leaves\n", N, GIRTH, min_hc, leaves);
    return 0;
}

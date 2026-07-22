/* Structured completion DFS in C.
 *
 * WLOG a 4-regular uniquely hamiltonian graph on n vertices is C_n (the unique
 * HC, vertices 0..n-1 in cycle order) plus a set of chords in which every
 * vertex lies on exactly 2 chords, such that no chord subset creates a second
 * hamiltonian cycle. Since adding edges never destroys HCs, EVERY intermediate
 * graph (C_n + partial chord set) must have HC count exactly 1; a chord (u,v)
 * is addable iff the current graph has no hamiltonian u-v path.
 *
 * DFS over chord additions; each candidate chord validated by a hamiltonian
 * u-v path existence test (with pruning). Randomized ordering + restarts.
 *
 * Usage: ./dfs n seed time_budget_seconds [exhaust]
 *   exhaust=1: deterministic full enumeration with symmetry breaking on the
 *   first chord (first chord fixed to involve vertex 0 with the smallest gap,
 *   using dihedral symmetry of C_n).
 * Prints near-misses (chords placed) and any full witness (then exits 42).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 64
static int n;
static int adj[MAXN][MAXN];   /* adjacency matrix incl. cycle edges */
static int deg[MAXN];         /* chord-degree (0..2) */
static int nbr[MAXN][8], nd[MAXN]; /* adjacency lists */
static int visited[MAXN];
static double t_end;
static long long max_nodes;
static int best_rem;
static unsigned long long rng_s;
static long long nodes;

static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+1e-9*ts.tv_nsec; }
static unsigned long long rnd(void){ rng_s^=rng_s<<13; rng_s^=rng_s>>7; rng_s^=rng_s<<17; return rng_s; }

/* is there a hamiltonian path from s to t in current graph? */
static int target;
static int hp_dfs(int u, int depth) {
    if (depth == n) return adj[u][target] ? 1 : 0;
    for (int i = 0; i < nd[u]; i++) {
        int v = nbr[u][i];
        if (visited[v] || v == target) continue;
        /* prune: unvisited neighbor w of v (w!=target) with no remaining access */
        visited[v] = 1;
        int ok = 1;
        for (int j = 0; j < nd[v]; j++) {
            int w = nbr[v][j];
            if (visited[w] || w == target) continue;
            int acc = 0;
            for (int k = 0; k < nd[w]; k++) {
                int x = nbr[w][k];
                if (!visited[x] || x == target) { acc++; if (acc>=1) break; }
            }
            /* w is adjacent to the new endpoint v (it appears in v's list), so it
               needs >=1 further connection among unvisited vertices or target */
            if (acc < 1) { ok = 0; break; }
        }
        if (ok && hp_dfs(v, depth + 1)) { visited[v]=0; return 1; }
        visited[v] = 0;
    }
    return 0;
}

static int ham_path_exists(int s, int t) {
    memset(visited, 0, sizeof(visited));
    visited[s] = 1;
    target = t;
    return hp_dfs(s, 2); /* depth counts vertices on path so far incl s and (later) t: start=2 means s + t reserved */
}

static void add_edge(int u,int v){ adj[u][v]=adj[v][u]=1; nbr[u][nd[u]++]=v; nbr[v][nd[v]++]=u; deg[u]++; deg[v]++; }
static void del_edge(int u,int v){ adj[u][v]=adj[v][u]=0; nd[u]--; nd[v]--; deg[u]--; deg[v]--; }

static int chords[MAXN][2]; static int nch;

static int dfs(void) {
    nodes++;
    if (nodes > max_nodes) return -1;
    if ((nodes & 1023)==0 && now() > t_end) return -1;
    /* pick unfilled vertex with max chord-degree (most constrained), tie->lowest index */
    int u = -1;
    for (int v = 0; v < n; v++)
        if (deg[v] < 2 && (u == -1 || deg[v] > deg[u])) u = v;
    if (u == -1) {
        /* complete! */
        FILE *f = fopen("WITNESS.txt","a");
        fprintf(f,"DFS-C n=%d chords:",n);
        for (int i=0;i<nch;i++) fprintf(f," (%d,%d)",chords[i][0],chords[i][1]);
        fprintf(f,"\n"); fclose(f);
        printf("!!! WITNESS FOUND !!!\n");
        return 1;
    }
    int rem = 0;
    for (int v = 0; v < n; v++) rem += 2 - deg[v];
    if (rem < best_rem) {
        best_rem = rem;
        if (rem <= 6) { printf("rem=%d nodes=%lld\n", rem, nodes); fflush(stdout); }
    }
    int cands[MAXN], nc = 0;
    for (int v = 0; v < n; v++)
        if (v != u && deg[v] < 2 && !adj[u][v]) cands[nc++] = v;
    /* shuffle */
    for (int i = nc - 1; i > 0; i--) { int j = rnd() % (i + 1); int t2=cands[i]; cands[i]=cands[j]; cands[j]=t2; }
    for (int i = 0; i < nc; i++) {
        int v = cands[i];
        if (!ham_path_exists(u, v)) {
            add_edge(u, v);
            chords[nch][0]=u; chords[nch][1]=v; nch++;
            int r = dfs();
            if (r) return r;
            nch--;
            del_edge(u, v);
        }
        if (now() > t_end) return -1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 4 && strcmp(argv[4], "hptest") == 0) {
        /* stdin: m s t, then m edges; print 1 if ham s-t path exists */
        int m, s, t;
        if (scanf("%d %d %d", &m, &s, &t) != 3) return 1;
        n = atoi(argv[1]);
        memset(adj,0,sizeof(adj)); memset(nd,0,sizeof(nd));
        for (int i = 0; i < m; i++) {
            int u, v; if (scanf("%d %d",&u,&v)!=2) return 1;
            if (!adj[u][v]) { adj[u][v]=adj[v][u]=1; nbr[u][nd[u]++]=v; nbr[v][nd[v]++]=u; }
        }
        printf("%d\n", ham_path_exists(s, t));
        return 0;
    }
    n = atoi(argv[1]);
    rng_s = strtoull(argv[2], 0, 10) * 2654435761ULL + 12345;
    double budget = atof(argv[3]);
    max_nodes = argc > 4 ? atoll(argv[4]) : (1LL<<62);
    t_end = now() + budget;
    long restarts = 0;
    int global_best = 1000;
    while (now() < t_end) {
        memset(adj,0,sizeof(adj)); memset(deg,0,sizeof(deg)); memset(nd,0,sizeof(nd));
        for (int i = 0; i < n; i++) { int j=(i+1)%n; adj[i][j]=adj[j][i]=1; nbr[i][nd[i]++]=j; nbr[j][nd[j]++]=i; }
        memset(deg,0,sizeof(deg)); /* deg tracks chords only */
        nch = 0; best_rem = 2*n; nodes = 0;
        int r = dfs();
        restarts++;
        if (best_rem < global_best) {
            global_best = best_rem;
            printf("new best rem=%d (restart %ld)\n", global_best, restarts); fflush(stdout);
        }
        if (r == 1) { printf("FOUND after %ld restarts\n", restarts); return 42; }
    }
    printf("n=%d restarts=%ld best_rem_stubs=%d\n", n, restarts, global_best);
    return 0;
}

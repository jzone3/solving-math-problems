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
static int multi;             /* allow doubled chords (multigraph mode) */
static int cmult[MAXN][MAXN]; /* chord multiplicity */
/* Monotonicity memo: once a hamiltonian u-v path exists it exists in every
   supergraph, so the pair (u,v) is dead for the whole DFS subtree. Marks are
   recorded per dfs() call and cleared on exit. */
static int dead[MAXN][MAXN];

static int dfs(void) {
    nodes++;
    if (nodes > max_nodes) return -1;
    if ((nodes & 1023)==0 && now() > t_end) return -1;
    /* MRV: pick unfilled vertex with fewest live candidates */
    int u = -1, ubest = 1 << 30;
    for (int w = 0; w < n; w++) {
        if (deg[w] >= 2) continue;
        int c = 0;
        for (int v = 0; v < n; v++) {
            if (v == w || deg[v] >= 2 || dead[w][v]) continue;
            int cyc = (v == (w+1)%n || w == (v+1)%n);
            if (multi ? (!cyc && cmult[w][v] < 2) : !adj[w][v]) c++;
        }
        if (c < ubest) { ubest = c; u = w; }
    }
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
        if (rem <= 4) {
            FILE *f = fopen("nearmiss.txt", "a");
            fprintf(f, "NEAR n=%d multi=%d rem=%d chords:", n, multi, rem);
            for (int i = 0; i < nch; i++) fprintf(f, " (%d,%d)", chords[i][0], chords[i][1]);
            fprintf(f, " deficient:");
            for (int v = 0; v < n; v++) if (deg[v] < 2) fprintf(f, " %d(x%d)", v, 2 - deg[v]);
            fprintf(f, "\n"); fclose(f);
        }
    }
    if (ubest == 0) return 0; /* u has no live candidates: dead end */
    int cands[MAXN], nc = 0;
    for (int v = 0; v < n; v++) {
        if (v == u || deg[v] >= 2 || dead[u][v]) continue;
        int cyc = (v == (u+1)%n || u == (v+1)%n);
        if (multi) { if (!cyc && cmult[u][v] < 2) cands[nc++] = v; }
        else       { if (!adj[u][v]) cands[nc++] = v; }
    }
    /* shuffle */
    for (int i = nc - 1; i > 0; i--) { int j = rnd() % (i + 1); int t2=cands[i]; cands[i]=cands[j]; cands[j]=t2; }
    int aborted = 0;
    int marked[MAXN], nm = 0;
    for (int i = 0; i < nc; i++) {
        int v = cands[i];
        /* a second parallel chord copy creates no new vertex sequence, so only
           the first copy needs the ham-path test */
        int alive;
        if (cmult[u][v] > 0) alive = 1;
        else if (ham_path_exists(u, v)) {
            alive = 0;
            dead[u][v] = dead[v][u] = 1;
            marked[nm++] = v;
        } else alive = 1;
        if (alive) {
            add_edge(u, v); cmult[u][v]++; cmult[v][u]++;
            chords[nch][0]=u; chords[nch][1]=v; nch++;
            int r = dfs();
            if (r == 1) return 1;
            if (r == -1) aborted = 1;
            nch--;
            cmult[u][v]--; cmult[v][u]--;
            del_edge(u, v);
        }
        if (nodes > max_nodes || now() > t_end) { aborted = 1; break; }
    }
    for (int i = 0; i < nm; i++) { int v = marked[i]; dead[u][v] = dead[v][u] = 0; }
    return aborted ? -1 : 0;
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
    multi = argc > 5 && strcmp(argv[5], "multi") == 0;
    int seeded = argc > 5 && strcmp(argv[5], "seed") == 0;
    /* seed mode: stdin "c" then c chord pairs (graph = C_n + these chords, must
       already be uniquely hamiltonian with HC = C_n; caller verifies) */
    int nseed = 0; static int seedch[2*MAXN][2];
    if (seeded) {
        if (scanf("%d", &nseed) != 1) return 1;
        for (int i = 0; i < nseed; i++)
            if (scanf("%d %d", &seedch[i][0], &seedch[i][1]) != 2) return 1;
    }
    t_end = now() + budget;
    long restarts = 0;
    int global_best = 1000;
    while (now() < t_end) {
        memset(adj,0,sizeof(adj)); memset(deg,0,sizeof(deg)); memset(nd,0,sizeof(nd));
        memset(cmult,0,sizeof(cmult));
        memset(dead,0,sizeof(dead));
        for (int i = 0; i < n; i++) { int j=(i+1)%n; adj[i][j]=adj[j][i]=1; nbr[i][nd[i]++]=j; nbr[j][nd[j]++]=i; }
        memset(deg,0,sizeof(deg)); /* deg tracks chords only */
        nch = 0;
        for (int i = 0; i < nseed; i++) {
            int u = seedch[i][0], v = seedch[i][1];
            add_edge(u, v); cmult[u][v]++; cmult[v][u]++;
            chords[nch][0]=u; chords[nch][1]=v; nch++;
        }
        best_rem = 2*n; nodes = 0;
        int r = dfs();
        restarts++;
        if (best_rem < global_best) {
            global_best = best_rem;
            printf("new best rem=%d (restart %ld)\n", global_best, restarts); fflush(stdout);
        }
        if (r == 1) { printf("FOUND after %ld restarts\n", restarts); return 42; }
        if (r == 0) { printf("EXHAUSTED n=%d (multi=%d): no witness; tree fully explored, nodes=%lld\n", n, multi, nodes); return 0; }
    }
    printf("n=%d restarts=%ld best_rem_stubs=%d\n", n, restarts, global_best);
    return 0;
}

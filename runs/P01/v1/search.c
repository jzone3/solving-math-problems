/* P01 Sheehan V1: annealed local search over Hamiltonian 4-regular simple graphs.
 * Objective: minimize number of Hamiltonian cycles (capped), target exactly 1.
 * Moves: 2-opt edge swaps preserving 4-regularity (swap only among non-cycle
 * "chord" 2-factor edges in one mode, or any edges in another mode).
 *
 * Usage: ./search n seed max_iters cap time_limit_sec
 * Prints progress; if a graph with exactly 1 HC is found, prints WITNESS with
 * adjacency list and exits.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAXN 64

static int n;
static unsigned char adj[MAXN][MAXN];   /* adjacency matrix */
static int nbr[MAXN][4];                /* neighbor lists (deg 4) */
static int deg[MAXN];

/* xorshift rng */
static unsigned long long rngstate;
static unsigned long long xrand(void){
    rngstate ^= rngstate << 13; rngstate ^= rngstate >> 7; rngstate ^= rngstate << 17;
    return rngstate;
}
static int randint(int m){ return (int)(xrand() % (unsigned long long)m); }

static void rebuild_nbrs(void){
    for(int i=0;i<n;i++){ deg[i]=0;
        for(int j=0;j<n;j++) if(adj[i][j]) nbr[i][deg[i]++]=j;
    }
}

/* ---- Hamiltonian cycle counting with cutoff ----
 * DFS from vertex 0, only extend in one direction; to avoid double counting
 * each cycle (traversed both ways), require second vertex < last vertex... simpler:
 * count directed cycles starting 0 -> min neighbor direction: we count each cycle
 * twice and divide; with cutoff we instead force first step to smaller-indexed
 * neighbor than the closing step. Easiest robust approach: count directed
 * Hamiltonian cycles starting at 0 and divide by 2 (cutoff *2).
 */
static int hc_count_cap;
static int hc_count;      /* directed count */
static unsigned char used[MAXN];
static int order_left[MAXN]; /* remaining unvisited count not needed explicitly */

/* prune: every unvisited vertex must have >=2 free (unvisited or endpoint(0)/current) neighbors */
static int freedeg[MAXN]; /* number of unvisited neighbors + (neighbor==0) */

/* prune (safe relaxation): every unvisited u must have
 * freedeg[u] + adj[u][head] >= 2, where freedeg counts unvisited neighbors
 * plus adjacency to vertex 0 (0 is never decremented: it stays "free" as the
 * closing endpoint). */
static void dfs(int v, int depth){
    if(hc_count >= hc_count_cap) return;
    if(depth == n){
        if(adj[v][0]) hc_count++;
        return;
    }
    for(int k=0;k<4;k++){
        int w = nbr[v][k];
        if(used[w]) continue;
        used[w]=1;
        for(int t=0;t<4;t++) freedeg[nbr[w][t]]--;
        int ok = 1;
        for(int u=1;u<n;u++){
            if(!used[u] && freedeg[u] + adj[u][w] < 2){ ok=0; break; }
        }
        if(ok) dfs(w, depth+1);
        for(int t=0;t<4;t++) freedeg[nbr[w][t]]++;
        used[w]=0;
        if(hc_count >= hc_count_cap) return;
    }
}

/* returns undirected HC count, capped at cap */
static int count_hc(int cap){
    hc_count_cap = cap*2;
    hc_count = 0;
    memset(used,0,sizeof(used));
    for(int i=0;i<n;i++){
        freedeg[i]=0;
        for(int k=0;k<4;k++){ int u=nbr[i][k]; if(!used[u]) freedeg[i]++; }
    }
    /* freedeg counts unvisited neighbors; vertex 0 counts as available (it's endpoint) */
    used[0]=1;
    /* after marking 0 used, decrement freedeg of its neighbors? 0 is the endpoint so
       it remains "available" for closing; keep freedeg counting 0 as free. */
    dfs(0, 1);
    return hc_count/2;
}

/* build random Hamiltonian 4-regular graph: cycle 0..n-1 + random 2-factor (as a
 * random permutation-cycle structure) avoiding existing edges */
static int build_random(void){
    memset(adj,0,sizeof(adj));
    for(int i=0;i<n;i++){ adj[i][(i+1)%n]=1; adj[(i+1)%n][i]=1; }
    /* random second Hamiltonian-ish 2-factor: random permutation p, connect p[i]-p[i+1] cyclically.
       Retry if it creates duplicate edges. */
    int p[MAXN];
    for(int tries=0; tries<2000; tries++){
        for(int i=0;i<n;i++) p[i]=i;
        for(int i=n-1;i>0;i--){ int j=randint(i+1); int t=p[i];p[i]=p[j];p[j]=t; }
        int ok=1;
        for(int i=0;i<n && ok;i++){
            int a=p[i], b=p[(i+1)%n];
            if(adj[a][b]) ok=0;
        }
        if(ok){
            for(int i=0;i<n;i++){ int a=p[i], b=p[(i+1)%n]; adj[a][b]=1; adj[b][a]=1; }
            rebuild_nbrs();
            return 1;
        }
    }
    return 0;
}

/* 2-opt swap: pick edges (a,b),(c,d) with all distinct, replace by (a,c),(b,d)
 * or (a,d),(b,c) if simple. Returns 1 and fills undo info if applied. */
static int last_a,last_b,last_c,last_d,last_mode;
static int try_swap(void){
    for(int t=0;t<200;t++){
        int a = randint(n);
        int b = nbr[a][randint(4)];
        int c = randint(n);
        int d = nbr[c][randint(4)];
        if(a==c||a==d||b==c||b==d) continue;
        int mode = randint(2);
        int x1,x2,y1,y2;
        if(mode==0){ x1=a;x2=c; y1=b;y2=d; } else { x1=a;x2=d; y1=b;y2=c; }
        if(adj[x1][x2]||adj[y1][y2]) continue;
        adj[a][b]=adj[b][a]=0; adj[c][d]=adj[d][c]=0;
        adj[x1][x2]=adj[x2][x1]=1; adj[y1][y2]=adj[y2][y1]=1;
        last_a=a;last_b=b;last_c=c;last_d=d;last_mode=mode;
        rebuild_nbrs();
        return 1;
    }
    return 0;
}
static void undo_swap(void){
    int a=last_a,b=last_b,c=last_c,d=last_d;
    int x1,x2,y1,y2;
    if(last_mode==0){ x1=a;x2=c; y1=b;y2=d; } else { x1=a;x2=d; y1=b;y2=c; }
    adj[x1][x2]=adj[x2][x1]=0; adj[y1][y2]=adj[y2][y1]=0;
    adj[a][b]=adj[b][a]=1; adj[c][d]=adj[d][c]=1;
    rebuild_nbrs();
}

static double objective(int cnt){
    if(cnt==0) return 1e6;           /* lost Hamiltonicity */
    return log((double)cnt);         /* minimize; 1 -> 0 */
}

static void print_graph(const char* tag, int cnt){
    printf("%s n=%d hc=%d edges:", tag, n, cnt);
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) if(adj[i][j]) printf(" %d-%d", i, j);
    printf("\n"); fflush(stdout);
}

int main(int argc, char**argv){
    if(argc>=2 && strcmp(argv[1],"count")==0){
        /* read: n, then edges "a b" until EOF; print exact HC count (cap 1000000) */
        if(scanf("%d",&n)!=1) return 2;
        memset(adj,0,sizeof(adj));
        int a,b;
        while(scanf("%d %d",&a,&b)==2){ adj[a][b]=adj[b][a]=1; }
        rebuild_nbrs();
        for(int i=0;i<n;i++) if(deg[i]!=4){ fprintf(stderr,"vertex %d deg %d != 4\n", i, deg[i]); return 2; }
        printf("%d\n", count_hc(1000000));
        return 0;
    }
    if(argc<6){ fprintf(stderr,"usage: %s n seed iters cap tlimit [hop]\n",argv[0]); return 2; }
    int hop = (argc>=7) ? atoi(argv[6]) : 0;   /* basin hopping: perturb best instead of random restart */
    n = atoi(argv[1]);
    rngstate = strtoull(argv[2],0,10) * 2654435761ULL + 88172645463325252ULL;
    long long iters = atoll(argv[3]);
    int cap = atoi(argv[4]);
    int tlimit = atoi(argv[5]);
    time_t t0 = time(0);

    int best_ever = 1<<30;
    static unsigned char best_adj[MAXN][MAXN];
    long long it_total = 0;
    while(time(0)-t0 < tlimit){
        if(hop && best_ever < (1<<30)){
            memcpy(adj, best_adj, sizeof(adj));
            rebuild_nbrs();
            for(int k=0;k<8;k++) try_swap();
        } else {
            if(!build_random()) continue;
        }
        int cur = count_hc(cap);
        if(cur==0) continue;
        double curobj = objective(cur);
        double T = 1.0;
        for(long long it=0; it<iters && time(0)-t0<tlimit; it++, it_total++){
            T = 0.30 * exp(-5.0*(double)it/(double)iters) + 0.02;
            if(!try_swap()) break;
            int dyncap = cur*2+8; if(dyncap>cap) dyncap=cap;
            int cnt = count_hc(dyncap);
            double obj = objective(cnt);
            if(obj <= curobj || exp((curobj-obj)/T) * 4294967296.0 > (double)(xrand()&0xffffffffULL)){
                cur = cnt; curobj = obj;
                if(cnt>0 && cnt < best_ever){
                    best_ever = cnt;
                    memcpy(best_adj, adj, sizeof(adj));
                    print_graph(cnt==1?"WITNESS":"BEST", cnt);
                    if(cnt==1) return 0;
                }
            } else {
                undo_swap();
            }
        }
        printf("restart: it_total=%lld best_ever=%d elapsed=%lds\n", it_total, best_ever, (long)(time(0)-t0));
        fflush(stdout);
    }
    printf("DONE n=%d best_ever=%d it_total=%lld\n", n, best_ever, it_total);
    return 1;
}

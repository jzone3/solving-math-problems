/* P01 Sheehan V1 continuation: multigraph-relaxation annealing.
 *
 * State space: 4-regular MULTIgraphs (edge multiplicities 0..2, no loops) on n vertices.
 * #HC counts each Hamiltonian cycle once per choice of parallel copies (product of
 * multiplicities of used edges) — the standard convention under which Fleischner's
 * uniquely hamiltonian 4-regular multigraphs have exactly one HC.
 *
 * Objective: log(#HC) + lambda * (#extra parallel copies). lambda ramps up during the
 * run, pushing toward SIMPLE graphs while keeping #HC low. A state with #HC == 1 and no
 * parallel edges would be a counterexample to Sheehan's conjecture.
 *
 * Modes:
 *   ./msearch n seed iters tlimit [lambda_max]   annealed search (random multigraph start)
 *   ./msearch count < graphfile                  exact weighted HC count (n, then "a b" lines,
 *                                                repeated lines = multiplicity)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAXN 64
#define CAP 2000000000LL

static int n;
static unsigned char mult[MAXN][MAXN];
static int nbr[MAXN][8];   /* neighbor list with repetition by multiplicity (deg 4) */
static int deg[MAXN];

static unsigned long long rngstate;
static unsigned long long xrand(void){
    rngstate ^= rngstate << 13; rngstate ^= rngstate >> 7; rngstate ^= rngstate << 17;
    return rngstate;
}
static int randint(int m){ return (int)(xrand() % (unsigned long long)m); }

static void rebuild_nbrs(void){
    for(int i=0;i<n;i++){ deg[i]=0;
        for(int j=0;j<n;j++) for(int k=0;k<mult[i][j];k++) nbr[i][deg[i]++]=j;
    }
}

static long long hc_cap, hc_count;
static unsigned char used[MAXN];
static int freedeg[MAXN];   /* sum of multiplicities to unvisited vertices (+ to vertex 0) */

static void dfs(int v, int depth, long long weight){
    if(hc_count >= hc_cap) return;
    if(depth == n){
        if(mult[v][0]) hc_count += weight * mult[v][0];
        return;
    }
    for(int w=0; w<n; w++){
        if(!mult[v][w] || used[w]) continue;
        used[w]=1;
        for(int u=0;u<n;u++) if(mult[w][u]) freedeg[u]-=mult[w][u];
        int ok = 1;
        for(int u=1;u<n;u++){
            if(!used[u] && freedeg[u] + mult[u][w] < 2){ ok=0; break; }
        }
        if(ok) dfs(w, depth+1, weight * mult[v][w]);
        for(int u=0;u<n;u++) if(mult[w][u]) freedeg[u]+=mult[w][u];
        used[w]=0;
        if(hc_count >= hc_cap) return;
    }
}

static long long count_hc(long long cap){
    hc_cap = cap*2; hc_count = 0;
    memset(used,0,sizeof(used));
    for(int i=0;i<n;i++){
        freedeg[i]=0;
        for(int u=0;u<n;u++) freedeg[i]+=mult[i][u];
    }
    used[0]=1;
    dfs(0, 1, 1);
    return hc_count/2;
}

static int extra_edges(void){
    int e=0;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) if(mult[i][j]>1) e += mult[i][j]-1;
    return e;
}

static int build_random(void){
    memset(mult,0,sizeof(mult));
    for(int i=0;i<n;i++){ mult[i][(i+1)%n]++; mult[(i+1)%n][i]++; }
    int p[MAXN];
    for(int tries=0; tries<2000; tries++){
        for(int i=0;i<n;i++) p[i]=i;
        for(int i=n-1;i>0;i--){ int j=randint(i+1); int t=p[i];p[i]=p[j];p[j]=t; }
        int ok=1;
        for(int i=0;i<n && ok;i++) if(mult[p[i]][p[(i+1)%n]]>=2) ok=0;
        if(ok){
            for(int i=0;i<n;i++){ int a=p[i], b=p[(i+1)%n]; mult[a][b]++; mult[b][a]++; }
            rebuild_nbrs();
            return 1;
        }
    }
    return 0;
}

static int last_a,last_b,last_c,last_d,last_mode;
static int try_swap(void){
    for(int t=0;t<300;t++){
        int a = randint(n);
        int b = nbr[a][randint(4)];
        int c = randint(n);
        int d = nbr[c][randint(4)];
        if(a==c||a==d||b==c||b==d) continue;
        int mode = randint(2);
        int x1,x2,y1,y2;
        if(mode==0){ x1=a;x2=c; y1=b;y2=d; } else { x1=a;x2=d; y1=b;y2=c; }
        if(mult[x1][x2]>=3 || mult[y1][y2]>=3) continue;   /* cap multiplicity at 2 */
        mult[a][b]--; mult[b][a]--; mult[c][d]--; mult[d][c]--;
        mult[x1][x2]++; mult[x2][x1]++; mult[y1][y2]++; mult[y2][y1]++;
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
    mult[x1][x2]--; mult[x2][x1]--; mult[y1][y2]--; mult[y2][y1]--;
    mult[a][b]++; mult[b][a]++; mult[c][d]++; mult[d][c]++;
    rebuild_nbrs();
}

static void print_graph(const char* tag, long long cnt, int xe){
    printf("%s n=%d hc=%lld extra=%d edges:", tag, n, cnt, xe);
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) for(int k=0;k<mult[i][j];k++) printf(" %d-%d", i, j);
    printf("\n"); fflush(stdout);
}

int main(int argc, char**argv){
    if(argc>=2 && strcmp(argv[1],"count")==0){
        if(scanf("%d",&n)!=1) return 2;
        memset(mult,0,sizeof(mult));
        int a,b;
        while(scanf("%d %d",&a,&b)==2){ mult[a][b]++; mult[b][a]++; }
        rebuild_nbrs();
        for(int i=0;i<n;i++) if(deg[i]!=4){ fprintf(stderr,"vertex %d deg %d != 4\n", i, deg[i]); return 2; }
        printf("%lld\n", count_hc(CAP));
        return 0;
    }
    if(argc<5){ fprintf(stderr,"usage: %s n seed iters tlimit [lambda_max]\n",argv[0]); return 2; }
    n = atoi(argv[1]);
    rngstate = strtoull(argv[2],0,10) * 2654435761ULL + 88172645463325252ULL;
    long long iters = atoll(argv[3]);
    int tlimit = atoi(argv[4]);
    double lambda_max = (argc>=6)? atof(argv[5]) : 2.0;
    time_t t0 = time(0);

    double best_score = 1e18;
    long long it_total = 0;
    int best_simple_hc = 1<<30;
    while(time(0)-t0 < tlimit){
        if(!build_random()) continue;
        long long cur = count_hc(200000);
        if(cur==0) continue;
        int xe = extra_edges();
        for(long long it=0; it<iters && time(0)-t0<tlimit; it++, it_total++){
            double frac = (double)it/(double)iters;
            double T = 0.30 * exp(-5.0*frac) + 0.02;
            double lambda = 0.1 + (lambda_max-0.1)*frac;
            if(!try_swap()) break;
            long long dyncap = cur*2+8; if(dyncap>200000) dyncap=200000;
            long long cnt = count_hc(dyncap);
            int nxe = extra_edges();
            double curobj = (cur==0? 1e6: log((double)cur)) + lambda*xe;
            double obj = (cnt==0? 1e6: log((double)cnt)) + lambda*nxe;
            if(obj <= curobj || exp((curobj-obj)/T) * 4294967296.0 > (double)(xrand()&0xffffffffULL)){
                cur = cnt; xe = nxe;
                if(cnt>0){
                    double score = log((double)cnt)*100 + xe;   /* report lexicographic-ish */
                    if(cnt==1 && xe==0){ print_graph("WITNESS", cnt, xe); return 0; }
                    if(cnt < 288 && score < best_score){
                        best_score = score;
                        print_graph("BEST", cnt, xe);
                    }
                    if(xe==0 && cnt < best_simple_hc){ best_simple_hc = (int)cnt; }
                }
            } else {
                undo_swap();
            }
        }
        printf("restart: it_total=%lld best_simple_hc=%d elapsed=%lds\n", it_total, best_simple_hc, (long)(time(0)-t0));
        fflush(stdout);
    }
    printf("DONE n=%d best_simple_hc=%d it_total=%lld\n", n, best_simple_hc, it_total);
    return 1;
}

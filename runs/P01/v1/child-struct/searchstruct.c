/* P01 Sheehan V1 child-struct: annealed search over CONSTRAINED families of
 * Hamiltonian 4-regular simple graphs:
 *   family 1: girth >= 5
 *   family 2: 4-connected (vertex connectivity >= 4)
 *   family 3: both
 * Objective: minimize exact number of Hamiltonian cycles (capped).
 * Moves: 2-opt edge swaps preserving 4-regularity; a move is rejected outright
 * if it breaks the family constraint. Seeds: file (edge list) or random
 * 4-regular + constraint-repair phase (hill climb minimizing short cycles /
 * small cuts before the main anneal).
 *
 * Usage: ./searchstruct n seed iters cap tlimit hop family [seedfile]
 *        ./searchstruct count family < graphfile   (exact count + constraint check)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>

uint64_t adjm[64];
extern long long count_hc_fast(long long cap);

#define MAXN 64

int n;
static unsigned char adj[MAXN][MAXN];
static int nbr[MAXN][4];
static int deg[MAXN];
static int family;   /* 1 girth>=5, 2 4-connected, 3 both */

static unsigned long long rngstate;
static unsigned long long xrand(void){
    rngstate ^= rngstate << 13; rngstate ^= rngstate >> 7; rngstate ^= rngstate << 17;
    return rngstate;
}
static int randint(int m){ return (int)(xrand() % (unsigned long long)m); }

static void rebuild_nbrs(void){
    for(int i=0;i<n;i++){ deg[i]=0; adjm[i]=0;
        for(int j=0;j<n;j++) if(adj[i][j]){ if(deg[i]<4) nbr[i][deg[i]]=j; deg[i]++; adjm[i] |= 1ULL<<j; }
    }
}

/* ---- girth ----
 * returns girth (length of shortest cycle), or 99 if acyclic (never here).
 * BFS from each vertex; shortest cycle through v found when an edge joins two
 * visited vertices at appropriate depths. Standard O(n*m). */
static int girth(void){
    static int distv[MAXN], par[MAXN], q[MAXN];
    int best = 99;
    for(int s=0;s<n;s++){
        for(int i=0;i<n;i++) distv[i] = -1;
        int qh=0, qt=0;
        distv[s]=0; par[s]=-1; q[qt++]=s;
        while(qh<qt){
            int v=q[qh++];
            if(2*distv[v] >= best) break;
            for(int k=0;k<deg[v] && k<4;k++){
                int w=nbr[v][k];
                if(w==par[v]) continue;
                if(distv[w]<0){ distv[w]=distv[v]+1; par[w]=v; q[qt++]=w; }
                else {
                    int c = distv[v]+distv[w]+1;
                    if(c<best) best=c;
                }
            }
        }
    }
    return best;
}
/* count cycles of length 3 and 4 (for repair objective) */
static int short_cycles(void){
    int tri=0, quad=0;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++){
        if(adj[i][j]){
            for(int k=j+1;k<n;k++) if(adj[i][k]&&adj[j][k]) tri++;
        }
    }
    /* C4: count paths i-j, i-k (j<k, j,k != i), pairs with common second neighbor */
    for(int j=0;j<n;j++) for(int k=j+1;k<n;k++){
        if(j==k) continue;
        int common=0;
        uint64_t c = adjm[j]&adjm[k];
        common = __builtin_popcountll(c);
        if(adj[j][k]) { /* common neighbors give triangles, not squares */ }
        quad += common*(common-1)/2;
    }
    return 10*tri + quad;   /* weight triangles higher */
}

/* ---- 4-connectivity check (brute force, obviously correct) ----
 * vertex connectivity >= 4 iff removing any set of <= 3 vertices leaves the
 * graph connected. n <= 40 => C(40,3) ~ 1e4 subsets, BFS each: cheap enough. */
static int connected_without(uint64_t removed){
    uint64_t vis = 0, all = (n==64)? ~0ULL : ((1ULL<<n)-1);
    all &= ~removed;
    if(all==0) return 1;
    int start = __builtin_ctzll(all);
    static int q[MAXN];
    int qh=0,qt=0;
    vis |= 1ULL<<start; q[qt++]=start;
    while(qh<qt){
        int v=q[qh++];
        uint64_t cand = adjm[v] & all & ~vis;
        while(cand){
            int w=__builtin_ctzll(cand); cand&=cand-1;
            vis |= 1ULL<<w; q[qt++]=w;
        }
    }
    return vis==all;
}
static int is_4connected(void){
    if(n<6) return 0;
    if(!connected_without(0)) return 0;
    for(int a=0;a<n;a++){
        if(!connected_without(1ULL<<a)) return 0;
        for(int b=a+1;b<n;b++){
            if(!connected_without((1ULL<<a)|(1ULL<<b))) return 0;
            for(int c=b+1;c<n;c++)
                if(!connected_without((1ULL<<a)|(1ULL<<b)|(1ULL<<c))) return 0;
        }
    }
    return 1;
}

static int constraint_ok(void){
    if((family&1) && girth()<5) return 0;
    if((family&2) && !is_4connected()) return 0;
    return 1;
}

static int build_random(void){
    memset(adj,0,sizeof(adj));
    for(int i=0;i<n;i++){ adj[i][(i+1)%n]=1; adj[(i+1)%n][i]=1; }
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

static int last_a,last_b,last_c,last_d,last_mode;
static int try_swap_raw(void){
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
/* constraint penalty: 0 iff the state is in the family; smooth for girth
 * (weighted count of short cycles), 0/1 indicator for 4-connectivity */
static double penalty(void){
    double p = 0.0;
    if(family&1) p += 0.25 * (double)short_cycles();
    if(family&2) p += is_4connected()? 0.0 : 3.0;
    return p;
}

/* repair: hill-climb from a random 4-regular graph into the constrained family */
static int repair(void){
    /* objective: (family&1 -> weighted short cycles) + (conn: #(s,t) deficits) */
    for(int outer=0; outer<40; outer++){
        if(!build_random()) return 0;
        int cur = 0;
        if(family&1) cur = short_cycles();
        int steps = 0;
        while(steps < 20000){
            if(family&1 && cur==0) break;
            if(family==2) break;   /* random is usually 4-connected; check below */
            if(!try_swap_raw()) break;
            int nw = short_cycles();
            if(nw <= cur) cur = nw;
            else undo_swap();
            steps++;
        }
        if((family&1) && short_cycles()!=0) continue;
        if(girth()<5 && (family&1)) continue;
        if(family>=2 && !is_4connected()) continue;
        if(constraint_ok()) return 1;
    }
    return 0;
}

static double objective(long long cnt){
    if(cnt==0) return 1e6;
    return log((double)cnt);
}

static void print_graph(const char* tag, long long cnt){
    printf("%s n=%d hc=%lld girth=%d conn4=%d edges:", tag, n, cnt, girth(), is_4connected());
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) if(adj[i][j]) printf(" %d-%d", i, j);
    printf("\n"); fflush(stdout);
}

int main(int argc, char**argv){
    if(argc>=2 && strcmp(argv[1],"count")==0){
        family = (argc>=3)? atoi(argv[2]) : 3;
        if(scanf("%d",&n)!=1) return 2;
        memset(adj,0,sizeof(adj));
        int a,b;
        while(scanf("%d %d",&a,&b)==2){ adj[a][b]=adj[b][a]=1; }
        rebuild_nbrs();
        for(int i=0;i<n;i++) if(deg[i]!=4){ fprintf(stderr,"vertex %d deg %d != 4\n", i, deg[i]); return 2; }
        printf("hc=%lld girth=%d conn4=%d\n", count_hc_fast(1000000), girth(), is_4connected());
        return 0;
    }
    if(argc>=2 && strcmp(argv[1],"g6min")==0){
        /* read graph6 lines from stdin (4-regular graphs); print per-graph
         * hc/girth/conn4 and track the min positive HC count; also print the
         * argmin graph at EOF. For exhaustive scans over geng output. */
        char line[256];
        long long best = -1; char bestline[256] = "";
        long long processed = 0;
        while(fgets(line,sizeof(line),stdin)){
            int len = 0; while(line[len] && line[len]!='\n') len++;
            if(len==0) continue;
            n = line[0]-63;
            if(n<5 || n>62){ fprintf(stderr,"bad g6 line\n"); continue; }
            memset(adj,0,sizeof(adj));
            int bitpos=0;
            for(int j=1;j<n;j++) for(int i=0;i<j;i++){
                int byte = 1 + bitpos/6, bit = 5 - bitpos%6;
                if(byte>=len){ fprintf(stderr,"g6 too short\n"); break; }
                if((line[byte]-63)>>bit & 1){ adj[i][j]=adj[j][i]=1; }
                bitpos++;
            }
            rebuild_nbrs();
            int reg4=1; for(int i=0;i<n;i++) if(deg[i]!=4) reg4=0;
            if(!reg4){ fprintf(stderr,"skip non-4-regular\n"); continue; }
            long long c = count_hc_fast(1000000);
            processed++;
            if(c>0 && (best<0 || c<best)){ best=c; strncpy(bestline,line,255);
                printf("NEWMIN hc=%lld girth=%d conn4=%d g6=%s\n", c, girth(), is_4connected(), line);
                fflush(stdout);
            }
        }
        printf("G6MIN processed=%lld min_hc=%lld argmin=%s\n", processed, best, bestline);
        return 0;
    }
    if(argc<8){ fprintf(stderr,"usage: %s n seed iters cap tlimit hop family [seedfile]\n",argv[0]); return 2; }
    n = atoi(argv[1]);
    rngstate = strtoull(argv[2],0,10) * 2654435761ULL + 88172645463325252ULL;
    long long iters = atoll(argv[3]);
    long long cap = atoll(argv[4]);
    int tlimit = atoi(argv[5]);
    int hop = atoi(argv[6]);
    family = atoi(argv[7]);
    time_t t0 = time(0);

    long long best_ever = 1LL<<40;
    static unsigned char best_adj[MAXN][MAXN];
    if(argc>=9){
        FILE* f = fopen(argv[8],"r");
        if(!f){ fprintf(stderr,"no seedfile\n"); return 2; }
        int nn,a,b; if(fscanf(f,"%d",&nn)!=1 || nn!=n){ fprintf(stderr,"seedfile n mismatch\n"); return 2; }
        memset(best_adj,0,sizeof(best_adj));
        while(fscanf(f,"%d %d",&a,&b)==2){ best_adj[a][b]=best_adj[b][a]=1; }
        fclose(f);
        memcpy(adj,best_adj,sizeof(adj)); rebuild_nbrs();
        if(!constraint_ok()){ fprintf(stderr,"seed violates family %d constraint (girth=%d conn4=%d)\n", family, girth(), is_4connected()); return 2; }
        best_ever = count_hc_fast(1000000);
        print_graph("SEED", best_ever);
    }
    long long it_total = 0;
    while(time(0)-t0 < tlimit){
        if(hop && best_ever < (1LL<<40)){
            memcpy(adj, best_adj, sizeof(adj));
            rebuild_nbrs();
            for(int k=0;k<8;k++) try_swap_raw();
        } else {
            if(!repair()){ fprintf(stderr,"repair failed at n=%d family=%d\n", n, family); return 1; }
        }
        long long cur = count_hc_fast(cap);
        if(cur==0) continue;
        double curobj = objective(cur) + penalty();
        double T = 1.0;
        for(long long it=0; it<iters && time(0)-t0<tlimit; it++, it_total++){
            T = 0.30 * exp(-5.0*(double)it/(double)iters) + 0.02;
            if(!try_swap_raw()) break;
            double pen = penalty();
            long long dyncap = cur*2+8; if(dyncap>cap) dyncap=cap;
            long long cnt = count_hc_fast(dyncap);
            double obj = objective(cnt) + pen;
            if(obj <= curobj || exp((curobj-obj)/T) * 4294967296.0 > (double)(xrand()&0xffffffffULL)){
                cur = cnt; curobj = obj;
                if(cnt>0 && pen==0.0 && cnt < best_ever){
                    best_ever = cnt;
                    memcpy(best_adj, adj, sizeof(adj));
                    print_graph(cnt==1?"WITNESS":"BEST", cnt);
                    if(cnt==1 && constraint_ok()) return 0;
                }
            } else {
                undo_swap();
            }
        }
        printf("restart: it_total=%lld best_ever=%lld elapsed=%lds\n", it_total, best_ever, (long)(time(0)-t0));
        fflush(stdout);
    }
    printf("DONE n=%d family=%d best_ever=%lld it_total=%lld\n", n, family, best_ever, it_total);
    return 1;
}

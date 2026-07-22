/* P01 V5 targeted search: 4-regular G = C_n + chord 2-factor F, minimize #HC.
 * Structural conditions used (see NOTES.md):
 *  (C2) search space = simple 2-factors F edge-disjoint from C_n
 *  (C4) hard-reject parallel adjacent chords (i,j)&(i+1,j+1): they force a 2nd HC
 * Energy = number of Hamiltonian cycles, counted by pruned bitmask DFS with cutoff.
 * Pruning is conservative (never discards a valid HC): a vertex is only pruned if,
 * even crediting adjacency to the current endpoint and to the start vertex, it
 * cannot retain 2 usable HC-edges.
 * Usage: ./anneal n seed iters cutoff [restarts]
 * Prints improvements; on energy==1 prints WITNESS chord list and exits 42.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 64
typedef unsigned long long u64;
static int n;
static int ch[MAXN][2];       /* two chord neighbours of each vertex */
static int adj[MAXN][4];      /* full adjacency: cycle nbrs + chords */
static u64 nbr[MAXN];         /* neighbour bitmask */
static u64 rng_s;
static u64 rnd(void){ /* xorshift64* */
    rng_s ^= rng_s >> 12; rng_s ^= rng_s << 25; rng_s ^= rng_s >> 27;
    return rng_s * 2685821657736338717ULL;
}
static int rndint(int m){ return (int)(rnd() % (unsigned)m); }

static int is_chord(int a,int b){ return ch[a][0]==b || ch[a][1]==b; }
static int hdist1(int a,int b){ int d=a-b; if(d<0)d=-d; return d==1 || d==n-1; }

static void build_adj(void){
    for(int v=0;v<n;v++){
        adj[v][0]=(v+1)%n; adj[v][1]=(v+n-1)%n; adj[v][2]=ch[v][0]; adj[v][3]=ch[v][1];
        nbr[v]=0;
        for(int k=0;k<4;k++) nbr[v] |= 1ULL<<adj[v][k];
    }
}

/* ---- HC counting: DFS from 0; counts each HC twice (both directions) ---- */
static long long cnt, cutoff;

static void dfs(int u, int depth, u64 unvis){
    if(cnt>=cutoff) return;
    if(depth==n){
        if(nbr[u] & 1ULL) cnt++;
        return;
    }
    u64 cand = nbr[u] & unvis;
    while(cand){
        int w = __builtin_ctzll(cand); cand &= cand-1;
        u64 unvis2 = unvis & ~(1ULL<<w);
        /* conservative prune: every remaining vertex must keep >=2 usable edges,
           crediting edges into {unvisited} U {new endpoint w} U {start 0} */
        u64 usable = unvis2 | (1ULL<<w) | 1ULL;
        u64 rem = unvis2; int ok=1;
        while(rem){
            int x = __builtin_ctzll(rem); rem &= rem-1;
            u64 e = nbr[x] & usable;
            if(__builtin_popcountll(e) < 2){ ok=0; break; }
        }
        if(ok) dfs(w, depth+1, unvis2);
        if(cnt>=cutoff) return;
    }
}

static long long count_hc(long long lim2){ /* lim2 = 2*cutoff on undirected count */
    build_adj();
    cutoff=lim2; cnt=0;
    u64 unvis = (n==64? ~0ULL : (1ULL<<n)-1ULL) & ~1ULL;
    dfs(0,1,unvis);
    return cnt/2;
}

/* (C4): does chord (a,b) participate in pattern (i,j)&(i+1,j+1)? */
static int c4_bad_edge(int a,int b){
    int a1=(a+1)%n, b1=(b+1)%n, a0=(a+n-1)%n, b0=(b+n-1)%n;
    return is_chord(a1,b1) || is_chord(a0,b0);
}

static int valid_new_chord(int a,int b){
    return a!=b && !hdist1(a,b) && !is_chord(a,b);
}

static void random_2factor(void){
    for(;;){
        int stubs[2*MAXN]; int m=2*n, ok=1;
        for(int v=0;v<n;v++){ stubs[2*v]=v; stubs[2*v+1]=v; ch[v][0]=ch[v][1]=-1; }
        while(m>0 && ok){
            int i=rndint(m); int a=stubs[i]; stubs[i]=stubs[m-1]; m--;
            int tries=0, done=0;
            while(tries<60 && m>0){
                int j=rndint(m); int b=stubs[j];
                if(b!=a && !hdist1(a,b) && !is_chord(a,b)){
                    stubs[j]=stubs[m-1]; m--;
                    if(ch[a][0]<0) ch[a][0]=b; else ch[a][1]=b;
                    if(ch[b][0]<0) ch[b][0]=a; else ch[b][1]=a;
                    done=1; break;
                }
                tries++;
            }
            if(!done) ok=0;
        }
        if(ok) return;
    }
}

static void print_state(long long e, const char*tag){
    printf("%s %lld n=%d chords:", tag, e, n);
    for(int v=0;v<n;v++) for(int k=0;k<2;k++) if(v<ch[v][k]) printf(" %d-%d", v, ch[v][k]);
    printf("\n"); fflush(stdout);
}

int main(int argc,char**argv){
    if(argc==2 && !strcmp(argv[1],"count")){
        /* count mode: stdin = "n k  a1 b1 a2 b2 ..." (k chords); prints exact #HC */
        long long lim; int k;
        if(scanf("%d %d %lld",&n,&k,&lim)!=3) return 1;
        for(int v=0;v<n;v++) ch[v][0]=ch[v][1]=-1;
        for(int i=0;i<k;i++){ int a,b; scanf("%d %d",&a,&b);
            if(ch[a][0]<0)ch[a][0]=b; else ch[a][1]=b;
            if(ch[b][0]<0)ch[b][0]=a; else ch[b][1]=a; }
        printf("%lld\n", count_hc(2*lim));
        return 0;
    }
    if(argc<5){ fprintf(stderr,"usage: %s n seed iters cutoff [restarts] [statefile] | %s count < spec\n",argv[0],argv[0]); return 1; }
    n=atoi(argv[1]); rng_s=strtoull(argv[2],0,10)*2862933555777941757ULL+3037000493ULL;
    long long iters=atoll(argv[3]); long long cut=atoll(argv[4]);
    int restarts=argc>5?atoi(argv[5]):1;
    int seeded=0; int seed_ch[MAXN][2];
    if(argc>6){ /* statefile: "k a1 b1 a2 b2 ..." chords on same n */
        FILE*f=fopen(argv[6],"r"); int k;
        if(!f||fscanf(f,"%d",&k)!=1){ fprintf(stderr,"bad statefile\n"); return 1; }
        for(int v=0;v<n;v++) seed_ch[v][0]=seed_ch[v][1]=-1;
        for(int i=0;i<k;i++){ int a,b; if(fscanf(f,"%d %d",&a,&b)!=2) return 1;
            if(seed_ch[a][0]<0)seed_ch[a][0]=b; else seed_ch[a][1]=b;
            if(seed_ch[b][0]<0)seed_ch[b][0]=a; else seed_ch[b][1]=a; }
        fclose(f); seeded=1;
    }
    long long global_best=1LL<<60;
    for(int r=0;r<restarts;r++){
        if(seeded && r==0) memcpy(ch,seed_ch,sizeof(ch));
        else if(seeded){ /* perturbed reseed from seed state */
            memcpy(ch,seed_ch,sizeof(ch));
        } else random_2factor();
        long long dyncut=cut;
        long long e=count_hc(2*dyncut);
        long long best=e;
        if(e<global_best){ global_best=e; print_state(e,"IMPROVE"); }
        double T=seeded?fmax(1.0,(double)e/40.0):fmax(2.0,(double)e/8.0);
        double cool=pow(0.05/T, 1.0/(double)iters);
        int sv_ch[MAXN][2];
        for(long long it=0; it<iters; it++){
            int a,ka,b,c,kc,d;
            a=rndint(n); ka=rndint(2); b=ch[a][ka];
            c=rndint(n); kc=rndint(2); d=ch[c][kc];
            if(a==c||a==d||b==c||b==d){ T*=cool; continue; }
            int mode=rndint(2);
            int na1,nb1,na2,nb2;
            if(mode==0){ na1=a; nb1=c; na2=b; nb2=d; }
            else       { na1=a; nb1=d; na2=b; nb2=c; }
            memcpy(sv_ch,ch,sizeof(ch));
            for(int k=0;k<2;k++){ if(ch[a][k]==b)ch[a][k]=-1; }
            for(int k=0;k<2;k++){ if(ch[b][k]==a){ch[b][k]=-1;break;} }
            for(int k=0;k<2;k++){ if(ch[c][k]==d){ch[c][k]=-1;break;} }
            for(int k=0;k<2;k++){ if(ch[d][k]==c){ch[d][k]=-1;break;} }
            if(!valid_new_chord(na1,nb1)||!valid_new_chord(na2,nb2)){
                memcpy(ch,sv_ch,sizeof(ch)); T*=cool; continue;
            }
            for(int k=0;k<2;k++) if(ch[na1][k]<0){ch[na1][k]=nb1;break;}
            for(int k=0;k<2;k++) if(ch[nb1][k]<0){ch[nb1][k]=na1;break;}
            /* careful: na2/nb2 may equal na1/nb1's partners; validity re-check */
            if(!valid_new_chord(na2,nb2)){ memcpy(ch,sv_ch,sizeof(ch)); T*=cool; continue; }
            for(int k=0;k<2;k++) if(ch[na2][k]<0){ch[na2][k]=nb2;break;}
            for(int k=0;k<2;k++) if(ch[nb2][k]<0){ch[nb2][k]=na2;break;}
            if(c4_bad_edge(na1,nb1)||c4_bad_edge(na2,nb2)){
                memcpy(ch,sv_ch,sizeof(ch)); T*=cool; continue;
            }
            long long e2=count_hc(2*dyncut);
            long long dE=e2-e;
            if(dE<=0 || (double)(rnd()>>11)/9007199254740992.0 < exp(-(double)dE/T)){
                e=e2;
                if(e<best){
                    best=e;
                    long long nc=4*best; if(nc<500) nc=500; if(nc<dyncut) dyncut=nc;
                    if(e<global_best){ global_best=e; print_state(e,"IMPROVE"); }
                    if(e==1){ print_state(e,"WITNESS"); return 42; }
                }
            } else memcpy(ch,sv_ch,sizeof(ch));
            T*=cool;
        }
        fprintf(stderr,"restart %d done best=%lld\n",r,best);
    }
    printf("BEST %lld n=%d\n", global_best, n);
    return 0;
}

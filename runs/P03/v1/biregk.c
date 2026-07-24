/* Generalization of bireg.c to arbitrary tau=K: sink-regular (K+1,K)-
 * biregular bipartite digraphs. p sources of out-degree K+1, q = p(K+1)/K
 * sinks of in-degree K, (K+1)p arcs. Smallest open case for tau=4 (ACZ P4
 * is tau=3-specific, so rho=3 i.e. p=12, q=15, 60 arcs is open).
 *
 * Dicut enumeration as in bireg.c: single-sink in-arc sets (=> tau <= K)
 * plus, for each nonempty proper source subset S, arcs from S to partially
 * covered sinks. Minimality filter, then K-coloring backtracking (each
 * minimal dicut must contain all K colors <=> K disjoint dijoins).
 *
 * Usage: ./biregk K p seconds seed
 *        ./biregk validate K p count seed
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAXK 6
#define MAXP 16
#define MAXQ 24
#define MAXARCS 128
#define MAXCUTS 200000

static int K, p, q;
static int sink[MAXQ][MAXK];
static uint32_t smask[MAXQ];

static uint64_t cutmask[MAXCUTS][2];
static int cutlen[MAXCUTS];
static int ncuts;

static uint64_t rng_s;
static uint64_t rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static int rndint(int n){ return (int)(rnd() % (uint64_t)n); }

static int cmp_cut(const void *a, const void *b){
    return cutlen[*(const int*)a] - cutlen[*(const int*)b];
}

static int order_buf[MAXCUTS];
static uint64_t min0[MAXCUTS], min1[MAXCUTS]; static int nmin;
static int enum_cuts(void){
    ncuts = 0;
    uint32_t full = (1u<<p) - 1, used = 0;
    for (int t = 0; t < q; t++) used |= smask[t];
    if (used != full) return -1;
    for (int t = 0; t < q; t++){
        uint64_t m0=0,m1=0;
        for (int pos=0; pos<K; pos++){ int a=K*t+pos; if(a<64) m0|=1ULL<<a; else m1|=1ULL<<(a-64); }
        cutmask[ncuts][0]=m0; cutmask[ncuts][1]=m1; cutlen[ncuts]=K; ncuts++;
    }
    for (uint32_t S = 1; S < full; S++){
        uint64_t m0=0,m1=0; int len=0;
        for (int t = 0; t < q; t++){
            uint32_t inter = smask[t] & S;
            if (inter && inter != smask[t]){
                for (int pos=0; pos<K; pos++){
                    if ((S >> sink[t][pos]) & 1){
                        int a=K*t+pos; if(a<64) m0|=1ULL<<a; else m1|=1ULL<<(a-64); len++;
                    }
                }
            }
        }
        if (len && len < K) return len;   /* tau < K: reject */
        if (len){
            if (ncuts >= MAXCUTS) return -1;
            cutmask[ncuts][0]=m0; cutmask[ncuts][1]=m1; cutlen[ncuts]=len; ncuts++;
        }
    }
    for (int i=0;i<ncuts;i++) order_buf[i]=i;
    qsort(order_buf, ncuts, sizeof(int), cmp_cut);
    nmin=0;
    for (int oi=0; oi<ncuts; oi++){
        int i=order_buf[oi]; int sub=0;
        for (int j=0;j<nmin;j++)
            if ((min0[j] & cutmask[i][0]) == min0[j] &&
                (min1[j] & cutmask[i][1]) == min1[j]){ sub=1; break; }
        if (!sub){ min0[nmin]=cutmask[i][0]; min1[nmin]=cutmask[i][1]; nmin++; }
    }
    return K;
}

static int color[MAXARCS];
static int cnt[MAXCUTS][MAXK];
static int rem_[MAXCUTS];
static int cuts_of[MAXARCS][96]; static int ncuts_of[MAXARCS];

static long dfs_nodes, dfs_limit;
static int dfs(int a, int m){
    if (a == m) return 1;
    if (++dfs_nodes > dfs_limit) return -1;
    for (int c = 0; c < K; c++){
        int ok = 1;
        for (int k = 0; k < ncuts_of[a] && ok; k++){
            int j = cuts_of[a][k], missing = 0;
            for (int cc = 0; cc < K; cc++)
                if (cnt[j][cc] + (cc==c) == 0) missing++;
            if (missing > rem_[j] - 1) ok = 0;
        }
        if (!ok) continue;
        color[a] = c;
        for (int k = 0; k < ncuts_of[a]; k++){ int j=cuts_of[a][k]; cnt[j][c]++; rem_[j]--; }
        int r = dfs(a+1, m);
        if (r) return r;
        for (int k = 0; k < ncuts_of[a]; k++){ int j=cuts_of[a][k]; cnt[j][c]--; rem_[j]++; }
    }
    return 0;
}

/* returns 1 = packs, 0 = proven no packing, -1 = node limit hit (HARD) */
static int packsK(void){
    int m = K*q;
    dfs_nodes = 0; dfs_limit = 20000000;
    for (int a = 0; a < m; a++) ncuts_of[a]=0;
    for (int j = 0; j < nmin; j++){
        rem_[j]=0;
        for (int c=0;c<K;c++) cnt[j][c]=0;
        for (int a = 0; a < m; a++){
            int bit = (a<64)? (int)((min0[j]>>a)&1) : (int)((min1[j]>>(a-64))&1);
            if (bit){
                if (ncuts_of[a] < 96) cuts_of[a][ncuts_of[a]++]=j;
                rem_[j]++;
            }
        }
    }
    return dfs(0, m);
}

static void rand_inst(void){
    int stubs[MAXARCS];
    for (;;){
        int n=0;
        for (int s=0;s<p;s++) for(int k=0;k<K+1;k++) stubs[n++]=s;
        for (int i=n-1;i>0;i--){ int j=rndint(i+1); int t=stubs[i]; stubs[i]=stubs[j]; stubs[j]=t; }
        int ok=1;
        for (int t=0;t<q && ok;t++){
            uint32_t m=0;
            for (int pos=0;pos<K;pos++){
                int s=stubs[K*t+pos];
                if ((m>>s)&1){ ok=0; break; }
                sink[t][pos]=s; m|=1u<<s;
            }
            smask[t]=m;
        }
        if (ok) return;
    }
}

static void print_inst(void){
    printf("K=%d p=%d sinks=[", K, p);
    for (int t=0;t<q;t++){
        printf("[");
        for (int pos=0;pos<K;pos++) printf("%d%s", sink[t][pos], pos==K-1?"":",");
        printf("]%s", t==q-1?"":",");
    }
    printf("]\n");
}

int main(int argc, char **argv){
    if (argc >= 2 && !strcmp(argv[1], "validate")){
        K = atoi(argv[2]); p = atoi(argv[3]); q = p*(K+1)/K;
        int count = atoi(argv[4]); rng_s = (uint64_t)atoll(argv[5]);
        for (int i=0;i<count;i++){
            rand_inst();
            if (enum_cuts() != K){ i--; continue; }
            int r = packsK();
            print_inst();
            printf("mincuts=%d packs=%d\n", nmin, r);
        }
        return 0;
    }
    K = atoi(argv[1]); p = atoi(argv[2]); q = p*(K+1)/K;
    double seconds = atof(argv[3]); rng_s = (uint64_t)atoll(argv[4]);
    time_t t0 = time(NULL);
    long n=0, okK=0;
    while (difftime(time(NULL), t0) < seconds){
        for (int burst=0; burst<200; burst++){
            rand_inst(); n++;
            if (enum_cuts() != K) continue;
            okK++;
            int r = packsK();
            if (r == 0){
                printf("UNSAT COUNTEREXAMPLE "); print_inst(); fflush(stdout);
                FILE *f = fopen("counterexample.txt","a");
                fprintf(f, "BIREGK K=%d p=%d ", K, p); fclose(f);
            } else if (r == -1){
                printf("HARD "); print_inst(); fflush(stdout);
                FILE *f = fopen("hardk.txt","a");
                fprintf(f, "HARD K=%d p=%d ", K, p);
                for (int t=0;t<q;t++){ for(int pos=0;pos<K;pos++) fprintf(f,"%d ",sink[t][pos]); }
                fprintf(f, "\n"); fclose(f);
            }
        }
        if (n % 200000 < 200)
            { printf("[biregk K=%d p=%d] n=%ld tauK=%ld t=%.0fs\n", K, p, n, okK, difftime(time(NULL),t0)); fflush(stdout); }
    }
    printf("[biregk K=%d p=%d] DONE n=%ld tauK=%ld\n", K, p, n, okK);
    return 0;
}

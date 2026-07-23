/* Fast checker for the smallest open case of Woodall's Conjecture:
 * (4,3)-biregular bipartite digraphs, p sources (out-deg 4), q = 4p/3 sinks
 * (in-deg 3), 3q arcs. tau=3 automatic upper bound via single-sink dicuts.
 *
 * Dicut enumeration: for every nonempty proper subset S of sources, the
 * minimal dicut candidate is arcs from S to sinks not fully covered by S,
 * plus the q single-sink triples. Minimality filtering, then a 3-coloring
 * backtracking check: every minimal dicut must contain all 3 colors
 * (equivalent to packing 3 disjoint dijoins). Prints any UNSAT instance.
 *
 * Usage: ./bireg p seconds seed   (requires 4p % 3 == 0)
 * Cross-validated against bipsearch.py (pysat) - see validate mode:
 *        ./bireg validate p count seed   (prints instance + result lines)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAXP 16
#define MAXQ 24
#define MAXARCS (3*MAXQ)
#define MAXCUTS 100000

static int p, q;
static int sink[MAXQ][3];         /* in-neighbours of each sink */
static uint32_t smask[MAXQ];      /* source bitmask per sink */

static uint64_t cutmask[MAXCUTS][2]; /* arc bitset, arcs = 3*t+pos */
static int cutlen[MAXCUTS];
static int ncuts;

static uint64_t rng_s;
static uint64_t rnd(void){ rng_s ^= rng_s<<13; rng_s ^= rng_s>>7; rng_s ^= rng_s<<17; return rng_s; }
static int rndint(int n){ return (int)(rnd() % (uint64_t)n); }

static int cmp_cut(const void *a, const void *b){
    int ia = *(const int*)a, ib = *(const int*)b;
    return cutlen[ia] - cutlen[ib];
}

/* enumerate minimal dicuts; return tau (min cut size), or -1 if degenerate */
static int order_buf[MAXCUTS];
static uint64_t min0[MAXCUTS], min1[MAXCUTS]; static int nmin, minlen0;
static int enum_cuts(void){
    ncuts = 0;
    uint32_t full = (p >= 32) ? 0xffffffffu : ((1u<<p) - 1);
    uint32_t used = 0;
    for (int t = 0; t < q; t++) used |= smask[t];
    if (used != full) return -1;          /* an unused source */
    /* single-sink dicuts */
    for (int t = 0; t < q; t++){
        uint64_t m0=0,m1=0;
        for (int pos=0; pos<3; pos++){ int a=3*t+pos; if(a<64) m0|=1ULL<<a; else m1|=1ULL<<(a-64); }
        cutmask[ncuts][0]=m0; cutmask[ncuts][1]=m1; cutlen[ncuts]=3; ncuts++;
    }
    for (uint32_t S = 1; S < full; S++){
        uint64_t m0=0,m1=0; int len=0;
        for (int t = 0; t < q; t++){
            uint32_t inter = smask[t] & S;
            if (inter && inter != smask[t]){
                for (int pos=0; pos<3; pos++){
                    if ((S >> sink[t][pos]) & 1){
                        int a=3*t+pos; if(a<64) m0|=1ULL<<a; else m1|=1ULL<<(a-64); len++;
                    }
                }
            }
        }
        if (len && len < 3) return len;   /* tau < 3: reject early */
        if (len){
            if (ncuts >= MAXCUTS) return -1;
            cutmask[ncuts][0]=m0; cutmask[ncuts][1]=m1; cutlen[ncuts]=len; ncuts++;
        }
    }
    /* minimality filter (sort by size, keep non-superset) */
    for (int i=0;i<ncuts;i++) order_buf[i]=i;
    qsort(order_buf, ncuts, sizeof(int), cmp_cut);
    nmin=0;
    for (int oi=0; oi<ncuts; oi++){
        int i=order_buf[oi]; int sub=0;
        for (int j=0;j<nmin;j++){
            if ((min0[j] & cutmask[i][0]) == min0[j] &&
                (min1[j] & cutmask[i][1]) == min1[j]){ sub=1; break; }
        }
        if (!sub){ min0[nmin]=cutmask[i][0]; min1[nmin]=cutmask[i][1]; nmin++; }
    }
    return 3;
}

/* 3-coloring backtracking: color arcs 0..3q-1 so each minimal cut has all
 * 3 colors. Watch counts per (cut,color). */
static int color[MAXARCS];
static int cnt[MAXCUTS][3];       /* arcs of each color in cut */
static int rem_[MAXCUTS];         /* uncolored arcs in cut */
static int cuts_of[MAXARCS][64]; static int ncuts_of[MAXARCS];

static int dfs(int a, int m){
    if (a == m) return 1;
    for (int c = 0; c < 3; c++){
        int ok = 1;
        for (int k = 0; k < ncuts_of[a] && ok; k++){
            int j = cuts_of[a][k];
            /* after coloring, remaining must still be able to cover missing colors */
            int missing = 0;
            for (int cc = 0; cc < 3; cc++)
                if (cnt[j][cc] + (cc==c) == 0) missing++;
            if (missing > rem_[j] - 1) ok = 0;
        }
        if (!ok) continue;
        color[a] = c;
        for (int k = 0; k < ncuts_of[a]; k++){ int j=cuts_of[a][k]; cnt[j][c]++; rem_[j]--; }
        if (dfs(a+1, m)) return 1;
        for (int k = 0; k < ncuts_of[a]; k++){ int j=cuts_of[a][k]; cnt[j][c]--; rem_[j]++; }
    }
    return 0;
}

static int packs3c(void){
    int m = 3*q;
    for (int a = 0; a < m; a++) ncuts_of[a]=0;
    for (int j = 0; j < nmin; j++){
        rem_[j]=0; cnt[j][0]=cnt[j][1]=cnt[j][2]=0;
        for (int a = 0; a < m; a++){
            int bit = (a<64)? (int)((min0[j]>>a)&1) : (int)((min1[j]>>(a-64))&1);
            if (bit){
                if (ncuts_of[a] < 64) cuts_of[a][ncuts_of[a]++]=j;
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
        for (int s=0;s<p;s++) for(int k=0;k<4;k++) stubs[n++]=s;
        for (int i=n-1;i>0;i--){ int j=rndint(i+1); int t=stubs[i]; stubs[i]=stubs[j]; stubs[j]=t; }
        int ok=1;
        for (int t=0;t<q && ok;t++){
            int a=stubs[3*t],b=stubs[3*t+1],c=stubs[3*t+2];
            if (a==b||a==c||b==c) ok=0;
            sink[t][0]=a; sink[t][1]=b; sink[t][2]=c;
            smask[t]=(1u<<a)|(1u<<b)|(1u<<c);
        }
        if (ok) return;
    }
}

static void print_inst(void){
    printf("p=%d sinks=[", p);
    for (int t=0;t<q;t++) printf("[%d,%d,%d]%s", sink[t][0],sink[t][1],sink[t][2], t==q-1?"":",");
    printf("]\n");
}

int main(int argc, char **argv){
    if (argc >= 2 && !strcmp(argv[1], "validate")){
        p = atoi(argv[2]); q = 4*p/3;
        int count = atoi(argv[3]); rng_s = (uint64_t)atoll(argv[4]);
        for (int i=0;i<count;i++){
            rand_inst();
            int tau = enum_cuts();
            if (tau != 3){ i--; continue; }
            int r = packs3c();
            print_inst();
            printf("mincuts=%d packs=%d\n", nmin, r);
        }
        return 0;
    }
    p = atoi(argv[1]); q = 4*p/3;
    double seconds = atof(argv[2]); rng_s = (uint64_t)atoll(argv[3]);
    time_t t0 = time(NULL);
    long n=0, ok3=0;
    while (difftime(time(NULL), t0) < seconds){
        for (int burst=0; burst<1000; burst++){
            rand_inst(); n++;
            int tau = enum_cuts();
            if (tau != 3) continue;
            ok3++;
            if (!packs3c()){
                printf("UNSAT COUNTEREXAMPLE "); print_inst(); fflush(stdout);
                FILE *f = fopen("counterexample.txt","a");
                fprintf(f, "BIREG-C p=%d ", p); fclose(f);
            }
        }
        if (n % 1000000 < 1000)
            { printf("[bireg-c p=%d] n=%ld tau3=%ld t=%.0fs\n", p, n, ok3, difftime(time(NULL),t0)); fflush(stdout); }
    }
    printf("[bireg-c p=%d] DONE n=%ld tau3=%ld\n", p, n, ok3);
    return 0;
}

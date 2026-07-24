/* Exhaustive C enumeration of ALL in-degree-3 bipartite instances:
 * multisets of q sink-triples chosen from the C(p,3) triples of p sources
 * (nondecreasing triple indices = canonical up to sink permutation).
 * For each instance covering all sources: enumerate minimal dicuts
 * (2^p bitmask sweep + single-sink triples), require tau=3, then check the
 * 3-dijoin partition with a watched-count backtracker (node-limited; hard
 * cases go to hardx.txt for independent SAT resolution).
 *
 * Usage: ./bipexhaust p q [MOD RES]   (shard on first triple index % MOD)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXP 8
#define MAXQ 14
#define MAXT 56
#define MAXARCS (3*MAXQ)
#define MAXCUTS 20000

static int p, q, T, MOD = 1, RES = 0;
static int tri[MAXT][3];
static uint32_t trimask[MAXT];
static int choice[MAXQ];

static int sink[MAXQ][3];
static uint32_t smask[MAXQ];

static uint64_t cutmask[MAXCUTS];
static int cutlen[MAXCUTS];
static int ncuts;
static int order_buf[MAXCUTS];
static uint64_t minm[MAXCUTS]; static int nmin;

static long n_total, n_tau3, n_hard;

static int cmp_cut(const void *a, const void *b){
    return cutlen[*(const int*)a] - cutlen[*(const int*)b];
}

static int enum_cuts(void){
    ncuts = 0;
    uint32_t full = (1u<<p) - 1, used = 0;
    for (int t = 0; t < q; t++) used |= smask[t];
    if (used != full) return -1;
    for (int t = 0; t < q; t++){
        uint64_t m=0;
        for (int pos=0; pos<3; pos++) m |= 1ULL<<(3*t+pos);
        cutmask[ncuts]=m; cutlen[ncuts]=3; ncuts++;
    }
    for (uint32_t S = 1; S < full; S++){
        uint64_t m=0; int len=0;
        for (int t = 0; t < q; t++){
            uint32_t inter = smask[t] & S;
            if (inter && inter != smask[t]){
                for (int pos=0; pos<3; pos++)
                    if ((S >> sink[t][pos]) & 1){ m |= 1ULL<<(3*t+pos); len++; }
            }
        }
        if (len && len < 3) return len;
        if (len){
            if (ncuts >= MAXCUTS) return -1;
            cutmask[ncuts]=m; cutlen[ncuts]=len; ncuts++;
        }
    }
    for (int i=0;i<ncuts;i++) order_buf[i]=i;
    qsort(order_buf, ncuts, sizeof(int), cmp_cut);
    nmin=0;
    for (int oi=0; oi<ncuts; oi++){
        int i=order_buf[oi]; int sub=0;
        for (int j=0;j<nmin;j++)
            if ((minm[j] & cutmask[i]) == minm[j]){ sub=1; break; }
        if (!sub) minm[nmin++]=cutmask[i];
    }
    return 3;
}

static int cnt[MAXCUTS][3], rem_[MAXCUTS];
static int cuts_of[MAXARCS][64]; static int ncuts_of[MAXARCS];
static long dfs_nodes;

static int dfs(int a, int m){
    if (a == m) return 1;
    if (++dfs_nodes > 20000000) return -1;
    for (int c = 0; c < 3; c++){
        int ok = 1;
        for (int k = 0; k < ncuts_of[a] && ok; k++){
            int j = cuts_of[a][k], missing = 0;
            for (int cc = 0; cc < 3; cc++)
                if (cnt[j][cc] + (cc==c) == 0) missing++;
            if (missing > rem_[j] - 1) ok = 0;
        }
        if (!ok) continue;
        for (int k = 0; k < ncuts_of[a]; k++){ int j=cuts_of[a][k]; cnt[j][c]++; rem_[j]--; }
        int r = dfs(a+1, m);
        if (r) return r;
        for (int k = 0; k < ncuts_of[a]; k++){ int j=cuts_of[a][k]; cnt[j][c]--; rem_[j]++; }
    }
    return 0;
}

static int packs3c(void){
    int m = 3*q;
    dfs_nodes = 0;
    for (int a = 0; a < m; a++) ncuts_of[a]=0;
    for (int j = 0; j < nmin; j++){
        rem_[j]=0; cnt[j][0]=cnt[j][1]=cnt[j][2]=0;
        for (int a = 0; a < m; a++)
            if ((minm[j]>>a)&1){
                if (ncuts_of[a] < 64) cuts_of[a][ncuts_of[a]++]=j;
                rem_[j]++;
            }
    }
    return dfs(0, m);
}

static void report(const char *tag, FILE *f){
    fprintf(f, "%s p=%d q=%d sinks=[", tag, p, q);
    for (int t=0;t<q;t++)
        fprintf(f, "[%d,%d,%d]%s", sink[t][0],sink[t][1],sink[t][2], t==q-1?"":",");
    fprintf(f, "]\n");
}

static void process(void){
    n_total++;
    if (enum_cuts() != 3) return;
    n_tau3++;
    int r = packs3c();
    if (r == 0){
        report("UNSAT COUNTEREXAMPLE", stdout); fflush(stdout);
        FILE *f = fopen("counterexample.txt","a");
        report("BIPEXHAUST", f); fclose(f);
    } else if (r == -1){
        n_hard++;
        FILE *f = fopen("hardx.txt","a");
        report("HARDX", f); fclose(f);
    }
    if (n_tau3 % 5000000 == 0){
        printf("[bipexhaust p=%d q=%d shard %d/%d] total=%ld tau3=%ld hard=%ld\n",
               p,q,RES,MOD,n_total,n_tau3,n_hard);
        fflush(stdout);
    }
}

static void rec(int slot, int start){
    if (slot == q){ process(); return; }
    /* prune: remaining slots must be able to cover missing sources */
    for (int i = start; i < T; i++){
        if (slot == 0 && (i % MOD) != RES) continue;
        choice[slot] = i;
        sink[slot][0]=tri[i][0]; sink[slot][1]=tri[i][1]; sink[slot][2]=tri[i][2];
        smask[slot]=trimask[i];
        rec(slot+1, i);
    }
}

int main(int argc, char **argv){
    p = atoi(argv[1]); q = atoi(argv[2]);
    if (argc >= 5){ MOD = atoi(argv[3]); RES = atoi(argv[4]); }
    T = 0;
    for (int a=0;a<p;a++) for(int b=a+1;b<p;b++) for(int c=b+1;c<p;c++){
        tri[T][0]=a; tri[T][1]=b; tri[T][2]=c;
        trimask[T]=(1u<<a)|(1u<<b)|(1u<<c); T++;
    }
    time_t t0=time(NULL);
    rec(0, 0);
    printf("[bipexhaust p=%d q=%d shard %d/%d] DONE total=%ld tau3=%ld hard=%ld t=%.0fs\n",
           p,q,RES,MOD,n_total,n_tau3,n_hard,difftime(time(NULL),t0));
    return 0;
}

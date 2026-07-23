// LNS for ternary covering codes n=6 R=1: start from a K-code, repeatedly remove r random
// codewords and exactly re-cover the holes with <= r words (DFS set cover, branch on the
// first uncovered word's 13 possible coverers). If ever re-covered with < r, K shrinks.
// Usage: ./lns seedfile seed max_rounds r
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define N 729
static int ball[N][13];
static uint64_t rng;
static inline uint64_t rnd(void){ rng ^= rng<<13; rng ^= rng>>7; rng ^= rng<<17; return rng; }

static void build_balls(void){
    for(int w=0; w<N; w++){
        int k=0; ball[w][k++]=w;
        int d[6], t=w;
        for(int i=0;i<6;i++){ d[i]=t%3; t/=3; }
        int p3=1;
        for(int i=0;i<6;i++){
            for(int v=1;v<=2;v++) ball[w][k++] = w + ((d[i]+v)%3 - d[i])*p3;
            p3*=3;
        }
    }
}

static int K;
static int code[200];
static int covcnt[N];
static int uncovered[N], nunc, uncpos[N];
static void unc_add(int w){ uncpos[w]=nunc; uncovered[nunc++]=w; }
static void unc_del(int w){ int p=uncpos[w]; int last=uncovered[--nunc]; uncovered[p]=last; uncpos[last]=p; }
static void add_word(int c){ for(int j=0;j<13;j++){ int w=ball[c][j]; if(covcnt[w]++==0) unc_del(w);} }
static void del_word(int c){ for(int j=0;j<13;j++){ int w=ball[c][j]; if(--covcnt[w]==0) unc_add(w);} }

static int sol[32], bestlen, bestsol[32];
static long long nodes, node_budget;
// DFS: cover current uncovered set with <= limit words
static int dfs(int depth, int limit){
    if(nunc==0){ bestlen=depth; memcpy(bestsol,sol,sizeof(int)*depth); return 1; }
    if(depth>=limit) return 0;
    if((nunc+12)/13 > limit-depth) return 0;
    if(++nodes > node_budget) return 0;
    int u=uncovered[0];
    // find uncovered word with fewest... just use first for speed
    for(int t=0;t<13;t++){
        int w=ball[u][t];
        sol[depth]=w;
        add_word(w);
        int ok=dfs(depth+1,limit);
        del_word(w);
        if(ok) return 1;
    }
    return 0;
}

static void print_code(const char*tag){
    printf("%s K=%d\n",tag,K);
    for(int i=0;i<K;i++){ int t=code[i]; for(int p=0;p<6;p++){ printf("%d",t%3); t/=3;} printf("\n"); }
    fflush(stdout);
}

int main(int argc,char**argv){
    build_balls();
    FILE*f=fopen(argv[1],"r"); char buf[64]; K=0;
    while(fgets(buf,64,f)){ if(strlen(buf)<6) continue; int w=0,p3=1; for(int p=0;p<6;p++){ w+=(buf[p]-'0')*p3; p3*=3;} code[K++]=w; }
    fclose(f);
    rng=strtoull(argv[2],0,10)*2654435761u+88172645463325252ull;
    long long rounds = atoll(argv[3]);
    int r = atoi(argv[4]);
    nunc=0; for(int w=0;w<N;w++){ covcnt[w]=0; unc_add(w); }
    for(int i=0;i<K;i++) add_word(code[i]);
    if(nunc){ printf("seed not a covering code (%d uncovered)\n",nunc); return 2; }
    printf("start K=%d r=%d\n",K,r); fflush(stdout);
    for(long long it=0; it<rounds; it++){
        if((it & 0xFFF)==0xFFF){ printf("round %lld K=%d\n",it,K); fflush(stdout); }
        // remove r random distinct codewords
        int idx[32], rem[32];
        for(int i=0;i<r;i++){
            int j; int again;
            do{ again=0; j=rnd()%K; for(int q=0;q<i;q++) if(idx[q]==j) again=1; }while(again);
            idx[i]=j;
        }
        for(int i=0;i<r;i++){ rem[i]=code[idx[i]]; del_word(rem[i]); }
        nodes=0; node_budget=2000000;
        int found = dfs(0, r-1);          // try strict improvement first
        if(!found){ nodes=0; found = dfs(0, r) && bestlen<=r; }
        if(found){
            // rebuild code array: remove idx entries, append bestsol
            int newcode[200], m=0;
            for(int i=0;i<K;i++){ int skip=0; for(int q=0;q<r;q++) if(idx[q]==i) skip=1; if(!skip) newcode[m++]=code[i]; }
            for(int q=0;q<bestlen;q++) newcode[m++]=bestsol[q];
            for(int q=0;q<bestlen;q++) add_word(bestsol[q]);
            memcpy(code,newcode,sizeof(int)*m);
            if(m<K){ K=m; print_code("IMPROVED"); if(K<=72) return 0; }
            else K=m;
        } else {
            for(int i=0;i<r;i++) add_word(rem[i]);
        }
    }
    printf("done K=%d\n",K);
    return 1;
}

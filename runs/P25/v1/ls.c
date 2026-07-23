// Local search (tabu/annealing hybrid) for ternary covering codes, n=6, R=1.
// State: K codewords (indices in 0..728). Cost = # uncovered words of 729.
// Move: pick an uncovered word u (or random word), pick a codeword c, move c into ball(u).
// Usage: ./ls K seed [max_iters]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define N 729
static int ball[N][13]; // each word: itself + 12 neighbors (6 pos * 2 alt digits)
static uint64_t rng;
static inline uint64_t rnd(void){ rng ^= rng<<13; rng ^= rng>>7; rng ^= rng<<17; return rng; }

static void build_balls(void){
    for(int w=0; w<N; w++){
        int k=0; ball[w][k++]=w;
        int d[6], t=w;
        for(int i=0;i<6;i++){ d[i]=t%3; t/=3; }
        int p3=1;
        for(int i=0;i<6;i++){
            for(int v=1;v<=2;v++){
                int nb = w + ((d[i]+v)%3 - d[i])*p3;
                ball[w][k++]=nb;
            }
            p3*=3;
        }
    }
}

int K;
static int code[200];          // codeword indices
static int covcnt[N];          // how many codewords cover word w
static int uncovered[N], nunc; // list of uncovered words
static int uncpos[N];

static void unc_add(int w){ uncpos[w]=nunc; uncovered[nunc++]=w; }
static void unc_del(int w){ int p=uncpos[w]; int last=uncovered[--nunc]; uncovered[p]=last; uncpos[last]=p; }

static void add_word(int c){ for(int j=0;j<13;j++){ int w=ball[c][j]; if(covcnt[w]++==0) unc_del(w);} }
static void del_word(int c){ for(int j=0;j<13;j++){ int w=ball[c][j]; if(--covcnt[w]==0) unc_add(w);} }

int main(int argc,char**argv){
    K=atoi(argv[1]); rng=strtoull(argv[2],0,10)*2654435761u+88172645463325252ull;
    long long maxit = argc>3? atoll(argv[3]) : 2000000000LL;
    build_balls();
    nunc=0; for(int w=0;w<N;w++){ covcnt[w]=0; unc_add(w); }
    if(argc>5){ // seed file: one ternary word per line; take first K (or random subset)
        FILE*f=fopen(argv[5],"r"); char buf[64]; int m=0; int seedw[200];
        while(m<200 && fgets(buf,64,f)){ int w=0,p3=1; for(int p=0;p<6;p++){ w+=(buf[p]-'0')*p3; p3*=3; } seedw[m++]=w; }
        fclose(f);
        // random subset of size K
        for(int i=0;i<m;i++){ int j=rnd()%(i+1); int t=seedw[i]; seedw[i]=seedw[j]; seedw[j]=t; }
        for(int i=0;i<K;i++){ code[i]=seedw[i%m]; add_word(code[i]); }
    } else
    for(int i=0;i<K;i++){ code[i]=rnd()%N; add_word(code[i]); }
    int best=nunc;
    long long it=0;
    // fixed-temperature Metropolis with focused moves
    double T = argc>4? atof(argv[4]) : 0.25;
    unsigned acc1 = (unsigned)(4294967296.0*__builtin_exp(-1.0/T));
    unsigned acc2 = (unsigned)(4294967296.0*__builtin_exp(-2.0/T));
    for(it=0; it<maxit && nunc>0; it++){
        if((it & 0x3FFFFFFFLL)==0x3FFFFFFFLL){ printf("progress it=%lld best=%d cur=%d\n",it,best,nunc); fflush(stdout); }
        // pick uncovered word target
        int u = uncovered[rnd()%nunc];
        int tgt = ball[u][rnd()%13];
        int ci = rnd()%K;
        int old = code[ci];
        if(old==tgt) continue;
        int before=nunc;
        del_word(old); add_word(tgt);
        int delta = nunc - before;
        unsigned r=(unsigned)rnd();
        if(delta<=0 || (delta==1 && r<acc1) || (delta==2 && r<acc2)){
            code[ci]=tgt;
            if(nunc<best){ best=nunc; printf("best=%d it=%lld\n",best,it); fflush(stdout);
                if(best==0){
                    printf("SOLVED K=%d seed=%s iters=%lld\n",K,argv[2],it);
                    for(int i=0;i<K;i++){ int t=code[i]; for(int p=0;p<6;p++){ printf("%d",t%3); t/=3;} printf("\n"); }
                    fflush(stdout);
                    return 0;
                }
            }
        } else {
            del_word(tgt); add_word(old);
        }
    }
    printf("FAILED K=%d seed=%s best=%d iters=%lld\n",K,argv[2],best,it);
    return 1;
}

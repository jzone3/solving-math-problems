// Weighted local search (breakout / dynamic weighting) for ternary covering codes n=6 R=1.
// Cost = sum of weights of uncovered words. On local minimum, bump weights of uncovered.
// Usage: ./ls2 K seed max_iters [wp]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

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

int K;
static int code[200];
static int covcnt[N];
static long long wt[N];        // dynamic weights
static int uncovered[N], nunc, uncpos[N];
static long long wcost;        // sum of weights of uncovered

static void unc_add(int w){ uncpos[w]=nunc; uncovered[nunc++]=w; wcost+=wt[w]; }
static void unc_del(int w){ int p=uncpos[w]; int last=uncovered[--nunc]; uncovered[p]=last; uncpos[last]=p; wcost-=wt[w]; }
static void add_word(int c){ for(int j=0;j<13;j++){ int w=ball[c][j]; if(covcnt[w]++==0) unc_del(w);} }
static void del_word(int c){ for(int j=0;j<13;j++){ int w=ball[c][j]; if(--covcnt[w]==0) unc_add(w);} }

int main(int argc,char**argv){
    K=atoi(argv[1]); rng=strtoull(argv[2],0,10)*2654435761u+88172645463325252ull;
    long long maxit = argc>3? atoll(argv[3]) : 2000000000LL;
    int wp = argc>4? atoi(argv[4]) : 100; // random-walk prob in 1/1000
    build_balls();
    for(int w=0;w<N;w++) wt[w]=1;
    nunc=0; wcost=0; for(int w=0;w<N;w++){ covcnt[w]=0; unc_add(w); }
    for(int i=0;i<K;i++){ code[i]=rnd()%N; add_word(code[i]); }
    int best=nunc;
    for(long long it=0; it<maxit && nunc>0; it++){
        if((it & 0x3FFFFFFFLL)==0x3FFFFFFFLL){ printf("progress it=%lld best=%d cur=%d wcost=%lld\n",it,best,nunc,wcost); fflush(stdout); }
        int u = uncovered[rnd()%nunc];
        if((rnd()%1000) < (unsigned)wp){
            // random walk: move random codeword into ball(u)
            int ci = rnd()%K; int tgt = ball[u][rnd()%13];
            del_word(code[ci]); add_word(tgt); code[ci]=tgt;
        } else {
            // greedy: best (tgt in ball(u), codeword ci) pair by weighted delta; sample subset of ci
            long long bestd = (1LL<<62); int bci=-1, btgt=-1;
            for(int j=0;j<13;j++){
                int tgt = ball[u][j];
                for(int tr=0; tr<8; tr++){
                    int ci = rnd()%K;
                    int old = code[ci]; if(old==tgt) continue;
                    long long before=wcost;
                    del_word(old); add_word(tgt);
                    long long d = wcost - before;
                    del_word(tgt); add_word(old);
                    if(d<bestd){ bestd=d; bci=ci; btgt=tgt; }
                }
            }
            if(bci>=0 && bestd<0){
                del_word(code[bci]); add_word(btgt); code[bci]=btgt;
            } else {
                // local minimum: bump weights of uncovered words
                for(int q=0;q<nunc;q++){ wt[uncovered[q]]++; wcost++; }
                if(bci>=0 && bestd<= (long long)(wt[u])){ del_word(code[bci]); add_word(btgt); code[bci]=btgt; }
            }
        }
        if(nunc>0 && nunc<=2 && (it & 0xFFF)==0){
            // exhaustive 2-exchange: remove pair (i,j), cover resulting uncovered with 2 words
            for(int i=0;i<K && nunc>0;i++) for(int j=i+1;j<K;j++){
                int ci=code[i], cj=code[j];
                del_word(ci); del_word(cj);
                // uncovered set now in uncovered[0..nunc-1]
                int U[40], m=nunc; if(m>40){ add_word(ci); add_word(cj); continue; }
                for(int q=0;q<m;q++) U[q]=uncovered[q];
                int done=0;
                for(int t1=0;t1<13 && !done;t1++){
                    int w1=ball[U[0]][t1];
                    add_word(w1);
                    if(nunc==0){ code[i]=w1; code[j]=w1; done=1; break; } // duplicate allowed? avoid: skip
                    int u1=uncovered[0];
                    for(int t2=0;t2<13;t2++){
                        int w2=ball[u1][t2];
                        add_word(w2);
                        if(nunc==0){ code[i]=w1; code[j]=w2; done=1; break; }
                        del_word(w2);
                    }
                    if(!done) del_word(w1);
                }
                if(done){
                    printf("SOLVED-2EX K=%d seed=%s iters=%lld\n",K,argv[2],it);
                    for(int q=0;q<K;q++){ int t=code[q]; for(int p=0;p<6;p++){ printf("%d",t%3); t/=3;} printf("\n"); }
                    fflush(stdout);
                    return 0;
                }
                add_word(ci); add_word(cj);
            }
        }
        if(nunc<best){ best=nunc; printf("best=%d it=%lld\n",best,it); fflush(stdout);
            if(best==0){
                printf("SOLVED K=%d seed=%s iters=%lld\n",K,argv[2],it);
                for(int i=0;i<K;i++){ int t=code[i]; for(int p=0;p<6;p++){ printf("%d",t%3); t/=3;} printf("\n"); }
                return 0;
            }
        }
    }
    printf("FAILED K=%d seed=%s best=%d\n",K,argv[2],best);
    return 1;
}

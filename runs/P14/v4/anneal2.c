/* P14 V4 annealing++ v2.
 *
 * Phase 1: in-row swaps (row composition invariant) until all column sums == K.
 * Phase 2: compound trades that preserve BOTH row compositions and column sums:
 *   pick row i1, cols j1,j2 with a=M[i1][j1] != b=M[i1][j2]; pick row i2 with
 *   M[i2][j1]-M[i2][j2] == b-a; swap the pair in both rows. Only pairwise
 *   inner products change. Energy = sum_{i<k} w[i][k] * (P_ik - Lam)^2 with
 *   breakout-style dynamic weights: when stuck in a local minimum, weights of
 *   violated pairs are incremented. Metropolis at low temperature.
 *
 * Usage: anneal2 V B rho1 rho2 K Lam seed iters [startfile]
 * Prints SOLVED + matrix on success (exit 0), else BEST line + matrix (exit 1).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int V, B, R1, R2, K, LAM;
static int M[32][64], best[32][64], cs[64], P[32][32];
static double W[32][32];
static unsigned long long rngs;

static unsigned long long xrand(void){rngs^=rngs>>12;rngs^=rngs<<25;rngs^=rngs>>27;return rngs*2685821657736338717ULL;}
static int rnd(int n){return (int)(xrand()%(unsigned)n);}
static double rndu(void){return (xrand()>>11)*(1.0/9007199254740992.0);}

static void recompute(void){
    memset(cs,0,sizeof cs); memset(P,0,sizeof P);
    for(int j=0;j<B;j++) for(int i=0;i<V;i++) cs[j]+=M[i][j];
    for(int i=0;i<V;i++) for(int k=i+1;k<V;k++){int s=0;for(int j=0;j<B;j++)s+=M[i][j]*M[k][j];P[i][k]=P[k][i]=s;}
}
static void random_start(void){
    for(int i=0;i<V;i++){
        int vals[64];
        for(int j=0;j<B;j++) vals[j]= j<R1?1:(j<R1+R2?2:0);
        for(int j=B-1;j>0;j--){int t=rnd(j+1);int tmp=vals[j];vals[j]=vals[t];vals[t]=tmp;}
        for(int j=0;j<B;j++) M[i][j]=vals[j];
    }
    recompute();
}
static long long pair_raw(void){
    long long e=0;
    for(int i=0;i<V;i++)for(int k=i+1;k<V;k++){long long d=P[i][k]-LAM;e+=d*d;}
    return e;
}
static double pair_wsum(void){
    double e=0;
    for(int i=0;i<V;i++)for(int k=i+1;k<V;k++){long long d=P[i][k]-LAM;e+=W[i][k]*d*d;}
    return e;
}
/* fix column sums via in-row swaps, greedy + noise */
static int phase1(long long budget){
    long long Ec=0; for(int j=0;j<B;j++){long long d=cs[j]-K;Ec+=d*d;}
    double T=1.0;
    for(long long it=0;it<budget && Ec>0;it++){
        int i=rnd(V),j1=rnd(B),j2=rnd(B);
        int a=M[i][j1],b=M[i][j2]; if(a==b)continue;
        int d=b-a;
        long long c1=cs[j1]-K,c2=cs[j2]-K;
        long long dE=((c1+d)*(c1+d)-c1*c1)+((c2-d)*(c2-d)-c2*c2);
        if(dE<=0||rndu()<exp(-dE/T)){
            M[i][j1]=b;M[i][j2]=a;cs[j1]+=d;cs[j2]-=d;Ec+=dE;
            for(int k=0;k<V;k++){ if(k==i)continue; int dk=d*(M[k][j1]-M[k][j2]); if(dk){P[i][k]+=dk;P[k][i]+=dk;} }
        }
        T*=0.999999; if(T<0.02)T=0.02;
    }
    return Ec==0;
}

int main(int argc,char**argv){
    if(argc<9){fprintf(stderr,"usage: %s V B rho1 rho2 K Lam seed iters [startfile]\n",argv[0]);return 2;}
    V=atoi(argv[1]);B=atoi(argv[2]);R1=atoi(argv[3]);R2=atoi(argv[4]);K=atoi(argv[5]);LAM=atoi(argv[6]);
    rngs=strtoull(argv[7],0,10)*6364136223846793005ULL+1442695040888963407ULL; if(!rngs)rngs=88172645463325252ULL;
    long long iters=atoll(argv[8]);

    if(argc>9){
        FILE*f=fopen(argv[9],"r"); if(!f){perror("startfile");return 2;}
        for(int i=0;i<V;i++)for(int j=0;j<B;j++){int c=fgetc(f);while(c=='\n'||c==' '||c=='\r')c=fgetc(f);M[i][j]=c-'0';}
        fclose(f); recompute();
    } else random_start();

    long long bestraw=1LL<<60;
    long long it=0;
    while(it<iters){
        if(argc<=9 && it>0) random_start();
        if(!phase1(50000000)){ it+=50000000; continue; }
        for(int i=0;i<V;i++)for(int k=0;k<V;k++)W[i][k]=1.0;
        double T=0.35;
        long long since=0;
        long long inner=0, inner_budget= (iters-it<400000000LL)?(iters-it):400000000LL;
        long long raw=pair_raw();
        for(; inner<inner_budget; inner++){
            int i1=rnd(V), j1=rnd(B), j2=rnd(B);
            int a=M[i1][j1], b=M[i1][j2];
            if(a==b) continue;
            int d=b-a;
            /* find compatible i2 */
            int cand[32],nc=0;
            for(int i2=0;i2<V;i2++){ if(i2==i1)continue; if(M[i2][j1]-M[i2][j2]==d) cand[nc++]=i2; }
            if(!nc) continue;
            int i2=cand[rnd(nc)];
            /* apply move tentatively via delta on P:
               row i1: j1 a->b, j2 b->a ; row i2: j1 b2->a2, j2 a2->b2 where b2-a2 = d, i.e.
               row i2 swaps too: M[i2][j1] (=x) <-> M[i2][j2] (=x-d). */
            int x=M[i2][j1], y=M[i2][j2]; /* x - y == d */
            double dE=0; long long draw=0;
            for(int k=0;k<V;k++){
                if(k==i1||k==i2) continue;
                int dk1=d*(M[k][j1]-M[k][j2]);       /* change of P[i1][k] */
                if(dk1){ long long p=P[i1][k]-LAM; long long nd=(p+dk1)*(p+dk1)-p*p; dE+=W[i1][k]*nd; draw+=nd; }
                int dk2=-d*(M[k][j1]-M[k][j2]);      /* change of P[i2][k] */
                if(dk2){ long long p=P[i2][k]-LAM; long long nd=(p+dk2)*(p+dk2)-p*p; dE+=W[i2][k]*nd; draw+=nd; }
            }
            /* P[i1][i2] change: new a*x' etc. old contribution a*x + b*y ; new b*y + a*x? careful:
               after move: M[i1][j1]=b, M[i1][j2]=a, M[i2][j1]=y, M[i2][j2]=x.
               old P contribution from cols j1,j2: a*x + b*y ; new: b*y + a*x  -> unchanged!  */
            if(dE<=0||rndu()<exp(-dE/T)){
                M[i1][j1]=b;M[i1][j2]=a; M[i2][j1]=y;M[i2][j2]=x;
                for(int k=0;k<V;k++){
                    if(k==i1||k==i2)continue;
                    int dk1=d*(M[k][j1]-M[k][j2]); /* NOTE: M[k][*] unchanged */
                    /* recompute using original values: they are same since rows k untouched */
                    dk1=d*(M[k][j1]-M[k][j2]);
                    if(dk1){P[i1][k]+=dk1;P[k][i1]+=dk1;}
                    int dk2=-dk1;
                    if(dk2){P[i2][k]+=dk2;P[k][i2]+=dk2;}
                }
                raw+=draw;
                if(raw==0){
                    printf("SOLVED\n");
                    for(int r=0;r<V;r++){for(int c=0;c<B;c++)putchar('0'+M[r][c]);putchar('\n');}
                    return 0;
                }
                if(raw<bestraw){bestraw=raw;memcpy(best,M,sizeof M);since=0;}
            }
            since++;
            if(since>200000){ /* stuck: bump weights of violated pairs, mild reheat */
                for(int i=0;i<V;i++)for(int k=i+1;k<V;k++) if(P[i][k]!=LAM){W[i][k]+=1.0;W[k][i]+=1.0;}
                T=0.6; since=0;
            }
            T*=0.9999995; if(T<0.08)T=0.08;
        }
        it+=inner+1;
        if(argc>9) break; /* startfile mode: single pass */
    }
    memcpy(M,best,sizeof M); recompute();
    printf("BEST pair_sq=%lld\n",bestraw);
    for(int r=0;r<V;r++){for(int c=0;c<B;c++)putchar('0'+M[r][c]);putchar('\n');}
    return 1;
}

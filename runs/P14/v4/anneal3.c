/* P14 V4 annealing++ v3: breakout dynamic-weight local search.
 *
 * State: V x B matrix over {0,1,2}; each row permanently holds rho1 ones and
 * rho2 twos (moves = swap two entries within one row).
 * Violations: column sums (|cs_j - K|) and pair inner products (|P_ik - Lam|).
 * Weighted energy E = sum_j wcol_j*|cs_j-K| + sum_{i<k} wpair_ik*|P_ik-Lam|.
 * Search: sample random moves; accept improving; accept sideways with prob;
 * at local minima (many samples, no improvement) bump weights of currently
 * violated constraints (+1)  [Morris' breakout], occasionally reset weights.
 *
 * Usage: anneal3 V B rho1 rho2 K Lam seed seconds [startfile]
 * SOLVED + matrix on success (exit 0); else BEST + matrix (exit 1).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int V,B,R1,R2,K,LAM;
static int M[32][64],best[32][64],cs[64],P[32][32];
static int WC[64],WP[32][32];
static unsigned long long rngs;
static unsigned long long xrand(void){rngs^=rngs>>12;rngs^=rngs<<25;rngs^=rngs>>27;return rngs*2685821657736338717ULL;}
static int rnd(int n){return (int)(xrand()%(unsigned)n);}
static double rndu(void){return (xrand()>>11)*(1.0/9007199254740992.0);}
static int iabs(int x){return x<0?-x:x;}

static void recompute(void){
    memset(cs,0,sizeof cs);memset(P,0,sizeof P);
    for(int j=0;j<B;j++)for(int i=0;i<V;i++)cs[j]+=M[i][j];
    for(int i=0;i<V;i++)for(int k=i+1;k<V;k++){int s=0;for(int j=0;j<B;j++)s+=M[i][j]*M[k][j];P[i][k]=P[k][i]=s;}
}
static void random_start(void){
    for(int i=0;i<V;i++){
        int vals[64];
        for(int j=0;j<B;j++)vals[j]= j<R1?1:(j<R1+R2?2:0);
        for(int j=B-1;j>0;j--){int t=rnd(j+1);int tmp=vals[j];vals[j]=vals[t];vals[t]=tmp;}
        for(int j=0;j<B;j++)M[i][j]=vals[j];
    }
    recompute();
}
static long long raw_viol(void){
    long long e=0;
    for(int j=0;j<B;j++)e+=iabs(cs[j]-K);
    for(int i=0;i<V;i++)for(int k=i+1;k<V;k++)e+=iabs(P[i][k]-LAM);
    return e;
}

int main(int argc,char**argv){
    if(argc<9){fprintf(stderr,"usage: %s V B r1 r2 K Lam seed seconds [startfile]\n",argv[0]);return 2;}
    V=atoi(argv[1]);B=atoi(argv[2]);R1=atoi(argv[3]);R2=atoi(argv[4]);K=atoi(argv[5]);LAM=atoi(argv[6]);
    rngs=strtoull(argv[7],0,10)*6364136223846793005ULL+1442695040888963407ULL; if(!rngs)rngs=88172645463325252ULL;
    double seconds=atof(argv[8]);
    setvbuf(stdout,0,_IONBF,0);
    struct timespec t0,tn; clock_gettime(CLOCK_MONOTONIC,&t0);

    long long bestraw=1LL<<60;
    unsigned long long tries=0;
    int restart=1;
    if(argc>9){
        FILE*f=fopen(argv[9],"r"); if(!f){perror("startfile");return 2;}
        for(int i=0;i<V;i++)for(int j=0;j<B;j++){int c=fgetc(f);while(c=='\n'||c==' '||c=='\r')c=fgetc(f);M[i][j]=c-'0';}
        fclose(f);recompute();restart=0;
    }
    while(1){
        if(restart) random_start();
        restart=1;
        for(int j=0;j<B;j++)WC[j]=1;
        for(int i=0;i<V;i++)for(int k=0;k<V;k++)WP[i][k]=1;
        long long noimp=0, weight_bumps=0;
        long long raw=raw_viol();
        if(raw<bestraw){bestraw=raw;memcpy(best,M,sizeof M);}
        while(weight_bumps<4000){
            /* time check */
            if(!(tries&0xFFFFF)){
                clock_gettime(CLOCK_MONOTONIC,&tn);
                if(tn.tv_sec-t0.tv_sec+(tn.tv_nsec-t0.tv_nsec)*1e-9>seconds){
                    memcpy(M,best,sizeof M);recompute();
                    printf("BEST viol_l1=%lld\n",bestraw);
                    for(int r=0;r<V;r++){for(int c=0;c<B;c++)putchar('0'+M[r][c]);putchar('\n');}
                    return 1;
                }
            }
            tries++;
            int i=rnd(V),j1=rnd(B),j2=rnd(B);
            int a=M[i][j1],b=M[i][j2];
            if(a==b){continue;}
            int d=b-a;
            long long dE=0,draw=0;
            {   int c1=cs[j1]-K,c2=cs[j2]-K;
                dE+=WC[j1]*(long long)(iabs(c1+d)-iabs(c1));
                dE+=WC[j2]*(long long)(iabs(c2-d)-iabs(c2));
                draw+=iabs(c1+d)-iabs(c1)+iabs(c2-d)-iabs(c2);
            }
            for(int k=0;k<V;k++){
                if(k==i)continue;
                int dk=d*(M[k][j1]-M[k][j2]);
                if(!dk)continue;
                int p=P[i][k]-LAM;
                dE+=WP[i][k]*(long long)(iabs(p+dk)-iabs(p));
                draw+=iabs(p+dk)-iabs(p);
            }
            int accept=0;
            if(dE<0)accept=1;
            else if(dE==0)accept=(rndu()<0.5);
            if(accept){
                M[i][j1]=b;M[i][j2]=a;cs[j1]+=d;cs[j2]-=d;
                for(int k=0;k<V;k++){
                    if(k==i)continue;
                    int dk=d*(M[k][j1]-M[k][j2]);
                    if(dk){P[i][k]+=dk;P[k][i]+=dk;}
                }
                raw+=draw;
                if(raw==0){
                    printf("SOLVED\n");
                    for(int r=0;r<V;r++){for(int c=0;c<B;c++)putchar('0'+M[r][c]);putchar('\n');}
                    return 0;
                }
                if(raw<bestraw){bestraw=raw;memcpy(best,M,sizeof M);}
                if(dE<0)noimp=0;
            }
            noimp++;
            if(noimp> (long long)V*B*4){
                /* local minimum: breakout — bump weights of violated constraints */
                for(int j=0;j<B;j++) if(cs[j]!=K) WC[j]++;
                for(int x=0;x<V;x++)for(int k=x+1;k<V;k++) if(P[x][k]!=LAM){WP[x][k]++;WP[k][x]++;}
                weight_bumps++;
                noimp=0;
            }
        }
    }
}

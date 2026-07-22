/* P12 V5: simulated-annealing witness hunt for T2(n), n = 11 or 13.
 * Cost = sum over ordered pairs of max(0, count_dist1-1) + max(0, count_dist2-1).
 * (dist-1 exactly-once is equivalent to no-duplicates by counting: n(n-1) slots.)
 * Moves: swap two positions in a random row; reverse a random segment of a row.
 * Restarts with geometric cooling; prints best cost ever and any cost-0 witness.
 * Build: gcc -O3 -march=native -o anneal anneal.c -lm
 * Run: ./anneal n seconds [seed]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int N;
static int row[16][16];
static int c1[16][16], c2[16][16]; /* pair counts at distance 1, 2 */

static unsigned long long rng;
static inline unsigned long long xr(void){ rng^=rng<<13; rng^=rng>>7; rng^=rng<<17; return rng; }
static inline int ri(int m){ return (int)(xr() % (unsigned)m); }

static int cost_all(void){
    memset(c1,0,sizeof c1); memset(c2,0,sizeof c2);
    for(int i=0;i<N;i++){
        for(int j=0;j+1<N;j++) c1[row[i][j]][row[i][j+1]]++;
        for(int j=0;j+2<N;j++) c2[row[i][j]][row[i][j+2]]++;
    }
    int c=0;
    for(int a=0;a<N;a++)for(int b=0;b<N;b++){
        if(c1[a][b]>1)c+=c1[a][b]-1;
        if(c2[a][b]>1)c+=c2[a][b]-1;
    }
    return c;
}
/* remove/add contributions of row i around positions: recompute row i fully (cheap, N<=13) */
static int rowdelta(int i,int sign){
    int d=0;
    for(int j=0;j+1<N;j++){
        int a=row[i][j],b=row[i][j+1];
        if(sign>0){ if(c1[a][b]>=1)d++; c1[a][b]++; } else { c1[a][b]--; if(c1[a][b]>=1)d--; }
    }
    for(int j=0;j+2<N;j++){
        int a=row[i][j],b=row[i][j+2];
        if(sign>0){ if(c2[a][b]>=1)d++; c2[a][b]++; } else { c2[a][b]--; if(c2[a][b]>=1)d--; }
    }
    return d;
}

int main(int argc,char**argv){
    if(argc<3){fprintf(stderr,"usage: %s n seconds [seed]\n",argv[0]);return 1;}
    N=atoi(argv[1]);
    double budget=atof(argv[2]);
    rng=(argc>3)?strtoull(argv[3],0,10):((unsigned long long)time(0)*2654435761ULL+9);
    if(!rng)rng=88172645463325252ULL;
    double t0=(double)clock()/CLOCKS_PER_SEC;
    int bestever=1<<30;
    long long iters=0;
    while((double)clock()/CLOCKS_PER_SEC - t0 < budget){
        /* random init */
        for(int i=0;i<N;i++){ for(int j=0;j<N;j++)row[i][j]=j;
            for(int j=N-1;j>0;j--){int k=ri(j+1),t=row[i][j];row[i][j]=row[i][k];row[i][k]=t;} }
        int cost=cost_all();
        double T=3.0;
        for(long long it=0; it<2000000 && cost>0; it++,iters++){
            T*=0.999999; if(T<0.05)T=0.05;
            int i=ri(N);
            int d0=rowdelta(i,-1); /* removes row i; d0 = -gain */
            int save[16]; memcpy(save,row[i],sizeof save);
            if(xr()&1){ int a=ri(N),b=ri(N); int t=row[i][a];row[i][a]=row[i][b];row[i][b]=t; }
            else { int a=ri(N),b=ri(N); if(a>b){int t=a;a=b;b=t;}
                   while(a<b){int t=row[i][a];row[i][a]=row[i][b];row[i][b]=t;a++;b--;} }
            int d1=rowdelta(i,+1);
            int nd=cost+d0+d1;
            if(nd<=cost || exp((cost-nd)/T) * 4294967296.0 > (double)(xr()&0xffffffffULL)){
                cost=nd;
            } else { /* revert */
                rowdelta(i,-1); memcpy(row[i],save,sizeof save); rowdelta(i,+1);
            }
            if(cost<bestever){
                bestever=cost;
                fprintf(stderr,"best=%d iters=%lld t=%.0fs\n",bestever,iters,
                        (double)clock()/CLOCKS_PER_SEC-t0);
                if(cost==0){
                    printf("SOLUTION n=%d\n",N);
                    for(int r2=0;r2<N;r2++){for(int j=0;j<N;j++)printf("%d ",row[r2][j]);printf("\n");}
                    fflush(stdout); return 0;
                }
            }
            if((double)clock()/CLOCKS_PER_SEC - t0 >= budget) break;
        }
    }
    printf("NOSOLUTION n=%d bestever=%d iters=%lld\n",N,bestever,iters);
    return 0;
}

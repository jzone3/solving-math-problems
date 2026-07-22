/* V4: iterated local search / polish for CW(n,k) ternary sequences.
 *
 * Steepest 2-position-swap descent to a local minimum of
 * E = sum_{t=1}^{n-1} R(t)^2, then random perturbation kicks (ILS).
 * Can start from a given vector (polish mode) or random restarts.
 *
 * Usage: ./ils n s seed max_seconds [start_vec] [report_thresh]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int n, s, k, np, nm;
static int *a, *R;
static long long E;

static unsigned long long rng_state;
static inline unsigned long long rng(void){
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}
static inline int rngi(int m){ return (int)(rng() % (unsigned)m); }

static void recompute(void){
    E=0;
    for(int t=0;t<n;t++){
        int r=0;
        for(int i=0;i<n;i++) r += a[i]*a[(i+t)%n];
        R[t]=r;
        if(t) E += (long long)r*r;
    }
}
static inline void setval(int i, int v){
    int d = v - a[i];
    if(!d) return;
    for(int t=1;t<n;t++){
        int x=R[t];
        E -= (long long)x*x;
        x += d*(a[(i+t)%n] + a[(i-t+n)%n]);
        R[t]=x;
        E += (long long)x*x;
    }
    a[i]=v;
}
static void randinit(void){
    memset(a,0,n*sizeof(int));
    int *perm=malloc(n*sizeof(int));
    for(int i=0;i<n;i++) perm[i]=i;
    for(int i=n-1;i>0;i--){ int j=rngi(i+1); int t=perm[i]; perm[i]=perm[j]; perm[j]=t; }
    for(int i=0;i<np;i++) a[perm[i]]=1;
    for(int i=0;i<nm;i++) a[perm[np+i]]=-1;
    free(perm);
    recompute();
}

/* steepest-descent over all swaps until local min; returns E */
static long long descend(void){
    int improved=1;
    while(improved){
        improved=0;
        long long bestdE=0; int bi=-1,bj=-1;
        for(int i=0;i<n;i++) for(int j=i+1;j<n;j++){
            if(a[i]==a[j]) continue;
            int vi=a[i],vj=a[j];
            long long E0=E;
            setval(i,vj); setval(j,vi);
            long long dE=E-E0;
            setval(j,vj); setval(i,vi);
            if(dE<bestdE){ bestdE=dE; bi=i; bj=j; }
        }
        if(bi>=0){
            int vi=a[bi],vj=a[bj];
            setval(bi,vj); setval(bj,vi);
            improved=1;
        }
    }
    return E;
}

int main(int argc, char**argv){
    if(argc<4){ fprintf(stderr,"usage: %s n s seed max_seconds [start_vec] [report]\n",argv[0]); return 1; }
    n=atoi(argv[1]); s=atoi(argv[2]); k=s*s; np=(k+s)/2; nm=(k-s)/2;
    rng_state = strtoull(argv[3],0,10) ^ 0x9e3779b97f4a7c15ULL;
    for(int i=0;i<10;i++) rng();
    double max_sec = argc>4 ? atof(argv[4]) : 3600.0;
    const char *start = (argc>5 && strchr(argv[5],'+')) ? argv[5] : 0;
    long long report_thresh = (argc>6) ? atoll(argv[6]) : ((argc>5 && !start) ? atoll(argv[5]) : 40);
    a=malloc(n*sizeof(int)); R=malloc(n*sizeof(int));

    if(start){
        for(int i=0;i<n;i++) a[i] = start[i]=='+'?1:(start[i]=='-'?-1:0);
        recompute();
    } else randinit();

    time_t t0=time(0);
    long long bestE=-1; int *best=malloc(n*sizeof(int));
    long long kicks=0;
    while(difftime(time(0),t0)<max_sec){
        long long e = descend();
        if(bestE<0 || e<bestE){
            bestE=e; memcpy(best,a,n*sizeof(int));
            if(bestE<=report_thresh){
                printf("BEST n=%d s=%d E=%lld kicks=%lld t=%.0fs vec=",n,s,bestE,kicks,difftime(time(0),t0));
                for(int x=0;x<n;x++) putchar(best[x]==0?'0':(best[x]>0?'+':'-'));
                putchar('\n'); fflush(stdout);
            }
            if(bestE==0){
                printf("SOLUTION n=%d k=%d vec=",n,k);
                for(int x=0;x<n;x++) putchar(best[x]==0?'0':(best[x]>0?'+':'-'));
                putchar('\n'); fflush(stdout);
                return 0;
            }
        }
        /* kick: restart from best, random 3-6 swaps */
        memcpy(a,best,n*sizeof(int)); recompute();
        int nk = 3 + rngi(4);
        for(int q=0;q<nk;q++){
            int i=rngi(n), j=rngi(n);
            if(a[i]!=a[j]){ int vi=a[i],vj=a[j]; setval(i,vj); setval(j,vi); }
        }
        kicks++;
        if(kicks % 400 == 0){ randinit(); }  /* occasional full restart */
    }
    printf("DONE n=%d s=%d bestE=%lld kicks=%lld vec=",n,s,bestE,kicks);
    for(int x=0;x<n;x++) putchar(best[x]==0?'0':(best[x]>0?'+':'-'));
    putchar('\n');
    return 2;
}

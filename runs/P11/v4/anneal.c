/* V4: simulated annealing on ternary sequences for circulant weighing matrices.
 *
 * Search for a in {-1,0,+1}^n, weight k=s*s, with all nontrivial periodic
 * autocorrelations R(t) = sum_i a_i a_{i+t mod n} equal to zero.
 * DFT view: power spectrum |A(j)|^2 must be flat = k; j=0 forces
 * n_plus - n_minus = +-s, so we fix counts n_plus=(s^2+s)/2, n_minus=(s^2-s)/2
 * (negation symmetry makes the other sign redundant).
 *
 * Energy E = sum_{t=1}^{n-1} R(t)^2.  Moves: swap values of two positions
 * holding the composition fixed (nonzero<->zero, +1<->-1).
 * Incremental O(n) energy updates; geometric cooling with reheats/restarts.
 *
 * Usage: ./anneal n s seed max_seconds [report_thresh]
 * Prints BEST lines as records improve; prints SOLUTION and the vector if E=0.
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
static inline double rngd(void){ return (rng() >> 11) * (1.0/9007199254740992.0); }
static inline int rngi(int m){ return (int)(rng() % (unsigned)m); }

static void recompute(void){
    E = 0;
    for(int t=0;t<n;t++){
        int r=0;
        for(int i=0;i<n;i++) r += a[i]*a[(i+t)%n];
        R[t]=r;
        if(t) E += (long long)r*r;
    }
}

/* set a[i]=v, update R and E incrementally */
static void setval(int i, int v){
    int d = v - a[i];
    if(!d) return;
    for(int t=1;t<n;t++){
        int r = R[t];
        E -= (long long)r*r;
        r += d*(a[(i+t)%n] + a[(i-t+n)%n]);
        R[t]=r;
        E += (long long)r*r;
    }
    R[0] += d*(2*a[i]+d);
    a[i]=v;
}

static void randinit(void){
    memset(a,0,n*sizeof(int));
    /* place np +1s and nm -1s at random distinct positions */
    int *perm = malloc(n*sizeof(int));
    for(int i=0;i<n;i++) perm[i]=i;
    for(int i=n-1;i>0;i--){ int j=rngi(i+1); int t=perm[i]; perm[i]=perm[j]; perm[j]=t; }
    for(int i=0;i<np;i++) a[perm[i]]=1;
    for(int i=0;i<nm;i++) a[perm[np+i]]=-1;
    free(perm);
    recompute();
}

int main(int argc, char**argv){
    if(argc<4){ fprintf(stderr,"usage: %s n s seed max_seconds [report_thresh]\n",argv[0]); return 1; }
    n = atoi(argv[1]); s = atoi(argv[2]);
    rng_state = strtoull(argv[3],0,10) ^ 0x9e3779b97f4a7c15ULL;
    for(int i=0;i<10;i++) rng();
    double max_sec = argc>4 ? atof(argv[4]) : 3600.0;
    long long report_thresh = argc>5 ? atoll(argv[5]) : 16;
    k = s*s; np=(k+s)/2; nm=(k-s)/2;
    a = malloc(n*sizeof(int)); R = malloc(n*sizeof(int));

    time_t t0 = time(0);
    long long bestE = -1;
    int *best = malloc(n*sizeof(int));
    long long moves=0, restarts=0;

    while(difftime(time(0),t0) < max_sec){
        randinit();
        restarts++;
        double T = 6.0;
        double cool = 0.99997;
        long long stall = 0;
        long long localbest = E;
        while(T > 0.05 && difftime(time(0),t0) < max_sec){
            /* pick two positions with different values */
            int i = rngi(n), j = rngi(n);
            if(a[i]==a[j]){ T*=cool; continue; }
            int vi=a[i], vj=a[j];
            long long Eold = E;
            setval(i,vj); setval(j,vi);
            long long dE = E - Eold;
            moves++;
            if(dE > 0 && rngd() >= exp(-(double)dE/T)){
                setval(j,vj); setval(i,vi);   /* revert */
            }
            if(E < localbest){ localbest = E; stall = 0; } else stall++;
            if(bestE<0 || E < bestE){
                bestE = E; memcpy(best,a,n*sizeof(int));
                if(bestE <= report_thresh){
                    printf("BEST n=%d s=%d E=%lld moves=%lld restarts=%lld t=%.0fs vec=",
                           n,s,bestE,moves,restarts,difftime(time(0),t0));
                    for(int q=0;q<n;q++) putchar(best[q]==0?'0':(best[q]>0?'+':'-'));
                    putchar('\n'); fflush(stdout);
                }
                if(bestE==0){
                    printf("SOLUTION n=%d k=%d vec=",n,k);
                    for(int q=0;q<n;q++) putchar(best[q]==0?'0':(best[q]>0?'+':'-'));
                    putchar('\n'); fflush(stdout);
                    return 0;
                }
            }
            if(stall > 400000){ /* reheat */
                T = 3.0; stall = 0; localbest = E;
            }
            T *= cool;
        }
    }
    printf("DONE n=%d s=%d bestE=%lld moves=%lld restarts=%lld vec=",n,s,bestE,moves,restarts);
    for(int q=0;q<n;q++) putchar(best[q]==0?'0':(best[q]>0?'+':'-'));
    putchar('\n');
    return 2;
}

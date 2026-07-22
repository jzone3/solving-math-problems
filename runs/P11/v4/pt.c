/* V4: parallel tempering (replica exchange) for circulant weighing matrices.
 *
 * Same model as anneal.c: ternary a in {-1,0,+1}^n, fixed composition
 * n_plus=(s^2+s)/2, n_minus=(s^2-s)/2, energy E = sum_{t=1}^{n-1} R(t)^2,
 * target E=0 (all nontrivial periodic autocorrelations zero).
 *
 * M replicas at a geometric temperature ladder; each replica does `sweep`
 * Metropolis swap-moves per round, then adjacent replicas attempt exchange.
 *
 * Usage: ./pt n s seed max_seconds [M] [Tmin] [Tmax] [report_thresh]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int n, s, k, np, nm;

typedef struct { int *a; int *R; long long E; } Rep;

static unsigned long long rng_state;
static inline unsigned long long rng(void){
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}
static inline double rngd(void){ return (rng() >> 11) * (1.0/9007199254740992.0); }
static inline int rngi(int m){ return (int)(rng() % (unsigned)m); }

static void recompute(Rep *r){
    r->E = 0;
    for(int t=0;t<n;t++){
        int v=0;
        for(int i=0;i<n;i++) v += r->a[i]*r->a[(i+t)%n];
        r->R[t]=v;
        if(t) r->E += (long long)v*v;
    }
}

static inline void setval(Rep *r, int i, int v){
    int d = v - r->a[i];
    if(!d) return;
    int *a = r->a, *R = r->R;
    long long E = r->E;
    for(int t=1;t<n;t++){
        int x = R[t];
        E -= (long long)x*x;
        x += d*(a[(i+t)%n] + a[(i-t+n)%n]);
        R[t]=x;
        E += (long long)x*x;
    }
    a[i]=v;
    r->E = E;
}

static void randinit(Rep *r){
    memset(r->a,0,n*sizeof(int));
    int *perm = malloc(n*sizeof(int));
    for(int i=0;i<n;i++) perm[i]=i;
    for(int i=n-1;i>0;i--){ int j=rngi(i+1); int t=perm[i]; perm[i]=perm[j]; perm[j]=t; }
    for(int i=0;i<np;i++) r->a[perm[i]]=1;
    for(int i=0;i<nm;i++) r->a[perm[np+i]]=-1;
    free(perm);
    recompute(r);
}

int main(int argc, char**argv){
    if(argc<4){ fprintf(stderr,"usage: %s n s seed max_seconds [M] [Tmin] [Tmax] [report]\n",argv[0]); return 1; }
    n = atoi(argv[1]); s = atoi(argv[2]);
    rng_state = strtoull(argv[3],0,10) ^ 0x9e3779b97f4a7c15ULL;
    for(int i=0;i<10;i++) rng();
    double max_sec = argc>4 ? atof(argv[4]) : 3600.0;
    int M = argc>5 ? atoi(argv[5]) : 24;
    double Tmin = argc>6 ? atof(argv[6]) : 0.35;
    double Tmax = argc>7 ? atof(argv[7]) : 6.0;
    long long report_thresh = argc>8 ? atoll(argv[8]) : 40;
    k = s*s; np=(k+s)/2; nm=(k-s)/2;

    Rep *reps = malloc(M*sizeof(Rep));
    double *T = malloc(M*sizeof(double));
    for(int m=0;m<M;m++){
        reps[m].a = malloc(n*sizeof(int));
        reps[m].R = malloc(n*sizeof(int));
        randinit(&reps[m]);
        T[m] = Tmin * pow(Tmax/Tmin, (double)m/(M-1));
    }
    int sweep = 4*n;

    time_t t0 = time(0);
    long long bestE = -1;
    int *best = malloc(n*sizeof(int));
    long long moves=0, rounds=0, exch=0, exchacc=0;

    while(difftime(time(0),t0) < max_sec){
        rounds++;
        for(int m=0;m<M;m++){
            Rep *r = &reps[m];
            double temp = T[m];
            for(int q=0;q<sweep;q++){
                int i = rngi(n), j = rngi(n);
                if(r->a[i]==r->a[j]) continue;
                int vi=r->a[i], vj=r->a[j];
                long long Eold = r->E;
                setval(r,i,vj); setval(r,j,vi);
                long long dE = r->E - Eold;
                moves++;
                if(dE > 0 && rngd() >= exp(-(double)dE/temp)){
                    setval(r,j,vj); setval(r,i,vi);
                }
                if(bestE<0 || r->E < bestE){
                    bestE = r->E; memcpy(best,r->a,n*sizeof(int));
                    if(bestE <= report_thresh){
                        printf("BEST n=%d s=%d E=%lld moves=%lld rounds=%lld t=%.0fs vec=",
                               n,s,bestE,moves,rounds,difftime(time(0),t0));
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
            }
        }
        /* replica exchange between adjacent temperatures */
        for(int m=0;m+1<M;m++){
            exch++;
            double d = (1.0/T[m] - 1.0/T[m+1]) * (double)(reps[m].E - reps[m+1].E);
            if(d >= 0 || rngd() < exp(d)){
                Rep tmp = reps[m]; reps[m] = reps[m+1]; reps[m+1] = tmp;
                exchacc++;
            }
        }
        /* occasionally reseed the hottest replica to keep diversity */
        if(rounds % 2000 == 0) randinit(&reps[M-1]);
    }
    printf("DONE n=%d s=%d bestE=%lld moves=%lld rounds=%lld exch_acc=%.2f vec=",
           n,s,bestE,moves,rounds,(double)exchacc/(double)(exch?exch:1));
    for(int x=0;x<n;x++) putchar(best[x]==0?'0':(best[x]>0?'+':'-'));
    putchar('\n');
    return 2;
}

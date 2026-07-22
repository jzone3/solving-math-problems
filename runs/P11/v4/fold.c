/* V4 stage A: search integer "fold" sequences b of length d for CW(n,k) lifting.
 *
 * If a in {-1,0,1}^n is a CW(n,k) first row and d | n, the fold
 * b_j = sum_t a_{j+td} (length d) satisfies:
 *   PAF_d(b)(u) = 0 for u != 0,   PAF_d(b)(0) = sum b_j^2 = k,
 *   sum b_j = +-s (k=s^2), |b_j| <= n/d, sum |b_j| <= k, k - sum|b_j| even.
 * This program anneals such b (a necessary DFT-side projection of the target),
 * printing feasible candidates for the stage-B lifter (lift.c).
 *
 * Usage: ./fold d m s seed max_seconds [maxprint]
 *   d = fold length, m = n/d (entry bound), s = sqrt(k)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int d, m, s, k;
static int b[512]; static long long P[512];
static long long E;

static unsigned long long rng_state;
static inline unsigned long long rng(void){
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}
static inline double rngd(void){ return (rng() >> 11) * (1.0/9007199254740992.0); }
static inline int rngi(int q){ return (int)(rng() % (unsigned)q); }

static long long energy(void){
    long long e=0;
    for(int u=0;u<d;u++){
        long long p=0;
        for(int i=0;i<d;i++) p += (long long)b[i]*b[(i+u)%d];
        P[u]=p;
        if(u) e += p*p;
    }
    long long w = P[0]-k;      /* sum b^2 == k */
    e += 4*w*w;
    long long ab=0; for(int i=0;i<d;i++) ab += llabs(b[i]);
    if(ab>k) e += 4*(ab-k)*(ab-k);      /* sum|b| <= k */
    if(((k-ab)&1) && ab<=k) e += 4;     /* parity */
    return e;
}

int main(int argc, char**argv){
    if(argc<5){ fprintf(stderr,"usage: %s d m s seed max_seconds [maxprint]\n",argv[0]); return 1; }
    d=atoi(argv[1]); m=atoi(argv[2]); s=atoi(argv[3]); k=s*s;
    rng_state = strtoull(argv[4],0,10) ^ 0x9e3779b97f4a7c15ULL;
    for(int i=0;i<10;i++) rng();
    double max_sec = argc>5 ? atof(argv[5]) : 600.0;
    int maxprint = argc>6 ? atoi(argv[6]) : 200;

    time_t t0=time(0);
    int found=0;
    while(difftime(time(0),t0)<max_sec && found<maxprint){
        /* random init with sum = s */
        memset(b,0,sizeof(b));
        for(int i=0;i<s;i++) b[rngi(d)] += 1;
        E = energy();
        double T=8.0;
        for(long long it=0; it<4000000 && E>0; it++){
            /* transfer move: b[p]+=1, b[q]-=1 (preserves sum) */
            int p=rngi(d), q=rngi(d);
            if(p==q || b[p]>=m || b[q]<=-m){ T*=0.999995; continue; }
            b[p]++; b[q]--;
            long long En = energy();
            if(En<=E || rngd() < exp(-(double)(En-E)/T)) E=En;
            else { b[p]--; b[q]++; }
            T*=0.999995; if(T<0.05) T=0.05;
        }
        if(E==0){
            printf("FOLD d=%d m=%d k=%d b=",d,m,k);
            for(int i=0;i<d;i++) printf("%d%s",b[i], i+1<d?",":"\n");
            fflush(stdout);
            found++;
        }
    }
    fprintf(stderr,"found %d folds\n",found);
    return found?0:2;
}

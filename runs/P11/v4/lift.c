/* V4 stage B: anneal ternary lifts of a fixed fold b (DFT-projection pruning).
 *
 * Given d | n and an integer fold b (length d) with PAF_d(b) = k*delta
 * (from fold.c or a known CW(d,k) witness), search a in {-1,0,1}^n whose
 * fold equals b and whose full periodic autocorrelations vanish.
 * Fold-preserving moves: pick residue class j mod d and two slots p,q in it;
 * apply a[p]+=1, a[q]-=1 (reject if leaves {-1,0,1}).  Since the fold fixes
 * sum_{t == 0 mod d} PAF(t) = k, driving all t != 0 PAFs to zero forces
 * weight R(0)=k automatically.  Energy E = sum_{t=1}^{n-1} R(t)^2.
 *
 * Usage: ./lift n d s seed max_seconds b0,b1,...,b{d-1} [report_thresh]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int n, d, m, s, k;
static int *a, *R, *b;
static long long E;

static unsigned long long rng_state;
static inline unsigned long long rng(void){
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}
static inline double rngd(void){ return (rng() >> 11) * (1.0/9007199254740992.0); }
static inline int rngi(int q){ return (int)(rng() % (unsigned)q); }

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
    int dd = v - a[i];
    if(!dd) return;
    for(int t=1;t<n;t++){
        int x=R[t];
        E -= (long long)x*x;
        x += dd*(a[(i+t)%n] + a[(i-t+n)%n]);
        R[t]=x;
        E += (long long)x*x;
    }
    a[i]=v;
}

/* random ternary lift of b with total weight k */
static void randinit(void){
    memset(a,0,n*sizeof(int));
    int wt=0;
    for(int j=0;j<d;j++){
        int need = b[j], sg = need>=0?1:-1, c = abs(need);
        /* place |b_j| entries of sign sg in random slots of class j */
        for(int r=0;r<c;){
            int p = j + d*rngi(m);
            if(a[p]==0){ a[p]=sg; r++; wt++; }
        }
    }
    /* pad with (+1,-1) pairs in classes with >=2 free slots to reach weight k */
    while(wt+2<=k){
        int j=rngi(d), p=j+d*rngi(m), q=j+d*rngi(m);
        if(p!=q && a[p]==0 && a[q]==0){ a[p]=1; a[q]=-1; wt+=2; }
    }
    recompute();
}

int main(int argc, char**argv){
    if(argc<7){ fprintf(stderr,"usage: %s n d s seed max_seconds b_csv [report]\n",argv[0]); return 1; }
    n=atoi(argv[1]); d=atoi(argv[2]); s=atoi(argv[3]); k=s*s; m=n/d;
    rng_state = strtoull(argv[4],0,10) ^ 0x9e3779b97f4a7c15ULL;
    for(int i=0;i<10;i++) rng();
    double max_sec = atof(argv[5]);
    b = malloc(d*sizeof(int));
    { char *tok=strtok(argv[6],","); int j=0;
      while(tok && j<d){ b[j++]=atoi(tok); tok=strtok(0,","); }
      if(j!=d){ fprintf(stderr,"bad b\n"); return 1; }
    }
    long long report_thresh = argc>7 ? atoll(argv[7]) : 60;
    int ab=0; for(int j=0;j<d;j++) ab+=abs(b[j]);
    if(ab>k || ((k-ab)&1)){ fprintf(stderr,"infeasible fold\n"); return 1; }
    a=malloc(n*sizeof(int)); R=malloc(n*sizeof(int));

    time_t t0=time(0);
    long long bestE=-1, moves=0, restarts=0;
    int *best=malloc(n*sizeof(int));

    while(difftime(time(0),t0)<max_sec){
        randinit(); restarts++;
        double T=5.0; long long stall=0, localbest=E;
        while(T>0.04 && difftime(time(0),t0)<max_sec){
            int j=rngi(d);
            int p=j+d*rngi(m), q=j+d*rngi(m);
            if(p==q || a[p]>=1 || a[q]<=-1){ T*=0.99997; continue; }
            long long Eold=E;
            setval(p,a[p]+1); setval(q,a[q]-1);
            long long dE=E-Eold;
            moves++;
            if(dE>0 && rngd() >= exp(-(double)dE/T)){
                setval(q,a[q]+1); setval(p,a[p]-1);
            }
            if(E<localbest){ localbest=E; stall=0; } else stall++;
            if(bestE<0 || E<bestE){
                bestE=E; memcpy(best,a,n*sizeof(int));
                if(bestE<=report_thresh){
                    printf("BEST n=%d d=%d E=%lld moves=%lld restarts=%lld t=%.0fs vec=",
                           n,d,bestE,moves,restarts,difftime(time(0),t0));
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
            if(stall>300000){ T=2.5; stall=0; localbest=E; }
            T*=0.99997;
        }
    }
    printf("DONE n=%d d=%d bestE=%lld moves=%lld restarts=%lld vec=",n,d,bestE,moves,restarts);
    for(int x=0;x<n;x++) putchar(best[x]==0?'0':(best[x]>0?'+':'-'));
    putchar('\n');
    return 2;
}

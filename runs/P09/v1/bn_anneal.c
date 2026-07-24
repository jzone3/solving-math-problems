/* Native simulated-annealing / basin-hopping search for Bollobas-Nikiforov
 * counterexamples at n = 13..40 (uint64 adjacency bitmasks).
 *
 * Objective: maximize ratio = (l1^2 + l2^2) / (2m (1 - 1/omega)), omega exact
 * (Tomita BnB). Metropolis on single edge flips with geometric cooling and
 * periodic random restarts. Prints any graph with score > 1e-6 (counterexample
 * candidate) in graph6 for independent verification.
 *
 * Usage: ./bn_anneal nmin nmax seconds seed [tag]
 * Compile: gcc -O3 -march=native -o bn_anneal bn_anneal.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <time.h>

static int N;
static uint64_t adjm[40];

/* ---- xoshiro256** ---- */
static uint64_t rs[4];
static inline uint64_t rotl(uint64_t x, int k){return (x<<k)|(x>>(64-k));}
static uint64_t rnd(void){
    uint64_t r = rotl(rs[1]*5,7)*9, t = rs[1]<<17;
    rs[2]^=rs[0]; rs[3]^=rs[1]; rs[1]^=rs[2]; rs[0]^=rs[3]; rs[2]^=t; rs[3]=rotl(rs[3],45);
    return r;
}
static double rndu(void){ return (rnd()>>11) * (1.0/9007199254740992.0); }

/* ---- exact max clique ---- */
static int mc_best;
static void mc_expand(uint64_t P, int size){
    if(!P){ if(size>mc_best) mc_best=size; return; }
    int v_list[40], color[40], nv=0;
    uint64_t Q=P;
    while(Q){ int v=__builtin_ctzll(Q); Q&=Q-1; v_list[nv++]=v; }
    uint64_t classes[40]; int nc=0;
    for(int i=0;i<nv;i++){
        int v=v_list[i], c=0;
        while(c<nc && (classes[c]&adjm[v])) c++;
        if(c==nc) classes[nc++]=0;
        classes[c]|=1ULL<<v; color[i]=c+1;
    }
    for(int i=1;i<nv;i++){
        int v=v_list[i], c=color[i], j=i-1;
        while(j>=0 && color[j]>c){ v_list[j+1]=v_list[j]; color[j+1]=color[j]; j--; }
        v_list[j+1]=v; color[j+1]=c;
    }
    for(int i=nv-1;i>=0;i--){
        int v=v_list[i];
        if(size+color[i]<=mc_best) return;
        mc_expand(P&adjm[v], size+1);
        P&=~(1ULL<<v);
    }
}
static int max_clique(void){
    mc_best=0;
    mc_expand(N>=64?~0ULL:((1ULL<<N)-1),0);
    return mc_best;
}

/* ---- top-2 eigenvalues (Householder + Sturm bisection, full precision) ---- */
static void top2(double *l1,double *l2){
    double a[40][40], d[40], e[40];
    for(int i=0;i<N;i++)
        for(int j=0;j<N;j++)
            a[i][j]=(adjm[i]>>j)&1?1.0:0.0;
    for(int i=N-1;i>=1;i--){
        int l=i-1; double h=0,scale=0;
        if(l>0){
            for(int k=0;k<=l;k++) scale+=fabs(a[i][k]);
            if(scale==0) e[i]=a[i][l];
            else{
                for(int k=0;k<=l;k++){ a[i][k]/=scale; h+=a[i][k]*a[i][k]; }
                double f=a[i][l], g=f>=0?-sqrt(h):sqrt(h);
                e[i]=scale*g; h-=f*g; a[i][l]=f-g; f=0;
                for(int j=0;j<=l;j++){
                    g=0;
                    for(int k=0;k<=j;k++) g+=a[j][k]*a[i][k];
                    for(int k=j+1;k<=l;k++) g+=a[k][j]*a[i][k];
                    e[j]=g/h; f+=e[j]*a[i][j];
                }
                double hh=f/(h+h);
                for(int j=0;j<=l;j++){
                    f=a[i][j]; e[j]=g=e[j]-hh*f;
                    for(int k=0;k<=j;k++) a[j][k]-=(f*e[k]+g*a[i][k]);
                }
            }
        } else e[i]=a[i][l];
        d[i]=h;
    }
    e[0]=0;
    double off2[40];
    for(int i=0;i<N;i++) d[i]=a[i][i];
    off2[0]=0;
    for(int i=1;i<N;i++) off2[i]=e[i]*e[i];
    for(int k=1;k<=2;k++){
        double a0=-64,b0=64;
        if(k==2) b0=*l1+1e-9;
        int want=N-k;
        for(int it=0;it<50;it++){
            double x=0.5*(a0+b0);
            int cnt=0; double q=d[0]-x;
            if(q<0) cnt++;
            for(int i=1;i<N;i++){
                q=d[i]-x-(q==0?off2[i]/1e-300:off2[i]/q);
                if(q<0) cnt++;
            }
            if(cnt<=want) a0=x; else b0=x;
        }
        if(k==1) *l1=0.5*(a0+b0); else *l2=0.5*(a0+b0);
    }
}

static void print_g6(FILE*f){
    int nb=N*(N-1)/2, nch=(nb+5)/6, bit=0;
    char buf[256]; buf[0]=63+N;
    for(int c=0;c<nch;c++) buf[1+c]=63;
    for(int j=1;j<N;j++)
        for(int i=0;i<j;i++,bit++)
            if((adjm[i]>>j)&1) buf[1+bit/6]+= 1<<(5-bit%6);
    buf[1+nch]=0;
    fputs(buf,f);
}

static double eval(int *m_out,int *om_out){
    int m=0;
    for(int i=0;i<N;i++) m+=__builtin_popcountll(adjm[i]);
    m/=2;
    int nb=N*(N-1)/2;
    if(m==0||m==nb){ *m_out=m; *om_out=m==0?1:N; return 0.0; }
    double l1,l2; top2(&l1,&l2);
    int om=max_clique();
    *m_out=m; *om_out=om;
    if(om>=N) return 0.0;
    return (l1*l1+l2*l2)/(2.0*m*(1.0-1.0/om));
}

int main(int argc,char**argv){
    int nmin=atoi(argv[1]), nmax=atoi(argv[2]);
    double seconds=atof(argv[3]);
    uint64_t seed=strtoull(argv[4],0,10);
    const char*tag=argc>5?argv[5]:"";
    rs[0]=seed^0x9E3779B97F4A7C15ULL; rs[1]=seed*0xBF58476D1CE4E5B9ULL+1;
    rs[2]=seed^0x94D049BB133111EBULL; rs[3]=seed*2685821657736338717ULL+11;
    for(int i=0;i<20;i++) rnd();
    time_t t0=time(0);
    double globalbest=-1; long long steps=0, restarts=0;
    char bestg6[256]="";
    int bestn=0;
    while(difftime(time(0),t0)<seconds){
        N=nmin+(int)(rnd()%(uint64_t)(nmax-nmin+1));
        double p=0.2+0.6*rndu();
        memset(adjm,0,sizeof(adjm));
        for(int i=0;i<N;i++)for(int j=i+1;j<N;j++)
            if(rndu()<p){ adjm[i]|=1ULL<<j; adjm[j]|=1ULL<<i; }
        int m,om;
        double cur=eval(&m,&om), T=0.02, cool=exp(log(0.0005/0.02)/60000.0);
        restarts++;
        for(int s=0;s<60000;s++,T*=cool){
            int i=rnd()%N, j=rnd()%N;
            if(i==j) continue;
            adjm[i]^=1ULL<<j; adjm[j]^=1ULL<<i;
            double nxt=eval(&m,&om);
            steps++;
            if(nxt>=cur || rndu()<exp((nxt-cur)/T)) cur=nxt;
            else { adjm[i]^=1ULL<<j; adjm[j]^=1ULL<<i; }
            if(cur>globalbest){
                globalbest=cur; bestn=N;
                FILE*mem=fmemopen(bestg6,sizeof(bestg6),"w");
                print_g6(mem); fclose(mem);
                if(cur>1.0+1e-9){
                    double l1,l2; top2(&l1,&l2);
                    printf("CANDIDATE n=%d m=%d omega=%d ratio=%.12f l1=%.9f l2=%.9f g6=",N,m,om,cur,l1,l2);
                    print_g6(stdout); printf("\n"); fflush(stdout);
                }
            }
        }
    }
    fprintf(stderr,"[%s] steps=%lld restarts=%lld best_ratio=%.12f n=%d g6=%s\n",
            tag,steps,restarts,globalbest,bestn,bestg6);
    return 0;
}

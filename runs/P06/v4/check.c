/* check.c  --  exhaustive checker for Graffiti conjectures 129 & 698 (P06 V4)
 *
 * Reads graph6 graphs from stdin (one per line, as produced by nauty geng/gentreeg).
 *
 * For each graph G on n vertices with m edges and degree sequence d_i:
 *   Laplacian eigenvalue population std-dev (129):
 *     dev = sqrt( (sum d_i^2 + 2m)/n  -  (2m/n)^2 )
 *     [ uses trace(L)=2m, trace(L^2)=sum d_i^2 + 2m; depends only on degrees ]
 *   L2-norm of centered eigenvalues (698, "L2 variant" reading):
 *     l2  = sqrt( sum (lambda_i - mean)^2 ) = dev * sqrt(n)
 *   Randic index:
 *     R = sum_{uv in E} 1/sqrt(d_u d_v)
 *
 * Conjecture 129 claims dev <= R.  698 (this reading) claims l2 <= R.
 * We report any graph with dev - R > EPS (129) or l2 - R > EPS (698),
 * and always track the maximum of (dev-R) and (l2-R) seen (the near-misses).
 *
 * graph6 decoding: first char c gives n = c-63 (only n<63 supported here).
 * Then ceil(n*(n-1)/2 / 6) chars, 6 bits each (char-63), MSB first, encoding
 * the upper triangle in column order: for j=1..n-1, for i=0..j-1 the bit A[i][j].
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 40

int main(int argc, char** argv){
    /* args: mode  (129 | 698 | both)   optional: report threshold override */
    const char* mode = (argc>1)? argv[1] : "both";
    int do129 = (strcmp(mode,"698")!=0);
    int do698 = (strcmp(mode,"129")!=0);
    double EPS = 1e-9;

    char* line = NULL; size_t cap = 0; ssize_t len;
    unsigned long long count = 0, viol129 = 0, viol698 = 0, ties129 = 0, violpad = 0, tiespad = 0;
    double best129 = -1e18, best698 = -1e18, near129 = -1e18, bestpad = -1e18;
    char best129g[512]={0}, best698g[512]={0}, near129g[512]={0}, tie129g[512]={0}, bestpadg[512]={0};
    long bestpadN = 0;

    static int deg[MAXN];
    /* store adjacency upper triangle as edge list on the fly */
    while((len = getline(&line, &cap, stdin)) != -1){
        if(len==0) continue;
        /* strip newline */
        while(len>0 && (line[len-1]=='\n'||line[len-1]=='\r')) line[--len]=0;
        if(len==0) continue;
        const char* p = line;
        int n = (int)(*p++) - 63;
        if(n<=0 || n>=63 || n>MAXN){ fprintf(stderr,"bad n=%d\n",n); continue; }
        for(int i=0;i<n;i++) deg[i]=0;
        long m = 0;
        double R = 0.0;
        /* We need degrees before computing R (which uses endpoint degrees),
           so decode edges into a temporary list first. */
        int nbits = n*(n-1)/2;
        /* decode bits */
        static unsigned char bits[MAXN*(MAXN-1)/2];
        int bi=0;
        int nbytes = (nbits+5)/6;
        for(int b=0;b<nbytes;b++){
            int c = (int)(*p++) - 63;
            for(int k=5;k>=0 && bi<nbits;k--){
                bits[bi++] = (c>>k)&1;
            }
        }
        /* map bits to (i,j): order j=1..n-1, i=0..j-1 */
        static int ei[MAXN*(MAXN-1)/2], ej[MAXN*(MAXN-1)/2];
        bi=0;
        for(int j=1;j<n;j++){
            for(int i=0;i<j;i++){
                if(bits[bi]){ deg[i]++; deg[j]++; ei[m]=i; ej[m]=j; m++; }
                bi++;
            }
        }
        /* dev from degrees */
        long sumd2=0; for(int i=0;i<n;i++) sumd2 += (long)deg[i]*deg[i];
        double var = ((double)sumd2 + 2.0*m)/n - ((2.0*m)/n)*((2.0*m)/n);
        if(var<0) var=0;
        double dev = sqrt(var);
        double l2  = dev*sqrt((double)n);
        /* Randic */
        for(long e=0;e<m;e++){
            int a=deg[ei[e]], b=deg[ej[e]];
            R += 1.0/sqrt((double)a*(double)b);
        }
        count++;
        if(do129){
            double g = dev - R;
            if(g>best129){ best129=g; strncpy(best129g,line,511); }
            if(g>-EPS && g<EPS && m>0){ ties129++; if(ties129<=5) strncpy(tie129g,line,511); }
            if(g<=-EPS && g>near129){ near129=g; strncpy(near129g,line,511); }
            if(g>EPS){ viol129++;
                if(viol129<=20) printf("VIOL129 %s dev=%.12f R=%.12f gap=%.12g\n",line,dev,R,g);
            }
        }
        if(do129 && m>0){
            /* padding with isolated vertices: total N vertices, N>n.
               var(N) = (S+2m)/N - (2m/N)^2 maximized at N* = 8m^2/(S+2m). */
            double Nstar = 8.0*(double)m*(double)m/((double)sumd2+2.0*m);
            if(Nstar > (double)n+0.5){
                long Nlo = (long)floor(Nstar), Nhi = Nlo+1;
                if(Nlo <= n) Nlo = n+1;
                for(long N=Nlo; N<=Nhi; N++){
                    double v = ((double)sumd2+2.0*m)/N - (2.0*m/N)*(2.0*m/N);
                    if(v<0) v=0;
                    double g = sqrt(v) - R;
                    if(g>bestpad){ bestpad=g; bestpadN=N; strncpy(bestpadg,line,511); }
                    if(g>EPS){ violpad++;
                        if(violpad<=20) printf("VIOLPAD %s N=%ld dev=%.12f R=%.12f gap=%.12g\n",line,N,sqrt(v),R,g);
                    } else if(g>-EPS){ tiespad++; }
                }
            }
        }
        if(do698){
            double g = l2 - R;
            if(g>best698){ best698=g; strncpy(best698g,line,511); }
            if(g>EPS){ viol698++;
                if(viol698<=20) printf("VIOL698 %s l2=%.12f R=%.12f gap=%.12g\n",line,l2,R,g);
            }
        }
        if((count & 0x3FFFFFFFULL)==0){
            fprintf(stderr,"...processed %llu graphs (best129=%.9f best698=%.9f)\n",count,best129,best698);
            fflush(stderr);
        }
    }
    printf("DONE count=%llu\n", count);
    if(do129){
        printf("129: violations=%llu  best(dev-R)=%.12f  witness=%s\n", viol129, best129, best129g);
        printf("129: ties(|gap|<eps,m>0)=%llu example=%s   best strict near-miss gap=%.12f g6=%s\n", ties129, tie129g, near129, near129g);
        printf("PAD: violations=%llu ties=%llu best(dev_pad-R)=%.12f at N=%ld witness=%s\n", violpad, tiespad, bestpad, bestpadN, bestpadg);
    }
    if(do698) printf("698: violations=%llu  best(l2-R)=%.12f  witness=%s\n", viol698, best698, best698g);
    return 0;
}

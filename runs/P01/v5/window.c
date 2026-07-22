/* P01 V5 window-gadget search.
 * KEY REDUCTION (see NOTES.md §4, SUFFICIENT direction): a 4-regular simple uniquely hamiltonian graph EXISTS IF
 * there is a "window gadget": vertices 0..w-1, path edges (i,i+1), plus a 2-regular
 * simple chord set F (chords != path edges; (0,w-1) allowed), such that the number of
 * hamiltonian 0 -> w-1 paths in P_w + F equals exactly 1.
 * (Chain k>=2 copies of the window in a ring: every vertex gets degree 4, each window is
 * attached by a 2-edge cut, so #HC = t^k where t = #ham end-to-end paths. t=1 -> unique.)
 * Equivalently: t = #HCs through a fixed edge e in the 4-regular graph (window + edge(0,w-1)).
 *
 * This program EXHAUSTIVELY enumerates all chord 2-factors F for given w and reports the
 * minimum t (with the count of F attaining it), stopping immediately if t==1 is found.
 * Usage: ./window w [cutoff]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXW 40
typedef unsigned long long u64;
static int w;
static int ch[MAXW][2], chdeg[MAXW];
static u64 nbr[MAXW];
static long long total=0;
static long long best_t=1LL<<60, best_count=0;
static int best_ch[MAXW][2];
static long long CUT=64, CUT0=64;
static int use_c4=0;

static long long cnt;
static void dfs(int u, int depth, u64 unvis){
    if(cnt>=CUT) return;
    if(depth==w){ /* all visited; must end at w-1 */
        if(u==w-1) cnt++;
        return;
    }
    u64 cand = nbr[u] & unvis;
    while(cand){
        int x=__builtin_ctzll(cand); cand&=cand-1;
        if(x==w-1 && depth!=w-1) continue; /* target only last */
        u64 unvis2 = unvis & ~(1ULL<<x);
        /* conservative prune: every remaining vertex needs >=2 usable edges, crediting
           new endpoint x; the target w-1 needs >=1 usable edge */
        u64 usable = unvis2 | (1ULL<<x);
        u64 rem = unvis2; int ok=1;
        while(rem){
            int y=__builtin_ctzll(rem); rem&=rem-1;
            int need = (y==w-1)?1:2;
            if(__builtin_popcountll(nbr[y]&usable) < need){ ok=0; break; }
        }
        if(ok) dfs(x, depth+1, unvis2);
        if(cnt>=CUT) return;
    }
}

static long long count_paths(void){
    for(int v=0;v<w;v++){
        nbr[v]=0;
        if(v+1<w) nbr[v]|=1ULL<<(v+1);
        if(v-1>=0) nbr[v]|=1ULL<<(v-1);
        for(int k=0;k<2;k++) if(ch[v][k]>=0) nbr[v]|=1ULL<<ch[v][k];
    }
    cnt=0;
    CUT = best_t+1 < CUT0 ? best_t+1 : CUT0;  /* adaptive: only need to know t vs best */
    u64 unvis=((w==64?~0ULL:(1ULL<<w)-1)) & ~1ULL;
    dfs(0,1,unvis);
    return cnt;
}

static int is_chord(int a,int b){ return ch[a][0]==b||ch[a][1]==b; }

static void enumerate(int minu_for, int minu){
    /* find smallest incomplete vertex */
    int v=-1;
    for(int i=0;i<w;i++) if(chdeg[i]<2){ v=i; break; }
    if(v<0){
        total++;
        long long t=count_paths();
        if(t<best_t){ best_t=t; best_count=1; memcpy(best_ch,ch,sizeof(ch));
            fprintf(stderr,"w=%d new min t=%lld\n",w,t);
            if(t==1){
                printf("GADGET FOUND w=%d chords:",w);
                for(int a=0;a<w;a++)for(int k=0;k<2;k++)if(a<ch[a][k])printf(" %d-%d",a,ch[a][k]);
                printf("\n"); exit(42);
            }
        } else if(t==best_t) best_count++;
        return;
    }
    int start = (v==minu_for)? minu : v+1;
    for(int u=start; u<w; u++){
        if(chdeg[u]>=2) continue;
        if(u==v+1) continue;          /* path edge */
        if(is_chord(v,u)) continue;   /* simple */
        if(use_c4){                    /* prune parallel adjacent chords (forces t>=2) */
            if(v+1<w && u+1<w && is_chord(v+1,u+1)) continue;
            if(v-1>=0 && u-1>=0 && is_chord(v-1,u-1)) continue;
        }
        ch[v][chdeg[v]]=u; ch[u][chdeg[u]]=v;
        chdeg[v]++; chdeg[u]++;
        enumerate(v, u+1);
        chdeg[v]--; chdeg[u]--;
        ch[v][chdeg[v]]=-1; ch[u][chdeg[u]]=-1;
    }
}

int main(int argc,char**argv){
    if(argc<2){ fprintf(stderr,"usage: %s w [cutoff]\n",argv[0]); return 1; }
    w=atoi(argv[1]);
    if(argc>2) CUT0=atoll(argv[2]);
    if(argc>3 && !strcmp(argv[3],"c4")) use_c4=1;
    for(int i=0;i<w;i++){ ch[i][0]=ch[i][1]=-1; chdeg[i]=0; }
    enumerate(-1,0);
    printf("w=%d exhausted: %lld chord-2-factors, min t=%lld attained by %lld; example:",
           w,total,best_t,best_count);
    for(int a=0;a<w;a++)for(int k=0;k<2;k++)if(best_ch[a][k]>=0&&a<best_ch[a][k])
        printf(" %d-%d",a,best_ch[a][k]);
    printf("\n");
    return 0;
}

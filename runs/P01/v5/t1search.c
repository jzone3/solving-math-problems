/* P01 V5: exhaustive search for a t=1 window gadget (see NOTES.md §4).
 * Gadget: path 0-1-...-(w-1) plus chord set where every vertex gets exactly 2 chords
 * (chords simple, != path edges), such that the ONLY hamiltonian 0->(w-1) path in the
 * graph is the canonical path. Such a gadget immediately disproves Sheehan (ring k>=2).
 *
 * Enumeration = DFS over chord assignments (lowest-incomplete-vertex first).
 * Pruning:
 *  - monotonicity: chords only ADD ham paths, so if the PARTIAL graph already has a
 *    second ham 0->(w-1) path, prune the subtree (checked after every chord addition);
 *  - C4: parallel adjacent chords (i,j),(i+1,j+1) instantly give a second path;
 *  - reflection symmetry i <-> w-1-i broken on the first chord of vertex 0.
 * Exit 42 + "GADGET FOUND" if found; else prints "w exhausted, no t=1 gadget".
 * Usage: ./t1search w [firstpartner]   (firstpartner: split work by 0's first chord)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXW 64
typedef unsigned long long u64;
static int w;
static int ch[MAXW][2], chdeg[MAXW];
static u64 nbr[MAXW];
static long long nodes=0, leaves=0;

static long long cnt, CUT;
static void dfs(int u, int depth, u64 unvis){
    if(cnt>=CUT) return;
    if(depth==w){ if(u==w-1) cnt++; return; }
    u64 cand = nbr[u] & unvis;
    while(cand){
        int x=__builtin_ctzll(cand); cand&=cand-1;
        if(x==w-1 && depth!=w-1) continue;
        u64 unvis2 = unvis & ~(1ULL<<x);
        u64 usable = unvis2 | (1ULL<<x);
        u64 rem = unvis2; int ok=1;
        while(rem){
            int y=__builtin_ctzll(rem); rem&=rem-1;
            int need=(y==w-1)?1:2;
            /* vertices may have degree <4 in partial graphs: usable edges only among
               current nbr sets; conservative as chords only get added */
            u64 e = nbr[y]&usable;
            int p=__builtin_popcountll(e);
            /* in partial graph a vertex may have <need available now but gain chords
               later; pruning here would be UNSOUND for partial graphs. Only apply the
               degree prune when the vertex's chords are complete. */
            if(chdeg[y]==2 && p<need){ ok=0; break; }
        }
        if(ok) dfs(x, depth+1, unvis2);
        if(cnt>=CUT) return;
    }
}

static long long count_paths(long long lim){
    for(int v=0;v<w;v++){
        nbr[v]=0;
        if(v+1<w) nbr[v]|=1ULL<<(v+1);
        if(v-1>=0) nbr[v]|=1ULL<<(v-1);
        for(int k=0;k<chdeg[v];k++) nbr[v]|=1ULL<<ch[v][k];
    }
    cnt=0; CUT=lim;
    u64 unvis=((w==64?~0ULL:(1ULL<<w)-1)) & ~1ULL;
    dfs(0,1,unvis);
    return cnt;
}

static int is_chord(int a,int b){
    for(int k=0;k<chdeg[a];k++) if(ch[a][k]==b) return 1;
    return 0;
}

static int firstpartner=-1;

static void enumerate(void){
    nodes++;
    int v=-1;
    for(int i=0;i<w;i++) if(chdeg[i]<2){ v=i; break; }
    if(v<0){
        leaves++;
        if(count_paths(2)==1){
            printf("GADGET FOUND w=%d chords:",w);
            for(int a=0;a<w;a++)for(int k=0;k<2;k++)if(a<ch[a][k])printf(" %d-%d",a,ch[a][k]);
            printf("\n"); fflush(stdout); exit(42);
        }
        return;
    }
    for(int u=v+1; u<w; u++){
        if(chdeg[u]>=2) continue;
        if(u==v+1) continue;
        if(is_chord(v,u)) continue;
        /* C4 prune */
        if(v+1<w && u+1<w && is_chord(v+1,u+1)) continue;
        if(v-1>=0 && u-1>=0 && is_chord(v-1,u-1)) continue;
        /* symmetry: first chord of vertex 0 vs reflection — 0's partner p reflects to
           w-1's partner w-1-p; canonical: p-0 <= ... simple break: when v==0&&chdeg==0,
           require u-0 <= (w-1)-(smallest partner of w-1 after reflection) — cheap proxy:
           u <= w-1-2 always true; skip strict breaking, use firstpartner splitting. */
        if(v==0 && chdeg[0]==0 && firstpartner>=0 && u!=firstpartner) continue;
        ch[v][chdeg[v]++]=u; ch[u][chdeg[u]++]=v;
        if(count_paths(2)<2) enumerate();
        chdeg[v]--; chdeg[u]--;
    }
}

int main(int argc,char**argv){
    if(argc<2){ fprintf(stderr,"usage: %s w [firstpartner]\n",argv[0]); return 1; }
    w=atoi(argv[1]);
    if(argc>2) firstpartner=atoi(argv[2]);
    memset(chdeg,0,sizeof(chdeg));
    enumerate();
    printf("w=%d fp=%d exhausted, no t=1 gadget. nodes=%lld leaves=%lld\n",
           w,firstpartner,nodes,leaves);
    return 0;
}

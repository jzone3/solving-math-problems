/* Complete row-based search for Tuscan-2 squares T2(n), standard form,
 * with forward checking + MRV (minimum remaining values) row ordering.
 *
 * Standard form: row 0 = identity; first column = identity (WLOG, counting
 * lemma).  Row starting with symbol s chosen from precomputed candidate set
 * C_s (permutations starting s avoiding identity's d1/d2 pairs).  At each
 * node we keep, for every unassigned s, the list of candidates compatible
 * with all used d1/d2 pairs; we branch on the s with the fewest and filter
 * children lists incrementally (fail-fast on empty).
 *
 * Extra prune: the LAST column of a T2 square must also be a permutation
 * (counting lemma), so candidates whose last symbol is already used as some
 * chosen row's last symbol are filtered.
 *
 * usage: rowdfs2 n [split_s split_lo split_hi] [maxseconds]
 *   split: restrict the TOP-level branching (which is chosen as start
 *   symbol split_s) to candidate indices [lo,hi) of the root-filtered list,
 *   for distributed runs.  Use split_s=-1 (or omit) for full search.
 * Prints witness if found; final line: nodes=... SOLUTIONS=... EXHAUSTED|TIMEOUT
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAXN 13
#define W 3

typedef struct { uint64_t m[W]; } mask_t;
static int N;
static inline void mset(mask_t *x,int b){ x->m[b>>6]|=1ULL<<(b&63); }
static inline int mtest(const mask_t *x,int b){ return (x->m[b>>6]>>(b&63))&1; }
static inline int disjoint(const mask_t*a,const mask_t*b){
    return !((a->m[0]&b->m[0])|(a->m[1]&b->m[1])|(a->m[2]&b->m[2]));
}
static inline void morq(mask_t*a,const mask_t*b){a->m[0]|=b->m[0];a->m[1]|=b->m[1];a->m[2]|=b->m[2];}

typedef struct { unsigned char p[MAXN]; mask_t d1,d2; unsigned short lastbit; } cand_t;
static cand_t *cands[MAXN]; static int ncand[MAXN];

static unsigned char cur[MAXN]; static int used_[MAXN];
static mask_t id1,id2;
static cand_t *gbuf; static int gcnt,gcap;
static void gen(int pos){
    if(pos==N){
        cand_t c; memset(&c,0,sizeof c); memcpy(c.p,cur,N);
        for(int i=0;i<N-1;i++) mset(&c.d1,cur[i]*N+cur[i+1]);
        for(int i=0;i<N-2;i++) mset(&c.d2,cur[i]*N+cur[i+2]);
        c.lastbit = 1u << cur[N-1];
        if(gcnt==gcap){gcap=gcap?gcap*2:1024;gbuf=realloc(gbuf,gcap*sizeof(cand_t));}
        gbuf[gcnt++]=c; return;
    }
    for(int x=0;x<N;x++){
        if(used_[x]) continue;
        if(mtest(&id1,cur[pos-1]*N+x)) continue;
        if(pos>=2 && mtest(&id2,cur[pos-2]*N+x)) continue;
        cur[pos]=x; used_[x]=1; gen(pos+1); used_[x]=0;
    }
}
static void build(void){
    memset(&id1,0,sizeof id1); memset(&id2,0,sizeof id2);
    for(int a=0;a<N-1;a++) mset(&id1,a*N+(a+1));
    for(int a=0;a<N-2;a++) mset(&id2,a*N+(a+2));
    for(int s=1;s<N;s++){
        gbuf=NULL;gcnt=gcap=0;memset(used_,0,sizeof used_);
        cur[0]=s;used_[s]=1;gen(1);
        cands[s]=gbuf;ncand[s]=gcnt;
        fprintf(stderr,"start=%d candidates=%d\n",s,gcnt);
    }
}

/* candidate index lists, per depth per symbol: we store filtered arrays in a
 * big arena indexed by depth */
static int *lists[MAXN][MAXN];   /* lists[depth][s] -> array of cand indices */
static int  lens[MAXN][MAXN];
static long long nodes=0, solutions=0;
static int stop_after_first=1, timedout=0;
static time_t t0; static double maxsec=1e18;
static unsigned char sol[MAXN][MAXN];
static int split_s=-1, split_lo=0, split_hi=-1;

static void print_sol(int depth_assigned_count){
    (void)depth_assigned_count;
    printf("WITNESS T2(%d):\n",N);
    for(int r=0;r<N;r++){for(int i=0;i<N;i++)printf("%d ",sol[r][i]);printf("\n");}
    fflush(stdout);
}

static int assigned[MAXN];

static int dfs(int depth, mask_t *u1, mask_t *u2, unsigned lastmask){
    if(depth==N){ solutions++; print_sol(depth); return stop_after_first; }
    /* MRV: pick unassigned s with min list length */
    int best=-1,bl=1<<30;
    for(int s=1;s<N;s++) if(!assigned[s]){
        if(lens[depth][s]<bl){bl=lens[depth][s];best=s;}
    }
    int s=best;
    int lo=0, hi=lens[depth][s];
    if(depth==1 && split_s>=0){ s=split_s; lo=split_lo; hi=split_hi<0?lens[depth][s]:split_hi;
        if(hi>lens[depth][s]) hi=lens[depth][s]; }
    for(int ii=lo;ii<hi;ii++){
        cand_t *c=&cands[s][lists[depth][s][ii]];
        nodes++;
        if((nodes&0xFFFFF)==0){
            double el=difftime(time(NULL),t0);
            fprintf(stderr,"nodes=%lld depth=%d elapsed=%.0fs\n",nodes,depth,el);
            if(el>maxsec){timedout=1;return 1;}
        }
        if(lastmask & c->lastbit) continue;
        mask_t n1=*u1,n2=*u2; morq(&n1,&c->d1); morq(&n2,&c->d2);
        unsigned nlast = lastmask | c->lastbit;
        /* forward check: filter all unassigned lists (excluding s) */
        int ok=1;
        for(int t=1;t<N && ok;t++) if(t!=s && !assigned[t]){
            int *src=lists[depth][t], m=lens[depth][t];
            int *dst=lists[depth+1][t], k=0;
            for(int j=0;j<m;j++){
                cand_t *d=&cands[t][src[j]];
                if(!(nlast & d->lastbit) && disjoint(&n1,&d->d1) && disjoint(&n2,&d->d2)) dst[k++]=src[j];
            }
            lens[depth+1][t]=k;
            if(k==0) ok=0;
        }
        if(ok){
            memcpy(sol[s],c->p,N);
            assigned[s]=1;
            if(dfs(depth+1,&n1,&n2,nlast)) return 1;
            assigned[s]=0;
        }
    }
    return 0;
}

int main(int argc,char**argv){
    N=atoi(argv[1]);
    if(argc>=5){ split_s=atoi(argv[2]); split_lo=atoi(argv[3]); split_hi=atoi(argv[4]); }
    if(argc>=6) maxsec=atof(argv[5]);
    build();
    for(int i=0;i<N;i++) sol[0][i]=i;
    for(int d=1;d<N;d++) for(int s=1;s<N;s++) lists[d][s]=malloc(ncand[s]*sizeof(int));
    mask_t u1,u2; memset(&u1,0,sizeof u1); memset(&u2,0,sizeof u2);
    morq(&u1,&id1); morq(&u2,&id2);
    for(int s=1;s<N;s++){ for(int j=0;j<ncand[s];j++) lists[1][s][j]=j; lens[1][s]=ncand[s]; }
    t0=time(NULL);
    dfs(1,&u1,&u2, 1u<<(N-1)); /* identity row's last symbol is n-1 */
    printf("nodes=%lld SOLUTIONS=%lld %s\n",nodes,solutions,timedout?"TIMEOUT":"EXHAUSTED");
    return 0;
}

/* Complete row-based search for Tuscan-2 squares T2(n), standard form.
 *
 * Standard form (WLOG, see NOTES.md): row 0 = identity, first column =
 * identity (each symbol is first in exactly one row).  Row r must be a
 * permutation starting with symbol r.  Candidates for each row are
 * precomputed: permutations starting with r whose distance-1 pairs avoid the
 * identity row's pairs (a,a+1) and distance-2 pairs avoid (a,a+2)
 * internally consistent.  DFS over rows 1..n-1 keeping bitmasks of used
 * distance-1 pairs (must end with ALL n(n-1) covered - guaranteed by
 * counting) and used distance-2 pairs (at most once).
 *
 * usage: rowdfs n [first_row_lo first_row_hi] [maxseconds]
 *   optional range restricts the level-1 (row starting with 1) candidate
 *   indices searched, for distributed splitting.  Prints progress, any
 *   witness found, and SOLUTIONS=k / EXHAUSTED or TIMEOUT at the end.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAXN 13
#define MAXP (MAXN*MAXN)   /* pair index a*n+b < 169 -> 3 x 64-bit words */
#define W 3

typedef struct { uint64_t m[W]; } mask_t;

static int N;
static inline void mset(mask_t *x, int b){ x->m[b>>6] |= 1ULL<<(b&63); }
static inline int mtest(const mask_t *x, int b){ return (x->m[b>>6]>>(b&63))&1; }
static inline int disjoint(const mask_t *a, const mask_t *b){
    return !((a->m[0]&b->m[0])|(a->m[1]&b->m[1])|(a->m[2]&b->m[2]));
}
static inline void morq(mask_t *a, const mask_t *b){
    a->m[0]|=b->m[0]; a->m[1]|=b->m[1]; a->m[2]|=b->m[2];
}
static inline void mandn(mask_t *a, const mask_t *b){ /* a &= ~b */
    a->m[0]&=~b->m[0]; a->m[1]&=~b->m[1]; a->m[2]&=~b->m[2];
}

typedef struct { unsigned char p[MAXN]; mask_t d1, d2; } cand_t;

static cand_t *cands[MAXN];
static int ncand[MAXN];

/* generation */
static unsigned char cur[MAXN];
static int used[MAXN];
static mask_t id1, id2;
static int gen_start;
static cand_t *gbuf; static int gcnt, gcap;

static void gen(int pos){
    if (pos == N){
        cand_t c; memset(&c,0,sizeof c);
        memcpy(c.p, cur, N);
        for (int i=0;i<N-1;i++) mset(&c.d1, cur[i]*N+cur[i+1]);
        for (int i=0;i<N-2;i++) mset(&c.d2, cur[i]*N+cur[i+2]);
        if (gcnt==gcap){ gcap=gcap?gcap*2:1024; gbuf=realloc(gbuf,gcap*sizeof(cand_t)); }
        gbuf[gcnt++]=c;
        return;
    }
    for (int x=0;x<N;x++){
        if (used[x]) continue;
        int a=cur[pos-1];
        if (mtest(&id1,a*N+x)) continue;                 /* identity d1 */
        if (pos>=2){ int b=cur[pos-2]; if (mtest(&id2,b*N+x)) continue; }
        /* internal repeats impossible within a permutation row for d1;
           d2 within one row: pairs distinct positions -> can repeat? a d2
           pair (u,v) occurs twice in one row only if u appears twice: no. */
        cur[pos]=x; used[x]=1; gen(pos+1); used[x]=0;
    }
}

static void build(void){
    memset(&id1,0,sizeof id1); memset(&id2,0,sizeof id2);
    for (int a=0;a<N-1;a++) mset(&id1, a*N+(a+1));
    for (int a=0;a<N-2;a++) mset(&id2, a*N+(a+2));
    for (int s=1;s<N;s++){
        gbuf=NULL; gcnt=gcap=0;
        memset(used,0,sizeof used);
        cur[0]=s; used[s]=1;
        gen(1);
        cands[s]=gbuf; ncand[s]=gcnt;
        fprintf(stderr,"start=%d candidates=%d\n", s, gcnt);
    }
}

/* search */
static long long nodes=0, solutions=0;
static int stop_after_first=1;
static time_t t0; static double maxsec=1e18;
static unsigned char sol[MAXN][MAXN];
static int lo1=0, hi1=-1;
static int timedout=0;

static void print_sol(void){
    printf("WITNESS T2(%d):\n", N);
    for (int r=0;r<N;r++){ for(int i=0;i<N;i++) printf("%d ", sol[r][i]); printf("\n"); }
    fflush(stdout);
}

static int dfs(int level, mask_t *u1, mask_t *u2){
    if (level == N){
        solutions++;
        print_sol();
        return stop_after_first;
    }
    cand_t *cs = cands[level]; int nc = ncand[level];
    int lo = (level==1)? lo1 : 0;
    int hi = (level==1 && hi1>=0)? hi1 : nc;
    for (int i=lo;i<hi;i++){
        cand_t *c=&cs[i];
        if (!disjoint(u1,&c->d1)) continue;
        if (!disjoint(u2,&c->d2)) continue;
        nodes++;
        if ((nodes & 0xFFFFF)==0){
            double el = difftime(time(NULL),t0);
            fprintf(stderr,"nodes=%lld level=%d elapsed=%.0fs\n",nodes,level,el);
            if (el > maxsec){ timedout=1; return 1; }
        }
        memcpy(sol[level], c->p, N);
        mask_t n1=*u1, n2=*u2; morq(&n1,&c->d1); morq(&n2,&c->d2);
        if (dfs(level+1,&n1,&n2)) return 1;
    }
    return 0;
}

int main(int argc, char **argv){
    N = atoi(argv[1]);
    if (argc>=4){ lo1=atoi(argv[2]); hi1=atoi(argv[3]); }
    if (argc>=5) maxsec=atof(argv[4]);
    build();
    for (int i=0;i<N;i++) sol[0][i]=i;
    mask_t u1, u2; memset(&u1,0,sizeof u1); memset(&u2,0,sizeof u2);
    morq(&u1,&id1); morq(&u2,&id2);
    t0=time(NULL);
    dfs(1,&u1,&u2);
    printf("nodes=%lld SOLUTIONS=%lld %s\n", nodes, solutions,
           timedout? "TIMEOUT": "EXHAUSTED");
    return 0;
}

/* exhaust_indep.c — independent exhaustive (v,k)-PMD search, deliberately
 * different from pmd_dlx.c: no dancing links, no precomputed candidate rows.
 * Plain backtracking on blocks: at each step take the lexicographically
 * smallest ordered pair (x,y) not yet covered at distance 1 and branch over
 * every k-tuple (x, y, z1..z_{k-2}) of distinct points whose coverage
 * (all distances) is disjoint from the current coverage.  Every PMD contains
 * exactly one block covering each distance-1 pair, and each cyclic block
 * containing x->y adjacent has exactly one representation starting (x,y),
 * so the tree contains every PMD exactly once.
 *
 * Usage: exhaust_indep v k [fixfirst]
 *   fixfirst=1: force the block chosen for pair (0,1) at depth 0 to be
 *   (0,1,...,k-1) (WLOG relabelling).  Default 0 = fully unrestricted.
 * Prints "solutions=<n> nodes=<n>".
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int V, K, B, fixfirst = 0;
static unsigned char cov[8][40][40]; /* cov[d][x][y] */
static long long nsol = 0, nodescnt = 0;
static int sol[64][16];

static int try_block(int depth);

static void place(int depth){
    /* find smallest uncovered distance-1 pair */
    int x = -1, y = -1;
    for(int a = 0; a < V && x < 0; a++)
        for(int bb = 0; bb < V; bb++)
            if(a != bb && !cov[1][a][bb]){ x = a; y = bb; break; }
    int blk[16];
    int used[40];
    if(x < 0){ nsol++;
        printf("SOLUTION BEGIN\n");
        for(int i=0;i<depth;i++){ for(int j=0;j<K;j++) printf("%d ", sol[i][j]); printf("\n"); }
        printf("SOLUTION END\n");
        return; }
    blk[0] = x; blk[1] = y;
    memset(used, 0, sizeof(used)); used[x] = used[y] = 1;
    /* recursive extension over positions 2..K-1 */
    void ext(int p){
        if(p == K){
            nodescnt++;
            /* check coverage disjoint */
            for(int d = 1; d < K; d++)
                for(int i = 0; i < K; i++)
                    if(cov[d][blk[i]][blk[(i+d)%K]]) return;
            for(int d = 1; d < K; d++)
                for(int i = 0; i < K; i++)
                    cov[d][blk[i]][blk[(i+d)%K]] = 1;
            memcpy(sol[depth], blk, sizeof(int)*K);
            place(depth + 1);
            for(int d = 1; d < K; d++)
                for(int i = 0; i < K; i++)
                    cov[d][blk[i]][blk[(i+d)%K]] = 0;
            return;
        }
        for(int e = 0; e < V; e++){
            if(used[e]) continue;
            if(fixfirst && depth == 0 && e != p) continue;
            /* prune: distance-1 pair blk[p-1]->e must be uncovered */
            if(cov[1][blk[p-1]][e]) continue;
            blk[p] = e; used[e] = 1; ext(p + 1); used[e] = 0;
        }
    }
    if(fixfirst && depth == 0 && (x != 0 || y != 1)){ return; }
    ext(2);
}

int main(int argc, char **argv){
    V = atoi(argv[1]); K = atoi(argv[2]);
    if(argc > 3) fixfirst = atoi(argv[3]);
    B = V*(V-1)/K;
    place(0);
    printf("v=%d k=%d solutions=%lld nodes=%lld\n", V, K, nsol, nodescnt);
    return 0;
}

/* Exact MAXIMUM partial (v,6)-PMD packing.
 *
 * Finds the maximum number of blocks (cyclic 6-tuples, distinct points) such
 * that no ordered pair (x,y) is t-apart in more than one block, for each
 * t = 1..5.  A (v,6)-PMD is exactly a packing of size b = v(v-1)/6, so this
 * quantifies how close to perfect one can get (near-miss measure).
 *
 * Complete branch-and-bound: pick the lexicographically smallest distance-1
 * pair (x,y) that is neither covered nor excluded; branch over (a) every
 * block starting (x,y,...) consistent with the current state, and (b)
 * excluding (x,y) (deciding no chosen block ever has x immediately before y).
 * Every packing is reachable: blocks are added in the order of their minimal
 * uncovered distance-1 pair.  Bound: placed + floor(free_d1_pairs/6) <= best
 * prunes, since each block consumes 6 free distance-1 pairs.
 *
 * WLOG first block (0,1,2,3,4,5) only if -fix given (for max-packing the
 * empty packing has no block to normalize, but any nonempty maximum packing
 * can be relabeled so some block is (0..5), so -fix is safe for max >= 1).
 *
 * Usage: ./pmd6_truemax v [-fix]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define K 6
#define MAXV 20

static int V, B, fix = 0;
static unsigned char used[K][MAXV][MAXV];
static unsigned char excl[MAXV][MAXV];
static int blocks[64][K];
static int nblocks = 0;
static int best = 0;
static int bestblocks[64][K];
static uint64_t nodes = 0;
static time_t t0;

static void mark(int *blk, int val) {
    int i, t;
    for (t = 1; t < K; t++)
        for (i = 0; i < K; i++)
            used[t][blk[i]][blk[(i + t) % K]] = (unsigned char)val;
}

static int fits(int *blk, int p, int z) {
    int q;
    for (q = 0; q < p; q++) {
        int d = p - q;
        if (used[d][blk[q]][z]) return 0;
        if (used[K - d][z][blk[q]]) return 0;
    }
    return 1;
}

static int free_d1(void) {
    int x, y, c = 0;
    for (x = 0; x < V; x++)
        for (y = 0; y < V; y++)
            if (x != y && !used[1][x][y] && !excl[x][y]) c++;
    return c;
}

static void search(void);

static void extend(int *blk, int p, unsigned int usedmask) {
    int z;
    if (p == K) {
        /* block must not use any excluded distance-1 pair */
        int i;
        for (i = 0; i < K; i++)
            if (excl[blk[i]][blk[(i + 1) % K]]) return;
        mark(blk, 1);
        memcpy(blocks[nblocks], blk, sizeof(int) * K);
        nblocks++;
        search();
        nblocks--;
        mark(blk, 0);
        return;
    }
    for (z = 0; z < V; z++) {
        if (usedmask & (1u << z)) continue;
        if (!fits(blk, p, z)) continue;
        blk[p] = z;
        extend(blk, p + 1, usedmask | (1u << z));
    }
}

static void search(void) {
    int x, y, fx = -1, fy = -1;
    int blk[K];
    nodes++;
    if ((nodes & ((1ULL << 28) - 1)) == 0) {
        fprintf(stderr, "truemax v=%d: nodes=%llu best=%d elapsed=%lds\n",
                V, (unsigned long long)nodes, best, (long)(time(NULL) - t0));
        fflush(stderr);
    }
    if (nblocks > best) {
        best = nblocks;
        memcpy(bestblocks, blocks, sizeof(blocks));
        fprintf(stderr, "new best packing: %d blocks (nodes=%llu)\n", best,
                (unsigned long long)nodes);
        {
            int a, c;
            for (a = 0; a < best; a++) {
                for (c = 0; c < K; c++) fprintf(stderr, "%d ", bestblocks[a][c]);
                fprintf(stderr, "\n");
            }
        }
        fflush(stderr);
        if (best == B) return; /* perfect: cannot do better */
    }
    if (nblocks + free_d1() / K <= best) return; /* bound */
    for (x = 0; x < V && fx < 0; x++)
        for (y = 0; y < V; y++)
            if (x != y && !used[1][x][y] && !excl[x][y]) { fx = x; fy = y; break; }
    if (fx < 0) return;
    /* branch (a): cover (fx,fy) */
    blk[0] = fx; blk[1] = fy;
    extend(blk, 2, (1u << fx) | (1u << fy));
    /* branch (b): exclude (fx,fy) */
    excl[fx][fy] = 1;
    search();
    excl[fx][fy] = 0;
}

int main(int argc, char **argv) {
    int i, j;
    if (argc < 2) { fprintf(stderr, "usage: %s v [-fix]\n", argv[0]); return 2; }
    V = atoi(argv[1]);
    for (i = 2; i < argc; i++)
        if (!strcmp(argv[i], "-fix")) fix = 1;
    if (V < K || V > MAXV) { fprintf(stderr, "bad v\n"); return 2; }
    B = V * (V - 1) / K;
    t0 = time(NULL);
    memset(used, 0, sizeof(used));
    memset(excl, 0, sizeof(excl));
    if (fix) {
        int first[K] = {0, 1, 2, 3, 4, 5};
        mark(first, 1);
        memcpy(blocks[0], first, sizeof(first));
        nblocks = 1;
        best = 1;
        memcpy(bestblocks, blocks, sizeof(blocks));
    }
    search();
    printf("MAXPACK v=%d k=%d: maximum partial PMD packing = %d blocks (perfect would be %d)\n",
           V, K, best, B);
    for (i = 0; i < best; i++) {
        for (j = 0; j < K; j++) printf("%d ", bestblocks[i][j]);
        printf("\n");
    }
    printf("nodes=%llu\n", (unsigned long long)nodes);
    return 0;
}

/* Exhaustive backtracking search for (v,6)-PMD (perfect Mendelsohn design,
 * block size k=6).
 *
 * Definition: a (v,k)-PMD is a collection of b = v(v-1)/k cyclically ordered
 * k-tuples of distinct points from {0..v-1} such that for every t = 1..k-1,
 * every ordered pair (x,y) of distinct points is t-apart in exactly one block
 * (x at position i, y at position (i+t) mod k).
 *
 * Search strategy (complete / exhaustive):
 *   - WLOG (point relabeling) the design contains the block (0,1,2,3,4,5):
 *     any PMD has some block; relabel its points to 0..5 in cyclic order.
 *     Optionally disabled with -nofix (for cross-checking small cases).
 *   - At each node, find the lexicographically smallest ordered pair (x,y)
 *     with the distance-1 slot still uncovered.  Some block must contain
 *     x immediately followed by y; every block containing x->y adjacent can
 *     be rotated (cyclic symmetry of blocks) to start (x, y, ...).  So we
 *     branch over all completions (x,y,c3,c4,c5,c6) consistent with the
 *     current partial design.  Each block is generated exactly once, so the
 *     enumeration is exhaustive without block-order symmetry duplication.
 *   - Incremental constraint checking: when placing an element we check all
 *     ordered pairs (both directions, at their cyclic distances) against
 *     already-placed elements of the block.
 *
 * Output: first solution found (then exits with SAT), or "UNSAT" after the
 * full tree is exhausted.  Node counts printed for the log.
 *
 * Usage: ./pmd6_search v [-all] [-nofix]
 *   -all   : count all solutions instead of stopping at the first
 *   -nofix : do not fix the first block (full search; for validation)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define K 6
#define MAXV 20

static int V, B;
static int nofix = 0, findall = 0;
static unsigned char used[K][MAXV][MAXV]; /* used[t][x][y]: pair (x,y) t-apart covered */
static int blocks[64][K];
static int nblocks = 0;
static uint64_t nodes = 0, solutions = 0;

static void print_solution(void) {
    int i, j;
    printf("SOLUTION v=%d k=%d b=%d\n", V, K, B);
    for (i = 0; i < nblocks; i++) {
        for (j = 0; j < K; j++) printf("%d ", blocks[i][j]);
        printf("\n");
    }
    fflush(stdout);
}

/* mark/unmark all 30 ordered-pair slots of a block */
static void mark(int *blk, int val) {
    int i, t;
    for (t = 1; t < K; t++)
        for (i = 0; i < K; i++)
            used[t][blk[i]][blk[(i + t) % K]] = (unsigned char)val;
}

/* check whether element z can be placed at position p of partial block blk
 * (positions 0..p-1 filled) */
static int fits(int *blk, int p, int z) {
    int q;
    for (q = 0; q < p; q++) {
        int d = p - q;              /* (blk[q], z) is d-apart */
        if (used[d][blk[q]][z]) return 0;
        if (used[K - d][z][blk[q]]) return 0;
    }
    return 1;
}

static void search(void);

static void extend(int *blk, int p, unsigned int usedmask) {
    int z;
    if (p == K) {
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
    if (nblocks == B) {
        solutions++;
        print_solution();
        if (!findall) exit(0);
        return;
    }
    /* forced pair: smallest (x,y) with distance-1 slot uncovered */
    for (x = 0; x < V && fx < 0; x++)
        for (y = 0; y < V; y++)
            if (x != y && !used[1][x][y]) { fx = x; fy = y; break; }
    if (fx < 0) return; /* all covered but fewer than B blocks: impossible */
    blk[0] = fx; blk[1] = fy;
    if (!fits(blk, 1, fy)) return; /* cannot happen, but keep safe */
    extend(blk, 2, (1u << fx) | (1u << fy));
}

int main(int argc, char **argv) {
    int i;
    if (argc < 2) { fprintf(stderr, "usage: %s v [-all] [-nofix]\n", argv[0]); return 2; }
    V = atoi(argv[1]);
    for (i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "-all")) findall = 1;
        else if (!strcmp(argv[i], "-nofix")) nofix = 1;
    }
    if (V < K || V > MAXV || (V * (V - 1)) % K != 0) {
        fprintf(stderr, "bad v\n"); return 2;
    }
    B = V * (V - 1) / K;
    memset(used, 0, sizeof(used));
    if (!nofix) {
        int first[K] = {0, 1, 2, 3, 4, 5};
        mark(first, 1);
        memcpy(blocks[0], first, sizeof(first));
        nblocks = 1;
    }
    search();
    printf("UNSAT v=%d k=%d b=%d (exhaustive%s)\n", V, K, B, nofix ? ", no fixed block" : ", first block fixed WLOG");
    printf("nodes=%llu solutions=%llu\n", (unsigned long long)nodes, (unsigned long long)solutions);
    return 1;
}

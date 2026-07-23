/* Exhaustive backtracking search for (v,6)-PMD — version 2.
 *
 * Same completeness argument as pmd6_search.c (see that file / NOTES.md), plus:
 *   - MRV branching: instead of the lexicographically smallest uncovered
 *     distance-1 pair, branch on the uncovered pair (x,y) with the FEWEST
 *     feasible third elements z (blk = x,y,z).  Any uncovered pair must be
 *     completed by some block, so branching on any single uncovered pair is
 *     complete; choosing the most constrained one shrinks the tree.
 *   - Forward check: if any uncovered distance-1 pair has zero feasible third
 *     elements, prune the node.
 *   - Parallel partitioning: -mod r m runs only the top-level branches
 *     (completions of the very first branching pair) with index ≡ r (mod m).
 *     The union over r = 0..m-1 covers the whole tree exactly once.
 *   - Progress line to stderr every 2^30 nodes.
 *
 * Usage: ./pmd6_search2 v [-all] [-nofix] [-mod r m]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define K 6
#define MAXV 20

static int V, B;
static int nofix = 0, findall = 0;
static int modr = 0, modm = 1;
static int firstlevel;          /* nblocks value at the first branching level */
static long topidx = 0;
static unsigned char used[K][MAXV][MAXV];
static int blocks[64][K];
static int nblocks = 0;
static uint64_t nodes = 0, solutions = 0;
static int maxdepth = 0;
static time_t t0;

static void print_solution(void) {
    int i, j;
    printf("SOLUTION v=%d k=%d b=%d\n", V, K, B);
    for (i = 0; i < nblocks; i++) {
        for (j = 0; j < K; j++) printf("%d ", blocks[i][j]);
        printf("\n");
    }
    fflush(stdout);
}

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

static void search(void);

static void extend(int *blk, int p, unsigned int usedmask) {
    int z;
    if (p == K) {
        if (nblocks == firstlevel) {          /* top-level partitioning */
            long idx = topidx++;
            if (idx % modm != modr) return;
        }
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
    int x, y, z;
    int fx = -1, fy = -1, best = 1 << 30;
    int blk[K];
    nodes++;
    if (nblocks > maxdepth) { maxdepth = nblocks; fprintf(stderr, "new max blocks: %d (nodes=%llu)\n", maxdepth, (unsigned long long)nodes); }
    if ((nodes & ((1ULL << 30) - 1)) == 0) {
        fprintf(stderr, "progress v=%d mod %d/%d: nodes=%llu depth=%d elapsed=%lds\n",
                V, modr, modm, (unsigned long long)nodes, nblocks,
                (long)(time(NULL) - t0));
        fflush(stderr);
    }
    if (nblocks == B) {
        solutions++;
        print_solution();
        if (!findall) exit(0);
        return;
    }
    /* MRV: uncovered distance-1 pair with fewest feasible third elements */
    for (x = 0; x < V; x++) {
        for (y = 0; y < V; y++) {
            if (x == y || used[1][x][y]) continue;
            int cnt = 0;
            int tb[K];
            tb[0] = x; tb[1] = y;
            for (z = 0; z < V; z++) {
                if (z == x || z == y) continue;
                if (fits(tb, 2, z)) cnt++;
            }
            if (cnt == 0) return;   /* forward-check failure */
            if (cnt < best) { best = cnt; fx = x; fy = y; }
        }
    }
    if (fx < 0) return; /* all distance-1 covered but nblocks < B: impossible */
    blk[0] = fx; blk[1] = fy;
    extend(blk, 2, (1u << fx) | (1u << fy));
}

int main(int argc, char **argv) {
    int i;
    if (argc < 2) { fprintf(stderr, "usage: %s v [-all] [-nofix] [-mod r m]\n", argv[0]); return 2; }
    V = atoi(argv[1]);
    for (i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "-all")) findall = 1;
        else if (!strcmp(argv[i], "-nofix")) nofix = 1;
        else if (!strcmp(argv[i], "-mod") && i + 2 < argc) {
            modr = atoi(argv[i + 1]); modm = atoi(argv[i + 2]); i += 2;
        }
    }
    if (V < K || V > MAXV || (V * (V - 1)) % K != 0) { fprintf(stderr, "bad v\n"); return 2; }
    B = V * (V - 1) / K;
    t0 = time(NULL);
    memset(used, 0, sizeof(used));
    if (!nofix) {
        int first[K] = {0, 1, 2, 3, 4, 5};
        mark(first, 1);
        memcpy(blocks[0], first, sizeof(first));
        nblocks = 1;
    }
    firstlevel = nofix ? 0 : 1;
    search();
    printf("UNSAT v=%d k=%d b=%d (exhaustive%s) mod %d/%d\n", V, K, B,
           nofix ? ", no fixed block" : ", first block fixed WLOG", modr, modm);
    printf("nodes=%llu solutions=%llu topbranches=%ld\n",
           (unsigned long long)nodes, (unsigned long long)solutions, topidx);
    return 1;
}

/* t2dlx.c — exact-cover (Algorithm X / dancing links) formulation of
 * Tuscan-2 square search, standard form (row 0 = identity, col 0 = identity).
 *
 * Primary items (must be covered exactly once):
 *   - G_r  (r = 1..n-1): row-slot r is filled (by a candidate starting with r)
 *   - P_ab (a != b, pair not used by row 0): distance-1 pair (a,b) is used
 *   - L_s  (s = 0..n-2): symbol s is the last symbol of some row (row 0 ends
 *          with n-1, so the other rows' last symbols are exactly 0..n-2)
 * Secondary items (at most once, never branched on):
 *   - D_ab: distance-2 pair (a,b), for pairs not used by row 0
 *
 * Each DLX row = one candidate permutation (starts with its group symbol,
 * avoids row 0's d1/d2 pairs) covering: its G, its 10 P's, its L, its 9 D's.
 *
 * Because #candidates covering each P is ~ #candidates/n, and MRV column
 * selection + O(1) dancing-links updates replace full domain rescans, this
 * should exhaust far faster than t2dfs.c.
 *
 * Usage: ./t2dlx n mode [seed]
 *   mode 0 = exhaustive (UNSAT proof if no solution)
 *   mode 1 = randomized row order within each column (witness hunt; single
 *            exhaustive pass in randomized order)
 *   mode 2 = sliced exhaustive: ./t2dlx n 2 slice stride — only group-1
 *            candidates with index % stride == slice at the top level.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define NMAX 16
static int N;

/* ---------- candidate generation (same pruning as t2dfs.c) ---------- */
static uint8_t (*cands)[NMAX];
static long ncand, ccap;
static uint8_t buf[NMAX];
static int usedsym;

static void addcand(const uint8_t *p) {
    if (ncand == ccap) { ccap = ccap ? ccap * 2 : 1 << 20; cands = realloc(cands, ccap * NMAX); }
    memcpy(cands[ncand++], p, N);
}
static void gen(int pos) {
    if (pos == N) { addcand(buf); return; }
    for (int s = 0; s < N; s++) {
        if (usedsym >> s & 1) continue;
        if (pos >= 1 && s == buf[pos - 1] + 1) continue;
        if (pos >= 2 && s == buf[pos - 2] + 2) continue;
        buf[pos] = s; usedsym |= 1 << s;
        gen(pos + 1);
        usedsym &= ~(1 << s);
    }
}

/* ---------- DLX ---------- */
/* items: 0 .. nitems-1; header nodes 0..nitems-1, root = nitems */
static int nprim, nitems, root;
static int gid[NMAX];                /* item id of G_r */
static int pid_[NMAX][NMAX];         /* item id of P_ab, or -1 */
static int lid[NMAX];                /* item id of L_s, or -1 */
static int did_[NMAX][NMAX];         /* item id of D_ab (secondary), or -1 */

typedef struct { int up, dn, lt, rt, itm; } Node;
static Node *nd;
static long nnodes_alloc, nfree;
static int *len;                      /* per item: column length */
static long *rowid;                   /* node -> candidate index (for first node of row) */
static long *node_row;                /* node -> candidate index */

static long long steps;
static int maxdepth;
static long sol[NMAX];
static int soldepth;

static uint64_t rng = 88172645463325252ULL;
static uint64_t xrnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

static void cover(int c) {
    Node *h = &nd[c];
    nd[h->lt].rt = h->rt; nd[h->rt].lt = h->lt;
    for (int i = nd[c].dn; i != c; i = nd[i].dn)
        for (int j = nd[i].rt; j != i; j = nd[j].rt) {
            nd[nd[j].up].dn = nd[j].dn; nd[nd[j].dn].up = nd[j].up;
            len[nd[j].itm]--;
        }
}
static void uncover(int c) {
    for (int i = nd[c].up; i != c; i = nd[i].up)
        for (int j = nd[i].lt; j != i; j = nd[j].lt) {
            len[nd[j].itm]++;
            nd[nd[j].up].dn = j; nd[nd[j].dn].up = j;
        }
    Node *h = &nd[c];
    nd[h->lt].rt = c; nd[h->rt].lt = c;
}

static int mode = 0;
static long slice = 0, stride = 1;

static int search(int depth) {
    steps++;
    if (depth > maxdepth) {
        maxdepth = depth;
        fprintf(stderr, "depth %d steps %lld\n", depth, steps);
    }
    if (steps % 500000000LL == 0)
        fprintf(stderr, "... steps %lld depth %d maxdepth %d\n", steps, depth, maxdepth);
    if (nd[root].rt == root) { soldepth = depth; return 1; }
    /* MRV over primary items */
    int c = -1, best = 1 << 30;
    for (int i = nd[root].rt; i != root; i = nd[i].rt)
        if (len[i] < best) { best = len[i]; c = i; }
    if (best == 0) return 0;
    cover(c);
    /* collect row nodes (optionally shuffled) */
    if (mode == 1) {
        int cnt = 0;
        int *stack_rows = malloc((len[c] + 1) * sizeof(int));
        for (int i = nd[c].dn; i != c; i = nd[i].dn) stack_rows[cnt++] = i;
        for (int i = cnt - 1; i > 0; i--) {
            int j = xrnd() % (i + 1);
            int t = stack_rows[i]; stack_rows[i] = stack_rows[j]; stack_rows[j] = t;
        }
        for (int k = 0; k < cnt; k++) {
            int i = stack_rows[k];
            sol[depth] = node_row[i];
            for (int j = nd[i].rt; j != i; j = nd[j].rt) cover(nd[j].itm);
            if (search(depth + 1)) { free(stack_rows); return 1; }
            for (int j = nd[i].lt; j != i; j = nd[j].lt) uncover(nd[j].itm);
        }
        free(stack_rows);
    } else {
        long k = 0;
        for (int i = nd[c].dn; i != c; i = nd[i].dn, k++) {
            if (depth == 0 && mode == 2 && (k % stride) != slice) continue;
            sol[depth] = node_row[i];
            for (int j = nd[i].rt; j != i; j = nd[j].rt) cover(nd[j].itm);
            if (search(depth + 1)) return 1;
            for (int j = nd[i].lt; j != i; j = nd[j].lt) uncover(nd[j].itm);
            if (depth == 0 && mode == 2)
                fprintf(stderr, "SUBTREE-DONE top-index %ld steps %lld maxdepth %d\n", k, steps, maxdepth);
        }
    }
    uncover(c);
    return 0;
}

int main(int argc, char **argv) {
    N = atoi(argv[1]);
    mode = argc > 2 ? atoi(argv[2]) : 0;
    int sample_pct = 100;   /* mode 1: keep each candidate with this prob (%) */
    if (mode == 1 && argc > 3) { rng = strtoull(argv[3], 0, 10); if (!rng) rng = 1; }
    if (mode == 1 && argc > 4) sample_pct = atoi(argv[4]);
    if (mode == 2) { slice = argc > 3 ? atol(argv[3]) : 0; stride = argc > 4 ? atol(argv[4]) : 1; }

    gen(0);  /* all candidates (any first symbol != forbidden), filter groups below */
    fprintf(stderr, "candidates (all groups incl 0): %ld\n", ncand);

    /* assign items */
    nitems = 0;
    for (int r = 1; r < N; r++) gid[r] = nitems++;
    memset(pid_, -1, sizeof pid_);
    memset(did_, -1, sizeof did_);
    memset(lid, -1, sizeof lid);
    for (int a = 0; a < N; a++)
        for (int b = 0; b < N; b++) {
            if (a == b) continue;
            if (b == a + 1) continue;           /* d1 used by row 0 */
            pid_[a][b] = nitems++;
        }
    for (int s = 0; s < N - 1; s++) lid[s] = nitems++;
    nprim = nitems;
    for (int a = 0; a < N; a++)
        for (int b = 0; b < N; b++) {
            if (a == b) continue;
            if (b == a + 2) continue;           /* d2 used by row 0 */
            did_[a][b] = nitems++;
        }
    root = nitems;

    /* count usable candidates: first symbol in 1..N-1, last symbol != N-1 */
    uint8_t *keep = malloc(ncand);
    long usable = 0;
    for (long i = 0; i < ncand; i++) {
        keep[i] = cands[i][0] >= 1 && cands[i][N - 1] != N - 1 &&
                  (sample_pct >= 100 || (int)(xrnd() % 100) < sample_pct);
        if (keep[i]) usable++;
    }
    fprintf(stderr, "usable candidates: %ld  items: %d (primary %d)\n", usable, nitems, nprim);

    long per_row = 1 /*G*/ + (N - 1) /*P*/ + 1 /*L*/ + (N - 2) /*D*/;
    nnodes_alloc = nitems + 1 + usable * per_row + 16;
    nd = malloc(nnodes_alloc * sizeof(Node));
    len = calloc(nitems, sizeof(int));
    node_row = malloc(nnodes_alloc * sizeof(long));

    /* header ring */
    for (int i = 0; i <= nitems; i++) {
        nd[i].up = nd[i].dn = i;
        nd[i].itm = i;
    }
    /* only primary items in the header ring */
    int prev = root;
    for (int i = 0; i < nprim; i++) { nd[prev].rt = i; nd[i].lt = prev; prev = i; }
    nd[prev].rt = root; nd[root].lt = prev;
    /* secondary items: self-looped left/right so cover() of them never touches ring */
    for (int i = nprim; i < nitems; i++) { nd[i].lt = i; nd[i].rt = i; }

    nfree = nitems + 1;
    for (long i = 0; i < ncand; i++) {
        const uint8_t *p = cands[i];
        if (!keep[i]) continue;
        int items[2 * NMAX + 2], cnt = 0;
        items[cnt++] = gid[p[0]];
        for (int c = 0; c + 1 < N; c++) items[cnt++] = pid_[p[c]][p[c + 1]];
        items[cnt++] = lid[p[N - 1]];
        for (int c = 0; c + 2 < N; c++) items[cnt++] = did_[p[c]][p[c + 2]];
        int first = -1, prevn = -1;
        for (int t = 0; t < cnt; t++) {
            int it = items[t];
            if (it < 0) { fprintf(stderr, "BUG: bad item\n"); return 2; }
            long id = nfree++;
            nd[id].itm = it;
            node_row[id] = i;
            /* vertical insert at bottom of column */
            nd[id].up = nd[it].up; nd[id].dn = it;
            nd[nd[it].up].dn = id; nd[it].up = id;
            len[it]++;
            /* horizontal ring */
            if (first < 0) { first = id; nd[id].lt = nd[id].rt = id; }
            else {
                nd[id].lt = prevn; nd[id].rt = first;
                nd[prevn].rt = id; nd[first].lt = id;
            }
            prevn = id;
        }
    }
    fprintf(stderr, "DLX built: %ld nodes\n", nfree);

    clock_t t0 = clock();
    int found = search(0);
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    fprintf(stderr, "found %d steps %lld maxdepth %d time %.2fs\n", found, steps, maxdepth, el);
    if (found) {
        printf("WITNESS\n");
        for (int c = 0; c < N; c++) printf("%d ", c);
        printf("\n");
        /* solution rows are unordered; print by first symbol */
        for (int r = 1; r < N; r++)
            for (int d = 0; d < soldepth; d++)
                if (cands[sol[d]][0] == r) {
                    for (int c = 0; c < N; c++) printf("%d ", cands[sol[d]][c]);
                    printf("\n");
                }
        fflush(stdout);
    }
    return found ? 0 : 1;
}

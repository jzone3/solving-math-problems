/* Generic exact-cover DFS over bitmask candidates.
 * Input (stdin): n_items n_cands then one hex mask per line (candidate).
 * Optional argv[1] = hex mask of pre-covered items (fixed partial solution).
 * Pivot: uncovered item with fewest live candidates (recomputed per node).
 * Prints chosen candidate indices if a solution is found, else "UNSAT".
 * Exhaustive on termination.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXW 16
static int n_items, n_cands, W;
static unsigned long long (*masks)[MAXW];
static int **by_item, *by_len;
static unsigned long long cover[MAXW];
static int chosen[512], n_chosen = 0;
static long long nodes = 0;

static int intersects(unsigned long long *a, unsigned long long *b) {
    for (int i = 0; i < W; i++) if (a[i] & b[i]) return 1;
    return 0;
}

static int dfs(void) {
    nodes++;
    if ((nodes & 0xFFFFF) == 0) {
        fprintf(stderr, "nodes=%lldM depth=%d\n", nodes >> 20, n_chosen);
        fflush(stderr);
    }
    int full = 1;
    for (int w = 0; w < W; w++) {
        unsigned long long want = (w == W - 1 && n_items % 64)
            ? ((1ULL << (n_items % 64)) - 1) : ~0ULL;
        if (w * 64 >= n_items) want = 0;
        if ((cover[w] & want) != want) { full = 0; break; }
    }
    if (full) return 1;
    /* pivot */
    int best_item = -1, best_cnt = 1 << 30;
    for (int it = 0; it < n_items; it++) {
        if ((cover[it >> 6] >> (it & 63)) & 1ULL) continue;
        int cnt = 0;
        for (int j = 0; j < by_len[it]; j++) {
            int ci = by_item[it][j];
            if (!intersects(masks[ci], cover)) cnt++;
        }
        if (cnt < best_cnt) { best_cnt = cnt; best_item = it; if (!cnt) return 0; }
    }
    for (int j = 0; j < by_len[best_item]; j++) {
        int ci = by_item[best_item][j];
        if (intersects(masks[ci], cover)) continue;
        for (int w = 0; w < W; w++) cover[w] |= masks[ci][w];
        chosen[n_chosen++] = ci;
        if (dfs()) return 1;
        n_chosen--;
        for (int w = 0; w < W; w++) cover[w] &= ~masks[ci][w];
    }
    return 0;
}

int main(int argc, char **argv) {
    if (scanf("%d %d", &n_items, &n_cands) != 2) return 1;
    W = (n_items + 63) / 64;
    masks = malloc(sizeof(*masks) * n_cands);
    char buf[600];
    for (int i = 0; i < n_cands; i++) {
        scanf("%512s", buf);
        memset(masks[i], 0, sizeof(masks[i]));
        int len = strlen(buf);
        /* hex string, big-endian; parse nibble by nibble from the end */
        for (int p = 0; p < len; p++) {
            char c = buf[len - 1 - p];
            int v = c <= '9' ? c - '0' : (c | 32) - 'a' + 10;
            int bit = p * 4;
            for (int b = 0; b < 4; b++)
                if (v & (1 << b)) masks[i][(bit + b) >> 6] |= 1ULL << ((bit + b) & 63);
        }
    }
    memset(cover, 0, sizeof(cover));
    if (argc > 1) { /* fixed cover mask in hex */
        char *s = argv[1];
        int len = strlen(s);
        for (int p = 0; p < len; p++) {
            char c = s[len - 1 - p];
            int v = c <= '9' ? c - '0' : (c | 32) - 'a' + 10;
            int bit = p * 4;
            for (int b = 0; b < 4; b++)
                if (v & (1 << b)) cover[(bit + b) >> 6] |= 1ULL << ((bit + b) & 63);
        }
    }
    by_item = malloc(sizeof(int *) * n_items);
    by_len = calloc(n_items, sizeof(int));
    for (int i = 0; i < n_cands; i++)
        for (int it = 0; it < n_items; it++)
            if ((masks[i][it >> 6] >> (it & 63)) & 1ULL) by_len[it]++;
    for (int it = 0; it < n_items; it++) {
        by_item[it] = malloc(sizeof(int) * by_len[it]);
        by_len[it] = 0;
    }
    for (int i = 0; i < n_cands; i++)
        for (int it = 0; it < n_items; it++)
            if ((masks[i][it >> 6] >> (it & 63)) & 1ULL)
                by_item[it][by_len[it]++] = i;
    if (dfs()) {
        printf("SOLUTION");
        for (int i = 0; i < n_chosen; i++) printf(" %d", chosen[i]);
        printf("\n");
    } else {
        printf("UNSAT\n");
    }
    fprintf(stderr, "nodes=%lld\n", nodes);
    return 0;
}

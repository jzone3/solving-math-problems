/* Fast longest-path triple-intersection scanner for P05 (Gallai 3 longest paths).
 *
 * Reads graph6 lines on stdin (n <= 62). For each graph, enumerates all longest
 * paths (by vertex count), dedupes their vertex sets (up to MAXMASKS), and computes
 * the minimum over triples of |P1 & P2 & P3|.
 *
 * Output per graph: "<t> <L> <nmasks> <g6>"  (t = min triple intersection; if only
 * 1 or 2 distinct vertex sets exist, t = popcount of their intersection).
 * Prints "HIT <g6>" and exits 42 immediately if t == 0.
 *
 * Usage: nauty-geng -C 10 | ./lp [tmax]     (only lines with t <= tmax printed; default 3)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 62
#define MAXMASKS 200000

static int n;
static uint64_t adjm[MAXN];
static int deg[MAXN], nbr[MAXN][MAXN];
static int bestL;                 /* best path length in vertices */
static uint64_t masks[MAXMASKS];
static int nmasks;
static int overflow;

static inline int pc(uint64_t x) { return __builtin_popcountll(x); }

static uint64_t reach(uint64_t start, uint64_t allowed) {
    uint64_t seen = start & allowed, frontier = seen;
    while (frontier) {
        uint64_t nxt = 0, f = frontier;
        while (f) {
            int v = __builtin_ctzll(f);
            f &= f - 1;
            nxt |= adjm[v];
        }
        frontier = nxt & allowed & ~seen;
        seen |= frontier;
    }
    return seen;
}

/* hash table stamping: we bump cur_stamp per graph */
static int cur_stamp_global = 0;
static uint64_t htab[1 << 18];
static int hstamp[1 << 18];
static void clear_masks(void) { nmasks = 0; overflow = 0; cur_stamp_global++; }
static void add_mask2(uint64_t m) {
    if (nmasks >= MAXMASKS) { overflow = 1; return; }
    uint32_t h = (uint32_t)((m * 0x9E3779B97F4A7C15ULL) >> 46);
    while (hstamp[h] == cur_stamp_global && htab[h] != m) h = (h + 1) & ((1 << 18) - 1);
    if (hstamp[h] == cur_stamp_global) return;
    hstamp[h] = cur_stamp_global;
    htab[h] = m;
    masks[nmasks++] = m;
}

static int path[MAXN];

static int ham_found;

static void dfs(int v, uint64_t used, int len, int start) {
    if (ham_found) return;
    if (len > bestL) {
        bestL = len; clear_masks(); cur_stamp_global++;
        if (len == n) { ham_found = 1; return; }  /* t = n, uninteresting */
    }
    if (len == bestL && start <= path[len - 1]) add_mask2(used);
    uint64_t avail = adjm[v] & ~used;
    if (!avail) return;
    uint64_t rm = reach(avail, ~used);
    if (len + pc(rm) < bestL) return;
    uint64_t a = avail;
    while (a) {
        int u = __builtin_ctzll(a);
        a &= a - 1;
        path[len] = u;
        dfs(u, used | (1ULL << u), len + 1, start);
    }
}

/* min over triples of |Pi & Pj & Pk|; masks[] deduped */
static int triple_min(void) {
    if (nmasks == 1) return pc(masks[0]);
    if (nmasks == 2) return pc(masks[0] & masks[1]);
    int best = 64;
    /* sound lower bound: any triple intersection contains the global intersection */
    uint64_t all = ~0ULL;
    for (int i = 0; i < nmasks; i++) all &= masks[i];
    int lb = pc(all);
    long budget = 400000000L; /* ops; if exceeded, result is an upper bound (flagged) */
    for (int i = 0; i < nmasks && best > lb; i++) {
        for (int j = i + 1; j < nmasks && best > lb; j++) {
            uint64_t m = masks[i] & masks[j];
            for (int k = 0; k < nmasks; k++) {
                if (k == i || k == j) continue;
                int c = pc(m & masks[k]);
                if (c < best) { best = c; if (best <= lb) break; }
            }
            budget -= nmasks;
            if (budget < 0) { overflow = 1; return best; }
        }
    }
    return best;
}

static int parse_g6(const char *s) {
    int idx = 0;
    n = s[idx++] - 63;
    if (n < 1 || n > MAXN) return -1;
    memset(adjm, 0, sizeof(adjm));
    int k = 0, x = 0, bits = 0;
    for (int j = 1; j < n; j++) {
        for (int i = 0; i < j; i++) {
            if (bits == 0) { x = s[idx++] - 63; bits = 6; }
            if (x & (1 << (bits - 1))) {
                adjm[i] |= 1ULL << j;
                adjm[j] |= 1ULL << i;
            }
            bits--;
            k++;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    int tmax = argc > 1 ? atoi(argv[1]) : 3;
    char line[8192];
    long cnt = 0;
    int global_min = 999;
    long hist[65];
    memset(hist, 0, sizeof(hist));
    while (fgets(line, sizeof(line), stdin)) {
        if (line[0] == '>' || line[0] == '\n') continue;
        line[strcspn(line, "\r\n")] = 0;
        if (parse_g6(line) < 0) continue;
        cnt++;
        bestL = 0;
        ham_found = 0;
        clear_masks();
        for (int s = 0; s < n && !ham_found; s++) {
            path[0] = s;
            dfs(s, 1ULL << s, 1, s);
        }
        int t = ham_found ? n : triple_min();
        hist[t]++;
        if (t < global_min) {
            global_min = t;
            fprintf(stderr, "new min t=%d L=%d masks=%d%s g6=%s (graph %ld)\n",
                    t, bestL, nmasks, overflow ? "(overflow)" : "", line, cnt);
        }
        if (t <= tmax) { printf("%d %d %d %d %s\n", t, bestL, nmasks, overflow, line); fflush(stdout); }
        if (t == 0) { printf("HIT %s\n", line); fflush(stdout); if (!getenv("LP_NOEXIT")) return 42; }
    }
    fprintf(stderr, "done: %ld graphs, min t=%d, hist:", cnt, global_min);
    for (int i = 0; i <= 64; i++) if (hist[i]) fprintf(stderr, " %d->%ld", i, hist[i]);
    fprintf(stderr, "\n");
    return 0;
}

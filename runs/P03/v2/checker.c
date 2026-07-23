/* Fast Woodall checker for directg -T streams (phase 4).
 *
 * Reads lines "n m  u v u v ...", for each digraph:
 *   1. SCC condensation (Tarjan, iterative);
 *   2. enumerate lower sets of the condensation -> dicuts as arc bitmasks;
 *   3. tau = min dicut size; skip tau < 2;
 *   4. rho shortcut (ACZ): rho <= 2, or (tau == 3 && rho == 3) => packs;
 *   5. randomized greedy packing (T tries); survivors printed to stdout
 *      for exact ILP certification in Python.
 * Stats printed to stderr at EOF.
 *
 * Assumes n <= 16, arcs <= 64 (fits u64 arc masks), lower sets <= 2^16.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint64_t u64;
typedef uint32_t u32;

static u32 rngs = 0x9E3779B9u;
static inline u32 rnd(void) {
    rngs ^= rngs << 13; rngs ^= rngs >> 17; rngs ^= rngs << 5;
    return rngs;
}

#define MAXN 16
#define MAXM 64
#define MAXCUTS 70000

static int au[MAXM], av[MAXM];
static u64 cuts[MAXCUTS];

/* Tarjan SCC, iterative */
static int comp[MAXN];
static int scc(int n, int m) {
    static int idx[MAXN], low[MAXN], onstk[MAXN], stk[MAXN], sp;
    static int head[MAXN], nxt[MAXM], to[MAXM];
    static int wv[MAXN], wp[MAXN];
    int counter = 0, nc = 0, wtop;
    for (int i = 0; i < n; i++) { idx[i] = -1; onstk[i] = 0; head[i] = -1; }
    for (int i = 0; i < m; i++) { to[i] = av[i]; nxt[i] = head[au[i]]; head[au[i]] = i; }
    sp = 0;
    for (int root = 0; root < n; root++) {
        if (idx[root] != -1) continue;
        wtop = 0; wv[0] = root; wp[0] = head[root];
        idx[root] = low[root] = counter++; stk[sp++] = root; onstk[root] = 1;
        while (wtop >= 0) {
            int v = wv[wtop];
            int advanced = 0;
            for (int e = wp[wtop]; e != -1; e = nxt[e]) {
                int w = to[e];
                if (idx[w] == -1) {
                    wp[wtop] = nxt[e];
                    wtop++; wv[wtop] = w; wp[wtop] = head[w];
                    idx[w] = low[w] = counter++; stk[sp++] = w; onstk[w] = 1;
                    advanced = 1; break;
                } else if (onstk[w] && idx[w] < low[v]) low[v] = idx[w];
            }
            if (advanced) continue;
            wp[wtop] = -1;
            if (low[v] == idx[v]) {
                int w;
                do { w = stk[--sp]; onstk[w] = 0; comp[w] = nc; } while (w != v);
                nc++;
            }
            wtop--;
            if (wtop >= 0) { int pv = wv[wtop]; if (low[v] < low[pv]) low[pv] = low[v]; }
        }
    }
    return nc;
}

int main(int argc, char **argv) {
    long long readn = 0, tau_ge2 = 0, rho_short = 0, greedy_ok = 0,
              survivors = 0, cut_blow = 0;
    int gtries = argc > 1 ? atoi(argv[1]) : 60;
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        char *p = line;
        int n = (int)strtol(p, &p, 10);
        int m = (int)strtol(p, &p, 10);
        if (n <= 0 || m <= 0 || n > MAXN || m > MAXM) continue;
        for (int i = 0; i < m; i++) {
            au[i] = (int)strtol(p, &p, 10);
            av[i] = (int)strtol(p, &p, 10);
        }
        readn++;
        int nc = scc(n, m);
        if (nc == 1) continue;
        /* condensation arcs: cu != cv, keep original arc index */
        int cm = 0;
        static int cu_[MAXM], cv_[MAXM];
        static u64 predmask[MAXN];
        for (int i = 0; i < nc; i++) predmask[i] = 0;
        for (int i = 0; i < m; i++) {
            int cu = comp[au[i]], cv = comp[av[i]];
            if (cu != cv) { cu_[cm] = cu; cv_[cm] = cv; predmask[cv] |= 1ull << cu; cm++; }
        }
        /* topological order of condensation (Tarjan gives reverse topo:
           comp ids are numbered so that all arcs go from higher to lower id;
           so topo order = nc-1, nc-2, ..., 0) */
        /* enumerate lower (ancestor-closed) sets over comps in topo order */
        int ncuts = 0;
        int nsets = 0;
        static u32 sets[1 << MAXN];
        sets[nsets++] = 0;
        /* iterate comps in topo order: id nc-1 down to 0 */
        for (int ci = nc - 1; ci >= 0; ci--) {
            int cur = nsets;
            u32 pm = (u32)predmask[ci];
            for (int s = 0; s < cur; s++) {
                u32 msk = sets[s];
                if ((pm & ~msk) == 0) {
                    if (nsets >= (1 << MAXN)) { nsets = -1; break; }
                    sets[nsets++] = msk | (1u << ci);
                }
            }
            if (nsets < 0) break;
        }
        if (nsets < 0) { cut_blow++; continue; }
        u32 fullmask = (nc >= 32) ? 0xffffffffu : ((1u << nc) - 1);
        int tau = 999;
        for (int s = 0; s < nsets; s++) {
            u32 U = sets[s];
            if (U == 0 || U == fullmask) continue;
            /* dicut iff no arc enters U */
            u64 cutmask = 0; int bad = 0, sz = 0;
            for (int j = 0; j < cm; j++) {
                int inu = (U >> cu_[j]) & 1, inv = (U >> cv_[j]) & 1;
                if (!inu && inv) { bad = 1; break; }
                if (inu && !inv) { cutmask |= 1ull << j; sz++; }
            }
            if (bad) continue;
            if (ncuts >= MAXCUTS) { bad = 2; cut_blow++; ncuts = -1; break; }
            cuts[ncuts++] = cutmask;
            if (sz < tau) tau = sz;
        }
        if (ncuts < 0) continue;
        if (ncuts == 0 || tau < 2) continue;
        tau_ge2++;
        /* rho = (1/tau) * sum_v ((outdeg-indeg) mod tau) over ORIGINAL
           digraph with unit weights */
        {
            int rho = 0, t = tau;
            static int deg[MAXN];
            for (int i = 0; i < n; i++) deg[i] = 0;
            for (int i = 0; i < m; i++) { deg[au[i]]++; deg[av[i]]--; }
            for (int i = 0; i < n; i++) {
                int mv = deg[i] % t; if (mv < 0) mv += t;
                rho += mv;
            }
            rho /= t;
            if (rho <= 2 || (t == 3 && rho == 3)) { rho_short++; continue; }
        }
        /* minimal cuts filter */
        static u64 mcuts[MAXCUTS]; int nmc = 0;
        /* sort by popcount (simple insertion into buckets) */
        for (int pass = 2; pass <= 64 && nmc < ncuts; pass++) {
            for (int i = 0; i < ncuts; i++) {
                u64 c = cuts[i];
                if (__builtin_popcountll(c) != pass) continue;
                int dom = 0;
                for (int j = 0; j < nmc; j++)
                    if ((mcuts[j] & c) == mcuts[j]) { dom = 1; break; }
                if (!dom) mcuts[nmc++] = c;
            }
        }
        /* randomized greedy packing: tau colors */
        int packed = 0;
        for (int t2 = 0; t2 < gtries && !packed; t2++) {
            u64 used = 0; int ok = 1;
            for (int col = 0; col < tau && ok; col++) {
                u64 chosen = 0;
                /* random order over cuts */
                for (int rep = 0; rep < nmc; rep++) {
                    int ci2 = (rep + (int)(rnd() % (u32)nmc)) % nmc;
                    u64 c = mcuts[ci2];
                    if (c & chosen) continue;
                    u64 availm = c & ~used;
                    if (!availm) { ok = 0; break; }
                    /* pick random set bit */
                    int nb = __builtin_popcountll(availm);
                    int k = (int)(rnd() % (u32)nb);
                    u64 b = availm;
                    while (k--) b &= b - 1;
                    b = b & -b;
                    chosen |= b; used |= b;
                }
                if (!ok) break;
                /* verify all cuts hit (random order may have skipped none:
                   loop above iterates nmc times but random start may repeat
                   indices; redo deterministic fill for unhit cuts) */
                for (int ci2 = 0; ci2 < nmc && ok; ci2++) {
                    u64 c = mcuts[ci2];
                    if (c & chosen) continue;
                    u64 availm = c & ~used;
                    if (!availm) { ok = 0; break; }
                    int nb = __builtin_popcountll(availm);
                    int k = (int)(rnd() % (u32)nb);
                    u64 b = availm;
                    while (k--) b &= b - 1;
                    b = b & -b;
                    chosen |= b; used |= b;
                }
            }
            if (ok) packed = 1;
        }
        if (packed) { greedy_ok++; continue; }
        survivors++;
        /* survivor: emit original line for Python ILP */
        printf("%d %d", n, m);
        for (int i = 0; i < m; i++) printf(" %d %d", au[i], av[i]);
        printf("\n");
        fflush(stdout);
    }
    fprintf(stderr,
        "CFINAL read=%lld tau_ge2=%lld rho_short=%lld greedy=%lld "
        "survivors=%lld cut_blow=%lld\n",
        readn, tau_ge2, rho_short, greedy_ok, survivors, cut_blow);
    return 0;
}

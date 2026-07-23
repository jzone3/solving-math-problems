/* P05 V4 exhaustive frontier checker for Gallai's 3 longest paths question.
 *
 * Reads graph6 lines (n <= 32) on stdin. For each connected graph:
 *   1. If traceable (has Hamiltonian path), it is SAFE (all longest paths are
 *      spanning; any three share every vertex... in fact share all n vertices).
 *   2. Else compute exact longest path length L (edges) by DFS.
 *   3. If some vertex v has longestpath(G-v) < L, then v lies on every longest
 *      path -> SAFE.
 *   4. Else enumerate all distinct vertex sets of longest paths and check every
 *      triple has nonempty intersection. If some triple is empty -> print the
 *      graph6 line as COUNTEREXAMPLE.
 *
 * Prints stats at end:
 *   total, nontraceable, emptyfull (empty intersection of ALL longest paths),
 *   counterexamples.
 * Compile: gcc -O3 -march=native -o gallai_check gallai_check.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n;                 /* vertices */
static uint32_t adj[32];      /* adjacency bitmasks */
static uint32_t full;         /* (1<<n)-1 */

/* ---------- graph6 parsing ---------- */
static int parse_graph6(const char *s) {
    int idx = 0;
    if ((unsigned char)s[0] == 126) return -1; /* n > 62 unsupported */
    n = s[idx++] - 63;
    if (n <= 0 || n > 32) return -1;
    memset(adj, 0, sizeof(adj));
    int nbits = n * (n - 1) / 2;
    int bit = 0, i = 1, j = 0; /* edge (j,i) ordering: column-wise upper triangle */
    int c = 0, have = 0;
    while (bit < nbits) {
        if (have == 0) { c = s[idx++] - 63; if (c < 0) return -1; have = 6; }
        int b = (c >> (have - 1)) & 1; have--;
        if (b) { adj[i] |= 1u << j; adj[j] |= 1u << i; }
        bit++;
        j++;
        if (j == i) { i++; j = 0; }
    }
    full = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    return 0;
}

/* ---------- connectivity of a vertex-subset mask ---------- */
static inline int connected_mask(uint32_t mask) {
    if (!mask) return 1;
    uint32_t start = mask & (~mask + 1);
    uint32_t seen = start, frontier = start;
    while (frontier) {
        uint32_t nxt = 0;
        while (frontier) {
            int v = __builtin_ctz(frontier);
            frontier &= frontier - 1;
            nxt |= adj[v] & mask & ~seen;
        }
        seen |= nxt;
        frontier = nxt;
    }
    return seen == mask;
}

/* ---------- traceability (Hamiltonian path) DFS with pruning ---------- */
static uint32_t sub;   /* allowed vertex set for current computation */
static int subn;       /* popcount(sub) */

static int ham_dfs(int v, uint32_t visited, int len) {
    if (len == subn) return 1;
    uint32_t rest = sub & ~visited;
    /* prune: rest plus v must be connected */
    if (!connected_mask(rest | (1u << v))) return 0;
    /* prune: count degree-into-rest endpoints: any rest vertex with no
       neighbor in rest|{v} is unreachable */
    uint32_t r = rest;
    int deg1 = 0;
    while (r) {
        int u = __builtin_ctz(r);
        r &= r - 1;
        uint32_t nb = adj[u] & (rest | (1u << v));
        if (!nb) return 0;
        if (!(nb & (nb - 1))) deg1++; /* exactly one neighbor: must be endpoint */
    }
    if (deg1 > 2) return 0;
    uint32_t cand = adj[v] & rest;
    while (cand) {
        int u = __builtin_ctz(cand);
        cand &= cand - 1;
        if (ham_dfs(u, visited | (1u << u), len + 1)) return 1;
    }
    return 0;
}

static int traceable_in(uint32_t mask) {
    sub = mask;
    subn = __builtin_popcount(mask);
    if (subn <= 1) return 1;
    uint32_t m = mask;
    while (m) {
        int v = __builtin_ctz(m);
        m &= m - 1;
        if (ham_dfs(v, 1u << v, 1)) return 1;
    }
    return 0;
}

/* ---------- longest path length (vertices) within mask ---------- */
static int best;
static void lp_dfs(int v, uint32_t visited, int len) {
    if (len > best) best = len;
    if (best == subn) return;
    uint32_t cand = adj[v] & sub & ~visited;
    while (cand) {
        int u = __builtin_ctz(cand);
        cand &= cand - 1;
        lp_dfs(u, visited | (1u << u), len + 1);
        if (best == subn) return;
    }
}

static int longest_in(uint32_t mask) { /* returns #vertices of longest path */
    sub = mask;
    subn = __builtin_popcount(mask);
    if (subn == 0) return 0;
    best = 0;
    uint32_t m = mask;
    while (m) {
        int v = __builtin_ctz(m);
        m &= m - 1;
        lp_dfs(v, 1u << v, 1);
        if (best == subn) break;
    }
    return best;
}

/* ---------- enumerate distinct vertex sets of longest paths ---------- */
#define MAXSETS 2000000
static uint32_t sets[MAXSETS];
static int nsets;
static int Lverts;
static int overflow;

#define HSIZE (1 << 22)
static uint32_t htab[HSIZE];
static void hclear(void) { memset(htab, 0, sizeof(htab)); }
static void addset(uint32_t s) {
    uint32_t h = (s * 2654435761u) & (HSIZE - 1);
    while (htab[h]) {
        if (htab[h] == s) return;
        h = (h + 1) & (HSIZE - 1);
    }
    htab[h] = s;
    if (nsets < MAXSETS) sets[nsets++] = s; else overflow = 1;
}

static void enum_dfs(int v, uint32_t visited, int len) {
    if (len == Lverts) { addset(visited); return; }
    uint32_t cand = adj[v] & ~visited;
    while (cand) {
        int u = __builtin_ctz(cand);
        cand &= cand - 1;
        /* prune: can path still reach Lverts? upper bound = len + reachable */
        uint32_t rest = ~ (visited) & full;
        /* cheap reachability bound: vertices reachable from u in rest */
        uint32_t seen = 1u << u, fr = 1u << u;
        while (fr) {
            uint32_t nx = 0;
            while (fr) { int w = __builtin_ctz(fr); fr &= fr - 1; nx |= adj[w] & rest & ~seen; }
            seen |= nx; fr = nx;
        }
        if (len + __builtin_popcount(seen) < Lverts) continue;
        enum_dfs(u, visited | (1u << u), len + 1);
    }
}

int main(int argc, char **argv) {
    char line[256];
    int verbose = (argc > 1 && !strcmp(argv[1], "-v"));
    long total = 0, nontrace = 0, emptyfull = 0, cex = 0, oflow = 0;
    long maxsets_seen = 0;
    while (fgets(line, sizeof(line), stdin)) {
        size_t sl = strlen(line);
        while (sl && (line[sl-1] == '\n' || line[sl-1] == '\r')) line[--sl] = 0;
        if (!sl) continue;
        if (parse_graph6(line)) { fprintf(stderr, "parse fail: %s\n", line); continue; }
        total++;
        if (verbose) {
            int L = longest_in(full);
            nsets = 0; overflow = 0; Lverts = L;
            hclear();
            sub = full; subn = n;
            for (int v = 0; v < n; v++) enum_dfs(v, 1u << v, 1);
            int found = 0;
            for (int i = 0; i < nsets && !found; i++)
                for (int j = i + 1; j < nsets && !found; j++) {
                    uint32_t t = sets[i] & sets[j];
                    for (int k = j + 1; k < nsets; k++)
                        if (!(t & sets[k])) { found = 1; break; }
                }
            printf("%s L=%d nsets=%d gallai3=%s\n", line, L, nsets, found ? "FAIL" : "OK");
            continue;
        }
        if (traceable_in(full)) continue;
        nontrace++;
        int L = longest_in(full);           /* vertices on longest path */
        /* step 3: vertex on all longest paths? */
        int safe = 0;
        for (int v = 0; v < n; v++) {
            uint32_t mask = full & ~(1u << v);
            /* G-v may be disconnected; longest path within it still defined */
            if (longest_in(mask) < L) { safe = 1; break; }
        }
        if (safe) continue;
        emptyfull++; printf("EMPTYFULL %s\n", line); fflush(stdout);
        /* step 4: enumerate longest path vertex sets, triple check */
        nsets = 0; overflow = 0; Lverts = L;
        hclear();
        sub = full; subn = n;
        for (int v = 0; v < n; v++) enum_dfs(v, 1u << v, 1);
        if (overflow) { oflow++; printf("OVERFLOW %s\n", line); fflush(stdout); continue; }
        if (nsets > maxsets_seen) maxsets_seen = nsets;
        /* reduce to inclusion-minimal sets: if S subset of S', S' is redundant
           for finding an empty triple intersection */
        /* sort by popcount ascending (insertion into buckets) */
        {
            static uint32_t tmp[MAXSETS];
            int cnt[33] = {0}, start[34];
            for (int i = 0; i < nsets; i++) cnt[__builtin_popcount(sets[i])]++;
            start[0] = 0;
            for (int b = 0; b <= 32; b++) start[b+1] = start[b] + cnt[b];
            int pos[33];
            memcpy(pos, start, sizeof(int)*33);
            for (int i = 0; i < nsets; i++) tmp[pos[__builtin_popcount(sets[i])]++] = sets[i];
            int m = 0;
            for (int i = 0; i < nsets; i++) {
                uint32_t s = tmp[i];
                int dominated = 0;
                for (int j = 0; j < m; j++)
                    if ((sets[j] & ~s) == 0) { dominated = 1; break; }
                if (!dominated) sets[m++] = s;
            }
            nsets = m;
        }
        int found = 0;
        for (int i = 0; i < nsets && !found; i++)
            for (int j = i + 1; j < nsets && !found; j++) {
                uint32_t t = sets[i] & sets[j];
                for (int k = j + 1; k < nsets; k++)
                    if (!(t & sets[k])) { found = 1; break; }
            }
        if (found) {
            cex++;
            printf("COUNTEREXAMPLE %s\n", line);
            fflush(stdout);
        }
    }
    fprintf(stderr, "STATS total=%ld nontraceable=%ld emptyfullint=%ld counterexamples=%ld overflow=%ld maxsets=%ld\n",
            total, nontrace, emptyfull, cex, oflow, maxsets_seen);
    return 0;
}

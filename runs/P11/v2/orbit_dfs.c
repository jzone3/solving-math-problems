/* P11 V2: fast DFS over multiplier-orbit value assignments for CW(n,k).
 *
 * Input (stdin, text):
 *   n k r
 *   then r orbit lines: size m, then m pairs "pos sign"
 * (signs allow the signed-character variant; plain case has all signs +1)
 *
 * Searches assignments v_i in {0,+1,-1} per orbit with:
 *   - total weight == k,
 *   - (sum of entries)^2 == k,
 *   - all nontrivial periodic autocorrelations == 0 (exact, checked at leaves
 *     via O(k^2) difference table),
 * with pruning: exact subset-sum feasibility on remaining sizes (bitset DP),
 * entry-sum reachability, first nonzero orbit forced to +1.
 *
 * Prints WITNESS lines and a final summary. Exits early if time budget
 * (argv[1], seconds; 0 = unlimited) is exceeded, printing EXCEEDED.
 *
 * Optional prefix split (for parallelization): argv[2] is a string of
 * characters from {0,+,-}, giving forced values for the first P orbits in
 * the engine's descending-size order.  The DFS then starts at depth P.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAXN 256
#define MAXR 128

static int n, k, r, s0;
static int osize[MAXR], osum[MAXR];
static int opos[MAXR][MAXN], osgn[MAXR][MAXN];
static int order_[MAXR];
static uint64_t feas[MAXR + 1][4]; /* bitset of achievable weights (k<=127) */
static int suf_abs[MAXR + 1];
static int a[MAXN];
static int val[MAXR];
static long long nodes = 0, leaves = 0, wits = 0;
static double t_end = 0;
static int exceeded = 0;

static double now(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int isqrt_(int x){int s=0;while((s+1)*(s+1)<=x)s++;return s;}

static int check_leaf(void) {
    /* exact autocorrelation via difference counts over nonzero positions */
    static int pos[MAXN], sv[MAXN];
    static int acc[MAXN];
    int m = 0;
    for (int i = 0; i < n; i++) if (a[i]) { pos[m]=i; sv[m]=a[i]; m++; }
    if (m != k) return 0;
    memset(acc, 0, sizeof(int)*n);
    for (int i = 0; i < m; i++)
        for (int j = 0; j < m; j++) {
            if (i == j) continue;
            int d = pos[i] - pos[j]; if (d < 0) d += n;
            acc[d] += sv[i]*sv[j];
        }
    for (int t = 1; t < n; t++) if (acc[t]) return 0;
    return 1;
}

static void print_witness(void) {
    printf("WITNESS [");
    for (int i = 0; i < n; i++) printf("%s%d", i?", ":"", a[i]);
    printf("]\n"); fflush(stdout);
}

static void dfs(int idx, int rem, int cur_sum, int any_nz) {
    if (exceeded) return;
    if ((++nodes & 0xFFFFF) == 0 && t_end > 0 && now() > t_end) { exceeded = 1; return; }
    if (rem == 0) {
        if (cur_sum == s0 || cur_sum == -s0) {
            leaves++;
            if (check_leaf()) { wits++; print_witness(); }
        }
        return;
    }
    if (idx >= r) return;
    if (!((feas[idx][rem >> 6] >> (rem & 63)) & 1ULL)) return;
    int d1 = s0 - cur_sum; if (d1 < 0) d1 = -d1;
    int d2 = -s0 - cur_sum; if (d2 < 0) d2 = -d2;
    int dm = d1 < d2 ? d1 : d2;
    if (dm > suf_abs[idx]) return;
    int oi = order_[idx];
    dfs(idx + 1, rem, cur_sum, any_nz);
    if (osize[oi] > 0 && osize[oi] <= rem) {
        for (int vi = 0; vi < (any_nz ? 2 : 1); vi++) {
            int v = vi ? -1 : 1;
            for (int j = 0; j < osize[oi]; j++) a[opos[oi][j]] = osgn[oi][j] * v;
            dfs(idx + 1, rem - osize[oi], cur_sum + v * osum[oi], 1);
            for (int j = 0; j < osize[oi]; j++) a[opos[oi][j]] = 0;
            if (exceeded) return;
        }
    }
}

int main(int argc, char **argv) {
    double budget = argc > 1 ? atof(argv[1]) : 0;
    const char *prefix = argc > 2 ? argv[2] : "";
    if (scanf("%d %d %d", &n, &k, &r) != 3) return 1;
    if (k > 255 || r > MAXR || n > MAXN) { fprintf(stderr, "too big\n"); return 1; }
    s0 = isqrt_(k);
    if (s0 * s0 != k) { printf("NO_SQUARE\n"); return 0; }
    int usable_sizes[MAXR];
    for (int i = 0; i < r; i++) {
        int m; if (scanf("%d", &m) != 1) return 1;
        int usable = 1;
        /* read pairs; detect stabilizer conflicts encoded upstream as size 0 */
        osize[i] = m; osum[i] = 0;
        for (int j = 0; j < m; j++) {
            scanf("%d %d", &opos[i][j], &osgn[i][j]);
            osum[i] += osgn[i][j];
        }
        (void)usable;
    }
    /* order by size descending */
    for (int i = 0; i < r; i++) order_[i] = i;
    for (int i = 0; i < r; i++)
        for (int j = i + 1; j < r; j++)
            if (osize[order_[j]] > osize[order_[i]]) {
                int t = order_[i]; order_[i] = order_[j]; order_[j] = t;
            }
    /* suffix DP */
    memset(feas[r], 0, sizeof feas[r]);
    feas[r][0] = 1ULL; /* weight 0 achievable */
    suf_abs[r] = 0;
    for (int i = r - 1; i >= 0; i--) {
        int oi = order_[i];
        memcpy(feas[i], feas[i + 1], sizeof feas[i]);
        int sz = osize[oi];
        if (sz > 0) {
            /* shift bitset left by sz, OR in (cap at k) */
            uint64_t tmp[4] = {0,0,0,0};
            int w = sz >> 6, b = sz & 63;
            for (int q = 3; q >= 0; q--) {
                uint64_t v = 0;
                if (q - w >= 0) {
                    v = feas[i + 1][q - w] << b;
                    if (b && q - w - 1 >= 0) v |= feas[i + 1][q - w - 1] >> (64 - b);
                }
                tmp[q] = v;
            }
            for (int q = 0; q < 4; q++) feas[i][q] |= tmp[q];
        }
        suf_abs[i] = suf_abs[i + 1] + (osum[oi] >= 0 ? osum[oi] : -osum[oi]);
    }
    memset(a, 0, sizeof a);
    if (budget > 0) t_end = now() + budget;
    double t0 = now();
    int P = (int)strlen(prefix);
    int rem0 = k, sum0 = 0, anz = 0, bad = 0;
    for (int i = 0; i < P && i < r; i++) {
        int oi = order_[i];
        int v = prefix[i] == '+' ? 1 : prefix[i] == '-' ? -1 : 0;
        if (v != 0) {
            if (osize[oi] == 0 || osize[oi] > rem0) { bad = 1; break; }
            for (int j = 0; j < osize[oi]; j++) a[opos[oi][j]] = osgn[oi][j] * v;
            rem0 -= osize[oi]; sum0 += v * osum[oi]; anz = 1;
        }
    }
    if (bad) { printf("DONE nodes=0 leaves=0 wits=0 time=0.0 (bad prefix)\n"); return 0; }
    dfs(P, rem0, sum0, anz);
    if (exceeded) printf("EXCEEDED nodes=%lld leaves=%lld time=%.1f\n", nodes, leaves, now()-t0);
    else printf("DONE nodes=%lld leaves=%lld wits=%lld time=%.1f\n", nodes, leaves, wits, now()-t0);
    return 0;
}
